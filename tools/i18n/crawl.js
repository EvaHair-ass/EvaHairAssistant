// Обход приложения на выбранном языке: собирает русский текст, который остался непереведённым.
// Запуск: NODE_PATH=$(npm root -g) node tools/i18n/crawl.js tr [out.json]
const { chromium } = require('playwright');
const lang = process.argv[2] || 'tr', outFile = process.argv[3];
const URL = 'file:///home/user/EvaHairAssistant/prototype/index.html';
const CYR = /[А-Яа-яЁё]/;
const collect = () => {
  const out = [];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const n = w.currentNode, p = n.parentNode; if (!p || ['SCRIPT', 'STYLE', 'TEXTAREA'].includes(p.tagName)) continue; const v = n.nodeValue.trim(); if (/[А-Яа-яЁё]/.test(v)) out.push(v); }
  document.querySelectorAll('[placeholder],[aria-label],[title],[alt]').forEach(e => ['placeholder', 'aria-label', 'title', 'alt'].forEach(a => { const v = e.getAttribute(a); if (v && /[А-Яа-яЁё]/.test(v)) out.push('@' + a + ': ' + v); }));
  return out;
};
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
  await ctx.addInitScript(l => { window.__PWA__ = true; try { localStorage.setItem('mm-app-lang', l); } catch (e) {} }, lang);
  const seen = new Map(); // текст -> где
  const rec = (arr, where) => arr.forEach(t => { if (!seen.has(t)) seen.set(t, where); });
  let pg = await ctx.newPage();
  const errs = []; pg.on('pageerror', e => errs.push(e.message));
  await pg.goto(URL); await pg.waitForTimeout(1500);
  await pg.click('[data-t=more]'); await pg.waitForTimeout(300);
  rec(await pg.evaluate(collect), 'more');
  if (!process.env.EMPTY) { await pg.click('[data-act=resetOpen]'); await pg.waitForTimeout(300); rec(await pg.evaluate(collect), 'confirm-demo');
  await pg.click('[data-act=confirmOk]'); await pg.waitForTimeout(4000); }
  await pg.close();
  const screens = [['stock', '[data-t=stock]'], ['buy', '[data-t=buy]'], ['work', '[data-t=work]'], ['arch', '[data-t=arch]'], ['more', '[data-t=more]'], ['acad', null]];
  for (const [name, sel] of screens) {
    pg = await ctx.newPage(); pg.on('pageerror', e => errs.push(name + ': ' + e.message));
    await pg.goto(URL); await pg.waitForTimeout(1500);
    if (name === 'acad') await pg.click('[data-act=mode][data-v=acad]'); else await pg.click(sel);
    await pg.waitForTimeout(700); rec(await pg.evaluate(collect), name);
    const subs = name === 'arch' ? ['runs', 'fin', 'sold', 'stats'] : [];
    const acts = await pg.evaluate(() => [...new Set([...document.querySelectorAll('[data-act]')].map(e => e.dataset.act))]);
    await pg.close();
    const skipAct = /^(setLang|confirmOk|wipeGo|logout|gateGo|catDelGo|saleCancelGo|delGo|impGo|resetOpen|wipeOpen)$/;
    for (const act of acts.filter(a => !skipAct.test(a))) {
      const p2 = await ctx.newPage(); p2.on('pageerror', e => errs.push(name + '/' + act + ': ' + e.message));
      try {
        await p2.goto(URL); await p2.waitForTimeout(1200);
        if (name === 'acad') await p2.click('[data-act=mode][data-v=acad]'); else await p2.click(sel);
        await p2.waitForTimeout(400);
        const el = p2.locator('[data-act="' + act + '"]').first();
        await el.click({ timeout: 2500 }); await p2.waitForTimeout(700);
        rec(await p2.evaluate(collect), name + ' > ' + act);
        // второй уровень: действия, появившиеся в открытом окне/странице
        const acts2 = await p2.evaluate(() => [...new Set([...document.querySelectorAll('.sheet [data-act], .page [data-act], #pages [data-act], #sheets [data-act]')].map(e => e.dataset.act))]);
        for (const a2 of acts2.filter(a => !skipAct.test(a) && a !== act).slice(0, 14)) {
          const p3 = await ctx.newPage();
          try {
            await p3.goto(URL); await p3.waitForTimeout(1000);
            if (name === 'acad') await p3.click('[data-act=mode][data-v=acad]'); else await p3.click(sel);
            await p3.waitForTimeout(300);
            await p3.locator('[data-act="' + act + '"]').first().click({ timeout: 2000 }); await p3.waitForTimeout(500);
            await p3.locator('.sheet [data-act="' + a2 + '"], .page [data-act="' + a2 + '"], #pages [data-act="' + a2 + '"], #sheets [data-act="' + a2 + '"]').first().click({ timeout: 2000 }); await p3.waitForTimeout(600);
            rec(await p3.evaluate(collect), name + ' > ' + act + ' > ' + a2);
          } catch (e) {} finally { await p3.close(); }
        }
      } catch (e) {} finally { await p2.close(); }
    }
  }
  // вход в аккаунт (экран gate) покажем отдельно, если он есть в DOM
  const res = [...seen.entries()];
  console.log('осталось непереведённого:', res.length, ' ошибок JS:', errs.length, errs.slice(0, 3));
  if (outFile) require('fs').writeFileSync(outFile, JSON.stringify(res, null, 1));
  else res.slice(0, 80).forEach(([t, w]) => console.log(' ', JSON.stringify(t), '←', w));
  await b.close();
})();
