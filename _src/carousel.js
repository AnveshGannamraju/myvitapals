// Renders Instagram carousel slides (1080x1350) from _src/carousels.json into _social/<post>/NN.png.
// Usage: EMOJI_FONT=/path/to/noto-color-emoji-0-400-normal.woff2 node _src/carousel.js
//        ONLY=02-vitamin-d-sunny node _src/carousel.js   (render just one post)
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, '_social');
const FONTS = path.join(ROOT, 'assets', 'fonts');
const ONLY = process.env.ONLY ? new Set(process.env.ONLY.split(',')) : null;
const posts = JSON.parse(fs.readFileSync(path.join(__dirname, 'carousels.json'), 'utf8')).filter(p => !ONLY || ONLY.has(p.id));
const pals = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(__dirname, 'og.json'), 'utf8')).map(o => [o.name, o]));

const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const pal = (name, w) => (pals[name] ? pals[name].svg : '').replace(/width="\d+" height="\d+"/, `width="${w}" height="${Math.round(w * 4 / 3)}"`);

const css = (color) => `
@font-face{font-family:Fraunces;font-weight:600;src:url(file://${FONTS}/fraunces-latin-600-normal.woff2)}
@font-face{font-family:Fraunces;font-weight:700;src:url(file://${FONTS}/fraunces-latin-700-normal.woff2)}
@font-face{font-family:Inter;font-weight:400;src:url(file://${FONTS}/inter-latin-400-normal.woff2)}
@font-face{font-family:Inter;font-weight:500;src:url(file://${FONTS}/inter-latin-500-normal.woff2)}
@font-face{font-family:Inter;font-weight:600;src:url(file://${FONTS}/inter-latin-600-normal.woff2)}
@font-face{font-family:Inter;font-weight:700;src:url(file://${FONTS}/inter-latin-700-normal.woff2)}
${process.env.EMOJI_FONT ? `@font-face{font-family:Emo;src:url(file://${process.env.EMOJI_FONT})}` : ''}
:root{--c:${color};--bg:#faf7f2;--ink:#17201b;--muted:#5b675f;--line:#e8e1d5;--brand:#1e6b52;--soft:#e9f3ee;--warm:#fff3dc;--warn:#fdecea;--warn-ink:#8a2a1c}
*{box-sizing:border-box}html,body{margin:0}
body{width:1080px;height:1350px;background:var(--bg);color:var(--ink);font-family:Inter,Emo,sans-serif;position:relative;overflow:hidden}
.band{position:absolute;left:0;right:0;top:0;height:20px;background:var(--c)}
.page{position:absolute;inset:20px 0 0;padding:96px 88px 150px;display:flex;flex-direction:column}
.foot{position:absolute;left:88px;right:88px;bottom:56px;display:flex;justify-content:space-between;align-items:center;font-size:26px;color:var(--muted)}
.brand{font-family:Fraunces,serif;font-weight:700;font-size:34px;color:var(--ink)}.brand b{color:var(--brand)}
.count{font-weight:600;letter-spacing:.04em}
h1{font-family:Fraunces,Emo,serif;font-weight:700;font-size:96px;line-height:1.04;letter-spacing:-.02em;margin:0}
h2{font-family:Fraunces,Emo,serif;font-weight:600;font-size:66px;line-height:1.1;letter-spacing:-.01em;margin:0 0 44px}
.k{font-size:28px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--c);margin:0 0 28px}
.lead{font-size:40px;line-height:1.35;color:var(--muted);margin:36px 0 0}
p{margin:0}
/* cover */
.cover{justify-content:center}
.cover .pal{margin:0 0 40px -8px}
.swipe{margin-top:auto;font-size:28px;font-weight:600;color:var(--c)}
/* text */
.body p{font-size:40px;line-height:1.4;padding:0 0 30px 38px;position:relative}
.body p:before{content:"";position:absolute;left:0;top:20px;width:14px;height:14px;border-radius:50%;background:var(--c)}
/* list */
.items{display:flex;flex-direction:column;gap:22px}
.item{background:#fff;border:2px solid var(--line);border-radius:24px;padding:26px 32px;border-left:12px solid var(--c)}
.item b{display:block;font-size:36px;line-height:1.25;margin-bottom:6px}
.item span{font-size:30px;line-height:1.4;color:var(--muted)}
/* myth */
.mythbox{border-radius:28px;padding:40px 44px}
.tag{display:inline-block;font-size:26px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;padding:8px 18px;border-radius:999px;margin-bottom:22px}
.m{background:var(--warn)}.m .tag{background:var(--warn-ink);color:#fff}
.m p{font-family:Fraunces,serif;font-weight:600;font-size:52px;line-height:1.18;color:var(--warn-ink)}
.f{background:var(--soft);margin-top:30px}.f .tag{background:var(--brand);color:#fff}
.f p{font-size:40px;line-height:1.4}
/* foods */
.need{display:inline-block;align-self:flex-start;background:var(--warm);font-size:30px;font-weight:600;padding:12px 22px;border-radius:14px;margin:-20px 0 34px}
.row{display:grid;grid-template-columns:1fr auto;gap:4px 24px;padding:20px 0;border-bottom:2px solid var(--line)}
.row .n{font-size:34px;font-weight:600;line-height:1.25}.row .s{font-size:26px;color:var(--muted)}
.row .a{font-size:38px;font-weight:700;text-align:right;grid-row:span 2;align-self:center}
.bar{grid-column:1/-1;height:14px;background:#efe9df;border-radius:99px;overflow:hidden;margin-top:10px}
.bar i{display:block;height:100%;background:var(--c);border-radius:99px}
.dv{font-size:24px;color:var(--muted);margin-top:16px}
.ind{margin-top:auto}
.ind h3{font-size:26px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 0 16px}
.chips{display:flex;flex-wrap:wrap;gap:12px}
.chips span{background:#fff;border:2px solid var(--line);border-radius:999px;padding:10px 22px;font-size:28px;font-weight:500}
/* table */
.trow{display:flex;justify-content:space-between;font-size:38px;padding:20px 0;border-bottom:2px solid var(--line)}
.trow b{font-weight:700}
.note{margin-top:34px;background:var(--warm);border-radius:20px;padding:26px 30px;font-size:30px;line-height:1.4}
/* cta */
.cta{justify-content:center;text-align:center;align-items:center}
.cta h2{font-size:72px;margin-bottom:40px}
.url{display:inline-block;background:var(--brand);color:#fff;font-weight:700;font-size:38px;padding:24px 40px;border-radius:999px}
.cta .sm{font-size:32px;color:var(--muted);margin-top:44px;line-height:1.4}
.disc{position:absolute;left:88px;right:88px;bottom:140px;text-align:center;font-size:24px;color:var(--muted)}
`;

function slideHtml(post, s, i, n) {
  let inner = '';
  if (s.type === 'cover') {
    inner = `<div class="page cover"><div class="pal">${pal(post.pal, 220)}</div><p class="k">${esc(s.kicker)}</p><h1>${esc(s.title)}</h1><p class="lead">${esc(s.lead)}</p><p class="swipe">Swipe →</p></div>`;
  } else if (s.type === 'text') {
    inner = `<div class="page" style="justify-content:center"><h2>${esc(s.title)}</h2><div class="body">${s.body.map(b => `<p>${esc(b)}</p>`).join('')}</div></div>`;
  } else if (s.type === 'list') {
    inner = `<div class="page"><h2>${esc(s.title)}</h2><div class="items">${s.items.map(([b, t]) => `<div class="item"><b>${esc(b)}</b><span>${esc(t)}</span></div>`).join('')}</div></div>`;
  } else if (s.type === 'myth') {
    inner = `<div class="page" style="justify-content:center"><div class="mythbox m"><span class="tag">Myth</span><p>“${esc(s.myth)}”</p></div><div class="mythbox f"><span class="tag">Fact</span><p>${esc(s.fact)}</p></div></div>`;
  } else if (s.type === 'foods') {
    const max = Math.max(100, ...s.rows.map(r => r[3]));
    inner = `<div class="page"><h2>${esc(s.title)}</h2>${s.need ? `<span class="need">${esc(s.need)}</span>` : ''}
      <div>${s.rows.map(([f, sv, a, dv]) => `<div class="row"><span class="n">${esc(f)}</span><span class="a">${esc(a)}</span><span class="s">${esc(sv)} · ${dv}% DV</span><div class="bar"><i style="width:${Math.max(2, dv / max * 100)}%"></i></div></div>`).join('')}</div>
      <p class="dv">${esc(s.dvNote)}</p>
      ${s.indian ? `<div class="ind"><h3>Indian kitchen picks</h3><div class="chips">${s.indian.map(c => `<span>${esc(c)}</span>`).join('')}</div></div>` : ''}</div>`;
  } else if (s.type === 'table') {
    inner = `<div class="page"><h2>${esc(s.title)}</h2><div>${s.rows.map(([a, b]) => `<div class="trow"><span>${esc(a)}</span><b>${esc(b)}</b></div>`).join('')}</div><p class="note">${esc(s.note)}</p></div>`;
  } else if (s.type === 'cta') {
    inner = `<div class="page cta"><div class="pal">${pal(post.pal, 150)}</div><h2>${esc(s.title)}</h2><span class="url">${esc(s.path)}</span><p class="sm">${esc(s.note || 'Free. No ads. Sources on every page.')}</p></div>
      <p class="disc">Educational only, not medical advice. Ask your doctor before starting supplements.</p>`;
  }
  return `<!doctype html><html><head><meta charset="utf-8"><style>${css(post.color)}</style></head><body><div class="band"></div>${inner}
  <div class="foot"><span class="brand">Vita<b>Pals</b></span><span class="count">${i + 1} / ${n}</span></div></body></html>`;
}

(async () => {
  const browser = await chromium.launch();
  const p = await (await browser.newContext({ viewport: { width: 1080, height: 1350 } })).newPage();
  const tmp = path.join(__dirname, '.tmp.html');
  let count = 0;
  for (const post of posts) {
    const dir = path.join(OUT, post.id);
    fs.rmSync(dir, { recursive: true, force: true });
    fs.mkdirSync(dir, { recursive: true });
    for (const [i, s] of post.slides.entries()) {
      fs.writeFileSync(tmp, slideHtml(post, s, i, post.slides.length));
      await p.goto('file://' + tmp);
      await p.evaluate(async () => { await document.fonts.load('40px Emo', document.body.innerText + '☀️🩸'); await document.fonts.ready; });
      await p.waitForTimeout(100);
      const over = await p.evaluate(() => { const pg = document.querySelector('.page'); return pg.scrollHeight > pg.clientHeight + 1; });
      if (over) console.warn(`OVERFLOW: ${post.id} slide ${i + 1}`);
      await p.screenshot({ path: path.join(dir, String(i + 1).padStart(2, '0') + '.png') });
      count++;
    }
  }
  fs.unlinkSync(tmp);
  await browser.close();
  console.log(`Rendered ${count} slides for ${posts.length} posts into _social/`);
})();
