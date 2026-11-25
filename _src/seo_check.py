"""SEO and structured-data checks for the generated site.

Run after `python3 _src/build.py`:  python3 _src/seo_check.py
Exits non-zero on errors. Uses only the Python standard library.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://myvitapals.com"
errors, warnings = [], []


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title, self.meta, self.links, self.ids = "", {}, [], set()
        self.canonical, self.headings, self.ld, self.imgs = None, [], [], []
        self.hrefs, self.lang = [], None
        self._in_title = self._in_ld = False
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            k = a.get("name") or a.get("property")
            if k:
                if k in self.meta and k not in ("og:image",):
                    errors.append(f"{self.path}: duplicate meta {k}")
                self.meta[k] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        elif tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld, self._buf = True, ""
        elif tag == "img":
            self.imgs.append(a)
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_ld:
            self._in_ld = False
            self.ld.append(self._buf)

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_ld:
            self._buf += data


def url_for(p):
    rel = p.relative_to(ROOT).as_posix()
    return "/" + rel[: -len("index.html")] if rel.endswith("index.html") else "/" + rel


pages = {}
for f in sorted(ROOT.rglob("*.html")):
    if any(part.startswith(("_", ".")) for part in f.relative_to(ROOT).parts):
        continue
    pg = Page()
    pg.path = url_for(f)
    pg.feed(f.read_text(encoding="utf-8"))
    pages[pg.path] = pg

indexable = {u: p for u, p in pages.items() if "noindex" not in p.meta.get("robots", "")}

# ---- metadata
for kind, getter, lo, hi in (("title", lambda p: p.title.strip(), 15, 70), ("description", lambda p: p.meta.get("description", ""), 50, 160)):
    seen = defaultdict(list)
    for u, p in indexable.items():
        v = getter(p)
        if not v:
            errors.append(f"{u}: missing {kind}")
            continue
        seen[v].append(u)
        if not lo <= len(v) <= hi:
            warnings.append(f"{u}: {kind} length {len(v)} (aim {lo}-{hi})")
    for v, us in seen.items():
        if len(us) > 1:
            errors.append(f"duplicate {kind} on {us}")

for u, p in indexable.items():
    if p.lang != "en":
        errors.append(f"{u}: <html lang> missing")
    if p.canonical != SITE + u:
        errors.append(f"{u}: canonical {p.canonical} != {SITE + u}")
    for k in ("og:title", "og:description", "og:url", "og:image", "og:type", "og:site_name", "twitter:card"):
        if not p.meta.get(k):
            errors.append(f"{u}: missing {k}")
    if p.meta.get("og:url") != SITE + u:
        errors.append(f"{u}: og:url mismatch")
    og = p.meta.get("og:image", "")
    if og.startswith(SITE) and not (ROOT / urlsplit(og).path.lstrip("/")).exists():
        errors.append(f"{u}: og:image file missing {og}")
    h = p.headings
    if h.count(1) != 1:
        errors.append(f"{u}: {h.count(1)} <h1> elements")
    for a, b in zip(h, h[1:]):
        if b > a + 1:
            warnings.append(f"{u}: heading jumps h{a}->h{b}")
            break
    for img in p.imgs:
        if "alt" not in img:
            errors.append(f"{u}: <img> without alt")

# ---- links and anchors
for u, p in pages.items():
    for href in p.hrefs:
        if href.startswith(("http", "mailto:", "tel:", "//")):
            continue
        parts = urlsplit(href)
        target = unquote(parts.path) if parts.path else u
        if not target.startswith("/"):
            errors.append(f"{u}: relative link {href}")
            continue
        file = ROOT / target.lstrip("/")
        if target.endswith("/"):
            file = file / "index.html"
        if not file.exists():
            errors.append(f"{u}: broken link {href}")
            continue
        if parts.fragment:
            tp = pages.get(target if target.endswith("/") else url_for(file))
            if tp and parts.fragment not in tp.ids:
                errors.append(f"{u}: broken anchor {href}")

# ---- structured data
for u, p in pages.items():
    types = Counter()
    for raw in p.ld:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as ex:
            errors.append(f"{u}: invalid JSON-LD ({ex})")
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else data
        if data.get("@context") not in ("https://schema.org", "https://schema.org/"):
            errors.append(f"{u}: JSON-LD missing schema.org @context")
        for n in nodes:
            t = n.get("@type")
            types[t if isinstance(t, str) else ",".join(t)] += 1
            if t == "FAQPage":
                for q in n.get("mainEntity", []):
                    if not q.get("name") or not q.get("acceptedAnswer", {}).get("text"):
                        errors.append(f"{u}: FAQ entry incomplete")
                    # FAQ markup must match visible content
                    html_text = (ROOT / (u.lstrip("/") + "index.html" if u.endswith("/") else u.lstrip("/"))).read_text(encoding="utf-8")
                    import html as _h
                    if _h.escape(q["name"], quote=True) not in html_text and q["name"] not in html_text:
                        errors.append(f"{u}: FAQ question not visible: {q['name'][:50]}")
            if t == "BreadcrumbList":
                items = n.get("itemListElement", [])
                for i, it in enumerate(items, 1):
                    if it.get("position") != i or not it.get("name"):
                        errors.append(f"{u}: bad breadcrumb item {i}")
                    if i < len(items) and not it.get("item"):
                        errors.append(f"{u}: breadcrumb item {i} missing URL")
            if t in ("Article", "MedicalWebPage"):
                for k in ("headline", "dateModified", "author", "publisher"):
                    if not n.get(k):
                        errors.append(f"{u}: {t} missing {k}")
                if len(n.get("headline", "")) > 110:
                    warnings.append(f"{u}: headline over 110 chars")
            for bad in ("aggregateRating", "review", "reviewedBy"):
                if bad in n:
                    errors.append(f"{u}: unexpected {bad} in structured data")
    p.types = types
    if u in indexable and u != "/" and not types.get("BreadcrumbList"):
        warnings.append(f"{u}: no BreadcrumbList")

# ---- sitemap, robots, llms.txt
sm_file = ROOT / "sitemap.xml"
ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
locs = [e.text for e in ET.parse(sm_file).getroot().findall("s:url/s:loc", ns)]
if len(locs) != len(set(locs)):
    errors.append("sitemap has duplicate URLs")
want = {SITE + u for u in indexable}
for missing in sorted(want - set(locs)):
    errors.append(f"sitemap missing {missing}")
for extra in sorted(set(locs) - want):
    errors.append(f"sitemap lists non-indexable or missing page {extra}")

robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
if f"Sitemap: {SITE}/sitemap.xml" not in robots:
    errors.append("robots.txt missing Sitemap line")
groups, cur = {}, []
for line in robots.splitlines():
    line = line.split("#")[0].strip()
    if not line:
        continue
    k, _, v = line.partition(":")
    k, v = k.strip().lower(), v.strip()
    if k == "user-agent":
        if cur and groups.get(cur[-1]) not in (None, []):
            cur = []
        cur.append(v)
        groups.setdefault(v, [])
    elif k in ("allow", "disallow"):
        for ua in cur:
            groups[ua].append((k, v))
for bot in ("Googlebot", "Bingbot", "OAI-SearchBot", "Claude-SearchBot", "PerplexityBot"):
    rules = groups.get(bot)
    if rules is None:
        errors.append(f"robots.txt has no group for {bot}")
    elif ("disallow", "/") in rules:
        errors.append(f"robots.txt blocks {bot}")
    elif ("allow", "/") not in rules:
        errors.append(f"robots.txt does not allow / for {bot}")

llms = ROOT / "llms.txt"
if llms.exists():
    t = llms.read_text(encoding="utf-8")
    if not t.startswith("# "):
        errors.append("llms.txt should start with an H1")
    for link in re.findall(r"\]\((https://myvitapals\.com[^)]*)\)", t):
        path = link[len(SITE):] or "/"
        if path not in pages and not (ROOT / path.lstrip("/")).is_file():
            errors.append(f"llms.txt links to missing page {link}")
else:
    warnings.append("no llms.txt")

for w in warnings:
    print("WARN ", w)
for er in errors:
    print("ERROR", er)
print(f"{len(pages)} pages ({len(indexable)} indexable), {len(locs)} sitemap URLs, "
      f"structured data types: {dict(sum((p.types for p in pages.values()), Counter()))}")
print(f"{'FAIL' if errors else 'PASS'}: {len(errors)} errors, {len(warnings)} warnings")
sys.exit(1 if errors else 0)
