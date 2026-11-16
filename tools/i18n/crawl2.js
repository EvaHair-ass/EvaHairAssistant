// Сценарные проверки состояний, которые обход crawl.js не достаёт. node tools/i18n/crawl2.js tr
const { chromium } = require('playwright');
const lang = process.argv[2] || 'tr';
const URL = 'file:///home/user/EvaHairAssistant/prototype/index.html';
const collect = () => {
  const out = [];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (w.nextNode()) { const n = w.currentNode, p = n.parentNode; if (!p || ['SCRIPT', 'STYLE', 'TEXTAREA'].includes(p.tagName)) continue; const v = n.nodeValue.trim(); if (/[А-Яа-яЁё]/.test(v)) out.push(v); }
  document.querySelectorAll('[placeholder],[aria-label],[title],[alt]').forEach(e => ['placeholder', 'aria-label', 'title', 'alt'].forEach(a => { const v = e.getAttribute(a); if (v && /[А-Яа-яЁё]/.test(v)) out.push('@' + a + ': ' + v); }));
  return out;
};
const SC = {
  'stats-month': ['[data-t=arch]', '[data-act=archSeg][data-v=stats]'],
  'stats-year': ['[data-t=arch]', '[data-act=archSeg][data-v=stats]', '[data-act=statMode][data-v=year]'],
  'arch-fin': ['[data-t=arch]', '[data-act=archSeg][data-v=fin]'],
  'arch-sold': ['[data-t=arch]', '[data-act=archSeg][data-v=stats]'],
  'sale-sheet': ['[data-t=arch]', '[data-act=archSeg][data-v=fin]', '[data-act=saleOpen]'],
  'sold-sheet': ['[data-t=arch]', '[data-act=archSeg][data-v=stats]', '[data-act=saleOpen]'],
  'run-open': ['[data-t=arch]', '[data-act=archSeg][data-v=runs]', '[data-act=openRun]'],
  'newwork': ['[data-t=work]', '[data-act=newWork]'],
  'draft-finish': ['[data-t=work]', '[data-act=openDraft]', '[data-act=toFinish]'],
  'cat-mgr': ['[data-t=stock]', '[data-act=catMgr]'],
  'new-purchase': ['[data-t=buy]', '[data-act=newPurchase]'],
  'cur-base': ['[data-t=more]', '[data-act=curBase]'],
  'exp': ['[data-t=more]', '[data-act=expOpen]'],
  'imp': ['[data-t=more]', '[data-act=impOpen]'],
  'wipe': ['[data-t=more]', '[data-act=wipeOpen]'],
  'ac-students': ['[data-act=mode][data-v=acad]', '[data-act=tab][data-t=students]'],
  'ac-chats': ['[data-act=mode][data-v=acad]', '[data-act=tab][data-t=chat]'],
  'ac-newcourse': ['[data-act=mode][data-v=acad]', '[data-act=newCourse]'],
  'ac-course': ['[data-act=mode][data-v=acad]', '[data-act=openCourse]'],
  'ac-lesson': ['[data-act=mode][data-v=acad]', '[data-act=openCourse]', '[data-act=openLesson]'],
  'ac-addlesson': ['[data-act=mode][data-v=acad]', '[data-act=openCourse]', '[data-act=addLesson]'],
  'ac-student': ['[data-act=mode][data-v=acad]', '[data-act=tab][data-t=students]', '[data-act=openStudent]'],
  'ac-chat': ['[data-act=mode][data-v=acad]', '[data-act=tab][data-t=chat]', '[data-act=openChat]'],
};
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 } });
  await ctx.addInitScript(l => { window.__PWA__ = true; try { localStorage.setItem('mm-app-lang', l); } catch (e) {} }, lang);
  let pg = await ctx.newPage();
  await pg.goto(URL); await pg.waitForTimeout(1200);
  await pg.click('[data-t=more]'); await pg.click('[data-act=resetOpen]'); await pg.click('[data-act=confirmOk]'); await pg.waitForTimeout(4000); await pg.close();
  const seen = new Map(), failed = [];
  for (const [name, steps] of Object.entries(SC)) {
    const p = await ctx.newPage();
    try {
      await p.goto(URL); await p.waitForTimeout(1000);
      for (const st of steps) { await p.locator(st).first().click({ timeout: 2500 }); await p.waitForTimeout(450); }
      for (const t of await p.evaluate(collect)) if (!seen.has(t)) seen.set(t, name);
    } catch (e) { failed.push(name); } finally { await p.close(); }
  }
  console.log('не удалось пройти сценарии:', failed.join(', '));
  console.log('осталось:', seen.size); for (const [t, w] of seen) console.log(' ', JSON.stringify(t), '←', w);
  await b.close();
})();
