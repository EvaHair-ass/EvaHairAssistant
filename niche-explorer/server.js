import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { extname, join, normalize } from 'node:path';
import { openDb } from './src/db.js';
import { analyzeNiche, AiError } from './src/ai.js';
import { normalizeReport } from './src/report.js';

const PUBLIC_DIR = join(fileURLToPath(new URL('.', import.meta.url)), 'public');
const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
};
const CLIENT_ID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const MAX_BODY = 200_000;

class HttpError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

export function createApp({
  apiKey = process.env.ANTHROPIC_API_KEY,
  baseUrl = process.env.ANTHROPIC_BASE_URL || 'https://api.anthropic.com',
  model = process.env.ANTHROPIC_MODEL || 'claude-sonnet-5-5',
  dataDir = process.env.DATA_DIR || './data',
  analysesPerHour = Number(process.env.ANALYSES_PER_HOUR) || 10,
} = {}) {
  const db = openDb(dataDir);
  const usage = new Map(); // clientId -> метки времени запросов за последний час

  // Защита от случайного расхода денег на API: лимит анализов в час на одно устройство.
  function checkRateLimit(clientId) {
    const now = Date.now();
    const recent = (usage.get(clientId) ?? []).filter((t) => now - t < 3_600_000);
    if (recent.length >= analysesPerHour) {
      throw new HttpError(429, 'Слишком много анализов за час. Загляни в «Сохраненное исследование» или попробуй позже.');
    }
    recent.push(now);
    usage.set(clientId, recent);
  }

  async function readJson(req) {
    let size = 0;
    const chunks = [];
    for await (const chunk of req) {
      size += chunk.length;
      if (size > MAX_BODY) throw new HttpError(413, 'Слишком большой запрос');
      chunks.push(chunk);
    }
    try {
      return JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}');
    } catch {
      throw new HttpError(400, 'Некорректный запрос');
    }
  }

  const send = (res, status, body) => {
    res.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' });
    res.end(JSON.stringify(body));
  };

  async function api(req, res, path) {
    const clientId = req.headers['x-client-id'];
    if (typeof clientId !== 'string' || !CLIENT_ID.test(clientId)) throw new HttpError(401, 'Нет идентификатора устройства');

    if (req.method === 'POST' && path === '/api/analyze') {
      const niche = String((await readJson(req)).niche ?? '').trim().replace(/\s+/g, ' ');
      if (niche.length < 2 || niche.length > 100) throw new HttpError(400, 'Введи нишу: от 2 до 100 символов');
      checkRateLimit(clientId);
      return send(res, 200, { report: await analyzeNiche(niche, { apiKey, baseUrl, model }) });
    }

    if (path === '/api/reports') {
      if (req.method === 'GET') return send(res, 200, { reports: db.list(clientId) });
      if (req.method === 'POST') {
        let report;
        try {
          report = normalizeReport((await readJson(req)).report);
        } catch (e) {
          if (e instanceof HttpError) throw e;
          throw new HttpError(400, 'Отчёт не удалось сохранить: он неполный');
        }
        return send(res, 201, { saved: db.save(clientId, report) });
      }
    }

    const m = path.match(/^\/api\/reports\/([0-9a-f-]{36})$/);
    if (m) {
      if (req.method === 'GET') {
        const found = db.get(clientId, m[1]);
        if (!found) throw new HttpError(404, 'Исследование не найдено');
        return send(res, 200, found);
      }
      if (req.method === 'DELETE') {
        if (!db.delete(clientId, m[1])) throw new HttpError(404, 'Исследование не найдено');
        return send(res, 200, { ok: true });
      }
    }
    throw new HttpError(404, 'Не найдено');
  }

  async function serveStatic(res, path) {
    const rel = path === '/' ? 'index.html' : normalize(path).replace(/^([/\\])+/, '');
    if (rel.startsWith('..') || !MIME[extname(rel)]) throw new HttpError(404, 'Не найдено');
    try {
      const body = await readFile(join(PUBLIC_DIR, rel));
      res.writeHead(200, { 'content-type': MIME[extname(rel)], 'cache-control': 'no-cache' });
      res.end(body);
    } catch {
      throw new HttpError(404, 'Не найдено');
    }
  }

  const server = createServer(async (req, res) => {
    const path = new URL(req.url, 'http://localhost').pathname;
    try {
      if (path.startsWith('/api/')) await api(req, res, path);
      else if (req.method === 'GET') await serveStatic(res, path);
      else throw new HttpError(404, 'Не найдено');
    } catch (e) {
      const status = e instanceof HttpError || e instanceof AiError ? e.status : 500;
      if (status === 500 && !(e instanceof AiError)) console.error(e);
      send(res, status, { error: status === 500 && !(e instanceof AiError) ? 'Что-то пошло не так' : e.message });
    }
  });
  server.on('close', () => db.close());
  return server;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  if (!process.env.ANTHROPIC_API_KEY) console.warn('⚠️  ANTHROPIC_API_KEY не задан — анализ ниш работать не будет.');
  const port = Number(process.env.PORT) || 3000;
  createApp().listen(port, () => console.log(`Прибыльные ниши: http://localhost:${port}`));
}
