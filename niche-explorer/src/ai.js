import { REPORT_SCHEMA, normalizeReport } from './report.js';
import { SYSTEM_PROMPT, userPrompt } from './prompt.js';

const TOOL = {
  name: 'submit_niche_report',
  description: 'Отправляет готовый отчёт об исследовании ниши',
  input_schema: REPORT_SCHEMA,
};

export class AiError extends Error {
  constructor(message, status = 502) {
    super(message);
    this.status = status;
  }
}

export async function analyzeNiche(niche, { apiKey, baseUrl, model }) {
  if (!apiKey) throw new AiError('На сервере не задан ANTHROPIC_API_KEY', 500);

  let res;
  try {
    res = await fetch(`${baseUrl}/v1/messages`, {
      method: 'POST',
      headers: { 'content-type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
      body: JSON.stringify({
        model,
        max_tokens: 8000,
        system: SYSTEM_PROMPT,
        tools: [TOOL],
        tool_choice: { type: 'tool', name: TOOL.name },
        messages: [{ role: 'user', content: userPrompt(niche) }],
      }),
      signal: AbortSignal.timeout(180_000),
    });
  } catch {
    throw new AiError('Не удалось связаться с ИИ. Попробуй ещё раз через минуту.');
  }

  if (!res.ok) {
    console.error('Anthropic API error', res.status, await res.text().catch(() => ''));
    throw new AiError(
      res.status === 429 || res.status === 529
        ? 'ИИ сейчас перегружен. Попробуй ещё раз через минуту.'
        : 'ИИ вернул ошибку. Попробуй ещё раз.',
    );
  }

  const data = await res.json();
  const block = data.content?.find((b) => b.type === 'tool_use' && b.name === TOOL.name);
  if (!block || data.stop_reason === 'max_tokens') throw new AiError('ИИ не успел дописать отчёт. Попробуй ещё раз.');

  try {
    return normalizeReport(block.input);
  } catch (e) {
    console.error('Bad report from model:', e.message);
    throw new AiError('ИИ вернул неполный отчёт. Попробуй ещё раз.');
  }
}
