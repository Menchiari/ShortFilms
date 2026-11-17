const { chromium } = require('playwright');
(async () => {
  const [src, out] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage();
  await p.goto('file://' + require('path').resolve(src));
  await p.pdf({ path: out, format: 'Letter', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<div style="font:7pt sans-serif;width:100%;padding:0 0.45in;display:flex;justify-content:space-between;color:#444"><span>POLITICIAN</span><span>Shooting script, draft 10</span></div>',
    footerTemplate: '<div style="font:7pt sans-serif;width:100%;padding:0 0.45in;text-align:right;color:#444"><span class="pageNumber"></span> / <span class="totalPages"></span></div>' });
  await b.close();
})();
