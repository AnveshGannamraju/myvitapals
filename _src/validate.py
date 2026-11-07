"""Regression checks for generated content and declared food servings."""
import json
import re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parent.parent
foods = json.loads((ROOT / 'assets/foods.json').read_text(encoding='utf-8'))
for food in foods:
    if not food.get('in'):
        assert food['a'] and food['s'] and food['source'], food
veg = (ROOT / 'guides/vegetarian/index.html').read_text(encoding='utf-8')
chips = re.findall(r'<div class="chips">(.*?)</div>', veg, re.S)
assert chips and not re.search(r'\b(fish|salmon|chicken|tuna)\b', ' '.join(chips), re.I)
assert 'EFSA: 12 mg' in (ROOT / 'vitamin-b6/index.html').read_text(encoding='utf-8')
assert 'Routine vitamin D blood testing' in (ROOT / 'vitamin-d/index.html').read_text(encoding='utf-8')

class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ('href', 'src'):
            value = attrs.get(key, '')
            if value.startswith('/') and not value.startswith('//'):
                path = ROOT / unquote(urlsplit(value).path).lstrip('/')
                assert path.exists(), f'Missing local target: {value}'

pages = list(ROOT.rglob('*.html'))
for page in pages:
    text = page.read_text(encoding='utf-8')
    assert 'Only a doctor and a blood test' not in text, page
    assert 'Mineral guides are coming soon' not in text, page
    Links().feed(text)
print(f'PASS: {len(pages)} pages, local targets, diet recommendations, clinical corrections and {len(foods)} food records')
