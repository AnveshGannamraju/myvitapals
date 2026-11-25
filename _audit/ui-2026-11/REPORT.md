# UI/UX, navigation, mobile and accessibility audit (November 2026)

Measured on a local build (python http.server, no gzip) with Chrome, Playwright, axe-core 4 and Lighthouse 12.
Folders starting with "_" are not published, so this report and its screenshots stay in the repo only.

## Before → after

| Measure | Before | After |
|---|---|---|
| Home: links in main content | 57 | 19 |
| Home: total links on page | 144 | 85 |
| Footer links (every page) | 36 | 12 |
| Mobile menu: items visible when opened | 43 links | 8 top-level items (current section auto-expands) |
| Home page height at 390 px | 8,260 px | 4,552 px |
| Search available | Home + 404 only | Every page (header) |
| Breadcrumbs | Plain text paragraph | `nav` + ordered list, `aria-current`, matches JSON-LD |
| axe WCAG 2.2 AA violations (55 pages × 390 + 1440 px) | 0 | 0 |
| Controls under 24 × 24 px (WCAG 2.5.8), key pages | up to 48 | 0 (inline text links exempt) |
| Controls under 44 px tall, home at 390 px | 76 | 0 |
| Horizontal overflow, 56 pages × 6 widths (320–1440) | none at 390 | none at any width |
| 200 % text at 320 px (stricter than 1.4.10) | not tested | passes |
| Lighthouse (mobile) perf / a11y / best / SEO, home | 98 / 100 / 100 / 100 | 98 / 100 / 100 / 100 |
| Lighthouse perf, /vitamin-c/ · /tools/vitamin-check/ · /vitamin-d/d3/ | 98 · 99 · 99 | 97 · 97 · 97 |

### Core Web Vitals (real browser, 390 px, 4× CPU slowdown, ~1.6 Mbps, median of 3; web-vitals library)

| Page (interaction) | LCP before → after | CLS before → after | INP before → after |
|---|---|---|---|
| Home (type in search) | 944 → 956 ms | 0 → 0 | 16 → 16 ms |
| Vitamin C (open menu, expand category) | 944 → 1,020 ms | 0 → 0 | 32 → 24 ms |
| Vitamin check (answer 4 questions) | 868 → 964 ms | 0 → 0 | 16 → 16 ms |
| Food finder (type a food) | 892 → 964 ms | 0.075 → 0.054 | 40 → 48 ms |

All values are well within Google's "good" thresholds (LCP < 2.5 s, CLS < 0.1, INP < 200 ms).
LCP is about 0.05–0.1 s slower in this unzipped local test because the stylesheet gained the menu, search and quiz styles (+8 KB raw, about 2 KB gzipped on GitHub Pages).

## Test suites (all pass)
`build.py` · `validate.py` · `seo_check.py` (0 errors, 0 warnings) · `qa.cjs` · `qa-accessibility.cjs` · `qa-analytics.cjs` · new `qa-ui.cjs`.

`qa-ui.cjs` covers:
- **Home layout:** one primary call to action, six category cards, the legacy `#vitamins`, `#minerals`, `#protein` and `#nutrients` anchors still resolve.
- **Keyboard:** skip link moves focus to `main`; the menu opens with Enter; Escape closes it and returns focus to the button; the focus outline is visible.
- **Panels:** opening search closes the menu.
- **Search:** focuses its input, announces the result count, and supports arrow keys and Escape.
- **Navigation markers:** breadcrumb trail with `aria-current`, plus the active section in the header.
- **Vitamin check:** progress bar, focused error summary with links, `aria-invalid` and `aria-describedby` on unanswered questions, results heading takes focus.
- **Every page at 6 widths:** no sideways scroll, and the header fits.
- **Reflow:** 200 % text at 320 px.

## Remaining issues / next steps
- **Screen readers:** the checks were automated (axe, roles, focus, live regions). Do a quick manual pass with VoiceOver on iPhone and TalkBack on Android before calling WCAG 2.2 AA "verified".
- **Field data:** Lighthouse and CWV here are lab numbers. Check the Core Web Vitals report in Search Console after a few weeks of traffic.
- **Long topic pages:** these are still long (about 13,000 px at 390 px). Collapsing "Claims we checked" or "Nutrients" further could help.
- **Food finder:** lists foods on load (94 links) by design. Consider showing only popular chips until the user types.
- **Brand:** the logo still reads "VitaPals" while metadata uses "MyVitaPals". The screen-reader label follows the visible text (WCAG 2.5.3).
- **Medical review:** content still awaits clinical review (unchanged).
