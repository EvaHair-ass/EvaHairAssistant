#!/usr/bin/env python3
"""Единый файл для носителя турецкого: сайт + приложение. Колонки: №, русский, турецкий, замечание."""
import sys, glob, pathlib, re
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import build_landing as B
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

R, T = B.TEXTS["ru"], B.TEXTS["tr"]
def clean(s): return str(s).replace("*", "")

def rows_for(path, ru, tr):
    """плоский список (подпись, ru, tr)"""
    out = []
    if isinstance(tr, dict):
        for k in tr:
            if k in ("path", "label", "locale", "ribbon", "gal_alt", "ui_note_dummy"): continue
            out += rows_for(f"{path}{k}.", ru.get(k, ""), tr[k])
    elif isinstance(tr, (list, tuple)):
        for i, x in enumerate(tr):
            rx = ru[i] if isinstance(ru, (list, tuple)) and i < len(ru) else ""
            out += rows_for(f"{path}{i + 1}.", rx, x)
    else:
        out.append((path.rstrip("."), clean(ru), clean(tr)))
    return out

# --- сайт: по блокам
SITE = [
 ("Главный экран и меню", ["title", "desc", "nav", "login", "kicker", "h1", "sub", "cta", "cta2", "note"]),
 ("Как это работает", ["how_title", "steps"]),
 ("Ремёсла (гирлянда)", ["cr"]),
 ("Примеры работ (галерея)", ["sh"]),
 ("Академия", ["ac"]),
 ("Возможности", ["feat_title", "features"]),
 ("Подписи к скриншотам", ["gal_title", "gal", "ui_note"]),
 ("Вопросы и ответы", ["faq_title", "faq"]),
 ("Финальный призыв и подвал", ["final_title", "final_text", "final_cta", "footer"]),
]
LABELS = {"pill": "Плашка", "ac_badge": "Бейдж", "ac_h": "Подзаголовок", "ac_big": "Главный заголовок", "ac_lead": "Вступление", "pain_title": "«Знакомо?»", "pains": "Боли", "ac_cta": "Кнопка", "ac_cards": "Карточки Академии", "b_ok": "Метка «работает»", "b_soon": "Метка «скоро»", "road_kick": "Надпись над дорожной картой", "road_title": "Дорожная карта: заголовок", "road_text": "Дорожная карта: текст", "ac_note": "Честная оговорка", "features_extra": "Карточка в «Возможностях»", "faq_extra": "Вопросы про Академию", "kick": "Надпись над заголовком", "title": "Заголовок", "lead": "Вступление", "items": "Ремёсла", "foot": "Подпись", "yk": "Блок «Твоя мастерская»: надпись", "yt": "Блок «Твоя мастерская»: заголовок", "yl": "Блок «Твоя мастерская»: вступление", "yi": "Блок «Твоя мастерская»: пункты", "faq": "Вопрос про ремесло", "chips": "Кнопки-фильтры", "names": "Названия работ", "kinds": "Виды работ", "note": "Примечание"}

doc = Document()
sec = doc.sections[0]; sec.orientation = WD_ORIENT.LANDSCAPE; sec.page_width, sec.page_height = sec.page_height, sec.page_width
for m in ("left_margin", "right_margin"): setattr(sec, m, Cm(1.6))
sec.top_margin = sec.bottom_margin = Cm(1.5)
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)

def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcolor); tcPr.append(sh)

def table(rows, start=1):
    tb = doc.add_table(rows=1, cols=4); tb.style = "Table Grid"
    hdr = tb.rows[0].cells
    for c, t in zip(hdr, ("№", "Русский (для понимания смысла)", "Türkçe (текст для проверки)", "Исправление носителя")):
        c.text = ""; r = c.paragraphs[0].add_run(t); r.bold = True; r.font.size = Pt(10); shade(c, "E8DCC6")
    W = (Cm(1.1), Cm(8.0), Cm(9.0), Cm(7.6))
    n = start
    for lab, ru, tr in rows:
        cells = tb.add_row().cells
        cells[0].text = str(n)
        cells[1].text = ru
        cells[2].text = ""; run = cells[2].paragraphs[0].add_run(tr); run.bold = True
        cells[3].text = ""
        n += 1
    tb.autofit = False
    for col, w in zip(tb.columns, W): col.width = w
    for row in tb.rows:
        for c, w in zip(row.cells, W): c.width = w
    return n

h = doc.add_heading("Turkish texts for review: Melaymade «Atölyem»", 0)
doc.add_paragraph("Проверка турецких текстов сайта melaymade.com и приложения «Моя мастерская» (Atölyem).")
p = doc.add_paragraph()
p.add_run("Просьба к носителю (Türkçe): ").bold = True
p.add_run("Bu metinler, el işi ustaları için hazırlanan bir uygulamanın tanıtım sitesine ve uygulamanın kendisine aittir. Lütfen her satırı doğallık, yazım ve anlam açısından kontrol eder misiniz? Üslup: «siz» (saygılı, sıcak). Marka adı: Melaymade (tek kelime). Uygulamanın adı: Atölyem. Yanlış ya da kulağa yapay gelen yerleri son sütuna daha doğal halini yazmanız yeterli. Çok teşekkürler!")
doc.add_paragraph("Правила: стиль «siz»; {0}, {1} в приложении — подставляемые значения (числа, названия), их менять не нужно; русский столбец нужен только чтобы понять смысл. Если фраза звучит неестественно, напишите свой вариант в последнем столбце.").runs[0].italic = True

n = 1
doc.add_heading("ЧАСТЬ 1. САЙТ melaymade.com", 1)
for title, keys in SITE:
    doc.add_heading(title, 2)
    rows = []
    for k in keys:
        rows += [(f"{LABELS.get(k, k)}", r_, t_) for _, r_, t_ in rows_for(k + ".", R[k] if k in R else "", T[k])] if k not in ("cr", "sh", "ac") else []
    if "cr" in keys:
        rows += [(k, a, b) for k, a, b in rows_for("", R["cr"], T["cr"])]
    if "sh" in keys:
        rows += [(k, a, b) for k, a, b in rows_for("", R["sh"], T["sh"])]
    if "ac" in keys:
        for k in ("pill", "ac_badge", "ac_big", "ac_h", "ac_lead", "ac_cta", "pain_title", "pains", "ac_cards", "b_ok", "b_soon", "road_kick", "road_title", "road_text", "ac_note", "features_extra", "faq_extra"):
            rows += [(k, a, b) for _, a, b in rows_for("", R["ac"][k], T["ac"][k])]
    # убрать дубли и пустые
    seen, uniq = set(), []
    for lab, a, b in rows:
        if not b or (a, b) in seen: continue
        seen.add((a, b)); uniq.append((lab, a, b))
    n = table(uniq, n)
site_count = n - 1

# --- приложение
doc.add_page_break()
doc.add_heading("ЧАСТЬ 2. ПРИЛОЖЕНИЕ «Atölyem»", 1)
app = []
for f in sorted(glob.glob(str(pathlib.Path(__file__).parent / "i18n" / "phrases_*.txt"))):
    for l in open(f, encoding="utf-8"):
        p_ = l.rstrip("\n").split(" ⇒ ")
        if len(p_) == 3: app.append(p_)
# разложить по темам, чтобы носителю было проще
def theme(ru):
    if re.search(r"доллар|евро|рубль|гривн|тенге|лари|драм|манат|сум|сом|лей|злотый|крона|лев|динар|фунт|франк|дирхам|риял|шекель|рупия|юань|иена|вона|бат\b|донг|ринггит|реал|песо|рэнд|форинт", ru, re.I) and len(ru) < 40: return "Валюты"
    if re.search(r"Катушка|Коробка|Лоток|Пакет|Полка|Ящик", ru): return "Места хранения (демо)"
    if re.search(r"«|Заколка|Прядь|Коса|Косы|Ободок|Серьги|Тика|Подвеска|Афро|Браслет|Колье", ru) and len(ru) < 60: return "Названия изделий и демо-данные"
    if len(ru) > 90: return "Длинные подсказки и пояснения"
    return "Кнопки, подписи и короткие сообщения"
groups = {}
for ru, tr, en in app: groups.setdefault(theme(ru), []).append(("", ru, tr))
for g in ("Кнопки, подписи и короткие сообщения", "Длинные подсказки и пояснения", "Названия изделий и демо-данные", "Места хранения (демо)", "Валюты"):
    if g not in groups: continue
    doc.add_heading(g, 2)
    n = table(sorted(groups[g], key=lambda x: x[1].lower()), n)
doc.save("/home/user/EvaHairAssistant/Turkish_texts_for_review_Melaymade.docx")
print("сайт:", site_count, "строк; всего:", n - 1)
