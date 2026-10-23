// Создатель сценариев каруселей — сервер.
// Отдаёт статику из ./public и проксирует запросы к Claude, чтобы API-ключ не попадал в браузер.

import http from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import Anthropic from '@anthropic-ai/sdk';

try { process.loadEnvFile(); } catch { /* .env необязателен */ }

const here = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC_DIR = path.join(here, 'public');
const PORT = Number(process.env.PORT) || 3000;
const MODEL = process.env.CLAUDE_MODEL || 'claude-opus-5-5';
const MOCK = process.env.MOCK_AI === '1';
const RATE_LIMIT = Number(process.env.RATE_LIMIT_PER_10MIN) || 60;
const TRUST_PROXY = process.env.TRUST_PROXY === '1';

class AppError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

/* ───────────────────────── Промпты ───────────────────────── */

const SYSTEM = `Ты — редактор-копирайтер, который пишет сценарии каруселей для тематических Instagram-страниц. Страницы обучают аудиторию и подводят её к покупке цифрового продукта.

Ты пишешь ТОЛЬКО тексты. Не описывай графику, цвета, шрифты, иллюстрации, фон и вёрстку, не давай указаний дизайнеру.

Язык: по умолчанию пиши по-русски. Если в полях пользователя (тема, аудитория, продукт) явно используется другой язык, например турецкий, пиши на нём.

Правила слайдов:
- Один слайд — одна основная мысль.
- Язык понятен выбранной аудитории, тон выдержан от первого до последнего слайда.
- Никакой воды, общих фраз без содержания и повторов одной и той же мысли разными словами.
- Слайды переходят один в другой естественно: у читателя должно появляться желание свайпнуть дальше.
- Слайд 1 — самый сильный крючок. Он вызывает любопытство, но не обманывает: карусель обязана выполнить обещание крючка.
- Текст короткий, как для карусели в Instagram: слайд 1 — до 12 слов, остальные — до 40 слов, чаще 15–30. Короткие абзацы, осмысленные переносы строк, простые предложения.
- Текст слайда — это только текст для читателя. Без номера слайда, без пометок вроде «Слайд 1», без указаний по оформлению, без markdown и без хештегов. Эмодзи в слайдах не используй.
- Абзацы внутри слайда разделяй переносом строки (одним или пустой строкой).

Честность:
- Не выдумывай статистику, цифры, исследования, отзывы, кейсы и «результаты клиентов».
- Если для убедительности нужен факт, цифра или личный опыт, оставь в тексте маркер в квадратных скобках, который начинается со слова «ДОБАВЬ:», например: [ДОБАВЬ: свой результат за последний месяц]. Автор потом заменит его настоящими данными.

Призыв к действию:
- Последний слайд завершается призывом к действию, который соответствует выбранной основной цели.
- Если цель — продать цифровой продукт, продукт должен вырастать из проблемы, о которой идёт речь: покажи, как он закрывает именно эту боль, а не вспоминай о нём внезапно на последнем слайде. Не обещай результатов, которые нельзя гарантировать. Если название продукта не указано, оставь маркер [ДОБАВЬ: название продукта].

Структура — рекомендация, а не догма. Для длинной карусели обычно: крючок → проблема или любопытство → обучение, объяснение, история или тезисы → итог или открывающаяся возможность → призыв к действию. Если слайдов мало, объединяй роли (например, крючок и проблема в одном слайде), но не раздувай объём. Если слайд всего один, он содержит крючок, главную мысль и призыв к действию.`;

function brief(s) {
  const lines = [
    `Ниша: ${s.niche}`,
    `Целевая аудитория: ${s.audience}`,
    `Основная цель: ${s.goal}`,
    `Основной тон: ${s.tone}${s.tone2 ? `; дополнительный тон: ${s.tone2}` : ''}`,
    `Количество слайдов: ${s.count}`,
  ];
  if (s.topic) lines.push(`Тема или идея карусели: ${s.topic}`);
  else lines.push('Тема карусели не задана: выбери сильную, конкретную тему сам(а), подходящую нише, аудитории и цели.');
  if (s.product) lines.push(`Цифровой продукт автора: ${s.product}`);
  return lines.join('\n');
}

function numbered(slides) {
  return slides.map((t, i) => `[${i + 1}]\n${t}`).join('\n\n');
}

function carouselContext(body) {
  const parts = [`Параметры публикации:\n${brief(body.settings)}`];
  if (body.title) parts.push(`Рабочее название карусели: ${body.title}`);
  if (body.slides?.length) parts.push(`Слайды карусели (нумерация только для тебя):\n${numbered(body.slides)}`);
  return parts.join('\n\n');
}

const CAPTION_RULES = `Правила подписи к публикации в Instagram:
- Она дополняет карусель, а не пересказывает каждый слайд.
- Тон выдержан как в карусели.
- Начинается с цепляющего вступления (первая строка видна без нажатия «ещё»).
- Добавляет контекст или развивает главную мысль, даёт читателю дополнительную ценность.
- Содержит подходящий призыв к действию, соответствующий основной цели.
- Разбита на короткие абзацы для удобного чтения.
- Хештегов нет или не больше трёх по-настоящему релевантных. Никаких «облаков» хештегов.
- Не выдумывай статистику, отзывы и результаты; если нужен факт, оставь маркер [ДОБАВЬ: что именно].
- Обычный объём: 500–900 знаков, не больше 1500. Эмодзи не больше двух-трёх, только если они уместны.
- Верни только текст подписи, без пояснений и заголовков.`;

const CAROUSEL_SCHEMA = {
  type: 'object',
  properties: {
    title: { type: 'string' },
    slides: { type: 'array', items: { type: 'string' } },
    caption: { type: 'string' },
    cta: { type: 'string' },
  },
  required: ['title', 'slides', 'caption', 'cta'],
  additionalProperties: false,
};

function generationPrompt(s, problem) {
  return `Напиши полный сценарий карусели.

${brief(s)}

Верни JSON с полями:
- title: короткое рабочее название карусели (до 8 слов), для папки с проектом, не обязательно совпадает с текстом первого слайда;
- slides: массив из РОВНО ${s.count} строк — тексты слайдов по порядку;
- caption: подпись к публикации.
${CAPTION_RULES.replace('Верни только текст подписи, без пояснений и заголовков.', '')}
- cta: один короткий призыв к действию (одно предложение), тот же, что звучит на последнем слайде и в подписи.${problem ? `\n\nПредыдущая попытка не подошла: ${problem} Исправь это.` : ''}`;
}

const SLIDE_ACTIONS = {
  regenerate: (n) => `Напиши слайд [${n}] заново: новая подача, другие формулировки, но та же роль в логике карусели. Он должен естественно продолжать предыдущий слайд и вести к следующему.`,
  shorter: (n) => `Сделай слайд [${n}] короче примерно на треть: убери лишнее, сохрани главную мысль, тон и связь с соседними слайдами.`,
  stronger: (n) => `Сделай слайд [${n}] сильнее: конкретнее, ярче, точнее, без пустых слов. Мысль и роль слайда сохрани, объём увеличь не больше чем на 10–15%.`,
};

function slidePrompt(body) {
  const { action, index, slides } = body;
  let task;
  if (action === 'add') {
    const after = index + 1; // номер слайда, после которого вставляем
    const next = slides[index + 1] !== undefined ? `, перед слайдом [${index + 2}]` : ' в самый конец карусели';
    task = `Нужно вставить НОВЫЙ слайд после слайда [${after}]${next}. Он раскрывает новую мысль, не повторяя соседние слайды, и естественно соединяет их по логике. Если он идёт после слайда с призывом к действию, сделай его логичным дополнением (напоминание, бонус, уточнение), не дублируя призыв.`;
  } else {
    task = SLIDE_ACTIONS[action](index + 1);
  }
  return `${carouselContext(body)}\n\nЗадача: ${task}\n\nВерни только новый текст этого слайда: без номера, без кавычек, без пояснений.`;
}

const CAPTION_ACTIONS = {
  generate: () => 'Напиши подпись к этой карусели.',
  regenerate: () => 'Напиши подпись к этой карусели заново: другое вступление и подача, не повторяй формулировки текущей.',
  shorter: () => 'Сократи текущую подпись примерно на 40%: сохрани цепляющее вступление, главную мысль и призыв к действию.',
  longer: () => 'Расширь текущую подпись примерно наполовину: добавь контекст и пользу, не пересказывай слайды. Объём не больше 1500 знаков.',
  tone: (tone) => `Перепиши текущую подпись в тоне «${tone}». Смысл и призыв к действию сохрани.`,
};

function captionPrompt(body) {
  const task = CAPTION_ACTIONS[body.action](body.tone);
  const current = body.caption && body.action !== 'generate' ? `\n\nТекущая подпись:\n${body.caption}` : '';
  return `${carouselContext(body)}${current}\n\nЗадача: ${task}\n\n${CAPTION_RULES}`;
}

/* ───────────────────────── Вызов Claude ───────────────────────── */

let client;
function getClient() {
  if (!process.env.ANTHROPIC_API_KEY && !process.env.ANTHROPIC_AUTH_TOKEN) {
    throw new AppError(503, 'ИИ пока не подключён: на сервере не задан ANTHROPIC_API_KEY. Твои настройки сохранены, как только ключ появится, нажми кнопку ещё раз.');
  }
  client ??= new Anthropic();
  return client;
}

async function askClaude({ user, effort = 'medium', maxTokens = 8000, schema }) {
  const params = {
    model: MODEL,
    max_tokens: maxTokens,
    system: SYSTEM,
    messages: [{ role: 'user', content: user }],
    output_config: { effort },
  };
  if (schema) params.output_config.format = { type: 'json_schema', schema };

  let res;
  try {
    res = await getClient().messages.create(params);
  } catch (err) {
    throw mapApiError(err);
  }

  if (res.stop_reason === 'refusal') {
    throw new AppError(422, 'ИИ отказался писать на эту тему. Попробуй переформулировать тему или выбрать другую.');
  }
  if (res.stop_reason === 'max_tokens') {
    throw new AppError(502, 'ИИ не успел дописать ответ. Нажми кнопку ещё раз или уменьши число слайдов.');
  }
  const text = res.content.filter((b) => b.type === 'text').map((b) => b.text).join('').trim();
  if (!text) throw new AppError(502, 'ИИ вернул пустой ответ. Попробуй ещё раз.');
  return text;
}

function mapApiError(err) {
  if (err instanceof AppError) return err;
  if (err instanceof Anthropic.AuthenticationError || err instanceof Anthropic.PermissionDeniedError) {
    console.error('Anthropic auth error:', err.message);
    return new AppError(502, 'Сервер не смог войти в сервис ИИ: проверь API-ключ в настройках сервера.');
  }
  if (err instanceof Anthropic.RateLimitError) {
    return new AppError(429, 'Сервис ИИ сейчас перегружен. Подожди минуту и нажми кнопку ещё раз.');
  }
  if (err instanceof Anthropic.NotFoundError) {
    console.error('Anthropic model error:', err.message);
    return new AppError(502, `Модель «${MODEL}» недоступна. Проверь CLAUDE_MODEL в настройках сервера.`);
  }
  if (err instanceof Anthropic.APIConnectionError) {
    return new AppError(502, 'Не получилось связаться с сервисом ИИ. Проверь интернет и попробуй ещё раз.');
  }
  console.error('Anthropic error:', err);
  return new AppError(502, 'Сервис ИИ ответил ошибкой. Попробуй ещё раз через минуту.');
}

/* ───────────────────────── Демо-режим (без ключа) ───────────────────────── */

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

async function mockCarousel(s) {
  await delay(1200);
  const slides = Array.from({ length: s.count }, (_, i) => {
    if (i === 0) return 'Демо-режим: так будет выглядеть сильный крючок';
    if (i === s.count - 1 && s.count > 1) return 'Призыв к действию появится здесь.\n\n[ДОБАВЬ: название продукта]';
    return `Мысль слайда ${i + 1}.\n\nКороткий абзац с одной идеей. [ДОБАВЬ: свой факт]`;
  });
  return { title: 'Демо-карусель', slides, caption: 'Это демо-подпись.\n\nНастоящий текст появится, когда подключится ИИ.', cta: 'Напиши «хочу» в комментариях' };
}

async function mockText(label) {
  await delay(700);
  return `${label} (демо-режим)`;
}

/* ───────────────────────── Валидация ───────────────────────── */

function str(v, field, { max = 800, required = false } = {}) {
  if (v === undefined || v === null || v === '') {
    if (required) throw new AppError(400, `Не заполнено поле «${field}».`);
    return '';
  }
  if (typeof v !== 'string') throw new AppError(400, `Некорректное поле «${field}».`);
  const t = v.trim();
  if (required && !t) throw new AppError(400, `Не заполнено поле «${field}».`);
  if (t.length > max) throw new AppError(400, `Поле «${field}» слишком длинное (максимум ${max} знаков).`);
  return t;
}

function parseSettings(raw) {
  if (!raw || typeof raw !== 'object') throw new AppError(400, 'Нет настроек карусели.');
  const count = Number(raw.count);
  if (!Number.isInteger(count) || count < 1 || count > 10) throw new AppError(400, 'Количество слайдов — от 1 до 10.');
  return {
    niche: str(raw.niche, 'Ниша', { required: true }),
    audience: str(raw.audience, 'Целевая аудитория', { required: true, max: 1200 }),
    goal: str(raw.goal, 'Основная цель', { required: true }),
    tone: str(raw.tone, 'Тон', { required: true }),
    tone2: str(raw.tone2, 'Дополнительный тон'),
    topic: str(raw.topic, 'Тема', { max: 1200 }),
    product: str(raw.product, 'Цифровой продукт', { max: 1200 }),
    count,
  };
}

function parseContext(body) {
  const settings = parseSettings(body.settings);
  const title = str(body.title, 'Название', { max: 200 });
  let slides = [];
  if (body.slides !== undefined) {
    if (!Array.isArray(body.slides) || body.slides.length > 30) throw new AppError(400, 'Некорректный список слайдов.');
    slides = body.slides.map((t) => str(t, 'Текст слайда', { max: 4000 }));
  }
  return { settings, title, slides };
}

/* ───────────────────────── Обработчики API ───────────────────────── */

async function handleGenerate(body) {
  const s = parseSettings(body.settings);
  if (MOCK) return mockCarousel(s);

  let problem = '';
  for (let attempt = 0; attempt < 2; attempt++) {
    const raw = await askClaude({ user: generationPrompt(s, problem), effort: 'medium', maxTokens: 16000, schema: CAROUSEL_SCHEMA });
    let data;
    try { data = JSON.parse(raw); } catch { problem = 'ответ не был корректным JSON.'; continue; }

    const slides = Array.isArray(data.slides) ? data.slides.map((t) => String(t ?? '').trim()) : [];
    if (slides.length !== s.count) { problem = `нужно ровно ${s.count} слайдов, а в массиве slides их ${slides.length}.`; continue; }
    if (slides.some((t) => !t)) { problem = 'один из слайдов пустой.'; continue; }
    return {
      title: String(data.title ?? '').trim() || 'Новая карусель',
      slides,
      caption: String(data.caption ?? '').trim(),
      cta: String(data.cta ?? '').trim(),
    };
  }
  throw new AppError(502, `ИИ не смог составить карусель ровно из ${s.count} слайдов. Нажми кнопку ещё раз.`);
}

async function handleSlide(body) {
  const ctx = parseContext(body);
  const index = Number(body.index);
  const action = body.action;
  if (!Number.isInteger(index) || index < 0) throw new AppError(400, 'Некорректный номер слайда.');
  if (action === 'add') {
    if (index > ctx.slides.length - 1) throw new AppError(400, 'Некорректный номер слайда.');
  } else {
    if (!SLIDE_ACTIONS[action]) throw new AppError(400, 'Неизвестное действие.');
    if (index >= ctx.slides.length) throw new AppError(400, 'Некорректный номер слайда.');
  }
  if (MOCK) return { text: await mockText(`Слайд (${action})`) };
  const text = await askClaude({
    user: slidePrompt({ ...ctx, action, index }),
    effort: 'low',
    maxTokens: 6000,
  });
  return { text: text.replace(/^\[\d+\]\s*/, '') };
}

async function handleCaption(body) {
  const ctx = parseContext(body);
  const action = body.action;
  if (!CAPTION_ACTIONS[action]) throw new AppError(400, 'Неизвестное действие.');
  const caption = str(body.caption, 'Подпись', { max: 4000 });
  const tone = str(body.tone, 'Тон');
  if (action === 'tone' && !tone) throw new AppError(400, 'Не выбран тон.');
  if (['shorter', 'longer', 'tone'].includes(action) && !caption) throw new AppError(400, 'Сначала нужна подпись.');
  if (MOCK) return { caption: await mockText(`Подпись (${action})`) };
  const text = await askClaude({
    user: captionPrompt({ ...ctx, action, caption, tone }),
    effort: 'low',
    maxTokens: 6000,
  });
  return { caption: text };
}

const ROUTES = {
  '/api/generate': handleGenerate,
  '/api/slide': handleSlide,
  '/api/caption': handleCaption,
};

/* ───────────────────────── HTTP ───────────────────────── */

const hits = new Map();
function rateLimited(ip) {
  const now = Date.now();
  const recent = (hits.get(ip) ?? []).filter((t) => now - t < 10 * 60_000);
  recent.push(now);
  hits.set(ip, recent);
  return recent.length > RATE_LIMIT;
}
setInterval(() => {
  const now = Date.now();
  for (const [ip, list] of hits) if (list.every((t) => now - t >= 10 * 60_000)) hits.delete(ip);
}, 60_000).unref();

function clientIp(req) {
  if (TRUST_PROXY) {
    const fwd = req.headers['x-forwarded-for'];
    if (typeof fwd === 'string' && fwd) return fwd.split(',')[0].trim();
  }
  return req.socket.remoteAddress ?? 'unknown';
}

function readJson(req, limit = 200_000) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (c) => {
      size += c.length;
      if (size > limit) { reject(new AppError(413, 'Слишком большой запрос.')); req.destroy(); return; }
      chunks.push(c);
    });
    req.on('end', () => {
      try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}')); }
      catch { reject(new AppError(400, 'Некорректный запрос.')); }
    });
    req.on('error', reject);
  });
}

function sendJson(res, status, data) {
  const body = JSON.stringify(data);
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(body);
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.ico': 'image/x-icon',
  '.json': 'application/json; charset=utf-8',
};

async function serveStatic(req, res, pathname) {
  let rel = decodeURIComponent(pathname);
  if (rel === '/') rel = '/index.html';
  const file = path.normalize(path.join(PUBLIC_DIR, rel));
  if (file !== PUBLIC_DIR && !file.startsWith(PUBLIC_DIR + path.sep)) {
    res.writeHead(403).end('Forbidden');
    return;
  }
  try {
    const data = await readFile(file);
    res.writeHead(200, {
      'Content-Type': MIME[path.extname(file)] ?? 'application/octet-stream',
      'Cache-Control': 'no-cache',
      'X-Content-Type-Options': 'nosniff',
    });
    res.end(req.method === 'HEAD' ? undefined : data);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Не найдено');
  }
}

const server = http.createServer(async (req, res) => {
  try {
    const { pathname } = new URL(req.url, 'http://localhost');

    if (pathname === '/api/health' && req.method === 'GET') {
      return sendJson(res, 200, { ok: true, mock: MOCK, configured: MOCK || Boolean(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN) });
    }

    const handler = ROUTES[pathname];
    if (handler) {
      if (req.method !== 'POST') throw new AppError(405, 'Метод не поддерживается.');
      if (rateLimited(clientIp(req))) throw new AppError(429, 'Слишком много запросов. Подожди несколько минут.');
      const body = await readJson(req);
      return sendJson(res, 200, await handler(body));
    }

    if (req.method !== 'GET' && req.method !== 'HEAD') throw new AppError(405, 'Метод не поддерживается.');
    await serveStatic(req, res, pathname);
  } catch (err) {
    const e = err instanceof AppError ? err : new AppError(500, 'Что-то пошло не так на сервере. Попробуй ещё раз.');
    if (!(err instanceof AppError)) console.error(err);
    if (!res.headersSent) sendJson(res, e.status, { error: e.message });
  }
});

server.listen(PORT, () => {
  console.log(`Создатель сценариев каруселей: http://localhost:${PORT}`);
  console.log(MOCK ? 'Режим: ДЕМО (без ИИ)' : `Модель: ${MODEL}`);
});
