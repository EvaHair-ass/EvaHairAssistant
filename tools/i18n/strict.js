// Строгая проверка: каждый русский фрагмент исходника переводится движком (или входит в шаблон с подстановками).
const { chromium } = require('playwright');
const fs = require('fs');
const lang = process.argv[2] || 'tr';
const { frags, pats } = JSON.parse(fs.readFileSync('/tmp/work/frags.json', 'utf-8'));
const SKIP = new Set(['Русский','лв','дин','с','янв','фев','мар','апр','мая','июн','июл','авг','сен','окт','ноя','дек','Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь','закупок','позиций','уроков','участниц','участница','участницы','человек','человека','материалов по рецепту','Проверка по ТЗ','Что попробовать','Эти сценарии из раздела 6 считаются прямо сейчас на отдельном пустом складе']);
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext();
  await ctx.addInitScript(l => { window.__PWA__ = true; localStorage.setItem('mm-app-lang', l); }, lang);
  const pg = await ctx.newPage();
  await pg.goto('file:///home/user/EvaHairAssistant/prototype/index.html'); await pg.waitForTimeout(1500);
  const bad = await pg.evaluate(fr => fr.filter(f => { const t = window.__I18N_TEST.tr(f); return /[А-Яа-яЁё]/.test(t); }), frags);
  // фрагмент допустим, если он входит в ключ-шаблон (там он переводится вместе с подстановками)
  const rest = bad.filter(f => !SKIP.has(f) && !pats.some(p => p.includes(f.replace(/[.!…]+$/, ''))) && !/^[\d,. ]*(мм|см|г|шт|м|мл)\b/.test(f));
  console.log(lang, 'движок включён:', await pg.evaluate(() => window.__I18N_TEST.on()), '| фрагментов:', frags.length, '| без перевода:', rest.length);
  rest.forEach(f => console.log('  ', JSON.stringify(f.slice(0, 160))));
  await b.close();
})();
