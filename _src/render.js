// Renders share-preview images (og/*.png) and PNG icons.
// Usage: FONT_DIR=/path/to/node_modules/@fontsource node _src/render.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const FONT_DIR = process.env.FONT_DIR;
const ONLY = process.env.ONLY ? new Set(process.env.ONLY.split(',')) : null; // e.g. ONLY=iron,calcium renders just those
const items = JSON.parse(fs.readFileSync(path.join(__dirname, 'og.json'), 'utf8')).filter(it => !ONLY || ONLY.has(it.name));

function fontCss() {
  if (!FONT_DIR) return '';
  const pick = (pkg, file) => `file://${path.join(FONT_DIR, pkg, file)}`;
  let css = `
  @font-face{font-family:Fraunces;font-weight:700;src:url(${pick('fraunces', 'files/fraunces-latin-700-normal.woff2')})}
  @font-face{font-family:Inter;font-weight:600;src:url(${pick('inter', 'files/inter-latin-600-normal.woff2')})}`;
  return css + `@font-face{font-family:Emo;src:url(${pick('noto-color-emoji', 'files/noto-color-emoji-0-400-normal.woff2')})}`;
}

const page = (it) => `<!doctype html><html><head><meta charset="utf-8"><style>
${fontCss()}
*{box-sizing:border-box}html,body{margin:0}
body{width:1200px;height:630px;background:#fffaf2;font-family:Inter,'Emo',sans-serif;color:#2b2340;display:flex;flex-direction:column;justify-content:center;padding:56px 72px;position:relative;overflow:hidden}
body:before{content:"";position:absolute;inset:0;border-top:22px solid ${it.color}}
.row{display:flex;align-items:center;gap:56px}
.multi{display:flex;gap:6px;justify-content:center;margin-bottom:26px}
h1{font-family:Fraunces,'Emo',sans-serif;font-size:${it.name === 'home' ? 76 : 84}px;line-height:1.05;margin:0 0 18px}
.k{font-size:30px;font-weight:600;color:#6b6380;text-transform:uppercase;letter-spacing:.05em;margin:0 0 10px}
.l{font-size:32px;margin:0;line-height:1.35}
.brand{position:absolute;right:56px;bottom:36px;font-family:Fraunces,'Emo',sans-serif;font-size:36px;font-weight:700}
.brand b{color:#1e6b52}
svg text{font-family:Fraunces,'Emo',sans-serif}
.home{text-align:center}
</style></head><body>
${it.name === 'home' || it.multi
  ? `<div class="home"><div class="multi">${it.svg}</div><h1>${it.title}</h1><p class="l">${it.lead}</p></div>`
  : `<div class="row">${it.svg}<div><p class="k">${it.kicker}</p><h1>${it.title}</h1><p class="l">${it.lead}</p></div></div>`}
<div class="brand">Vita<b>Pals</b> · myvitapals.com</div>
</body></html>`;

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1200, height: 630 } });
  const p = await ctx.newPage();
  fs.mkdirSync(path.join(ROOT, 'og'), { recursive: true });
  const tmp = path.join(__dirname, '.tmp.html');
  for (const it of items) {
    fs.writeFileSync(tmp, page(it));
    await p.goto('file://' + tmp);
    await p.evaluate(async () => { const t = document.body.innerText + Array.from(document.querySelectorAll('svg text')).map(n => n.textContent).join(''); await document.fonts.load('40px Emo', t); await document.fonts.load('40px Fredoka', t); await document.fonts.ready; });
    await p.waitForTimeout(150);
    await p.screenshot({ path: path.join(ROOT, 'og', it.name + '.png') });
  }
  // Icons from favicon.svg
  if (ONLY) { fs.unlinkSync(tmp); await browser.close(); console.log(`Rendered ${items.length} share images`); return; }
  const svg = fs.readFileSync(path.join(ROOT, 'favicon.svg'), 'utf8');
  for (const [file, size, bg] of [['favicon-32.png', 32, 'transparent'], ['apple-touch-icon.png', 180, '#fffaf2']]) {
    await p.setViewportSize({ width: size, height: size });
    await p.setContent(`<html><body style="margin:0;background:${bg}"><div style="width:${size}px;height:${size}px;display:flex;align-items:center;justify-content:center">${svg.replace('<svg ', `<svg width="${Math.round(size * (bg === 'transparent' ? 1 : 0.8))}" height="${Math.round(size * (bg === 'transparent' ? 1 : 0.8))}" `)}</div></body></html>`);
    await p.screenshot({ path: path.join(ROOT, file), omitBackground: bg === 'transparent' });
  }
  fs.unlinkSync(tmp);
  await browser.close();
  console.log(`Rendered ${items.length} share images + 2 icons`);
})();
