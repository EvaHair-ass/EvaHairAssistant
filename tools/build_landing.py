#!/usr/bin/env python3
"""Собирает посадочную страницу Melaymade на трёх языках в папку landing/.

Запуск из корня репозитория:  python3 tools/build_landing.py
Страницы: / (русский), /tr/ (турецкий), /en/ (английский).
Тексты лежат в словаре TEXTS ниже. Турецкий проверять носителем (правила: ЯЗЫКИ_И_СТИЛЬ.md).
"""
import html, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "landing"
BASE = "https://melaymade.com"
APP = "https://app.melaymade.com/"


# ---------------------------------------------------------------- ловец снов (SVG)
def catcher_inner():
    f = lambda v: f"{v:.1f}"
    cx, cy, R, n = 60, 58, 44, 10
    P = lambda r, a: (cx + r * math.cos(a), cy + r * math.sin(a))
    s = f'<path d="M{cx} 0V{cy - R}"/><circle cx="{cx}" cy="{cy}" r="{R}"/><circle cx="{cx}" cy="{cy}" r="{R - 4}" stroke-dasharray="1.2 3"/>'
    rs = [R - 4, R - 13, R - 21, R - 28, R - 34]
    layers = [[P(r, ((i + (0.5 if j % 2 else 0)) / n) * 2 * math.pi - math.pi / 2) for i in range(n)] for j, r in enumerate(rs)]
    for j in range(1, len(layers)):
        s += '<polygon points="' + " ".join(f"{f(p[0])},{f(p[1])}" for p in layers[j]) + '"/>'
    for j in range(len(layers) - 1):
        for i, p in enumerate(layers[j]):
            q1, q2 = layers[j + 1][i], layers[j + 1][(i - 1) % n]
            s += f'<path d="M{f(p[0])} {f(p[1])}L{f(q1[0])} {f(q1[1])}M{f(p[0])} {f(p[1])}L{f(q2[0])} {f(q2[1])}"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="2.4"/>'
    for d in (30, 150, 210, 330):
        p = P(R, math.radians(d))
        s += f'<circle cx="{f(p[0])}" cy="{f(p[1])}" r="2"/>'
    for dx, ln, k in ((-26, 62, 1), (0, 92, 2), (26, 70, 3)):
        y0 = cy + math.sqrt(R * R - dx * dx)
        s += f'<path d="M{cx + dx} {f(y0)}V{f(y0 + ln * .55)}"/><circle cx="{cx + dx}" cy="{f(y0 + ln * .22)}" r="2"/>'
        s += feather(cx + dx, y0 + ln * .55, ln * .5, (k - 2) * 4, k * .6)
    return s


def feather(x, y, ln, rot, delay):
    f = lambda v: f"{v:.1f}"
    w, a = ln * .17, ln * .3
    bars = ""
    for i in range(1, 6):
        yy = a + (ln - a) * i / 6
        k = w * (1 - abs(i - 3) / 4.5)
        bars += f"M0 {f(yy)}l{f(k)} {f(-ln * .06)}M0 {f(yy)}l{f(-k)} {f(-ln * .06)}"
    return (f'<g transform="translate({f(x)} {f(y)})"><g class="fth" style="--r:{rot}deg;animation-delay:{delay}s">'
            f'<path d="M0 0V{f(ln)}"/><path d="M0 {f(a)}C{f(w)} {f(ln * .45)} {f(w)} {f(ln * .8)} 0 {f(ln)}C{f(-w)} {f(ln * .8)} {f(-w)} {f(ln * .45)} 0 {f(a)}"/>'
            f'<path d="{bars}" stroke-width=".7"/></g></g>')


def catcher_svg(cls=""):
    return f'<svg class="art {cls}" viewBox="0 0 120 206" aria-hidden="true">{catcher_inner()}</svg>'


ICONS = {
    "stock": '<rect x="3.5" y="3.5" width="7" height="7" rx="3"/><rect x="13.5" y="3.5" width="7" height="7" rx="3"/><rect x="3.5" y="13.5" width="7" height="7" rx="3"/><rect x="13.5" y="13.5" width="7" height="7" rx="3"/>',
    "bag": '<path d="M5.5 8h13l-1 12h-11z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/>',
    "layers": '<path d="m12 3.5 9 4.8-9 4.8-9-4.8z"/><path d="m3 13 9 4.8 9-4.8"/>',
    "tool": '<path d="M14.7 6.3a4 4 0 0 0-5 5L3.5 17.5l3 3 6.2-6.2a4 4 0 0 0 5-5l-2.4 2.4-2.6-.6-.6-2.6z"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "tag": '<path d="M3.5 12V4.5H11l9.5 9.5-7 7z"/><circle cx="8" cy="9" r="1.2"/>',
    "archive": '<rect x="3" y="4.5" width="18" height="4.5" rx="1.8"/><path d="M5 9v10.5h14V9M10 13h4"/>',
    "phone": '<rect x="7" y="3" width="10" height="18" rx="2.5"/><path d="M11 17.5h2"/>',
    "book": '<path d="M4 5.5A2 2 0 0 1 6 3.5h13v15H6a2 2 0 0 0-2 2z"/><path d="M4 20.5v-15M8.5 8h6"/>',
    "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3 19.5c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5"/><circle cx="17" cy="9" r="2.4"/><path d="M17 14c2.5 0 4.5 1.6 4.5 4.5"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M21 20H3"/>',
    "user": '<circle cx="12" cy="8" r="3.5"/><path d="M5 20c0-3.6 3-6 7-6s7 2.4 7 6"/>',
    "chat": '<path d="M4 5.5h16v11H11l-4.5 3.5V16.5H4z"/>',
    "upload": '<path d="M12 16V4M7 9l5-5 5 5M4.5 20h15"/>',
    "cap": '<path d="m2.5 9 9.5-4.5L21.5 9 12 13.5z"/><path d="M6.5 11.5v4.5c0 1.2 2.5 2.5 5.5 2.5s5.5-1.3 5.5-2.5v-4.5M21.5 9v5.5"/>',
}


def icon(name):
    return f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


# ---------------------------------------------------------------- тексты
TEXTS = {
    "ru": {
        "path": "/", "label": "RU", "locale": "ru_RU",
        "title": "Melaymade: склад, закупки и себестоимость для мастериц handmade",
        "desc": "Фото-склад материалов, расчёт себестоимости с учётом брака и времени, рекомендуемая цена и архив работ. На телефоне и компьютере, даже без интернета.",
        "nav": ["Как это работает", "Возможности", "Вопросы"], "login": "Войти",
        "kicker": "для мастериц handmade",
        "h1": "Знай, сколько на самом деле стоит твоё изделие",
        "sub": "Melaymade ведёт склад материалов с фото, считает себестоимость с учётом брака, времени и инструмента и подсказывает цену, на которой ты зарабатываешь.",
        "cta": "Попробовать бесплатно", "cta2": "Как это работает",
        "note": "Без банковской карты. Работает на телефоне и компьютере, даже без интернета.",
        "how_title": "Три шага до честной цены",
        "steps": [
            ("Добавь материалы", "Сфотографируй, укажи количество и цену. Материалы сами попадут на склад, а доставка распределится по позициям."),
            ("Собери изделие", "Выбери материалы из галереи. Приложение резервирует их, учитывает брак, время и инструмент."),
            ("Узнай цену", "Получи себестоимость и рекомендуемую цену с учётом комиссии площадки, доставки и твоей прибыли."),
        ],
        "feat_title": "Всё, что нужно мастерице",
        "features": [
            ("stock", "Фото-склад", "Материалы в виде красивых карточек. Поиск по названию, цвету, размеру и артикулу."),
            ("bag", "Закупки в любой валюте", "Больше 40 валют. Доставка делится по позициям, средняя цена считается сама."),
            ("layers", "Резерв без списания", "Материал занят в работе, а со склада уходит только при завершении. Можно вести несколько работ сразу."),
            ("tool", "Брак и инструменты", "Брак считается отдельно. У инструмента есть стоимость каждого применения."),
            ("clock", "Таймер и труд", "Включи таймер или впиши время. Оплата труда считается по твоей ставке."),
            ("tag", "Рекомендуемая цена", "С учётом комиссии площадки, доставки покупателю и желаемой прибыли."),
            ("archive", "Архив и продажи", "Каждая работа с фото и составом. Кому и куда продано. Статистика по месяцам и годам."),
            ("phone", "Везде и без интернета", "Телефон, планшет, компьютер. Данные синхронизируются и доступны офлайн."),
        ],
        "gal_title": "Так выглядит приложение",
        "gal": ["Фото-склад", "Себестоимость и цена", "Продажи и статистика", "Архив работ"],
        "gal_alt": ["Экран фото-склада", "Экран расчёта себестоимости и цены", "Экран статистики продаж", "Экран работы в архиве"],
        "ui_note": "Интерфейс сейчас на русском. Турецкий и английский скоро.",
        "ac_kicker": "Скоро", "ac_title": "Академия: продавай свои уроки",
        "ac_text": "Курсы, ученицы и общий чат рядом с твоим складом. Сделай свою мастерскую ещё и школой.",
        "faq_title": "Частые вопросы",
        "faq": [
            ("Нужно ли ставить из магазина приложений?", "Нет. Открой приложение в браузере и добавь на главный экран. Оно работает как обычное."),
            ("Мои данные в безопасности?", "У каждой пользовательницы свой отдельный склад, другие его не видят. Данные хранятся в защищённом облаке в Европе (Париж)."),
            ("Работает ли без интернета?", "Да. Изменения сохраняются на устройстве и отправляются в облако, когда появится связь."),
            ("На каких языках?", "Сейчас на русском. Турецкий и английский готовим."),
            ("Сколько это стоит?", "Сначала пробный период, потом подписка. Тарифы скоро объявим."),
            ("Что будет, когда закончится подписка?", "Твои данные останутся, а сохранить копию можно в любой момент."),
        ],
        "final_title": "Начни с первой закупки",
        "final_text": "Создай аккаунт за минуту и посчитай своё первое изделие.",
        "final_cta": "Создать аккаунт",
        "footer": "© 2026 Melaymade. Сделано с любовью для мастериц.",
    },
    "tr": {
        "path": "/tr/", "label": "TR", "locale": "tr_TR",
        "title": "Melaymade: El işi ustaları için stok, alışveriş ve maliyet hesabı",
        "desc": "Fotoğraflı malzeme stoku, fire ve süreyi hesaba katan maliyet hesabı, önerilen fiyat ve iş arşivi. Telefonda ve bilgisayarda, internet olmadan da çalışır.",
        "nav": ["Nasıl çalışır?", "Özellikler", "Sık sorulanlar"], "login": "Giriş Yap",
        "kicker": "el işi ustaları için",
        "h1": "Ürününüzün gerçek maliyetini bilin",
        "sub": "Melaymade, malzeme stokunuzu fotoğraflarla tutar; fireyi, süreyi ve aletleri hesaba katarak maliyeti çıkarır ve kazanç sağlayacağınız fiyatı önerir.",
        "cta": "Ücretsiz Deneyin", "cta2": "Nasıl çalışır?",
        "note": "Banka kartı gerekmez. Telefonda ve bilgisayarda çalışır, internet olmadan da.",
        "how_title": "Doğru fiyata üç adımda",
        "steps": [
            ("Malzemeleri ekleyin", "Fotoğraf çekin, miktarı ve fiyatı girin. Malzemeler stoka kendiliğinden eklenir, kargo ücreti kalemlere dağıtılır."),
            ("Ürününüzü oluşturun", "Galeriden malzemeleri seçin. Uygulama malzemeleri ayırır; fireyi, süreyi ve aletleri hesaba katar."),
            ("Fiyatı öğrenin", "Pazar yeri komisyonunu, kargoyu ve istediğiniz kârı hesaba katan maliyeti ve önerilen fiyatı görün."),
        ],
        "feat_title": "Bir ustanın ihtiyaç duyduğu her şey",
        "features": [
            ("stock", "Fotoğraflı Malzeme Stoku", "Malzemeler şık kartlar halinde. Ada, renge, boyuta ve ürün koduna göre arama."),
            ("bag", "Her para biriminde alışveriş", "40'tan fazla para birimi. Kargo kalemlere dağıtılır, ortalama fiyat otomatik hesaplanır."),
            ("layers", "Stoktan düşmeden ayırma", "Malzeme işte ayrılır ama stoktan ancak iş tamamlanınca düşer. Aynı anda birden fazla iş yürütebilirsiniz."),
            ("tool", "Fire ve aletler", "Fire ayrı hesaplanır. Aletler için her kullanımın maliyeti eklenir."),
            ("clock", "Sayaç ve emek", "Sayacı başlatın ya da süreyi girin. İşçilik, saat ücretinize göre hesaplanır."),
            ("tag", "Önerilen fiyat", "Pazar yeri komisyonu, alıcıya kargo ve istediğiniz kâr hesaba katılır."),
            ("archive", "Arşiv ve satışlar", "Her iş fotoğrafı ve içeriğiyle saklanır. Kime ve nereye satıldığı. Aylık ve yıllık istatistik."),
            ("phone", "Her yerde, internetsiz de", "Telefon, tablet, bilgisayar. Veriler eşitlenir ve çevrimdışı da kullanılabilir."),
        ],
        "gal_title": "Uygulama böyle görünüyor",
        "gal": ["Fotoğraflı Malzeme Stoku", "Maliyet ve Fiyat", "Satışlar ve İstatistik", "İş Arşivi"],
        "gal_alt": ["Malzeme stoku ekranı", "Maliyet ve fiyat hesabı ekranı", "Satış istatistikleri ekranı", "Arşivdeki iş ekranı"],
        "ui_note": "Arayüz şu anda Rusça. Türkçe ve İngilizce çok yakında.",
        "ac_kicker": "Çok yakında", "ac_title": "Akademi: derslerinizi satın",
        "ac_text": "Kurslar, öğrenciler ve ortak sohbet, stokunuzun yanında. Atölyenizi bir okula da dönüştürün.",
        "faq_title": "Sık sorulan sorular",
        "faq": [
            ("Mağazadan indirmem gerekiyor mu?", "Hayır. Uygulamayı tarayıcıda açın ve ana ekrana ekleyin. Normal bir uygulama gibi çalışır."),
            ("Verilerim güvende mi?", "Her kullanıcının kendine ait ayrı bir stoku vardır, başkaları göremez. Veriler Avrupa'daki (Paris) güvenli bir bulutta saklanır."),
            ("İnternet olmadan çalışır mı?", "Evet. Değişiklikler cihazınıza kaydedilir ve bağlantı geldiğinde buluta gönderilir."),
            ("Hangi dillerde?", "Şu anda Rusça. Türkçe ve İngilizce hazırlanıyor."),
            ("Ne kadar?", "Önce deneme süresi, sonra abonelik. Fiyatları yakında duyuracağız."),
            ("Abonelik biterse ne olur?", "Verileriniz saklanır, istediğiniz zaman yedeğini alabilirsiniz."),
        ],
        "final_title": "İlk alışverişinizle başlayın",
        "final_text": "Bir dakikada hesap oluşturun ve ilk ürününüzün maliyetini hesaplayın.",
        "final_cta": "Hesap Oluştur",
        "footer": "© 2026 Melaymade. El işi ustaları için sevgiyle yapıldı.",
    },
    "en": {
        "path": "/en/", "label": "EN", "locale": "en_US",
        "title": "Melaymade: stock, purchases and pricing for handmade makers",
        "desc": "Photo inventory of your materials, cost calculation including waste and time, a recommended price and an archive of your work. On phone and computer, even offline.",
        "nav": ["How it works", "Features", "FAQ"], "login": "Log in",
        "kicker": "for handmade makers",
        "h1": "Know what your handmade piece really costs",
        "sub": "Melaymade keeps a photo inventory of your materials, calculates the cost including waste, time and tools, and suggests a price that actually earns you money.",
        "cta": "Try it free", "cta2": "How it works",
        "note": "No credit card needed. Works on phone and computer, even offline.",
        "how_title": "Three steps to an honest price",
        "steps": [
            ("Add your materials", "Take a photo, enter the quantity and price. Materials go to your stock automatically and shipping is split across items."),
            ("Build your piece", "Pick materials from the gallery. The app reserves them and accounts for waste, time and tools."),
            ("Find your price", "Get the cost and a recommended price that includes the marketplace fee, shipping and your profit."),
        ],
        "feat_title": "Everything a maker needs",
        "features": [
            ("stock", "Photo inventory", "Materials as beautiful cards. Search by name, colour, size and article number."),
            ("bag", "Purchases in any currency", "40+ currencies. Shipping is split across items and the average price is calculated for you."),
            ("layers", "Reserve without writing off", "Materials are held for a project but leave your stock only when it is finished. Run several projects at once."),
            ("tool", "Waste and tools", "Waste is tracked separately. Tools carry a cost per use."),
            ("clock", "Timer and labour", "Start the timer or type the time. Labour is calculated at your hourly rate."),
            ("tag", "Recommended price", "Includes the marketplace fee, shipping to the buyer and the profit you want."),
            ("archive", "Archive and sales", "Every project with its photo and materials. Who bought it and where it went. Statistics by month and year."),
            ("phone", "Everywhere, even offline", "Phone, tablet, computer. Data syncs and stays available offline."),
        ],
        "gal_title": "This is how the app looks",
        "gal": ["Photo inventory", "Cost and price", "Sales and statistics", "Project archive"],
        "gal_alt": ["Photo inventory screen", "Cost and price calculation screen", "Sales statistics screen", "Archived project screen"],
        "ui_note": "The interface is currently in Russian. Turkish and English are coming soon.",
        "ac_kicker": "Coming soon", "ac_title": "Academy: sell your own lessons",
        "ac_text": "Courses, students and a shared chat next to your stock. Turn your workshop into a school too.",
        "faq_title": "Frequently asked questions",
        "faq": [
            ("Do I need to install it from an app store?", "No. Open the app in your browser and add it to your home screen. It works like a regular app."),
            ("Is my data safe?", "Every user has their own separate stock that nobody else can see. Data is stored in a secure cloud in Europe (Paris)."),
            ("Does it work offline?", "Yes. Changes are saved on your device and sent to the cloud when you are back online."),
            ("Which languages are supported?", "Russian for now. Turkish and English are on the way."),
            ("How much does it cost?", "A trial first, then a subscription. We will announce pricing soon."),
            ("What happens when my subscription ends?", "Your data stays safe and you can save a copy of it at any time."),
        ],
        "final_title": "Start with your first purchase",
        "final_text": "Create an account in a minute and calculate your first piece.",
        "final_cta": "Create an account",
        "footer": "© 2026 Melaymade. Made with love for makers.",
    },
}

# ------------------------------------------------- Академия (дополнения к текстам)
ACADEMY = {
    "ru": {
        "title": "Melaymade: склад, цена и личная Академия для мастериц handmade",
        "desc": "Фото-склад материалов, расчёт себестоимости и цены, а ещё личная Академия: курсы, уроки и ученицы в одном приложении. На телефоне и компьютере.",
        "sub": "Melaymade ведёт склад материалов с фото, считает себестоимость и цену, на которой ты зарабатываешь, а ещё хранит твою личную Академию: уроки, ученицы и материалы в одном месте.",
        "nav": ["Как это работает", "Академия", "Возможности", "Вопросы"],
        "pill": "Новое · личная Академия для твоих уроков",
        "ac_badge": "Моя Академия · бета",
        "ac_h": "Твоя школа рукоделия в одном приложении",
        "ac_lead": "Обычно школа мастерицы живёт в пяти местах: чат, таблица, облако с фото, заметки и блокнот с закупками. Melaymade собирает всё вместе: уроки, материалы, ученицы и доход рядом со складом и расчётом цены.",
        "pain_title": "Знакомо?",
        "pains": [
            ("«А что покупать для урока?» в сотый раз", "Материалы прикрепляются к уроку прямо из твоего склада. Список всегда под рукой, а себестоимость урока считается сама."),
            ("Кто оплатил и на каком уроке остановилась?", "Ученицы, их доступ и прогресс собраны в одном списке. Без таблиц и разрозненных заметок."),
            ("Один урок, один вечер возни", "Мы делаем загрузку уроков на площадки для мастериц в одно нажатие. Пока это в разработке, но направление именно такое."),
        ],
        "ac_cta": "Собрать свою академию",
        "ac_cards": [
            ("book", "Курсы и уроки по полочкам", "Создавай курсы, добавляй уроки с описанием и публикуй, когда готово.", "ok"),
            ("layers", "Материалы прямо в уроке", "Прикрепи материалы со склада. Одним нажатием собери свою работу по уроку: резерв, расчёт и цена уже готовы.", "ok"),
            ("users", "Ученицы и их прогресс", "Веди список учениц, доступ к курсам и пройденные уроки. Всё вносишь ты.", "ok"),
            ("chart", "Доход от курсов", "Видно, сколько приносят курсы. Оплату от учениц ты принимаешь как сейчас, а в приложении отмечаешь покупку.", "ok"),
            ("user", "Личный кабинет ученицы", "Ученица заходит сама, смотрит уроки и отмечает свой прогресс.", "soon"),
            ("chat", "Общий чат курса", "Вопросы по уроку и общение учениц рядом с материалами.", "soon"),
        ],
        "b_ok": "Работает", "b_soon": "Скоро",
        "road_kick": "Развиваем дальше",
        "road_title": "Следующий шаг: уроки на площадки в одно нажатие",
        "road_text": "Ты готовишь урок один раз, а мы отправляем его на площадки для мастериц, где ты хочешь продавать. Без переписывания и повторных загрузок. Сейчас это в разработке, сроки назовём, когда будем уверены. Какие площадки нужны тебе, решим вместе.",
        "ac_note": "Честно: сейчас в Академии ты сама ведёшь курсы, уроки, учениц и доход, а ученицы пока не заходят в приложение. Всё, что помечено «Скоро», в разработке.",
        "features_extra": ("book", "Личная Академия", "Курсы, уроки с материалами и ученицы рядом со складом. Раздел развивается."),
        "faq_extra": [
            ("Что такое Академия?", "Раздел «Моя Академия» — твоя личная школа внутри Melaymade: курсы, уроки с материалами со склада, ученицы и доход от курсов. Всё рядом с расчётом себестоимости."),
            ("Смогут ли ученицы учиться прямо в приложении?", "Пока нет: сейчас ты сама ведёшь учениц и их прогресс. Личный кабинет ученицы и общий чат курса в разработке."),
            ("Можно ли загружать уроки на площадки?", "Это в планах: загрузка уроков на площадки для мастериц в одно нажатие. Сейчас в разработке, точные сроки пока не назовём."),
        ],
        "final_title": "Начни со склада, а потом собери первый курс",
        "final_text": "Создай аккаунт за минуту: посчитай своё первое изделие и собери первый курс в своей Академии.",
    },
    "tr": {
        "title": "Melaymade: El işi ustaları için stok, fiyat ve kişisel Akademi",
        "desc": "Fotoğraflı malzeme stoku, maliyet ve fiyat hesabı, ayrıca kişisel Akademi: kurslar, dersler ve öğrenciler tek uygulamada. Telefonda ve bilgisayarda.",
        "sub": "Melaymade malzeme stokunuzu fotoğraflarla tutar, maliyeti ve kazanç sağlayacağınız fiyatı hesaplar; ayrıca kişisel Akademinizi barındırır: dersler, öğrenciler ve malzemeler tek yerde.",
        "nav": ["Nasıl çalışır?", "Akademi", "Özellikler", "Sık sorulanlar"],
        "pill": "Yeni · dersleriniz için kişisel Akademi",
        "ac_badge": "Akademim · beta",
        "ac_h": "El işi okulunuz tek uygulamada",
        "ac_lead": "Bir ustanın okulu çoğu zaman beş ayrı yerde yaşar: sohbet, tablo, fotoğraf bulutu, notlar ve alışveriş defteri. Melaymade hepsini bir araya getirir: dersler, malzemeler, öğrenciler ve gelir; stokunuzun ve fiyat hesabının yanında.",
        "pain_title": "Tanıdık geliyor mu?",
        "pains": [
            ("«Ders için ne almalıyım?» yüzüncü kez", "Malzemeler doğrudan stokunuzdan derse eklenir. Liste her zaman elinizin altında, dersin maliyeti kendiliğinden hesaplanır."),
            ("Kim ödedi, hangi derste kaldı?", "Öğrenciler, erişimleri ve ilerlemeleri tek listede. Tablolara ve dağınık notlara gerek yok."),
            ("Bir ders, bir akşam uğraş", "Derslerinizi el işi ustalarının platformlarına tek dokunuşla yüklemek için çalışıyoruz. Henüz geliştirme aşamasında, ama yön tam olarak bu."),
        ],
        "ac_cta": "Akademinizi Kurun",
        "ac_cards": [
            ("book", "Kurslar ve dersler düzenli", "Kurs oluşturun, açıklamalı dersler ekleyin, hazır olunca yayınlayın.", "ok"),
            ("layers", "Malzemeler dersin içinde", "Derse stoktan malzeme ekleyin. Tek dokunuşla dersteki işinizi oluşturun: ayırma, hesap ve fiyat hazır.", "ok"),
            ("users", "Öğrenciler ve ilerlemeleri", "Öğrenci listesini, kurslara erişimi ve tamamlanan dersleri tutun. Hepsini siz girersiniz.", "ok"),
            ("chart", "Kurs geliri", "Kursların ne kazandırdığını görün. Öğrencilerden ödemeyi şimdiki gibi siz alırsınız, uygulamada satın alımı işaretlersiniz.", "ok"),
            ("user", "Öğrenci hesabı", "Öğrenci kendisi giriş yapar, dersleri izler ve ilerlemesini işaretler.", "soon"),
            ("chat", "Kurs sohbeti", "Ders soruları ve öğrenci sohbeti malzemelerin yanında.", "soon"),
        ],
        "b_ok": "Hazır", "b_soon": "Yakında",
        "road_kick": "Gelişmeye devam ediyoruz",
        "road_title": "Sıradaki adım: dersler tek dokunuşla platformlara",
        "road_text": "Dersi bir kez hazırlarsınız; biz de satış yapmak istediğiniz el işi platformlarına göndeririz. Yeniden yazmak ve tekrar yüklemek yok. Şu anda geliştirme aşamasında, tarihi kesinleşince duyuracağız. Hangi platformları istediğinizi birlikte belirleriz.",
        "ac_note": "Dürüst olalım: şu anda Akademi'de kursları, dersleri, öğrencileri ve geliri siz yönetirsiniz; öğrenciler henüz uygulamaya giriş yapmaz. «Yakında» işaretli her şey geliştirme aşamasındadır.",
        "features_extra": ("book", "Kişisel Akademi", "Kurslar, malzemeli dersler ve öğrenciler stokunuzun yanında. Bölüm gelişmeye devam ediyor."),
        "faq_extra": [
            ("Akademi nedir?", "«Akademim» bölümü, Melaymade içindeki kişisel okulunuzdur: kurslar, stoktan malzemeli dersler, öğrenciler ve kurs geliri. Hepsi maliyet hesabının yanında."),
            ("Öğrenciler doğrudan uygulamada öğrenebilir mi?", "Henüz değil: şu anda öğrencileri ve ilerlemelerini siz takip edersiniz. Öğrenci hesabı ve kurs sohbeti geliştirme aşamasında."),
            ("Dersleri platformlara yükleyebilir miyim?", "Planlarımızda var: dersleri el işi ustalarının platformlarına tek dokunuşla yüklemek. Geliştirme aşamasında, kesin tarih vermiyoruz."),
        ],
        "final_title": "Stokla başlayın, ilk kursunuzu kurun",
        "final_text": "Bir dakikada hesap oluşturun: ilk ürününüzün maliyetini hesaplayın ve Akademinizde ilk kursunuzu oluşturun.",
    },
    "en": {
        "title": "Melaymade: stock, pricing and a personal Academy for handmade makers",
        "desc": "Photo inventory, cost and price calculation, plus a personal Academy: courses, lessons and students in one app. On phone and computer.",
        "sub": "Melaymade keeps a photo inventory of your materials, calculates your cost and a price that earns you money, and hosts your personal Academy: lessons, students and materials in one place.",
        "nav": ["How it works", "Academy", "Features", "FAQ"],
        "pill": "New · your personal Academy for your lessons",
        "ac_badge": "My Academy · beta",
        "ac_h": "Your craft school, in one app",
        "ac_lead": "A maker's school usually lives in five places: a chat, a spreadsheet, a cloud with photos, notes and a shopping notebook. Melaymade brings it together: lessons, materials, students and income, right next to your stock and pricing.",
        "pain_title": "Sound familiar?",
        "pains": [
            ("“What do I buy for the lesson?” for the hundredth time", "Attach materials to a lesson straight from your stock. The list is always at hand and the lesson cost calculates itself."),
            ("Who paid, and which lesson are they on?", "Students, their access and progress in one list. No spreadsheets or scattered notes."),
            ("One lesson, one evening of uploading", "We are working on uploading your lessons to handmade platforms in one tap. It is still in development, but that is exactly where we are heading."),
        ],
        "ac_cta": "Build your academy",
        "ac_cards": [
            ("book", "Courses and lessons, neatly shelved", "Create courses, add lessons with descriptions and publish when ready.", "ok"),
            ("layers", "Materials right in the lesson", "Attach materials from your stock. Build your own piece from a lesson in one tap: reserve, cost and price are ready.", "ok"),
            ("users", "Students and their progress", "Keep a list of students, their course access and completed lessons. You enter everything yourself.", "ok"),
            ("chart", "Course income", "See what your courses earn. You collect payments from students as you do now and mark the purchase in the app.", "ok"),
            ("user", "Student account", "Students sign in themselves, watch lessons and mark their progress.", "soon"),
            ("chat", "Shared course chat", "Lesson questions and student conversation next to the materials.", "soon"),
        ],
        "b_ok": "Available", "b_soon": "Coming soon",
        "road_kick": "What we are building next",
        "road_title": "Next: lessons to platforms in one tap",
        "road_text": "Prepare a lesson once and we send it to the handmade platforms where you want to sell. No retyping, no repeat uploads. This is in development and we will share dates once we are sure. Which platforms matter to you, we will decide together.",
        "ac_note": "To be honest: right now in the Academy you run courses, lessons, students and income yourself, and students do not sign in to the app yet. Everything marked “Coming soon” is in development.",
        "features_extra": ("book", "Personal Academy", "Courses, lessons with materials and students next to your stock. This section keeps growing."),
        "faq_extra": [
            ("What is the Academy?", "“My Academy” is your personal school inside Melaymade: courses, lessons with materials from your stock, students and course income. All next to your cost calculation."),
            ("Can students learn right in the app?", "Not yet: for now you manage students and their progress yourself. A student account and a shared course chat are in development."),
            ("Can I upload lessons to platforms?", "It is planned: uploading lessons to handmade platforms in one tap. It is in development and we are not giving exact dates yet."),
        ],
        "final_title": "Start with your stock, then build your first course",
        "final_text": "Create an account in a minute: calculate your first piece and build your first course in your Academy.",
    },
}
for _c, _a in ACADEMY.items():
    _t = TEXTS[_c]
    for _k in ("title", "desc", "sub", "nav", "final_title", "final_text"):
        _t[_k] = _a[_k]
    _t["features"] = list(_t["features"]) + [_a["features_extra"]]
    _t["faq"] = list(_a["faq_extra"]) + list(_t["faq"])
    _t["ac"] = _a

CSS = """
:root{--bg:#F1E8D6;--surface:#FAF4E7;--surface2:#EDE1CA;--line:#D9C7A6;--ink:#33291F;--ink2:#645644;--clay:#A64F2E;--clay-ink:#FFF6EA;--clay-soft:#EFD3C0;--accent:#3E6150;--accent-soft:#D3E0D4;--ochre:#C98F27;--art:#8B6B45;--glass:color-mix(in srgb,var(--surface) 90%,transparent);--shadow:0 2px 4px rgba(74,59,44,.08),0 24px 60px rgba(74,59,44,.2)}
@media (prefers-color-scheme:dark){:root{--bg:#17120D;--surface:#221B14;--surface2:#2B231A;--line:#3B3024;--ink:#F1E6D2;--ink2:#C2B297;--clay:#D8805A;--clay-ink:#2A130A;--clay-soft:#4A281C;--accent:#A5BD8F;--accent-soft:#2A3523;--ochre:#E2B25A;--art:#C7A877;--shadow:0 2px 4px rgba(0,0,0,.4),0 24px 60px rgba(0,0,0,.55);color-scheme:dark}}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font-family:'Nunito',system-ui,-apple-system,'Segoe UI',sans-serif;font-size:17px;line-height:1.55;-webkit-text-size-adjust:100%}
h1,h2,h3,p{margin:0}
a{color:inherit}
img{max-width:100%;height:auto;display:block}
.wrap{width:100%;max-width:1080px;margin:0 auto;padding-left:max(20px,env(safe-area-inset-left,0px));padding-right:max(20px,env(safe-area-inset-right,0px))}
.ic{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;flex:none}
.art{fill:none;stroke:var(--art);stroke-width:1.1;stroke-linecap:round;stroke-linejoin:round}
.fth{transform-box:fill-box;transform-origin:50% 0;transform:rotate(var(--r,0deg));animation:flutter 4.5s ease-in-out infinite alternate}
@keyframes flutter{from{transform:rotate(calc(var(--r,0deg) - 5deg))}to{transform:rotate(calc(var(--r,0deg) + 5deg))}}
@keyframes hang{from{transform:rotate(-2.2deg)}to{transform:rotate(2.6deg)}}
@keyframes floatin{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
.hdr{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.hdr .wrap{display:flex;align-items:center;gap:16px;min-height:64px}
.brand{display:flex;align-items:center;gap:10px;font-family:'Forum','Cormorant Garamond',Georgia,serif;font-size:19px;letter-spacing:.14em;color:var(--clay);text-decoration:none}
.brand svg{width:26px;height:26px;color:var(--accent)}
.nav{display:none;gap:24px;margin-left:24px;font-weight:600;font-size:15px}
.nav a{text-decoration:none;color:var(--ink2)}
.nav a:hover{color:var(--clay)}
.sp{flex:1}
.lang{display:flex;gap:2px;background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:3px}
.lang a{padding:4px 10px;border-radius:999px;font-size:13px;font-weight:700;text-decoration:none;color:var(--ink2)}
.lang a.on{background:var(--clay);color:var(--clay-ink)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:48px;padding:0 24px;border-radius:16px;font-weight:800;font-size:16px;text-decoration:none;border:1.5px solid var(--line);background:var(--surface);transition:transform .15s,box-shadow .2s}
.btn:hover{transform:translateY(-2px);box-shadow:0 10px 24px rgba(120,86,50,.18)}
.btn.pri{background:var(--clay);color:var(--clay-ink);border-color:var(--clay)}
.btn.sm{white-space:nowrap;min-height:40px;padding:0 16px;font-size:14px;border-radius:12px}
.hero{position:relative;overflow:hidden;padding:48px 0 64px}
.hero .wrap{display:grid;gap:40px;position:relative;z-index:1}
.kick{font-size:12px;font-weight:800;letter-spacing:.18em;text-transform:uppercase;color:var(--clay);margin-bottom:14px;display:block}
h1{font-family:'Cormorant','Cormorant Garamond',Georgia,serif;font-style:italic;font-weight:600;font-size:clamp(38px,8vw,64px);line-height:1.04;letter-spacing:-.01em;text-wrap:balance}
.sub{font-size:19px;color:var(--ink2);margin-top:20px;max-width:34em}
.cta{display:flex;flex-wrap:wrap;gap:12px;margin-top:28px}
.note{margin-top:16px;font-size:14px;color:var(--ink2)}
.phone{width:min(290px,76vw);margin:0 auto;border-radius:34px;overflow:hidden;border:6px solid var(--surface);box-shadow:var(--shadow);background:var(--surface)}
.herovis{position:relative;display:flex;justify-content:center;align-items:flex-start;animation:floatin .8s .1s both}
.herovis .art{position:absolute;width:210px;top:-40px;right:2%;opacity:.55;transform-origin:50% 0;animation:hang 7s ease-in-out infinite alternate;z-index:0}
.herovis .phone{position:relative;z-index:1}
section{padding:64px 0}
h2{font-family:'Cormorant','Cormorant Garamond',Georgia,serif;font-style:italic;font-weight:600;font-size:clamp(30px,5vw,42px);line-height:1.1;margin-bottom:12px}
h2::after{content:"";display:block;width:66px;height:10px;margin-top:10px;background:var(--ochre);-webkit-mask:url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 66 10'%3E%3Cpath d='M0 5h24M42 5h24' stroke='black' stroke-width='1.2'/%3E%3Cpath d='M33 0.5l4.5 4.5-4.5 4.5-4.5-4.5z' fill='black'/%3E%3C/svg%3E") left center/contain no-repeat;mask:url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 66 10'%3E%3Cpath d='M0 5h24M42 5h24' stroke='black' stroke-width='1.2'/%3E%3Cpath d='M33 0.5l4.5 4.5-4.5 4.5-4.5-4.5z' fill='black'/%3E%3C/svg%3E") left center/contain no-repeat}
.grid{display:grid;gap:16px;margin-top:32px}
.card{background:var(--glass);border:1.5px solid var(--line);border-radius:24px;padding:24px}
.step .n{width:40px;height:40px;border-radius:50%;background:var(--clay-soft);color:var(--clay);display:grid;place-items:center;font-weight:800;margin-bottom:14px}
.card h3{font-size:19px;font-weight:800;margin-bottom:6px}
.card p{color:var(--ink2);font-size:16px}
.feat .ic{width:30px;height:30px;color:var(--accent);margin-bottom:12px}
.alt{background:var(--surface2)}
.gallery{display:flex;gap:20px;overflow-x:auto;scroll-snap-type:x mandatory;padding:32px 20px 12px;margin:0 -20px;scrollbar-width:thin}
.gallery figure{margin:0;flex:none;width:min(260px,70vw);scroll-snap-align:center}
.gallery .phone{width:100%}
.gallery figcaption{text-align:center;font-weight:700;margin-top:14px;font-size:15px}
.uinote{font-size:14px;color:var(--ink2);margin-top:8px}
.ac{position:relative;border-radius:32px;background:var(--glass);border:1.5px dashed var(--line);padding:40px 28px;text-align:center}
.ac p{color:var(--ink2);max-width:30em;margin:0 auto}
details{background:var(--glass);border:1.5px solid var(--line);border-radius:18px;padding:16px 20px;margin-top:12px}
summary{cursor:pointer;font-weight:800;list-style:none;display:flex;justify-content:space-between;gap:12px}
summary::-webkit-details-marker{display:none}
summary::after{content:"+";color:var(--clay);font-size:22px;line-height:1}
details[open] summary::after{content:"\\2212"}
details p{margin-top:10px;color:var(--ink2);font-size:16px}
.final{text-align:center;position:relative;overflow:hidden}
.final p{color:var(--ink2);margin:0 auto 24px;max-width:28em}
.final h2::after{margin-left:auto;margin-right:auto;-webkit-mask-position:center;mask-position:center}
footer{padding:32px 0 48px;color:var(--ink2);font-size:14px;text-align:center;border-top:1px solid var(--line)}
:focus-visible{outline:2px solid var(--clay);outline-offset:3px}
.pill{display:inline-flex;align-items:center;gap:8px;padding:7px 16px 7px 11px;border-radius:999px;background:var(--clay-soft);color:var(--clay);font-weight:800;font-size:13px;text-decoration:none;margin-bottom:18px;line-height:1.3}
.pill .ic{width:18px;height:18px}
.acad{position:relative;overflow:hidden;background:linear-gradient(180deg,var(--accent-soft) 0%,var(--bg) 100%)}
.acad .top{display:grid;gap:40px;align-items:center}
.acad .badge{display:inline-flex;align-items:center;gap:8px;font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);border:1.5px solid var(--accent);border-radius:999px;padding:5px 14px;margin-bottom:16px}
.acad h2.big{font-size:clamp(34px,6.4vw,54px);line-height:1.04}
.acad .lead{font-size:19px;color:var(--ink2);margin-top:6px;max-width:34em}
.acad .vis{display:flex;gap:16px;justify-content:center;align-items:flex-start}
.acad .vis .phone{width:min(210px,42vw)}
.acad .vis .phone+.phone{margin-top:48px}
.acad h3.sec{font-family:'Cormorant','Cormorant Garamond',Georgia,serif;font-style:italic;font-weight:600;font-size:clamp(26px,4.4vw,34px);margin:56px 0 0;color:var(--clay)}
.pains .card{border-style:dashed;background:var(--surface)}
.pains q{display:block;quotes:none;font-family:'Cormorant','Cormorant Garamond',Georgia,serif;font-style:italic;font-weight:600;font-size:23px;line-height:1.2;color:var(--clay);margin-bottom:10px}
.acard{position:relative}
.acard .st{position:absolute;top:18px;right:18px;font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;padding:3px 10px;border-radius:999px}
.acard .st.ok{background:var(--accent-soft);color:var(--accent)}
.acard .st.soon{background:var(--clay-soft);color:var(--clay)}
.acard.soon{border-style:dashed}
.road{margin-top:32px;border-radius:28px;padding:32px 28px;background:var(--surface);border:1.5px solid var(--ochre);display:grid;gap:18px;box-shadow:var(--shadow)}
.road .ic{width:38px;height:38px;color:var(--ochre)}
.road .kick{margin-bottom:6px}
.road h3{font-family:'Cormorant','Cormorant Garamond',Georgia,serif;font-style:italic;font-weight:600;font-size:clamp(26px,4.6vw,36px);line-height:1.1;margin-bottom:10px}
.road p{color:var(--ink2)}
.acnote{margin-top:20px;font-size:14px;color:var(--ink2);max-width:46em}
.acad .cta{margin-top:32px}
@media (max-width:560px){.hdr .wrap{gap:10px;min-height:60px}.brand{font-size:15px;letter-spacing:.1em;gap:7px}.brand svg{width:22px;height:22px}.lang a{padding:4px 8px;font-size:12px}.btn.sm{padding:0 12px;min-height:38px;font-size:13px}.herovis .art{width:150px;right:-4%}}
@media (min-width:860px){
  .nav{display:flex}
  .hero{padding:80px 0 96px}
  .hero .wrap{grid-template-columns:1.1fr .9fr;align-items:center}
  .grid.three{grid-template-columns:repeat(3,1fr)}
  .grid.four{grid-template-columns:repeat(4,1fr)}
  .gallery{justify-content:center;overflow:visible;margin:0;padding:32px 0 12px}
  .acad .top{grid-template-columns:1.1fr .9fr}
  .road{grid-template-columns:auto 1fr;gap:28px;align-items:center;padding:36px 40px}
}
@media (min-width:640px) and (max-width:859px){.grid.four{grid-template-columns:repeat(2,1fr)}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}html{scroll-behavior:auto}}
"""

REDIRECT_JS = """<script>
(function(){try{
  var saved=localStorage.getItem('mm-lang');
  if(!saved){var l=(navigator.language||'').slice(0,2).toLowerCase();
    var ru=['ru','uk','be','kk','ky','uz','tg','hy','az','ka'];
    var want=l==='tr'?'tr':(!l||ru.indexOf(l)>-1?'ru':'en');
    if(want==='tr')location.replace('/tr/');else if(want==='en')location.replace('/en/');}
  else if(saved==='tr')location.replace('/tr/');else if(saved==='en')location.replace('/en/');
}catch(e){}})();
</script>"""

FAV = '<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png"><link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">'


def esc(s):
    return html.escape(s, quote=True)


def render(code):
    t = TEXTS[code]
    langs = "".join(
        f'<a href="{TEXTS[c]["path"]}" hreflang="{c}" lang="{c}" class="{"on" if c == code else ""}" onclick="try{{localStorage.setItem(\'mm-lang\',\'{c}\')}}catch(e){{}}">{TEXTS[c]["label"]}</a>'
        for c in ("ru", "tr", "en"))
    alts = "".join(f'<link rel="alternate" hreflang="{c}" href="{BASE}{TEXTS[c]["path"]}">' for c in ("ru", "tr", "en"))
    alts += f'<link rel="alternate" hreflang="x-default" href="{BASE}/">'
    steps = "".join(f'<div class="card step"><div class="n">{i + 1}</div><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for i, (a, b) in enumerate(t["steps"]))
    feats = "".join(f'<div class="card feat">{icon(ic)}<h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for ic, a, b in t["features"])
    imgs = ["stock", "price", "stats", "archive"]
    gal = "".join(
        f'<figure><div class="phone"><img src="/img/{n}.jpg" width="780" height="1688" loading="lazy" alt="{esc(t["gal_alt"][i])}"></div><figcaption>{esc(t["gal"][i])}</figcaption></figure>'
        for i, n in enumerate(imgs))
    faq = "".join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in t["faq"])
    nav = f'<a href="#how">{esc(t["nav"][0])}</a><a href="#academy">{esc(t["nav"][1])}</a><a href="#features">{esc(t["nav"][2])}</a><a href="#faq">{esc(t["nav"][3])}</a>'
    a = t["ac"]
    pains = "".join(f'<div class="card"><q>{esc(q)}</q><p>{esc(x)}</p></div>' for q, x in a["pains"])
    acards = "".join(
        f'<div class="card feat acard {st}">{icon(ic)}<span class="st {st}">{esc(a["b_ok"] if st == "ok" else a["b_soon"])}</span><h3>{esc(ti)}</h3><p>{esc(tx)}</p></div>'
        for ic, ti, tx, st in a["ac_cards"])
    redirect = REDIRECT_JS if code == "ru" else ""
    brand_icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="9" r="6"/><circle cx="12" cy="9" r="2.6"/><path d="M12 3v12M6 9h12M9.5 15v5M12 15.5V22M14.5 15v4"/></svg>'
    return f"""<!doctype html>
<html lang="{code}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(t["title"])}</title>
<meta name="description" content="{esc(t["desc"])}">
<link rel="canonical" href="{BASE}{t["path"]}">
{alts}
<meta property="og:type" content="website"><meta property="og:site_name" content="Melaymade">
<meta property="og:title" content="{esc(t["title"])}"><meta property="og:description" content="{esc(t["desc"])}">
<meta property="og:url" content="{BASE}{t["path"]}"><meta property="og:image" content="{BASE}/og.png"><meta property="og:locale" content="{t["locale"]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F1E8D6" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#17120D" media="(prefers-color-scheme: dark)">
{FAV}
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,500;0,600;1,500;1,600&family=Forum&family=Nunito:wght@400;600;700;800&display=swap">
<style>{CSS}</style>
{redirect}
</head>
<body>
<header class="hdr"><div class="wrap">
  <a class="brand" href="{t["path"]}">{brand_icon}MELAYMADE</a>
  <nav class="nav" aria-label="Menu">{nav}</nav><span class="sp"></span>
  <div class="lang" role="navigation" aria-label="Language">{langs}</div>
  <a class="btn sm" href="{APP}">{esc(t["login"])}</a>
</div></header>
<main>
<section class="hero"><div class="wrap">
  <div>
    <a class="pill" href="#academy">{icon("cap")}{esc(a["pill"])}</a>
    <span class="kick">{esc(t["kicker"])}</span>
    <h1>{esc(t["h1"])}</h1>
    <p class="sub">{esc(t["sub"])}</p>
    <div class="cta"><a class="btn pri" href="{APP}">{esc(t["cta"])}</a><a class="btn" href="#how">{esc(t["cta2"])}</a></div>
    <p class="note">{esc(t["note"])}</p>
  </div>
  <div class="herovis">{catcher_svg()}<div class="phone"><img src="/img/stock.jpg" width="780" height="1688" alt="{esc(t["gal_alt"][0])}"></div></div>
</div></section>
<section id="how"><div class="wrap">
  <h2>{esc(t["how_title"])}</h2>
  <div class="grid three">{steps}</div>
</div></section>
<section id="academy" class="acad"><div class="wrap">
  <div class="top">
    <div>
      <span class="badge">{icon("cap")}{esc(a["ac_badge"])}</span>
      <h2 class="big">{esc(a["ac_h"])}</h2>
      <p class="lead">{esc(a["ac_lead"])}</p>
      <div class="cta"><a class="btn pri" href="{APP}">{esc(a["ac_cta"])}</a></div>
    </div>
    <div class="vis"><div class="phone"><img src="/img/academy.jpg" width="780" height="1688" loading="lazy" alt="{esc(a["ac_badge"])}"></div><div class="phone"><img src="/img/lesson.jpg" width="780" height="1688" loading="lazy" alt="{esc(a["ac_cards"][1][1])}"></div></div>
  </div>
  <h3 class="sec">{esc(a["pain_title"])}</h3>
  <div class="grid three pains">{pains}</div>
  <div class="grid three">{acards}</div>
  <div class="road">{icon("upload")}<div><span class="kick">{esc(a["road_kick"])}</span><h3>{esc(a["road_title"])}</h3><p>{esc(a["road_text"])}</p></div></div>
  <p class="acnote">{esc(a["ac_note"])}</p>
</div></section>
<section id="features" class="alt"><div class="wrap">
  <h2>{esc(t["feat_title"])}</h2>
  <div class="grid three">{feats}</div>
</div></section>
<section><div class="wrap">
  <h2>{esc(t["gal_title"])}</h2>
  <div class="gallery">{gal}</div>
  <p class="uinote">{esc(t["ui_note"])}</p>
</div></section>
<section id="faq"><div class="wrap">
  <h2>{esc(t["faq_title"])}</h2>
  {faq}
</div></section>
<section class="final"><div class="wrap">
  <h2>{esc(t["final_title"])}</h2>
  <p>{esc(t["final_text"])}</p>
  <a class="btn pri" href="{APP}">{esc(t["final_cta"])}</a>
</div></section>
</main>
<footer><div class="wrap">{esc(t["footer"])}</div></footer>
</body>
</html>
"""


def main():
    for code, t in TEXTS.items():
        d = OUT if code == "ru" else OUT / code
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(render(code), encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    urls = "".join(
        f'<url><loc>{BASE}{TEXTS[c]["path"]}</loc>' + "".join(
            f'<xhtml:link rel="alternate" hreflang="{o}" href="{BASE}{TEXTS[o]["path"]}"/>' for o in ("ru", "tr", "en")) + "</url>"
        for c in ("ru", "tr", "en"))
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + urls + "</urlset>\n", encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print("Готово: landing/ собрана (ru, tr, en)")


if __name__ == "__main__":
    main()
