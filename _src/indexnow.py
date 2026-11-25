"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver, ...) which pages changed.

Usage:
  python3 _src/indexnow.py                 # pages whose HTML changed in the last commit
  python3 _src/indexnow.py --all           # every URL in sitemap.xml (first run / after big changes)
  python3 _src/indexnow.py --dry-run ...   # print the payload, send nothing

Run it only after the site is live, because the engines fetch /<key>.txt from the live site to verify it.
Google does not use IndexNow; it reads sitemap.xml instead. Uses only the Python standard library.
"""
import json
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://myvitapals.com"
KEY = re.search(r'INDEXNOW_KEY = "([^"]+)"', (ROOT / "_src/build.py").read_text(encoding="utf-8")).group(1)
assert (ROOT / f"{KEY}.txt").read_text(encoding="utf-8").strip() == KEY, "key file missing: run python3 _src/build.py"

ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
sitemap = [e.text for e in ET.parse(ROOT / "sitemap.xml").getroot().findall("s:url/s:loc", ns)]

if "--all" in sys.argv:
    urls = sitemap
else:
    changed = subprocess.run(["git", "diff", "--name-only", "HEAD~1", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    urls = []
    for f in changed:
        if f.endswith("index.html") and not f.startswith("_"):
            u = SITE + "/" + f[: -len("index.html")]
            if u in sitemap:
                urls.append(u)
    if "sitemap.xml" in changed:
        urls.append(SITE + "/sitemap.xml")

if not urls:
    print("IndexNow: no public pages changed, nothing to submit.")
    sys.exit(0)

payload = {"host": "myvitapals.com", "key": KEY, "keyLocation": f"{SITE}/{KEY}.txt", "urlList": urls[:10000]}
if "--dry-run" in sys.argv:
    print(json.dumps(payload, indent=2))
    sys.exit(0)
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=json.dumps(payload).encode("utf-8"),
                             headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f"IndexNow: HTTP {r.status} for {len(urls)} URLs")  # 200 = OK, 202 = accepted, key check pending
except urllib.error.HTTPError as ex:
    print(f"IndexNow: HTTP {ex.code} {ex.reason}. 403 = key file not found on the live site yet; 422 = URL/host mismatch; 429 = too many requests")
    sys.exit(1)
