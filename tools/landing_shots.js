// Снимает экраны приложения для сайта на выбранном языке: NODE_PATH=$(npm root -g) node tools/landing_shots.js tr /путь/куда
const { chromium } = require('playwright');
const lang = process.argv[2], out = process.argv[3];
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
  await ctx.addInitScript(l => { window.__PWA__ = true; try { localStorage.setItem('mm-app-lang', l); } catch (e) {} }, lang);
  const pg = await ctx.newPage();
  await pg.goto('file:///home/user/EvaHairAssistant/prototype/index.html'); await pg.waitForTimeout(1500);
  await pg.click('[data-t=more]'); await pg.click('[data-act=resetOpen]'); await pg.click('[data-act=confirmOk]'); await pg.waitForTimeout(4000);
  const shot = async n => { await pg.waitForTimeout(800); await pg.screenshot({ path: `${out}/${n}.png` }); };
  await pg.click('[data-t=stock]'); await shot('stock');
  await pg.click('[data-t=work]'); await pg.waitForTimeout(500);
  await pg.locator('[data-act=openDraft]').first().click(); await pg.waitForTimeout(900);
  await pg.evaluate(() => { const x = document.querySelector('.pricebox'); if (x) x.scrollIntoView({ block: 'center' }); }); await shot('price');
  await pg.click('[data-act=back]'); await pg.click('[data-t=arch]'); await pg.click('[data-act=archSeg][data-v=stats]'); await pg.waitForTimeout(1500); await shot('stats');
  await pg.click('[data-act=archSeg][data-v=runs]'); await pg.waitForTimeout(500);
  await pg.locator('[data-act=openRun]').filter({ hasText: /Лабрадор|Labradorit/i }).first().click(); await pg.waitForTimeout(1200); await shot('archive');
  await pg.click('[data-act=back]').catch(() => {});
  await pg.click('[data-act=mode][data-v=acad]'); await pg.waitForTimeout(1200); await shot('academy');
  await pg.locator('[data-act=openCourse]').first().click(); await pg.waitForTimeout(900);
  await pg.locator('[data-act=openLesson]').nth(2).click(); await pg.waitForTimeout(900);
  await pg.fill('#ls_v', 'https://vimeo.com/lesson-3'); await pg.waitForTimeout(300);
  await pg.evaluate(() => { const x = document.querySelector('.sheet-b'); if (x) x.scrollTop = 0; }); await shot('video');
  await pg.evaluate(() => { const x = document.querySelector('.sheet-b'); const h = [...x.querySelectorAll('h2')].find(e => /Материалы урока|Ders malzemeleri|Lesson materials/.test(e.textContent)); if (h) x.scrollTop = h.offsetTop - 40; }); await shot('lesson');
  await b.close();
})();
