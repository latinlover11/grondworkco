# Groundwork Landscaping — Site

Static site for groundworkllc.netlify.app. Sources are plain HTML in the repo root;
`build.py` assembles `dist/` for Netlify. See `check_links.py` for the
pre-deploy link/image checker.

---

## Analytics

Page counts come from Cloudflare Web Analytics — cookieless, so no consent banner.
It stays off until `CF_ANALYTICS_TOKEN` is set in Netlify → Site settings →
Environment variables; `build.py` injects the beacon only when the variable is
present (`CF_ANALYTICS_TOKEN=… python3 build.py` locally if you want to see it).

The notice cannot drift from the beacon: the paragraph between the
`analytics-policy` markers in `privacy.html` is swapped between the "no analytics"
and "Cloudflare Web Analytics" copy at build time, and the build fails rather than
publish a beacon the notice doesn't describe. Bump the notice's *Last updated*
date when the token lands.

Known limitation: pageviews only. It cannot attribute phone calls; form leads carry
`?src=` into the hidden `source` field and are readable per-channel in Formspree.

---

## Photo checklist

Everything below feeds a real slot on the site. Shoot phone-quality is fine —
the specs matter more than the camera. Deliver originals as JPG; they get
converted to webp (plus a `-800.webp` variant each) and committed to the
repo — `build.py` copies `img/` verbatim, nothing generates variants at
build time.

### Universal shot specs

| Spec | Target |
|---|---|
| Orientation | Landscape (horizontal) for everything except instagram-style details |
| Resolution | Long edge ≥ 1600px (site serves full-size + 800px webp variants) |
| Light | Overcast or golden hour; avoid harsh noon shadows on stone/wood |
| Before/after pairs | **Same position, same height, same framing** — stand on the same spot for both; these may become comparison sliders |
| Per project | 1 wide establishing shot + 3–5 detail shots |
| People/trucks | Include the truck, trailer, or crew naturally in some frames — equipment in frame reads as "real operation" |

### Priority 1 — fills an empty slot now

- [ ] **Crew photo — About page story section** (replaces the bluestone-patio
  stand-in the About page currently borrows from
  `img/case-studies/bluestone-patio.webp`)
  Candid working shot beats a posed lineup: crew on a job site or with the
  truck/trailer, landscape 3:2, everyone identifiable. `alt` text will name it
  honestly, so it should genuinely show the crew.

### Priority 2 — trust & conversion upgrades

- [ ] **Truck/trailer with logo, clean and readable** — candidate for the
  homepage hero and future social/og images.
- [ ] **Owner portrait** (working, not studio) — About page, testimonial
  attribution, blog authorship.

### Priority 3 — matched before/after pairs per service

Existing case-study photos already tell the before → process → after story as
sequential galleries. A **comparison slider** needs something stricter: two
shots from the *same spot, same height, same framing*. Until those exist, the
case studies stay as-is (see `docs/MODERNIZATION_PLAN.md` §2.1).

How to shoot a matched pair:
1. Before starting work, pick the angle that shows the whole area and take the
   "before" shot.
2. Mark the spot (photo the ground reference, note a landmark).
3. On the final day, stand on the same spot at the same height and re-shoot.

- [ ] **Fencing** — old/leaning fence vs. finished cedar line, plus gate
  hardware close-up.
- [ ] **Hardscaping** — bare/muddy yard vs. finished patio; stone joint and
  cap-rail details.
- [ ] **Xeriscaping** — turf vs. finished gravel/stone conversion; edging and
  planting-zone details.
- [ ] **Lawn care** — overgrown vs. manicured same-week pairing; clean bed
  edges and mowing lines.

### Priority 4 — process proof (craftsmanship shots)

Already used in case studies; more is better.

- [ ] Excavation/grading in progress
- [ ] Concrete footings and post setting
- [ ] String lines/layout (shows precision)
- [ ] Base compaction, gravel layers
- [ ] End-of-day site cleanup (reinforces the "spotless" promise)

### Drop-off conventions

```
img/case-studies/<project-slug>/1-<description>.webp  # numbered process shots (7 of 11 projects)
img/case-studies/<description>.webp                   # single-purpose shots (3 projects: flat files)
img/blog/<description>.webp                           # blog imagery
img/about/crew.jpg                                    # when the crew photo exists (dir doesn't exist yet)
```

- Lowercase, hyphenated, descriptive (`1-before-front-yard-condition.webp`).
- Pages reference images root-absolute (`/img/...`) and only serve `.webp`
  (plus `.svg`/`.png` icons) — a `.jpg` original in the tree is never
  referenced by a page. Commit the `.webp` plus its `-800.webp` variant.
- Layout note: `cedar-privacy-fence.html` currently borrows images from
  `lafayette-cedar-fence/` — don't propagate that pattern for new projects.
- Note the project location + date when handing files over — captions and
  schema use them.
- Get client permission for any recognizable faces or street numbers before
  submitting.
