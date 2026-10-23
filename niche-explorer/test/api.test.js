import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { randomUUID } from 'node:crypto';
import { createApp } from '../server.js';
import { sampleInput } from './fixture.js';

let fakeAi, app, base, dataDir, aiCalls, aiReply;

const listen = (server) => new Promise((r) => server.listen(0, '127.0.0.1', () => r(`http://127.0.0.1:${server.address().port}`)));

before(async () => {
  aiCalls = [];
  aiReply = (niche) => ({ stop_reason: 'tool_use', content: [{ type: 'tool_use', name: 'submit_niche_report', input: sampleInput(niche) }] });
  fakeAi = createServer(async (req, res) => {
    let body = '';
    for await (const c of req) body += c;
    const parsed = JSON.parse(body);
    aiCalls.push({ headers: req.headers, body: parsed });
    const niche = /«(.+)»/.exec(parsed.messages[0].content)[1];
    const reply = aiReply(niche);
    res.writeHead(reply.status ?? 200, { 'content-type': 'application/json' });
    res.end(JSON.stringify(reply.json ?? reply));
  });
  const aiUrl = await listen(fakeAi);
  dataDir = mkdtempSync(join(tmpdir(), 'niches-'));
  app = createApp({ apiKey: 'test-key', baseUrl: aiUrl, model: 'test-model', dataDir, analysesPerHour: 3 });
  base = await listen(app);
});

after(() => {
  app.close();
  fakeAi.close();
  rmSync(dataDir, { recursive: true, force: true });
});

const call = (path, { client = randomUUID(), method = 'GET', body } = {}) =>
  fetch(base + path, {
    method,
    headers: { 'x-client-id': client, ...(body && { 'content-type': 'application/json' }) },
    body: body && JSON.stringify(body),
  });

test('отдаёт главную страницу', async () => {
  const res = await fetch(base + '/');
  assert.equal(res.status, 200);
  assert.match(await res.text(), /Прибыльные ниши/);
});

test('не отдаёт файлы за пределами public', async () => {
  const res = await fetch(base + '/..%2fserver.js');
  assert.equal(res.status, 404);
});

test('API требует идентификатор устройства', async () => {
  const res = await fetch(base + '/api/reports');
  assert.equal(res.status, 401);
});

test('анализ: запрос к ИИ и нормализованный отчёт', async () => {
  aiCalls.length = 0;
  const res = await call('/api/analyze', { method: 'POST', body: { niche: '  Дрессировка   собак ' } });
  assert.equal(res.status, 200);
  const { report } = await res.json();
  assert.equal(report.niche, 'Дрессировка собак');
  assert.equal(report.content.length, 5);
  assert.equal(aiCalls[0].headers['x-api-key'], 'test-key');
  assert.equal(aiCalls[0].body.model, 'test-model');
  assert.deepEqual(aiCalls[0].body.tool_choice, { type: 'tool', name: 'submit_niche_report' });
});

test('анализ: пустая и слишком длинная ниша', async () => {
  for (const niche of ['', ' a ', 'x'.repeat(101)]) {
    const res = await call('/api/analyze', { method: 'POST', body: { niche } });
    assert.equal(res.status, 400, `niche=${JSON.stringify(niche.slice(0, 5))}`);
  }
});

test('анализ: неполный ответ ИИ превращается в понятную ошибку', async () => {
  const prev = aiReply;
  aiReply = () => ({ stop_reason: 'tool_use', content: [{ type: 'tool_use', name: 'submit_niche_report', input: { niche: 'X', problems: [] } }] });
  const res = await call('/api/analyze', { method: 'POST', body: { niche: 'Фитнес' } });
  aiReply = prev;
  assert.equal(res.status, 502);
  assert.match((await res.json()).error, /неполный/);
});

test('анализ: ошибка API ИИ', async () => {
  const prev = aiReply;
  aiReply = () => ({ status: 529, json: { error: 'overloaded' } });
  const res = await call('/api/analyze', { method: 'POST', body: { niche: 'Фитнес' } });
  aiReply = prev;
  assert.equal(res.status, 502);
  assert.match((await res.json()).error, /перегружен/);
});

test('анализ: лимит запросов в час', async () => {
  const client = randomUUID();
  for (let i = 0; i < 3; i++) assert.equal((await call('/api/analyze', { client, method: 'POST', body: { niche: 'ИИ' } })).status, 200);
  assert.equal((await call('/api/analyze', { client, method: 'POST', body: { niche: 'ИИ' } })).status, 429);
});

test('сохранение: сохранить → список → открыть → удалить', async () => {
  const client = randomUUID();
  const report = (await (await call('/api/analyze', { client, method: 'POST', body: { niche: 'Фитнес' } })).json()).report;

  const saved = await call('/api/reports', { client, method: 'POST', body: { report } });
  assert.equal(saved.status, 201);
  const { id } = (await saved.json()).saved;

  const { reports } = await (await call('/api/reports', { client })).json();
  assert.equal(reports.length, 1);
  assert.equal(reports[0].niche, 'Фитнес');
  assert.ok(!Number.isNaN(Date.parse(reports[0].createdAt)));

  const opened = await (await call(`/api/reports/${id}`, { client })).json();
  assert.deepEqual(opened.report, report); // ровно то, что было сгенерировано

  assert.equal((await call(`/api/reports/${id}`, { client, method: 'DELETE' })).status, 200);
  assert.equal((await call(`/api/reports/${id}`, { client })).status, 404);
  assert.equal((await (await call('/api/reports', { client })).json()).reports.length, 0);
});

test('сохранение: чужие исследования недоступны', async () => {
  const alice = randomUUID();
  const bob = randomUUID();
  const { report } = await (await call('/api/analyze', { client: alice, method: 'POST', body: { niche: 'Мужская мода' } })).json();
  const { saved } = await (await call('/api/reports', { client: alice, method: 'POST', body: { report } })).json();

  assert.equal((await call(`/api/reports/${saved.id}`, { client: bob })).status, 404);
  assert.equal((await call(`/api/reports/${saved.id}`, { client: bob, method: 'DELETE' })).status, 404);
  assert.equal((await (await call('/api/reports', { client: bob })).json()).reports.length, 0);
  assert.equal((await call(`/api/reports/${saved.id}`, { client: alice })).status, 200);
});

test('сохранение: мусор вместо отчёта отклоняется', async () => {
  const res = await call('/api/reports', { method: 'POST', body: { report: { niche: 'X' } } });
  assert.equal(res.status, 400);
});
