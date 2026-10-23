// Создатель сценариев каруселей — клиентская часть (без сборки и зависимостей).

/* ───────────────────────── Справочники ───────────────────────── */

const NICHES = ['Деньги и бизнес', 'Личностное развитие', 'Фитнес и здоровье', 'Отношения', 'Недвижимость', 'Маркетинг', 'Искусственный интеллект', 'Продуктивность', 'Мотивация', 'Своя ниша'];
const AUDIENCES = ['Полные новички', 'Люди, уже знакомые с темой', 'Владельцы бизнеса', 'Создатели контента', 'Наёмные сотрудники', 'Студенты', 'Специалисты', 'Люди, столкнувшиеся с конкретной проблемой', 'Своя аудитория'];
const GOALS = ['Обучить аудиторию', 'Укрепить доверие и авторитет', 'Вызвать любопытство', 'Оспорить распространённое убеждение', 'Побудить сохранять публикацию и делиться ею', 'Получить комментарии', 'Продать цифровой продукт', 'Своя цель'];
const TONES = ['Смелый и прямой', 'Обучающий и вызывающий доверие', 'Разговорный', 'Мотивирующий', 'Идущий вразрез с общепринятым мнением', 'Профессиональный', 'Простой и понятный новичкам', 'Повествовательный', 'Создающий ощущение срочности', 'Юмористический'];

const CUSTOM_NICHE = 'Своя ниша';
const CUSTOM_AUDIENCE = 'Своя аудитория';
const CUSTOM_GOAL = 'Своя цель';
const SALE_GOAL = 'Продать цифровой продукт';

const KEYS = { projects: 'carousel.projects.v1', draft: 'carousel.draft.v1', session: 'carousel.session.v1' };
const PLACEHOLDER_RE = /\[ДОБАВЬ[^\]]*\]/gi;

/* ───────────────────────── Утилиты ───────────────────────── */

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const uid = () => (crypto.randomUUID ? crypto.randomUUID() : `id-${Date.now()}-${Math.random().toString(36).slice(2)}`);
const wordCount = (t) => t.trim().split(/\s+/).filter(Boolean).length;
const placeholderCount = (t) => (t.match(PLACEHOLDER_RE) || []).length;
const pluralize = (n, one, few, many) => {
  const m10 = n % 10, m100 = n % 100;
  if (m10 === 1 && m100 !== 11) return one;
  if (m10 >= 2 && m10 <= 4 && (m100 < 12 || m100 > 14)) return few;
  return many;
};
const fmtDate = (ts) => new Date(ts).toLocaleString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });

const storage = {
  get(key, fallback) {
    try { const raw = localStorage.getItem(key); return raw ? JSON.parse(raw) : fallback; } catch { return fallback; }
  },
  set(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch { return false; }
  },
  remove(key) { try { localStorage.removeItem(key); } catch { /* ничего */ } },
};

const ICONS = {
  copy: '<rect x="9" y="9" width="11" height="11" rx="2.5"/><path d="M5 15V6.5A2.5 2.5 0 0 1 7.5 4H15"/>',
  edit: '<path d="M4 20h4l10.5-10.5a2.1 2.1 0 0 0-3-3L5 17v3z"/>',
  refresh: '<path d="M20 11a8 8 0 0 0-14.5-4M4 4v4h4M4 13a8 8 0 0 0 14.5 4M20 20v-4h-4"/>',
  shorten: '<path d="M5 8h14M8 12h8M10.5 16h3"/>',
  spark: '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3zM19 17l.8 2.2L22 20l-2.2.8L19 23l-.8-2.2L16 20l2.2-.8L19 17z"/>',
  longer: '<path d="M5 7h14M5 12h14M5 17h9"/>',
  up: '<path d="M12 19V5M6 11l6-6 6 6"/>',
  down: '<path d="M12 5v14M6 13l6 6 6-6"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  trash: '<path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12M9 7V4h6v3"/>',
  check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
  search: '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>',
  save: '<path d="M5 4h11l3 3v13H5zM8 4v5h7V4M8 20v-6h8v6"/>',
  back: '<path d="M19 12H5M11 6l-6 6 6 6"/>',
  warn: '<path d="M12 4l9 16H3L12 4zM12 10v4M12 17v.5"/>',
  open: '<path d="M4 7a2 2 0 0 1 2-2h4l2 2h6a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7z"/>',
};
const icon = (name) => `<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name]}</svg>`;

/* ───────────────────────── Состояние ───────────────────────── */

const defaultSettings = () => ({
  niche: '', nicheCustom: '',
  audience: '', audienceDetails: '',
  goal: '', goalCustom: '', product: '',
  tone: '', tone2: '',
  count: 7,
  topic: '',
});

const state = {
  view: 'create',            // create | projects
  step: 'settings',          // settings | generating | result
  settings: { ...defaultSettings(), ...storage.get(KEYS.draft, {}) },
  result: null,              // { title, cta, caption, captionBusy, slides: [{ id, text, busy }] }
  projectId: null,
  projectName: '',
  dirty: false,
  error: null,
  health: null,
  search: '',
};
let projects = storage.get(KEYS.projects, []);

(function restoreSession() {
  const s = storage.get(KEYS.session, null);
  if (!s?.result?.slides?.length) return;
  state.result = {
    title: s.result.title || '',
    cta: s.result.cta || '',
    caption: s.result.caption || '',
    captionBusy: null,
    brief: s.result.brief || null,
    slides: s.result.slides.map((t) => ({ id: uid(), text: String(t), busy: null })),
  };
  state.projectId = s.projectId || null;
  state.projectName = s.projectName || '';
  state.dirty = Boolean(s.dirty);
  if (s.settings) state.settings = { ...defaultSettings(), ...s.settings };
  state.step = 'result';
})();

let sessionTimer;
function persistSession() {
  clearTimeout(sessionTimer);
  sessionTimer = setTimeout(() => {
    if (!state.result) { storage.remove(KEYS.session); return; }
    storage.set(KEYS.session, {
      settings: state.settings,
      projectId: state.projectId,
      projectName: state.projectName,
      dirty: state.dirty,
      result: {
        title: state.result.title,
        cta: state.result.cta,
        caption: state.result.caption,
        brief: state.result.brief,
        slides: state.result.slides.map((s) => s.text),
      },
    });
  }, 250);
}
const persistDraft = () => storage.set(KEYS.draft, state.settings);
function markDirty() { state.dirty = true; updateStatus(); persistSession(); }

/* ───────────────────────── Подсказки, диалог, буфер обмена ───────────────────────── */

const toastEl = $('#toast');
let toastTimer;
function toast(message, { error = false, action = null, ms } = {}) {
  clearTimeout(toastTimer);
  toastEl.className = 'toast';
  toastEl.replaceChildren(document.createTextNode(message));
  if (action) {
    const b = document.createElement('button');
    b.textContent = action.label;
    b.className = 'toast__action';
    b.onclick = () => { toastEl.classList.remove('is-on'); action.fn(); };
    toastEl.append(b);
    toastEl.classList.add('has-action');
  }
  if (error) toastEl.classList.add('is-error');
  requestAnimationFrame(() => toastEl.classList.add('is-on'));
  toastTimer = setTimeout(() => toastEl.classList.remove('is-on'), ms ?? (action ? 7000 : error ? 6000 : 2200));
}

const dialog = $('#dialog');
function confirmDialog({ title, text, okLabel = 'Подтвердить', danger = true }) {
  $('#dialogTitle').textContent = title;
  $('#dialogText').textContent = text;
  const ok = $('#dialogOk');
  ok.textContent = okLabel;
  ok.className = `btn ${danger ? 'btn--danger' : 'btn--primary'}`;
  dialog.returnValue = '';
  dialog.showModal();
  return new Promise((resolve) => {
    dialog.addEventListener('close', () => resolve(dialog.returnValue === 'ok'), { once: true });
  });
}

async function copyText(text, okMessage = 'Скопировано') {
  try {
    await navigator.clipboard.writeText(text);
  } catch {
    // запасной путь для браузеров без доступа к буферу обмена
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
    document.body.append(ta);
    ta.select();
    let ok = false;
    try { ok = document.execCommand('copy'); } catch { /* ничего */ }
    ta.remove();
    if (!ok) { toast('Не получилось скопировать. Выдели текст и скопируй вручную.', { error: true }); return false; }
  }
  toast(okMessage);
  return true;
}

/* ───────────────────────── Запросы к серверу ───────────────────────── */

async function api(path, body) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 240_000);
  let res;
  try {
    res = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: ctrl.signal });
  } catch (e) {
    throw new Error(e.name === 'AbortError' ? 'Генерация заняла слишком много времени. Попробуй ещё раз.' : 'Не удалось связаться с сервером. Проверь интернет и попробуй ещё раз.');
  } finally {
    clearTimeout(timer);
  }
  let data = null;
  try { data = await res.json(); } catch { /* не JSON */ }
  if (!res.ok) throw new Error(data?.error || 'Что-то пошло не так. Попробуй ещё раз.');
  return data;
}

/* ───────────────────────── Настройки → данные для ИИ ───────────────────────── */

function resolveSettings(s) {
  const niche = s.niche === CUSTOM_NICHE ? s.nicheCustom.trim() : s.niche;
  const details = s.audienceDetails.trim();
  const audience = s.audience === CUSTOM_AUDIENCE ? details : [s.audience, details].filter(Boolean).join(' — ');
  const goal = s.goal === CUSTOM_GOAL ? s.goalCustom.trim() : s.goal;
  const isSale = s.goal === SALE_GOAL;
  return {
    niche, audience, goal,
    tone: s.tone,
    tone2: s.tone2 && s.tone2 !== s.tone ? s.tone2 : '',
    count: s.count,
    topic: s.topic.trim(),
    product: isSale ? s.product.trim() : '',
  };
}

function validateSettings(s) {
  if (!s.niche) return { field: 'niche', message: 'Выбери нишу.' };
  if (s.niche === CUSTOM_NICHE && !s.nicheCustom.trim()) return { field: 'nicheCustom', message: 'Напиши свою нишу.' };
  if (!s.audience) return { field: 'audience', message: 'Выбери целевую аудиторию.' };
  if (s.audience === CUSTOM_AUDIENCE && !s.audienceDetails.trim()) return { field: 'audienceDetails', message: 'Опиши свою аудиторию.' };
  if (!s.goal) return { field: 'goal', message: 'Выбери основную цель.' };
  if (s.goal === CUSTOM_GOAL && !s.goalCustom.trim()) return { field: 'goalCustom', message: 'Напиши свою цель.' };
  if (!s.tone) return { field: 'tone', message: 'Выбери тон.' };
  return null;
}

/* ───────────────────────── Каркас и навигация ───────────────────────── */

const app = $('#app');

function render() {
  clearInterval(loadingTimer);
  $$('.nav__btn').forEach((b) => b.classList.toggle('is-active', b.dataset.nav === state.view));
  $('#projectsCount').textContent = projects.length;
  if (state.view === 'projects') renderProjects();
  else if (state.step === 'generating') renderGenerating();
  else if (state.step === 'result' && state.result) renderResult();
  else renderSettings();
  window.scrollTo({ top: 0 });
}

function stepsHTML(active, busy = false) {
  const items = ['Настройки', 'Генерация', 'Результат'];
  return `<ol class="steps" aria-label="Шаги">${items.map((label, i) => {
    const cls = i < active ? 'is-done' : i === active ? `is-active${busy ? ' is-busy' : ''}` : '';
    return `<li class="step ${cls}"${i === active ? ' aria-current="step"' : ''}><div class="step__bar"></div><span class="step__label">${i + 1}. ${label}</span></li>`;
  }).join('')}</ol>`;
}

async function guardUnsaved() {
  if (!state.result || !state.dirty) return true;
  return confirmDialog({
    title: 'Есть несохранённая карусель',
    text: 'Если продолжишь, текущая карусель пропадёт. Сохрани её в проекты, если хочешь вернуться к ней позже.',
    okLabel: 'Продолжить без сохранения',
  });
}

$$('.nav__btn').forEach((b) => b.addEventListener('click', () => { state.view = b.dataset.nav; render(); }));
$('#brand').addEventListener('click', () => { state.view = 'create'; render(); });

/* ───────────────────────── Шаг 1: настройки ───────────────────────── */

const options = (list, selected, placeholder) =>
  `<option value="" ${selected ? '' : 'selected'} disabled>${placeholder}</option>` +
  list.map((o) => `<option value="${esc(o)}" ${o === selected ? 'selected' : ''}>${esc(o)}</option>`).join('');

function renderSettings() {
  const s = state.settings;
  app.innerHTML = `
    ${stepsHTML(0)}
    <h1 class="h1">Сценарий карусели за пару минут</h1>
    <p class="lead">Выбери настройки, и я напишу тексты слайдов, подпись и экспорт, который остаётся вставить в твоё приложение для оформления.</p>

    <div id="healthNotice"></div>
    ${state.result ? `<div class="notice notice--info"><div class="notice__body"><strong>У тебя уже есть карусель</strong>Если создашь новую, она заменит текущую.
      <div class="notice__actions"><button class="btn btn--ghost btn--sm" id="backToResult" type="button">${icon('back')} Вернуться к результату</button></div></div></div>` : ''}
    <div id="formError" ${state.error ? '' : 'hidden'}>${state.error ? errorNoticeHTML(state.error) : ''}</div>

    <form class="card stack" id="settingsForm" novalidate>
      <div class="field">
        <label class="label" for="niche">Ниша</label>
        <select class="select" id="niche" name="niche">${options(NICHES, s.niche, 'Выбери нишу')}</select>
      </div>
      <div class="field" id="nicheCustomWrap" hidden>
        <label class="label" for="nicheCustom">Твоя ниша</label>
        <input class="input" id="nicheCustom" name="nicheCustom" maxlength="200" placeholder="Например: парикмахерское искусство" value="${esc(s.nicheCustom)}">
      </div>

      <div class="field">
        <label class="label" for="audience">Целевая аудитория</label>
        <select class="select" id="audience" name="audience">${options(AUDIENCES, s.audience, 'Выбери аудиторию')}</select>
      </div>
      <div class="field">
        <label class="label" for="audienceDetails" id="audienceDetailsLabel">Подробнее об аудитории <small>необязательно</small></label>
        <textarea class="textarea" id="audienceDetails" name="audienceDetails" rows="2" maxlength="600" placeholder="Кто эти люди, что они уже умеют, чего боятся, чего хотят">${esc(s.audienceDetails)}</textarea>
      </div>

      <div class="field">
        <label class="label" for="goal">Основная цель</label>
        <select class="select" id="goal" name="goal">${options(GOALS, s.goal, 'Выбери цель')}</select>
      </div>
      <div class="field" id="goalCustomWrap" hidden>
        <label class="label" for="goalCustom">Твоя цель</label>
        <input class="input" id="goalCustom" name="goalCustom" maxlength="300" placeholder="Чего ты хочешь добиться этой публикацией?" value="${esc(s.goalCustom)}">
      </div>
      <div class="field" id="productWrap" hidden>
        <label class="label" for="product">Твой цифровой продукт <small>название и что внутри</small></label>
        <textarea class="textarea" id="product" name="product" rows="2" maxlength="600" placeholder="Например: курс «…», 12 уроков, для начинающих. Без продукта я оставлю в тексте место, куда его вписать.">${esc(s.product)}</textarea>
      </div>

      <div class="row">
        <div class="field">
          <label class="label" for="tone">Основной тон</label>
          <select class="select" id="tone" name="tone">${options(TONES, s.tone, 'Выбери тон')}</select>
        </div>
        <div class="field">
          <label class="label" for="tone2">Дополнительный тон <small>необязательно</small></label>
          <select class="select" id="tone2" name="tone2"></select>
        </div>
      </div>

      <div class="field">
        <span class="label" id="countLabel">Количество слайдов</span>
        <div class="count" role="group" aria-labelledby="countLabel">
          ${Array.from({ length: 10 }, (_, i) => `<button type="button" class="count__btn" data-count="${i + 1}" aria-pressed="${s.count === i + 1}">${i + 1}</button>`).join('')}
        </div>
      </div>

      <div class="field">
        <label class="label" for="topic">О чём карусель <small>необязательно</small></label>
        <textarea class="textarea" id="topic" name="topic" rows="2" maxlength="800" placeholder="Тема или идея. Если оставишь пустым, я предложу сильную тему сама.">${esc(s.topic)}</textarea>
      </div>

      <button class="btn btn--primary btn--big" type="submit">Создать сценарий карусели</button>
    </form>`;

  const form = $('#settingsForm');
  syncConditionalFields();
  buildTone2();

  form.addEventListener('input', (e) => {
    const { name, value } = e.target;
    if (!name || !(name in state.settings)) return;
    state.settings[name] = value;
    e.target.removeAttribute('aria-invalid');
    persistDraft();
  });
  form.addEventListener('change', (e) => {
    if (['niche', 'audience', 'goal', 'tone'].includes(e.target.name)) {
      syncConditionalFields();
      if (e.target.name === 'tone') buildTone2();
    }
  });
  $$('.count__btn', form).forEach((b) => b.addEventListener('click', () => {
    state.settings.count = Number(b.dataset.count);
    $$('.count__btn', form).forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
    persistDraft();
  }));
  form.addEventListener('submit', (e) => { e.preventDefault(); startGeneration(); });
  $('#backToResult')?.addEventListener('click', () => { state.error = null; state.step = 'result'; render(); });
  showHealthNotice();
}

function syncConditionalFields() {
  const s = state.settings;
  $('#nicheCustomWrap').hidden = s.niche !== CUSTOM_NICHE;
  $('#goalCustomWrap').hidden = s.goal !== CUSTOM_GOAL;
  $('#productWrap').hidden = s.goal !== SALE_GOAL;
  const own = s.audience === CUSTOM_AUDIENCE;
  $('#audienceDetailsLabel').innerHTML = own ? 'Опиши свою аудиторию' : 'Подробнее об аудитории <small>необязательно</small>';
}

function buildTone2() {
  const s = state.settings;
  if (s.tone2 === s.tone) s.tone2 = '';
  const sel = $('#tone2');
  sel.innerHTML = `<option value="">Без дополнительного тона</option>` +
    TONES.filter((t) => t !== s.tone).map((t) => `<option value="${esc(t)}" ${t === s.tone2 ? 'selected' : ''}>${esc(t)}</option>`).join('');
  persistDraft();
}

function errorNoticeHTML(message) {
  return `<div class="notice notice--error" role="alert">${icon('warn')}<div class="notice__body"><strong>Не получилось</strong>${esc(message)}<br><span style="opacity:.85">Твои настройки сохранены, ничего вводить заново не нужно.</span></div></div>`;
}

async function showHealthNotice() {
  if (!state.health) {
    try { state.health = await (await fetch('/api/health')).json(); } catch { state.health = { configured: true }; }
  }
  const box = $('#healthNotice');
  if (!box) return;
  if (state.health.mock) {
    box.innerHTML = `<div class="notice notice--warn">${icon('warn')}<div class="notice__body"><strong>Демо-режим</strong>ИИ не подключён, тексты будут заглушками. Нужен для проверки интерфейса.</div></div>`;
  } else if (!state.health.configured) {
    box.innerHTML = `<div class="notice notice--warn">${icon('warn')}<div class="notice__body"><strong>ИИ пока не подключён</strong>На сервере не задан ключ ANTHROPIC_API_KEY. Интерфейс работает, но сценарий создать нельзя, пока ключ не добавлен.</div></div>`;
  }
}

/* ───────────────────────── Шаг 2: генерация ───────────────────────── */

let loadingTimer;
const LOADING_MESSAGES = ['Придумываю крючок…', 'Раскладываю мысль по слайдам…', 'Проверяю, чтобы слайды вели друг к другу…', 'Пишу подпись к публикации…', 'Шлифую формулировки…'];

function renderGenerating() {
  app.innerHTML = `
    ${stepsHTML(1, true)}
    <div class="card loading" role="status" aria-live="polite">
      <div class="loading__orb"></div>
      <p class="loading__msg" id="loadingMsg">${LOADING_MESSAGES[0]}</p>
      <p class="muted">Обычно это занимает от 20 секунд до минуты. Не закрывай страницу.</p>
    </div>`;
  let i = 0;
  loadingTimer = setInterval(() => {
    i = (i + 1) % LOADING_MESSAGES.length;
    const el = $('#loadingMsg');
    if (el) el.textContent = LOADING_MESSAGES[i];
  }, 3200);
}

async function startGeneration() {
  const problem = validateSettings(state.settings);
  if (problem) {
    state.error = problem.message;
    $('#formError').hidden = false;
    $('#formError').innerHTML = `<div class="notice notice--error" role="alert">${icon('warn')}<div class="notice__body">${esc(problem.message)}</div></div>`;
    const field = $(`#${problem.field}`);
    field?.setAttribute('aria-invalid', 'true');
    field?.scrollIntoView({ block: 'center', behavior: 'smooth' });
    field?.focus({ preventScroll: true });
    return;
  }
  if (!(await guardUnsaved())) return;

  const payload = resolveSettings(state.settings);
  state.error = null;
  state.step = 'generating';
  render();
  try {
    const data = await api('/api/generate', { settings: payload });
    if (!Array.isArray(data.slides) || data.slides.length !== payload.count) {
      throw new Error(`ИИ вернул не то количество слайдов (нужно ${payload.count}). Нажми кнопку ещё раз.`);
    }
    state.result = {
      title: data.title || '',
      cta: data.cta || '',
      caption: data.caption || '',
      captionBusy: null,
      brief: payload,
      slides: data.slides.map((text) => ({ id: uid(), text, busy: null })),
    };
    state.projectId = null;
    state.projectName = data.title || '';
    state.dirty = true;
    state.step = 'result';
    persistSession();
  } catch (e) {
    state.error = e.message;
    state.step = 'settings';
  }
  render();
}

/* ───────────────────────── Шаг 3: результат ───────────────────────── */

function renderResult() {
  const r = state.result;
  app.innerHTML = `
    ${stepsHTML(2)}
    <div class="result-head">
      <div style="display:flex;gap:8px;flex-wrap:wrap;justify-content:space-between;align-items:center">
        <button class="back-link" id="toSettings" type="button">${icon('back')} Изменить настройки</button>
        <button class="btn btn--ghost btn--sm" id="newCarousel" type="button">${icon('plus')} Новая карусель</button>
      </div>
      <h1 class="h1" style="margin:0">Сценарий готов</h1>
      <p class="lead" style="margin:0">Каждый текст можно править прямо в карточке. Места, где нужны твои факты, помечены как [ДОБАВЬ: …].</p>
      <div class="card">
        <div class="save-bar">
          <input class="input" id="projectName" maxlength="120" placeholder="Название проекта" aria-label="Название проекта" value="${esc(state.projectName)}">
          <button class="btn btn--primary" id="saveBtn" type="button">${icon('save')}<span id="saveLabel"></span></button>
        </div>
        <div class="status" id="status" style="margin-top:10px"></div>
      </div>
      <div id="placeholderNotice"></div>
    </div>

    <section class="section" aria-labelledby="s1">
      <div class="section__head">
        <div class="section__num">Раздел 1</div>
        <h2 class="h2" id="s1">Тексты слайдов</h2>
        <p class="card__sub" id="slidesCount"></p>
      </div>
      <div id="slides"></div>
    </section>

    <section class="section" aria-labelledby="s2" id="captionSec"></section>

    <section class="section" aria-labelledby="s3">
      <div class="card">
        <div class="section__head" style="margin-bottom:6px">
          <div class="section__num">Раздел 3</div>
          <h2 class="h2" id="s3">Экспорт для приложения с каруселями</h2>
          <p class="card__sub">Скопируй и вставь в приложение, где ты оформляешь карусели. Переносы строк сохраняются.</p>
        </div>
        <div class="row" style="margin-top:14px">
          <div class="field">
            <label class="label" for="exTitle">Название карусели</label>
            <input class="input" id="exTitle" maxlength="150" value="${esc(r.title)}">
          </div>
          <div class="field">
            <label class="label" for="exCta">Призыв к действию</label>
            <input class="input" id="exCta" maxlength="300" value="${esc(r.cta)}">
          </div>
        </div>
        <div class="export__preview" id="exportPreview" aria-label="Предпросмотр экспорта"></div>
        <div class="export__actions">
          <button class="btn btn--primary" id="copyAll" type="button">${icon('copy')} Скопировать всё для приложения для создания каруселей</button>
          <button class="btn btn--ghost" id="copySlides" type="button">${icon('copy')} Скопировать только тексты слайдов</button>
        </div>
      </div>
    </section>`;

  renderSlides();
  renderCaption();
  updateExport();
  updateStatus();

  $('#toSettings').addEventListener('click', () => { state.step = 'settings'; render(); });
  $('#newCarousel').addEventListener('click', async () => {
    if (!(await guardUnsaved())) return;
    state.result = null; state.projectId = null; state.projectName = ''; state.dirty = false; state.step = 'settings';
    storage.remove(KEYS.session);
    render();
  });
  $('#projectName').addEventListener('input', (e) => { state.projectName = e.target.value; markDirty(); });
  $('#saveBtn').addEventListener('click', saveProject);
  $('#exTitle').addEventListener('input', (e) => { r.title = e.target.value; updateExport(); markDirty(); });
  $('#exCta').addEventListener('input', (e) => { r.cta = e.target.value; updateExport(); markDirty(); });
  $('#copyAll').addEventListener('click', () => copyExport(exportAll(), 'Всё скопировано. Вставляй в приложение для каруселей'));
  $('#copySlides').addEventListener('click', () => copyExport(exportSlidesOnly(), 'Тексты слайдов скопированы'));
}

function updateStatus() {
  const status = $('#status');
  if (!status) return;
  const saved = projects.find((p) => p.id === state.projectId);
  $('#saveLabel').textContent = saved ? 'Сохранить изменения' : 'Сохранить проект';
  if (state.dirty) {
    status.textContent = saved ? 'Есть несохранённые изменения' : 'Ещё не сохранено в проекты';
    status.className = 'status status--dirty';
  } else {
    status.textContent = saved ? `Сохранено · ${fmtDate(saved.updatedAt)}` : '';
    status.className = 'status';
  }
}

/* ── Слайды ── */

const BUSY_LABELS = { regenerate: 'Пишу заново…', shorter: 'Сокращаю…', stronger: 'Усиливаю…', add: 'Пишу новый слайд…' };

function tool(act, label, ico, { title, cls = '', disabled = false, iconOnly = false } = {}) {
  return `<button type="button" class="tool ${cls} ${iconOnly ? 'tool--icon' : ''}" data-act="${act}" title="${esc(title || label)}" aria-label="${esc(title || label)}" ${disabled ? 'disabled' : ''}>${icon(ico)}${iconOnly ? '' : `<span>${label}</span>`}</button>`;
}

function slideHTML(s, i, total) {
  const off = Boolean(s.busy);
  return `
  <article class="slide ${off ? 'is-busy' : ''}" data-id="${s.id}">
    <div class="slide__top">
      <span class="slide__badge"><i>${i + 1}</i>Слайд ${i + 1}</span>
      <span class="slide__words" data-words></span>
    </div>
    <textarea class="textarea slide__text" data-text rows="3" aria-label="Текст слайда ${i + 1}" ${off ? 'disabled' : ''}></textarea>
    <div class="slide__flag" data-flag hidden></div>
    <div class="slide__tools">
      <div class="tool-group">
        ${tool('edit', 'Редактировать', 'edit', { disabled: off })}
        ${tool('copy', 'Копировать', 'copy', { title: 'Копировать текст слайда', disabled: off })}
      </div>
      <span class="tool-sep"></span>
      <div class="tool-group">
        ${tool('regenerate', 'Заново', 'refresh', { title: 'Сгенерировать слайд заново', cls: 'tool--accent', disabled: off })}
        ${tool('shorter', 'Короче', 'shorten', { title: 'Сделать короче', cls: 'tool--accent', disabled: off })}
        ${tool('stronger', 'Сильнее', 'spark', { title: 'Сделать сильнее', cls: 'tool--accent', disabled: off })}
      </div>
      <span class="tool-sep"></span>
      <div class="tool-group">
        ${tool('up', 'Выше', 'up', { title: 'Переместить слайд вверх', iconOnly: true, disabled: off || i === 0 })}
        ${tool('down', 'Ниже', 'down', { title: 'Переместить слайд вниз', iconOnly: true, disabled: off || i === total - 1 })}
        ${tool('add', 'Добавить ниже', 'plus', { title: 'Добавить слайд ниже', disabled: off })}
        ${tool('delete', 'Удалить', 'trash', { title: 'Удалить слайд', cls: 'tool--danger', iconOnly: true, disabled: off || total === 1 })}
      </div>
    </div>
    ${off ? `<div class="slide__busy"><span><i class="dot-spin"></i>${BUSY_LABELS[s.busy] || 'Пишу…'}</span></div>` : ''}
  </article>`;
}

function grow(el) {
  el.style.height = 'auto';
  el.style.height = `${el.scrollHeight + 2}px`;
}

function hydrateCard(card, slide) {
  const ta = $('[data-text]', card);
  ta.value = slide.text;
  grow(ta);
  updateCardMeta(card, slide);
}

function updateCardMeta(card, slide) {
  $('[data-words]', card).textContent = `${wordCount(slide.text)} ${pluralize(wordCount(slide.text), 'слово', 'слова', 'слов')}`;
  const flag = $('[data-flag]', card);
  const n = placeholderCount(slide.text);
  flag.hidden = n === 0;
  if (n) flag.textContent = `Здесь нужно добавить твои данные: ${n} ${pluralize(n, 'место', 'места', 'мест')} в [ДОБАВЬ: …]`;
}

function renderSlides() {
  const box = $('#slides');
  const slides = state.result.slides;
  box.innerHTML = slides.map((s, i) => slideHTML(s, i, slides.length)).join('');
  $$('.slide', box).forEach((card, i) => hydrateCard(card, slides[i]));
  $('#slidesCount').textContent = `${slides.length} ${pluralize(slides.length, 'слайд', 'слайда', 'слайдов')}`;
}

function refreshCard(id) {
  const slides = state.result.slides;
  const i = slides.findIndex((s) => s.id === id);
  const old = $(`.slide[data-id="${id}"]`);
  if (i < 0 || !old) return;
  const tmp = document.createElement('div');
  tmp.innerHTML = slideHTML(slides[i], i, slides.length);
  const fresh = tmp.firstElementChild;
  old.replaceWith(fresh);
  hydrateCard(fresh, slides[i]);
}

const slidesBox = () => $('#slides');

document.addEventListener('input', (e) => {
  const ta = e.target.closest?.('.slide [data-text]');
  if (!ta || !state.result) return;
  const card = ta.closest('.slide');
  const slide = state.result.slides.find((s) => s.id === card.dataset.id);
  if (!slide) return;
  slide.text = ta.value;
  grow(ta);
  updateCardMeta(card, slide);
  updateExport();
  markDirty();
});

document.addEventListener('click', (e) => {
  const btn = e.target.closest?.('.slide [data-act]');
  if (!btn || !state.result) return;
  const card = btn.closest('.slide');
  slideAct(card.dataset.id, btn.dataset.act);
});

function slideContext() {
  // Контекст берём из настроек, с которыми карусель создавалась, а не из формы, которую могли изменить позже.
  return { settings: state.result.brief || resolveSettings(state.settings), title: state.result.title };
}

async function slideAct(id, act) {
  const slides = state.result.slides;
  const i = slides.findIndex((s) => s.id === id);
  if (i < 0) return;
  const slide = slides[i];

  switch (act) {
    case 'edit': {
      const ta = $(`.slide[data-id="${id}"] [data-text]`);
      ta.focus();
      ta.setSelectionRange(ta.value.length, ta.value.length);
      return;
    }
    case 'copy':
      copyText(slide.text, `Слайд ${i + 1} скопирован`);
      return;
    case 'up':
    case 'down': {
      const j = act === 'up' ? i - 1 : i + 1;
      if (j < 0 || j >= slides.length) return;
      [slides[i], slides[j]] = [slides[j], slides[i]];
      renderSlides();
      updateExport();
      markDirty();
      $(`.slide[data-id="${id}"]`)?.scrollIntoView({ block: 'center', behavior: 'smooth' });
      return;
    }
    case 'delete': {
      if (slides.length === 1) return;
      const [removed] = slides.splice(i, 1);
      renderSlides();
      updateExport();
      markDirty();
      toast(`Слайд ${i + 1} удалён`, {
        action: {
          label: 'Вернуть',
          fn: () => {
            slides.splice(Math.min(i, slides.length), 0, removed);
            renderSlides(); updateExport(); markDirty();
          },
        },
      });
      return;
    }
    case 'add': {
      const placeholder = { id: uid(), text: '', busy: 'add' };
      const others = slides.map((s) => s.text);
      slides.splice(i + 1, 0, placeholder);
      renderSlides();
      updateExport();
      $(`.slide[data-id="${placeholder.id}"]`)?.scrollIntoView({ block: 'center', behavior: 'smooth' });
      try {
        const { text } = await api('/api/slide', { ...slideContext(), slides: others, index: i, action: 'add' });
        placeholder.text = text;
        markDirty();
      } catch (err) {
        toast(`${err.message} Пустая карточка осталась: напиши текст сам или нажми «Заново».`, { error: true });
      }
      placeholder.busy = null;
      if ($(`.slide[data-id="${placeholder.id}"]`)) refreshCard(placeholder.id);
      updateExport();
      return;
    }
    case 'regenerate':
    case 'shorter':
    case 'stronger': {
      if (slide.busy) return;
      slide.busy = act;
      refreshCard(id);
      try {
        const { text } = await api('/api/slide', { ...slideContext(), slides: slides.map((s) => s.text), index: slides.findIndex((s) => s.id === id), action: act });
        slide.text = text;
        markDirty();
      } catch (err) {
        toast(err.message, { error: true });
      }
      slide.busy = null;
      if ($(`.slide[data-id="${id}"]`)) refreshCard(id);
      updateExport();
    }
  }
}

/* ── Подпись ── */

const CAPTION_BUSY = { regenerate: 'Пишу подпись заново…', shorter: 'Сокращаю…', longer: 'Расширяю…', tone: 'Меняю тон…' };

function renderCaption() {
  const r = state.result;
  const off = Boolean(r.captionBusy);
  const sec = $('#captionSec');
  sec.innerHTML = `
    <div class="card" style="position:relative">
      <div class="section__head" style="margin-bottom:10px">
        <div class="section__num">Раздел 2</div>
        <h2 class="h2" id="s2">Подпись к публикации в Instagram</h2>
        <p class="card__sub">Дополняет карусель и не пересказывает слайды.</p>
      </div>
      <textarea class="textarea caption__text" id="captionText" aria-label="Подпись к публикации" ${off ? 'disabled' : ''}></textarea>
      <div class="caption__meta" id="captionMeta"></div>
      <div class="caption__tools">
        <button class="btn btn--soft btn--sm" data-cap="copy" type="button" ${off ? 'disabled' : ''}>${icon('copy')} Копировать подпись</button>
        <button class="tool" data-cap="edit" type="button" ${off ? 'disabled' : ''}>${icon('edit')}<span>Редактировать</span></button>
        <button class="tool tool--accent" data-cap="regenerate" type="button" ${off ? 'disabled' : ''}>${icon('refresh')}<span>Сгенерировать заново</span></button>
        <button class="tool tool--accent" data-cap="shorter" type="button" ${off ? 'disabled' : ''}>${icon('shorten')}<span>Сделать короче</span></button>
        <button class="tool tool--accent" data-cap="longer" type="button" ${off ? 'disabled' : ''}>${icon('longer')}<span>Сделать длиннее</span></button>
        <select class="select tone-select" id="captionTone" aria-label="Изменить тон подписи" ${off ? 'disabled' : ''}>
          <option value="" selected disabled>Изменить тон…</option>
          ${TONES.map((t) => `<option value="${esc(t)}">${esc(t)}</option>`).join('')}
        </select>
      </div>
      ${off ? `<div class="slide__busy"><span><i class="dot-spin"></i>${CAPTION_BUSY[r.captionBusy]}</span></div>` : ''}
    </div>`;
  const ta = $('#captionText');
  ta.value = r.caption;
  grow(ta);
  updateCaptionMeta();
  ta.addEventListener('input', () => { r.caption = ta.value; grow(ta); updateCaptionMeta(); updateExport(); markDirty(); });
  $$('[data-cap]', sec).forEach((b) => b.addEventListener('click', () => captionAct(b.dataset.cap)));
  $('#captionTone').addEventListener('change', (e) => captionAct('tone', e.target.value));
}

function updateCaptionMeta() {
  const t = state.result.caption;
  const n = placeholderCount(t);
  $('#captionMeta').textContent = `${t.length} / 2200 знаков${n ? ` · нужно добавить свои данные: ${n}` : ''}`;
}

async function captionAct(act, tone = '') {
  const r = state.result;
  if (act === 'edit') { const ta = $('#captionText'); ta.focus(); ta.setSelectionRange(ta.value.length, ta.value.length); return; }
  if (act === 'copy') { copyText(r.caption, 'Подпись скопирована'); return; }
  if (r.captionBusy) return;
  r.captionBusy = act;
  renderCaption();
  try {
    const { caption } = await api('/api/caption', {
      ...slideContext(), slides: r.slides.map((s) => s.text), caption: r.caption, action: act, tone,
    });
    r.caption = caption;
    markDirty();
  } catch (err) {
    toast(err.message, { error: true });
  }
  r.captionBusy = null;
  if ($('#captionSec')) renderCaption();
  updateExport();
}

/* ── Экспорт ── */

const clean = (t) => t.replace(/\r\n/g, '\n').trim();

function exportSlidesOnly() {
  return state.result.slides.map((s, i) => `СЛАЙД ${i + 1}:\n${clean(s.text)}`).join('\n\n') + '\n';
}

function exportAll() {
  const r = state.result;
  return [
    `НАЗВАНИЕ КАРУСЕЛИ:\n${clean(r.title)}`,
    ...r.slides.map((s, i) => `СЛАЙД ${i + 1}:\n${clean(s.text)}`),
    `ПОДПИСЬ:\n${clean(r.caption)}`,
    `ПРИЗЫВ К ДЕЙСТВИЮ:\n${clean(r.cta)}`,
  ].join('\n\n') + '\n';
}

function totalPlaceholders() {
  const r = state.result;
  return r.slides.reduce((n, s) => n + placeholderCount(s.text), 0) + placeholderCount(r.caption) + placeholderCount(r.cta);
}

function updateExport() {
  if (!state.result || !$('#exportPreview')) return;
  $('#exportPreview').textContent = exportAll();
  const n = totalPlaceholders();
  const box = $('#placeholderNotice');
  box.innerHTML = n
    ? `<div class="notice notice--warn">${icon('warn')}<div class="notice__body"><strong>Осталось добавить свои данные: ${n} ${pluralize(n, 'место', 'места', 'мест')}</strong>Найди пометки [ДОБАВЬ: …] и замени их настоящими фактами, цифрами или примерами. Выдумывать их я не стала.</div></div>`
    : '';
}

async function copyExport(text, message) {
  const ok = await copyText(text, message);
  const n = totalPlaceholders();
  if (ok && n) setTimeout(() => toast(`Не забудь заменить пометки [ДОБАВЬ: …]: их ${n}`, { ms: 4200 }), 1800);
}

/* ───────────────────────── Сохранённые проекты ───────────────────────── */

function writeProjects() {
  if (!storage.set(KEYS.projects, projects)) {
    toast('Не получилось сохранить: память браузера недоступна или заполнена.', { error: true });
    return false;
  }
  return true;
}

function saveProject() {
  const r = state.result;
  const name = state.projectName.trim() || r.title.trim() || 'Без названия';
  const now = Date.now();
  const data = {
    name,
    settings: { ...state.settings },
    title: r.title, cta: r.cta, caption: r.caption, brief: r.brief || null,
    slides: r.slides.map((s) => s.text),
  };
  const before = JSON.stringify(projects);
  const existing = projects.find((p) => p.id === state.projectId);
  if (existing) Object.assign(existing, data, { updatedAt: now });
  else {
    const p = { id: uid(), createdAt: now, updatedAt: now, ...data };
    projects.unshift(p);
    state.projectId = p.id;
  }
  if (!writeProjects()) { projects = JSON.parse(before); if (!existing) state.projectId = null; return; }
  state.projectName = name;
  state.dirty = false;
  const input = $('#projectName');
  if (input) input.value = name;
  $('#projectsCount').textContent = projects.length;
  updateStatus();
  persistSession();
  toast('Проект сохранён');
}

function openProject(id) {
  const p = projects.find((x) => x.id === id);
  if (!p) return;
  state.settings = { ...defaultSettings(), ...p.settings };
  state.result = {
    title: p.title, cta: p.cta, caption: p.caption, captionBusy: null, brief: p.brief || null,
    slides: p.slides.map((text) => ({ id: uid(), text, busy: null })),
  };
  state.projectId = p.id;
  state.projectName = p.name;
  state.dirty = false;
  state.error = null;
  state.view = 'create';
  state.step = 'result';
  persistDraft();
  persistSession();
  render();
}

async function duplicateProject(id) {
  const p = projects.find((x) => x.id === id);
  if (!p) return;
  const now = Date.now();
  const copy = { ...structuredClone(p), id: uid(), name: `${p.name} (копия)`, createdAt: now, updatedAt: now };
  projects.unshift(copy);
  if (writeProjects()) { toast('Копия создана'); render(); } else projects.shift();
}

async function deleteProject(id) {
  const p = projects.find((x) => x.id === id);
  if (!p) return;
  const ok = await confirmDialog({
    title: 'Удалить проект?',
    text: `Проект «${p.name}» будет удалён навсегда. Вернуть его не получится.`,
    okLabel: 'Удалить',
  });
  if (!ok) return;
  const before = projects;
  projects = projects.filter((x) => x.id !== id);
  if (!writeProjects()) { projects = before; return; }
  if (state.projectId === id) { state.projectId = null; state.dirty = Boolean(state.result); persistSession(); }
  toast('Проект удалён');
  render();
}

function renderProjects() {
  app.innerHTML = `
    <h1 class="h1">Проекты</h1>
    <p class="lead">Сохранённые карусели хранятся в этом браузере. Открой любую, чтобы дописать или скопировать.</p>
    ${projects.length ? `<div class="search">${icon('search')}<input class="input" id="search" type="search" placeholder="Искать по названию и тексту" aria-label="Поиск проектов" value="${esc(state.search)}"></div>` : ''}
    <div class="projects" id="projectList"></div>`;
  $('#search')?.addEventListener('input', (e) => { state.search = e.target.value; renderProjectList(); });
  renderProjectList();
}

function renderProjectList() {
  const box = $('#projectList');
  const q = state.search.trim().toLowerCase();
  const list = projects
    .filter((p) => !q || [p.name, p.title, p.caption, ...p.slides].join('\n').toLowerCase().includes(q))
    .sort((a, b) => b.updatedAt - a.updatedAt);

  if (!projects.length) {
    box.innerHTML = `<div class="card empty"><h2 class="h2">Пока пусто</h2><p class="muted">Создай карусель и нажми «Сохранить проект»: она появится здесь.</p><button class="btn btn--primary" id="goCreate" type="button">Создать карусель</button></div>`;
    $('#goCreate').addEventListener('click', () => { state.view = 'create'; render(); });
    return;
  }
  if (!list.length) {
    box.innerHTML = `<div class="card empty"><h2 class="h2">Ничего не найдено</h2><p class="muted">Попробуй другое слово.</p></div>`;
    return;
  }
  box.innerHTML = list.map((p) => {
    const edited = p.updatedAt - p.createdAt > 1000;
    return `<article class="card project" data-id="${p.id}">
      <h2 class="project__title">${esc(p.name)}</h2>
      <div class="project__meta">
        <span>Создан ${fmtDate(p.createdAt)}</span>
        ${edited ? `<span>Обновлён ${fmtDate(p.updatedAt)}</span>` : ''}
        <span>${p.slides.length} ${pluralize(p.slides.length, 'слайд', 'слайда', 'слайдов')}</span>
      </div>
      <p class="project__excerpt">${esc(p.slides[0] || '')}</p>
      <div class="project__actions">
        <button class="btn btn--primary btn--sm" data-p="open" type="button">${icon('edit')} Открыть и редактировать</button>
        <button class="btn btn--ghost btn--sm" data-p="copy" type="button">${icon('copy')} Создать копию</button>
        <button class="btn btn--ghost btn--sm" data-p="delete" type="button">${icon('trash')} Удалить</button>
      </div>
    </article>`;
  }).join('');
  $$('.project', box).forEach((card) => {
    const id = card.dataset.id;
    $('[data-p="open"]', card).addEventListener('click', async () => {
      if (!(await guardUnsaved())) return;
      openProject(id);
    });
    $('[data-p="copy"]', card).addEventListener('click', () => duplicateProject(id));
    $('[data-p="delete"]', card).addEventListener('click', () => deleteProject(id));
  });
}

/* ───────────────────────── Старт ───────────────────────── */

// Высота текстовых полей зависит от шрифта и ширины окна, поэтому пересчитываем её после их изменения.
const regrowAll = () => $$('.slide [data-text], #captionText').forEach(grow);
let resizeTimer;
window.addEventListener('resize', () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(regrowAll, 120); });
document.fonts?.ready.then(regrowAll);

render();
