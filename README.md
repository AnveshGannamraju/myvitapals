# VitaPals — myvitapals.com

Vitamins explained simply, food first. Plain language, with real numbers from the NIH Office of Dietary Supplements.

## How to update
Content lives in `_src/`:
- `vitamins.json`: names, what each vitamin does, forms, sub-types (A, D, E, K), fun facts
- `details.json`: daily needs, upper limits, food tables (% Daily Value), Indian foods, risk groups, supplements, interactions, myths, FAQ
- `guides.json`: life-stage guides (vegetarian, over 50, pregnancy, kids, supplements, tiredness)

Then run `python3 _src/build.py` to regenerate every page, the sitemap and the search/food data.
Optionally, run `node _src/render.js` (needs Playwright; FONT_DIR points to @fontsource fonts) to refresh share images in `og/`.

Interactive bits (search, food finder, vitamin check) are in `assets/app.js`. No tracking, and nothing is sent anywhere.
Folders starting with `_` are not published by GitHub Pages.

## Audit regression checks

Run `python _src/build.py`, then `python _src/validate.py`.
For interactive checks, install Playwright in your development environment and run a local static server on port 8765. Run `node _src/qa.cjs` (uses installed Edge); `BASE_URL` can point to a different local server. Checks cover diet filters, aliases, reproductive stages, consent-based local storage, protein unit conversion, mobile overflow and browser errors.

Content-update dates do not certify clinical review. Qualified review of medication, pregnancy and dosing guidance remains outstanding. The audit's meal builder, supplement label decoder, weekly planner, multilingual content and new topic library are future product work, not implemented features. Full assistive-technology testing and claim-by-claim evidence appraisal also remain outstanding.
