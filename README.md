# zume / zumee.org

Static marketing site for Zume, a vehicle advertising platform for Metro Vancouver.

- `index.html` – the whole site (Chinese / English, hash-routed pages: home, driver, business, about, terms, pay). Images and logo are embedded; the only external dependency is Google Fonts.
- `404.html` – same page, so deep links like `/#driver` still work.
- `favicon.svg`, `apple-touch-icon.png` – brand icons.
- `robots.txt` – currently disallows indexing while the site is a demo; remove once forms are live.
- `_headers` – security headers for Cloudflare Pages.
- `brand/` – logo sources (SVG) and PNG exports; `generate-logo-d.py` regenerates concept D from paths (needs `fonttools` and `Sora-VF.ttf`).

## Deploy

Hosted on Cloudflare Pages, production branch `main`, build command none, output directory `/`.
