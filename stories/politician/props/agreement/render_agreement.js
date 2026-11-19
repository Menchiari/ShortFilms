// node render_agreement.js : agreement.html -> agreement_page_v1.png, frame.html -> agreement_frame_v1.png
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const d = __dirname;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2550, height: 3300 } });
  await p.goto('file://' + path.join(d, 'agreement.html'), { waitUntil: 'networkidle' });
  await p.evaluate(async () => { await document.fonts.ready; });
  console.log('caslon:', await p.evaluate(() => document.fonts.check('40px "Libre Caslon Text"')));
  await (await p.$('.sheet')).screenshot({ path: path.join(d, 'agreement_page_v1.png') });
  const f = await b.newPage({ viewport: { width: 3840, height: 1646 } });
  await f.goto('file://' + path.join(d, 'frame.html'), { waitUntil: 'networkidle' });
  await (await f.$('.frame')).screenshot({ path: path.join(d, 'agreement_frame_v1.png') });
  await b.close();
})();
