// Renders Instagram carousel slides (1080x1350) from _src/carousels.json into _social/<post>/NN.png.
// Visual-first: one big picture + a few words per slide, readable in about a second.
// Usage: node _src/carousel.js            (needs the "Noto Color Emoji" font installed, or EMOJI_FONT=/path/to/font)
//        ONLY=02-vitamin-d-sunny node _src/carousel.js
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
const words = s => String(s).trim().split(/\s+/).length;

const css = (post) => `
@font-face{font-family:Fraunces;font-weight:700;src:url(file://${FONTS}/fraunces-latin-700-normal.woff2)}
@font-face{font-family:Inter;font-weight:500;src:url(file://${FONTS}/inter-latin-500-normal.woff2)}
@font-face{font-family:Inter;font-weight:600;src:url(file://${FONTS}/inter-latin-600-normal.woff2)}
@font-face{font-family:Inter;font-weight:700;src:url(file://${FONTS}/inter-latin-700-normal.woff2)}
${process.env.EMOJI_FONT ? `@font-face{font-family:"Noto Color Emoji";src:url(file://${process.env.EMOJI_FONT})}` : ''}
:root{--c:${post.color};--on:${post.dark ? '#17201b' : '#fff'};--bg:#faf7f2;--ink:#17201b;--muted:#5b675f;--line:#e8e1d5;--brand:#1e6b52;--soft:#e9f3ee;--warn:#fdecea;--warn-ink:#8a2a1c}
*{box-sizing:border-box}html,body{margin:0}
body{width:1080px;height:1350px;background:var(--bg);color:var(--ink);font-family:Inter,"Noto Color Emoji",sans-serif;position:relative;overflow:hidden}
body.color{background:var(--c);color:var(--on)}
.e{font-family:"Noto Color Emoji";line-height:1}
.page{position:absolute;inset:0;padding:110px 80px 150px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
h1{font-family:Fraunces,serif;font-weight:700;font-size:112px;line-height:1.02;letter-spacing:-.025em;margin:0}
h2{font-family:Fraunces,serif;font-weight:700;font-size:76px;line-height:1.05;letter-spacing:-.015em;margin:0}
.sub{font-size:34px;font-weight:600;margin-top:20px;color:var(--muted)}
.color .sub{color:var(--on);opacity:.85}
.foot{position:absolute;left:80px;right:80px;bottom:56px;display:flex;justify-content:space-between;align-items:center;font-size:28px;font-weight:600}
.brand{font-family:Fraunces,serif;font-weight:700;font-size:38px}.brand b{color:var(--brand)}
.color .brand b{color:inherit;opacity:.75}
.count{opacity:.6}
/* hook */
.hook .big{font-size:340px;margin-bottom:60px}
.hook .pal{margin-bottom:50px}
.swipe{position:absolute;bottom:140px;left:0;right:0;font-size:32px;font-weight:700;opacity:.85}
/* grid */
.grid{display:grid;grid-template-columns:1fr 1fr;gap:28px;width:100%;margin-top:50px}
.tile{background:#fff;border-radius:36px;padding:40px 20px 34px;box-shadow:0 2px 0 var(--line);display:flex;flex-direction:column;align-items:center}
.tile .e{font-size:150px;margin-bottom:18px}
.tile .amt{font-size:62px;font-weight:700;color:var(--c);letter-spacing:-.02em;line-height:1.05}
.dark-c .tile .amt{color:#9a6b00}
.tile .nm{font-size:34px;font-weight:600;margin-top:8px;line-height:1.2}
.tile .sv{font-size:26px;color:var(--muted);margin-top:4px}
.tile.label .nm{font-size:40px;margin-top:6px}
.small .grid{grid-template-columns:1fr 1fr;gap:22px}
.small .tile{padding:28px 16px 24px}.small .tile .e{font-size:96px;margin-bottom:10px}
.small .tile .amt{font-size:50px}.small .tile .nm{font-size:30px}
.note{margin-top:34px;font-size:34px;font-weight:600}
/* myth / fact */
.mf{width:100%;border-radius:40px;padding:50px 50px 56px;display:flex;flex-direction:column;align-items:center}
.mf .e{font-size:130px;margin-bottom:20px}
.mf p{margin:0;font-family:Fraunces,serif;font-weight:700;font-size:64px;line-height:1.1}
.mf.m{background:var(--warn);color:var(--warn-ink)}.mf.m p{text-decoration:line-through;text-decoration-thickness:6px}
.mf.f{background:var(--soft);color:var(--ink);margin-top:34px}.mf.f p{font-family:Inter,sans-serif;font-weight:600;font-size:50px;line-height:1.25}
/* stat */
.stat .e{font-size:220px;margin-bottom:40px}
.stat .num{font-family:Fraunces,serif;font-weight:700;font-size:150px;line-height:1;letter-spacing:-.03em;color:var(--c)}
.dark-c .stat .num{color:#9a6b00}
.stat .lbl{font-size:52px;font-weight:700;margin-top:30px;line-height:1.2}
.stat .sub{font-size:40px}
/* tips */
.rows{width:100%;margin-top:56px;display:flex;flex-direction:column;gap:26px}
.r{display:flex;align-items:center;gap:36px;background:#fff;border-radius:36px;padding:30px 40px;text-align:left;box-shadow:0 2px 0 var(--line)}
.r .e{font-size:120px;flex:none}
.r span{font-size:48px;font-weight:700;line-height:1.2}
/* vs */
.vs{display:flex;gap:40px;align-items:flex-end;justify-content:center;margin-top:60px;height:640px}
.col{display:flex;flex-direction:column;align-items:center;width:340px}
.col .amt{font-size:72px;font-weight:700;margin-bottom:16px}
.bar{width:220px;background:var(--c);border-radius:28px 28px 8px 8px}
.col .nm{font-size:40px;font-weight:700;margin-top:24px}
/* cta */
.cta .pal{margin-bottom:40px}
.url{display:inline-block;background:var(--brand);color:#fff;font-weight:700;font-size:42px;padding:26px 44px;border-radius:999px;margin-top:44px}
.cta .follow{font-size:36px;font-weight:600;margin-top:44px;color:var(--muted)}
.disc{position:absolute;left:80px;right:80px;bottom:130px;text-align:center;font-size:24px;color:var(--muted)}
`;

function slide(post, s) {
  const e = x => `<span class="e">${x}</span>`;
  switch (s.type) {
    case 'hook': return [true, `<div class="page hook">${s.pal ? `<div class="pal">${pal(post.pal, 300)}</div>` : `<div class="big e">${s.emoji}</div>`}<h1>${esc(s.title)}</h1></div><div class="swipe">Swipe →</div>`];
    case 'grid': return [false, `<div class="page${s.small ? ' small' : ''}"><h2>${esc(s.title)}</h2>${s.sub ? `<p class="sub">${esc(s.sub)}</p>` : ''}
      <div class="grid">${s.tiles.map(([em, nm, amt, sv]) => `<div class="tile${amt ? '' : ' label'}">${e(em)}${amt ? `<div class="amt">${esc(amt)}</div>` : ''}<div class="nm">${esc(nm)}</div>${sv ? `<div class="sv">${esc(sv)}</div>` : ''}</div>`).join('')}</div>
      ${s.note ? `<p class="note">${esc(s.note)}</p>` : ''}</div>`];
    case 'mythfact': return [false, `<div class="page"><div class="mf m">${e('❌')}<p>${esc(s.myth)}</p></div><div class="mf f">${e('✅')}<p>${esc(s.fact)}</p></div></div>`];
    case 'stat': return [false, `<div class="page stat">${e(s.emoji)}<div class="num">${esc(s.big)}</div><div class="lbl">${esc(s.label)}</div>${s.sub ? `<p class="sub">${esc(s.sub)}</p>` : ''}</div>`];
    case 'tips': return [false, `<div class="page"><h2>${esc(s.title)}</h2><div class="rows">${s.rows.map(([em, t]) => `<div class="r">${e(em)}<span>${esc(t)}</span></div>`).join('')}</div></div>`];
    case 'vs': {
      const max = Math.max(...s.items.map(i => i[3]));
      return [false, `<div class="page"><h2>${esc(s.title)}</h2><div class="vs">${s.items.map(([em, nm, amt, v]) => `<div class="col"><div class="amt">${esc(amt)}</div><div class="bar" style="height:${Math.max(30, v / max * 440)}px"></div><div class="nm">${esc(nm)}</div></div>`).join('')}</div>${s.note ? `<p class="note">${esc(s.note)}</p>` : ''}</div>`];
    }
    case 'cta': return [false, `<div class="page cta"><div class="pal">${pal(post.pal, 200)}</div><h2>${esc(s.title)}</h2><span class="url">${esc(s.path)}</span><p class="follow">Follow for more 1-second vitamin facts</p></div>
      <p class="disc">Educational only, not medical advice. Ask your doctor before starting supplements.</p>`];
  }
  throw new Error('Unknown slide type ' + s.type);
}

(async () => {
  const browser = await chromium.launch();
  const p = await (await browser.newContext({ viewport: { width: 1080, height: 1350 } })).newPage();
  const tmp = path.join(__dirname, '.tmp.html');
  let count = 0;
  for (const post of posts) {
    const dir = path.join(OUT, post.id);
    fs.mkdirSync(dir, { recursive: true });
    for (const f of fs.readdirSync(dir)) if (f.endsWith('.png')) fs.unlinkSync(path.join(dir, f));
    for (const [i, s] of post.slides.entries()) {
      if (s.title && words(s.title) > 8) console.warn(`LONG TITLE (${words(s.title)} words): ${post.id} slide ${i + 1}`);
      const [colored, inner] = slide(post, s);
      fs.writeFileSync(tmp, `<!doctype html><html><head><meta charset="utf-8"><style>${css(post)}</style></head><body class="${colored ? 'color' : ''}${post.dark ? ' dark-c' : ''}">${inner}
        <div class="foot"><span class="brand">Vita<b>Pals</b></span><span class="count">${i + 1} / ${post.slides.length}</span></div></body></html>`);
      await p.goto('file://' + tmp);
      await p.evaluate(async () => { await document.fonts.ready; });
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
