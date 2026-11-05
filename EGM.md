# Groundwork Landscaping — Repository Blueprint

*EGM architecture contract. The human-maintained `README.md` (analytics ops +
photo checklist) remains the operational doc; this file is the code
structure contract and both are kept.*

## System Overview

Static marketing site for Groundwork Landscaping (Longmont & Boulder County,
CO), deployed on Netlify at `groundworkllc.netlify.app` (`build.py` line 121).
Sources are hand-authored plain HTML — 17 pages in the repo root (including
`theme-lab.html`, a dev-only theme playground, and
`googleb057abba7f039342.html`, the Google site-verification file) — plus
`site.css` / `site.js`; `build.py` assembles `dist/` for Netlify (36 HTML
pages: 17 root + 8 blog + 11 case-studies), injecting shared chrome, meta
tags, cache-busted asset URLs, and the sitemap. Contact forms post to
Formspree (`site.js` line 4); lead source is captured from `?src=` / `utm_*`
query params into a hidden form field (`site.js` lines 10–18). Analytics are
Cloudflare Web Analytics, gated entirely on the `CF_ANALYTICS_TOKEN` env var
— unset means nothing is injected.

## Local Interface & Invariants

- `build.py` (481 lines) — the build pipeline. Public functions:
  `asset_version` (line 94, 8-char sha256 content hash),
  `asset_tags` (109), `case_topics` (135), `case_label` (139),
  `inject_case_related` (151), `page_url` (168), `first_content_image` (173),
  `inject_og_tags` (183), `apply_analytics_policy` (256), `minify_css` (267),
  `inject_twitter_card` (275), `should_skip` (295),
  `transform_gallery_markup` (299), `inject_skip_link` (341),
  `build_html` (369), `git_lastmod` (400), `build_sitemap` (408),
  `_run_pdf_writer` (422), `build_pdfs` (438), `main` (459).
- `dev.py` (75 lines) — local dev server. `pick_port` (line 24) probes
  127.0.0.1 by binding; default port 8010, deliberately not 8000
  (Paperless-ngx publishes 8000 on this machine — lines 17–20), with an
  explicit port overridable as `argv[1]` (line 59) and a 20-port probe window
  (`PORT_ATTEMPTS`, line 21). Rebuilds via
  `subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)`
  before serving (line 43) and serves `dist/` by `directory=` argument
  (line 67) because the build deletes and recreates `dist/`.
  `NoCacheHandler` (line 46) sends `Cache-Control: no-store`.
- `check_links.py` (349 lines) — offline link/anchor/image checker.
  `PageParser` (line 50), `discover_pages` (98), `parse_page` (109),
  `resolve_target` (126), `find_file` (137), `main` (171). Beyond plain links it detects
  case-mismatches for existing targets, reports orphan pages/images, and
  scans CSS `url()` references, ld+json image fields, and `og:image` meta
  content values (lines 77–78).
  Flags: `--root`, `--check-external` (HEAD-requests external links),
  `--quiet`.
- `site.js` (406 lines) — one IIFE wiring progressive enhancements:
  `initializeContactForm` (line 3) intercepts submit, validates fields with
  `aria-invalid` state, posts via `fetch()` with success/error boxes
  (58–97), and captures lead source (10–18); `requestedService` (100) /
  `serviceFromPage` (107) with service aliases (`hardscape→hardscaping`,
  `lawn|maintenance→lawn-care`, lines 21–26); `ensureQuoteSheet` (113);
  `ensureMobileCta` (244) wires the server-rendered CTA bar and rebuilds the
  whole bar itself if `#mobile-cta` is absent (covering pages built before
  it existed); `enhanceKeyboardAccess` (270) adds mobile-nav panel syncing
  plus lightbox dialog semantics, focus traps, Escape handling, and keyboard
  activation of gallery cards (282–332); `wireGalleryTriggers` (337,
  lightbox). The mobile CTA markup is server-rendered by the build
  (`build.py` lines 86–92) so it survives blocked scripts.

Root-level invariants:

- **Nav and footer are single-sourced in `build.py`** (`HEADER`/`FOOTER`,
  lines 32–84) and replace every page's `<header>`/`<footer>` at build time
  except `thank-you.html` (lines 371–373). Edit the nav in `build.py`, not in
  the HTML files. The Fall cleanup nav item is seasonal and must be removed
  after the campaign ends (comment at line 36).
- **Cache busting is mandatory**: `netlify.toml` serves `/site.css` and
  `/site.js` immutable for a year, so every reference carries
  `?v=<sha256[:8]>` of the file bytes (`asset_version`, lines 94–106;
  `asset_tags`, 109–113). A hand-written reference without `?v=` ships an
  update nobody receives. Every page gets the versioned injection —
  including `thank-you.html`: since 2026-11-05 the strip-and-inject block
  runs outside the thank-you guard (`build.py` `build_html`), so its
  hand-written unversioned references are replaced like every other page's.
- **`build_html` also transforms page heads**: inline `<style>` blocks are
  extracted, minified and re-injected before `</head>` (lines 374–377);
  hand-written `/site.css` and `/site.js` references are stripped (381–382);
  Google Fonts `<link>` tags are stripped (385); favicon/apple-touch
  `ICON_TAGS` are injected (116–119, applied at 390).
- **The privacy notice cannot drift from the beacon**: `privacy.html` must
  keep the `analytics-policy:start/end` marker comments; the build raises
  `RuntimeError` rather than ship a beacon the notice doesn't describe
  (`apply_analytics_policy`, lines 256–264). The token itself is public but
  comes from the env var, never the repo (lines 233–243).
- **Print PDFs are build outputs with a guard**: `PDF_JOBS` (lines 19–30)
  lists five print pieces in `docs/marketing/` — two flyers
  (`flyer-door-hanger`, `flyer-fall-cleanup`), a realtor counter card, and
  two quote-calibration worksheets. `_run_pdf_writer` (422) prefers the
  weasyprint import and falls back to a `/tmp/pdfgen` venv subprocess;
  `build_pdfs` (438) regenerates a PDF only when its HTML source is newer
  (mtime guard, 450–452), and any rendering failure never breaks the site
  build (455).
- **Sitemap freshness comes from git**: `<lastmod>` per URL is the page's
  last commit date via `git log` (`git_lastmod`, lines 400–405), falling back
  to today.
- **Title suffixes vary by page group** (verified 2026-11-05): root
  info/service pages use `— Groundwork Landscaping` (em dash); the two root
  service-area pages (`drainage-longmont`, `fall-cleanup-longmont`) and all
  blog and case-study pages use ` | Groundwork`; `services.html` uses
  ` | Groundwork Landscaping`; `index.html`, `contact.html`, `theme-lab.html`
  carry no brand suffix. The only build logic that depends on a suffix is
  `case_label` (line 148), which splits on the first `|` and only runs on
  case-study pages.
- `index.html` is section-per-band rather than `<main>`-wrapped; the skip-link
  injector handles that case specially (`inject_skip_link`, lines 341–366).

## Subdirectories & System Boundaries

- [blog](./blog/README.md) — seven posts + index; same build transforms as
  all pages.
- [case-studies](./case-studies/README.md) — eleven project pages; the build
  cross-links them by filename-derived topic.
- [docs](./docs/README.md) — plans + marketing; excluded from the deployed
  site, but five print PDFs in it are regenerated by the build when stale.
- [dev-archive](./dev-archive/README.md) — frozen one-off scripts; excluded
  from build and link checking.
- `fonts/` (no contract) — three woff2 files, copied verbatim
  (`COPY_DIRS`, `build.py` line 16); `FONT_TAGS` (114–115) preloads two of
  them (`fraunces-var`, `work-sans-var`); `fraunces-italic-var.woff2` has no
  preload.
- `img/` (no contract) — site imagery, copied wholesale into `dist/`
  (`build.py` lines 470–472); drop-off conventions documented in `README.md`.

## Global Invariants

- `dist/` is fully derived output — deleted and rebuilt on every run
  (`build.py` lines 459–462). Never edit `dist/` directly.
- `SKIP_DIRS` (`build.py` line 14) — `.git`, `dev-archive`, `__pycache__`,
  `dist`, `docs` — never deploy. Anything that must ship lives at root, in
  `blog/`, `case-studies/`, `fonts/`, or `img/`.
- `COPY_FILES` (`build.py` line 15) is the exhaustive list of root files
  copied as-is (`site.css`, `site.js`, `sitemap.xml`, `robots.txt`,
  `favicon.ico`); a new root-level asset needs an entry there or it silently
  won't deploy.
- `netlify.toml` configures the deployment itself (`publish = "dist"`,
  `command = "python3 build.py"`, lines 1–3) and sets caching and security
  headers site-wide: HTML is
  `max-age=0, must-revalidate` (deploys propagate immediately); `/img/*`,
  `/site.css`, `/site.js` are `max-age=31536000, immutable`; every response
  carries `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: strict-origin-when-cross-origin`, and
  `Permissions-Policy: camera=(), microphone=(), geolocation=()`.

## Global Side Effects

- A build wipes and rewrites `dist/`, minifies `site.css` into it, writes
  `dist/sitemap.xml` with git-derived lastmod dates, and regenerates stale
  print PDFs inside the source tree (`docs/marketing/`).
- The build reads `CF_ANALYTICS_TOKEN` from the environment and shells out to
  `git log`.
- The dev server binds `127.0.0.1` on the first free port from 8010 (or the
  port given as `argv[1]`).

## System Verification

- Run: `python3 check_links.py --quiet` — all internal links, anchors, and
  images resolve (passing as of 2026-11-05). Add `--check-external` to also
  probe external URLs.
- Run: `python3 build.py` — rebuilds `dist/`; the printed page count should
  match the HTML sources (36 as of 2026-11-05).
- Run: `python3 dev.py` — build + serve locally at http://127.0.0.1:8010.
