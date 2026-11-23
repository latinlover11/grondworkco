# Waxwing Landscaping — Site

Static site for waxwinglandscaping.com. Sources are plain HTML in the repo root;
`build.py` assembles `dist/` for Netlify. See `check_links.py` for the
pre-deploy link/image checker.

---

## Analytics

Three states, chosen by what the build actually emits. The paragraph between the
`analytics-policy` markers in `privacy.html` is rewritten at build time, and the
build fails rather than ship a beacon the notice doesn't describe.

| State | Trigger | What the notice says |
| --- | --- | --- |
| off | no token, no GA4 ID, `EDGE_ANALYTICS = False` | no third-party analytics |
| Cloudflare | `CF_ANALYTICS_TOKEN` env var or untracked `.analytics-token` | cookieless Cloudflare paragraph |
| GA4 | `GA4_MEASUREMENT_ID` env var or untracked `.ga4-id` | the `_ga` cookie paragraph, plus the Cloudflare one when both are on |

Cloudflare Web Analytics is cookieless and aggregate. GA4 sets a first-party `_ga`
cookie, which is why it gets its own state instead of reusing the Cloudflare copy —
that copy correctly says "sets no cookies". The GA4 tag ships with Google Signals
and ad personalisation denied, and Consent Mode defaults denying ad storage. Both
IDs are public (they appear in page source) but stay out of git, so a clone cannot
silently start measuring. Never switch a state by hand-editing `privacy.html`.

### Consent stance

No banner. The GA4 setup here is first-party analytics, not advertising: no Signals,
no ad personalisation, nothing sold or shared for advertising. The Colorado Privacy
Act duties attach at 100k+ consumers a year (or 25k+ while selling data), far above
this business, so the notice discloses the cookie and gives a refusal route — block
cookies for the site, or install Google's opt-out add-on — instead of a consent gate.

Revisit before shipping under any of these, and answer with a banner (or Consent
Mode with denied defaults), not a quieter sentence in the notice: EEA/UK traffic
becomes material (ePrivacy wants prior consent for analytics cookies); ads or
remarketing are switched on; audience data is shared; the CPA thresholds are met.
Not legal advice — the owner signs off on this stance.

Known limitation: pageviews only. It cannot attribute phone calls; form leads carry
`?src=` into the hidden `source` field and are readable per-channel in Formspree.

---

## Deployment

Push to `main` and you are done. The Netlify project (`groundworkllc`, site id
`38200c77-154d-4ee6-a062-578b904cec1a`) is connected to this repository, so
Netlify builds the site itself from `netlify.toml` — `python3 build.py` on
Python 3.12, publishing `dist/`. Nothing runs by hand, and there is no local
publish step.

That also means Netlify is where `CF_ANALYTICS_TOKEN` takes effect: it is read
from the site's environment variables at build time, not from your shell.

### What CI does, and deliberately does not do

Every push and pull request runs `.github/workflows/ci.yml`: the link/image
checker (`check_links.py --quiet`) gates the build, `dist/` is assembled, and it
is uploaded as a build artifact. CI never publishes.

That is on purpose. Two publishers for the same commit race each other and make
it unclear which build is live, so the workflow stops at the artifact and
leaves deploying to Netlify. This was confirmed, not assumed: with the old CI
deploy step disabled and a marker added to `404.html`, the workflow skipped its
deploy while production served the marker — so the publish came from Netlify's
build.

One consequence worth knowing: GitHub cannot see Netlify's builds, so a failing
Netlify build still leaves the workflow green. If a push seems not to have
landed, look at Netlify → Deploys for that commit rather than at the Actions tab.

### Checking a deploy

- `https://waxwinglandscaping.com` — production
- Netlify → Deploys — build log and source commit for every deploy
- HTML is served `must-revalidate` (see `netlify.toml`), so a finished deploy is
  visible on the next request; `curl -sI https://waxwinglandscaping.com/`
  confirms the headers

No Netlify credentials belong in this repo any more. `NETLIFY_AUTH_TOKEN` and
`NETLIFY_SITE_ID` are unused by CI; if the token is still sitting in the repo's
secrets, revoke it in Netlify → Account settings → Access tokens and then run
`gh secret delete NETLIFY_AUTH_TOKEN`.

### GitHub Pages note

GitHub Pages is **disabled** (removed 2026-11-13) so the site is served from one
host only. It previously ran a legacy build from `main`, which served the repo
root rather than `dist/` — a second, publicly reachable copy of every page and a
duplicate-content liability. Deploying the Netlify site is the production path.
If Pages is ever needed again, point it at `dist/` in repo Settings → Pages.

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
  **Parked until roughly mid-January 2027** — the owner isn't ready for this
  shoot yet. Don't add a placeholder image or a "Meet the crew" section in the
  meantime; the About page keeps the bluestone-patio stand-in until a real
  candid lands. Revisit after the fall campaign wraps.
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
