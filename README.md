# Groundwork Landscaping — Site

Static site for groundworkllc.netlify.app. Sources are plain HTML in the repo root;
`build.py` assembles `dist/` for Netlify. See `check_links.py` for the
pre-deploy link/image checker.

---

## Photo checklist

Everything below feeds a real slot on the site. Shoot phone-quality is fine —
the specs matter more than the camera. Deliver originals as JPG; webp/resize
variants get generated during the build.

### Universal shot specs

| Spec | Target |
|---|---|
| Orientation | Landscape (horizontal) for everything except instagram-style details |
| Resolution | Long edge ≥ 1600px (site serves 1200w + 800w variants) |
| Light | Overcast or golden hour; avoid harsh noon shadows on stone/wood |
| Before/after pairs | **Same position, same height, same framing** — stand on the same spot for both; these may become comparison sliders |
| Per project | 1 wide establishing shot + 3–5 detail shots |
| People/trucks | Include the truck, trailer, or crew naturally in some frames — equipment in frame reads as "real operation" |

### Priority 1 — fills an empty slot now

- [ ] **Crew photo — About page story section** (replaces the bluestone-patio
  stand-in currently at `img/about/`)
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
img/case-studies/<project-slug>/1-<description>.jpg   # numbered process shots
img/case-studies/<description>.jpg                    # single-purpose shots
img/blog/<description>.jpg                            # blog imagery
img/about/crew.jpg                                    # when the crew photo exists
```

- Lowercase, hyphenated, descriptive (`5-completed-front-cedar-fence.jpg`).
- Note the project location + date when handing files over — captions and
  schema use them.
- Get client permission for any recognizable faces or street numbers before
  submitting.
