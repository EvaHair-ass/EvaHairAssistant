#!/usr/bin/env python3
"""Проверка полноты: каждый русский фрагмент исходника должен быть в словаре (как часть ключа)."""
import re, glob, pathlib, sys
R = pathlib.Path(__file__).resolve().parent.parent.parent
s = (R / "prototype/index.html").read_text(encoding="utf-8")
js = s[s.index("<script>"):]
js = re.sub(r"/\*.*?\*/", "", js, flags=re.S); js = re.sub(r"(?m)^\s*//.*$", "", js); js = re.sub(r"(?m)\s//\s.*$", "", js)
html = s[:s.index("<script>")]
keys = set()
for f in glob.glob(str(R / "tools/i18n/phrases_*.txt")):
    for l in open(f, encoding="utf-8"): keys.add(l.split(" ⇒ ")[0].strip())
big = "\n".join(keys)
CY = re.compile(r"[А-Яа-яЁё]")
SKIP = {"авг","июл","июн","мар","окт","фев","янв","закупок","позиций","уроков","участниц","участница","участницы","человек","человека","материалов по рецепту","закупок, сохранённые дизайны и активные работы (","Проверка по ТЗ","Что попробовать","Эти сценарии из раздела 6 считаются прямо сейчас на отдельном пустом складе","В настоящем приложении копия будет делаться сама, в облаке. Эта кнопка нужна на время прототипа","· мало","Русский","лв","дин","Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"}
miss = {}
for src, name in ((js, "js"), (html, "html")):
    if name == "html": src = re.sub(r"<(script|style)[\s\S]*?</\1>", "", src)
    for m in re.finditer(r"[^'`\"<>${}|\\\n]*[А-Яа-яЁё][^'`\"<>${}|\\\n]*", src):
        frag = re.sub(r"\s+", " ", m.group(0)).strip(" ,.:;")
        if len(frag) < 3 or "А-Яа-я" in frag or frag in SKIP: continue
        if frag in big: continue
        # кусочки множественного числа и единицы
        if re.fullmatch(r"[\d,. ]*(мм|см|г|шт|м|мл)\b.*", frag): continue
        miss[frag] = 1
for f in sorted(miss): print(repr(f[:150]))
print(len(miss), "фрагментов без перевода")
sys.exit(1 if miss else 0)
