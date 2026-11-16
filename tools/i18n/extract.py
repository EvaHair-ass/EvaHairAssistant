#!/usr/bin/env python3
"""Достаёт из prototype/index.html все русские фразы приложения (для перевода).
Выход: tools/i18n/ru_keys.json: список уникальных фраз. {0},{1}: подставляемые значения."""
import re, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
src = (ROOT / "prototype" / "index.html").read_text(encoding="utf-8")
CYR = re.compile(r"[А-Яа-яЁё]")
keys = {}

def add(t):
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"^[\W\d_]*(?=[А-Яа-яЁё{])", lambda m: m.group(0), t)
    if t and CYR.search(t):
        keys[t] = keys.get(t, 0) + 1

def strip_expr(t):
    """заменяет ${...} (с вложенностью) на {n}"""
    out, i, n = [], 0, 0
    while i < len(t):
        if t.startswith("${", i):
            d, j = 1, i + 2
            while j < len(t) and d:
                if t[j] == "{": d += 1
                elif t[j] == "}": d -= 1
                j += 1
            expr = t[i + 2:j - 1]
            if expr.lstrip().startswith("ic("):
                i = j; continue
            if "pl(" in expr and re.search(r"pl\(", expr):
                out.append("§"); i = j; continue
            # вложенные шаблоны и строки внутри выражения тоже содержат фразы
            for m in re.finditer(r"'([^'\n]*[А-Яа-яЁё][^'\n]*)'", expr): add_seg(m.group(1))
            for m in re.finditer(r"`([^`]*[А-Яа-яЁё][^`]*)`", expr, flags=re.S): handle_tpl(m.group(1))
            out.append("{%d}" % n); n += 1; i = j
        else:
            out.append(t[i]); i += 1
    r = "".join(out)
    r = re.sub(r"\{(\d+)\}\s§", r"{\1}", r)
    return r

def add_seg(t):
    # атрибуты тегов
    for m in re.finditer(r'(?:placeholder|aria-label|title|alt)="([^"]*)"', t): add(m.group(1))
    # текст между тегами
    for part in re.split(r"<[^>]*>", t): add(part)

def handle_tpl(t):
    add_seg(strip_expr(t))

js = src[src.index("<script>"):]
html = src[:src.index("<script>")]
# html-часть
for m in re.finditer(r'(?:placeholder|aria-label|title|alt)="([^"]*)"', html): add(m.group(1))
for part in re.split(r"<[^>]*>", re.sub(r"<(script|style)[\s\S]*?</\1>", "", html)): add(part)
# шаблоны
pos = 0
for m in re.finditer(r"`((?:[^`\\]|\\.)*)`", js, flags=re.S):
    if CYR.search(m.group(1)): handle_tpl(m.group(1))
# обычные строки (вне шаблонов)
js_wo = re.sub(r"`((?:[^`\\]|\\.)*)`", "``", js, flags=re.S)
for m in re.finditer(r"'((?:[^'\\\n]|\\.)*)'", js_wo):
    if CYR.search(m.group(1)): add_seg(m.group(1).replace("\\'", "'"))
for m in re.finditer(r'"((?:[^"\\\n]|\\.)*)"', js_wo):
    if CYR.search(m.group(1)): add_seg(m.group(1))
# комментарии могли попасть: убираем строки, где нет русских букв после чистки
for k in list(keys):
    if "§" in k: del keys[k]
# окончательная чистка артефактов
clean = {}
for k, v in keys.items():
    k2 = re.sub(r"^[^А-Яа-яЁёA-Za-z{(«\"0-9+/]*\}", "", k).strip() if re.match(r"^[^А-Яа-яЁёA-Za-z{(«0-9+/]*['\"]*\}", k) else k
    k2 = k2.strip()
    if k2 and CYR.search(k2): clean[k2] = 1
keys = clean
# группы множественного числа
pls = set()
for m in re.finditer(r"pl\([^,()]+(?:\([^)]*\))?[^,()]*,\s*\[([^\]]+)\]\)", js):
    pls.add(tuple(re.findall(r"'([^']+)'", m.group(1))))
(ROOT / "tools" / "i18n" / "ru_plurals.json").write_text(json.dumps(sorted(pls), ensure_ascii=False, indent=0), encoding="utf-8")
print(len(pls), "групп множественного числа")
out = sorted(keys)
(ROOT / "tools" / "i18n" / "ru_keys.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
print(len(out), "фраз")
