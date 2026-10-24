#!/usr/bin/env python3
"""VitaPals static site builder.

Edit _src/vitamins.json, then run:  python3 _src/build.py
Every page is written as plain HTML so search engines and link previews see the full content.
(Folders starting with "_" are not published by GitHub Pages.)
"""
import json, html, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://myvitapals.com"
REVIEWED = "October 2026"
TODAY = datetime.date.today().isoformat()
YEAR = datetime.date.today().year
CSS_VERSION = "3"

V = json.loads((ROOT / "_src" / "vitamins.json").read_text(encoding="utf-8"))
BYID = {v["id"]: v for v in V}
BS = [v for v in V if v["id"].startswith("B")]
B_HUB = {"id": "B", "color": "#ef476f", "text": "#fff", "prop": "🐝", "nick": "The B-Team", "name": "8 B vitamins"}
FAMILY = [BYID["A"], B_HUB, BYID["C"], BYID["D"], BYID["E"], BYID["K"]]

e = lambda s: html.escape(str(s), quote=True)
slug = lambda v: f"vitamin-{v['id'].lower()}"
url = lambda v: f"/{slug(v)}/"
txt = lambda v: v.get("text", "#fff")


def pal(v, w, decorative=True):
    label = 'aria-hidden="true"' if decorative else f'role="img" aria-label="Vitamin {e(v["id"])} mascot"'
    fs = 24 if len(v["id"]) > 2 else (28 if len(v["id"]) == 2 else 40)
    c = v["color"]
    return (f'<svg viewBox="0 0 120 160" width="{w}" height="{round(w*4/3)}" {label}>'
            f'<ellipse cx="60" cy="153" rx="34" ry="5" fill="#000" opacity=".08"/>'
            f'<path d="M22 88q-16-2-18-20" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<path d="M98 88q16-6 16-26" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<rect x="22" y="12" width="76" height="136" rx="38" fill="{c}"/>'
            f'<path d="M22 80H98V110A38 38 0 0 1 22 110Z" fill="#fff" opacity=".22"/>'
            f'<ellipse cx="40" cy="36" rx="6" ry="13" fill="#fff" opacity=".35"/>'
            f'<circle cx="47" cy="56" r="7.5" fill="#fff"/><circle cx="73" cy="56" r="7.5" fill="#fff"/>'
            f'<circle cx="48" cy="57" r="3.8" fill="#2b2340"/><circle cx="74" cy="57" r="3.8" fill="#2b2340"/>'
            f'<circle cx="37" cy="69" r="5" fill="#ff8fa3" opacity=".6"/><circle cx="83" cy="69" r="5" fill="#ff8fa3" opacity=".6"/>'
            f'<path d="M50 68q10 10 20 0" stroke="#2b2340" stroke-width="3" fill="none" stroke-linecap="round"/>'
            f'<text x="60" y="{128 if fs == 40 else 122}" text-anchor="middle" font-family="Fredoka,sans-serif" font-weight="700" font-size="{fs}" fill="{txt(v)}">{e(v["id"])}</text>'
            f'<text x="96" y="22" font-size="24" text-anchor="middle">{v["prop"]}</text></svg>')


def head(title, desc, path, og):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta name="theme-color" content="#fffaf2">
<meta property="og:type" content="website">
<meta property="og:site_name" content="VitaPals">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/og/{og}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v={CSS_VERSION}">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""


def tabs(cur, sub=None):
    out = [f'<a href="/" style="--c:var(--accent)"{" class=on aria-current=page" if cur == "home" else ""}>🏠 Home</a>']
    for v in FAMILY:
        on = cur == v["id"]
        out.append(f'<a href="{url(v)}" style="--c:{v["color"]};--t:{txt(v)}"{" class=on" if on else ""}{" aria-current=page" if on and not sub else ""}>{e(v["id"])}</a>')
    nav = f'<nav class="tabs" aria-label="Vitamins">{"".join(out)}</nav>'
    if cur == "B":
        s = [f'<a href="{url(b)}" style="--c:{b["color"]};--t:{txt(b)}"{" class=on aria-current=page" if sub == b["id"] else ""}>{e(b["id"])}</a>' for b in BS]
        nav += f'<nav class="tabs subtabs" aria-label="B vitamins">{"".join(s)}</nav>'
    return f"""
<header>
  <div class="top">
    <a class="brand" href="/" aria-label="VitaPals home">💊 Vita<b>Pals</b></a>
    <div class="tag">Tiny helpers.<br>Big jobs.</div>
  </div>
  {nav}
</header>
<main id="main">"""


FOOT = f"""
</main>
<footer>
  <nav aria-label="Footer"><a href="/">Home</a><a href="/vitamin-b/">B-Team</a><a href="/about/">About</a></nav>
  <p>VitaPals is for friendly learning, not medical advice. Please talk to a doctor or pharmacist before starting any supplement.</p>
  <p>© {YEAR} VitaPals</p>
</footer>
</body>
</html>
"""


def vcard(v):
    return (f'<a class="vcard" href="{url(v)}" style="--c:{v["color"]}">{pal(v, 70)}'
            f'<h3>{"Vitamin " if len(v["id"]) == 1 else ""}{e(v["id"])}</h3><p class="nick">{e(v["nick"])}</p><p>{e(v["name"])}</p></a>')


def mini(v):
    return f'<a href="{url(v)}" style="--c:{v["color"]};--t:{txt(v)}">{e(v["id"])}</a>'


def perks(items):
    return '<div class="perks">' + "".join(
        f'<div class="perk"><div class="e" aria-hidden="true">{p[0]}</div><div><h3>{e(p[1])}</h3><p>{e(p[2])}</p></div></div>' for p in items) + "</div>"


def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


# ---------- Home ----------
water = [v for v in V if v["type"] == "water"]
fat = [v for v in V if v["type"] == "fat"]
home = head("VitaPals — Vitamins Made Easy (and a Little Fun)",
            "A friendly, simple guide to vitamins A, B, C, D, E and K: what they do, where to find them, and fun facts for all ages.",
            "/", "home") + tabs("home") + f"""
<section class="hero center">
  <p class="kicker">Welcome to VitaPals</p>
  <h1>Meet your VitaPals 👋</h1>
  <div class="squad">{"".join(pal(v, 58) for v in FAMILY)}</div>
  <p class="lead">13 tiny vitamins with very big jobs. They power you up, protect your cells, build your bones and help you see in the dark. Tap one to say hi!</p>
</section>

<h2 class="sec">Pick a pal 👇</h2>
<div class="grid">{"".join(vcard(v) for v in FAMILY)}</div>

<h2 class="sec">Meet the B-Team 🐝</h2>
<p class="sub">Vitamin B is actually a squad of eight. Each one has its own job.</p>
<div class="grid">{"".join(vcard(v) for v in BS)}</div>

<h2 class="sec">Two teams, two styles</h2>
<div class="teams">
  <div class="team water"><h3>💧 Water-soluble</h3><p>They dissolve in water, so your body flushes out extras. You need a steady supply from food, and too much from food is rarely a worry.</p>
    <div class="mini">{"".join(mini(v) for v in water)}</div></div>
  <div class="team fat"><h3>🧈 Fat-soluble</h3><p>They're stored in your body's fat and liver, so they stick around. That's handy, but too much from supplements can build up and cause trouble.</p>
    <div class="mini">{"".join(mini(v) for v in fat)}</div></div>
</div>

<h2 class="sec">What vitamins do for you</h2>
{perks([
 ["⚡","Energy from food","The B-Team turns breakfast into get-up-and-go."],
 ["👀","Eyes that see in the dark","Vitamin A keeps your eyes working in dim light."],
 ["🛡️","Germ fighting","Vitamins A, C and D help your immune system."],
 ["🦴","Strong bones","Vitamins D and K help build and protect bones."],
 ["🩹","Healing cuts","Vitamin K stops bleeding; vitamin C rebuilds skin."],
 ["🧠","Brain & nerves","B6 and B12 keep your body's wiring humming."],
 ["🧬","New cells","Folate (B9) and B12 are your body's builders."],
 ["🔰","Cell protection","Vitamins C and E guard cells from damage."]
])}

<div class="cards">
  <div class="card note"><h2>🌈 Eat the rainbow</h2><p>Most people get the vitamins they need from a mix of colorful foods: fruits, veggies, whole grains, beans, nuts, seeds and dairy. Different colors bring different pals!</p></div>
  <div class="card fun"><h2>🤔 Why A, B, C, D, E… then K?</h2><p>F, G, H and friends were once on the list, but scientists later found they weren't true vitamins and kicked them off. K got its letter from the German word for clotting. Alphabet drama!</p></div>
  <div class="card warn"><h2>⚠️ More isn't always better</h2><p>Supplements can help some people, but big doses can cause problems. Always check with a doctor or pharmacist first.</p></div>
</div>
""" + FOOT
write("index.html", home)

# ---------- B hub ----------
hub = head("The B Vitamins: Meet the B-Team | VitaPals",
           "All 8 B vitamins in one place: B1, B2, B3, B5, B6, B7, B9 and B12. What each does, where to find it, and fun facts.",
           "/vitamin-b/", "vitamin-b") + tabs("B") + f"""
<p class="crumbs"><a href="/">Home</a> › The B-Team</p>
<section class="hero" style="--c:{B_HUB['color']}">
  {pal(B_HUB, 130, decorative=False)}
  <div>
    <p class="kicker">Vitamin B · 8 vitamins</p>
    <h1>The B-Team 🐝</h1>
    <p class="lead">Eight tiny vitamins with very big jobs. They turn food into energy, keep your brain sharp and help build your blood.</p>
    <span class="badge">💧 Water-soluble</span>
  </div>
</section>

<h2 class="sec">Pick a B 👇</h2>
<div class="grid">{"".join(vcard(v) for v in BS)}</div>

<h2 class="sec">What the B-Team does for you</h2>
{perks([
 ["⚡","Energy from food","They turn breakfast into get-up-and-go."],
 ["🧠","Brain & nerves","They keep your body's wiring humming."],
 ["🩸","Healthy blood","B9 and B12 help build red blood cells."],
 ["😊","Mood & sleep","B6 helps make feel-good brain chemicals."],
 ["✨","Skin, hair & eyes","B2, B3 and B7 help you glow."],
 ["🧬","DNA & new cells","B9 and B12 are your body's builders."],
 ["👶","Healthy pregnancies","Folate helps babies grow strong."]
])}

<div class="cards">
  <div class="card note"><h2>🥗 Good news</h2><p>Most people get enough B vitamins from a varied diet. Whole grains, beans, leafy greens, nuts, eggs and dairy are the all-stars.</p></div>
  <div class="card fun"><h2>🤔 Wait, where's B4? B8?</h2><p>Some numbers were once called B vitamins, but scientists later found they weren't truly vitamins after all. They got kicked off the team. Harsh, but fair.</p></div>
  <div class="card"><h2>💧 Use it or lose it</h2><p>B vitamins dissolve in water, so your body flushes out extras instead of storing them (B12 is the exception). That's why you need a steady supply from food.</p></div>
</div>
""" + FOOT
write("vitamin-b/index.html", hub)

# ---------- Vitamin pages ----------
for i, v in enumerate(V):
    isb = v["id"].startswith("B")
    prev = V[i - 1] if i > 0 else None
    nxt = V[i + 1] if i < len(V) - 1 else None
    title = f"Vitamin {v['id']} ({v['name']}): Benefits, Foods & Fun Facts | VitaPals"
    desc = f"Vitamin {v['id']}, {v['nick']}: {v['job']} Learn the best foods, signs you're low and how much you need."
    crumbs = f'<a href="/">Home</a> › ' + (f'<a href="/vitamin-b/">The B-Team</a> › ' if isb else "") + f"Vitamin {e(v['id'])}"
    badge = "💧 Water-soluble" if v["type"] == "water" else "🧈 Fat-soluble"
    warn_cls = "note" if v.get("warnTitle") else "warn"
    p = head(title, desc, url(v), slug(v)) + tabs("B" if isb else v["id"], v["id"] if isb else None) + f"""
<p class="crumbs">{crumbs}</p>
<section class="hero" style="--c:{v['color']}">
  {pal(v, 130, decorative=False)}
  <div>
    <p class="kicker">Vitamin {e(v['id'])} · {e(v['name'])}</p>
    <h1>{e(v['nick'])}</h1>
    <p class="lead">{e(v['job'])}</p>
    <span class="badge">{badge}</span>
  </div>
</section>
<div class="cards">
  <div class="card"><h2>💪 Superpowers</h2><ul>{"".join(f"<li>{e(x)}</li>" for x in v['powers'])}</ul></div>
  <div class="card"><h2>🍽️ Find me in</h2><div class="chips">{"".join(f'<div class="chip"><span aria-hidden="true">{f[0]}</span>{e(f[1])}</div>' for f in v['foods'])}</div></div>
  <div class="card"><h2>🪫 Running low? You might notice</h2><ul>{"".join(f"<li>{e(x)}</li>" for x in v['low'])}</ul></div>
  <div class="card"><h2>📏 How much do I need?</h2><p>{e(v['amount'])}</p></div>
  <div class="card fun"><h2>🤓 Fun fact</h2><p>{e(v['fun'])}</p></div>
  <div class="card {warn_cls}"><h2>{e(v.get('warnTitle', '⚠️ Heads-up'))}</h2><p>{e(v['warn'])}</p></div>
</div>
<p class="sources">📚 Source: <a href="https://ods.od.nih.gov/factsheets/{v['nih']}/" rel="noopener">NIH Office of Dietary Supplements — Vitamin {e(v['id'])} fact sheet</a>. Amounts are general daily needs for healthy adults. Last reviewed {REVIEWED}.</p>
<div class="pager">
  {f'<a href="{url(prev)}"><small>← Previous</small>{e(prev["id"])} {e(prev["nick"])}</a>' if prev else '<a href="/"><small>← Back</small>Home</a>'}
  {f'<a href="{url(nxt)}"><small>Next →</small>{e(nxt["id"])} {e(nxt["nick"])}</a>' if nxt else '<a href="/"><small>Done! →</small>Home</a>'}
</div>
""" + FOOT
    write(f"{slug(v)}/index.html", p)

# ---------- About ----------
about = head("About VitaPals", "VitaPals is a friendly, simple guide to vitamins for all ages: what they do, where to find them, and why they matter.",
             "/about/", "home") + tabs("about") + """
<p class="crumbs"><a href="/">Home</a> › About</p>
<section class="hero center"><p class="kicker">About</p><h1>Hi, we're VitaPals! 💊</h1>
<p class="lead">Vitamins can sound like a science exam. We think they should feel more like meeting new friends.</p></section>
<div class="prose">
  <h2>What is this site?</h2>
  <p>VitaPals explains vitamins in plain, friendly language, with a little humor, for kids, parents and grandparents alike. Each vitamin gets one simple page: what it does, where to find it, signs you might be low, and a fun fact.</p>
  <h2>Where does the information come from?</h2>
  <p>Our facts and daily amounts are based on the <a href="https://ods.od.nih.gov/factsheets/list-VitaminsMinerals/" rel="noopener">NIH Office of Dietary Supplements</a> fact sheets. Each page links to its source.</p>
  <h2>Is this medical advice?</h2>
  <p>Nope. VitaPals is for learning and curiosity. Everyone's body is different, so please talk to a doctor, dietitian or pharmacist before starting any supplement or changing your diet for a health reason.</p>
  <h2>What's next?</h2>
  <p>Minerals like iron, calcium and zinc are on our wish list. Stay tuned!</p>
</div>
""" + FOOT
write("about/index.html", about)

# ---------- 404 ----------
nf = head("Page not found | VitaPals", "Oops, this page wandered off.", "/404.html", "home") + tabs("none") + f"""
<section class="hero center"><p class="kicker">Error 404</p><h1>Oops! This pal wandered off 🙈</h1>
<div class="squad">{pal(BYID['C'], 70)}</div>
<p class="lead">We couldn't find that page. Maybe it went to get some sunshine with Vitamin D.</p>
<a class="btn" href="/">Take me home</a></section>
""" + FOOT
write("404.html", nf)

# ---------- sitemap + robots ----------
paths = ["/", "/vitamin-b/"] + [url(v) for v in V] + ["/about/"]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>\n" for p in paths) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

# ---------- favicon ----------
write("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
      '<rect x="14" y="2" width="36" height="60" rx="18" fill="#ff7a59"/>'
      '<path d="M14 32H50V44A18 18 0 0 1 14 44Z" fill="#fff" opacity=".3"/>'
      '<circle cx="25" cy="22" r="4.5" fill="#fff"/><circle cx="39" cy="22" r="4.5" fill="#fff"/>'
      '<circle cx="25.5" cy="22.5" r="2.4" fill="#2b2340"/><circle cx="39.5" cy="22.5" r="2.4" fill="#2b2340"/>'
      '<path d="M26 30q6 6 12 0" stroke="#2b2340" stroke-width="2.6" fill="none" stroke-linecap="round"/></svg>\n')

# ---------- share-image source pages (rendered to PNG by _src/render.js) ----------
og_items = [("home", None), ("vitamin-b", B_HUB)] + [(slug(v), v) for v in V]
(ROOT / "_src" / "og.json").write_text(json.dumps([
    {"name": n,
     "svg": pal(v, 300) if v else "".join(pal(x, 120) for x in FAMILY),
     "kicker": ("Vitamin " + v["id"] + (" · " + v["name"] if v is not B_HUB else " · 8 vitamins")) if v else "Vitamins made easy",
     "title": v["nick"] if v else "Meet your VitaPals 👋",
     "color": v["color"] if v else "#ff7a59",
     "lead": (v.get("job") or "Eight tiny vitamins with very big jobs.") if v else "13 tiny vitamins with very big jobs. Simple, friendly and a little bit funny."}
    for n, v in og_items], ensure_ascii=False), encoding="utf-8")

print(f"Built {len(paths)} pages + 404, sitemap, robots, favicon.")
