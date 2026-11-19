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
    "camera": '<path d="M4 8.5h3l1.6-2.5h6.8L17 8.5h3v11H4z"/><circle cx="12" cy="14" r="3.5"/>',
    "ruler": '<path d="M3.5 15.5 15.5 3.5l5 5-12 12z"/><path d="m7 12 2 2M10 9l2 2M13 6l2 2"/>',
    "coin": '<circle cx="12" cy="12" r="8.5"/><path d="M14.8 9.4c-.6-1-1.7-1.6-2.9-1.6-1.6 0-2.8.9-2.8 2.1 0 2.9 5.8 1.4 5.8 4.3 0 1.2-1.2 2.2-2.9 2.2-1.3 0-2.4-.6-3-1.7M12 6v1.8M12 16.2V18"/>',
    "sliders": '<path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>',
    "cap": '<path d="m2.5 9 9.5-4.5L21.5 9 12 13.5z"/><path d="M6.5 11.5v4.5c0 1.2 2.5 2.5 5.5 2.5s5.5-1.3 5.5-2.5v-4.5M21.5 9v5.5"/>',
}


def icon(name):
    return f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


# ---------------------------------------------------------------- тексты
TEXTS = {
    "ru": {
        "path": "/", "label": "RU", "locale": "ru_RU",
        "title": "Melaymade | Моя мастерская: склад, закупки и себестоимость для мастериц handmade",
        "desc": "Фото-склад материалов, расчёт себестоимости с учётом брака и времени, рекомендуемая цена и архив работ. На телефоне и компьютере, даже без интернета.",
        "nav": ["Как это работает", "Возможности", "Вопросы"], "login": "Войти",
        "kicker": "приложение от Melaymade",
        "h1": "Знай, сколько на самом деле стоит твоё изделие",
        "sub": "«Моя мастерская» ведёт склад материалов с фото, считает себестоимость с учётом брака, времени и инструмента и подсказывает цену, на которой ты зарабатываешь.",
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
        "ui_note": "Приложение работает на русском, турецком и английском.",
        "ac_kicker": "Скоро", "ac_title": "Академия: продавай свои уроки",
        "ac_text": "Курсы, ученицы и общий чат рядом с твоим складом. Сделай свою мастерскую ещё и школой.",
        "faq_title": "Частые вопросы",
        "faq": [
            ("Нужно ли ставить из магазина приложений?", "Нет. Открой приложение в браузере и добавь на главный экран. Оно работает как обычное."),
            ("Мои данные в безопасности?", "У каждой пользовательницы свой отдельный склад, другие его не видят. Данные хранятся в защищённом облаке в Европе (Париж)."),
            ("Работает ли без интернета?", "Да. Изменения сохраняются на устройстве и отправляются в облако, когда появится связь."),
            ("На каких языках?", "На русском, турецком и английском. Язык выбирается на экране входа и в разделе «Ещё»."),
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
        "title": "Melaymade | Atölyem: El işi ustaları için stok, alışveriş ve maliyet hesabı",
        "desc": "Fotoğraflı malzeme stoğu, fire ve süreyi hesaba katan maliyet hesabı, önerilen fiyat ve iş arşivi. Telefonda ve bilgisayarda, internet olmadan da çalışır.",
        "nav": ["Nasıl çalışır?", "Özellikler", "Sık sorulanlar"], "login": "Giriş Yap",
        "kicker": "Melaymade uygulaması",
        "h1": "Ürününüzün gerçek maliyetini bilin",
        "sub": "Atölyem, malzeme stoğunuzu fotoğraflarla tutar; fireyi, süreyi ve aletleri hesaba katarak maliyeti çıkarır ve kazanç sağlayacağınız fiyatı önerir.",
        "cta": "Ücretsiz Deneyin", "cta2": "Nasıl çalışır?",
        "note": "Banka kartı gerekmez. Telefonda ve bilgisayarda çalışır, internet olmadan da.",
        "how_title": "Doğru fiyata üç adımda",
        "steps": [
            ("Malzemeleri ekleyin", "Fotoğraf çekin, miktarı ve fiyatı girin. Malzemeler stoğa kendiliğinden eklenir, kargo ücreti kalemlere dağıtılır."),
            ("Ürününüzü oluşturun", "Galeriden malzemeleri seçin. Uygulama malzemeleri ayırır; fireyi, süreyi ve aletleri hesaba katar."),
            ("Fiyatı öğrenin", "Pazar yeri komisyonunu, kargoyu ve istediğiniz kârı hesaba katan maliyeti ve önerilen fiyatı görün."),
        ],
        "feat_title": "Bir ustanın ihtiyaç duyduğu her şey",
        "features": [
            ("stock", "Fotoğraflı Malzeme Stoğu", "Malzemeler şık kartlar halinde. Ada, renge, boyuta ve ürün koduna göre arama."),
            ("bag", "Her para biriminde alışveriş", "40'tan fazla para birimi. Kargo kalemlere dağıtılır, ortalama fiyat otomatik hesaplanır."),
            ("layers", "Stoktan düşmeden ayırma", "Malzeme işte ayrılır ama stoktan ancak iş tamamlanınca düşer. Aynı anda birden fazla iş yürütebilirsiniz."),
            ("tool", "Fire ve aletler", "Fire ayrı hesaplanır. Aletler için her kullanımın maliyeti eklenir."),
            ("clock", "Sayaç ve emek", "Sayacı başlatın ya da süreyi girin. İşçilik, saat ücretinize göre hesaplanır."),
            ("tag", "Önerilen fiyat", "Pazar yeri komisyonu, alıcıya kargo ve istediğiniz kâr hesaba katılır."),
            ("archive", "Arşiv ve satışlar", "Her iş fotoğrafı ve içeriğiyle saklanır. Kime ve nereye satıldığı. Aylık ve yıllık istatistik."),
            ("phone", "Her yerde, internetsiz de", "Telefon, tablet, bilgisayar. Veriler eşitlenir ve çevrimdışı da kullanılabilir."),
        ],
        "gal_title": "Uygulama böyle görünüyor",
        "gal": ["Fotoğraflı Malzeme Stoğu", "Maliyet ve Fiyat", "Satışlar ve İstatistik", "İş Arşivi"],
        "gal_alt": ["Malzeme stoğu ekranı", "Maliyet ve fiyat hesabı ekranı", "Satış istatistikleri ekranı", "Arşivdeki iş ekranı"],
        "ui_note": "Uygulama Rusça, Türkçe ve İngilizce olarak çalışır.",
        "ac_kicker": "Çok yakında", "ac_title": "Akademi: derslerinizi satın",
        "ac_text": "Kurslar, öğrenciler ve ortak sohbet, stoğunuzun yanında. Atölyenizi bir okula da dönüştürün.",
        "faq_title": "Sık sorulan sorular",
        "faq": [
            ("Mağazadan indirmem gerekiyor mu?", "Hayır. Uygulamayı tarayıcıda açın ve ana ekrana ekleyin. Normal bir uygulama gibi çalışır."),
            ("Verilerim güvende mi?", "Her kullanıcının kendine ait ayrı bir stoğu vardır, başkaları göremez. Veriler Avrupa'daki (Paris) güvenli bir bulutta saklanır."),
            ("İnternet olmadan çalışır mı?", "Evet. Değişiklikler cihazınıza kaydedilir ve bağlantı geldiğinde buluta gönderilir."),
            ("Hangi dillerde?", "Rusça, Türkçe ve İngilizce. Dil, giriş ekranında ve «Daha» bölümünde seçilir."),
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
        "title": "Melaymade | My Workshop: stock, purchases and pricing for handmade makers",
        "desc": "Photo inventory of your materials, cost calculation including waste and time, a recommended price and an archive of your work. On phone and computer, even offline.",
        "nav": ["How it works", "Features", "FAQ"], "login": "Log in",
        "kicker": "an app by Melaymade",
        "h1": "Know what your handmade piece really costs",
        "sub": "My Workshop keeps a photo inventory of your materials, calculates the cost including waste, time and tools, and suggests a price that actually earns you money.",
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
        "ui_note": "The app works in Russian, Turkish and English.",
        "ac_kicker": "Coming soon", "ac_title": "Academy: sell your own lessons",
        "ac_text": "Courses, students and a shared chat next to your stock. Turn your workshop into a school too.",
        "faq_title": "Frequently asked questions",
        "faq": [
            ("Do I need to install it from an app store?", "No. Open the app in your browser and add it to your home screen. It works like a regular app."),
            ("Is my data safe?", "Every user has their own separate stock that nobody else can see. Data is stored in a secure cloud in Europe (Paris)."),
            ("Does it work offline?", "Yes. Changes are saved on your device and sent to the cloud when you are back online."),
            ("Which languages are supported?", "Russian, Turkish and English. You pick the language on the login screen and in the “More” section."),
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
        "title": "Melaymade | Моя мастерская: склад, цена и личная Академия для мастериц handmade",
        "desc": "Фото-склад материалов, расчёт себестоимости и цены, а ещё личная Академия: курсы, уроки и ученицы в одном приложении. На телефоне и компьютере.",
        "sub": "«Моя мастерская» ведёт склад материалов с фото, считает себестоимость и цену, на которой ты зарабатываешь, а ещё хранит твою личную Академию: уроки, ученицы и материалы в одном месте.",
        "nav": ["Как это работает", "Академия", "Возможности", "Вопросы"],
        "pill": "Новое · личная Академия для твоих уроков",
        "ac_badge": "Моя Академия · бета",
        "ac_h": "Твоя школа рукоделия в одном приложении",
        "ac_lead": "Обычно школа мастерицы живёт в пяти местах: чат, таблица, облако с фото, заметки и блокнот с закупками. «Моя мастерская» собирает всё вместе: уроки, материалы, ученицы и доход рядом со складом и расчётом цены.",
        "pain_title": "Знакомо?",
        "pains": [
            ("«А что покупать для урока?» в сотый раз", "Материалы прикрепляются к уроку прямо из твоего склада. Список всегда под рукой, а себестоимость урока считается сама."),
            ("Кто оплатил и на каком уроке остановилась?", "Ученицы, их доступ и прогресс собраны в одном списке. Без таблиц и разрозненных заметок."),
            ("Один урок, один вечер возни", "Мы делаем загрузку уроков на площадки для мастериц в одно нажатие. Пока это в разработке, но направление именно такое."),
        ],
        "ac_cta": "Собрать свою академию",
        "ac_cards": [
            ("book", "Курсы и уроки по полочкам", "Создавай курсы, добавляй уроки с видео по ссылке и описанием, публикуй, когда готово. Видео остаётся на твоём видеосервисе.", "ok"),
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
            ("Что такое Академия?", "Раздел «Моя Академия» — твоя личная школа внутри приложения: курсы, уроки с материалами со склада, ученицы и доход от курсов. Всё рядом с расчётом себестоимости."),
            ("Смогут ли ученицы учиться прямо в приложении?", "Пока нет: сейчас ты сама ведёшь учениц и их прогресс. Личный кабинет ученицы и общий чат курса в разработке."),
            ("Можно ли загружать уроки на площадки?", "Это в планах: загрузка уроков на площадки для мастериц в одно нажатие. Сейчас в разработке, точные сроки пока не назовём."),
        ],
        "final_title": "Начни со склада, а потом собери первый курс",
        "final_text": "Создай аккаунт за минуту: посчитай своё первое изделие и собери первый курс в своей Академии.",
    },
    "tr": {
        "title": "Melaymade | Atölyem: El işi ustaları için stok, fiyat ve kişisel Akademi",
        "desc": "Fotoğraflı malzeme stoğu, maliyet ve fiyat hesabı, ayrıca kişisel Akademi: kurslar, dersler ve öğrenciler tek uygulamada. Telefonda ve bilgisayarda.",
        "sub": "Atölyem malzeme stoğunuzu fotoğraflarla tutar, maliyeti ve kazanç sağlayacağınız fiyatı hesaplar; ayrıca kişisel Akademinizi barındırır: dersler, öğrenciler ve malzemeler tek yerde.",
        "nav": ["Nasıl çalışır?", "Akademi", "Özellikler", "Sık sorulanlar"],
        "pill": "Yeni · dersleriniz için kişisel Akademi",
        "ac_badge": "Akademim · beta",
        "ac_h": "El işi okulunuz tek uygulamada",
        "ac_lead": "Bir ustanın okulu çoğu zaman beş ayrı yerde yaşar: sohbet, tablo, fotoğraf bulutu, notlar ve alışveriş defteri. Atölyem hepsini bir araya getirir: dersler, malzemeler, öğrenciler ve gelir; stoğunuzun ve fiyat hesabının yanında.",
        "pain_title": "Tanıdık geliyor mu?",
        "pains": [
            ("«Ders için ne almalıyım?» yüzüncü kez", "Malzemeler doğrudan stoğunuzdan derse eklenir. Liste her zaman elinizin altında, dersin maliyeti kendiliğinden hesaplanır."),
            ("Kim ödedi, hangi derste kaldı?", "Öğrenciler, erişimleri ve ilerlemeleri tek listede. Tablolara ve dağınık notlara gerek yok."),
            ("Bir ders, bir akşam uğraş", "Derslerinizi el işi ustalarının platformlarına tek dokunuşla yüklemek için çalışıyoruz. Henüz geliştirme aşamasında, ama yön tam olarak bu."),
        ],
        "ac_cta": "Akademinizi Kurun",
        "ac_cards": [
            ("book", "Kurslar ve dersler düzenli", "Kurs oluşturun, bağlantıyla video ve açıklama içeren dersler ekleyin, hazır olunca yayınlayın. Videolar kendi video servisinizde kalır.", "ok"),
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
        "features_extra": ("book", "Kişisel Akademi", "Kurslar, malzemeli dersler ve öğrenciler stoğunuzun yanında. Bölüm gelişmeye devam ediyor."),
        "faq_extra": [
            ("Akademi nedir?", "«Akademim» bölümü, Atölyem içindeki kişisel okulunuzdur: kurslar, stoktan malzemeli dersler, öğrenciler ve kurs geliri. Hepsi maliyet hesabının yanında."),
            ("Öğrenciler doğrudan uygulamada öğrenebilir mi?", "Henüz değil: şu anda öğrencileri ve ilerlemelerini siz takip edersiniz. Öğrenci hesabı ve kurs sohbeti geliştirme aşamasında."),
            ("Dersleri platformlara yükleyebilir miyim?", "Planlarımızda var: dersleri el işi ustalarının platformlarına tek dokunuşla yüklemek. Geliştirme aşamasında, kesin tarih vermiyoruz."),
        ],
        "final_title": "Stokla başlayın, ilk kursunuzu kurun",
        "final_text": "Bir dakikada hesap oluşturun: ilk ürününüzün maliyetini hesaplayın ve Akademinizde ilk kursunuzu oluşturun.",
    },
    "en": {
        "title": "Melaymade | My Workshop: stock, pricing and a personal Academy for handmade makers",
        "desc": "Photo inventory, cost and price calculation, plus a personal Academy: courses, lessons and students in one app. On phone and computer.",
        "sub": "My Workshop keeps a photo inventory of your materials, calculates your cost and a price that earns you money, and hosts your personal Academy: lessons, students and materials in one place.",
        "nav": ["How it works", "Academy", "Features", "FAQ"],
        "pill": "New · your personal Academy for your lessons",
        "ac_badge": "My Academy · beta",
        "ac_h": "Your craft school, in one app",
        "ac_lead": "A maker's school usually lives in five places: a chat, a spreadsheet, a cloud with photos, notes and a shopping notebook. My Workshop brings it together: lessons, materials, students and income, right next to your stock and pricing.",
        "pain_title": "Sound familiar?",
        "pains": [
            ("“What do I buy for the lesson?” for the hundredth time", "Attach materials to a lesson straight from your stock. The list is always at hand and the lesson cost calculates itself."),
            ("Who paid, and which lesson are they on?", "Students, their access and progress in one list. No spreadsheets or scattered notes."),
            ("One lesson, one evening of uploading", "We are working on uploading your lessons to handmade platforms in one tap. It is still in development, but that is exactly where we are heading."),
        ],
        "ac_cta": "Build your academy",
        "ac_cards": [
            ("book", "Courses and lessons, neatly shelved", "Create courses, add lessons with a video link and a description, and publish when ready. Videos stay on your own video service.", "ok"),
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
            ("What is the Academy?", "“My Academy” is your personal school inside My Workshop: courses, lessons with materials from your stock, students and course income. All next to your cost calculation."),
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

# ------------------------------------------------- смелые заголовки и лента
BOLD = {
    "ru": {
        "h1": "Ты создаёшь магию. *Мы считаем, сколько она стоит.*",
        "how_title": "От идеи до честной цены: три шага",
        "feat_title": "Каждая мелочь на счету",
        "gal_title": "Загляни внутрь",
        "faq_title": "Остались вопросы?",
        "final_title": "Пора превратить рукоделие в своё дело",
        "ribbon": ["Склад", "Себестоимость", "Цена", "Академия", "Уроки", "Ученицы", "Handmade"],
        "ac_big": "Твои руки знают то, чему хотят научиться другие",
    },
    "tr": {
        "h1": "Siz büyüyü yaratın. *Ne kadar ettiğini biz hesaplayalım.*",
        "how_title": "Fikirden dürüst fiyata: üç adım",
        "feat_title": "Her ayrıntı hesapta",
        "gal_title": "İçeri bir göz atın",
        "faq_title": "Aklınıza takılanlar",
        "final_title": "El emeğinizi kendi işinize dönüştürme zamanı",
        "ribbon": ["Stok", "Maliyet", "Fiyat", "Akademi", "Dersler", "Öğrenciler", "Handmade"],
        "ac_big": "Ellerinizin bildiğini başkaları da öğrenmek ister",
    },
    "en": {
        "h1": "You make the magic. *We work out what it's worth.*",
        "how_title": "From idea to honest price: three steps",
        "feat_title": "Every detail counted",
        "gal_title": "Take a look inside",
        "faq_title": "Still wondering?",
        "final_title": "Time to turn your craft into your business",
        "ribbon": ["Stock", "Cost", "Price", "Academy", "Lessons", "Students", "Handmade"],
        "ac_big": "Your hands know what others want to learn",
    },
}
for _c, _b in BOLD.items():
    TEXTS[_c].update({k: v for k, v in _b.items() if k != "ac_big"})
    TEXTS[_c]["ac"]["ac_big"] = _b["ac_big"]

# ------------------------------------------------- виды рукоделия (линейные знаки)
CRAFT_ICONS = {
    "beads": '<path d="M5 14C10 36 38 36 43 14"/><circle cx="7" cy="20" r="3"/><circle cx="12.3" cy="26.4" r="3"/><circle cx="24" cy="30.5" r="3.4"/><circle cx="35.7" cy="26.4" r="3"/><circle cx="41" cy="20" r="3"/><path d="M24 34v3.5"/><path d="M24 37.5c3 3 3 5.5 0 7.5-3-2-3-4.5 0-7.5z"/>',
    "stones": '<path d="M14 8h20l8 10-18 22L6 18z"/><path d="M6 18h36M18 8l-4 10 10 22M30 8l4 10-10 22"/>',
    "knit": '<circle cx="21" cy="27" r="14"/><path d="M9 21c8 3 20 3 28-2M8 29c9 3 21 2 28-4M12 38c6-3 14-4 22-2M16 14c5 8 5 18 2 26M26 13c3 8 3 18-1 27"/><path d="M31 9l14 23"/><circle cx="30" cy="7.5" r="1.6"/>',
    "sew": '<path d="M9 41 36 11"/><ellipse cx="38" cy="9" rx="1.1" ry="3.3" transform="rotate(40 38 9)"/><path d="M39 11c8 5-8 14-15 9-8-6-15 4-9 11 4 5-2 10-8 7"/>',
    "clay": '<path d="M18 6h12M20 6c0 4-1 6-4 10-6 6-6 18 2 24h12c8-6 8-18 2-24-3-4-4-6-4-10"/><path d="M12 25c8 4 16 4 24 0M14 18c6 3 14 3 20 0"/>',
    "hair": '<path d="M24 4c-9 5-9 9 0 14s9 9 0 14-9 9 0 12"/><path d="M24 4c9 5 9 9 0 14s-9 9 0 14 9 9 0 12"/><path d="M24 40l-6 5M24 40l6 5"/>',
    "macrame": '<path d="M5 8h38"/><path d="M12 8v32M18 8v10M24 8v32M30 8v10M36 8v32"/><path d="M18 18l6 8M30 18l-6 8M12 26l6-8M36 26l-6-8"/><path d="M10 40l2 4 2-4M22 40l2 4 2-4M34 40l2 4 2-4"/>',
    "candle": '<rect x="14" y="21" width="20" height="22" rx="2"/><path d="M24 21v-4M14 29h20"/><path d="M24 5c5 4 5 8 0 11-5-3-5-7 0-11z"/>',
    "embroid": '<circle cx="24" cy="24" r="18"/><circle cx="24" cy="24" r="14.5"/><path d="M24 6V3M24 31v-9"/><path d="M24 22c-5-1-6-6-2-8M24 22c5-1 6-6 2-8M24 19c-1-4 1-6 3-7M24 27c-4 0-8 2-9 6M24 27c4 0 8 2 9 6"/>',
}


def craft_icon(n):
    return f'<svg viewBox="0 0 48 48" aria-hidden="true">{CRAFT_ICONS[n]}</svg>'


CRAFTS = {
    "ru": {
        "nav": "Ремёсла",
        "kick": "для любого рукоделия",
        "title": "Любое рукоделие, которое можно посчитать",
        "lead": "Если твоё изделие собирается из материалов, «Моя мастерская» его посчитает: штуки, метры, граммы, миллилитры. Неважно, чем ты занимаешься.",
        "items": ["Бисероплетение", "Украшения из камней", "Вязание", "Шитьё", "Изделия из глины", "Украшения для волос", "Макраме", "Свечи и мыло", "Вышивка"],
        "foot": "…и всё остальное, что рождается у тебя в руках.",
        "desc_add": "Для любого рукоделия: бисер, камни, вязание, шитьё, глина, украшения для волос.",
        "yk": "Твоя мастерская",
        "yt": "Твои правила. Приложение подстраивается под тебя.",
        "yl": "Ты не подгоняешь своё ремесло под программу. Это программа подстраивается под твоё ремесло.",
        "yi": [
            ("camera", "Твои фотографии", "Каждый материал и каждая работа с твоим фото. Кадрируй и приближай, как тебе нравится."),
            ("tag", "Твои категории", "Придумай разделы под свой вид рукоделия: от «Бусин» до «Пряжи», «Глины» и «Волос»."),
            ("ruler", "Твои единицы", "Штуки, метры, граммы, миллилитры и пересчёт между ними."),
            ("coin", "Твоя валюта", "Больше 40 валют. Закупай в любой, а считай в удобной."),
            ("sliders", "Твои правила цены", "Комиссия площадки, желаемая прибыль, ставка за час работы и стоимость инструмента."),
        ],
        "faq": ("Подойдёт ли это для моего вида рукоделия?", "Да, если изделие собирается из материалов, которые можно посчитать: бисер, камни, пряжа, ткань, глина, волосы, воск и многое другое. Не уверена, попробуй бесплатно на своих материалах."),
    },
    "tr": {
        "nav": "El işleri",
        "kick": "her el işi için",
        "title": "Sayabildiğiniz her el işi için",
        "lead": "Ürününüz malzemelerden oluşuyorsa Atölyem onu hesaplar: adet, metre, gram, mililitre. Ne yaptığınız fark etmez.",
        "items": ["Boncuk işi", "Doğal taş takılar", "Örgü", "Dikiş", "Seramik ve kil", "Saç aksesuarları", "Makrome", "Mum ve sabun", "Nakış"],
        "foot": "…ve ellerinizle yarattığınız her şey.",
        "desc_add": "Her el işi için: boncuk, taş, örgü, dikiş, kil, saç aksesuarları.",
        "yk": "Sizin atölyeniz",
        "yt": "Kurallar sizin. Uygulama size uyum sağlar.",
        "yl": "El işinizi programa uydurmazsınız. Program sizin el işinize uyum sağlar.",
        "yi": [
            ("camera", "Kendi fotoğraflarınız", "Her malzeme ve her iş sizin fotoğrafınızla. İstediğiniz gibi kırpın ve yakınlaştırın."),
            ("tag", "Kendi kategorileriniz", "El işinize göre bölümler oluşturun: «Boncuklar»dan «İplik», «Kil» ve «Saç»a kadar."),
            ("ruler", "Kendi birimleriniz", "Adet, metre, gram, mililitre ve aralarında dönüştürme."),
            ("coin", "Kendi para biriminiz", "40'tan fazla para birimi. İstediğinizle alışveriş yapın, rahat ettiğinizle hesaplayın."),
            ("sliders", "Kendi fiyat kurallarınız", "Pazar yeri komisyonu, istediğiniz kâr, saat ücretiniz ve aletlerin maliyeti."),
        ],
        "faq": ("Benim el işime uygun mu?", "Evet, ürününüz sayılabilen malzemelerden oluşuyorsa: boncuk, taş, iplik, kumaş, kil, saç, balmumu ve daha fazlası. Emin değilseniz kendi malzemelerinizle ücretsiz deneyin."),
    },
    "en": {
        "nav": "Crafts",
        "kick": "for every craft",
        "title": "Any craft you can count",
        "lead": "If your piece is built from materials, My Workshop can price it: pieces, metres, grams, millilitres. It does not matter what you make.",
        "items": ["Beadwork", "Natural-stone jewelry", "Knitting and crochet", "Sewing", "Clay and ceramics", "Hair accessories", "Macramé", "Candles and soap", "Embroidery"],
        "foot": "…and anything else your hands make.",
        "desc_add": "For every craft: beads, stones, knitting, sewing, clay, hair accessories.",
        "yk": "Your workshop",
        "yt": "Your rules. The app adapts to you.",
        "yl": "You do not bend your craft to fit a program. The program bends to fit your craft.",
        "yi": [
            ("camera", "Your own photos", "Every material and every piece with your own photo. Crop and zoom as you like."),
            ("tag", "Your own categories", "Create sections for your craft: from “Beads” to “Yarn”, “Clay” and “Hair”."),
            ("ruler", "Your own units", "Pieces, metres, grams, millilitres and conversion between them."),
            ("coin", "Your own currency", "40+ currencies. Buy in any, calculate in the one you like."),
            ("sliders", "Your own pricing rules", "Marketplace fee, the profit you want, your hourly rate and the cost of tools."),
        ],
        "faq": ("Will it work for my kind of craft?", "Yes, if your piece is built from materials you can count: beads, stones, yarn, fabric, clay, hair, wax and more. Not sure? Try it free with your own materials."),
    },
}
for _c, _x in CRAFTS.items():
    _t = TEXTS[_c]
    _t["cr"] = _x
    _t["nav"] = [_x["nav"]] + list(_t["nav"])
    _t["desc"] = _t["desc"].rstrip() + " " + _x["desc_add"]
    _t["faq"] = [_x["faq"]] + list(_t["faq"])


# порядок работ в галерее: (ремесло, файл)
WORKS = [("hair", "work1"), ("macrame", "w_macrame"), ("hair", "work2"), ("stones", "w_stones"),
         ("embroid", "w_embroid"), ("hair", "work3"), ("candles", "w_candles"), ("hair", "work4"),
         ("knit", "w_knit"), ("clay", "w_clay"), ("hair", "work5"), ("beads", "w_beads"),
         ("sewing", "w_sewing"), ("hair", "work6"), ("hair", "work7"), ("hair", "work8")]
SHOW = {
    "ru": {"kick": "примеры работ", "title": "Красота, у которой есть честная цена", "lead": "Такие изделия собираются из десятков материалов. «Моя мастерская» помнит каждый и считает, сколько стоит всё вместе.",
           "chips": {"all": "Все", "beads": "Бисер", "stones": "Камни", "knit": "Вязание", "sewing": "Шитьё", "clay": "Глина", "hair": "Для волос", "macrame": "Макраме", "candles": "Свечи и мыло", "embroid": "Вышивка"},
           "names": ["Лесной оберег", "Дыхание ветра", "Янтарная луна", "Аметистовый сад", "Луговые травы", "Лунный камень", "Лаванда и апельсин", "Древо жизни", "Овсяное облако", "Песок и терракота", "Золотой лабрадорит", "Розовое золото", "Льняной шёпот", "Пепел, медь и ночь", "Розовый кварц", "Осенний лес"],
           "kinds": ["Заколка", "Макраме-панно", "Заколка", "Колье и браслет из камней", "Вышивка", "Съёмная прядь", "Свеча и мыло", "Тика", "Вязаный шарф", "Керамика", "Коса с украшениями", "Жгут из бисера", "Мешочек с вышивкой", "Косы на карабинах", "Коса с кристаллами", "Афро-резинки"], "note": "Примеры изделий."},
    "tr": {"kick": "örnek çalışmalar", "title": "Dürüst fiyatı olan güzellik", "lead": "Böyle ürünler onlarca malzemeden oluşur. Atölyem hepsini hatırlar ve toplamının maliyetini hesaplar.",
           "chips": {"all": "Tümü", "beads": "Boncuk", "stones": "Taş", "knit": "Örgü", "sewing": "Dikiş", "clay": "Kil", "hair": "Saç", "macrame": "Makrome", "candles": "Mum ve sabun", "embroid": "Nakış"},
           "names": ["Orman Muskası", "Rüzgârın Nefesi", "Kehribar Ay", "Ametist Bahçesi", "Kır Otları", "Ay Taşı", "Lavanta ve Portakal", "Hayat Ağacı", "Yulaf Bulutu", "Kum ve Terakota", "Altın Labradorit", "Gül Altın", "Keten Fısıltısı", "Kül, Bakır ve Gece", "Gül Kuvarsı", "Sonbahar Ormanı"],
           "kinds": ["Toka", "Makrome pano", "Toka", "Taş kolye ve bileklik", "Nakış", "Saç parçası", "Mum ve sabun", "Tika", "Örgü atkı", "Seramik", "Süslü örgü", "Boncuk kolye", "Nakışlı keseler", "Karabinalı örgüler", "Kristalli örgü", "Afro lastik"], "note": "Örnek ürünler."},
    "en": {"kick": "example pieces", "title": "Beauty with an honest price", "lead": "Pieces like these are built from dozens of materials. My Workshop remembers every one and works out what it all costs together.",
           "chips": {"all": "All", "beads": "Beads", "stones": "Stones", "knit": "Knitting", "sewing": "Sewing", "clay": "Clay", "hair": "Hair", "macrame": "Macramé", "candles": "Candles and soap", "embroid": "Embroidery"},
           "names": ["Forest Amulet", "Breath of the Wind", "Amber Moon", "Amethyst Garden", "Meadow Herbs", "Moonstone", "Lavender and Orange", "Tree of Life", "Oatmeal Cloud", "Sand and Terracotta", "Golden Labradorite", "Rose Gold", "Linen Whisper", "Ash, Copper and Night", "Rose Quartz", "Autumn Forest"],
           "kinds": ["Hair slide", "Macramé wall hanging", "Hair slide", "Stone necklace and bracelet", "Hand embroidery", "Hair piece", "Candle and soap", "Tikka headpiece", "Knitted scarf", "Ceramics", "Jeweled braid", "Beaded rope necklace", "Embroidered pouch", "Braids on carabiners", "Crystal braid", "Afro hair ties"], "note": "Example pieces."},
}
for _c, _x in SHOW.items():
    TEXTS[_c]["sh"] = _x


import math


def moon(cx, cy, r, illum):
    """Фаза луны: illum 0..1, освещена правая сторона."""
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}"/>'
    if illum <= 0.02:
        return out
    if illum >= 0.98:
        return out.replace("/>", ' fill="currentColor"/>')
    rx = abs(1 - 2 * illum) * r
    sweep = 0 if illum < 0.5 else 1
    return out + f'<path d="M{cx} {cy - r}A{r} {r} 0 0 1 {cx} {cy + r}A{rx:.2f} {r} 0 0 {sweep} {cx} {cy - r}Z" fill="currentColor"/>'


def moons_row():
    ph = [0.12, 0.35, 1, 0.65, 0.88]
    return '<div class="moons rv" aria-hidden="true">' + "".join(
        f'<svg viewBox="0 0 24 24" style="--i:{i}">{moon(12, 12, 9, v)}</svg>' for i, v in enumerate(ph)) + "</div>"


def mandala_svg():
    c = 200
    a = [f'<circle cx="{c}" cy="{c}" r="196" stroke-dasharray="2 7"/>', f'<circle cx="{c}" cy="{c}" r="176"/>',
         f'<circle cx="{c}" cy="{c}" r="122"/>', f'<circle cx="{c}" cy="{c}" r="70" stroke-dasharray="1 4"/>']
    for k in range(48):
        ang = math.radians(k * 7.5)
        r1, r2 = (126, 170) if k % 2 == 0 else (126, 152)
        a.append(f'<path d="M{c + r1 * math.sin(ang):.1f} {c - r1 * math.cos(ang):.1f}L{c + r2 * math.sin(ang):.1f} {c - r2 * math.cos(ang):.1f}"/>')
    b = []
    for k in range(12):
        b.append(f'<path d="M200 70C216 98 216 124 200 150C184 124 184 98 200 70" transform="rotate({k * 30} 200 200)"/>')
    for k in range(8):
        ang = math.radians(k * 45)
        b.append(moon(round(200 + 186 * math.sin(ang), 1), round(200 - 186 * math.cos(ang), 1), 7, [0.08, 0.3, 0.6, 1, 0.6, 0.3, 0.08, 0][k]))
    return (f'<div class="halo" aria-hidden="true"><svg class="a" viewBox="0 0 400 400">{"".join(a)}</svg>'
            f'<svg class="b" viewBox="0 0 400 400">{"".join(b)}</svg></div>')


def feather_svg(left, top, size, t, dl):
    return (f'<svg class="fe" viewBox="-10 0 20 48" style="left:{left};top:{top};width:{size}px;--t:{t}s;--dl:{dl}s" aria-hidden="true">'
            '<path d="M0 0V46"/><path d="M0 13.8C7.8 20.7 7.8 36.8 0 46C-7.8 36.8-7.8 20.7 0 13.8"/>'
            '<path d="M0 19l4.3-2.8M0 19l-4.3-2.8M0 24.5l6-2.8M0 24.5l-6-2.8M0 30l7.5-2.8M0 30l-7.5-2.8M0 35.3l6-2.8M0 35.3l-6-2.8M0 40.6l4.3-2.8M0 40.6l-4.3-2.8" stroke-width=".6"/></svg>')


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
.acad .vis{gap:12px}
.acad .vis .phone{width:min(168px,29vw);border-width:5px;border-radius:28px}
.acad .vis .phone+.phone{margin-top:40px}
.acad .vis .phone:nth-child(3){margin-top:12px}
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

html,body{overflow-x:clip}
main{overflow-x:clip}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes pulse{0%,100%{opacity:.55;transform:scale(.92)}50%{opacity:1;transform:scale(1.06)}}
@keyframes bob{from{transform:translateY(-8px)}to{transform:translateY(10px)}}
@keyframes marq{to{transform:translateX(-50%)}}
@keyframes shine{to{background-position:-220% 0}}
@keyframes rise{0%{opacity:0;transform:translate(0,0)}12%{opacity:.95}85%{opacity:.5}100%{opacity:0;transform:translate(var(--dx),-680px)}}
@keyframes twinkle{0%,100%{opacity:.15;transform:scale(.7)}50%{opacity:1;transform:scale(1.25)}}
@keyframes drift{0%{opacity:0;transform:translate(0,-30px) rotate(-22deg)}12%{opacity:.6}50%{transform:translate(34px,240px) rotate(24deg)}88%{opacity:.5}100%{opacity:0;transform:translate(-14px,520px) rotate(-18deg)}}
@keyframes ring{0%{box-shadow:0 0 0 0 rgba(166,79,46,.35)}100%{box-shadow:0 0 0 14px rgba(166,79,46,0)}}
.hero{background:radial-gradient(60% 55% at 82% 28%,rgba(201,143,39,.2),transparent 70%),radial-gradient(50% 50% at 6% 90%,rgba(166,79,46,.12),transparent 70%)}
.hero .txt>*{animation:floatin .9s both}
.hero .txt>*:nth-child(1){animation-delay:.05s}.hero .txt>*:nth-child(2){animation-delay:.15s}.hero .txt>*:nth-child(3){animation-delay:.28s}.hero .txt>*:nth-child(4){animation-delay:.42s}.hero .txt>*:nth-child(5){animation-delay:.56s}.hero .txt>*:nth-child(6){animation-delay:.68s}
.shine{background:linear-gradient(100deg,var(--clay) 0%,var(--ochre) 38%,var(--clay) 76%);background-size:220% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;-webkit-text-fill-color:transparent;animation:shine 7s linear infinite;-webkit-box-decoration-break:clone;box-decoration-break:clone}
h1{font-size:clamp(40px,8.4vw,68px)}
.herovis{min-height:420px;align-items:center;perspective:900px}
.halo{position:absolute;left:50%;top:50%;width:min(620px,150vw);aspect-ratio:1;transform:translate(-50%,-50%);z-index:0;pointer-events:none}
.halo svg{position:absolute;inset:0;width:100%;height:100%;fill:none;stroke:var(--art);stroke-width:.9;stroke-linecap:round;color:var(--ochre);opacity:.6}
.halo .a{animation:spin 110s linear infinite}.halo .b{animation:spin 160s linear infinite reverse}
.halo::before{content:"";position:absolute;inset:20%;border-radius:50%;background:radial-gradient(closest-side,rgba(232,184,95,.55),rgba(232,184,95,0));animation:pulse 6s ease-in-out infinite}
.herovis .bob{position:relative;z-index:1;animation:bob 7s ease-in-out infinite alternate}
.herovis .phone{transform:rotateY(var(--ry,0deg)) rotateX(var(--rx,0deg));transition:transform .25s ease-out;will-change:transform}
.sparks,.stars{position:absolute;inset:0;overflow:hidden;pointer-events:none;z-index:0}
.sparks i{position:absolute;bottom:-12px;left:var(--x);width:var(--s);height:var(--s);border-radius:50%;background:var(--ochre);box-shadow:0 0 10px 2px var(--ochre);opacity:0;animation:rise var(--t) var(--dl) linear infinite}
.stars i{position:absolute;left:var(--x);top:var(--y);width:var(--s);height:var(--s);border-radius:50%;background:#FFE9BE;box-shadow:0 0 8px 1px rgba(255,226,160,.8);animation:twinkle var(--t) var(--dl) ease-in-out infinite}
.fe{position:absolute;z-index:0;fill:none;stroke:var(--art);stroke-width:1;stroke-linecap:round;opacity:0;animation:drift var(--t) var(--dl) ease-in-out infinite;pointer-events:none}
.moons{display:flex;justify-content:center;gap:clamp(18px,4vw,40px);color:var(--ochre);padding:4px 0}
.moons svg{width:28px;height:28px;fill:none;stroke:currentColor;stroke-width:1.3;animation:twinkle 5s calc(var(--i)*.7s) ease-in-out infinite}
.step .n{animation:ring 2.6s ease-out infinite}
.card{transition:transform .3s,box-shadow .3s,border-color .3s}
.card:hover{transform:translateY(-6px);border-color:var(--ochre);box-shadow:0 18px 40px rgba(120,86,50,.2)}
.phone{transition:transform .4s}
.gallery figure:hover .phone{transform:translateY(-8px) rotate(-1deg)}
.acad{--ink:#F3E8D3;--ink2:#CDBEA3;--surface:#2A2119;--glass:rgba(255,238,210,.055);--line:rgba(232,184,95,.3);--clay:#EBA27A;--clay-ink:#2A130A;--clay-soft:rgba(235,162,122,.18);--accent:#B4CC9E;--accent-soft:rgba(180,204,158,.16);--ochre:#E8B85F;--shadow:0 30px 80px rgba(0,0,0,.55);color:var(--ink);padding:96px 0 104px;background:radial-gradient(70% 45% at 82% 6%,rgba(232,184,95,.2),transparent 70%),radial-gradient(60% 40% at 8% 96%,rgba(235,162,122,.16),transparent 70%),#1A1410}
.acad::before,.acad::after{content:"";position:absolute;left:0;right:0;height:22px;z-index:1}
.acad::before{top:-1px;background:radial-gradient(circle at 14px 0,var(--bg) 13px,transparent 14px) 0 0/28px 22px repeat-x}
.acad::after{bottom:-1px;background:radial-gradient(circle at 14px 22px,var(--surface2) 13px,transparent 14px) 0 0/28px 22px repeat-x}
.acad .wrap{position:relative;z-index:2}
.acad .phone{border-color:#FAF4E7;box-shadow:0 0 0 1px rgba(232,184,95,.3),0 0 60px rgba(232,184,95,.28),0 30px 70px rgba(0,0,0,.6)}
.acad .vis .phone:first-child{animation:bob 7s ease-in-out infinite alternate}
.acad .vis .phone+.phone{animation:bob 8s 1s ease-in-out infinite alternate-reverse}
.acad .ac-sub{font-family:'Cormorant','Cormorant Garamond',Georgia,serif;font-style:italic;font-size:clamp(22px,3.4vw,28px);color:var(--clay);margin:4px 0 12px}
.acad h2.big{font-size:clamp(36px,6.8vw,58px)}
.acad .btn:not(.pri){background:transparent;color:var(--ink)}
.road{background:linear-gradient(135deg,rgba(232,184,95,.14),rgba(255,238,210,.04))}
.road .ic{animation:pulse 3.6s ease-in-out infinite}
.final{padding:0 0 88px;background:radial-gradient(50% 60% at 50% 100%,rgba(232,184,95,.22),transparent 70%)}
.final .hang{width:150px;margin:0 auto 18px;display:block;transform-origin:50% 0;animation:hang 7s ease-in-out infinite alternate;position:relative;z-index:1}
.final .wrap{position:relative;z-index:1}
.final h2{font-size:clamp(34px,6vw,54px)}

@keyframes swing{from{transform:rotate(-2.6deg)}to{transform:rotate(2.6deg)}}
@keyframes sheen{from{transform:translateX(-120%)}to{transform:translateX(220%)}}
body{background-image:url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 .4 0 0 0 0 .3 0 0 0 0 .18 0 0 0 .06 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
section{padding:92px 0}
h2::after{background:linear-gradient(90deg,#9C6A14,#F3DA8E,#9C6A14)}
.card{border-radius:22px;border:1px solid color-mix(in srgb,var(--ochre) 42%,var(--line));background:linear-gradient(180deg,color-mix(in srgb,var(--surface) 96%,#fff),var(--glass));box-shadow:inset 0 1px 0 rgba(255,255,255,.55)}
.btn{border-radius:14px;letter-spacing:.02em}
.btn.pri{position:relative;overflow:hidden;background:linear-gradient(135deg,#B9583A,#A04A2A);border-color:transparent;box-shadow:0 0 0 1px rgba(240,204,120,.65) inset,0 10px 26px rgba(166,79,46,.35)}
.btn.pri::after{content:"";position:absolute;top:0;bottom:0;width:40%;left:0;background:linear-gradient(100deg,transparent,rgba(255,240,200,.45),transparent);transform:translateX(-120%)}
.btn.pri:hover::after{animation:sheen .9s ease}
.kick{letter-spacing:.28em}
.lead2{font-size:19px;color:var(--ink2);max-width:36em;margin-top:6px}
.crafts{text-align:center;padding-top:80px}
.crafts h2::after{margin-left:auto;margin-right:auto;-webkit-mask-position:center;mask-position:center}
.crafts .lead2{margin-left:auto;margin-right:auto}
.garland{position:relative;display:grid;grid-template-columns:repeat(auto-fit,minmax(128px,1fr));gap:36px 10px;margin-top:56px;padding-top:34px}
.garland::before{content:"";position:absolute;left:-20px;right:-20px;top:0;height:28px;background:url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='72' height='28' viewBox='0 0 72 28'%3E%3Cpath d='M0 4Q36 26 72 4' fill='none' stroke='%23C98F27' stroke-width='1.6'/%3E%3C/svg%3E") repeat-x 0 0/72px 28px;opacity:.8}
.charm{position:relative;display:flex;flex-direction:column;align-items:center;gap:12px;padding-top:var(--len);transform-origin:50% -34px}
.charm.in{animation:swing 6.5s var(--dl) ease-in-out infinite alternate}
.charm::before{content:"";position:absolute;top:-14px;left:50%;width:1px;height:calc(var(--len) + 14px);background:linear-gradient(180deg,var(--ochre),color-mix(in srgb,var(--ochre) 40%,transparent))}
.orb{position:relative;overflow:visible;width:108px;height:108px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle at 32% 28%,color-mix(in srgb,var(--surface) 70%,#fff),var(--surface));border:1px solid color-mix(in srgb,var(--ochre) 60%,var(--line));box-shadow:0 0 0 5px var(--bg),0 0 0 6px color-mix(in srgb,var(--ochre) 38%,transparent),0 14px 28px rgba(120,86,50,.18);transition:transform .35s,box-shadow .35s}
.orb img{width:100%;height:100%;border-radius:50%;object-fit:cover;display:block;transition:transform .6s ease}
.charm:hover .orb img{transform:scale(1.12)}
.orb{padding:0}
.orb::after{content:"";position:absolute;inset:0;border-radius:50%;box-shadow:inset 0 0 0 1px rgba(255,255,255,.4),inset 0 -10px 18px rgba(60,35,15,.12);pointer-events:none}
.charm:hover .orb{transform:translateY(-4px) scale(1.06);box-shadow:0 0 0 5px var(--bg),0 0 0 6px var(--ochre),0 0 34px rgba(232,184,95,.55)}
.charm span{font-weight:800;font-size:15px;line-height:1.25;max-width:9em}
.foot2{margin-top:44px;font-family:'Cormorant','Cormorant Garamond',Georgia,serif;font-style:italic;font-size:clamp(22px,3.4vw,30px);color:var(--clay)}
.yours .ytop{max-width:40em}
.ygrid{display:grid;gap:18px;margin-top:36px;counter-reset:y}
.yitem{display:flex;gap:18px;align-items:flex-start;padding:22px 24px;border-radius:22px;border:1px solid color-mix(in srgb,var(--ochre) 42%,var(--line));background:var(--glass)}
.yn{flex:none;width:52px;height:52px;border-radius:50%;display:grid;place-items:center;background:var(--accent-soft);color:var(--accent);border:1px solid color-mix(in srgb,var(--accent) 40%,transparent)}
.yn .ic{width:26px;height:26px}
.yitem h3{font-size:18px;font-weight:800;margin-bottom:4px}
.yitem p{color:var(--ink2);font-size:16px}
@media (min-width:1000px){.garland{grid-template-columns:repeat(9,1fr);gap:36px 6px}}
@media (min-width:860px){.ygrid{grid-template-columns:repeat(2,1fr)}.ygrid .yitem:last-child{grid-column:1/-1}}
@media (max-width:560px){.garland{grid-template-columns:repeat(3,1fr);gap:30px 6px}.orb{width:86px;height:86px}.charm span{font-size:13px}section{padding:72px 0}}

.showcase{text-align:center}
.showcase h2::after{margin-left:auto;margin-right:auto;-webkit-mask-position:center;mask-position:center}
.showcase .lead2{margin-left:auto;margin-right:auto}
.works{display:grid;grid-template-columns:repeat(2,1fr);gap:34px 14px;margin-top:40px}
.work{margin:0;width:100%}
.work[hidden]{display:none}
.work.lift{margin-top:34px}
.wchips{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-top:34px}
.wchips button{font:inherit;font-weight:800;font-size:14px;padding:9px 18px;border-radius:999px;border:1px solid color-mix(in srgb,var(--ochre) 50%,var(--line));background:var(--glass);color:var(--ink);cursor:pointer;transition:background .25s,color .25s,transform .2s}
.wchips button:hover{transform:translateY(-2px)}
.wchips button.on{background:var(--clay);color:var(--clay-ink);border-color:transparent}
.work .arch{aspect-ratio:3/4;border-radius:999px 999px 22px 22px;overflow:hidden;border:1px solid color-mix(in srgb,var(--ochre) 55%,var(--line));box-shadow:0 0 0 5px var(--bg),0 0 0 6px color-mix(in srgb,var(--ochre) 40%,transparent),0 20px 44px rgba(90,60,30,.25);transition:transform .5s,box-shadow .5s}
.work img{width:100%;height:100%;object-fit:cover;transition:transform 1.2s ease}
.work:hover .arch{transform:translateY(-8px)}
.work:hover img{transform:scale(1.06)}
.work figcaption{margin-top:20px;font-family:'Cormorant','Cormorant Garamond',Georgia,serif;font-style:italic;font-weight:600;font-size:clamp(18px,2.4vw,24px);line-height:1.15;color:var(--clay)}
.work figcaption small{display:block;margin-top:4px;font-family:'Nunito',system-ui,sans-serif;font-style:normal;font-weight:700;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--ink2)}
.shnote{margin-top:38px;font-size:14px;color:var(--ink2)}
@media (min-width:860px){.works{grid-template-columns:repeat(4,1fr);gap:44px 22px}.work.lift{margin-top:56px}}
@media (prefers-reduced-motion:no-preference){
  .js .rv{opacity:0;transform:translateY(28px);transition:opacity .8s ease,transform .8s ease;transition-delay:calc(var(--i,0)*90ms)}
  .js .rv.in{opacity:1;transform:none}
  .js .card.rv.in:hover{transform:translateY(-6px);transition-delay:0s;transition-duration:.3s}
}
@media (max-width:560px){.herovis{min-height:380px}.acad{padding:80px 0 88px}}
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

SCRIPT = """<script>
(function(){
var d=document,R=Math.random;
try{
d.querySelectorAll('[data-sparks]').forEach(function(b){for(var i=0;i<+b.dataset.sparks;i++){var s=d.createElement('i');s.style.cssText='--x:'+(R()*100)+'%;--s:'+(2+R()*4)+'px;--t:'+(10+R()*12)+'s;--dl:-'+(R()*20)+'s;--dx:'+(R()*90-45)+'px';b.appendChild(s)}});
d.querySelectorAll('[data-stars]').forEach(function(b){for(var i=0;i<+b.dataset.stars;i++){var s=d.createElement('i');s.style.cssText='--x:'+(R()*100)+'%;--y:'+(R()*100)+'%;--s:'+(1+R()*2.2)+'px;--t:'+(3+R()*5)+'s;--dl:-'+(R()*8)+'s';b.appendChild(s)}});
var els=d.querySelectorAll('.rv');
if(!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('in')})}
else{var io=new IntersectionObserver(function(en){en.forEach(function(x){if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}})},{threshold:.1,rootMargin:'0px 0px -5% 0px'});els.forEach(function(e){io.observe(e)})}
var wc=d.querySelectorAll('.wchips button'),ws=d.querySelectorAll('.work');
function lay(){var k=0;ws.forEach(function(w){if(!w.hidden){w.classList.toggle('lift',k%2===1);k++}})}
wc.forEach(function(c){c.addEventListener('click',function(){wc.forEach(function(x){x.classList.toggle('on',x===c);x.setAttribute('aria-pressed',x===c?'true':'false')});var f=c.dataset.f;ws.forEach(function(w){var on=f==='all'||w.dataset.c===f;w.hidden=!on;if(on){w.classList.remove('in');void w.offsetWidth;w.classList.add('in')}});lay()})});lay();
var hv=d.querySelector('.herovis');
if(hv&&matchMedia('(hover:hover)').matches&&!matchMedia('(prefers-reduced-motion:reduce)').matches){
hv.addEventListener('pointermove',function(e){var r=hv.getBoundingClientRect();var x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;hv.style.setProperty('--ry',(x*12).toFixed(1)+'deg');hv.style.setProperty('--rx',(-y*10).toFixed(1)+'deg')});
hv.addEventListener('pointerleave',function(){hv.style.setProperty('--ry','0deg');hv.style.setProperty('--rx','0deg')})}
}catch(e){d.querySelectorAll('.rv').forEach(function(x){x.classList.add('in')})}
})();
</script>"""

# ------------------------------------------------- правки носителя турецкого (файл Melaymade_TR_site_review.xlsx)
def _apply_tr_fixes():
    import json as _j
    fx = _j.loads((Path(__file__).parent / "tr_site_fixes.json").read_text(encoding="utf-8"))
    def walk(o):
        if isinstance(o, str):
            plain = o.replace("*", "")
            if plain in fx:
                new = fx[plain]
                if "*" in o:  # выделенная часть заголовка
                    new = _EMPH.get(plain, new)
                return new
            return o
        if isinstance(o, dict): return {k: walk(v) for k, v in o.items()}
        if isinstance(o, list): return [walk(x) for x in o]
        if isinstance(o, tuple): return tuple(walk(x) for x in o)
        return o
    for k in list(TEXTS["tr"]):
        if k not in ("path", "label", "locale"): TEXTS["tr"][k] = walk(TEXTS["tr"][k])
_EMPH = {"Siz büyüyü yaratın. Ne kadar ettiğini biz hesaplayalım.": "Siz harikalar yaratın, *biz maliyetini hesaplayalım.*"}
_apply_tr_fixes()


FAV = '<link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32.png"><link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">'


def esc(s):
    return html.escape(s, quote=True)


def render(code):
    t = TEXTS[code]
    APPL = f"{APP}?lang={code}"
    langs = "".join(
        f'<a href="{TEXTS[c]["path"]}" hreflang="{c}" lang="{c}" class="{"on" if c == code else ""}" onclick="try{{localStorage.setItem(\'mm-lang\',\'{c}\')}}catch(e){{}}">{TEXTS[c]["label"]}</a>'
        for c in ("ru", "tr", "en"))
    alts = "".join(f'<link rel="alternate" hreflang="{c}" href="{BASE}{TEXTS[c]["path"]}">' for c in ("ru", "tr", "en"))
    alts += f'<link rel="alternate" hreflang="x-default" href="{BASE}/">'
    import re as _re
    h1 = _re.sub(r"\*(.+?)\*", r'<span class="shine">\1</span>', esc(t["h1"]))
    feathers = feather_svg("4%", "-30px", 20, 17, -2) + feather_svg("46%", "-40px", 16, 22, -9) + feather_svg("92%", "-30px", 22, 19, -5) + feather_svg("68%", "-50px", 14, 25, -14)
    cr = t["cr"]
    sh = t["sh"]
    works = "".join(
        f'<figure class="work rv" data-c="{cr_}" style="--i:{n % 4}"><div class="arch"><img src="/img/{fn}.jpg" width="800" height="1067" loading="lazy" alt="{esc(sh["kinds"][n])}: {esc(sh["names"][n])}"></div><figcaption>{esc(sh["names"][n])}<small>{esc(sh["kinds"][n])}</small></figcaption></figure>'
        for n, (cr_, fn) in enumerate(WORKS))
    charms = "".join(
        f'<div class="charm rv" style="--i:{i};--len:{(i * 37) % 5 * 14 + 8}px;--dl:-{i * 1.3:.1f}s"><div class="orb"><img src="/img/craft_{k}.jpg" width="240" height="240" loading="lazy" alt=""></div><span>{esc(nm)}</span></div>'
        for i, (k, nm) in enumerate(zip(CRAFT_ICONS, cr["items"])))
    wchips = "".join(f'<button type="button" class="{"on" if k == "all" else ""}" data-f="{k}" aria-pressed="{"true" if k == "all" else "false"}">{esc(v)}</button>' for k, v in sh["chips"].items())
    yours = "".join(f'<div class="yitem rv" style="--i:{i}"><span class="yn">{icon(ic)}</span><div><h3>{esc(a_)}</h3><p>{esc(b_)}</p></div></div>' for i, (ic, a_, b_) in enumerate(cr["yi"]))
    steps = "".join(f'<div class="card step rv" style="--i:{i}"><div class="n">{i + 1}</div><h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for i, (a, b) in enumerate(t["steps"]))
    feats = "".join(f'<div class="card feat rv" style="--i:{i % 3}">{icon(ic)}<h3>{esc(a)}</h3><p>{esc(b)}</p></div>' for i, (ic, a, b) in enumerate(t["features"]))
    imgs = ["stock", "price", "stats", "archive"]
    gal = "".join(
        f'<figure class="rv" style="--i:{i}"><div class="phone"><img src="/img/{code}/{n}.jpg" width="780" height="1688" loading="lazy" alt="{esc(t["gal_alt"][i])}"></div><figcaption>{esc(t["gal"][i])}</figcaption></figure>'
        for i, n in enumerate(imgs))
    faq = "".join(f'<details class="rv"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in t["faq"])
    nav = "".join(f'<a href="#{h}">{esc(n)}</a>' for h, n in zip(("crafts", "how", "academy", "features", "faq"), t["nav"]))
    a = t["ac"]
    pains = "".join(f'<div class="card rv" style="--i:{i}"><q>{esc(q)}</q><p>{esc(x)}</p></div>' for i, (q, x) in enumerate(a["pains"]))
    acards = "".join(
        f'<div class="card feat acard rv {st}" style="--i:{i % 3}">{icon(ic)}<span class="st {st}">{esc(a["b_ok"] if st == "ok" else a["b_soon"])}</span><h3>{esc(ti)}</h3><p>{esc(tx)}</p></div>'
        for i, (ic, ti, tx, st) in enumerate(a["ac_cards"]))
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
<script>document.documentElement.className+=" js"</script>
<style>{CSS}</style>
{redirect}
</head>
<body>
<header class="hdr"><div class="wrap">
  <a class="brand" href="{t["path"]}">{brand_icon}MELAYMADE</a>
  <nav class="nav" aria-label="Menu">{nav}</nav><span class="sp"></span>
  <div class="lang" role="navigation" aria-label="Language">{langs}</div>
  <a class="btn sm" href="{APPL}">{esc(t["login"])}</a>
</div></header>
<main>
<section class="hero"><div class="sparks" data-sparks="22"></div>{feathers}<div class="wrap">
  <div class="txt">
    <a class="pill" href="#academy">{icon("cap")}{esc(a["pill"])}</a>
    <span class="kick">{esc(t["kicker"])}</span>
    <h1>{h1}</h1>
    <p class="sub">{esc(t["sub"])}</p>
    <div class="cta"><a class="btn pri" href="{APPL}">{esc(t["cta"])}</a><a class="btn" href="#how">{esc(t["cta2"])}</a></div>
    <p class="note">{esc(t["note"])}</p>
  </div>
  <div class="herovis">{mandala_svg()}<div class="bob"><div class="phone"><img src="/img/{code}/stock.jpg" width="780" height="1688" alt="{esc(t["gal_alt"][0])}"></div></div></div>
</div></section>
<section id="crafts" class="crafts"><div class="wrap">
  <span class="kick rv">{esc(cr["kick"])}</span>
  <h2 class="rv">{esc(cr["title"])}</h2>
  <p class="lead2 rv">{esc(cr["lead"])}</p>
  <div class="garland">{charms}</div>
  <p class="foot2 rv">{esc(cr["foot"])}</p>
</div></section>
<section class="showcase"><div class="wrap">
  <div class="shtop"><span class="kick rv">{esc(sh["kick"])}</span><h2 class="rv">{esc(sh["title"])}</h2><p class="lead2 rv">{esc(sh["lead"])}</p></div>
  <div class="wchips rv" role="group">{wchips}</div>
  <div class="works">{works}</div>
  <p class="shnote rv">{esc(sh["note"])}</p>
</div></section>
<section id="how"><div class="wrap">
  <h2 class="rv">{esc(t["how_title"])}</h2>
  <div class="grid three">{steps}</div>
</div></section>
<section id="academy" class="acad"><div class="stars" data-stars="70"></div><div class="wrap">
  <div class="top">
    <div>
      <span class="badge">{icon("cap")}{esc(a["ac_badge"])}</span>
      <h2 class="big">{esc(a["ac_big"])}</h2>
      <p class="ac-sub">{esc(a["ac_h"])}</p>
      <p class="lead">{esc(a["ac_lead"])}</p>
      <div class="cta"><a class="btn pri" href="{APPL}">{esc(a["ac_cta"])}</a></div>
    </div>
    <div class="vis"><div class="phone"><img src="/img/{code}/academy.jpg" width="780" height="1688" loading="lazy" alt="{esc(a["ac_badge"])}"></div><div class="phone"><img src="/img/{code}/video.jpg" width="780" height="1688" loading="lazy" alt="{esc(a["ac_cards"][0][1])}"></div><div class="phone"><img src="/img/{code}/lesson.jpg" width="780" height="1688" loading="lazy" alt="{esc(a["ac_cards"][1][1])}"></div></div>
  </div>
  <h3 class="sec rv">{esc(a["pain_title"])}</h3>
  <div class="grid three pains">{pains}</div>
  <div class="grid three">{acards}</div>
  <div class="road rv">{icon("upload")}<div><span class="kick">{esc(a["road_kick"])}</span><h3>{esc(a["road_title"])}</h3><p>{esc(a["road_text"])}</p></div></div>
  <p class="acnote rv">{esc(a["ac_note"])}</p>
</div></section>
<section id="features" class="alt"><div class="wrap">
  <h2 class="rv">{esc(t["feat_title"])}</h2>
  <div class="grid three">{feats}</div>
</div></section>
<section class="yours alt"><div class="wrap">
  <div class="ytop"><div><span class="kick rv">{esc(cr["yk"])}</span><h2 class="rv">{esc(cr["yt"])}</h2><p class="lead2 rv">{esc(cr["yl"])}</p></div></div>
  <div class="ygrid">{yours}</div>
</div></section>
<section><div class="wrap">
  <h2 class="rv">{esc(t["gal_title"])}</h2>
  <div class="gallery">{gal}</div>
  <p class="uinote">{esc(t["ui_note"])}</p>
</div></section>
<section id="faq"><div class="wrap">
  {moons_row()}
  <h2 class="rv">{esc(t["faq_title"])}</h2>
  {faq}
</div></section>
<section class="final"><div class="sparks" data-sparks="14"></div>{catcher_svg("hang")}<div class="wrap">
  <h2 class="rv">{esc(t["final_title"])}</h2>
  <p>{esc(t["final_text"])}</p>
  <a class="btn pri" href="{APPL}">{esc(t["final_cta"])}</a>
</div></section>
</main>
<footer><div class="wrap">{esc(t["footer"])}</div></footer>
{SCRIPT}
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
