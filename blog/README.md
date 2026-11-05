# Blog

## Overview

The site's blog: seven posts plus the index (eight HTML files). Posts are
hand-authored in this directory and receive the same build transforms as
every other page; nothing here is generated.

## Interface

- `index.html` — blog landing page (linked from the site nav,
  `build.py` line 41: `/blog/index.html`).
- `blog-post-1.html` … `blog-post-7.html` — the seven posts, in editorial
  order by number.

## Invariants

- Page titles end with ` | Groundwork` (verified across all eight files).
  OG- and Twitter-card injection copies each page's full `<title>` verbatim
  (`build.py` `inject_og_tags` line 209, `inject_twitter_card` line 289);
  the suffix-splitting `case_label` helper (lines 139–148) runs only on
  case-study pages — its caller guards on `source.parent.name ==
  "case-studies"` (line 152) — so nothing here depends on the suffix.
- Every page here gets the shared header/footer swapped in at build time
  (except `thank-you.html`, which lives at the root), OG/Twitter tags
  injected, and gallery markup transformed — see the root `EGM.md` Local
  Interface section. Do not hand-maintain nav or meta tags in these files.
- Post imagery lives in `../img/blog/` as `.webp` files (lowercase,
  hyphenated, matching the root `README.md`'s drop-off conventions). Two
  pages also reference images from `../img/case-studies/`, so blog imagery
  is not confined to `img/blog/`.

- `site.css` lines 75–207 are a dead legacy fold-in for the blog: rules
  scoped to `.blog-post-1`–`.blog-post-6` / `.blog-index` page classes —
  the two post blocks under `/* identical styles for: blog/... */` marker
  comments (lines 75, 123) and the `.blog-index` block under
  `/* blog/index.html */` (line 165) — that no
  element carries anywhere — every blog page is `<html lang="en">` with a
  plain `<body>`, and neither `build.py` nor `site.js` adds classes. The
  pages are styled by their own inline `<style>` blocks (element selectors:
  `:root`, `body`, `.wrap`, `header`, …); `blog-post-7.html` has no fold-in
  section at all. That range is not the only blog CSS in site.css: inside
  the `@media (max-width: 860px)` block (opened at line 3026), live rules
  override the pages at mobile widths — `body:not(.site-page) .wrap`,
  `.nav`, `.nav-toggle`, `.nav-links` (lines 3027–3030, applying to every
  blog page since none carries `.site-page`) and `body:not(.site-page)
  .blog-header`, `.blog-grid`, `.blog-image`, `.blog-content` (lines
  3053–3058, matching only `index.html`). The inline blocks fully style the
  pages at desktop widths; at ≤860px site.css's later-loaded rules win.
- Each blog page declares its own dark `:root` palette inside that inline
  block, but it is inert in `dist/`: the build emits the page `<style>`
  before the `site.css` link (`build.py` lines 377 and 383), so site.css's light
  `:root` variables shadow the page's.

## Side Effects

- None at rest. The build writes `dist/blog/*` from these sources.

## Verification

- Run: `python3 check_links.py` (from the repo root; verifies every internal
  link, anchor, and image on these pages).
