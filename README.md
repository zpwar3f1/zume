# Zumee · zumee.org

Static marketing site for Zumee, a vehicle advertising platform for Metro Vancouver.

- `index.html` – the whole site (Chinese / English, hash-routed pages: home, driver, business, about, terms, pay). Images and logo are embedded; the only external dependency is Google Fonts.
- `404.html` – same page, so deep links like `/#driver` still work.
- `favicon.png`, `apple-touch-icon.png` – brand icons (from the original logo).
- `robots.txt` – currently disallows indexing while the site is a demo; remove once forms are live.
- `_headers` – security headers for Cloudflare Pages.
- `brand/` – `zumee-logo-original.png` (the supplied logo) and `png/` with background-removed, horizontal, car-only, wordmark and icon versions; `vector-drafts/` keeps the earlier SVG explorations.

## Deploy

Hosted on Cloudflare Pages, production branch `main`, build command none, output directory `/`.
