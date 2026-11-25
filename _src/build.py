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
REVIEWED = "November 24, 2026"
TODAY = datetime.date.today().isoformat()
YEAR = datetime.date.today().year
ASSET_V = "16"
REVIEWED_ISO = datetime.datetime.strptime(REVIEWED, "%B %d, %Y").date().isoformat()

# ---- brand & search settings (edit here; everything below is generated from these)
BRAND = "MyVitaPals"
BRAND_ALT = ["VitaPals", "myvitapals.com"]
TAGLINE = "Food First, Science Always"
BRAND_DESC = ("Science-backed nutrition education for adults in the US and India: vitamins, minerals, protein and "
              "healthy foods explained in plain language, food first, with numbers from the NIH Office of Dietary Supplements.")
# Search-engine verification tokens. Leave "" to skip. Google's token is already verified in Search Console.
GOOGLE_VERIFY = "PWmqsbCTxIDBLfAWZAj158s1Cxm_8TM1bWkIVkYY31g"
BING_VERIFY = ""  # paste the msvalidate.01 content from Bing Webmaster Tools, or import the site from Search Console instead
# IndexNow (Bing, Yandex, Seznam, Naver...). The key is public by design: it is published at /<key>.txt.
INDEXNOW_KEY = "0d6a130a6f6e14f262e2b09373a78da5"
# AI training crawlers are controlled separately from search crawlers. "Allow" or "Disallow".
AI_TRAINING = "Allow"
SEARCH_BOTS = ["Googlebot", "Bingbot", "OAI-SearchBot", "ChatGPT-User", "Claude-SearchBot", "Claude-User",
               "PerplexityBot", "Perplexity-User", "Applebot", "DuckDuckBot"]
TRAINING_BOTS = ["GPTBot", "ClaudeBot", "Google-Extended", "Applebot-Extended", "CCBot"]
PAGE_CRUMBS = [None]  # breadcrumb trail of the page being built: rendered visibly by header() and as JSON-LD by head()
PAGES = []  # (path, title, desc, noindex) for every HTML page written; feeds sitemap.xml and llms.txt

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
EV = {"g": ("🟢", "Established guidance"), "y": ("🟡", "Limited evidence"), "w": ("⚪", "Not enough evidence"), "r": ("🔴", "Myth")}
badge = lambda k, labels=None: f'<span class="ev ev-{k}"><i aria-hidden="true">{EV[k][0]}</i>{(labels or {}).get(k, EV[k][1])}</span>'
txt = lambda v: v.get("text", "#fff")
subpal = lambda s: {"id": s["label"], "color": s["color"], "text": txt(s), "prop": s["prop"]}
psubpal = lambda x: {"id": x["prop"], "color": x["color"], "text": txt(x), "prop": x["prop"], "aria": x["tab"]}
vname = lambda v: v.get("label") or f"Vitamin {v['id']}"
ismin = lambda v: v["type"] in ("mineral", "omega")
lname = lambda v: f"vitamin {v['id']}" if vname(v).startswith("Vitamin") else vname(v)[0].lower() + vname(v)[1:]
cap = lambda t: t[0].upper() + t[1:]
# Related nutrients shown at the bottom of each nutrient page (overridden by details.json "related")
RELATED = {"A": ["D", "E", "Zn"], "B2": ["B1", "B3", "B6"], "B3": ["B1", "B2", "B6"], "B12": ["B9", "Fe", "B6"], "C": ["Fe", "E", "Zn"],
           "E": ["C", "Se", "A"], "K": ["D", "Ca", "Mg"], "Fe": ["C", "B12", "B9"], "Ca": ["D", "Mg", "K"], "Mg": ["Ca", "D", "B6"],
           "Zn": ["Fe", "C", "Se"], "I": ["Se", "Fe", "B12"], "Se": ["I", "E", "Zn"], "O3": ["D", "E", "B12"]}
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


ORG = {"@type": "Organization", "@id": f"{SITE}/#organization", "name": BRAND, "alternateName": BRAND_ALT, "url": f"{SITE}/",
       "slogan": TAGLINE, "description": BRAND_DESC,
       "logo": {"@type": "ImageObject", "url": f"{SITE}/apple-touch-icon.png", "width": 180, "height": 180},
       "publishingPrinciples": f"{SITE}/about/", "correctionsPolicy": f"{SITE}/about/#corrections"}
WEBSITE = {"@type": "WebSite", "@id": f"{SITE}/#website", "name": BRAND, "alternateName": BRAND_ALT, "url": f"{SITE}/",
           "description": BRAND_DESC, "inLanguage": "en", "publisher": {"@id": f"{SITE}/#organization"}}
DISCLAIMER = ("General nutrition education for adults, not medical advice. Content has not been clinically reviewed; "
              "talk to a doctor, dietitian or pharmacist before starting a supplement.")


def title_fit(*cands, n=65):
    """First title candidate (brand suffix included) that fits n characters; else the shortest."""
    full = [f"{c} | {BRAND}" for c in cands]
    return next((c for c in full if len(c) <= n), min(full, key=len))


def graph(path, title, desc, og, kind, crumbs, faq, cites, about):
    """One JSON-LD @graph per page: Organization, WebSite, the page, optional Article, breadcrumbs and FAQ."""
    page_url = f"{SITE}{path}"
    nodes = [ORG, WEBSITE]
    wp = {"@type": {"about": "AboutPage", "collection": "CollectionPage"}.get(kind, "WebPage"), "@id": f"{page_url}#webpage",
          "url": page_url, "name": title, "description": desc, "inLanguage": "en", "isPartOf": {"@id": f"{SITE}/#website"},
          "primaryImageOfPage": {"@type": "ImageObject", "url": f"{SITE}/og/{og}.png", "width": 1200, "height": 630},
          "dateModified": REVIEWED_ISO}
    if path == "/":
        wp["about"] = {"@id": f"{SITE}/#organization"}
    if crumbs:
        wp["breadcrumb"] = {"@id": f"{page_url}#breadcrumb"}
    nodes.append(wp)
    if kind == "article":
        art = {"@type": "Article", "@id": f"{page_url}#article", "headline": title.split(" | ")[0][:110], "description": desc,
               "mainEntityOfPage": {"@id": f"{page_url}#webpage"}, "image": f"{SITE}/og/{og}.png", "inLanguage": "en",
               "dateModified": REVIEWED_ISO, "author": {"@id": f"{SITE}/#organization"}, "publisher": {"@id": f"{SITE}/#organization"},
               "isAccessibleForFree": True, "audience": {"@type": "PeopleAudience", "suggestedMinAge": 20},
               "disambiguatingDescription": DISCLAIMER}
        if about:
            art["about"] = {"@type": "Thing", "name": about}
        if cites:
            art["citation"] = [{"@type": "CreativeWork", "name": n, "url": u} for n, u in cites]
        nodes.append(art)
    if crumbs:
        trail = [("Home", "/")] + list(crumbs)
        nodes.append({"@type": "BreadcrumbList", "@id": f"{page_url}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": i, "name": n, **({"item": f"{SITE}{u}"} if u else {})}
            for i, (n, u) in enumerate(trail, 1)]})
    if faq:
        nodes.append({"@type": "FAQPage", "@id": f"{page_url}#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})
    return jsonld({"@context": "https://schema.org", "@graph": nodes})


def head(title, desc, path, og="home", extra="", kind="website", crumbs=None, faq=None, cites=None, about=None, noindex=False):
    """kind: website | article | collection | about. crumbs: [(name, path or None for the current page)]."""
    PAGES.append((path, title, desc, noindex))
    PAGE_CRUMBS[0] = crumbs
    ogtype = "article" if kind == "article" else "website"
    verify = (f'<meta name="google-site-verification" content="{GOOGLE_VERIFY}">\n' if GOOGLE_VERIFY else "") + \
             (f'<meta name="msvalidate.01" content="{BING_VERIFY}">\n' if BING_VERIFY else "")
    robots = "noindex, follow" if noindex else "index, follow, max-image-preview:large, max-snippet:-1"
    art = f'<meta property="article:modified_time" content="{REVIEWED_ISO}">\n' if kind == "article" else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{SITE}{path}">
<meta name="theme-color" content="#faf7f2">
{verify}<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/og/{og}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{e(title.split(' | ')[0])}: {BRAND} illustration">
{art}<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{SITE}/og/{og}.png">
{graph(path, title, desc, og, kind, crumbs, faq, cites, about) if not noindex else ""}<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/fraunces-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.min.css?v={ASSET_V}">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""


SECTION_NAV = [("vitamins", "/vitamins/", "Vitamins"), ("minerals", "/minerals/", "Minerals"), ("protein", "/protein/", "Protein"),
               ("topics", "/topics/", "Health topics"), ("guides", "/guides/", "Guides"), ("tools", "/tools/", "Tools")]
SECTION_OF = {"finder": "tools", "check": "tools"}


def search_box(sid, placeholder="Search a vitamin, food or question… e.g. B12, spinach, tired", big=False):
    return (f'<div class="search{" big" if big else ""}" role="search" data-search><label class="sr-only" for="{sid}">Search {BRAND}</label>'
            f'<span class="ico" aria-hidden="true">🔍</span>'
            f'<input id="{sid}" type="search" placeholder="{placeholder}" autocomplete="off" aria-describedby="{sid}-status" aria-controls="{sid}-results">'
            f'<p class="sr-only" id="{sid}-status" aria-live="polite"></p><ul class="results" id="{sid}-results"></ul></div>')


def header(section="", vit=None, sub=None, psub=None):
    """Global header: logo, desktop section nav, search on every page, and a mobile menu of expandable categories."""
    sec = SECTION_OF.get(section, section)
    cur = lambda k: ' aria-current="true" class="on"' if sec == k else ""
    nav = "".join(f'<a href="{h}"{cur(k)}>{t}</a>' for k, h, t in SECTION_NAV)

    def group(key, title, items, all_link):
        here = PAGES[-1][0] if PAGES else ""
        links = "".join(f'<a href="{h}"{" aria-current=page" if h == here else ""}>{t}</a>' for h, t in [all_link] + items)
        return (f'<details class="mg"{" open" if sec == key else ""}><summary>{title}<span class="ct">{len(items)}</span></summary>'
                f'<div class="mg-links">{links}</div></details>')
    groups = "".join([
        group("vitamins", "Vitamins", [(url(v), e(vname(v)) + (" · " + e(v["name"].split(" (")[0]) if v["id"].startswith("B") else "")) for v in V], ("/vitamins/", "All 13 vitamins")),
        group("minerals", "Minerals &amp; omega-3", [(url(m), e(vname(m))) for m in M], ("/minerals/", "All minerals at a glance")),
        group("protein", "Protein", [(purl(x), e(x["tab"])) for x in PR["subs"]], ("/protein/", "Protein overview &amp; calculator")),
        group("topics", "Health topics", [(turl(t), e(t["title"])) for t in T], ("/topics/", "All health topics")),
        group("guides", "Guides", [(gurl(g), e(g["title"])) for g in G], ("/guides/", "All guides")),
        group("tools", "Tools", [("/tools/vitamin-check/", "2-minute vitamin check"), ("/tools/food-finder/", "Food finder")], ("/tools/", "All tools")),
    ])
    menu = (f'<details class="menu" data-dismiss><summary aria-label="Menu"><span aria-hidden="true" class="burger"></span><span class="lbl">Menu</span></summary>'
            f'<nav class="panel" aria-label="Site menu"><a class="mg-top" href="/"{" aria-current=page" if section == "home" else ""}>Home</a>{groups}'
            f'<a class="mg-top" href="/about/"{" aria-current=page" if section == "about" else ""}>About &amp; how we write</a></nav></details>')
    srch = (f'<details class="hsearch" data-dismiss><summary aria-label="Search"><span aria-hidden="true">🔍</span><span class="lbl">Search</span></summary>'
            f'<div class="hs-panel">{search_box("hs-q")}</div></details>')
    strip = ""
    if vit:
        cur_v = "B" if vit.startswith("B") else vit
        if cur_v == "B":
            s_ = [f'<a href="/vitamin-b/"{" class=on aria-current=page" if vit == "B" else ""}>All B vitamins</a>']
            s_ += [f'<a href="{url(b)}"{" class=on aria-current=page" if vit == b["id"] else ""}><i style="--c:{b["color"]}"></i>{e(b["id"])} · {e(b["name"].split(" (")[0])}</a>' for b in BS]
            strip = f'<nav class="strip sub" aria-label="B vitamins">{"".join(s_)}</nav>'
        elif BYID[cur_v].get("subs"):
            pv = BYID[cur_v]
            s_ = [f'<a href="{url(pv)}"{" class=on aria-current=page" if not sub else ""}>Overview</a>']
            s_ += [f'<a href="{suburl(pv, x)}"{" class=on aria-current=page" if sub == x["slug"] else ""}><i style="--c:{x["color"]}"></i>{e(x["tab"])}</a>' for x in pv["subs"]]
            strip = f'<nav class="strip sub" aria-label="Types of vitamin {e(cur_v)}">{"".join(s_)}</nav>'
    if section == "protein":
        s_ = [f'<a href="{purl()}"{" class=on aria-current=page" if not psub else ""}>Overview</a>']
        s_ += [f'<a href="{purl(x)}"{" class=on aria-current=page" if psub == x["slug"] else ""}><i style="--c:{x["color"]}"></i>{e(x["tab"])}</a>' for x in PR["subs"]]
        strip = f'<nav class="strip sub" aria-label="Types of protein">{"".join(s_)}</nav>'
    trail = PAGE_CRUMBS[0]
    crumbs = ""
    if trail:
        items = [("Home", "/")] + list(trail)
        crumbs = ('<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(
            f'<li aria-current="page">{e(n)}</li>' if i == len(items) - 1 else f'<li><a href="{u}">{e(n)}</a></li>'
            for i, (n, u) in enumerate(items)) + "</ol></nav>")
    return f"""
<header class="site-header"><div class="wrap">
  <div class="bar"><a class="logo" href="/" aria-label="VitaPals home">{LOGO}<span>Vita<b>Pals</b></span></a>
  <nav class="nav" aria-label="Main">{nav}</nav>{srch}{menu}</div>
  {strip}
</div></header>
<main id="main" tabindex="-1"><div class="wrap">{crumbs}"""


def footer(scripts=""):
    explore = "".join(f'<a href="{h}">{t}</a>' for _, h, t in SECTION_NAV[:5])
    return f"""
</div></main>
<footer class="site"><div class="wrap">
  <div class="cols">
    <div><p class="nh">Explore</p>{explore}</div>
    <div><p class="nh">Tools</p><a href="/tools/vitamin-check/">2-minute vitamin check</a><a href="/tools/food-finder/">Food finder</a><a href="/protein/#needs">Protein calculator</a></div>
    <div><p class="nh">{BRAND}</p><a href="/about/">About &amp; how we write</a><a href="/about/#corrections">Report an error</a><a href="/about/#privacy">Privacy</a><a href="/about/#history">Revision history</a></div>
  </div>
  <p class="disc">{BRAND} is written for adults aged 20 and over, for general education, not medical advice. Facts are based on the NIH Office of Dietary Supplements. Talk to a doctor, dietitian or pharmacist before starting a supplement, especially if you're pregnant, take medicines or have a health condition. Clinical review has not been completed; citing a source does not imply its endorsement.</p>
  <p class="disc">© {YEAR} {BRAND} · {TAGLINE} · Content updated <time datetime="{REVIEWED_ISO}">{REVIEWED}</time></p>
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


TABLE_RE = __import__("re").compile(r'(<table class="(?:foods|ul|needs)[^"]*".*?</table>)', __import__("re").S)


def write(path, content):
    content = TABLE_RE.sub(r'<div class="tscroll">\1</div>', content)
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
INDEX.append({"t": "All 13 vitamins", "u": "/vitamins/", "k": "Overview", "x": "vitamins vitamin list all water fat soluble", "s": " ".join(vname(v) for v in V)})
INDEX.append({"t": "Tools", "u": "/tools/", "k": "Overview", "x": "tools calculator quiz", "s": "vitamin check food finder protein calculator"})
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
for food in FOODS:
    if not food.get('in'):
        assert food['s'] and food['a'], 'Quantified food requires a reference serving'
        food['source'] = 'USDA FoodData Central / recipe estimate; see source page' if food['v'] == 'P' else 'NIH Office of Dietary Supplements; see nutrient page'
write("assets/search.json", json.dumps(INDEX, ensure_ascii=False))
write("assets/foods.json", json.dumps(FOODS, ensure_ascii=False))

SEARCH = ('<div class="search" data-search><span class="ico" aria-hidden="true">🔍</span>'
          '<input type="search" placeholder="Search a vitamin, food or question… e.g. B12, spinach, tired" aria-label="Search VitaPals" autocomplete="off">'
          '<ul class="results" aria-live="polite"></ul></div>')

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
home = head(f"{BRAND}: {TAGLINE} | Vitamins Explained",
            "What each vitamin and mineral does, which US and Indian foods have it, how much adults need and when a supplement makes sense. Numbers from NIH.",
            "/", "home") + header("home") + f"""
<section class="hero-home"><div class="hero-grid"><div>
  <p class="eyebrow">{TAGLINE}</p>
  <h1>Eat better. Understand your nutrients.</h1>
  <p class="lede">Plain-language answers on vitamins, minerals and protein: what they do, which everyday US and Indian foods have them, and when a supplement makes sense.</p>
  {search_box("home-q", big=True)}
  <div class="ctas"><a class="btn" href="/tools/vitamin-check/">Take the 2-minute vitamin check →</a></div>
  <ul class="trust"><li>Numbers from NIH fact sheets</li><li>Food first, supplements second</li><li>For adults 20+</li><li>US &amp; Indian foods</li><li>Updated <time datetime="{REVIEWED_ISO}">{REVIEWED}</time></li></ul>
</div>
<div class="hero-art" aria-hidden="true"><div class="squad">{"".join(pal(x, 54, prop=False) for x in FAMILY)}</div></div>
</div></section>

<section class="block" aria-labelledby="explore-h">
  <h2 id="explore-h">Explore by topic</h2>
  <div class="cats" id="nutrients">
    <a class="cat" id="vitamins" href="/vitamins/"><span class="cat-art" aria-hidden="true">{pal(BYID["C"], 34, prop=False)}{pal(BYID["D"], 34, prop=False)}</span><h3>Vitamins</h3><p>All 13, from A to K: what each does, the best foods and how much you need.</p></a>
    <a class="cat" id="minerals" href="/minerals/"><span class="cat-art" aria-hidden="true">{pal(BYID["Fe"], 34, prop=False)}{pal(BYID["Ca"], 34, prop=False)}</span><h3>Minerals &amp; omega-3</h3><p>Iron, calcium, magnesium, zinc, iodine, selenium and omega-3 fats.</p></a>
    <a class="cat" id="protein" href="/protein/"><span class="cat-art" aria-hidden="true">{pal(PR, 34, prop=False)}</span><h3>Protein</h3><p>How much you need, from dal and paneer to eggs, fish and soy, plus a calculator.</p></a>
    <a class="cat" href="/topics/"><span class="cat-art emo" aria-hidden="true">🔬</span><h3>Health topics</h3><p>Inflammation, hormones and more, with every claim rated by evidence.</p></a>
    <a class="cat" href="/guides/"><span class="cat-art emo" aria-hidden="true">🧭</span><h3>Life-stage guides</h3><p>Vegetarian, pregnancy, over 50, active, tired: the nutrients that matter most.</p></a>
    <a class="cat" href="/tools/food-finder/"><span class="cat-art emo" aria-hidden="true">🔎</span><h3>Food finder</h3><p>Type a food, like palak or eggs, to see which nutrients it's rich in.</p></a>
  </div>
</section>

<section class="block" aria-labelledby="guides-h">
  <div class="head-row"><h2 id="guides-h">Featured guides</h2><a class="more-link" href="/guides/">All {len(G)} guides →</a></div>
  <div class="cards three">{"".join(f'<a class="card" href="{gurl(g)}"><div class="ic" aria-hidden="true">{g["icon"]}</div><h3>{e(g["title"])}</h3><p>{e(g["card"])}</p></a>' for g in G if g["slug"] in ("vegetarian", "tired", "supplements"))}</div>
</section>

<section class="block split">
  <div><h2>Popular questions</h2>
  <ul class="qlist">{"".join(f'<li><a href="{u}">{e(q)}</a></li>' for q, u in questions[:6])}</ul></div>
  <div><h2>Myth vs fact</h2><div id="myth-week" class="mythstack" aria-live="off">
    {"".join(f'<div class="myth"><div class="m"><b>Myth</b>{e(m)}</div><div class="f"><b>Fact</b>{e(f)}</div></div>' for m, f, i in featured[:2])}
  </div><p class="tnote">Myths rotate weekly. Every nutrient page has its own myth-busters.</p></div>
</section>
""" + footer('\n<script type="application/json" id="myths-data">' + json.dumps([{"m": m, "f": f, "v": i} for m, f, i in ALLMYTHS], ensure_ascii=False) + "</script>")
write("index.html", home)

# ------------------------------------------------------------------ vitamins hub (detail that used to crowd the home page)
vh = head(title_fit("All 13 Vitamins: What Each Does, Best Foods & Daily Needs", "All 13 Vitamins: Foods & Daily Needs"),
          "All 13 vitamins in one place, from A to K: what each one does, the best US and Indian foods, how much adults need, and which ones vegetarians should watch.",
          "/vitamins/", "home", kind="collection", crumbs=[("Vitamins", None)]) + header("vitamins") + f"""
<div style="max-width:760px"><h1>All 13 vitamins</h1>
<p class="lede">Your body needs 13 vitamins. Most come easily from a varied diet; a few, like B12 and D, deserve a closer look. Tap any vitamin for foods, daily needs, who's at risk and supplement advice.</p></div>
<section class="sec" aria-labelledby="water-h"><h2 id="water-h"><span aria-hidden="true">💧</span> Water-soluble vitamins</h2>
  <p class="sub">The B vitamins and vitamin C. Most have limited stores, so you need a steady supply; B12 is an exception, with stores that can last years. <a href="/vitamin-b/">Compare all 8 B vitamins →</a></p>
  <div class="vlist">{"".join(vrow(v) for v in water)}</div></section>
<section class="sec" aria-labelledby="fat-h"><h2 id="fat-h"><span aria-hidden="true">🫒</span> Fat-soluble vitamins</h2>
  <p class="sub">A, D, E and K are stored in your body, so too much from supplements can build up.</p>
  <div class="vlist">{"".join(vrow(v) for v in fat)}</div></section>
<section class="sec" aria-labelledby="forms-h"><h2 id="forms-h">Forms worth knowing</h2>
  <div class="vlist">{"".join(f'<a class="vtile" href="{suburl(v, x)}">{pal(subpal(x), 26, prop=False)}<div><strong>{e(x["tab"])}</strong><span>{e(vname(v))}</span></div></a>' for v in V for x in v.get("subs", []))}</div></section>
<section class="sec" aria-labelledby="next-h"><h2 id="next-h">Keep exploring</h2><div class="cards">
  <a class="card" href="/minerals/"><div class="ic" aria-hidden="true">{pal(BYID["Fe"], 28, prop=False)}</div><h3>Minerals &amp; omega-3</h3><p>Iron, calcium, magnesium, zinc and more.</p></a>
  <a class="card" href="/guides/vegetarian/"><div class="ic" aria-hidden="true">🥗</div><h3>Vegetarian or vegan?</h3><p>The nutrients to watch and the foods that cover them.</p></a>
  <a class="card" href="/tools/vitamin-check/"><div class="ic" aria-hidden="true">🧭</div><h3>2-minute vitamin check</h3><p>See which nutrients deserve a closer look for you.</p></a></div></section>
<p class="sources">Sources: NIH Office of Dietary Supplements vitamin fact sheets. Content updated <time datetime="{REVIEWED_ISO}">{REVIEWED}</time>.</p>
""" + footer()
write("vitamins/index.html", vh)

th = head(title_fit("Free Nutrition Tools: Vitamin Check & Food Finder"),
          "Free, private nutrition tools: a 2-minute vitamin check, a food finder for US and Indian foods, and a protein calculator. Everything runs in your browser.",
          "/tools/", "home", kind="collection", crumbs=[("Tools", None)]) + header("tools") + f"""
<div style="max-width:760px"><h1>Tools</h1><p class="lede">Quick, private helpers. Everything runs in your browser: your answers are never sent anywhere.</p></div>
<div class="cards" style="margin-top:22px">
  <a class="card" href="/tools/vitamin-check/"><div class="ic" aria-hidden="true">🧭</div><h2 class="h3">2-minute vitamin check</h2><p>Answer 11 quick questions (plus 2 optional) about how you eat and live, and see which nutrients deserve a closer look.</p><span class="go">Start the check →</span></a>
  <a class="card" href="/tools/food-finder/"><div class="ic" aria-hidden="true">🔎</div><h2 class="h3">Food finder</h2><p>Search a food, like spinach, eggs, dal or amla, to see which nutrients it's rich in and how much one serving covers.</p><span class="go">Find a food →</span></a>
  <a class="card" href="/protein/#needs"><div class="ic" aria-hidden="true">💪</div><h2 class="h3">Protein calculator</h2><p>Enter your weight to see daily protein ranges in grams, from the RDA to current US targets.</p><span class="go">Work out my protein →</span></a>
</div>
<p class="tnote" style="margin-top:18px">These tools are educational, not a diagnosis.</p>
""" + footer()
write("tools/index.html", th)


# ------------------------------------------------------------------ vitamin pages
def related_nutrients(v, d):
    ids = [i for i in (d.get("related") or RELATED.get(v["id"]) or []) if i in BYID and i != v["id"]]
    if v["id"].startswith("B") and not ismin(v):
        extra = '<a class="card" href="/vitamin-b/"><div class="ic" aria-hidden="true">🐝</div><h3>All 8 B vitamins</h3><p>Compare daily needs and the best foods side by side.</p></a>'
    else:
        extra = '<a class="card" href="/minerals/"><div class="ic" aria-hidden="true">🧂</div><h3>Minerals &amp; omega-3</h3><p>Iron, calcium, magnesium, zinc and more at a glance.</p></a>'
    if not ids:
        return ""
    return ('<section class="sec" id="related"><h2>Related nutrients</h2><div class="cards">' + "".join(
        f'<a class="card" href="{url(BYID[i])}"><div class="ic" aria-hidden="true">{pal(BYID[i], 28, prop=False)}</div><h3>{e(vname(BYID[i]))}</h3><p>{e(BYID[i]["job"])}</p></a>'
        for i in ids) + extra + "</div></section>")


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
    short = v['name'].split(' (')[0]
    title = title_fit(*d["seoTitle"]) if d.get("seoTitle") else title_fit(f"{vname(v)} ({short}): Foods, Daily Needs & Supplements", f"{vname(v)} ({short}): Foods, Needs & Supplements",
                      f"{vname(v)}: Foods, Daily Needs & Supplements", f"{vname(v)} ({short}): Foods & Daily Needs", f"{vname(v)}: Foods & Daily Needs")
    desc = fit(d["seoDesc"]) if d.get("seoDesc") else fit(f"{vname(v)}: adults need {d['needShort']}. {v['job']} Top foods, who's at risk and when a supplement helps.",
               f"{vname(v)}: adults need {d['needShort']}. Top foods (US & Indian), who's at risk, upper limits and when a supplement helps.",
               f"{vname(v)}: adults need {d['needShort']}. Top foods, who's at risk and when a supplement helps.")
    crumbs = '<a href="/">Home</a> › ' + ('<a href="/vitamin-b/">B vitamins</a> › ' if isb else "") + ('<a href="/minerals/">Minerals</a> › ' if mn else "") + e(vname(v))
    soluble = {"water": "Water-soluble", "fat": "Fat-soluble", "mineral": "Mineral", "omega": "Essential fats"}[v["type"]]
    vcrumbs = ([("Minerals", "/minerals/")] if mn else [("Vitamins", "/vitamins/")]) + ([("B vitamins", "/vitamin-b/")] if isb else []) + [(vname(v), None)]
    vcites = [(f"NIH Office of Dietary Supplements: {vname(v)} fact sheet for health professionals", nih(v))] + [tuple(x) for x in d.get("auditSources", [])]
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
    p = head(title, desc, url(v), slug(v), kind="article", crumbs=vcrumbs, faq=d["faq"], cites=vcites, about=f"{vname(v)} ({v['name']})") + header("minerals" if mn else "vitamins", None if mn else v["id"]) + f"""
<div class="vhead">{pal(v, 64, decorative=False)}<div>
  <p class="kicker">{e(v['name'])} · {soluble}</p>
  <h1>{e(vname(v))}</h1>
  <p class="lede">{e(v['job'])}</p>
</div></div>
<aside class="note"><h2>{e(vname(v))} in 30 seconds</h2><p>{e(d.get("answer") or (v["job"] + " Adults need " + d["needShort"] + ". Top foods: " + d["top3"].lower() + "; in Indian kitchens, " + ", ".join(d["indian"][:3]).lower() + ". Start with foods, and discuss supplements with your doctor when needed."))}</p></aside>
{('<p class="tnote">Updated guidance: ' + ' · '.join('<a href="'+e(u)+'">'+e(n)+'</a>' for n,u in upd) + '</p>') if (upd := [x for x in d.get('auditSources', []) if not x[0].startswith(("NIH ODS:", "FSSAI"))]) else ''}
<div class="glance" id="glance">
  <div><small>Daily need (adults)</small><strong>{e(d['needShort'])}</strong></div>
  <div><small>Upper limit</small><strong>{e(d['ulShort'])}</strong></div>
  <div><small>Best foods</small><strong>{e(d['top3'])}</strong></div>
  <div><small>Pay attention if</small><strong>{e(d['risk'][0][0])}</strong></div>
</div>
<nav class="jump" aria-label="On this page"><a href="#foods">Foods</a><a href="#needs">How much</a><a href="#risk">Who's at risk</a><a href="#signs">Signs of low levels</a><a href="#supplements">Supplements</a><a href="#forms">Forms</a><a href="#myths">Myths</a><a href="#faq">FAQ</a></nav>
{subpick}

<section class="sec two">
  <div><h2>What does {e(lname(v))} do?</h2><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in v['powers'])}</ul></div>
  <div class="note warm"><h3>🤓 Did you know?</h3><p>{e(v['fun'])}</p></div>
</section>

<section class="sec" id="foods">
  <h2>Best food sources of {e(lname(v))}</h2>
  <p class="sub">{"Per typical serving, with how much of your daily need it covers." if d["dv"] else "Per typical serving, in grams. Plant foods give ALA; fish gives EPA and DHA."}</p>
  {food_table(d)}
  <div class="two" style="margin-top:16px">
    <div class="note"><h3>🇮🇳 Also great in Indian kitchens</h3><div class="chips">{"".join(f"<span>{e(x)}</span>" for x in d['indian'])}</div></div>
    <div class="note warm"><h3>👩‍🍳 Kitchen tips</h3><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in d['tips'])}</ul></div>
  </div>
  {f'<div class="note" style="margin-top:14px" id="vegetarian"><h3>🌱 Vegetarian &amp; vegan sources</h3><p>{e(d["veg"])}</p></div>' if d.get("veg") else ""}
  <p class="tnote" style="margin-top:10px"><a href="/tools/food-finder/">Look up any food in the food finder →</a></p>
</section>

<section class="sec two" id="needs">
  <div><h2>How much {e(lname(v))} do you need a day?</h2>
    <table class="needs">{"".join(f"<tr><td>{e(a)}</td><td>{e(b)}</td></tr>" for a, b in d['needs'])}</table>
    <p class="tnote">Recommended daily amounts for adults, from the US Food and Nutrition Board.</p></div>
  <div class="note {"warm" if d["ulShort"] == "None set" else "warn"}" style="align-self:start"><h3>{"ℹ️" if d["ulShort"] == "None set" else "⚠️"} Upper limit</h3><p>{e(d['ul'])}</p></div>
</section>

<section class="sec" id="risk">
  <h2>Who might run low on {e(lname(v))}?</h2>
  <div class="risk" style="--c:{v['color']}">{"".join(f"<div><strong>{e(a)}</strong><span>{e(b)}</span></div>" for a, b in d['risk'])}</div>
</section>

<section class="sec two" id="signs">
  <div><h2>Signs of low {e(lname(v))}</h2><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in v['low'])}</ul><p class="tnote">{e(d['lowNote'])}</p></div>
  <div class="note"><h3>🩺 When to see a doctor</h3><p>These signs have many possible causes. If they last more than a couple of weeks, see a doctor. Assessment depends on diet, symptoms and history; laboratory tests are useful for some nutrients. Don't guess with high-dose supplements.</p></div>
</section>

<section class="sec" id="supplements">
  <h2>Do you need a {e(lname(v))} supplement?</h2>
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
  <h2>{e(vname(v))} myths vs facts</h2>
  <div class="mythgrid">{"".join(f'<div class="myth"><div class="m"><b>Myth</b>{e(m)}</div><div class="f"><b>Fact</b>{e(f)}</div></div>' for m, f in d['myths'])}</div>
</section>

<section class="sec" id="faq">
  <h2>{e(vname(v))}: frequently asked questions</h2>
  {"".join(f'<details class="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in d['faq'])}
</section>
""" + related_nutrients(v, d) + (f"""<section class="sec"><h2>Related guides</h2><div class="cards">{"".join(f'<a class="card" href="{gurl(g)}"><div class="ic">{g["icon"]}</div><h3>{e(g["title"])}</h3><p>{e(g["card"])}</p></a>' for g in related)}</div></section>""" if related else "") + topic_links_html(topics_for("vitamins", v["id"])) + f"""
<p class="sources">Sources: {"; ".join(f'<a href="{e(u)}" rel="noopener">{e(n)}</a>' for n, u in vcites)}. Daily needs are for healthy adults. Content updated <time datetime="{REVIEWED_ISO}">{REVIEWED}</time>. This page is for education, not medical advice.</p>
<div class="pager">
  {f'<a href="{url(prev)}"><small>← Previous</small>{e(vname(prev))}</a>' if prev else ('<a href="/minerals/"><small>← Back to</small>All minerals</a>' if mn else '<a href="/vitamins/"><small>← Back to</small>All vitamins</a>')}
  {f'<a href="{url(nxt)}"><small>Next →</small>{e(vname(nxt))}</a>' if nxt else ('<a href="/vitamins/"><small>Next →</small>All 13 vitamins</a>' if mn else '<a href="/minerals/"><small>Next →</small>Minerals &amp; omega-3</a>')}
</div>
""" + footer()
    write(f"{slug(v)}/index.html", p)

    for j, s in enumerate(subs):
        sp = subs[j - 1] if j > 0 else None
        sn = subs[j + 1] if j < len(subs) - 1 else None
        stitle = (title_fit(f"Vitamin {s['tab']} ({s['name']}): What It Is, Foods & Labels", f"Vitamin {s['tab']} ({s['name']}): Foods & Labels", f"Vitamin {s['tab']}: What It Is, Foods & Labels")
                  if s["tab"].startswith(v["id"]) else title_fit(f"{s['tab']}, a Form of Vitamin {v['id']}: Foods & Labels", f"{s['tab']} (Vitamin {v['id']}): Foods & Labels"))
        if s.get("seoTitle"):
            stitle = title_fit(*s["seoTitle"])
        sdesc = fit(s["seoDesc"]) if s.get("seoDesc") else fit(f"{s['tab']}: {s['job']} Where to find it and how to read supplement labels.", f"{s['tab']}: {s['job']}")
        sname = f"Vitamin {s['tab']}" if s["tab"].startswith(v["id"]) else s["tab"]
        slow = f"vitamin {s['tab']}" if s["tab"].startswith(v["id"]) else s["tab"].lower()
        back = f'<a href="{url(v)}"><small>← Back to</small>{e(vname(v))} overview</a>'
        scites = [tuple(x) for x in s.get("sources", [])] or [(f"NIH Office of Dietary Supplements: {vname(v)} fact sheet for health professionals", nih(v))]
        dd = D[v["id"]]
        rich = ""
        if s.get("answer"):
            rich += f'<aside class="note"><h2>{e(sname)} in 30 seconds</h2><p>{e(s["answer"])}</p></aside>'
        if s.get("benefits"):
            rich += (f'<section class="sec" id="benefits"><h2>What is {e(slow)} good for?</h2><ul class="evlist">'
                     + "".join(f'<li><div class="evh"><strong>{e(t)}</strong></div><p>{e(x)}</p></li>' for t, x in s["benefits"]) + "</ul></section>")
        if s.get("table"):
            rows = "".join(f'<tr><td>{e(f)}<small>{e(sv)}</small></td><td class="amt">{e(am)}</td><td>{dvbar(pc)}</td></tr>' for f, sv, am, pc in s["table"])
            rich += (f'<section class="sec" id="foods"><h2>Best food sources of {e(slow)}</h2><p class="sub">Per typical serving, with how much of the {e(dd["dv"])} Daily Value it covers.</p>'
                     f'<table class="foods"><thead><tr><th>Food</th><th>Amount</th><th>% Daily Value</th></tr></thead><tbody>{rows}</tbody></table>'
                     f'<p class="tnote">% Daily Value is based on {e(dd["dv"])} for adults (US FDA). Data: NIH Office of Dietary Supplements. {e(s.get("tableNote", ""))}</p>'
                     + (f'<div class="note" style="margin-top:14px" id="vegetarian"><h3>🌱 Vegetarian &amp; vegan sources of {e(slow)}</h3><p>{e(s["veg"])}</p></div>' if s.get("veg") else "")
                     + f'<p class="tnote" style="margin-top:10px"><a href="/tools/food-finder/">Look up any food in the food finder →</a></p></section>')
            rich += (f'<section class="sec two" id="needs"><div><h2>How much {e(slow)} do you need a day?</h2><table class="needs">'
                     + "".join(f"<tr><td>{e(x)}</td><td>{e(y)}</td></tr>" for x, y in dd["needs"])
                     + f'</table><p class="tnote">Recommended daily amounts for adults count all forms of {e(lname(v))}, from the US Food and Nutrition Board.</p></div>'
                     f'<div class="note warn" style="align-self:start"><h3>⚠️ Upper limit</h3><p>{e(dd["ul"])}</p></div></section>')
        others = [x for x in subs if x is not s]
        vs = ""
        if s.get("benefits") and others:
            o = others[0]
            vs = (f'<section class="sec" id="vs"><h2>{e(sname)} vs {e("Vitamin " + o["tab"] if o["tab"].startswith(v["id"]) else o["tab"])}</h2>'
                  f'<div class="two"><div class="note"><h3>{e(sname)}</h3><p>{e(s["job"])}</p></div>'
                  f'<div class="note warm"><h3><a href="{suburl(v, o)}">{e("Vitamin " + o["tab"] if o["tab"].startswith(v["id"]) else o["tab"])} →</a></h3><p>{e(o["job"])} {e(o["warn"])}</p></div></div></section>')
        sfaq = s.get("faq") or None
        faq_html = (f'<section class="sec" id="faq"><h2>{e(sname)}: frequently asked questions</h2>'
                    + "".join(f'<details class="faq"><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in sfaq) + "</section>") if sfaq else ""
        rel = ""
        if s.get("benefits"):
            rg = [g for g in G if g["slug"] in ("vegetarian", "over-50")]
            rel = ('<section class="sec" id="related"><h2>Related reading</h2><div class="cards">'
                   f'<a class="card" href="{url(v)}"><div class="ic" aria-hidden="true">{pal(v, 28, prop=False)}</div><h3>{e(vname(v))} overview</h3><p>{e(v["job"])}</p></a>'
                   + "".join(f'<a class="card" href="{url(BYID[i])}"><div class="ic" aria-hidden="true">{pal(BYID[i], 28, prop=False)}</div><h3>{e(vname(BYID[i]))}</h3><p>{e(BYID[i]["job"])}</p></a>' for i in (dd.get("related") or [])[:1])
                   + "".join(f'<a class="card" href="{gurl(g)}"><div class="ic" aria-hidden="true">{g["icon"]}</div><h3>{e(g["title"])}</h3><p>{e(g["card"])}</p></a>' for g in rg)
                   + "</div></section>")
        sp_html = head(stitle, sdesc, suburl(v, s), f"{slug(v)}-{s['slug']}", kind="article", crumbs=[("Vitamins", "/vitamins/"), (vname(v), url(v)), (s["tab"], None)],
                       faq=sfaq, cites=scites, about=f"{sname} ({s['name']})") + header("vitamins", v["id"], s["slug"]) + f"""
<div class="vhead">{pal(subpal(s), 64, decorative=False)}<div>
  <p class="kicker">{e(vname(v))} · {e(s['name'])}</p>
  <h1>{e(sname)}</h1>
  <p class="lede">{e(s['job'])}</p>
</div></div>
{rich}
<section class="sec two">
  <div><h2>What makes {e(slow)} special</h2><ul class="clean">{"".join(f"<li>{e(x)}</li>" for x in s['what'])}</ul></div>
  <div><h2>Where to find {e(slow)}</h2><div class="chips">{"".join(f'<span>{f[0]} {e(f[1])}</span>' for f in s['foods'])}</div></div>
</section>
<section class="sec two">
  <div class="note"><h3>🏷️ Label decoder</h3><p>{e(s['labelTip'])}</p></div>
  <div class="note warm"><h3>🤓 Did you know?</h3><p>{e(s['fun'])}</p></div>
</section>
<section class="sec two">
  <div class="note warn"><h3>⚠️ Heads-up</h3><p>{e(s['warn'])}</p></div>
  <div class="note"><h3>📏 How much {e(lname(v))} do you need?</h3><p>{e(dd['needShort'])} for most adults. Upper limit: {e(dd['ulShort'])}.</p><p><a href="{url(v)}#foods">See top foods &amp; full details →</a></p></div>
</section>
{vs}{faq_html}{rel}
<p class="sources">Sources: {"; ".join(f'<a href="{e(u)}" rel="noopener">{e(n)}</a>' for n, u in scites)}. Content updated <time datetime="{REVIEWED_ISO}">{REVIEWED}</time>. General education, not medical advice.</p>
<div class="pager">
  {f'<a href="{suburl(v, sp)}"><small>← Previous</small>{e(sp["tab"])}</a>' if sp else back}
  {f'<a href="{suburl(v, sn)}"><small>Next →</small>{e(sn["tab"])}</a>' if sn else back.replace("← Back to", "Back to →")}
</div>
""" + footer()
        write(f"{slug(v)}/{s['slug']}/index.html", sp_html)

# ------------------------------------------------------------------ B hub
hub = head(title_fit("B Vitamins: All 8 Explained, Foods & Daily Needs"),
           "The 8 B vitamins in one place: what each does, how much you need, the best foods, and who should pay attention.",
           "/vitamin-b/", "vitamin-b", kind="article", crumbs=[("Vitamins", "/vitamins/"), ("B vitamins", None)], about="B vitamins",
           cites=[(f"NIH Office of Dietary Supplements: {vname(b)} fact sheet", nih(b)) for b in BS]) + header("vitamins", "B") + f"""
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
mhub = head(title_fit("Minerals & Omega-3: Iron, Calcium, Magnesium, Zinc", "Minerals & Omega-3: Iron, Calcium, Zinc & More"),
            fit("Iron, calcium, magnesium, zinc, iodine, selenium and omega-3 in one place: how much adults need, the best US and Indian foods, and who should watch them."),
            "/minerals/", "minerals", kind="article", crumbs=[("Minerals", None)], about="Dietary minerals and omega-3 fats",
            cites=[(f"NIH Office of Dietary Supplements: {vname(m)} fact sheet", nih(m)) for m in M]) + header("minerals") + f"""
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
<p class="sources">Sources: NIH Office of Dietary Supplements fact sheets: {", ".join(f'<a href="{nih(m)}" rel="noopener">{e(vname(m))}</a>' for m in M)}. Content updated {REVIEWED}.</p>
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
    if g['slug'] == 'vegetarian':
        us_f = ['Fortified plant milk (vegan; check B12 and calcium labels)', 'Beans and lentils', 'Leafy greens', 'Almonds', 'UV-exposed mushrooms', 'Milk or yogurt (eggless vegetarian only)', 'Eggs (ovo-vegetarian only)']
        in_f = ['Dal', 'Chana', 'Rajma', 'Palak', 'Til', 'Milk or curd (eggless vegetarian only)', 'Calcium-set tofu']
    foods_block = f"""<section class="sec"><h2>Foods to lean on</h2><p class="sub">Food first. These cover the vitamins above.</p><div class="two">
  <div class="note"><h3>🛒 Everyday picks</h3><div class="chips">{"".join(f"<span>{e(x)}</span>" for x in us_f[:8])}</div></div>
  <div class="note"><h3>🇮🇳 In Indian kitchens</h3><div class="chips">{"".join(f"<span>{e(x)}</span>" for x in in_f[:8])}</div></div></div></section>"""
    keys = "".join(
        f'<a href="{url(BYID[k])}">{pal(BYID[k], 34, prop=False)}<div><strong>{e(vname(BYID[k]))}</strong><span>{e(t)}</span></div></a>' for k, t in g["key"])
    srcs = ", ".join(f'<a href="{nih(BYID[k])}" rel="noopener">{e(vname(BYID[k]))}</a>' for k in g["sources"])
    gcites = [(f"NIH Office of Dietary Supplements: {vname(BYID[k])} fact sheet", nih(BYID[k])) for k in g["sources"]] + ([tuple(g["extraSource"])] if g.get("extraSource") else [])
    gp = head(title_fit(g["seo"], g["seo"].split(":")[0], g["title"]), fit(g["card"] + " " + g["intro"].split(". ")[0] + ".", g["card"]), gurl(g),
              kind="article", crumbs=[("Guides", "/guides/"), (g["title"], None)], cites=gcites, about=g["title"]) + header("guides") + f"""
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
<p class="sources">Sources: NIH Office of Dietary Supplements fact sheets: {srcs}{('; <a href="' + g['extraSource'][1] + '" rel="noopener">' + e(g['extraSource'][0]) + '</a>') if g.get('extraSource') else ''}. Content updated {REVIEWED}. General education, not medical advice.</p>
<div class="pager">
  {f'<a href="{gurl(gprev)}"><small>← Previous guide</small>{e(gprev["title"])}</a>' if gprev else '<a href="/guides/"><small>← Back to</small>All guides</a>'}
  {f'<a href="{gurl(gnext)}"><small>Next guide →</small>{e(gnext["title"])}</a>' if gnext else '<a href="/topics/"><small>Next →</small>Health topics</a>'}
</div>
""" + footer()
    write(f"guides/{g['slug']}/index.html", gp)

gi = head(title_fit("Vitamin Guides for Every Stage of Life"), "Vitamin guides for adults: vegetarians, your 20s to 40s, over 50, pregnancy, active lifestyles, supplements and tiredness.", "/guides/",
          kind="collection", crumbs=[("Guides", None)]) + header("guides") + f"""
<h1>Guides</h1><p class="lede">Practical vitamin advice for adults, for every stage of life.</p>
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
    tp = head(title_fit(t["seo"], t["seo"].split(":")[0], t["title"]), fit(t["card"], t["intro"]), turl(t), "home", kind="article",
              crumbs=[("Health topics", "/topics/"), (t["title"], None)], faq=t["faq"], cites=[tuple(x) for x in t["sources"]], about=t["title"]) + header("topics") + f"""
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
<p>Content updated {REVIEWED}. This page is for general education, not medical advice. It hasn't been reviewed by a medical professional yet.</p></section>
<div class="pager"><a href="/topics/"><small>← Back to</small>Health topics</a><a href="/vitamins/"><small>Next →</small>All 13 vitamins</a></div>
""" + footer()
    write(f"topics/{t['slug']}/index.html", tp)

ti = head(title_fit("Health Topics: Evidence-Rated Answers"), "Common health questions like inflammation and hormonal imbalance, answered in plain language with every claim rated by the strength of its evidence.", "/topics/",
          kind="collection", crumbs=[("Health topics", None)]) + header("topics") + f"""
<h1>Health topics</h1><p class="lede">Plain answers to common health questions. Every claim gets a badge, so you can see how strong the evidence is.</p>
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
        '<p>Content updated {rev}. This page is for general education, not medical advice. It hasn\'t been reviewed by a medical professional yet.</p></section>')
psources = PSRC.format(n=len(PR["sources"]), rev=REVIEWED, items="".join(f'<li><a href="{e(u)}" rel="noopener">{e(n)}</a></li>' for n, u in PR["sources"]))
pguides = [g for g in G if g["slug"] in PR["guides"]]
CALC = """<div class="tool pcalc" id="pcalc" hidden>
  <h3>Your number</h3>
  <div class="pcalc-in"><label for="pc-w">Your weight</label><input id="pc-w" type="number" inputmode="decimal" min="30" max="300" placeholder="e.g. 65">
  <select id="pc-u" aria-label="Unit"><option value="kg">kg</option><option value="lb">lb</option></select></div>
  <div id="pc-out" aria-live="polite"><p class="tnote">Enter your weight to see a daily range in grams. Answers are not sent to a server; you can optionally save them on your device.</p></div>
</div>"""
pp = head(title_fit("Protein: How Much You Need & the Best Sources (US & Indian)", "Protein: How Much You Need & the Best Sources"),
          fit("Protein for adults: traditional RDA and current dietary targets, the best US and Indian sources, protein powders, and myths checked with evidence."),
          purl(), "protein", kind="article", crumbs=[("Protein", None)], faq=PR["faq"], cites=[tuple(x) for x in PR["sources"]], about="Dietary protein") + header("protein") + f"""
<div class="vhead">{pal(PR, 64, decorative=False)}<div>
  <p class="kicker">Macronutrient · Made of amino acids</p>
  <h1>Protein</h1>
  <p class="lede">{e(PR['job'])}</p>
</div></div>
<aside class="note"><h2>30-second summary</h2><p>{e(PR['job'])} Start with foods, compare the reference intake for your life stage, and discuss supplements when needed.</p></aside>
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
    xh = head(title_fit(f"{x['tab']}: Protein, Best Picks & What to Watch", f"{x['tab']}: Protein & Best Picks"),
              fit(f"{x['tab']} as a protein source: {x['job']} Grams per serving, US and Indian picks, and what to watch.", f"{x['tab']} as a protein source: {x['job']}"),
              purl(x), f"protein-{x['slug']}", kind="article", crumbs=[("Protein", "/protein/"), (x["tab"], None)],
              cites=[tuple(y) for y in PR["sources"]], about=f"{x['tab']} as a protein source") + header("protein", psub=x["slug"]) + f"""
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
  <div class="note"><h3>📏 How much protein do you need?</h3><p>Compare the traditional adult RDA (0.8 g/kg/day) with the 2025–2030 US dietary target (1.2–1.6 g/kg/day). Age, activity and medical circumstances affect individual advice.</p><p><a href="/protein/#needs">See daily needs &amp; your number →</a></p></div>
</section>
{psources}
<div class="pager">
  {f'<a href="{purl(xp)}"><small>← Previous</small>{e(xp["tab"])}</a>' if xp else back}
  {f'<a href="{purl(xn)}"><small>Next →</small>{e(xn["tab"])}</a>' if xn else back.replace("← Back to", "Back to →")}
</div>
""" + footer()
    write(f"protein/{x['slug']}/index.html", xh)

# ------------------------------------------------------------------ tools
ff = head(title_fit("Food Finder: Which Vitamins Are in Your Food?"),
          "Search any food, like spinach, eggs, milk or dal, to see which vitamins it's rich in and how much of your daily need it covers.",
          "/tools/food-finder/", crumbs=[("Tools", "/tools/"), ("Food finder", None)]) + header("finder") + """
<div style="max-width:760px"><h1>Food finder</h1><p class="lede">Type a food to see which vitamins it's rich in, and how much of your daily need one serving covers.</p></div>
<div class="tool" style="margin-top:20px" id="food-finder">
  <div class="search"><span class="ico" aria-hidden="true">🔍</span><input id="ff-q" type="search" placeholder="Try spinach, eggs, milk, chickpeas, amla…" aria-label="Search foods" autocomplete="off"></div>
  <label for="ff-diet">Diet</label><select id="ff-diet"><option value="all">All foods</option><option value="veg">Eggless vegetarian</option><option value="ovo">Vegetarian with eggs</option><option value="vegan">Vegan</option><option value="pes">Pescatarian</option></select>
  <label for="ff-servings">Reference servings</label><input id="ff-servings" type="number" min="0.25" max="10" step="0.25" value="1"><p class="tnote">Compare amounts using each food’s declared serving. Mixed dishes and packaged foods vary; check ingredient labels for your dietary needs and allergies.</p><div class="pop" id="ff-pop"></div>
  <div id="ff-out" aria-live="polite"></div>
  <noscript><p>The food finder needs JavaScript. You can still browse foods on each vitamin page.</p></noscript>
</div>
<p class="tnote" style="margin-top:12px">Vitamin and mineral values use NIH food tables; protein values use USDA data or labeled recipe estimates on the linked source page. % Daily Value is a label reference, not your personal requirement. Indian kitchen suggestions without amounts are qualitative only.</p>
""" + footer()
write("tools/food-finder/index.html", ff)

vc = head(title_fit("2-Minute Vitamin Check: Which Vitamins to Watch?"),
          "Answer 13 quick questions about your diet and lifestyle to see which vitamins and minerals deserve a closer look. Free, private and educational.",
          "/tools/vitamin-check/", crumbs=[("Tools", "/tools/"), ("Vitamin check", None)]) + header("check") + """
<div style="max-width:760px"><h1>2-minute vitamin check</h1><p class="lede" id="vcheck-intro">Answer 13 quick questions about how you eat and live. We'll point out which vitamins deserve a closer look, and the foods that help. Answers are processed on your device. Saving is optional.</p></div>
<form class="tool" id="vcheck" style="margin-top:20px" novalidate aria-describedby="vcheck-intro">
  <div class="vc-progress"><label for="vcheck-bar" class="sr-only">Questions answered</label><progress id="vcheck-bar" max="11" value="0"></progress><p class="vprog" id="vcheck-prog" aria-live="polite">0 of 11 answered</p></div>
  <div id="vcheck-errors" class="err-summary" tabindex="-1" hidden></div>
  <fieldset class="q"><legend>1. How do you eat?</legend><div class="opts">
    <label><input type="radio" name="diet" value="omni" required> I eat meat or fish</label>
    <label><input type="radio" name="diet" value="veg"> Eggless vegetarian (dairy allowed)</label>
    <label><input type="radio" name="diet" value="ovo"> Vegetarian with eggs</label><label><input type="radio" name="diet" value="pes"> Pescatarian (fish, no meat)</label><label><input type="radio" name="diet" value="vegan"> Vegan (no animal foods)</label></div></fieldset>
  <fieldset class="q"><legend>2. Your age</legend><div class="opts">
    <label><input type="radio" name="age" value="u50" required> 20–49</label>
    <label><input type="radio" name="age" value="50"> 50</label>
    <label><input type="radio" name="age" value="51"> 51–64</label><label><input type="radio" name="age" value="65"> 65–70</label><label><input type="radio" name="age" value="71"> 71+</label></div></fieldset>
  <fieldset class="q"><legend>3. Are you pregnant, breastfeeding or planning a pregnancy?</legend><div class="opts">
    <label><input type="radio" name="preg" value="no" required> No</label>
    <label><input type="radio" name="preg" value="planning"> Planning pregnancy</label><label><input type="radio" name="preg" value="pregnant"> Pregnant</label><label><input type="radio" name="preg" value="breastfeeding"> Breastfeeding</label></div></fieldset>
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
  <fieldset class="q"><legend>12. Do you smoke, or have several alcoholic drinks most days? <span class="opt">(optional)</span></legend><div class="opts">
    <label><input type="checkbox" name="smoke"> I smoke</label>
    <label><input type="checkbox" name="alcohol"> Several drinks most days</label></div></fieldset>
  <fieldset class="q"><legend>13. Do you take any of these medicines regularly? <span class="opt">(optional)</span></legend><div class="opts">
    <label><input type="checkbox" name="metformin"> Metformin (diabetes)</label>
    <label><input type="checkbox" name="acid"> Acid reducers (omeprazole, pantoprazole, famotidine…)</label>
    <label><input type="checkbox" name="warfarin"> Warfarin</label>
    <label><input type="checkbox" name="otherblood"> Other blood thinner</label><label><input type="checkbox" name="supplements"> I take supplements</label><label><input type="checkbox" name="seizure"> Seizure medicines</label></div></fieldset>
  <div class="vc-actions"><label class="remember"><input type="checkbox" name="remember"> Save my answers on this device (optional)</label>
  <div class="row"><button class="btn" type="submit">See my next steps</button><button type="button" id="forget-check" class="btn ghost">Clear saved answers</button></div></div>
  <div class="res" id="vcheck-out"></div>
  <noscript><p>The vitamin check needs JavaScript.</p></noscript>
</form>
<p class="tnote" style="margin-top:12px">Designed for adults aged 20 and over. This is an educational tool, not a diagnosis. Assessment may include diet, symptoms, medical history and appropriate laboratory testing.</p>
""" + footer()
write("tools/vitamin-check/index.html", vc)

# ------------------------------------------------------------------ about
about = head(title_fit("About Us & How We Write"), f"How {BRAND} researches and writes about nutrition: who it's for, where the facts come from, how evidence is rated and what we never do.", "/about/",
             kind="about", crumbs=[("About", None)]) + header("about") + f"""
<div class="prose"><h1>About VitaPals</h1>
<p class="lede">VitaPals explains vitamins in plain language, so you can make sense of what you eat and have better conversations with your doctor.</p>
<h2>Who it's for</h2><p>VitaPals is written for adults aged 20 and over. Children and teens have different needs and safe limits, so please ask a pediatrician about them.</p>
<h2>Food first, science always</h2><p>Most people can get most vitamins from a varied diet. We show real foods, with real amounts, before we ever talk about supplements. We include everyday US and Indian foods, because that's how many of our readers eat.</p>
<h2>Where our facts come from</h2><p>Daily needs, upper limits, food amounts and medicine interactions come from the <a href="https://ods.od.nih.gov/factsheets/list-VitaminsMinerals/" rel="noopener">NIH Office of Dietary Supplements</a> fact sheets for health professionals, which are based on the US Food and Nutrition Board. Every page links to its source.</p>
<h2 id="evidence">How we rate evidence</h2><p>Topic badges are editorial summaries, not a validated evidence-grading system or proof of causation. Read the underlying sources and context. Clinical review and a claim-by-claim evidence appraisal remain pending:</p>
<ul class="clean"><li>🟢 <strong>Established guidance</strong>: summarizes guidance discussed in the page sources; this does not establish that every associated benefit is causal.</li><li>🟡 <strong>Limited evidence</strong>: promising or consistent studies, but smaller, mixed or mostly observational.</li><li>⚪ <strong>Not enough evidence</strong>: too little good research to say either way.</li><li>🔴 <strong>Myth</strong>: the evidence says no, or it isn't a recognized condition.</li></ul>
<h2>How we keep it current</h2><p>Dates indicate content updates, not clinical review. No qualified clinical reviewer is currently credited. Medical and dietetic review remains pending, especially for pregnancy, supplement doses and medication interactions.</p>
<h2>What we don't do</h2><p>We don't diagnose, and we don't recommend specific supplement brands. Our vitamin check is educational. It can point you toward questions to ask, but assessment may include diet, symptoms, medical history and appropriate laboratory testing.</p>
<h2 id="corrections">Corrections and contact</h2><p><a href="https://github.com/AnveshGannamraju/myvitapals/issues/new">Report a content error or contact the project maintainer on GitHub</a> (account required). Include the page URL, the wording and a reliable source. Reports are public: do not include personal health information. Reports can be tracked in the repository issue list.</p>
<h2 id="privacy">Privacy and disclosures</h2><p>Searches and tool answers are processed in your browser. Saving questionnaire answers is optional and uses this browser’s local storage; use Clear saved answers to remove them. The site uses no advertising trackers and no cookies. To learn which pages help people, it counts visits with GoatCounter, a privacy-friendly analytics service: the page address (without anything after a "?"), the referring website, screen size, which links are clicked, the matched food from our list when the food finder is used, and whether the vitamin check was started and completed. It never records what you type, your vitamin check answers or results, your weight, or anything that identifies you, and it is switched off if your browser sends Do Not Track or Global Privacy Control. The hosting provider may process ordinary request logs. External links follow the destination’s privacy policy. No supplement affiliate purchase links are used in these tools.</p>
<h2>Editorial accountability</h2><p>Content is maintained by the VitaPals project. No clinical credentials or independent medical review are claimed. A content update is an edit; a fact-check verifies a specific claim against its source; medical review requires a qualified named professional and a documented scope.</p>
<h2 id="history">Revision history</h2><p>November 24, 2026: expanded the vitamin D3, B1, B5, B6, B7 and folate pages (quick answers, vegetarian and Indian sources, more NIH food-table entries, FAQs), added related-nutrient links and privacy-friendly visit counts. Clinical review pending.</p><p>November 5, 2026: corrected diet-specific recommendations, protein reference wording, vitamin D testing, B6 limits, folate/MTHFR and methotrexate context, calcium absorption and questionnaire privacy. Clinical review pending. <a href="https://github.com/AnveshGannamraju/myvitapals/commits">Published change history</a>.</p>
<h2>Medical disclaimer</h2><p>VitaPals is for general education and isn't a substitute for professional medical advice. Talk to a doctor, registered dietitian or pharmacist before starting a supplement, especially if you're pregnant, breastfeeding, take medicines or have a health condition.</p>
</div>
""" + footer()
write("about/index.html", about)

nf = head(f"Page not found | {BRAND}", "This page wandered off.", "/404.html", noindex=True) + header() + f"""
<div style="text-align:center;padding:40px 0">{pal(BYID['C'], 80)}<h1 style="margin-top:12px">This page wandered off</h1>
<p class="lede" style="margin:12px auto 22px">Maybe it went to get some sunshine with vitamin D. Try searching instead:</p>
<div style="display:flex;justify-content:center">{SEARCH}</div><p style="margin-top:22px"><a class="btn" href="/">Go home</a></p></div>
""" + footer()
write("404.html", nf)

# ------------------------------------------------------------------ sitemap, robots, llms.txt, IndexNow, favicon, og
# The sitemap is built from every page head() produced, so new pages are included automatically; noindex pages are left out.
paths = [pth for pth, _, _, noidx in PAGES if not noidx]
assert len(paths) == len(set(paths)), "duplicate page paths"
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      "".join(f"  <url><loc>{SITE}{p}</loc><lastmod>{REVIEWED_ISO}</lastmod></url>\n" for p in paths) + "</urlset>\n")

ua = lambda bots: "".join(f"User-agent: {b}\n" for b in bots)
write("robots.txt", f"""# {BRAND} ({SITE}) - {TAGLINE}
# Everything public on this site is educational and may be crawled. Folders starting with "_" are build sources
# and are not published by GitHub Pages; the Disallow lines below only matter if the site moves to another host.

# Search engines and AI answer engines: index pages and link to them as sources.
{ua(SEARCH_BOTS)}Allow: /
Disallow: /_src/
Disallow: /_social/

# AI model training crawlers, kept separate from search. Blocking these does not remove the site from
# ChatGPT search, Claude, Perplexity, Google or Bing results. Change Allow to Disallow to opt out of training.
{ua(TRAINING_BOTS)}{AI_TRAINING}: /

# Everyone else
User-agent: *
Allow: /
Disallow: /_src/
Disallow: /_social/

Sitemap: {SITE}/sitemap.xml
""")

# llms.txt: an optional, plain-text map of the site for AI tools (not an indexing requirement).
def llm_line(pth, label, note):
    return f"- [{label}]({SITE}{pth}): {note}"
nutrient_note = lambda v: f"adults need {D[v['id']]['needShort']}; upper limit {D[v['id']]['ulShort'].lower() if D[v['id']]['ulShort'] == 'None set' else D[v['id']]['ulShort']}; best foods: {D[v['id']]['top3']}."
llms = [f"# {BRAND}", "", f"> {BRAND_DESC} Tagline: {TAGLINE}.", "",
        f"{BRAND} is a free, static, ad-free educational website for adults aged 20 and over (not children). Pages are plain HTML. "
        "Daily needs (RDA/AI), upper limits (UL), food amounts and medicine interactions come from the NIH Office of Dietary Supplements "
        "health-professional fact sheets; % Daily Value uses US FDA label values; protein food values use USDA FoodData Central. "
        "Every page links its sources and shows when it was last updated. Health-topic pages rate claims with evidence badges "
        "(established guidance, limited evidence, not enough evidence, myth).", "",
        f"Important: content is general education, not medical advice. It has not been clinically reviewed by a named dietitian or doctor. "
        f"Content last updated {REVIEWED}. When citing, please link the specific page.", "",
        "## Vitamins", llm_line("/vitamins/", "All 13 vitamins", "overview of every vitamin, water- and fat-soluble.")] + [llm_line(url(v), f"{vname(v)} ({v['name'].split(' (')[0]})", nutrient_note(v)) for v in V] + \
       [llm_line(suburl(v, x), f"{x['tab']} ({vname(v)})", x["job"]) for v in V for x in v.get("subs", [])] + \
       [llm_line("/vitamin-b/", "B vitamins hub", "all 8 B vitamins compared: daily needs and best foods.")] + \
       ["", "## Minerals and omega-3", llm_line("/minerals/", "Minerals overview", "iron, calcium, magnesium, zinc, iodine, selenium and omega-3 at a glance.")] + \
       [llm_line(url(m), vname(m), nutrient_note(m)) for m in M] + \
       ["", "## Protein", llm_line(purl(), "Protein", f"how much adults need ({PR['needShort']}), best US and Indian sources, powders and myths.")] + \
       [llm_line(purl(x), f"{x['tab']} (protein)", x["job"]) for x in PR["subs"]] + \
       ["", "## Life-stage guides"] + [llm_line(gurl(g), g["title"], g["card"]) for g in G] + \
       ["", "## Health topics (evidence-rated)"] + [llm_line(turl(t), t["title"], t["card"]) for t in T] + \
       ["", "## Tools", llm_line("/tools/", "Tools", "overview of the free tools."), llm_line("/tools/food-finder/", "Food finder", "search a food to see which nutrients it is rich in (needs JavaScript; the same data is on each nutrient page)."),
        llm_line("/tools/vitamin-check/", "2-minute vitamin check", "educational questionnaire; runs in the browser, nothing is sent to a server."),
        "", "## About", llm_line("/about/", "About and how we write", "audience, sources, evidence ratings, corrections policy, privacy and medical disclaimer."),
        "", "## Optional", llm_line("/sitemap.xml", "Sitemap", "every public page."), ""]
write("llms.txt", "\n".join(llms))
write(f"{INDEXNOW_KEY}.txt", INDEXNOW_KEY)
# Minified stylesheet for the site; edit assets/style.css (the readable source) and rebuild.
_css = (ROOT / "assets/style.css").read_text(encoding="utf-8")
_re = __import__("re")
_css = _re.sub(r"/\*.*?\*/", "", _css, flags=_re.S)
_css = _re.sub(r"\s+", " ", _css)
_css = _re.sub(r"\s*([{}:;,>])\s*", r"\1", _css).replace(";}", "}")
_css = _re.sub(r"\band\(", "and (", _css)
write("assets/style.min.css", _css.strip() + "\n")
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
     "color": PR["color"], "lead": "Compare protein reference ranges by body weight. Explore dals, dairy, eggs, fish and soy."}] + [
    {"name": f"protein-{x['slug']}", "svg": pal(psubpal(x), 260, prop=False), "kicker": "Protein source", "title": x["tab"], "color": x["color"], "lead": x["job"]}
    for x in PR["subs"]] + [
    {"name": "minerals", "svg": "".join(pal(m, 110) for m in M[:6]), "kicker": "Minerals & omega-3", "title": "Iron, calcium & friends",
     "color": "#1e6b52", "lead": "How much you need, the best US and Indian foods, and who should watch them.", "multi": 1}], ensure_ascii=False), encoding="utf-8")

print(f"Built {len(paths)} indexable pages + 404, sitemap, robots, llms.txt, IndexNow key, favicon, search & food data.")
