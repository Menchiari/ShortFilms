const { chromium } = require('playwright');
(async () => {
  const [,, inHtml, outPng, outPdf] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 4680, height: 1400 }, deviceScaleFactor: 1 });
  await p.goto('file://' + inHtml, { waitUntil: 'networkidle' });
  await p.evaluate(async () => { await document.fonts.ready; });
  const fams = await p.evaluate(() => ['IM Fell English','Libre Caslon Text','Oswald','Playfair Display','UnifrakturMaguntia'].map(f => f + ':' + document.fonts.check('italic 40px "' + f + '"') + '/' + document.fonts.check('700 40px "' + f + '"')));
  console.log(fams.join(' '));
  const el = await p.$('.sheet');
  await el.screenshot({ path: outPng });
  if (outPdf) {
    const box = await el.boundingBox();
    await p.pdf({ path: outPdf, width: (box.width/300)+'in', height: (box.height/300)+'in', printBackground: true, margin: {top:0,bottom:0,left:0,right:0}, scale: 1/3.125 });
  }
  await b.close();
})();
