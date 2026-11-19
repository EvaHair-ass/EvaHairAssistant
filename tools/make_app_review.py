#!/usr/bin/env python3
"""Файлы для носителя только по приложению: xlsx (в формате его таблицы по сайту) и docx."""
import glob, re, pathlib
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
R = pathlib.Path(__file__).resolve().parent.parent
rows = []
for f in sorted(glob.glob(str(R / "tools/i18n/phrases_*.txt"))):
    for l in open(f, encoding="utf-8"):
        p = l.rstrip("\n").split(" ⇒ ")
        if len(p) == 3: rows.append(p)
SKIP = re.compile(r"^(Проверка по ТЗ|Что попробовать|Эти сценарии|Прототип по ТЗ|В настоящем приложении копия|Зачем это нужно|Это кликабельный прототип|Все твои правки в прототипе|Заполнить пример из ТЗ|Закупка 100 камней|Инструмент: 3 применения|Черновик: 20 в изделии|60 минут при ставке|Повторная закупка дороже)")
rows = [r for r in rows if not SKIP.match(r[0])]
CUR = re.compile(r"доллар|евро\b|рубль|гривн|тенге|лари|драм|манат|\bсум\b|\bсом\b|лей\b|злотый|крона|\bлев\b|динар|фунт|франк|дирхам|риял|шекель|рупия|юань|иена|вона|\bбат\b|донг|ринггит|реал\b|песо|рэнд|форинт|лира", re.I)
def theme(ru):
    if CUR.search(ru) and len(ru) < 40: return "Валюты"
    if re.search(r"^(Катушка|Коробка|Лоток|Пакет|Полка|Ящик)", ru): return "Места хранения (демо)"
    if re.search(r"«|^(Заколка|Прядь|Коса|Косы|Ободок|Серьги|Тика|Подвеска|Афро|Браслет|Колье)", ru) and len(ru) < 70: return "Названия изделий (демо)"
    if len(ru) > 90: return "Длинные подсказки и пояснения"
    return "Кнопки, подписи и короткие сообщения"
ORDER = ["Кнопки, подписи и короткие сообщения", "Длинные подсказки и пояснения", "Названия изделий (демо)", "Места хранения (демо)", "Валюты"]
rows.sort(key=lambda r: (ORDER.index(theme(r[0])), r[0].lower()))

# ---------- xlsx
wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Приложение — турецкий"
hdr = ["№", "Раздел", "Русский оригинал", "Турецкий исходный", "Рекомендованный турецкий", "Решение", "Комментарий редактора"]
ws.append(hdr)
for i, (ru, tr, en) in enumerate(rows, 1): ws.append([i, theme(ru), ru, tr, "", "", ""])
fill = PatternFill("solid", fgColor="E8DCC6")
for c in ws[1]: c.font = Font(bold=True); c.fill = fill; c.alignment = Alignment(wrap_text=True, vertical="top")
for col, w in zip("ABCDEFG", (6, 26, 55, 55, 55, 16, 40)): ws.column_dimensions[col].width = w
for row in ws.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
n2 = wb.create_sheet("Решения по сайту")
n2.append(["Что решено", "Правило"])
for a, b in [
 ("Название работы", "«Gül Altın» (не «Rose Altın»)"),
 ("Слово stok", "Пишем так, как предложил носитель: stoğu, stoğunuz, stoğa (а stoktan, stokta, stok takibi остаются)"),
 ("Тика", "«Tika (Saç ve Alın Takısı)»"),
 ("Вкладка «Ещё»", "Diğer"),
 ("Таймер", "Zamanlayıcı"),
 ("Труд", "İşçilik"),
 ("Цена", "Önerilen satış fiyatı; maliyet = Maliyet; прибыль = Kâr; выручка = Ciro"),
 ("Тон", "Уважительное «siz», дружелюбно; не копировать русский порядок слов; {0}, {1} не менять")]: n2.append([a, b])
n2.column_dimensions["A"].width = 24; n2.column_dimensions["B"].width = 95
for c in n2[1]: c.font = Font(bold=True); c.fill = fill
for row in n2.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(wrap_text=True, vertical="top")
wb.save(R / "Melaymade_TR_app_review.xlsx")

# ---------- docx
doc = Document(); sec = doc.sections[0]; sec.orientation = WD_ORIENT.LANDSCAPE; sec.page_width, sec.page_height = sec.page_height, sec.page_width
sec.left_margin = sec.right_margin = Cm(1.6); sec.top_margin = sec.bottom_margin = Cm(1.5)
doc.styles["Normal"].font.name = "Calibri"; doc.styles["Normal"].font.size = Pt(10.5)
doc.add_heading("Atölyem (приложение): турецкие тексты для проверки", 0)
doc.add_paragraph("Bu metinler «Atölyem» uygulamasının arayüzüne aittir. Lütfen her satırı doğallık, yazım ve anlam açısından kontrol edin. Üslup: «siz». {0}, {1} gibi ifadeler sayı ve ad yerine geçer; değiştirmeyin. Düzeltmenizi son sütuna yazın. Teşekkürler!")
def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr(); sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), hexcolor); tcPr.append(sh)
n = 1
for g in ORDER:
    grp = [r for r in rows if theme(r[0]) == g]
    if not grp: continue
    doc.add_heading(g, 2)
    tb = doc.add_table(rows=1, cols=4); tb.style = "Table Grid"; tb.autofit = False
    W = (Cm(1.1), Cm(8.0), Cm(9.0), Cm(7.6))
    for c, t in zip(tb.rows[0].cells, ("№", "Русский (смысл)", "Türkçe (для проверки)", "Исправление носителя")):
        c.text = ""; r_ = c.paragraphs[0].add_run(t); r_.bold = True; shade(c, "E8DCC6")
    for ru, tr, en in grp:
        cells = tb.add_row().cells; cells[0].text = str(n); cells[1].text = ru; cells[2].text = ""; cells[2].paragraphs[0].add_run(tr).bold = True; n += 1
    for col, w in zip(tb.columns, W): col.width = w
    for row in tb.rows:
        for c, w in zip(row.cells, W): c.width = w
doc.save(R / "Atolyem_TR_app_texts_for_review.docx")
print(len(rows), "фраз")
