// Создатель сценариев каруселей — сервер.
// Отдаёт статику из ./public и проксирует запросы к Claude, чтобы API-ключ не попадал в браузер.

import http from 'node:http';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import Anthropic from '@anthropic-ai/sdk';
import * as core from './shared/core.js';
import { AppError, SYSTEM, parseSettings } from './shared/core.js';

try { process.loadEnvFile(); } catch { /* .env необязателен */ }

const here = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC_DIR = path.join(here, 'public');
const PORT = Number(process.env.PORT) || 3000;
const MODEL = process.env.CLAUDE_MODEL || 'claude-opus-5-5';
const MOCK = process.env.MOCK_AI === '1';
const RATE_LIMIT = Number(process.env.RATE_LIMIT_PER_10MIN) || 60;
const TRUST_PROXY = process.env.TRUST_PROXY === '1';

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

/* ───────────────────────── Обработчики API ───────────────────────── */

const mockAsk = () => mockText('Текст');

const handleGenerate = (body) => (MOCK ? mockCarousel(parseSettings(body.settings)) : core.generate(body, askClaude));
const handleSlide = (body) => core.slide(body, MOCK ? mockAsk : askClaude);
const handleCaption = (body) => core.caption(body, MOCK ? mockAsk : askClaude);

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
