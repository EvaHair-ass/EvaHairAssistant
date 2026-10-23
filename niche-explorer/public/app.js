const app = document.getElementById('app');
const EXAMPLES = ['Здоровье', 'Личные финансы', 'Знакомства', 'Недвижимость', 'Фитнес', 'ИИ', 'Продуктивность', 'Мужская мода', 'Дрессировка собак'];
const LOADING_STEPS = ['Разбираю аудиторию…', 'Ищу самые болезненные проблемы…', 'Придумываю идеи для постов…', 'Подбираю цифровые продукты…'];

// ---------- устройство пользователя ----------
// Исследования привязаны к браузеру через случайный идентификатор — без регистрации.
function uuid() {
  if (crypto.randomUUID) return crypto.randomUUID();
  const b = crypto.getRandomValues(new Uint8Array(16));
  b[6] = (b[6] & 0x0f) | 0x40;
  b[8] = (b[8] & 0x3f) | 0x80;
  const h = [...b].map((x) => x.toString(16).padStart(2, '0')).join('');
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
}
const clientId = (() => {
  try {
    let id = localStorage.getItem('clientId');
    if (!id) localStorage.setItem('clientId', (id = uuid()));
    return id;
  } catch {
    return uuid();
  }
})();

async function api(path, { method = 'GET', body } = {}) {
  let res;
  try {
    res = await fetch(path, {
      method,
      headers: { 'x-client-id': clientId, ...(body && { 'content-type': 'application/json' }) },
      body: body && JSON.stringify(body),
    });
  } catch {
    throw new Error('Нет связи с сервером. Проверь интернет и попробуй ещё раз.');
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Что-то пошло не так');
  return data;
}

// ---------- мелкие помощники ----------
function h(tag, attrs, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs ?? {})) {
    if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (v === true) el.setAttribute(k, '');
    else if (v !== false && v != null) el.setAttribute(k, v);
  }
  el.append(...children.flat().filter((c) => c != null && c !== false));
  return el;
}
const formatDate = (iso) => new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
const show = (...nodes) => {
  app.replaceChildren(...nodes);
  window.scrollTo({ top: 0 });
};

// ---------- отчёт ----------
const section = (num, title, ...body) =>
  h('section', { class: 'card' }, h('div', { class: 'card-head' }, h('span', { class: 'card-num' }, num), h('h2', null, title)), ...body);

const numbered = (items, cls = '') =>
  h('ol', { class: `items ${cls}` }, items.map((i) => h('li', null, h('strong', null, i.title), h('p', null, i.description))));

function renderSections(r) {
  const a = r.audience;
  const fact = (label, text) => h('div', { class: 'fact' }, h('h3', null, label), h('p', null, text));
  return [
    section('01', 'На кого мы ориентируемся?',
      h('div', { class: 'facts' },
        fact('Кто они', a.who),
        fact('В какой ситуации они сейчас', a.situation),
        fact('Уровень опыта', a.experience),
        fact('Что происходит в их жизни', a.life_context),
        fact('Почему они подпишутся на страницу', a.why_follow))),
    section('02', 'Какие у них есть проблемы?', numbered(r.problems)),
    section('03', 'Чего они хотят?', numbered(r.desires, 'wishes')),
    section('04', 'Какой контент им интересен?',
      h('div', { class: 'categories' },
        r.content.map((c) => h('div', { class: 'category' }, h('h3', null, c.category), h('ul', { class: 'hooks' }, c.ideas.map((i) => h('li', null, i))))))),
    section('05', 'Какие продукты мы можем им продавать?',
      h('div', { class: 'products' },
        r.products.map((p) =>
          h('div', { class: 'product' },
            h('div', null, h('div', { class: 'label' }, 'Продукт'), h('div', { class: 'name' }, p.name)),
            h('div', null, h('div', { class: 'label' }, 'Что он помогает им сделать'), h('p', null, p.helps)),
            h('div', null, h('div', { class: 'label' }, 'Простое описание продукта'), h('p', null, p.description)))))),
  ];
}

const disclaimer = () =>
  h('p', { class: 'disclaimer' }, 'Отчёт составлен ИИ: это обоснованные гипотезы, а не данные реальной статистики. Проверь их на своей аудитории.');

// ---------- экраны ----------
let fresh = null; // последний сгенерированный отчёт: { report, savedId }

function newScreen(prefill = '', error = '') {
  fresh = null;
  const input = h('input', { id: 'niche', type: 'text', maxlength: 100, autocomplete: 'off', placeholder: 'Например: Личные финансы', required: true, value: prefill });
  const err = h('p', { class: 'form-error', role: 'alert', hidden: !error }, error);
  const form = h('form', { class: 'finder', onsubmit: (e) => { e.preventDefault(); analyze(input.value); } },
    h('label', { for: 'niche' }, 'Введите вашу нишу'),
    h('div', { class: 'finder-row' }, input, h('button', { class: 'btn', type: 'submit' }, 'Анализировать нишу')),
    h('div', { class: 'examples', 'aria-label': 'Примеры ниш' },
      EXAMPLES.map((ex) => h('button', { type: 'button', class: 'chip', onclick: () => { input.value = ex; input.focus(); } }, ex))),
    err);
  show(
    h('div', { class: 'hero' },
      h('h1', null, 'Исследователь ниши'),
      h('p', null, 'Введите любую нишу и поймите, кто ваша аудитория, какие у нее проблемы, чего она хочет, какой контент она потребляет и что вы потенциально можете ей продавать.')),
    form);
  input.focus({ preventScroll: true });
}

async function analyze(rawNiche) {
  const niche = rawNiche.trim();
  if (niche.length < 2) return newScreen(rawNiche, 'Введи нишу — хотя бы пару букв.');

  const status = h('p', { 'aria-live': 'polite' }, LOADING_STEPS[0]);
  show(h('div', { class: 'card loading' }, h('div', { class: 'spinner', 'aria-hidden': 'true' }), h('h2', null, `Анализирую нишу «${niche}»`), status,
    h('p', null, 'Обычно это занимает 30–60 секунд.')));
  let step = 0;
  const timer = setInterval(() => { status.textContent = LOADING_STEPS[++step % LOADING_STEPS.length]; }, 6000);

  try {
    const { report } = await api('/api/analyze', { method: 'POST', body: { niche } });
    clearInterval(timer);
    fresh = { report, savedId: null };
    reportScreen();
  } catch (e) {
    clearInterval(timer);
    newScreen(niche, e.message);
  }
}

function reportScreen() {
  const { report } = fresh;
  const saveButtons = [];
  const paint = () => saveButtons.forEach((b) => {
    b.disabled = false;
    if (fresh.savedId) {
      b.className = 'btn btn-done';
      b.textContent = 'Сохранено ✓';
      b.disabled = true;
    }
  });
  const makeSave = () => {
    const b = h('button', { class: 'btn', type: 'button', onclick: save }, 'Сохранить исследование');
    saveButtons.push(b);
    return b;
  };
  async function save() {
    saveButtons.forEach((b) => { b.disabled = true; b.textContent = 'Сохраняю…'; });
    try {
      const { saved } = await api('/api/reports', { method: 'POST', body: { report } });
      fresh.savedId = saved.id;
      paint();
      note.textContent = '';
      note.append('Исследование сохранено. ', h('a', { href: '#/saved' }, 'Открыть сохраненные'));
    } catch (e) {
      saveButtons.forEach((b) => { b.disabled = false; b.textContent = 'Сохранить исследование'; });
      note.textContent = e.message;
      note.style.color = 'var(--danger)';
    }
  }
  const note = h('p', { class: 'disclaimer', role: 'status' });

  show(
    h('div', { class: 'report-head' },
      h('div', null, h('div', { class: 'eyebrow' }, 'Исследование ниши'), h('h1', null, report.niche)),
      makeSave()),
    note,
    ...renderSections(report),
    h('div', { class: 'report-foot' }, makeSave()),
    disclaimer());
  paint();
}

async function savedScreen() {
  show(h('div', { class: 'saved-title' }, h('h1', null, 'Сохраненное исследование'), h('p', null, 'Загружаю…')));
  let reports;
  try {
    ({ reports } = await api('/api/reports'));
  } catch (e) {
    return show(h('div', { class: 'empty' }, h('h2', null, 'Не получилось загрузить'), h('p', null, e.message), h('button', { class: 'btn', onclick: savedScreen }, 'Попробовать снова')));
  }

  const head = h('div', { class: 'saved-title' }, h('h1', null, 'Сохраненное исследование'), h('p', null, 'Все твои анализы ниш — открывай в любой момент, заново генерировать не нужно.'));
  if (!reports.length) {
    return show(head, h('div', { class: 'empty' }, h('h2', null, 'Пока ничего не сохранено'), h('p', null, 'Проанализируй нишу и нажми «Сохранить исследование».'), h('a', { class: 'btn', href: '#/new' }, 'Новое исследование')));
  }

  const list = h('ul', { class: 'saved-list' });
  const draw = () => list.replaceChildren(...reports.map(item));
  function item(r) {
    const del = h('button', { class: 'btn btn-quiet btn-danger', type: 'button' }, 'Удалить');
    let armed = null;
    del.addEventListener('click', async () => {
      if (!armed) { // двухшаговое удаление без всплывающих окон
        del.textContent = 'Точно удалить?';
        armed = setTimeout(() => { armed = null; del.textContent = 'Удалить'; }, 3500);
        return;
      }
      clearTimeout(armed);
      del.disabled = true;
      try {
        await api(`/api/reports/${r.id}`, { method: 'DELETE' });
        reports = reports.filter((x) => x.id !== r.id);
        reports.length ? draw() : savedScreen();
      } catch (e) {
        del.disabled = false;
        del.textContent = e.message;
        armed = null;
      }
    });
    return h('li', { class: 'saved-item' },
      h('div', null, h('h2', null, r.niche), h('time', { datetime: r.createdAt }, formatDate(r.createdAt))),
      h('div', { class: 'saved-actions' }, h('a', { class: 'btn btn-quiet', href: `#/saved/${r.id}` }, 'Открыть'), del));
  }
  draw();
  show(head, list);
}

async function savedReportScreen(id) {
  let found;
  try {
    found = await api(`/api/reports/${id}`);
  } catch (e) {
    return show(h('div', { class: 'empty' }, h('h2', null, 'Исследование не найдено'), h('p', null, e.message), h('a', { class: 'btn', href: '#/saved' }, 'К сохраненным')));
  }
  show(
    h('a', { class: 'back', href: '#/saved' }, '← Сохраненное исследование'),
    h('div', { class: 'report-head' },
      h('div', null, h('div', { class: 'eyebrow' }, 'Исследование ниши'), h('h1', null, found.report.niche),
        h('p', { class: 'meta' }, `Сохранено ${formatDate(found.createdAt)}`))),
    ...renderSections(found.report),
    disclaimer());
}

// ---------- маршрутизация ----------
function route() {
  const hash = location.hash.replace(/^#/, '') || '/new';
  const m = hash.match(/^\/saved\/([0-9a-f-]{36})$/);
  const tab = hash.startsWith('/saved') ? 'saved' : 'new';
  document.querySelectorAll('[data-nav]').forEach((a) => {
    if (a.dataset.nav === tab) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
  if (m) savedReportScreen(m[1]);
  else if (tab === 'saved') savedScreen();
  else newScreen();
}
window.addEventListener('hashchange', route);
route();

// повторный клик по текущему разделу возвращает на чистый экран
document.querySelectorAll('[data-nav]').forEach((a) =>
  a.addEventListener('click', () => { if (a.getAttribute('href') === location.hash) route(); }));
