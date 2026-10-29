#!/usr/bin/env python3
"""VitaPals static site builder.

Content lives in:
  _src/vitamins.json  - names, forms, sub-types, fun facts
  _src/details.json   - adult content: needs, limits, food tables, risk, supplements, myths, FAQ
  _src/guides.json    - life-stage guides
  _src/topics.json    - health topics with evidence badges (inflammation, ...)
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
ASSET_V = "12"

V = json.loads((SRC / "vitamins.json").read_text(encoding="utf-8"))
D = json.loads((SRC / "details.json").read_text(encoding="utf-8"))
G = json.loads((SRC / "guides.json").read_text(encoding="utf-8"))
T = json.loads((SRC / "topics.json").read_text(encoding="utf-8"))
M = json.loads((SRC / "minerals.json").read_text(encoding="utf-8"))
PR = json.loads((SRC / "protein.json").read_text(encoding="utf-8"))
ALL = V + M
BYID = {v["id"]: v for v in ALL}
BS = [v for v in V if v["id"].startswith("B")]
B_HUB = {"id": "B", "color": "#ef476f", "text": "#fff", "prop": "🐝", "nick": "The B-Team", "name": "8 B vitamins"}
FAMILY = [BYID["A"], B_HUB, BYID["C"], BYID["D"], BYID["E"], BYID["K"]]

e = lambda s: html.escape(str(s), quote=True)
slug = lambda v: v.get("slug") or f"vitamin-{v['id'].lower()}"
url = lambda v: f"/{slug(v)}/"
suburl = lambda pv, s: f"{url(pv)}{s['slug']}/"
gurl = lambda g: f"/guides/{g['slug']}/"
turl = lambda t: f"/topics/{t['slug']}/"
purl = lambda s=None: "/protein/" + (f"{s['slug']}/" if s else "")
EV = {"g": ("🟢", "Strong evidence"), "y": ("🟡", "Some evidence"), "w": ("⚪", "Not enough evidence"), "r": ("🔴", "Myth")}
badge = lambda k, labels=None: f'<span class="ev ev-{k}"><i aria-hidden="true">{EV[k][0]}</i>{(labels or {}).get(k, EV[k][1])}</span>'
txt = lambda v: v.get("text", "#fff")
subpal = lambda s: {"id": s["label"], "color": s["color"], "text": txt(s), "prop": s["prop"]}
psubpal = lambda x: {"id": x["prop"], "color": x["color"], "text": txt(x), "prop": x["prop"], "aria": x["tab"]}
vname = lambda v: v.get("label") or f"Vitamin {v['id']}"
ismin = lambda v: v["type"] in ("mineral", "omega")
nih = lambda v: f"https://ods.od.nih.gov/factsheets/{v['nih'].replace('Consumer', 'HealthProfessional')}/"


def pal(v, w, decorative=True, prop=True):
    label = 'aria-hidden="true"' if decorative else f'role="img" aria-label="{e(v.get("aria", "Vitamin " + v["id"]))} icon"'
    lab = v.get("sym", v["id"])
    fs = 24 if len(lab) > 2 else (28 if len(lab) == 2 else 40)
    c = v["color"]
    return (f'<svg viewBox="0 0 120 160" width="{w}" height="{round(w*4/3)}" {label}>'
            f'<path d="M22 88q-16-2-18-20" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<path d="M98 88q16-6 16-26" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>'
            f'<rect x="22" y="12" width="76" height="136" rx="38" fill="{c}"/>'
            f'<path d="M22 80H98V110A38 38 0 0 1 22 110Z" fill="#fff" opacity=".22"/>'
            f'<circle cx="47" cy="56" r="7.5" fill="#fff"/><circle cx="73" cy="56" r="7.5" fill="#fff"/>'
            f'<circle cx="48" cy="57" r="3.8" fill="#17201b"/><circle cx="74" cy="57" r="3.8" fill="#17201b"/>'
            f'<path d="M50 68q10 10 20 0" stroke="#17201b" stroke-width="3" fill="none" stroke-linecap="round"/>'
            f'<text x="60" y="{128 if fs == 40 else 122}" text-anchor="middle" font-family="Inter,sans-serif" font-weight="700" font-size="{fs}" fill="{txt(v)}">{e(v.get("sym", v["id"]))}</text>'
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
<meta name="google-site-verification" content="PWmqsbCTxIDBLfAWZAj158s1Cxm_8TM1bWkIVkYY31g">
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
<link rel="preload" href="/assets/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/fraunces-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css?v={ASSET_V}">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""


def header(section="", vit=None, sub=None, psub=None):
    links = [("vitamins", "/#vitamins", "Vitamins"), ("minerals", "/minerals/", "Minerals"), ("protein", "/protein/", "Protein"), ("topics", "/topics/", "Health topics"), ("guides", "/guides/", "Guides"),
             ("finder", "/tools/food-finder/", "Food finder"), ("check", "/tools/vitamin-check/", "Vitamin check"),
             ("about", "/about/", "About")]
    nav = "".join(f'<a href="{h}"{" class=on" if section == k else ""}>{t}</a>' for k, h, t in links)
    vit_links = "".join(f'<a href="{url(v)}">{e(vname(v))}{" · " + e(v["name"].split(" (")[0]) if v["id"].startswith("B") else ""}</a>' for v in V)
    guide_links = "".join(f'<a href="{gurl(g)}">{e(g["title"])}</a>' for g in G)
    topic_links = "".join(f'<a href="{turl(t)}">{t["icon"]} {e(t["title"])}</a>' for t in T)
    menu = f"""<details class="menu"><summary>Menu</summary><div class="panel">
<h4>Tools</h4><a href="/tools/vitamin-check/">🧭 2-minute vitamin check</a><a href="/tools/food-finder/">🔎 Food finder</a>
<h4>Health topics</h4>{topic_links}<a href="/topics/">All health topics</a>
<h4>Guides</h4>{guide_links}
<h4>Vitamins</h4><div class="grid2">{vit_links}</div>
<h4>Minerals &amp; omega-3</h4><div class="grid2">{"".join(f'<a href="{url(m)}">{e(vname(m))}</a>' for m in M)}<a href="/minerals/">All minerals</a></div>
<h4>Protein</h4><div class="grid2"><a href="/protein/">Protein overview</a>{"".join(f'<a href="{purl(x)}">{e(x["tab"])}</a>' for x in PR["subs"])}</div>
<h4>More</h4><a href="/">Home</a><a href="/about/">About &amp; how we write</a></div></details>"""
    strip = ""
    if vit:
        cur = "B" if vit.startswith("B") else vit
        items = []
        for v in FAMILY:
            on = " class=on" if v["id"] == cur else ""
            items.append(f'<a href="{url(v)}"{on}><i style="--c:{v["color"]}"></i>Vitamin {e(v["id"])}</a>')
        strip = ""
        if cur == "B":
            s = [f'<a href="/vitamin-b/"{" class=on" if vit == "B" else ""}>All B vitamins</a>']
            s += [f'<a href="{url(b)}"{" class=on" if vit == b["id"] else ""}><i style="--c:{b["color"]}"></i>{e(b["id"])} · {e(b["name"].split(" (")[0])}</a>' for b in BS]
            strip += f'<nav class="strip sub" aria-label="B vitamins">{"".join(s)}</nav>'
        elif BYID[cur].get("subs"):
            pv = BYID[cur]
            s = [f'<a href="{url(pv)}"{" class=on" if not sub else ""}>Overview</a>']
            s += [f'<a href="{suburl(pv, x)}"{" class=on" if sub == x["slug"] else ""}><i style="--c:{x["color"]}"></i>{e(x["tab"])}</a>' for x in pv["subs"]]
            strip += f'<nav class="strip sub" aria-label="Types of vitamin {e(cur)}">{"".join(s)}</nav>'
    if section == "protein":
        s = [f'<a href="{purl()}"{" class=on" if not psub else ""}>Overview</a>']
        s += [f'<a href="{purl(x)}"{" class=on" if psub == x["slug"] else ""}><i style="--c:{x["color"]}"></i>{e(x["tab"])}</a>' for x in PR["subs"]]
        strip = f'<nav class="strip sub" aria-label="Types of protein">{"".join(s)}</nav>'
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
    <div><h4>Guides</h4>{gd}<h4 style="margin-top:14px">Health topics</h4>{"".join(f'<a href="{turl(t)}">{e(t["title"])}</a>' for t in T)}</div>
    <div><h4>Minerals</h4>{"".join(f'<a href="{url(m)}">{e(vname(m))}</a>' for m in M)}<h4 style="margin-top:14px">Protein</h4><a href="/protein/">Protein &amp; its sources</a></div>
    <div><h4>Tools</h4><a href="/tools/vitamin-check/">Vitamin check</a><a href="/tools/food-finder/">Food finder</a><h4 style="margin-top:14px">VitaPals</h4><a href="/about/">About &amp; how we write</a></div>
  </div>
  <p class="disc">VitaPals is written for adults aged 20 and over, for general education, not medical advice. Facts are based on the NIH Office of Dietary Supplements. Talk to a doctor, dietitian or pharmacist before starting a supplement, especially if you're pregnant, take medicines or have a health condition.</p>
  <p class="disc">© {YEAR} VitaPals · Last reviewed {REVIEWED}</p>
</div></footer>
<script src="/assets/app.js?v={ASSET_V}" defer></script>{scripts}
</body>
</html>
"""


def fit(*cands, n=155):
    """First candidate that fits a search snippet; else trim the last one at a word boundary."""
    for c in cands:
        if len(c) <= n:
            return c
    c = cands[-1][:n - 1]
    return c[:c.rfind(" ")].rstrip(",;:") + "…"


def topics_for(kind, key):
    return [t for t in T if key in t.get("related", {}).get(kind, [])]


def topic_links_html(ts):
    if not ts:
        return ""
    return ('<section class="sec"><h2>Related health topics</h2><div class="cards">' + "".join(
        f'<a class="card" href="{turl(t)}"><div class="ic" aria-hidden="true">{t["icon"]}</div><h3>{e(t["title"])}</h3><p>{e(t["card"])}</p><span class="go">Read →</span></a>' for t in ts) + "</div></section>")


def write(path, content):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def dvbar(pct):
    return f'<div class="dv"><div class="b"><span style="width:{min(pct, 100)}%"></span></div><em>{pct}%</em></div>'


def food_table(d):
    if d["dv"] is None:
        rows = "".join(f'<tr><td>{e(f)}<small>{e(s)}</small></td><td class="amt">{e(a)}</td><td>{e(k)}</td></tr>' for f, s, a, k in d["table"])
        return (f'<table class="foods"><thead><tr><th>Food</th><th>Amount</th><th>Type</th></tr></thead><tbody>{rows}</tbody></table>'
                f'<p class="tnote">{e(d.get("tableNote", ""))} Data: NIH Office of Dietary Supplements.</p>')
    rows = "".join(f'<tr><td>{e(f)}<small>{e(s)}</small></td><td class="amt">{e(a)}</td><td>{dvbar(p)}</td></tr>' for f, s, a, p in d["table"])
    return (f'<table class="foods"><thead><tr><th>Food</th><th>Amount</th><th>% Daily Value</th></tr></thead><tbody>{rows}</tbody></table>'
            f'<p class="tnote">% Daily Value is based on {e(d["dv"])} for adults (US FDA). Data: NIH Office of Dietary Supplements.'
            + (f' {e(d["tableNote"])}' if d.get("tableNote") else "") + "</p>")


def jsonld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>\n'


# ------------------------------------------------------------------ search index
INDEX = []
# Extra words people search with; matched like title words.
VKEYS = {"A": "eyes skin night vision retinol beta-carotene", "B1": "energy carbs alcohol", "B2": "energy yellow pee migraine",
         "B3": "niacin cholesterol flushing", "B5": "energy", "B6": "pms nerves mood", "B7": "biotin hair nails skin lab tests",
         "B9": "folate folic acid pregnancy anemia", "B12": "vegetarian vegan anemia tired nerves metformin",
         "C": "immunity colds collagen iron absorption amla", "D": "sunshine sun calcium bones vegetarian", "E": "antioxidant skin",
         "K": "blood clotting warfarin bones calcium",
         "Fe": "anemia anaemia ferritin hemoglobin tired periods", "Ca": "bones osteoporosis dairy milk", "Mg": "cramps migraine blood pressure",
         "Zn": "immunity colds taste smell wounds", "I": "thyroid salt goiter pregnancy", "Se": "thyroid brazil nuts antioxidant",
         "O3": "omega 3 fish oil heart dha epa ala flaxseed walnuts triglycerides"}
GENERIC = "daily need dose dosage amount how much upper limit deficiency deficient low signs supplement foods"
for v in ALL:
    INDEX.append({"t": f"{vname(v)} ({v['name']})", "u": url(v), "k": ("Omega-3 fats" if v["type"] == "omega" else "Mineral") if ismin(v) else "Vitamin", "x": VKEYS.get(v["id"], ""),
                  "s": " ".join([GENERIC, v["job"]] + [f[1] for f in v["foods"]] + [f[0] for f in v.get("forms", [])])})
    for s in v.get("subs", []):
        INDEX.append({"t": f"{s['tab']} · {s['name']}", "u": suburl(v, s), "k": f"Vitamin {v['id']} type", "s": s["job"]})
for g in G:
    INDEX.append({"t": g["title"], "u": gurl(g), "k": "Guide", "x": g["slug"].replace("-", " ") + (" fatigue energy exhausted" if g["slug"] == "tired" else ""),
                  "s": g["card"] + " " + " ".join(vname(BYID[k]) for k, _ in g["key"])})
INDEX.append({"t": "Minerals & omega-3", "u": "/minerals/", "k": "Overview", "x": "minerals mineral", "s": " ".join(vname(m) for m in M)})
for t in T:
    INDEX.append({"t": t["title"], "u": turl(t), "k": "Health topic", "x": t.get("keywords", ""), "s": " ".join([t["card"]] + [c[0] for c in t["causes"]] + [c[0] for c in t["claims"]] + [t.get("keywords", "")])})
INDEX.append({"t": "Protein: how much you need & best sources", "u": purl(), "k": "Protein", "x": "protein proteins macronutrient muscle amino acids grams whey dal paneer",
              "s": " ".join([GENERIC, PR["job"]] + [k[0] for k in PR["kinds"]] + [c[0] for c in PR["claims"]])})
for x in PR["subs"]:
    INDEX.append({"t": f"{x['tab']} · protein", "u": purl(x), "k": "Protein source", "x": "protein " + x["name"].replace(",", " ").lower(), "s": x["job"]})
INDEX += [{"t": "2-minute vitamin check", "u": "/tools/vitamin-check/", "k": "Tool", "s": "quiz am I low deficient test"},
          {"t": "Food finder", "u": "/tools/food-finder/", "k": "Tool", "s": "which foods vitamins search"}]
FOODS = []
for v in ALL:
    d = D[v["id"]]
    for f, s, a, p in d["table"]:
        FOODS.append({"f": f, "s": s, "a": a, "p": p if isinstance(p, int) else None, "v": v["id"], "n": vname(v), "u": url(v), "c": v["color"]})
    for f in d["indian"]:
        FOODS.append({"f": f, "s": "", "a": "", "p": None, "v": v["id"], "n": vname(v), "u": url(v), "c": v["color"], "in": 1})
_seen = set()
for x in PR["subs"]:
    for f, s, a, p in x["table"]:
        if f in _seen:
            continue
        _seen.add(f)
        FOODS.append({"f": f, "s": s, "a": a, "p": p, "v": "P", "n": "Protein", "u": purl(x), "c": PR["color"]})
write("assets/search.json", json.dumps(INDEX, ensure_ascii=False))
write("assets/foods.json", json.dumps(FOODS, ensure_ascii=False))

SEARCH = ('<div class="search" data-search><span class="ico" aria-hidden="true">🔍</span>'
          '<input type="search" placeholder="Search a vitamin, food or question… e.g. B12, spinach, tired" aria-label="Search VitaPals" autocomplete="off">'
          '<ul class="results" role="listbox"></ul></div>')

# ------------------------------------------------------------------ home
ALLMYTHS = [(m, f, v["id"]) for v in V for m, f in D[v["id"]].get("myths", [])]
featured = [(D[k]["myths"][0][0], D[k]["myths"][0][1], k) for k in ("C", "D", "B12")]
questions = [("Do vegetarians need a B12 supplement?", "/vitamin-b12/#faq"),
             ("Am I getting enough vitamin D?", "/vitamin-d/"),
             ("Vitamin D3 or D2: which is better?", "/vitamin-d/d3/"),
             ("How much vitamin C is too much?", "/vitamin-c/#supplements"),
             ("Should I take folic acid before pregnancy?", "/guides/pregnancy/"),
             ("Can biotin mess up blood tests?", "/vitamin-b7/#supplements"),
             ("Why am I always tired?", "/guides/tired/"),
             ("How much protein do I need a day?", "/protein/#needs"),
             ("Is \"hormonal imbalance\" a real diagnosis?", "/topics/hormonal-imbalance/")]
water = [v for v in V if v["type"] == "water"]
fat = [v for v in V if v["type"] == "fat"]
vrow = lambda v: (f'<a class="vtile" href="{url(v)}">{pal(v, 26, prop=False)}<div><strong>{e(vname(v))}</strong>'
                  f'<span>{e(v["name"].split(" (")[0])}</span><span class="dose">{e(D[v["id"]]["needShort"].replace(" a day", "/day"))}</span></div></a>')
home = head("VitaPals — Vitamins Explained Simply, Food First",
            "What each vitamin does, which foods have it, how much you need and whether you need a supplement. Plain language, real numbers from NIH.",
            "/", "home") + header("home") + f"""
<section class="hero-home"><div class="hero-grid"><div>
  <p class="eyebrow">Vitamins, explained simply</p>
  <h1>Know what your body needs, and where to get it.</h1>
  <p class="lede">What each vitamin does, the foods that have the most, how much you need, and when a supplement actually makes sense. Plain language, with real numbers from the NIH.</p>
  {SEARCH}
  <div class="ctas"><a class="btn" href="/tools/vitamin-check/">Take the 2-minute vitamin check</a><a class="btn ghost" href="/tools/food-finder/">Find foods by vitamin</a></div>
  <div class="trust"><span>Based on NIH fact sheets</span><span>Food first, supplements second</span><span>For adults 20+</span><span>US &amp; Indian foods</span><span>Reviewed {REVIEWED}</span></div>
</div><aside class="hero-aside" aria-label="Most read">
  <div class="squad" aria-hidden="true">{"".join(pal(x, 46, prop=False) for x in FAMILY)}</div>
  <h2 class="h3">Popular questions</h2>
  <ul class="qlist">{"".join(f'<li><a href="{u}">{e(q)}</a></li>' for q, u in questions)}</ul>
</aside></div>
</section>

<section class="block">
  <div class="head-row"><div><h2>Start with your situation</h2><p>Different stages of life need different vitamins.</p></div></div>
  <div class="cards">{"".join(f'<a class="card" href="{gurl(g)}"><div class="ic" aria-hidden="true">{g["icon"]}</div><h3>{e(g["title"])}</h3><p>{e(g["card"])}</p></a>' for g in G)}</div>
</section>

<section class="block">
  <div class="head-row"><div><h2>Health topics</h2><p>Common health questions, with every claim rated by the strength of its evidence.</p></div></div>
  <div class="cards">{"".join(f'<a class="card" href="{turl(t)}"><div class="ic" aria-hidden="true">{t["icon"]}</div><h3>{e(t["title"])}</h3><p>{e(t["card"])}</p><span class="go">Read →</span></a>' for t in T)}</div>
</section>

<section class="block" id="vitamins">
  <div class="head-row"><div><h2>All 13 vitamins</h2><p>Tap any vitamin for foods, daily needs, who's at risk and supplement advice.</p></div></div>
  <h3 style="margin:6px 0 10px"><span aria-hidden="true">💧</span> Water-soluble <small style="font-family:var(--sans);font-weight:400;color:var(--muted);font-size:15px">· your body doesn't store much, so you need them regularly</small></h3>
  <div class="vlist">{"".join(vrow(v) for v in water)}</div>
  <h3 style="margin:22px 0 10px">🫒 Fat-soluble <small style="font-family:var(--sans);font-weight:400;color:var(--muted);font-size:15px">· stored in your body, so too much from supplements can build up</small></h3>
  <div class="vlist">{"".join(vrow(v) for v in fat)}</div>
</section>

<section class="block" id="minerals">
  <div class="head-row"><div><h2>Minerals &amp; omega-3</h2><p>Iron, calcium and friends: the nutrients people most often run short on, plus the healthy fats everyone asks about.</p></div></div>
  <div class="vlist">{"".join(vrow(m) for m in M)}</div>
  <p style="margin-top:12px"><a href="/minerals/">See all minerals at a glance →</a></p>
</section>

<section class="block" id="protein">
  <div class="head-row"><div><h2>Protein</h2><p>How much you need, and the best sources, from dal and paneer to eggs, fish and soy.</p></div></div>
  <div class="vlist"><a class="vtile" href="/protein/">{pal(PR, 26, prop=False)}<div><strong>Protein overview</strong><span>Needs, benefits, myths</span><span class="dose">{e(PR["needShort"].replace(" a day", "/day"))}</span></div></a>{"".join(f'<a class="vtile" href="{purl(x)}">{pal(psubpal(x), 26, prop=False)}<div><strong>{e(x["tab"])}</strong><span>{e(x["name"])}</span></div></a>' for x in PR["subs"])}</div>
</section>

<section class="block">
  <div><h2 style="margin-bottom:10px">Myth vs fact</h2><div id="myth-week" class="mythgrid">
    {"".join(f'<div class="myth"><div class="m"><b>Myth</b>{e(m)}</div><div class="f"><b>Fact</b>{e(f)} <a href="/vitamin-{i.lower()}/#myths">Vitamin {e(i)} →</a></div></div>' for m, f, i in featured)}
  </div></div>
</section>

<section class="block band">
  <div><h2>Not sure where to start?</h2><p>Answer 13 quick questions about what you eat and your lifestyle. We'll show which vitamins and minerals deserve a closer look, and the foods that help. Nothing is stored or sent anywhere.</p></div>
  <div><a class="btn" href="/tools/vitamin-check/">Start the vitamin check →</a></div>
</section>
""" + footer('\n<script type="application/json" id="myths-data">' + json.dumps([{"m": m, "f": f, "v": i} for m, f, i in ALLMYTHS], ensure_ascii=False) + "</script>")
write("index.html", home)


# ------------------------------------------------------------------ vitamin pages
def forms_html(v):
    return ('<ul class="forms">' + "".join(
        f'<li><strong>{e(f[0])}</strong><span class="ftag t-{f[2].lower().replace(" ", "-")}">{e(f[2])}</span><p>{e(f[1])}</p></li>' for f in v["forms"]) + "</ul>")


for i, v in enumerate(ALL):
    d = D[v["id"]]
    mn = ismin(v)
    grp = M if mn else V
    gi = grp.index(v)
    isb = v["id"].startswith("B") and not mn
    prev = grp[gi - 1] if gi > 0 else None
    nxt = grp[gi + 1] if gi < len(grp) - 1 else None
    subs = v.get("subs") or []
    title = f"{vname(v)} ({v['name'].split(' (')[0]}): Foods, Daily Needs & Supplements | VitaPals"
    desc = fit(f"{vname(v)}: adults need {d['needShort']}. {v['job']} Top foods, who's at risk and when a supplement helps.",
               f"{vname(v)}: adults need {d['needShort']}. Top foods (US & Indian), who's at risk, upper limits and when a supplement helps.",
               f"{vname(v)}: adults need {d['needShort']}. Top foods, who's at risk and when a supplement helps.")
    crumbs = '<a href="/">Home</a> › ' + ('<a href="/vitamin-b/">B vitamins</a> › ' if isb else "") + ('<a href="/minerals/">Minerals</a> › ' if mn else "") + e(vname(v))
    soluble = {"water": "Water-soluble", "fat": "Fat-soluble", "mineral": "Mineral", "omega": "Essential fats"}[v["type"]]
    faq_ld = jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]})
    subpick = ""
    if subs:
        subpick = '<div class="subpick">' + "".join(
            f'<a class="vrow" href="{suburl(v, s)}">{pal(subpal(s), 30, prop=False)}<div><strong>{e(s["tab"])}</strong><span>{e(s["job"])}</span></div></a>' for s in subs) + "</div>"
    keyed = [g for g in G if v["id"] in [k for k, _ in g["key"]]]
    keyed.sort(key=lambda g: [k for k, _ in g["key"]].index(v["id"]))
    related = (keyed + [g for g in G if v["id"] in g["sources"] and g not in keyed])[:3]
    if v.get("guides"):
        related = [g for g in G if g["slug"] in v["guides"]]
    if not related:
        related = [g for g in G if g["slug"] in ("over-50", "supplements")]
    p = head(title, desc, url(v), slug(v), faq_ld) + header("minerals" if mn else "vitamins", None if mn else v["id"]) + f"""
<p class="crumbs">{crumbs}</p>
<div class="vhead">{pal(v, 64, decorative=False)}<div>
  <p class="kicker">{e(v['name'])} · {soluble}</p>
  <h1>{e(vname(v))}</h1>
  <p class="lede">{e(v['job'])}</p>
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
  <p class="sub">{"Per typical serving, with how much of your daily need it covers." if d["dv"] else "Per typical serving, in grams. Plant foods give ALA; fish gives EPA and DHA."}</p>
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
""" + (f"""<section class="sec"><h2>Related guides</h2><div class="cards">{"".join(f'<a class="card" href="{gurl(g)}"><div class="ic">{g["icon"]}</div><h3>{e(g["title"])}</h3><p>{e(g["card"])}</p></a>' for g in related)}</div></section>""" if related else "") + topic_links_html(topics_for("vitamins", v["id"])) + f"""
<p class="sources">Sources: <a href="{nih(v)}" rel="noopener">NIH Office of Dietary Supplements, {e(vname(v))} fact sheet for health professionals</a>. Daily needs are for healthy adults. Last reviewed {REVIEWED}. This page is for education, not medical advice.</p>
<div class="pager">
  {f'<a href="{url(prev)}"><small>← Previous</small>{e(vname(prev))}</a>' if prev else ('<a href="/minerals/"><small>← Back to</small>All minerals</a>' if mn else '<a href="/"><small>← Back</small>Home</a>')}
  {f'<a href="{url(nxt)}"><small>Next →</small>{e(vname(nxt))}</a>' if nxt else ('<a href="/#vitamins"><small>Next →</small>All 13 vitamins</a>' if mn else '<a href="/minerals/"><small>Next →</small>Minerals &amp; omega-3</a>')}
</div>
""" + footer()
    write(f"{slug(v)}/index.html", p)

    for j, s in enumerate(subs):
        sp = subs[j - 1] if j > 0 else None
        sn = subs[j + 1] if j < len(subs) - 1 else None
        stitle = (f"Vitamin {s['tab']} ({s['name']}): What It Is, Foods & Labels | VitaPals" if s["tab"].startswith(v["id"])
                  else f"{s['tab']}, a Form of Vitamin {v['id']}: Foods & Labels | VitaPals")
        sdesc = fit(f"{s['tab']}: {s['job']} Where to find it and how to read supplement labels.", f"{s['tab']}: {s['job']}")
        back = f'<a href="{url(v)}"><small>← Back to</small>{e(vname(v))} overview</a>'
        sp_html = head(stitle, sdesc, suburl(v, s), f"{slug(v)}-{s['slug']}") + header("vitamins", v["id"], s["slug"]) + f"""
<p class="crumbs"><a href="/">Home</a> › <a href="{url(v)}">{e(vname(v))}</a> › {e(s['tab'])}</p>
<div class="vhead">{pal(subpal(s), 64, decorative=False)}<div>
  <p class="kicker">{e(vname(v))} · {e(s['name'])}</p>
  <h1>{e(s['tab'])}</h1>
  <p class="lede">{e(s['job'])}</p>
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
{"".join(f'<tr><td><a href="{url(b)}"><strong>{e(b["id"])} · {e(b["name"].split(" (")[0])}</strong></a><small>{e(b["job"])}</small></td><td class="amt">{e(D[b["id"]]["needShort"].replace(" a day", ""))}</td><td>{e(D[b["id"]]["top3"])}<small>India: {e(D[b["id"]]["indian"][0])}</small></td></tr>' for b in BS)}
</tbody></table></section>
<section class="sec two">
  <div class="note"><h3>👀 The two to watch</h3><p><a href="/vitamin-b12/">B12</a> (vegetarians, vegans, adults over 50, metformin or acid-reducer users) and <a href="/vitamin-b9/">folate</a> (anyone who could become pregnant). The others are usually easy to get from food.</p></div>
  <div class="note warm"><h3>🤔 Where are B4, B8, B10 and B11?</h3><p>They were once called B vitamins, but later research showed they weren't true vitamins, or they were the same as others. So the numbering has gaps.</p></div>
</section>
<section class="sec"><h2>B vitamin all-stars</h2><p class="sub">Foods that bring several B vitamins at once.</p>
<div class="chips"><span>🫘 Beans, dals &amp; chickpeas</span><span>🌾 Whole grains &amp; fortified cereal</span><span>🥛 Milk &amp; curd</span><span>🥚 Eggs</span><span>🐟 Fish</span><span>🍄 Mushrooms</span><span>🌻 Sunflower seeds</span><span>🥬 Leafy greens</span></div></section>
""" + footer()
write("vitamin-b/index.html", hub)

# ------------------------------------------------------------------ minerals hub
mhub = head("Minerals & Omega-3: Iron, Calcium, Magnesium, Zinc & More | VitaPals",
            fit("Iron, calcium, magnesium, zinc, iodine, selenium and omega-3 in one place: how much adults need, the best US and Indian foods, and who should watch them."),
            "/minerals/", "minerals") + header("minerals") + f"""
<p class="crumbs"><a href="/">Home</a> › Minerals</p>
<div style="max-width:760px"><h1>Minerals &amp; omega-3</h1>
<p class="lede">Your body needs minerals in small amounts to build bones, carry oxygen and run your thyroid. These six, plus omega-3 fats, are the ones people ask about most.</p></div>
<section class="sec"><h2>All 7 at a glance</h2>
<table class="foods"><thead><tr><th>Nutrient</th><th>Adults need</th><th>Best foods</th></tr></thead><tbody>
{"".join(f'<tr><td><a href="{url(m)}"><strong>{e(vname(m))}</strong></a><small>{e(m["job"])}</small></td><td class="amt">{e(D[m["id"]]["needShort"].replace(" a day", ""))}</td><td>{e(D[m["id"]]["top3"])}<small>India: {e(D[m["id"]]["indian"][0])}</small></td></tr>' for m in M)}
</tbody></table><p class="tnote">Daily needs for adults from the US Food and Nutrition Board, via the NIH Office of Dietary Supplements.</p></section>
<section class="sec two">
  <div class="note"><h3>👀 The three to watch</h3><p><a href="/iron/">Iron</a> (heavy periods, pregnancy, vegetarians), <a href="/calcium/">calcium</a> (no dairy, women after menopause) and <a href="/iodine/">iodine</a> (no iodized salt, pregnancy). The others are usually easy to get from a varied diet.</p></div>
  <div class="note warn"><h3>⚠️ More isn't better</h3><p>Minerals have upper limits, and some build up. Iron, selenium and zinc pills can cause real harm in high doses. Test before you take, and keep iron away from children.</p></div>
</section>
{topic_links_html([t for t in T if any(x in t.get("related", {}).get("vitamins", []) for x in [m["id"] for m in M])])}
<p class="sources">Sources: NIH Office of Dietary Supplements fact sheets: {", ".join(f'<a href="{nih(m)}" rel="noopener">{e(vname(m))}</a>' for m in M)}. Last reviewed {REVIEWED}.</p>
""" + footer()
write("minerals/index.html", mhub)

# ------------------------------------------------------------------ guides
ulrows = "".join(f'<tr><td><a href="{url(v)}">{e(vname(v))}</a></td><td>{e(D[v["id"]]["needShort"].replace(" a day", ""))}</td><td>{e(D[v["id"]]["ulShort"])}</td></tr>' for v in V)
for gi_, g in enumerate(G):
    gprev, gnext = G[gi_ - 1] if gi_ > 0 else None, G[gi_ + 1] if gi_ < len(G) - 1 else None
    us_f, in_f = [], []
    for k, _ in g["key"][:4]:
        for x in D[k]["top3"].split(", "):
            x = x[0].upper() + x[1:]
            if not any(x.lower() in y.lower() or y.lower() in x.lower() for y in us_f):
                us_f.append(x)
        for x in D[k]["indian"][:2]:
            if not any(x.lower().split(" (")[0] in y.lower() or y.lower().split(" (")[0] in x.lower() for y in in_f):
                in_f.append(x)
    foods_block = f"""<section class="sec"><h2>Foods to lean on</h2><p class="sub">Food first. These cover the vitamins above.</p><div class="two">
  <div class="note"><h3>🛒 Everyday picks</h3><div class="chips">{"".join(f"<span>{e(x)}</span>" for x in us_f[:8])}</div></div>
  <div class="note"><h3>🇮🇳 In Indian kitchens</h3><div class="chips">{"".join(f"<span>{e(x)}</span>" for x in in_f[:8])}</div></div></div></section>"""
    keys = "".join(
        f'<a href="{url(BYID[k])}">{pal(BYID[k], 34, prop=False)}<div><strong>{e(vname(BYID[k]))}</strong><span>{e(t)}</span></div></a>' for k, t in g["key"])
    srcs = ", ".join(f'<a href="{nih(BYID[k])}" rel="noopener">{e(vname(BYID[k]))}</a>' for k in g["sources"])
    gp = head(g["seo"] + " | VitaPals", fit(g["card"] + " " + g["intro"].split(". ")[0] + ".", g["card"]), gurl(g)) + header("guides") + f"""
<p class="crumbs"><a href="/">Home</a> › <a href="/guides/">Guides</a> › {e(g['title'])}</p>
<div style="max-width:760px"><p class="kicker" style="font-size:36px;margin:0">{g['icon']}</p><h1>{e(g['title'])}</h1><p class="lede">{e(g['intro'])}</p></div>
<section class="sec"><h2>The vitamins to focus on</h2><div class="gkey">{keys}</div></section>
{foods_block}
<section class="sec"><h2>{e(g['plateTitle'])}</h2><div class="plate">{"".join(f"<div><b>{e(a)}</b>{e(b)}</div>" for a, b in g['plate'])}</div></section>
""" + (f"""<section class="sec"><h2>Daily needs and upper limits</h2><table class="ul"><tr><th>Vitamin</th><th>Adults need</th><th>Upper limit</th></tr>{ulrows}</table><p class="tnote">Upper limits are for adults and include food plus supplements unless noted. "None set" doesn't mean megadoses are safe.</p></section>""" if g.get("showUL") else "") + f"""
{f'<div class="note" style="margin-top:22px"><h3>💪 Don\'t forget protein</h3><p>{e(g["protein"])} <a href="/protein/">Protein: needs &amp; best sources →</a></p></div>' if g.get("protein") else ""}
<section class="sec two">
  <div class="note warm"><h3>📌 Good to know</h3><p>{e(g['beyond'])}</p></div>
  <div class="note"><h3>🩺 Talk to your doctor about</h3><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in g['doctor'])}</ul></div>
</section>
{topic_links_html(topics_for("guides", g["slug"]))}
<p class="sources">Sources: NIH Office of Dietary Supplements fact sheets: {srcs}{('; <a href="' + g['extraSource'][1] + '" rel="noopener">' + e(g['extraSource'][0]) + '</a>') if g.get('extraSource') else ''}. Last reviewed {REVIEWED}. General education, not medical advice.</p>
<div class="pager">
  {f'<a href="{gurl(gprev)}"><small>← Previous guide</small>{e(gprev["title"])}</a>' if gprev else '<a href="/guides/"><small>← Back to</small>All guides</a>'}
  {f'<a href="{gurl(gnext)}"><small>Next guide →</small>{e(gnext["title"])}</a>' if gnext else '<a href="/topics/"><small>Next →</small>Health topics</a>'}
</div>
""" + footer()
    write(f"guides/{g['slug']}/index.html", gp)

gi = head("Vitamin Guides for Every Stage of Life | VitaPals", "Vitamin guides for adults: vegetarians, your 20s to 40s, over 50, pregnancy, active lifestyles, supplements and tiredness.", "/guides/") + header("guides") + f"""
<p class="crumbs"><a href="/">Home</a> › Guides</p><h1>Guides</h1><p class="lede">Practical vitamin advice for adults, for every stage of life.</p>
<div class="cards" style="margin-top:22px">{"".join(f'<a class="card" href="{gurl(g)}"><div class="ic">{g["icon"]}</div><h3>{e(g["title"])}</h3><p>{e(g["card"])}</p><span class="go">Read guide →</span></a>' for g in G).replace("<h3>", '<h2 class="h3">').replace("</h3>", "</h2>")}</div>
""" + footer()
write("guides/index.html", gi)

# ------------------------------------------------------------------ health topics
LEGEND = '<div class="evlegend" aria-label="Evidence badges">' + "".join(badge(k) for k in "gywr") + '<a href="/about/#evidence">How we rate evidence</a></div>'


def evrows(rows, linkcol=False, labels=None, show=None, what="items"):
    out = []
    for r in rows:
        if linkcol:
            name, k, link, text = r
            title = f'<a href="{e(link)}">{e(name)}</a>' if link else e(name)
        else:
            name, k, text = r
            title = e(name)
        out.append(f'<li><div class="evh"><strong>{title}</strong>{badge(k, labels)}</div><p>{e(text)}</p></li>')
    if show and len(out) > show + 1:
        return ('<ul class="evlist">' + "".join(out[:show]) + "</ul>"
                f'<details class="more"><summary>Show all {len(out)} {what}</summary><ul class="evlist">' + "".join(out[show:]) + "</ul></details>")
    return '<ul class="evlist">' + "".join(out) + "</ul>"


def claims_html(cl, show=4):
    cards = [f'<div class="claim"><div class="cq"><b>Claim</b>{e(c)}</div><div class="cv">{badge(k)}<p>{e(v)}</p></div></div>' for c, k, v in cl]
    if len(cards) <= show + 1:
        return f'<div class="claimgrid">{"".join(cards)}</div>'
    return (f'<div class="claimgrid">{"".join(cards[:show])}</div><details class="more"><summary>Show all {len(cards)} claims</summary>'
            f'<div class="claimgrid">{"".join(cards[show:])}</div></details>')


for t in T:
    faq_ld = jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]})
    tp = head(t["seo"] + " | VitaPals", fit(t["card"], t["intro"]), turl(t), "home", faq_ld) + header("topics") + f"""
<p class="crumbs"><a href="/">Home</a> › <a href="/topics/">Health topics</a> › {e(t['title'])}</p>
<div style="max-width:760px"><p class="kicker" style="font-size:36px;margin:0" aria-hidden="true">{t['icon']}</p><p class="tkick">{e(t['kicker'])}</p><h1>{e(t['title'])}</h1><p class="lede">{e(t['intro'])}</p></div>
<div class="note short"><h2 class="h3">The short answer</h2><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in t['short'])}</ul></div>
<div class="glance">{"".join(f"<div><small>{e(a)}</small><strong>{e(b)}</strong></div>" for a, b in t['glance'])}</div>
<nav class="jump sticky" aria-label="On this page"><a href="#what">What it is</a><a href="#causes">{e(t.get("causesNav", "Causes"))}</a><a href="#helps">What helps</a><a href="#foods">Foods</a><a href="#nutrients">Nutrients</a><a href="#claims">Claims checked</a><a href="#doctor">Doctor &amp; tests</a><a href="#faq">FAQ</a></nav>
{LEGEND}

<section class="sec" id="what">
  <h2>What it is</h2>
  <div class="prose">{"".join(f"<p>{e(x)}</p>" for x in t['what'])}</div>
  <div class="two">{"".join(f'<div class="note{" warm" if i else ""}"><h3>{e(a)}</h3><p>{e(b)}</p></div>' for i, (a, b) in enumerate(t['types']))}</div>
  <div class="note warn" style="margin-top:14px"><h3>🏷️ Is it a diagnosis?</h3><p>{e(t['termNote'])}</p></div>
</section>

<section class="sec" id="causes">
  <h2>{e(t["causesTitle"])}</h2>
  <p class="sub">{e(t["causesSub"])}</p>
  {evrows(t['causes'], labels=t.get('causesLabels'))}
</section>

<section class="sec" id="helps">
  <h2>What actually helps</h2>
  <p class="sub">{e(t.get("helpsSub", "Lifestyle first. These are the changes with research behind them, strongest first."))}</p>
  {evrows(t['helps'])}
  <div class="note warn" style="margin-top:14px"><h3>{e(t["helpsNote"][0])}</h3><p>{e(t["helpsNote"][1])}</p></div>
</section>

<section class="sec" id="foods">
  <h2>Foods and eating patterns that help</h2>
  <p class="sub">{e(t["foodsSub"])}</p>
  <div class="two">
    <div class="note"><h3>🛒 Everyday picks</h3><div class="chips">{"".join(f"<span>{e(x)}</span>" for x in t['foodsUS'])}</div></div>
    <div class="note"><h3>🇮🇳 In Indian kitchens</h3><div class="chips">{"".join(f"<span>{e(x)}</span>" for x in t['foodsIndian'])}</div></div>
  </div>
  <div class="note warm" style="margin-top:14px"><h3>🍩 Go easy on</h3><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in t['limit'])}</ul></div>
  <h3 style="margin:22px 0 10px">A day of eating, for example</h3>
  <div class="plate">{"".join(f"<div><b>{e(a)}</b>{e(b)}</div>" for a, b in t['plate'])}</div>
</section>

<section class="sec" id="nutrients">
  <h2>Nutrients and supplements</h2>
  <p class="sub">Food first. Talk to your doctor or pharmacist before starting a supplement, especially if you take medicines.</p>
  {evrows(t['nutrients'], linkcol=True, show=4, what="nutrients")}
</section>

<section class="sec" id="claims">
  <h2>Popular claims we checked</h2>
  {claims_html(t['claims'])}
</section>

<section class="sec" id="doctor">
  <h2>When to see a doctor</h2>
  <div class="two">
    <div class="note warn"><h3>🩺 Book a visit if you have</h3><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in t['doctor'])}</ul></div>
    <div><h3 style="margin-bottom:8px">Tests to ask about</h3><table class="needs tests">{"".join(f"<tr><td><strong>{e(a)}</strong><span>{e(b)}</span></td></tr>" for a, b in t['tests'])}</table>
    <p class="tnote">Only your doctor can interpret results. One reading isn't a diagnosis.</p></div>
  </div>
</section>

<section class="sec" id="faq">
  <h2>Frequently asked questions</h2>
  {"".join(f'<details class="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in t['faq'])}
</section>

<section class="sources" id="sources"><details><summary><strong>Sources ({len(t['sources'])})</strong></summary>
<ol>{"".join(f'<li><a href="{e(u)}" rel="noopener">{e(n)}</a></li>' for n, u in t['sources'])}</ol></details>
<p>Last reviewed {REVIEWED}. This page is for general education, not medical advice. It hasn't been reviewed by a medical professional yet.</p></section>
<div class="pager"><a href="/topics/"><small>← Back to</small>Health topics</a><a href="/#vitamins"><small>Next →</small>All 13 vitamins</a></div>
""" + footer()
    write(f"topics/{t['slug']}/index.html", tp)

ti = head("Health Topics: Evidence-Rated Answers | VitaPals", "Common health questions like inflammation and hormonal imbalance, answered in plain language with every claim rated by the strength of its evidence.", "/topics/") + header("topics") + f"""
<p class="crumbs"><a href="/">Home</a> › Health topics</p><h1>Health topics</h1><p class="lede">Plain answers to common health questions. Every claim gets a badge, so you can see how strong the evidence is.</p>
<div style="margin-top:16px">{LEGEND}</div>
<div class="cards" style="margin-top:18px">{"".join(f'<a class="card" href="{turl(t)}"><div class="ic">{t["icon"]}</div><h3>{e(t["title"])}</h3><p>{e(t["card"])}</p><span class="go">Read →</span></a>' for t in T).replace("<h3>", '<h2 class="h3">').replace("</h3>", "</h2>")}</div>
<p class="tnote" style="margin-top:18px">Coming next: deep dives on thyroid, PCOS, menopause and PMS, then sleep, mood, bones, heart and more.</p>
""" + footer()
write("topics/index.html", ti)

# ------------------------------------------------------------------ protein
def ptable(rows, note):
    body = "".join(f'<tr><td>{e(f)}<small>{e(s)}</small></td><td class="amt">{e(a)}</td><td>{dvbar(p)}</td></tr>' for f, s, a, p in rows)
    return (f'<table class="foods"><thead><tr><th>Food</th><th>Protein</th><th>% Daily Value</th></tr></thead><tbody>{body}</tbody></table>'
            f'<p class="tnote">% Daily Value is based on {e(PR["dv"])} of protein a day for adults (US FDA). {e(note)}</p>')


PSRC = ('<section class="sources" id="sources"><details><summary><strong>Sources ({n})</strong></summary><ol>{items}</ol></details>'
        '<p>Last reviewed {rev}. This page is for general education, not medical advice. It hasn\'t been reviewed by a medical professional yet.</p></section>')
psources = PSRC.format(n=len(PR["sources"]), rev=REVIEWED, items="".join(f'<li><a href="{e(u)}" rel="noopener">{e(n)}</a></li>' for n, u in PR["sources"]))
pguides = [g for g in G if g["slug"] in PR["guides"]]
pfaq_ld = jsonld({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in PR["faq"]]})
CALC = """<div class="tool pcalc" id="pcalc" hidden>
  <h3>Your number</h3>
  <div class="pcalc-in"><label for="pc-w">Your weight</label><input id="pc-w" type="number" inputmode="decimal" min="30" max="300" placeholder="e.g. 65">
  <select id="pc-u" aria-label="Unit"><option value="kg">kg</option><option value="lb">lb</option></select></div>
  <div id="pc-out" aria-live="polite"><p class="tnote">Enter your weight to see a daily range in grams. Nothing is stored or sent anywhere.</p></div>
</div>"""
pp = head("Protein: How Much You Need & the Best Sources (US & Indian) | VitaPals",
          fit("Protein for adults: how much you need (about 0.8 g per kg), the best US and Indian sources, protein powders, and myths checked with evidence."),
          purl(), "protein", pfaq_ld) + header("protein") + f"""
<p class="crumbs"><a href="/">Home</a> › Protein</p>
<div class="vhead">{pal(PR, 64, decorative=False)}<div>
  <p class="kicker">Macronutrient · Made of amino acids</p>
  <h1>Protein</h1>
  <p class="lede">{e(PR['job'])}</p>
</div></div>
<div class="glance" id="glance">{"".join(f"<div><small>{e(a)}</small><strong>{e(b)}</strong></div>" for a, b in PR['glance'])}</div>
<nav class="jump" aria-label="On this page"><a href="#types">Sources</a><a href="#foods">Top foods</a><a href="#needs">How much</a><a href="#benefits">Benefits</a><a href="#risk">Who needs more</a><a href="#supplements">Powders</a><a href="#claims">Claims checked</a><a href="#doctor">Doctor</a><a href="#faq">FAQ</a></nav>

<section class="sec" id="types">
  <h2>Protein by source</h2>
  <p class="sub">Tap a type for its best foods, Indian picks and what to watch.</p>
  <div class="subpick">{"".join(f'<a class="vrow" href="{purl(x)}">{pal(psubpal(x), 30, prop=False)}<div><strong>{e(x["tab"])}</strong><span>{e(x["job"])}</span></div></a>' for x in PR["subs"])}</div>
</section>

<section class="sec two">
  <div><h2>What it does</h2><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in PR['powers'])}</ul></div>
  <div class="note warm"><h3>🤓 Did you know?</h3><p>{e(PR['fun'])}</p></div>
</section>

<section class="sec" id="foods">
  <h2>Top food sources</h2>
  <p class="sub">Per typical serving, with how much of the 50 g Daily Value it covers.</p>
  {ptable(PR["table"], PR["tableNote"])}
  <div class="two" style="margin-top:16px">
    <div class="note"><h3>🇮🇳 Also great in Indian kitchens</h3><div class="chips">{"".join(f"<span>{e(x)}</span>" for x in PR['indian'])}</div></div>
    <div class="note warm"><h3>👩‍🍳 Kitchen tips</h3><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in PR['tips'])}</ul></div>
  </div>
</section>

<section class="sec two" id="needs">
  <div><h2>How much do you need?</h2>
    <table class="needs">{"".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in PR['needs'])}</table>
    <p class="tnote">{e(PR['needNote'])}</p></div>
  <div style="align-self:start;display:grid;gap:14px">{CALC}
    <div class="note warm"><h3>ℹ️ Upper limit</h3><p>{e(PR['ul'])}</p></div></div>
</section>

<section class="sec" id="kinds">
  <h2>Complete vs incomplete protein</h2>
  <p class="sub">{e(PR['kindsIntro'])}</p>
  <ul class="forms">{"".join(f'<li><strong>{e(a)}</strong><span class="ftag t-{c.lower()}">{e(c)}</span><p>{e(b)}</p></li>' for a, b, c in PR["kinds"])}</ul>
</section>

<section class="sec" id="benefits">
  <h2>Benefits, rated by evidence</h2>
  {LEGEND}
  {evrows(PR['benefits'])}
</section>

<section class="sec" id="risk">
  <h2>Who should pay more attention?</h2>
  <div class="risk" style="--c:{PR['color']}">{"".join(f"<div><strong>{e(a)}</strong><span>{e(b)}</span></div>" for a, b in PR['risk'])}</div>
</section>

<section class="sec" id="supplements">
  <h2>Protein powders: do you need one?</h2>
  <div class="two">
    <div class="note"><h3>When it helps</h3><p>{e(PR['suppWhen'])}</p></div>
    <div class="note warm"><h3>Choosing one</h3><p>{e(PR['suppPick'])} <a href="{purl(PR['subs'][-1])}">More on powders →</a></p></div>
  </div>
  <div class="note warn" style="margin-top:14px"><h3>💊 Health conditions, medicines &amp; cautions</h3><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in PR['cautions'])}</ul><p style="margin-top:8px">Always tell your doctor and pharmacist about any supplements you take.</p></div>
</section>

<section class="sec" id="claims">
  <h2>Popular claims we checked</h2>
  {claims_html(PR['claims'])}
</section>

<section class="sec" id="doctor">
  <h2>When to see a doctor</h2>
  <div class="two">
    <div class="note warn"><h3>🩺 Book a visit if you have</h3><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in PR['doctor'])}</ul></div>
    <div><h3 style="margin-bottom:8px">Tests to ask about</h3><table class="needs tests">{"".join(f"<tr><td><strong>{e(a)}</strong><span>{e(b)}</span></td></tr>" for a, b in PR['tests'])}</table>
    <p class="tnote">Only your doctor can interpret results. {e(PR['lowNote'])}</p></div>
  </div>
</section>

<section class="sec" id="faq">
  <h2>Frequently asked questions</h2>
  {"".join(f'<details class="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in PR['faq'])}
</section>
<section class="sec"><h2>Related guides</h2><div class="cards">{"".join(f'<a class="card" href="{gurl(g)}"><div class="ic">{g["icon"]}</div><h3>{e(g["title"])}</h3><p>{e(g["card"])}</p></a>' for g in pguides)}</div></section>
{psources}
<div class="pager">
  <a href="/minerals/"><small>← Previous</small>Minerals &amp; omega-3</a>
  <a href="{purl(PR['subs'][0])}"><small>Next →</small>{e(PR['subs'][0]['tab'])}</a>
</div>
""" + footer()
write("protein/index.html", pp)

for j, x in enumerate(PR["subs"]):
    xp = PR["subs"][j - 1] if j > 0 else None
    xn = PR["subs"][j + 1] if j < len(PR["subs"]) - 1 else None
    back = '<a href="/protein/"><small>← Back to</small>Protein overview</a>'
    indian = (f'<div class="note"><h3>🇮🇳 In Indian kitchens</h3><div class="chips">{"".join(f"<span>{e(i)}</span>" for i in x["indian"])}</div></div>' if x["indian"] else "")
    table = (f'<section class="sec" id="foods"><h2>How much protein?</h2><p class="sub">Per typical serving, with how much of the 50 g Daily Value it covers.</p>{ptable(x["table"], x["tableNote"])}<div style="margin-top:16px">{indian}</div></section>'
             if x["table"] else "")
    xh = head(f"{x['tab']}: Protein, Best Picks & What to Watch | VitaPals",
              fit(f"{x['tab']} as a protein source: {x['job']} Grams per serving, US and Indian picks, and what to watch.", f"{x['tab']} as a protein source: {x['job']}"),
              purl(x), f"protein-{x['slug']}") + header("protein", psub=x["slug"]) + f"""
<p class="crumbs"><a href="/">Home</a> › <a href="/protein/">Protein</a> › {e(x['tab'])}</p>
<div class="vhead">{pal(psubpal(x), 64, decorative=False, prop=False)}<div>
  <p class="kicker">Protein source · {e(x['name'])}</p>
  <h1>{e(x['tab'])}</h1>
  <p class="lede">{e(x['job'])}</p>
</div></div>
<section class="sec two">
  <div><h2>What makes it special</h2><ul class="clean">{"".join(f"<li>{e(i)}</li>" for i in x['what'])}</ul></div>
  <div class="note warm"><h3>🤓 Did you know?</h3><p>{e(x['fun'])}</p></div>
</section>
{table}
<section class="sec two">
  <div class="note"><h3>👍 Why it's worth eating</h3><p>{e(x['good'])}</p></div>
  <div class="note warn"><h3>⚠️ What to watch</h3><p>{e(x['watch'])}</p></div>
</section>
{f'<section class="sec">{indian}</section>' if indian and not table else ""}
<section class="sec two">
  <div class="note warm"><h3>{"🏷️ Label decoder" if x['slug'] == "powders" else "💡 Easy win"}</h3><p>{e(x['tip'])}</p></div>
  <div class="note"><h3>📏 How much protein do you need?</h3><p>About 0.8 g per kg of body weight a day for most adults: {e(PR['needShort'])}. More if you're over 65 or train hard.</p><p><a href="/protein/#needs">See daily needs &amp; your number →</a></p></div>
</section>
{psources}
<div class="pager">
  {f'<a href="{purl(xp)}"><small>← Previous</small>{e(xp["tab"])}</a>' if xp else back}
  {f'<a href="{purl(xn)}"><small>Next →</small>{e(xn["tab"])}</a>' if xn else back.replace("← Back to", "Back to →")}
</div>
""" + footer()
    write(f"protein/{x['slug']}/index.html", xh)

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
          "Answer 13 quick questions about your diet and lifestyle to see which vitamins and minerals deserve a closer look. Free, private and educational.",
          "/tools/vitamin-check/") + header("check") + """
<p class="crumbs"><a href="/">Home</a> › Vitamin check</p>
<div style="max-width:760px"><h1>2-minute vitamin check</h1><p class="lede">Answer 13 quick questions about how you eat and live. We'll point out which vitamins deserve a closer look, and the foods that help. Your answers stay on your device.</p></div>
<form class="tool" id="vcheck" style="margin-top:20px">
  <fieldset class="q"><legend>1. How do you eat?</legend><div class="opts">
    <label><input type="radio" name="diet" value="omni" required> I eat meat or fish</label>
    <label><input type="radio" name="diet" value="veg"> Vegetarian (dairy and/or eggs)</label>
    <label><input type="radio" name="diet" value="vegan"> Vegan (no animal foods)</label></div></fieldset>
  <fieldset class="q"><legend>2. Your age</legend><div class="opts">
    <label><input type="radio" name="age" value="u50" required> 20–49</label>
    <label><input type="radio" name="age" value="50"> 50–70</label>
    <label><input type="radio" name="age" value="71"> Over 70</label></div></fieldset>
  <fieldset class="q"><legend>3. Are you pregnant, breastfeeding or planning a pregnancy?</legend><div class="opts">
    <label><input type="radio" name="preg" value="no" required> No</label>
    <label><input type="radio" name="preg" value="yes"> Yes</label></div></fieldset>
  <fieldset class="q"><legend>4. How often are you outdoors in daylight (arms or face uncovered)?</legend><div class="opts">
    <label><input type="radio" name="sun" value="often" required> Most days</label>
    <label><input type="radio" name="sun" value="rare"> Rarely, or mostly covered up</label></div></fieldset>
  <fieldset class="q"><legend>5. Your skin tone</legend><div class="opts">
    <label><input type="radio" name="skin" value="light" required> Lighter</label>
    <label><input type="radio" name="skin" value="dark"> Medium to darker (makes less vitamin D from sun)</label></div></fieldset>
  <fieldset class="q"><legend>6. Leafy greens, dals or beans</legend><div class="opts">
    <label><input type="radio" name="greens" value="daily" required> Most days</label>
    <label><input type="radio" name="greens" value="some"> A few times a week</label>
    <label><input type="radio" name="greens" value="rare"> Rarely</label></div></fieldset>
  <fieldset class="q"><legend>7. Fresh fruit or raw veggies (oranges, guava, peppers, tomatoes…)</legend><div class="opts">
    <label><input type="radio" name="fruit" value="daily" required> Daily</label>
    <label><input type="radio" name="fruit" value="rare"> Rarely</label></div></fieldset>
  <fieldset class="q"><legend>8. Nuts, seeds or nut butters</legend><div class="opts">
    <label><input type="radio" name="nuts" value="often" required> Several times a week</label>
    <label><input type="radio" name="nuts" value="rare"> Rarely</label></div></fieldset>
  <fieldset class="q"><legend>9. Milk, curd, paneer, or calcium-fortified foods (like fortified soy milk)</legend><div class="opts">
    <label><input type="radio" name="dairy" value="daily" required> Most days</label>
    <label><input type="radio" name="dairy" value="rare"> Rarely</label></div></fieldset>
  <fieldset class="q"><legend>10. Do you use iodized salt at home?</legend><div class="opts">
    <label><input type="radio" name="salt" value="yes" required> Yes</label>
    <label><input type="radio" name="salt" value="no"> No, or not sure (sea, rock or pink salt usually isn't iodized)</label></div></fieldset>
  <fieldset class="q"><legend>11. Do you have heavy periods?</legend><div class="opts">
    <label><input type="radio" name="periods" value="heavy" required> Yes</label>
    <label><input type="radio" name="periods" value="no"> No, or doesn't apply</label></div></fieldset>
  <fieldset class="q"><legend>12. Do you smoke, or have several alcoholic drinks most days?</legend><div class="opts">
    <label><input type="checkbox" name="smoke"> I smoke</label>
    <label><input type="checkbox" name="alcohol"> Several drinks most days</label></div></fieldset>
  <fieldset class="q"><legend>13. Do you take any of these medicines regularly?</legend><div class="opts">
    <label><input type="checkbox" name="metformin"> Metformin (diabetes)</label>
    <label><input type="checkbox" name="acid"> Acid reducers (omeprazole, pantoprazole, famotidine…)</label>
    <label><input type="checkbox" name="warfarin"> Warfarin or another blood thinner</label>
    <label><input type="checkbox" name="seizure"> Seizure medicines</label></div></fieldset>
  <p class="vprog" id="vcheck-prog" aria-live="polite">0 of 11 answered · questions 12 and 13 are optional</p>
  <button class="btn" type="submit">See my results</button>
  <div class="res" id="vcheck-out" aria-live="polite"></div>
  <noscript><p>The vitamin check needs JavaScript.</p></noscript>
</form>
<p class="tnote" style="margin-top:12px">Designed for adults aged 20 and over. This is an educational tool, not a diagnosis. Only a doctor and a blood test can tell you if you're low.</p>
""" + footer()
write("tools/vitamin-check/index.html", vc)

# ------------------------------------------------------------------ about
about = head("About VitaPals & How We Write", "How VitaPals researches and writes about vitamins: who it's for, where the facts come from, how evidence is rated and what we never do.", "/about/") + header("about") + f"""
<p class="crumbs"><a href="/">Home</a> › About</p>
<div class="prose"><h1>About VitaPals</h1>
<p class="lede">VitaPals explains vitamins in plain language, so you can make sense of what you eat and have better conversations with your doctor.</p>
<h2>Who it's for</h2><p>VitaPals is written for adults aged 20 and over. Children and teens have different needs and safe limits, so please ask a pediatrician about them.</p>
<h2>Food first</h2><p>Most people can get most vitamins from a varied diet. We show real foods, with real amounts, before we ever talk about supplements. We include everyday US and Indian foods, because that's how many of our readers eat.</p>
<h2>Where our facts come from</h2><p>Daily needs, upper limits, food amounts and medicine interactions come from the <a href="https://ods.od.nih.gov/factsheets/list-VitaminsMinerals/" rel="noopener">NIH Office of Dietary Supplements</a> fact sheets for health professionals, which are based on the US Food and Nutrition Board. Every page links to its source.</p>
<h2 id="evidence">How we rate evidence</h2><p>On health topic pages, every claim gets a badge:</p>
<ul class="clean"><li>🟢 <strong>Strong evidence</strong>: backed by large randomized trials, meta-analyses or major medical guidelines.</li><li>🟡 <strong>Some evidence</strong>: promising or consistent studies, but smaller, mixed or mostly observational.</li><li>⚪ <strong>Not enough evidence</strong>: too little good research to say either way.</li><li>🔴 <strong>Myth</strong>: the evidence says no, or it isn't a recognized condition.</li></ul>
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
paths = (["/", "/vitamin-b/"] + [p for v in V for p in [url(v)] + [suburl(v, s) for s in v.get("subs", [])]] + ["/minerals/"] + [url(m) for m in M] + [purl()] + [purl(x) for x in PR["subs"]]
         + ["/guides/"] + [gurl(g) for g in G] + ["/topics/"] + [turl(t) for t in T] + ["/tools/food-finder/", "/tools/vitamin-check/", "/about/"])
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{TODAY}</lastmod></url>\n" for p in paths) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
write("favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect x="16" y="2" width="32" height="60" rx="16" fill="#1e6b52"/><path d="M16 32H48V46A16 16 0 0 1 16 46Z" fill="#7cc4a4"/></svg>\n')

og_items = [("home", None), ("vitamin-b", B_HUB)] + [(slug(v), v) for v in ALL]
(SRC / "og.json").write_text(json.dumps([
    {"name": n,
     "svg": pal(v, 260) if v else "".join(pal(x, 110) for x in FAMILY),
     "kicker": (((("Mineral · " if v["type"] == "mineral" else "Essential fats · ") + v["name"]) if ismin(v) else ("Vitamin " + v["id"] + " · " + v["name"])) if v is not B_HUB else "8 vitamins · water-soluble") if v else "Vitamins, explained simply",
     "title": (vname(v) if v is not B_HUB else "The B vitamins") if v else "Know what your body needs",
     "color": v["color"] if v else "#1e6b52",
     "lead": (D[v["id"]]["needShort"][:1].upper() + D[v["id"]]["needShort"][1:] + ". Best foods: " + D[v["id"]]["top3"].lower() + ".") if v and v is not B_HUB else ("Foods, daily needs and supplement advice for all 8." if v else "Foods, daily needs and honest supplement advice. Based on NIH data.")}
    for n, v in og_items] + [
    {"name": f"{slug(v)}-{s['slug']}", "svg": pal(subpal(s), 260), "kicker": f"Vitamin {v['id']} · {s['name']}",
     "title": s["tab"], "color": s["color"], "lead": s["job"]}
    for v in V for s in v.get("subs", [])] + [
    {"name": "protein", "svg": pal(PR, 260), "kicker": "Macronutrient · amino acids", "title": "Protein",
     "color": PR["color"], "lead": "Adults need about 0.8 g per kg a day. Best foods: dals, dairy, eggs, fish, soy."}] + [
    {"name": f"protein-{x['slug']}", "svg": pal(psubpal(x), 260, prop=False), "kicker": "Protein source", "title": x["tab"], "color": x["color"], "lead": x["job"]}
    for x in PR["subs"]] + [
    {"name": "minerals", "svg": "".join(pal(m, 110) for m in M[:6]), "kicker": "Minerals & omega-3", "title": "Iron, calcium & friends",
     "color": "#1e6b52", "lead": "How much you need, the best US and Indian foods, and who should watch them.", "multi": 1}], ensure_ascii=False), encoding="utf-8")

print(f"Built {len(paths)} pages + 404, sitemap, robots, favicon, search & food data.")
