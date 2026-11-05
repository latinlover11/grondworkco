# Case Studies

## Overview

Eleven finished-project pages forming the site's portfolio. The build treats
them as a linked set: each page automatically gets a "related projects"
section pointing at its three closest siblings.

## Interface

- Pages: `cedar-privacy-fence.html`, `fort-collins-retaining-wall-patio.html`,
  `front-bed-gravel-edging.html`, `front-yard-xeriscape.html`,
  `lafayette-cedar-fence.html`, `lafayette-downspout-drainage.html`,
  `lakewood-privacy-fence.html`, `longmont-flagstone-entry.html`,
  `river-rock-parking-pad.html`, `seasonal-landscape-cleanup.html`,
  `vertical-flagstone-longmont.html`
- Topic classification is derived from the filename at build time
  (`build.py` `CASE_TOPICS`, lines 126–132): fence, drainage, stone,
  hardscape, planting.

## Invariants

- Filenames carry the topic tokens. Renaming a case-study file changes which
  related-project links it and its siblings receive (`build.py`
  `case_topics`, line 135, matches words in `path.stem`).
- The related-projects section is injected before `</main>` only when the
  page contains `</main>` (`build.py` `inject_case_related`, lines 151–165) —
  keep the `</main>` closing tag intact.
- Each related card's label is the target page's `<title>` minus the
  ` | Groundwork` suffix (`build.py` `case_label`, lines 139–148; all eleven
  pages end their titles with exactly that suffix).
- Gallery images are referenced root-absolute (`/img/case-studies/...`) and
  served as `.webp`. Layout varies by page (verified 2026-11-05): seven
  pages use `<project-slug>/N-<description>.webp` numbered process shots;
  three use flat unnumbered files in `img/case-studies/`
  (`river-rock-parking-pad`, `front-yard-xeriscape`,
  `seasonal-landscape-cleanup`); `cedar-privacy-fence.html` borrows
  `lafayette-cedar-fence/` (no `cedar-privacy-fence/` directory exists).
  Drop-off conventions for new photos live in the root `README.md`.
  (A former exception in `seasonal-landscape-cleanup.html` line 326 — a
  legacy `onclick` lightbox call with a relative path — was fixed
  2026-11-05; every gallery reference in all 11 pages is now
  root-absolute `.webp`.)
- `site.css` carries six page-scoped stylesheets keyed to
  `case-study-<slug>` classes — five single-slug blocks under
  `/* case-studies/<page>.html */` marker comments (cedar-privacy-fence,
  lafayette-cedar-fence, lakewood-privacy-fence, longmont-flagstone-entry,
  vertical-flagstone-longmont) and one combined block whose selectors list
  all three of front-yard-xeriscape,
  river-rock-parking-pad, and seasonal-landscape-cleanup (site.css lines
  285–344).
  **They are currently dead**: no page, build step, or script applies a
  `case-study-<slug>` class — ten pages carry only the shared
  `case-study-cta` class, and `lakewood-privacy-fence.html` carries neither
  (its CTA is `case-cta`, its body `site-page`) — so editing these blocks
  has no visible effect. Case-study pages are styled by their own
  page-scoped inline `<style>` blocks plus the site-wide rules — not by
  these blocks. The inline vocabulary differs from the dead blocks': the
  ten standard pages use `.case-hero`, `.case-meta-grid`, `.story-layout`,
  `.cta-box`, `.gallery-card`, `.lightbox-modal*`, while
  `lakewood-privacy-fence.html` uses `.case-page`, `.story`, `.fact-box`,
  `.case-cta`, `.gallery-grid`. No page carries a bare `.lightbox` class —
  it survives only inside these dead site.css blocks.
- Gallery markup may use legacy inline `onclick=` handlers or declarative
  `data-lightbox-*` / `data-gallery-*` attributes; the build normalizes both
  (`build.py` `transform_gallery_markup`, lines 299–338). The declarative
  attributes are inert on their own: all eleven pages embed an inline
  `openLightbox(imgSrc, caption)` implementation plus lightbox modal markup
  (`.lightbox-modal` with a `.lightbox-close` control), and `site.js`
  `wireGalleryTriggers()` (lines 337–390) dispatches clicks on
  `data-lightbox-*` elements back to the page-local
  `window.openLightbox`. (`lakewood-privacy-fence.html` previously used a
  divergent `openLightbox(card)` signature and a `.lightbox` modal that
  could neither open nor close in the built site; aligned with the standard
  pattern on 2026-11-05.)
- The build also normalizes legacy `switchCasePhoto(...)` handlers into
  `data-gallery-*` attributes (`build.py` lines 301–309) and `site.js`
  (lines 359–368) dispatches them to `window.switchCasePhoto`. No
  case-study page defines `switchCasePhoto` or carries `data-gallery-*`
  markup, so the path is inert within these pages — but it is live on
  `../work.html`, which defines a global `switchCasePhoto(caseId, imgSrc,
  badgeText, btn)` and whose 58 inline handlers the build converts into
  `data-gallery-*` attributes; that is the photo-switcher mechanism of the
  portfolio grid there (`.case-study-card` entries with `data-category`
  filters showcasing these case studies, styled by work.html's inline
  styles and site.css `:where(.work-page)` rules).

## Side Effects

- None at rest. The build writes `dist/case-studies/*` from these sources.

## Verification

- Run: `python3 check_links.py` (from the repo root).
