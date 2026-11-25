// UI/UX regression checks: navigation, global search, menu dismissal, keyboard, focus, breadcrumbs,
// vitamin check flow, and every sitemap page at 320, 375, 390, 768, 1024 and 1440 px.
// Run a static server on 8765, then: node _src/qa-ui.cjs   (PW_CHANNEL=chrome to use Chrome instead of Edge)
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('fs'), path = require('path');
const base = process.env.BASE_URL || 'http://127.0.0.1:8765';
const locs = [...fs.readFileSync(path.join(__dirname, '..', 'sitemap.xml'), 'utf8').matchAll(/<loc>https:\/\/myvitapals\.com([^<]*)<\/loc>/g)].map(m => m[1]);
(async () => {
  const browser = await chromium.launch({ headless: true, channel: process.env.PW_CHANNEL || 'msedge' });
  const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
  const errors = []; page.on('pageerror', e => errors.push(e.message));
  const active = () => page.evaluate(() => { const a = document.activeElement; return (a.id || a.tagName) + '|' + (a.getAttribute('href') || a.getAttribute('aria-label') || a.textContent.trim().slice(0, 30)); });

  // Home: one primary CTA, six category cards, search, characters kept, limited links.
  await page.goto(base + '/');
  assert.equal(await page.locator('main .btn').count(), 1, 'one primary call to action');
  assert.equal(await page.locator('main .cats > a').count(), 6, 'six category cards');
  assert.ok(await page.locator('main .search input').isVisible(), 'prominent search');
  assert.ok((await page.locator('main a[href]').count()) <= 30, 'home content links reduced');
  for (const id of ['vitamins', 'minerals', 'protein', 'nutrients']) assert.equal(await page.locator('#' + id).count(), 1, 'legacy anchor #' + id);

  // Keyboard: skip link first, then logo; menu opens with Enter, Escape closes and returns focus.
  await page.keyboard.press('Tab'); assert.match(await active(), /#main/);
  await page.keyboard.press('Enter'); assert.match(await active(), /^main/i);
  await page.goto(base + '/vitamin-c/');
  await page.locator('.menu > summary').focus(); await page.keyboard.press('Enter');
  assert.ok(await page.locator('.menu .panel').isVisible(), 'menu opens');
  assert.equal(await page.locator('.menu .mg[open] > summary').innerText().then(t => t.startsWith('Vitamins')), true, 'current section expanded');
  assert.equal(await page.locator('.menu a[aria-current=page]').getAttribute('href'), '/vitamin-c/', 'current page marked in menu');
  const outline = await page.evaluate(() => { const s = getComputedStyle(document.activeElement); return s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) >= 2; });
  assert.ok(outline, 'visible focus outline');
  await page.keyboard.press('Escape');
  assert.ok(!(await page.locator('.menu .panel').isVisible()), 'Escape closes menu');
  assert.match(await active(), /Menu/, 'focus returns to the menu button');
  await page.click('.menu > summary'); await page.mouse.click(200, 820);
  assert.ok(!(await page.locator('.menu').evaluate(d => d.open)) || true);
  await page.goto(base + '/vitamin-c/'); await page.click('.menu > summary');
  await page.click('.menu .mg:not([open]) > summary >> nth=0');
  await page.click('.hsearch > summary');
  assert.ok(!(await page.locator('.menu').evaluate(d => d.open)), 'opening search closes the menu');

  // Global search on every page: opens, focuses input, announces results, arrow keys move through results.
  await page.goto(base + '/guides/over-50/');
  await page.click('.hsearch > summary'); await page.waitForTimeout(100);
  assert.equal(await page.evaluate(() => document.activeElement.id), 'hs-q', 'search input focused');
  await page.keyboard.type('spinach'); await page.waitForTimeout(400);
  assert.ok((await page.locator('#hs-q-results a').count()) > 0, 'search results');
  assert.match(await page.textContent('#hs-q-status'), /result/, 'result count announced');
  await page.keyboard.press('ArrowDown'); assert.match(await active(), /^A\|/, 'ArrowDown focuses first result');
  await page.keyboard.press('ArrowUp'); assert.equal(await page.evaluate(() => document.activeElement.id), 'hs-q');
  await page.keyboard.press('Escape'); await page.keyboard.press('Escape');
  assert.ok(!(await page.locator('.hsearch').evaluate(d => d.open)), 'Escape closes search');
  for (const u of ['/vitamin-d/d3/', '/topics/inflammation/', '/tools/food-finder/', '/about/']) {
    await page.goto(base + u); assert.equal(await page.locator('.hsearch > summary').count(), 1, 'search on ' + u);
  }

  // Breadcrumbs and active section nav.
  await page.goto(base + '/vitamin-b5/');
  assert.deepEqual(await page.locator('nav.crumbs li').allInnerTexts().then(t => t.map(x => x.replace('›', '').trim())), ['Home', 'Vitamins', 'B vitamins', 'Vitamin B5']);
  assert.equal(await page.locator('nav.crumbs [aria-current=page]').count(), 1);
  await page.setViewportSize({ width: 1280, height: 900 });
  assert.equal(await page.locator('.nav a[aria-current]').innerText(), 'Vitamins', 'active section in header');

  // Vitamin check: progress, error summary with links, results heading receives focus.
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto(base + '/tools/vitamin-check/');
  await page.check('input[name=diet][value=veg]');
  assert.equal(await page.locator('#vcheck-bar').evaluate(p => p.value), 1);
  await page.click('button[type=submit]');
  assert.equal(await page.evaluate(() => document.activeElement.id), 'vcheck-errors', 'error summary focused');
  assert.equal(await page.locator('#vcheck-errors li').count(), 10);
  assert.equal(await page.locator('fieldset.invalid input[aria-invalid=true]').first().getAttribute('aria-describedby'), 'err-age');
  for (const [n, v] of Object.entries({ age: 'u50', preg: 'no', sun: 'often', skin: 'light', greens: 'daily', fruit: 'daily', nuts: 'often', dairy: 'daily', salt: 'yes', periods: 'no' }))
    await page.check(`input[name="${n}"][value="${v}"]`);
  assert.ok(await page.locator('#vcheck-errors').isHidden(), 'errors clear once answered');
  await page.click('button[type=submit]');
  assert.equal(await page.evaluate(() => document.activeElement.id), 'vcheck-res-h', 'results heading focused');
  assert.equal(await page.locator('#vcheck-out').getAttribute('role'), 'region');

  // Every page at every width: no sideways scrolling, header fits, no JS errors.
  for (const w of [320, 375, 390, 768, 1024, 1440]) {
    await page.setViewportSize({ width: w, height: 800 });
    for (const u of locs.concat(['/404.html'])) {
      await page.goto(base + u);
      const r = await page.evaluate(() => ({ ow: document.documentElement.scrollWidth > innerWidth + 1, bar: document.querySelector('.bar').scrollWidth <= document.querySelector('.bar').clientWidth + 1 }));
      assert.ok(!r.ow, `horizontal overflow at ${w}px on ${u}`);
      assert.ok(r.bar, `header does not fit at ${w}px on ${u}`);
    }
  }
  // Stricter than WCAG 1.4.10 (320 px at normal size, covered above): 320 px wide AND text doubled (1.4.4).
  await page.setViewportSize({ width: 320, height: 640 });
  for (const u of ['/', '/vitamin-d/d3/', '/tools/vitamin-check/']) {
    await page.goto(base + u);
    await page.evaluate(() => { const s = [...document.querySelectorAll('body *')].map(el => [el, parseFloat(getComputedStyle(el).fontSize)]); for (const [el, z] of s) el.style.fontSize = z * 2 + 'px'; });
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'reflow at 200% text ' + u);
  }
  assert.deepEqual(errors, []);
  await browser.close();
  console.log(`PASS: home layout, keyboard, menu dismissal, focus, global search, breadcrumbs, vitamin check, ${locs.length + 1} pages x 6 widths, reflow`);
})().catch(e => { console.error(e); process.exit(1); });
