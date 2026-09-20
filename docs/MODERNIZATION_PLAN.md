# Modernization Plan — groundworkllc.netlify.app

A prioritized, staged plan based on a real audit of the codebase (Sept 2026).
Effort estimates assume the existing static-site architecture stays. Nothing
here requires a rewrite.

---

## Where the site stands (keep these)

The bones are already modern. Don't touch:

- **Static HTML + Python build → Netlify.** Fast, cheap, secure, zero deps.
- **Design system**: dark editorial theme, Fraunces/Work Sans, consistent tokens.
- **SEO fundamentals**: LocalBusiness/Service schema, city landing pages,
  case studies, sitemap, clean canonical URLs.
- **Image pipeline convention**: webp + `srcset` + lazy loading + preload.
- **Recent additions**: security/cache headers, 404 page, testimonials.

---

## Stage 1 — Quick wins (1–2 sittings, ~1 day total)

Cheap changes with outsized polish/speed effect.

| # | Change | Why | Effort |
|---|---|---|---|
| 1.1 | Add `twitter:card`, `twitter:title`, `twitter:image` to all 23 pages (extend `build.py` to inject them from existing og: tags) | Slack/X/iMessage previews currently fall back to bare titles | 30 min |
| 1.2 | Self-host fonts (download woff2 subsets, drop Google Fonts request) | Removes render-blocking third-party CSS; saves ~2 round-trips on every page | 1 hr |
| 1.3 | Minify `site.css`/`site.js` + generated CSS at build time (regex strip is fine at this size) | ~40% smaller payloads | 45 min |
| 1.4 | `<lastmod>` dates in `sitemap.xml`, auto-generated from git mtime in `build.py` | Recrawl freshness signal | 30 min |
| 1.5 | Inline critical CSS per page (the ~2KB above-the-fold rules), defer the rest | Fastest LCP win available | 2 hr |
| 1.6 | Remove inline `style=` attributes (18 in `work.html`), fold into classes | Consistency + CSP readiness | 1 hr |

## Stage 2 — Experience upgrades (a weekend)

Things visitors will actually feel.

| # | Change | Why | Effort |
|---|---|---|---|
| 2.1 | ~~Before/after comparison slider~~ **BLOCKED — no matched photo pairs.** Case studies already tell the before → process → after story as sequential galleries, which works without matched framing. Revisit only after pairs are shot per the README photo checklist (same spot, same height, same framing). | Slider with mismatched angles reads as broken and cheapens the page | — |
| 2.2 | Sticky mobile call bar → real bottom sheet with service preselect (extend the existing `contact.html?service=` param) | Friction between "I'm interested" and "I sent it" | 3 hr |
| 2.3 | Instant quote estimator (stone/fence/lawn calculators, email-me-the-number fallback) | Differentiator no local competitor has; generates pre-qualified leads | 1–2 days |
| 2.4 | Gallery/filterable project grid on `work.html` (filter by service + city) | Turns a photo dump into a sales tool | 4 hr |
| 2.5 | Lightbox with keyboard nav + swipe (current `onclick` lightbox has no a11y) | Table-stakes for photo-heavy pages | 2 hr |

## Stage 3 — Platform & workflow (as needed)

| # | Change | Why | Effort |
|---|---|---|---|
| 3.1 | Lighthouse CI + `check_links.py` + HTML validation as a Netlify deploy check | Catches regressions (like the stripped `<img>` bug) before they ship | 2 hr |
| 3.2 | Migrate blog to a tiny data-driven model (JSON/markdown posts compiled by `build.py`) | Blog posts are hand-copied HTML today; every new post risks drift | 1 day |
| 3.3 | Form submissions → Netlify Forms or a small worker (Formspree free tier is the single point of failure for leads today) | Lead resilience | 2 hr |
| 3.4 | Auto-generate `og.jpg` per page (pillow: project photo + text overlay) | Every page shares one og image today | 3 hr |
| 3.5 | Delete `dev-archive/` from the repo | Dead weight, confusing | 5 min |

## Stage 4 — Growth bets (quarter-scale ideas)

- **Service-area landing pages** (Niwot, Firestone, Erie, Mead…) from a
  template + data file — the city-page pattern already works; scale it.
- **Seasonal campaign pages** (spring cleanup, fall aeration) with dated
  urgency copy + schema `SpecialAnnouncement`.
- **Google Business Profile posts ↔ site job feed**: publish each finished
  job as both a GBP update and a site case study from one source.

---

## What NOT to do

- **Don't move to React/Next/Astro.** Zero JS interactivity needs justify the
  complexity; the static build is already faster than any framework default.
- **Don't add a CMS yet.** Post volume doesn't justify it; Stage 3.2 solves the
  actual pain for free.
- **Don't chase 100 Lighthouse scores.** After Stage 1, remaining points come
  from third-party embeds and diminishing returns.

## Suggested order of execution

1. ~~Stage 1.1–1.4~~ ✅ Done
2. ~~Stage 1.5–1.6~~ ✅ Done
3. Stage 2.2 (bottom-sheet quote flow) — biggest remaining visible win, no assets needed
4. Stage 3.1 (deploy checks) — cheap insurance
5. Stage 2.4 (filterable work grid) + 2.5 (accessible lightbox) as capacity allows
6. Stage 3.2–3.3 before the next blog push
7. Stage 2.1 (comparison slider) only after matched before/after pairs exist — see README photo checklist
