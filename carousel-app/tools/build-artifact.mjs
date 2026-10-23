// Собирает автономную версию приложения в один HTML-файл (dist/artifact.html).
// Вместо сервера с API-ключом она просит текст у Claude через возможность «sample» страниц-артефактов
// и работает на аккаунте того, кто открыл страницу.
//
//   node tools/build-artifact.mjs

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), '..');
const read = (p) => readFile(path.join(root, p), 'utf8');

const [indexHtml, css, appJs, coreSrc] = await Promise.all([
  read('public/index.html'), read('public/styles.css'), read('public/app.js'), read('shared/core.js'),
]);

// Общая логика: убираем `export`, заворачиваем в функцию и отдаём то, что нужно переходнику.
const core = coreSrc.replace(/^export /gm, '');
const coreBlock = `const Core = (() => {\n${core}\nreturn { AppError, SYSTEM, generate, slide, caption };\n})();`;

const adapter = `
// ── Переходник: запросы приложения → «Спросить Claude» ──
const ERRORS = {
  not_granted: 'Страница не получила разрешение использовать Claude. Обнови страницу и нажми «Разрешить» в окне запроса.',
  sampling_disabled: 'Claude недоступен для этого аккаунта.',
  rate_limited: 'Слишком много запросов подряд или закончился лимит. Подожди немного и нажми кнопку ещё раз.',
  session_expired: 'Нужно заново войти в аккаунт Claude, потом нажми кнопку ещё раз.',
  refused: 'ИИ отказался писать на эту тему. Попробуй переформулировать тему или выбрать другую.',
  empty_completion: 'ИИ вернул пустой ответ. Нажми кнопку ещё раз.',
  invalid_json: 'ИИ ответил в неожиданном формате. Нажми кнопку ещё раз.',
  prompt_too_large: 'Слишком много текста. Удали часть слайдов и попробуй ещё раз.',
};
const sampleError = (e) => new Error(ERRORS[e?.code] || 'Не получилось связаться с ИИ. Нажми кнопку ещё раз через минуту.');

async function ask({ user, schema }) {
  const sample = await window.claude?.use?.('sample');
  if (!sample) throw new Error('ИИ доступен только внутри Claude: открой страницу по ссылке в приложении или на claude.ai.');
  const input = Core.SYSTEM + '\\n\\n---\\n\\n' + user;
  try {
    if (schema) return JSON.stringify(await sample.json(input, { cache: false }));
    const { text, truncated } = await sample(input, { cache: false });
    if (truncated) throw new Error('ИИ не успел дописать ответ. Нажми кнопку ещё раз.');
    return text.trim();
  } catch (e) {
    throw e instanceof Error ? e : sampleError(e);
  }
}

const HANDLERS = { '/api/generate': Core.generate, '/api/slide': Core.slide, '/api/caption': Core.caption };
window.CAROUSEL_API = async (path, body) => HANDLERS[path](body, ask);
window.CAROUSEL_HEALTH = async () => {
  const sample = await window.claude?.use?.('sample');
  return sample
    ? { configured: true }
    : { configured: false, hint: 'Эта страница создаёт тексты через Claude и работает только в окне Claude. Открой её по ссылке в приложении или на claude.ai.' };
};
`;

const fonts = indexHtml.match(/<link href="https:\/\/fonts\.googleapis\.com[^>]*>/)[0];
const markup = indexHtml.slice(indexHtml.indexOf('<header'), indexHtml.indexOf('<script src='));

if (/<\/script/i.test(appJs + coreBlock + adapter)) throw new Error('В скрипте найден </script>: его нельзя встроить в страницу.');

const html = `<title>Сценарии каруселей</title>
<meta name="claude:viewport-fit-sides" content="cover">
${fonts}
<style>
${css}
</style>
${markup.trim()}
<script>
${coreBlock}
${adapter}
${appJs}
</script>
`;

await mkdir(path.join(root, 'dist'), { recursive: true });
const out = path.join(root, 'dist/artifact.html');
await writeFile(out, html);
console.log(`Готово: ${out} (${Math.round(html.length / 1024)} КБ)`);
