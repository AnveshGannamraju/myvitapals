# VitaPals — myvitapals.com

A friendly, simple guide to vitamins for all ages.

## How to update
1. Edit the vitamin content in `_src/vitamins.json`.
2. Run `python3 _src/build.py` to regenerate every page, plus `sitemap.xml`.
3. (Optional) Run `node _src/render.js` to refresh the share images in `og/`. This needs Playwright, and optionally FONT_DIR pointing to @fontsource fonts.

Folders starting with `_` are not published by GitHub Pages.
