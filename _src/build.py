#!/usr/bin/env python3
"""VitaPals static site builder.

Content lives in:
  _src/vitamins.json  - names, forms, sub-types, fun facts
  _src/details.json   - adult content: needs, limits, food tables, risk, supplements, myths, FAQ
  _src/guides.json    - life-stage guides
Run:  python3 _src/build.py
Every page is plain HTML (search engines and link previews see the full content).
Folders starting with "_" are not published by GitHub Pages.
"""
import json, html, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_src"
SITE = "https://myvitapals.com"
REVIEWED = "October 2026"
TODAY = datetime.date.today().isoformat()
YEAR = datetime.date.today().year
ASSET_V = "7"

V = json.loads((SRC / "vitamins.json").read_text(encoding="utf-8"))
D = json.loads((SRC / "details.json").read_text(encoding="utf-8"))
G = json.loads((SRC / "guides.json").read_text(encoding="utf-8"))
BYID = {v["id"]: v for v in V}
BS = [v for v in V if v["id"].startswith("B")]
B_HUB = {"id": "B", "color": "#ef476f", "text": "#fff", "prop": "🐝", "nick": "The B-Team", "name": "8 B vitamins"}
FAMILY = [BYID["A"], B_HUB, BYID["C"], BYID["D"], BYID["E"], BYID["K"]]

e = lambda s: html.escape(str(s), quote=True)
slug = lambda v: f"vitamin-{v['id'].lower()}"
url = lambda v: f"/{slug(v)}/"
suburl = lambda pv, s: f"{url(pv)}{s['slug']}/"
gurl = lambda g: f"/guides/{g['slug']}/"
txt = lambda v: v.get("text", "#fff")
subpal = lambda s: {"id": s["label"], "color": s["color"], "text": txt(s), "prop": s["prop"]}
vname = lambda v: f"Vitamin {v['id']}"
nih = lambda v: f"https://ods.od.nih.gov/factsheets/{v['nih'].replace('Consumer', 'HealthProfessional')}/"


def pal(v, w, decorative=True, prop=True):
    label = 'aria-hidden="true"' if decorative else f'role="img" aria-label="Vitamin {e(v["id"])} icon"'
    fs = 24 if len(v["id"]) > 2 else (28 if len(v["id"]) == 2 else 40)
    c = v["color"]
    return (f'<svg viewBox="0 0 120 160" width="{w}" height="{round(w*4/3)}" {label}>'
            f'<path d="M22 88q-16-2-18-20" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<path d="M98 88q16-6 16-26" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<rect x="22" y="12" width="76" height="136" rx="38" fill="{c}"/>'
            f'<path d="M22 80H98V110A38 38 0 0 1 22 110Z" fill="#fff" opacity=".22"/>'
            f'<circle cx="47" cy="56" r="7.5" fill="#fff"/><circle cx="73" cy="56" r="7.5" fill="#fff"/>'
            f'<circle cx="48" cy="57" r="3.8" fill="#17201b"/><circle cx="74" cy="57" r="3.8" fill="#17201b"/>'
            f'<path d="M50 68q10 10 20 0" stroke="#17201b" stroke-width="3" fill="none" stroke-linecap="round"/>'
            f'<text x="60" y="{128 if fs == 40 else 122}" text-anchor="middle" font-family="Inter,sans-serif" font-weight="700" font-size="{fs}" fill="{txt(v)}">{e(v["id"])}</text>'
            + (f'<text x="96" y="22" font-size="24" text-anchor="middle">{v["prop"]}</text>' if prop else "") + '</svg>')


LOGO = ('<svg viewBox="0 0 64 88" aria-hidden="true"><rect x="8" y="2" width="48" height="84" rx="24" fill="#1e6b52"/>'
        '<path d="M8 44H56V62A24 24 0 0 1 8 62Z" fill="#7cc4a4"/></svg>')


def head(title, desc, path, og="home", extra=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta name="theme-color" content="#faf7f2">
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
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css?v={ASSET_V}">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""


def header(section="", vit=None, sub=None):
    links = [("vitamins", "/#vitamins", "Vitamins"), ("guides", "/guides/", "Guides"),
             ("finder", "/tools/food-finder/", "Food finder"), ("check", "/tools/vitamin-check/", "Vitamin check"),
             ("about", "/about/", "About")]
    nav = "".join(f'<a href="{h}"{" class=on" if section == k else ""}>{t}</a>' for k, h, t in links)
    vit_links = "".join(f'<a href="{url(v)}">{e(vname(v))}{" · " + e(v["name"].split(" (")[0]) if v["id"].startswith("B") else ""}</a>' for v in V)
    guide_links = "".join(f'<a href="{gurl(g)}">{e(g["title"])}</a>' for g in G)
    menu = f"""<details class="menu"><summary>Menu</summary><div class="panel">
<h4>Tools</h4><a href="/tools/vitamin-check/">🧭 2-minute vitamin check</a><a href="/tools/food-finder/">🔎 Food finder</a>
<h4>Guides</h4>{guide_links}
<h4>Vitamins</h4><div class="grid2">{vit_links}</div>
<h4>More</h4><a href="/">Home</a><a href="/about/">About &amp; how we write</a></div></details>"""
    strip = ""
    if vit:
        cur = "B" if vit.startswith("B") else vit
        items = []
        for v in FAMILY:
            on = " class=on" if v["id"] == cur else ""
            items.append(f'<a href="{url(v)}"{on}><i style="--c:{v["color"]}"></i>Vitamin {e(v["id"])}</a>')
        strip = f'<nav class="strip" aria-label="Vitamins">{"".join(items)}</nav>'
        if cur == "B":
            s = [f'<a href="/vitamin-b/"{" class=on" if vit == "B" else ""}>All B vitamins</a>']
            s += [f'<a href="{url(b)}"{" class=on" if vit == b["id"] else ""}><i style="--c:{b["color"]}"></i>{e(b["id"])} · {e(b["name"].split(" (")[0])}</a>' for b in BS]
            strip += f'<nav class="strip sub" aria-label="B vitamins">{"".join(s)}</nav>'
        elif BYID[cur].get("subs"):
            pv = BYID[cur]
            s = [f'<a href="{url(pv)}"{" class=on" if not sub else ""}>Overview</a>']
            s += [f'<a href="{suburl(pv, x)}"{" class=on" if sub == x["slug"] else ""}><i style="--c:{x["color"]}"></i>{e(x["tab"])}</a>' for x in pv["subs"]]
            strip += f'<nav class="strip sub" aria-label="Types of vitamin {e(cur)}">{"".join(s)}</nav>'
    return f"""
<header class="site-header"><div class="wrap">
  <div class="bar"><a class="logo" href="/" aria-label="VitaPals home">{LOGO}<span>Vita<b>Pals</b></span></a>
  <nav class="nav" aria-label="Main">{nav}</nav>{menu}</div>
  {strip}
</div></header>
<main id="main"><div class="wrap">"""


def footer(scripts=""):
    vit = "".join(f'<a href="{url(v)}">{e(vname(v))}</a>' for v in V[:7])
    vit2 = "".join(f'<a href="{url(v)}">{e(vname(v))}</a>' for v in V[7:])
    gd = "".join(f'<a href="{gurl(g)}">{e(g["title"])}</a>' for g in G)
    return f"""
</div></main>
<footer class="site"><div class="wrap">
  <div class="cols">
    <div><h4>Vitamins</h4>{vit}</div><div><h4>&nbsp;</h4>{vit2}</div>
    <div><h4>Guides</h4>{gd}</div>
    <div><h4>Tools</h4><a href="/tools/vitamin-check/">Vitamin check</a><a href="/tools/food-finder/">Food finder</a><h4 style="margin-top:14px">VitaPals</h4><a href="/about/">About &amp; how we write</a></div>
  </div>
  <p class="disc">VitaPals is for general education, not medical advice. Facts are based on the NIH Office of Dietary Supplements. Talk to a doctor, dietitian or pharmacist before starting a supplement, especially if you're pregnant, take medicines or have a health condition.</p>
  <p class="disc">© {YEAR} VitaPals · Last reviewed {REVIEWED}</p>
</div></footer>
<script src="/assets/app.js?v={ASSET_V}" defer></script>{scripts}
</body>
</html>
"""


def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def dvbar(pct):
    return f'<div class="dv"><div class="b"><span style="width:{min(pct, 100)}%"></span></div><em>{pct}%</em></div>'


def food_table(d):
    rows = "".join(f'<tr><td>{e(f)}<small>{e(s)}</small></td><td class="amt">{e(a)}</td><td>{dvbar(p)}</td></tr>' for f, s, a, p in d["table"])
    return (f'<table class="foods"><thead><tr><th>Food</th><th>Amount</th><th>% Daily Value</th></tr></thead><tbody>{rows}</tbody></table>'
            f'<p class="tnote">% Daily Value is based on {e(d["dv"])} for adults (US FDA). Data: NIH Office of Dietary Supplements.'
            + (f' {e(d["tableNote"])}' if d.get("tableNote") else "") + "</p>")


def jsonld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>\n'


# ------------------------------------------------------------------ search index
INDEX = []
for v in V:
    INDEX.append({"t": f"{vname(v)} ({v['name']})", "u": url(v), "k": "Vitamin", "s": " ".join([v["nick"], v["job"]] + [f[1] for f in v["foods"]] + [f[0] for f in v.get("forms", [])])})
    for s in v.get("subs", []):
        INDEX.append({"t": f"{s['tab']} · {s['name']}", "u": suburl(v, s), "k": f"Vitamin {v['id']} type", "s": s["job"]})
for g in G:
    INDEX.append({"t": g["title"], "u": gurl(g), "k": "Guide", "s": g["card"]})
INDEX += [{"t": "2-minute vitamin check", "u": "/tools/vitamin-check/", "k": "Tool", "s": "quiz am I low deficient test"},
          {"t": "Food finder", "u": "/tools/food-finder/", "k": "Tool", "s": "which foods vitamins search"}]
FOODS = []
for v in V:
    d = D[v["id"]]
    for f, s, a, p in d["table"]:
        FOODS.append({"f": f, "s": s, "a": a, "p": p, "v": v["id"], "u": url(v), "c": v["color"]})
    for f in d["indian"]:
        FOODS.append({"f": f, "s": "", "a": "", "p": None, "v": v["id"], "u": url(v), "c": v["color"], "in": 1})
write("assets/search.json", json.dumps(INDEX, ensure_ascii=False))
write("assets/foods.json", json.dumps(FOODS, ensure_ascii=False))

SEARCH = ('<div class="search" data-search><span class="ico" aria-hidden="true">🔍</span>'
          '<input type="search" placeholder="Search a vitamin, food or question… e.g. B12, spinach, tired" aria-label="Search VitaPals" autocomplete="off">'
          '<ul class="results" role="listbox"></ul></div>')

# ------------------------------------------------------------------ home
ALLMYTHS = [(m, f, v["id"]) for v in V for m, f in D[v["id"]].get("myths", [])]
featured = [(D[k]["myths"][0][0], D[k]["myths"][0][1], k) for k in ("C", "D", "B12")]
questions = [("Do vegetarians need a B12 supplement?", "/vitamin-b12/#faq"),
             ("Vitamin D3 or D2: which is better?", "/vitamin-d/d3/"),
             ("How much vitamin C is too much?", "/vitamin-c/#supplements"),
             ("Should I take folic acid before pregnancy?", "/guides/pregnancy/"),
             ("Can biotin mess up blood tests?", "/vitamin-b7/#supplements"),
             ("Why am I always tired?", "/guides/tired/"),
             ("Which foods have the most vitamin K?", "/vitamin-k/#foods")]
water = [v for v in V if v["type"] == "water"]
fat = [v for v in V if v["type"] == "fat"]
vrow = lambda v: (f'<a class="vrow" href="{url(v)}">{pal(v, 30, prop=False)}<div><strong>{e(vname(v))} <small style="color:var(--muted);font-weight:500">· {e(v["name"])}</small></strong>'
                  f'<span>{e(v["job"])}</span></div><em>{e(D[v["id"]]["needShort"].replace(" a day", "/day"))}</em></a>')
home = head("VitaPals — Vitamins Explained Simply, Food First",
            "What each vitamin does, which foods have it, how much you need and whether you need a supplement. Plain language, real numbers from NIH.",
            "/", "home") + header("home") + f"""
<section class="hero-home"><div class="hero-grid"><div>
  <p class="eyebrow">Vitamins, explained simply</p>
  <h1>Know what your body needs, and where to get it.</h1>
  <p class="lede">What each vitamin does, the foods that have the most, how much you need, and when a supplement actually makes sense. Plain language, with real numbers from the NIH.</p>
  {SEARCH}
  <div class="ctas"><a class="btn" href="/tools/vitamin-check/">Take the 2-minute vitamin check</a><a class="btn ghost" href="/tools/food-finder/">Find foods by vitamin</a></div>
  <div class="trust"><span>Based on NIH fact sheets</span><span>Food first, supplements second</span><span>US &amp; Indian foods</span><span>Reviewed {REVIEWED}</span></div>
</div><aside class="hero-aside" aria-label="Most read">
  <div class="squad" aria-hidden="true">{"".join(pal(x, 46, prop=False) for x in FAMILY)}</div>
  <h3>Most people ask about</h3>
  <ul class="qlist">{"".join(f'<li><a href="{u}">{t}</a></li>' for t, u in [("Vitamin B12 for vegetarians", "/vitamin-b12/"), ("Vitamin D: am I getting enough?", "/vitamin-d/"), ("Folic acid before pregnancy", "/guides/pregnancy/"), ("Foods highest in vitamin C", "/vitamin-c/#foods")])}</ul>
</aside></div>
</section>

<section class="block">
  <div class="head-row"><div><h2>Start with your situation</h2><p>Different stages of life need different vitamins.</p></div></div>
  <div class="cards">{"".join(f'<a class="card" href="{gurl(g)}"><div class="ic" aria-hidden="true">{g["icon"]}</div><h3>{e(g["title"])}</h3><p>{e(g["card"])}</p></a>' for g in G)}</div>
</section>

<section class="block" id="vitamins">
  <div class="head-row"><div><h2>All 13 vitamins</h2><p>Tap any vitamin for foods, daily needs, who's at risk and supplement advice.</p></div></div>
  <h3 style="margin:6px 0 10px">💧 Water-soluble <small style="font-family:var(--sans);font-weight:400;color:var(--muted);font-size:15px">· your body doesn't store much, so you need them regularly</small></h3>
  <div class="vlist">{"".join(vrow(v) for v in water)}</div>
  <h3 style="margin:22px 0 10px">🫒 Fat-soluble <small style="font-family:var(--sans);font-weight:400;color:var(--muted);font-size:15px">· stored in your body, so too much from supplements can build up</small></h3>
  <div class="vlist">{"".join(vrow(v) for v in fat)}</div>
</section>

<section class="block split">
  <div><h2 style="margin-bottom:10px">Popular questions</h2><ul class="qlist">{"".join(f'<li><a href="{u}">{e(q)}</a></li>' for q, u in questions)}</ul></div>
  <div><h2 style="margin-bottom:10px">Myth vs fact</h2><div id="myth-week" style="display:grid;gap:12px">
    {"".join(f'<div class="myth"><div class="m"><b>Myth</b>{e(m)}</div><div class="f"><b>Fact</b>{e(f)} <a href="/vitamin-{i.lower()}/#myths">Vitamin {e(i)} →</a></div></div>' for m, f, i in featured)}
  </div></div>
</section>

<section class="block band">
  <div><h2>Not sure where to start?</h2><p>Answer 10 quick questions about what you eat and your lifestyle. We'll show which vitamins deserve a closer look, and the foods that help. Nothing is stored or sent anywhere.</p></div>
  <div><a class="btn" href="/tools/vitamin-check/">Start the vitamin check →</a></div>
</section>
""" + footer('\n<script type="application/json" id="myths-data">' + json.dumps([{"m": m, "f": f, "v": i} for m, f, i in ALLMYTHS], ensure_ascii=False) + "</script>")
write("index.html", home)


# ------------------------------------------------------------------ vitamin pages
def forms_html(v):
    return ('<ul class="forms">' + "".join(
        f'<li><strong>{e(f[0])}</strong><span class="ftag t-{f[2].lower().replace(" ", "-")}">{e(f[2])}</span><p>{e(f[1])}</p></li>' for f in v["forms"]) + "</ul>")


for i, v in enumerate(V):
    d = D[v["id"]]
    isb = v["id"].startswith("B")
    prev = V[i - 1] if i > 0 else None
    nxt = V[i + 1] if i < len(V) - 1 else None
    subs = v.get("subs") or []
    title = f"Vitamin {v['id']} ({v['name'].split(' (')[0]}): Foods, Daily Needs & Supplements | VitaPals"
    desc = f"{vname(v)}: {v['job']} Top foods with amounts, how much you need ({d['needShort']}), who's at risk, and when a supplement makes sense."
    crumbs = '<a href="/">Home</a> › ' + ('<a href="/vitamin-b/">B vitamins</a> › ' if isb else "") + e(vname(v))
    soluble = "Water-soluble" if v["type"] == "water" else "Fat-soluble"
    faq_ld = jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]})
    subpick = ""
    if subs:
        subpick = '<div class="subpick">' + "".join(
            f'<a class="vrow" href="{suburl(v, s)}">{pal(subpal(s), 30, prop=False)}<div><strong>{e(s["tab"])}</strong><span>{e(s["job"])}</span></div></a>' for s in subs) + "</div>"
    related = [g for g in G if v["id"] in g["sources"]]
    p = head(title, desc, url(v), slug(v), faq_ld) + header("vitamins", v["id"]) + f"""
<p class="crumbs">{crumbs}</p>
<div class="vhead">{pal(v, 64, decorative=False)}<div>
  <p class="kicker">{e(v['name'])} · {soluble}</p>
  <h1>{e(vname(v))}</h1>
  <p class="lede">{e(v['job'])}</p>
  <span class="nick">{v['prop']} Nickname: {e(v['nick'])}</span>
</div></div>
<div class="glance" id="glance">
  <div><small>Daily need (adults)</small><strong>{e(d['needShort'])}</strong></div>
  <div><small>Upper limit</small><strong>{e(d['ulShort'])}</strong></div>
  <div><small>Best foods</small><strong>{e(d['top3'])}</strong></div>
  <div><small>Pay attention if</small><strong>{e(d['risk'][0][0])}</strong></div>
</div>
<nav class="jump" aria-label="On this page"><a href="#foods">Foods</a><a href="#needs">How much</a><a href="#risk">Who's at risk</a><a href="#signs">Signs of low levels</a><a href="#supplements">Supplements</a><a href="#forms">Forms</a><a href="#myths">Myths</a><a href="#faq">FAQ</a></nav>
{subpick}

<section class="sec two">
  <div><h2>What it does</h2><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in v['powers'])}</ul></div>
  <div class="note warm"><h3>🤓 Did you know?</h3><p>{e(v['fun'])}</p></div>
</section>

<section class="sec" id="foods">
  <h2>Top food sources</h2>
  <p class="sub">Per typical serving, with how much of your daily need it covers.</p>
  {food_table(d)}
  <div class="two" style="margin-top:16px">
    <div class="note"><h3>🇮🇳 Also great in Indian kitchens</h3><div class="chips">{"".join(f"<span>{e(x)}</span>" for x in d['indian'])}</div></div>
    <div class="note warm"><h3>👩‍🍳 Kitchen tips</h3><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in d['tips'])}</ul></div>
  </div>
</section>

<section class="sec two" id="needs">
  <div><h2>How much do you need?</h2>
    <table class="needs">{"".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in d['needs'])}</table>
    <p class="tnote">Recommended daily amounts for adults, from the US Food and Nutrition Board.</p></div>
  <div class="note {"warm" if d["ulShort"] == "None set" else "warn"}" style="align-self:start"><h3>{"ℹ️" if d["ulShort"] == "None set" else "⚠️"} Upper limit</h3><p>{e(d['ul'])}</p></div>
</section>

<section class="sec" id="risk">
  <h2>Who's most at risk of running low?</h2>
  <div class="risk" style="--c:{v['color']}">{"".join(f"<div><strong>{e(a)}</strong><span>{e(b)}</span></div>" for a, b in d['risk'])}</div>
</section>

<section class="sec two" id="signs">
  <div><h2>Signs you might be low</h2><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in v['low'])}</ul><p class="tnote">{e(d['lowNote'])}</p></div>
  <div class="note"><h3>🩺 When to see a doctor</h3><p>These signs have many possible causes. If they last more than a couple of weeks, see a doctor. A simple blood test can often check your levels. Don't guess with high-dose supplements.</p></div>
</section>

<section class="sec" id="supplements">
  <h2>Supplements: do you need one?</h2>
  <div class="two">
    <div class="note"><h3>When it helps</h3><p>{e(d['suppWhen'])}</p></div>
    <div class="note warm"><h3>Choosing one</h3><p>{e(d['suppPick'])}</p></div>
  </div>
  <div class="note warn" style="margin-top:14px"><h3>💊 Medicine interactions</h3><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in d['interactions'])}</ul><p style="margin-top:8px">Always tell your doctor and pharmacist about any supplements you take.</p></div>
</section>

<section class="sec" id="forms">
  <h2>Forms of {e(vname(v))}</h2>
  <p class="sub">{e(v['formsIntro'])}</p>
  {forms_html(v)}
</section>

<section class="sec" id="myths">
  <h2>Myths vs facts</h2>
  <div class="mythgrid">{"".join(f'<div class="myth"><div class="m"><b>Myth</b>{e(m)}</div><div class="f"><b>Fact</b>{e(f)}</div></div>' for m, f in d['myths'])}</div>
</section>

<section class="sec" id="faq">
  <h2>Frequently asked questions</h2>
  {"".join(f'<details class="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in d['faq'])}
</section>
""" + (f"""<section class="sec"><h2>Related guides</h2><div class="cards">{"".join(f'<a class="card" href="{gurl(g)}"><div class="ic">{g["icon"]}</div><h3>{e(g["title"])}</h3><p>{e(g["card"])}</p></a>' for g in related)}</div></section>""" if related else "") + f"""
<p class="sources">Sources: <a href="{nih(v)}" rel="noopener">NIH Office of Dietary Supplements, {e(vname(v))} fact sheet for health professionals</a>. Daily needs are for healthy adults. Last reviewed {REVIEWED}. This page is for education, not medical advice.</p>
<div class="pager">
  {f'<a href="{url(prev)}"><small>← Previous</small>{e(vname(prev))}</a>' if prev else '<a href="/"><small>← Back</small>Home</a>'}
  {f'<a href="{url(nxt)}"><small>Next →</small>{e(vname(nxt))}</a>' if nxt else '<a href="/"><small>Done →</small>Home</a>'}
</div>
""" + footer()
    write(f"{slug(v)}/index.html", p)

    for j, s in enumerate(subs):
        sp = subs[j - 1] if j > 0 else None
        sn = subs[j + 1] if j < len(subs) - 1 else None
        stitle = (f"Vitamin {s['tab']} ({s['name']}): What It Is, Foods & Labels | VitaPals" if s["tab"].startswith(v["id"])
                  else f"{s['tab']}, a Form of Vitamin {v['id']}: Foods & Labels | VitaPals")
        sdesc = f"{s['tab']}: {s['job']} Where to find it and how to read supplement labels."
        back = f'<a href="{url(v)}"><small>← Back to</small>{e(vname(v))} overview</a>'
        sp_html = head(stitle, sdesc, suburl(v, s), f"{slug(v)}-{s['slug']}") + header("vitamins", v["id"], s["slug"]) + f"""
<p class="crumbs"><a href="/">Home</a> › <a href="{url(v)}">{e(vname(v))}</a> › {e(s['tab'])}</p>
<div class="vhead">{pal(subpal(s), 64, decorative=False)}<div>
  <p class="kicker">{e(vname(v))} · {e(s['name'])}</p>
  <h1>{e(s['tab'])}</h1>
  <p class="lede">{e(s['job'])}</p>
  <span class="nick">{s['prop']} Nickname: {e(s['nick'])}</span>
</div></div>
<section class="sec two">
  <div><h2>What makes it special</h2><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in s['what'])}</ul></div>
  <div><h2>Where to find it</h2><div class="chips">{"".join(f'<span>{f[0]} {e(f[1])}</span>' for f in s['foods'])}</div></div>
</section>
<section class="sec two">
  <div class="note"><h3>🏷️ Label decoder</h3><p>{e(s['labelTip'])}</p></div>
  <div class="note warm"><h3>🤓 Did you know?</h3><p>{e(s['fun'])}</p></div>
</section>
<section class="sec two">
  <div class="note warn"><h3>⚠️ Heads-up</h3><p>{e(s['warn'])}</p></div>
  <div class="note"><h3>📏 How much {e(vname(v))} do you need?</h3><p>{e(D[v['id']]['needShort'])} for most adults. Upper limit: {e(D[v['id']]['ulShort'])}.</p><p><a href="{url(v)}#foods">See top foods &amp; full details →</a></p></div>
</section>
<p class="sources">Sources: <a href="{nih(v)}" rel="noopener">NIH Office of Dietary Supplements, {e(vname(v))} fact sheet for health professionals</a>. Last reviewed {REVIEWED}.</p>
<div class="pager">
  {f'<a href="{suburl(v, sp)}"><small>← Previous</small>{e(sp["tab"])}</a>' if sp else back}
  {f'<a href="{suburl(v, sn)}"><small>Next →</small>{e(sn["tab"])}</a>' if sn else back.replace("← Back to", "Back to →")}
</div>
""" + footer()
        write(f"{slug(v)}/{s['slug']}/index.html", sp_html)

# ------------------------------------------------------------------ B hub
hub = head("B Vitamins: All 8 Explained — Foods, Needs & Who Needs More | VitaPals",
           "The 8 B vitamins in one place: what each does, how much you need, the best foods, and who should pay attention.",
           "/vitamin-b/", "vitamin-b") + header("vitamins", "B") + f"""
<p class="crumbs"><a href="/">Home</a> › B vitamins</p>
<div class="vhead">{pal(B_HUB, 64, decorative=False)}<div>
  <p class="kicker">8 vitamins · Water-soluble</p><h1>The B vitamins</h1>
  <p class="lead lede">Eight vitamins that work as a team to turn food into energy, keep nerves healthy and build blood cells. Your body doesn't store most of them, so you need a steady supply from food.</p>
</div></div>
<section class="sec"><h2>All 8 at a glance</h2>
<table class="foods"><thead><tr><th>Vitamin</th><th>Daily need</th><th>Best foods</th></tr></thead><tbody>
{"".join(f'<tr><td><a href="{url(b)}"><strong>{e(b["id"])} · {e(b["name"].split(" (")[0])}</strong></a><small>{e(b["job"])}</small></td><td class="amt">{e(D[b["id"]]["needShort"].replace(" a day", ""))}</td><td>{e(D[b["id"]]["top3"])}</td></tr>' for b in BS)}
</tbody></table></section>
<section class="sec two">
  <div class="note"><h3>👀 The two to watch</h3><p><a href="/vitamin-b12/">B12</a> (vegetarians, vegans, adults over 50, metformin or acid-reducer users) and <a href="/vitamin-b9/">folate</a> (anyone who could become pregnant). The others are usually easy to get from food.</p></div>
  <div class="note warm"><h3>🤔 Where are B4, B8, B10 and B11?</h3><p>They were once called B vitamins, but later research showed they weren't true vitamins, or they were the same as others. So the numbering has gaps.</p></div>
</section>
<section class="sec"><h2>B vitamin all-stars</h2><p class="sub">Foods that bring several B vitamins at once.</p>
<div class="chips"><span>🫘 Beans, dals &amp; chickpeas</span><span>🌾 Whole grains &amp; fortified cereal</span><span>🥛 Milk &amp; curd</span><span>🥚 Eggs</span><span>🐟 Fish</span><span>🍄 Mushrooms</span><span>🌻 Sunflower seeds</span><span>🥬 Leafy greens</span></div></section>
""" + footer()
write("vitamin-b/index.html", hub)

# ------------------------------------------------------------------ guides
ulrows = "".join(f'<tr><td><a href="{url(v)}">{e(vname(v))}</a></td><td>{e(D[v["id"]]["needShort"].replace(" a day", ""))}</td><td>{e(D[v["id"]]["ulShort"])}</td></tr>' for v in V)
for g in G:
    keys = "".join(
        f'<a href="{url(BYID[k])}">{pal(BYID[k], 34, prop=False)}<div><strong>{e(vname(BYID[k]))}</strong><span>{e(t)}</span></div></a>' for k, t in g["key"])
    srcs = ", ".join(f'<a href="{nih(BYID[k])}" rel="noopener">{e(vname(BYID[k]))}</a>' for k in g["sources"])
    gp = head(g["seo"] + " | VitaPals", g["card"] + " " + g["intro"][:110], gurl(g)) + header("guides") + f"""
<p class="crumbs"><a href="/">Home</a> › <a href="/guides/">Guides</a> › {e(g['title'])}</p>
<div style="max-width:760px"><p class="kicker" style="font-size:36px;margin:0">{g['icon']}</p><h1>{e(g['title'])}</h1><p class="lede">{e(g['intro'])}</p></div>
<section class="sec"><h2>The vitamins to focus on</h2><div class="gkey">{keys}</div></section>
<section class="sec"><h2>{e(g['plateTitle'])}</h2><div class="plate">{"".join(f"<div><b>{e(a)}</b>{e(b)}</div>" for a, b in g['plate'])}</div></section>
""" + (f"""<section class="sec"><h2>Daily needs and upper limits</h2><table class="ul"><tr><th>Vitamin</th><th>Adults need</th><th>Upper limit</th></tr>{ulrows}</table><p class="tnote">Upper limits are for adults and include food plus supplements unless noted. "None set" doesn't mean megadoses are safe.</p></section>""" if g.get("showUL") else "") + f"""
<section class="sec two">
  <div class="note warm"><h3>📌 Good to know</h3><p>{e(g['beyond'])}</p></div>
  <div class="note"><h3>🩺 Talk to your doctor about</h3><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in g['doctor'])}</ul></div>
</section>
<p class="sources">Sources: NIH Office of Dietary Supplements fact sheets: {srcs}. Last reviewed {REVIEWED}. General education, not medical advice.</p>
""" + footer()
    write(f"guides/{g['slug']}/index.html", gp)

gi = head("Vitamin Guides for Every Stage of Life | VitaPals", "Vitamin guides for vegetarians, adults over 50, pregnancy, kids, supplements and tiredness.", "/guides/") + header("guides") + f"""
<p class="crumbs"><a href="/">Home</a> › Guides</p><h1>Guides</h1><p class="lede">Practical vitamin advice for your stage of life.</p>
<div class="cards" style="margin-top:22px">{"".join(f'<a class="card" href="{gurl(g)}"><div class="ic">{g["icon"]}</div><h3>{e(g["title"])}</h3><p>{e(g["card"])}</p><span class="go">Read guide →</span></a>' for g in G)}</div>
""" + footer()
write("guides/index.html", gi)

# ------------------------------------------------------------------ tools
ff = head("Food Finder: Which Vitamins Are in Your Food? | VitaPals",
          "Search any food, like spinach, eggs, milk or dal, to see which vitamins it's rich in and how much of your daily need it covers.",
          "/tools/food-finder/") + header("finder") + """
<p class="crumbs"><a href="/">Home</a> › Food finder</p>
<div style="max-width:760px"><h1>Food finder</h1><p class="lede">Type a food to see which vitamins it's rich in, and how much of your daily need one serving covers.</p></div>
<div class="tool" style="margin-top:20px" id="food-finder">
  <div class="search"><span class="ico" aria-hidden="true">🔍</span><input id="ff-q" type="search" placeholder="Try spinach, eggs, milk, chickpeas, amla…" aria-label="Search foods" autocomplete="off"></div>
  <div class="pop" id="ff-pop"></div>
  <div id="ff-out" aria-live="polite"></div>
  <noscript><p>The food finder needs JavaScript. You can still browse foods on each vitamin page.</p></noscript>
</div>
<p class="tnote" style="margin-top:12px">Amounts and % Daily Value come from NIH food tables. Foods marked "Indian kitchen" are good everyday sources without an exact NIH value.</p>
""" + footer()
write("tools/food-finder/index.html", ff)

vc = head("2-Minute Vitamin Check: Which Vitamins Should You Watch? | VitaPals",
          "Answer 10 quick questions about your diet and lifestyle to see which vitamins deserve a closer look. Free, private and educational.",
          "/tools/vitamin-check/") + header("check") + """
<p class="crumbs"><a href="/">Home</a> › Vitamin check</p>
<div style="max-width:760px"><h1>2-minute vitamin check</h1><p class="lede">Answer a few questions about how you eat and live. We'll point out which vitamins deserve a closer look, and the foods that help. Your answers stay on your device.</p></div>
<form class="tool" id="vcheck" style="margin-top:20px">
  <fieldset class="q"><legend>1. How do you eat?</legend><div class="opts">
    <label><input type="radio" name="diet" value="omni" checked> I eat meat or fish</label>
    <label><input type="radio" name="diet" value="veg"> Vegetarian (dairy and/or eggs)</label>
    <label><input type="radio" name="diet" value="vegan"> Vegan (no animal foods)</label></div></fieldset>
  <fieldset class="q"><legend>2. Your age</legend><div class="opts">
    <label><input type="radio" name="age" value="u50" checked> Under 50</label>
    <label><input type="radio" name="age" value="50"> 50–70</label>
    <label><input type="radio" name="age" value="71"> Over 70</label></div></fieldset>
  <fieldset class="q"><legend>3. Are you pregnant, breastfeeding or planning a pregnancy?</legend><div class="opts">
    <label><input type="radio" name="preg" value="no" checked> No</label>
    <label><input type="radio" name="preg" value="yes"> Yes</label></div></fieldset>
  <fieldset class="q"><legend>4. How often are you outdoors in daylight (arms or face uncovered)?</legend><div class="opts">
    <label><input type="radio" name="sun" value="often" checked> Most days</label>
    <label><input type="radio" name="sun" value="rare"> Rarely, or mostly covered up</label></div></fieldset>
  <fieldset class="q"><legend>5. Your skin tone</legend><div class="opts">
    <label><input type="radio" name="skin" value="light" checked> Lighter</label>
    <label><input type="radio" name="skin" value="dark"> Medium to darker (makes less vitamin D from sun)</label></div></fieldset>
  <fieldset class="q"><legend>6. Leafy greens, dals or beans</legend><div class="opts">
    <label><input type="radio" name="greens" value="daily" checked> Most days</label>
    <label><input type="radio" name="greens" value="some"> A few times a week</label>
    <label><input type="radio" name="greens" value="rare"> Rarely</label></div></fieldset>
  <fieldset class="q"><legend>7. Fresh fruit or raw veggies (oranges, guava, peppers, tomatoes…)</legend><div class="opts">
    <label><input type="radio" name="fruit" value="daily" checked> Daily</label>
    <label><input type="radio" name="fruit" value="rare"> Rarely</label></div></fieldset>
  <fieldset class="q"><legend>8. Nuts, seeds or nut butters</legend><div class="opts">
    <label><input type="radio" name="nuts" value="often" checked> Several times a week</label>
    <label><input type="radio" name="nuts" value="rare"> Rarely</label></div></fieldset>
  <fieldset class="q"><legend>9. Do you smoke, or have several alcoholic drinks most days?</legend><div class="opts">
    <label><input type="checkbox" name="smoke"> I smoke</label>
    <label><input type="checkbox" name="alcohol"> Several drinks most days</label></div></fieldset>
  <fieldset class="q"><legend>10. Do you take any of these medicines regularly?</legend><div class="opts">
    <label><input type="checkbox" name="metformin"> Metformin (diabetes)</label>
    <label><input type="checkbox" name="acid"> Acid reducers (omeprazole, pantoprazole, famotidine…)</label>
    <label><input type="checkbox" name="warfarin"> Warfarin or another blood thinner</label>
    <label><input type="checkbox" name="seizure"> Seizure medicines</label></div></fieldset>
  <button class="btn" type="submit">See my results</button>
  <div class="res" id="vcheck-out" aria-live="polite"></div>
  <noscript><p>The vitamin check needs JavaScript.</p></noscript>
</form>
<p class="tnote" style="margin-top:12px">This is an educational tool, not a diagnosis. Only a doctor and a blood test can tell you if you're low.</p>
""" + footer()
write("tools/vitamin-check/index.html", vc)

# ------------------------------------------------------------------ about
about = head("About VitaPals & How We Write", "How VitaPals researches, writes and reviews its vitamin information.", "/about/") + header("about") + f"""
<p class="crumbs"><a href="/">Home</a> › About</p>
<div class="prose"><h1>About VitaPals</h1>
<p class="lede">VitaPals explains vitamins in plain language, so you can make sense of what you eat and have better conversations with your doctor.</p>
<h2>Food first</h2><p>Most people can get most vitamins from a varied diet. We show real foods, with real amounts, before we ever talk about supplements. We include everyday US and Indian foods, because that's how many of our readers eat.</p>
<h2>Where our facts come from</h2><p>Daily needs, upper limits, food amounts and medicine interactions come from the <a href="https://ods.od.nih.gov/factsheets/list-VitaminsMinerals/" rel="noopener">NIH Office of Dietary Supplements</a> fact sheets for health professionals, which are based on the US Food and Nutrition Board. Every page links to its source.</p>
<h2>How we keep it current</h2><p>Each page shows when it was last reviewed. We re-check facts against the latest NIH fact sheets when they're updated. Spotted something wrong? We want to know.</p>
<h2>What we don't do</h2><p>We don't diagnose, and we don't recommend specific supplement brands. Our vitamin check is educational. It can point you toward questions to ask, but only a doctor and a blood test can tell you if you're low.</p>
<h2>Medical disclaimer</h2><p>VitaPals is for general education and isn't a substitute for professional medical advice. Talk to a doctor, registered dietitian or pharmacist before starting a supplement, especially if you're pregnant, breastfeeding, take medicines or have a health condition.</p>
</div>
""" + footer()
write("about/index.html", about)

nf = head("Page not found | VitaPals", "This page wandered off.", "/404.html") + header() + f"""
<div style="text-align:center;padding:40px 0">{pal(BYID['C'], 80)}<h1 style="margin-top:12px">This page wandered off</h1>
<p class="lede" style="margin:12px auto 22px">Maybe it went to get some sunshine with vitamin D. Try searching instead:</p>
<div style="display:flex;justify-content:center">{SEARCH}</div><p style="margin-top:22px"><a class="btn" href="/">Go home</a></p></div>
""" + footer()
write("404.html", nf)

# ------------------------------------------------------------------ sitemap, robots, favicon, og
paths = (["/", "/vitamin-b/"] + [p for v in V for p in [url(v)] + [suburl(v, s) for s in v.get("subs", [])]]
         + ["/guides/"] + [gurl(g) for g in G] + ["/tools/food-finder/", "/tools/vitamin-check/", "/about/"])
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>\n" for p in paths) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
write("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect x="16" y="2" width="32" height="60" rx="16" fill="#1e6b52"/><path d="M16 32H48V46A16 16 0 0 1 16 46Z" fill="#7cc4a4"/></svg>\n')

og_items = [("home", None), ("vitamin-b", B_HUB)] + [(slug(v), v) for v in V]
(SRC / "og.json").write_text(json.dumps([
    {"name": n,
     "svg": pal(v, 260) if v else "".join(pal(x, 110) for x in FAMILY),
     "kicker": (("Vitamin " + v["id"] + " · " + v["name"]) if v is not B_HUB else "8 vitamins · water-soluble") if v else "Vitamins, explained simply",
     "title": (vname(v) if v is not B_HUB else "The B vitamins") if v else "Know what your body needs",
     "color": v["color"] if v else "#1e6b52",
     "lead": (D[v["id"]]["needShort"].capitalize() + ". Best foods: " + D[v["id"]]["top3"].lower() + ".") if v and v is not B_HUB else ("Foods, daily needs and supplement advice for all 8." if v else "Foods, daily needs and honest supplement advice. Based on NIH data.")}
    for n, v in og_items] + [
    {"name": f"{slug(v)}-{s['slug']}", "svg": pal(subpal(s), 260), "kicker": f"Vitamin {v['id']} · {s['name']}",
     "title": s["tab"], "color": s["color"], "lead": s["job"]}
    for v in V for s in v.get("subs", [])], ensure_ascii=False), encoding="utf-8")

print(f"Built {len(paths)} pages + 404, sitemap, robots, favicon, search & food data.")
