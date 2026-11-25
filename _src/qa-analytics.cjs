// Privacy test for analytics: serves the local build as https://myvitapals.com with GC_CODE switched on,
// captures every GoatCounter request and checks nothing typed or answered is sent.
// Run: node _src/qa-analytics.cjs   (PW_CHANNEL=chrome to use Chrome instead of Edge)
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2' };
(async () => {
  const browser = await chromium.launch({ headless: true, channel: process.env.PW_CHANNEL || 'msedge' });
  const run = async (opts, fn) => {
    const ctx = await browser.newContext(opts);
    const sent = [];
    await ctx.route('https://myvitapals.com/**', route => {
      let p = decodeURIComponent(new URL(route.request().url()).pathname);
      if (p.endsWith('/')) p += 'index.html';
      const file = path.join(ROOT, p);
      if (!fs.existsSync(file)) return route.fulfill({ status: 404, body: 'not found' });
      let body = fs.readFileSync(file);
      if (p === '/assets/app.js') body = body.toString().replace('var GC_CODE = "";', 'var GC_CODE = "qa";');
      route.fulfill({ status: 200, body, contentType: TYPES[path.extname(file)] || 'application/octet-stream' });
    });
    await ctx.route('https://qa.goatcounter.com/**', route => { sent.push(new URL(route.request().url())); route.fulfill({ status: 200, body: '' }); });
    const page = await ctx.newPage();
    await fn(page);
    await page.waitForTimeout(300);
    await ctx.close();
    return sent;
  };
  const SECRET = 'zqxsecretword';
  let sent = await run({}, async page => {
    await page.goto('https://myvitapals.com/tools/food-finder/?q=' + SECRET);
    await page.fill('#ff-q', 'spinach ' + SECRET); await page.waitForTimeout(1700);
    await page.fill('#ff-q', 'spinach'); await page.waitForTimeout(1700);
    await page.selectOption('#ff-diet', 'vegan');
    await page.goto('https://myvitapals.com/tools/vitamin-check/');
    for (const [n, v] of Object.entries({ diet: 'vegan', age: '71', preg: 'no', sun: 'rare', skin: 'dark', greens: 'daily', fruit: 'daily', nuts: 'often', dairy: 'rare', salt: 'yes', periods: 'no' }))
      await page.check(`input[name="${n}"][value="${v}"]`);
    await page.check('[name=metformin]');
    await page.click('button[type=submit]');
    await page.click('#vcheck-out a[href="/vitamin-b12/"]'); await page.waitForLoadState();
  });
  const all = sent.map(u => decodeURIComponent(u.search)).join('\n');
  assert.ok(sent.some(u => u.searchParams.get('p') === '/tools/food-finder/' && u.searchParams.get('e') === 'false'), 'page view recorded');
  assert.ok(!all.includes(SECRET), 'typed text or query string leaked');
  assert.ok(sent.some(u => /^food-finder-search:/i.test(u.searchParams.get('p'))), 'food finder event');
  assert.ok(sent.some(u => u.searchParams.get('p') === 'vitamin-check-complete'), 'vitamin check completion event');
  assert.ok(sent.some(u => u.searchParams.get('p') === 'nav-content:/vitamin-b12/'), 'navigation click event');
  for (const bad of ['vegan', '71', 'metformin', 'dark', 'rare']) assert.ok(!sent.some(u => (u.searchParams.get('p') || '').includes('vitamin-check') && decodeURIComponent(u.search).includes(bad)), 'answer leaked: ' + bad);
  assert.ok(sent.every(u => !(u.searchParams.get('p') || '').startsWith('/') || !u.searchParams.get('p').includes('?')), 'path contains a query string');
  // Do Not Track / Global Privacy Control: nothing is sent.
  const dnt = await run({ extraHTTPHeaders: {} }, async page => {
    await page.addInitScript(() => Object.defineProperty(navigator, 'globalPrivacyControl', { get: () => true }));
    await page.goto('https://myvitapals.com/');
  });
  assert.equal(dnt.length, 0, 'GPC not respected');
  await browser.close();
  console.log(`PASS: analytics sends ${sent.length} anonymous counts; no typed text, query strings or vitamin-check answers; GPC respected`);
})().catch(e => { console.error(e); process.exit(1); });
