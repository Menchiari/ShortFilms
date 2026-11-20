// node render_page_v2.js in.html out.png : renders .sheet at 2550x3300 (US Letter, 300 dpi)
const { chromium } = require('playwright');
(async () => {
  const [,, inHtml, outPng] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2550, height: 3300 } });
  await p.goto('file://' + inHtml, { waitUntil: 'networkidle' });
  await p.evaluate(async () => { await document.fonts.ready; });
  console.log('tinos:', await p.evaluate(() => document.fonts.check('40px "Tinos"')));
  const box = await p.evaluate(() => { const r = document.querySelector('#by').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; });
  console.log('BY', JSON.stringify(box));
  await (await p.$('.sheet')).screenshot({ path: outPng });
  await b.close();
})();
