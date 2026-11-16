#!/usr/bin/env python3
"""Собирает prototype/i18n-tr.js и i18n-en.js из tools/i18n/phrases_*.txt (ru ⇒ tr ⇒ en)."""
import json, re, pathlib, glob, sys
D = pathlib.Path(__file__).resolve().parent
OUT = D.parent.parent / "prototype"
rows = {}
for f in sorted(glob.glob(str(D / "phrases_*.txt"))):
    for ln, line in enumerate(open(f, encoding="utf-8"), 1):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"): continue
        p = line.split(" ⇒ ")
        if len(p) != 3: print("ОШИБКА формата:", f, ln, line[:80]); continue
        rows[p[0].strip()] = (p[1].strip(), p[2].strip())

# множественное число: формы, tr, [en один, en много]
PL = [
 (["закупка", "закупки", "закупок"], "alım", ["purchase", "purchases"]),
 (["изделие", "изделия", "изделий"], "ürün", ["piece", "pieces"]),
 (["курс", "курса", "курсов"], "kurs", ["course", "courses"]),
 (["материал", "материала", "материалов"], "malzeme", ["material", "materials"]),
 (["позиция", "позиции", "позиций"], "kalem", ["item", "items"]),
 (["работа", "работы", "работ"], "iş", ["project", "projects"]),
 (["урок", "урока", "уроков"], "ders", ["lesson", "lessons"]),
 (["участница", "участницы", "участниц"], "katılımcı", ["participant", "participants"]),
 (["ученица", "ученицы", "учениц"], "öğrenci", ["student", "students"]),
 (["человек", "человека", "человек"], "kişi", ["person", "people"]),
]
# единицы и мелкие правила: (регулярное выражение, tr, en)
RULES = [
 (r"(\d)(\s?)мм(?![А-Яа-яЁё])", r"$1$2mm", r"$1$2mm"),
 (r"(\d)(\s?)см(?![А-Яа-яЁё])", r"$1$2cm", r"$1$2cm"),
 (r"(\d)(\s?)мл(?![А-Яа-яЁё])", r"$1$2ml", r"$1$2ml"),
 (r"(\d)(\s?)шт(?![А-Яа-яЁё])", r"$1$2adet", r"$1$2pcs"),
 (r"(\d)(\s?)г(?![А-Яа-яЁё])", r"$1$2g", r"$1$2g"),
 (r"(\d)(\s?)м(?![А-Яа-яЁё])", r"$1$2m", r"$1$2m"),
 (r"(\d)(\s?)уп\.", r"$1$2pkt", r"$1$2pk"),
 (r"(\d)\s+фото(?![А-Яа-яЁё])", r"$1 fotoğraf", r"$1 photos"),
 (r"/прим\.", "/uyg.", "/use"),
 (r"/шт(?![А-Яа-яЁё])", "/adet", "/pcs"),
 (r"/мл(?![А-Яа-яЁё])", "/ml", "/ml"),
 (r"/см(?![А-Яа-яЁё])", "/cm", "/cm"),
 (r"/г(?![А-Яа-яЁё])", "/g", "/g"),
 (r"/м(?![А-Яа-яЁё])", "/m", "/m"),
 (r"/ч(?![А-Яа-яЁё])", "/sa", "/h"),
 (r"/упак(?![А-Яа-яЁё])", "/pkt", "/pk"),
]
UNITS = {"шт": ("adet", "pcs"), "м": ("m", "m"), "см": ("cm", "cm"), "г": ("g", "g"), "мл": ("ml", "ml"), "мм": ("mm", "mm"), "ед.": ("birim", "unit"), "мин": ("dk", "min")}
for k, v in UNITS.items(): rows.setdefault(k, v)

def ph(s): return sorted(re.findall(r"\{\d+\}", s))
bad = 0
for k, (t, e) in rows.items():
    if ph(k) != ph(t) or ph(k) != ph(e):
        print("ПЛЕЙСХОЛДЕРЫ не совпадают:", k[:70]); bad += 1

for i, lang in ((0, "tr"), (1, "en")):
    d = {"t": {k: v[i] for k, v in rows.items()},
         "pl": [[f, o if lang == "tr" else o2] for f, o, o2 in PL],
         "rules": [[r[0], r[1 + i]] for r in RULES]}
    (OUT / f"i18n-{lang}.js").write_text("window.I18N_DICT=" + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(lang, len(d["t"]), "фраз,", round((OUT / f"i18n-{lang}.js").stat().st_size / 1024), "КБ")

keys = json.load(open(D / "ru_keys.json", encoding="utf-8"))
plforms = {f for g in PL for f in g[0]}
skip = {"Русский", "лв", "дин", "с", "за"} | plforms
miss = [k for k in keys if k not in rows and k not in skip and not re.fullmatch(r"[\d,.\s]*(мм|см|г|шт|м|мл)\b.*", k)]
print("не переведено из исходника:", len(miss))
for k in miss[:80]: print("  ", k)
sys.exit(1 if bad else 0)
