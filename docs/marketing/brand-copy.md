# Waxwing copy deck

Written 2026-11-21, for the switch from Groundwork Landscaping to **Waxwing
Landscaping**. **Applied to the site source on 2026-11-21** — the strings and the §3–§4
prose are in the pages. The domain is still not bought and the name is not registered, so
none of it is deployed. §9's claims checklist is still open.

**What this actually costs:** the name appears in ~95 files, almost all of it as a
literal string. That part is one scripted replace (§8). Only eight pieces of prose
need writing, and they are all below: the name block, the tagline, the hero
subhead, the about hero line, three story paragraphs, the Google Business Profile
description, and four GBP service blurbs.

Source of truth for why this name: `../BRAND_AND_LAUNCH.md` §2b–§2d.

---

## 1. How the name is written

| Where | Form |
|---|---|
| Logo / nav / footer | **Waxwing** in roman + *Landscaping* in the italic ember accent — the existing `<span>` treatment, no new asset |
| First mention on any page | "Waxwing Landscaping", both words |
| Google Business Profile | "Waxwing Landscaping" |
| Invoices, estimates, truck | "Waxwing Landscaping" |
| Legal suffix | **Do not print "LLC" until the entity is filed.** Use "Waxwing Landscaping" everywhere until then |
| Domain | `waxwinglandscaping.com` |

Never: "Wax Wing", "Waxwing Lawn & Landscape", "Waxwing Co.", "Waxwing Services".

**The bird gets one clause, on the About page, and nowhere else.** Not in a title,
not in the hero, not on the truck. A name nobody has heard before needs to sound
like a name, not like a riddle.

---

## 2. Tagline

**Recommended: _One crew for the whole property._**

It is already the homepage H2, which means it survived being written once and read
many times. It carries the actual differentiator the research kept turning up — one
accountable crew, no subcontracting the trades you're known for — and it is not a
service list. It also needs no edit for the switch, so it costs nothing to promote:
truck, GBP, email signature, door hangers, the flyer masthead.

Alternates, by surface:

- **Flyers, door hangers, business card back** — "Hardscape. Fence. Lawn. One crew."
- **Spring campaigns** — "Built for Colorado. Kept that way." (build *and* maintenance)
- **Estimate footer** — "The whole property, start to finish."

Do not use: "Landscaping done right" (says nothing), "luxury" anything (the price
signal fights the free estimate), or a bird pun — "Where landscapes take flight"
reads cheap stencilled on a trailer.

---

## 3. Hero

**Keep the H1: _Outdoor spaces built to last._**

Five words, three lines at the existing 12ch measure, and it already states the
promise the whole site is built around. A domain move is not the week to also change
the strongest sentence on the site.

If a new hero line is wanted anyway, in preference order:

1. **The yard that holds its shape.** — closest to what customers actually say in
   the testimonials: things staying where they were put.
2. **Built once. Held for years.** — build plus maintenance, in four words.
3. **Good bones. Then the beauty.** — the hardscape-first argument, slightly smug.

**New subhead**, replacing "Hardscaping, fencing, and lawn care for Longmont and
Boulder County.":

> Hardscaping, fencing, and lawn care for Longmont and Boulder County — planned,
> built, and kept by one crew.

Shorter, if the 40ch measure looks crowded on mobile:

> Hardscaping, fencing, and lawn care across Longmont and Boulder County, from one
> crew.

Both keep the three service words (search), both keep the cities (search), and both
add the crew promise, which the old subhead left to the next section.

Eyebrow stays: **Hardscaping · Fencing · Lawn care**

---

## 4. About page

### 4a. Hero line

Replaces "Groundwork Landscaping is a Longmont-based crew of hardscapers, fence
builders, and lawn care pros who treat every property like it's our own."

> Waxwing Landscaping is a small Longmont crew of hardscapers, fence builders, and
> lawn care hands. We take the whole property — the structure underfoot and the
> planting around it — and we're still there after the build is finished.

The headline above it, "Built by a crew that lives with the results.", needs no
change. Neither do the three value cards (Built to last / Straight answers / One
crew, start to finish) or the stats row.

### 4b. Story — three paragraphs

Paste into `.story-copy`, replacing the current three.

> The name comes from a bird. Waxwings arrive in a flock, strip a berry bush in an
> afternoon, and move on — a small crew that shows up together and finishes what it
> starts. We spent ten-plus years — and hundreds of jobs — building patios, walls,
> and fences across Boulder County before starting our own outfit, and that habit
> is the part we kept.

> We don't subcontract out the trades we're known for. The crew that pours the
> footings for your fence is the crew that grades your patio base and mows the lawn
> the following spring. That continuity is why the work holds its shape season after
> season — same hands, same standard, whether it's a two-day repair or a full
> rebuild.

> Every project gets the same walk-through, the same clear estimate, and the same
> people who said they'd be there. If something changes mid-build, you hear it from
> us before we do it, not after.

**If the bird explanation feels like too much**, swap P1's first two sentences for:

> Waxwing Landscaping is a small crew by choice. Ten-plus years of building patios,
> walls, and fences across Boulder County came before we started our own outfit, and
> the habit we kept was the one that matters: show up together, finish what you
> start.

Also update, in the same file: the story photo alt text ("Bluestone patio built by
Waxwing Landscaping") and the breadcrumb JSON-LD, which names the company.

---

## 5. Page titles

Rule: **service and city first, brand last.** Nobody searches "Waxwing" yet, so the
brand position in the title stays at the end, exactly where Groundwork sat. Every
title below is the current one with the name swapped, which keeps them all under 60
characters and keeps whatever they rank for intact.

### 5a. Changed by the swap alone (suffix "— Groundwork Landscaping" → "— Waxwing Landscaping")

| File | Title |
|---|---|
| `index.html` | Waxwing Landscaping — Hardscaping, Fencing & Lawn Care |
| `about.html` | About Us — Waxwing Landscaping |
| `contact.html` | Contact Waxwing Landscaping — Get a Quote |
| `work.html` | Our Work & Case Studies — Waxwing Landscaping |
| `hardscaping-longmont.html` | Hardscaping in Longmont, CO — Waxwing Landscaping |
| `fencing-boulder.html` | Fencing in Boulder, CO — Waxwing Landscaping |
| `lawn-care-longmont.html` | Lawn Care in Longmont, CO — Waxwing Landscaping |
| `xeriscaping-boulder-county.html` | Xeriscaping in Boulder County, CO — Waxwing Landscaping |
| `privacy.html` | Privacy Notice — Waxwing Landscaping |
| `accessibility.html` | Accessibility Statement — Waxwing Landscaping |
| `404.html` | Page Not Found — Waxwing Landscaping |
| `thank-you.html` | Request Received — Waxwing Landscaping |

### 5b. Changed by the swap alone (suffix "| Groundwork" → "| Waxwing")

| File | Title |
|---|---|
| `services.html` | Services — Hardscaping, Fencing & Lawn Care \| Waxwing |
| `fencing-longmont.html` | Fence Installation & Repair in Longmont, CO \| Waxwing |
| `landscape-design-longmont.html` | Landscape Design in Longmont, CO \| Waxwing |
| `sprinkler-repair-longmont.html` | Sprinkler Repair in Longmont, CO \| Waxwing |
| `drainage-longmont.html` | Drainage & Downspout Solutions, Longmont \| Waxwing |
| `fall-cleanup-longmont.html` | Fall Cleanup & Winterizing, Longmont \| Waxwing |
| `blog/index.html` | Landscaping Tips for Colorado Homes \| Waxwing |
| `blog/blog-post-1.html` | Choosing the Right Patio Material for Colorado \| Waxwing |
| `blog/blog-post-2.html` | Extending the Life of Your Wood Fence \| Waxwing |
| `blog/blog-post-3.html` | Water-Wise Lawn Alternatives for Colorado \| Waxwing |
| `blog/blog-post-4.html` | Designing an Outdoor Kitchen for Entertaining \| Waxwing |
| `blog/blog-post-5.html` | Spring Landscape Cleanup Checklist \| Waxwing |
| `blog/blog-post-6.html` | Outdoor Kitchens for Colorado Seasons \| Waxwing |
| `blog/blog-post-7.html` | Sprinkler Blowout 101: Why Longmont Homes Need It Before the First Freeze \| Waxwing |
| `case-studies/cedar-privacy-fence.html` | Cedar Privacy Fence Installation \| Waxwing |
| `case-studies/fort-collins-retaining-wall-patio.html` | Curved Block Retaining Wall & Terrace \| Waxwing |
| `case-studies/front-bed-gravel-edging.html` | Stone-Edged Gravel Bed & Plantings \| Waxwing |
| `case-studies/front-yard-xeriscape.html` | Front Yard River Rock Conversion \| Waxwing |
| `case-studies/lafayette-cedar-fence.html` | Cedar Property-Line Fence in Lafayette \| Waxwing |
| `case-studies/lafayette-downspout-drainage.html` | Downspout Drainage, Lafayette CO \| Waxwing |
| `case-studies/lakewood-privacy-fence.html` | 6-Foot Privacy Fence, Lakewood CO \| Waxwing |
| `case-studies/longmont-flagstone-entry.html` | Flagstone Steps & Entry Refresh, Longmont \| Waxwing |
| `case-studies/river-rock-parking-pad.html` | Off-Street River Rock Parking Pad \| Waxwing |
| `case-studies/seasonal-landscape-cleanup.html` | Seasonal Landscape Clean-Up \| Waxwing |
| `case-studies/vertical-flagstone-longmont.html` | Vertical Flagstone Monolith, Longmont \| Waxwing |

One title is already over 60 characters and stays over, unchanged from today:
`blog-post-7`, at 83. It was already long before the switch; trimming it is a
separate job, not part of the name change. Everything else lands at 56 or under.

**`theme-lab.html` is excluded** — leave it out of the swap and out of the sitemap.

### 5c. Meta descriptions that change

Only the ones that name the company. The rest — drainage, fencing-longmont,
fall-cleanup, landscape-design, lawn-care, sprinkler-repair, blog posts — never say
"Groundwork" and need no edit at all.

| File | Description |
|---|---|
| `index.html` | Waxwing Landscaping provides expert hardscaping, fencing, and lawn care services in Longmont and Boulder County, CO. Built to last, season after season. |
| `about.html` | Meet the crew behind Waxwing Landscaping — hardscaping, fencing, and lawn care built to last in Longmont and Boulder County, CO. |
| `contact.html` | Contact Waxwing Landscaping for expert hardscaping, fencing, and lawn care services in Longmont and Boulder County, CO. Get a free quote today. |
| `work.html` | Explore real hardscaping, fencing, and landscape restoration case studies from Waxwing Landscaping in Longmont and Boulder County, CO. |
| `hardscaping-longmont.html` | Waxwing Landscaping designs and builds patios, walkways, retaining walls, fire pits, and drainage solutions in Longmont, Colorado. |
| `fencing-boulder.html` | Waxwing Landscaping installs cedar privacy, picket, split-rail, ornamental steel, and custom gates in Boulder, Colorado. |
| `lawn-care-longmont.html` | Waxwing Landscaping provides lawn mowing, aeration, overseeding, fertilization, and seasonal cleanup in Longmont, Colorado. |
| `xeriscaping-boulder-county.html` | Waxwing Landscaping creates water-wise xeriscapes, gravel landscapes, natural stone features, and lower-maintenance yards across Boulder County. |
| `accessibility.html` | Accessibility statement for the Waxwing Landscaping website, including how to report an access barrier or request assistance. |
| `privacy.html` | Privacy notice for Waxwing Landscaping and visitors who request a quote or contact the company. |
| `thank-you.html` | Your Waxwing Landscaping quote request has been received. |
| `404.html` | That page doesn't exist, but our hardscaping, fencing, and lawn care work around Longmont and Boulder County does. |

Two items are already over their limit **today**, before the switch, and stay over:
`blog-post-7`'s title at 83 characters, and `landscape-design-longmont`'s
description at 162 (that page's description never names the company, so it is not
in the table above). Neither is caused by the rename; trim them the next time those
pages are opened, not in this pass. Everything else is inside 60 / 160.

---

## 6. Google Business Profile

**Name:** Waxwing Landscaping

**Description** (750-character limit; this is 744):

> Waxwing Landscaping is a small, home-based crew building and maintaining outdoor
> spaces in Longmont and Boulder County. We do hardscaping (flagstone patios,
> retaining walls, walkways, fire pits), fencing (cedar privacy, picket, split-rail,
> ornamental steel, custom gates), and lawn care (mowing, aeration, overseeding,
> seasonal cleanup), plus drainage, xeriscaping, and sprinkler repair. One crew
> handles the whole property, so the person who quotes your project is the one
> building it. Materials and drainage are chosen for Colorado freeze-thaw, because
> that is what makes the surface last. Free on-site estimates; call or text
> (720) 893-0394.

**Service blurbs** (2–3 sentences each, no keyword stuffing):

- *Hardscaping* — Flagstone and paver patios, retaining walls, walkways, fire pits,
  and steps. Bases are compacted and drained for Front Range clay and freeze-thaw,
  because the base is what the surface is standing on.
- *Fencing* — Cedar privacy, picket, split-rail, and ornamental steel, plus custom
  gates and repairs to fences that have shifted. Posts are set in concrete and braced
  for wind, and the line gets checked before the first board goes up.
- *Lawn care* — Weekly and biweekly mowing, core aeration, overseeding, and seasonal
  cleanups. Same crew on a schedule, so the property stays finished between visits.
- *Xeriscaping* — Gravel and stone landscapes, native and low-water planting, and
  conversions from lawn. Designed to look intentional in August, not just in May.

---

## 7. Everywhere else the name lives

One-time edits, outside the build:

- **Footer line** — "© 2026 Waxwing Landscaping", plus "Free on-site estimates · <area>"
  in the page footers. The old "Licensed & insured" was dropped (§9).
- **Email** — `cmoneyq11@gmail.com` is on the site and on the schema. A
  `hello@waxwinglandscaping.com` (or `estimates@`) reads better on an estimate and on
  a door hanger; keep the Gmail as a forwarding catch-all rather than abandoning it.
- **Handles** — `@waxwinglandscaping` is free on Instagram, TikTok, X, YouTube and
  Pinterest (verified 2026-11-21). Claim all five in one sitting, even the ones that
  will sit empty, before somebody else does.
- **PDFs to regenerate** — `flyer-door-hanger.pdf`, `flyer-fall-cleanup.pdf`,
  `quote-calibration-worksheet.pdf`, `quote-calibration-worksheet-example.pdf`,
  `realtor-counter-card.pdf`. Their HTML sources live in `docs/marketing/`, which
  step 1 below deliberately skips, so they need the separate replace in step 2b.
- **Screenshots** — `qr-fall-page.png` and the repo's `screenshot-*.png` set show the
  old header; re-shoot only the ones that get published.
- **Social copy** — `social-post-series.md` signs every post "Groundwork Landscaping ·
  Longmont". One pass with the same replace.
- **Invoice/estimate template, truck lettering, business cards** — the only items that
  cost real money and cannot be re-run. Order them after the LLC filing.

---

## 8. The afternoon

Run order matters: replace the name, then the host, then rebuild, then verify. Do it
on a branch so the diff is reviewable.

```bash
cd ~/Projects/Web-dev/grondworkco
git switch -c rename-waxwing

# 1. The name. Longer form first, then the bare word.
#    Skips three kinds of copy that must keep the old name: build output (dist/,
#    regenerated in step 4), the planning and archive copies (claudplan4gg/,
#    dev-archive/), and the docs that record the decision on purpose.
FILES=$(grep -rl 'Groundwork' --include='*.html' --include='*.js' --include='*.py' \
  --include='*.xml' --include='*.txt' --include='*.md' . \
  | grep -v -E '^\./(dist|docs|claudplan4gg|dev-archive)/' \
  | grep -v -E 'README\.md$|EGM\.md$|DRIFT_REPORT' \
  | grep -v 'theme-lab.html')
echo "$FILES"          # 40 source files; read this list before running the next line
echo "$FILES" | xargs sed -i 's/Groundwork Landscaping/Waxwing Landscaping/g; s/Groundwork/Waxwing/g'

# 2. The internal section id. Not a brand string: three references in index.html,
#    and nothing in site.css depends on it.
sed -i 's/why-groundwork/why-us/g' index.html

# 2b. The flyer/card HTML sources, which live under docs/marketing and were skipped.
sed -i 's/Groundwork Landscaping/Waxwing Landscaping/g; s/Groundwork/Waxwing/g' \
  docs/marketing/*.html docs/marketing/door-hanger-copy.md \
  docs/marketing/social-post-series.md docs/marketing/past-client-outreach.md \
  docs/marketing/fall-reset-campaign.md docs/marketing/fall-campaign-checklist.md
#    Leave brand-copy.md and BRAND_AND_LAUNCH.md alone: they describe the switch.

# 3. The host. Skips dist/ for the same reason as step 1.
grep -rl 'waxwinglandscaping.com' . --exclude-dir=.git --exclude-dir=__pycache__ \
  --exclude-dir=dist --exclude-dir=claudplan4gg --exclude-dir=dev-archive \
  | xargs sed -i 's#groundworkllc\.netlify\.app#waxwinglandscaping.com#g'

# 4. Rebuild (build.py owns SITE, sitemap, dist/ and the JSON-LD image URLs).
python3 build.py

# 5. Verify nothing was missed or half-replaced.
grep -rn 'Groundwork' --exclude-dir=.git --exclude-dir=docs --exclude-dir=__pycache__ . || echo "name clean"
grep -rn 'netlify.app' --exclude-dir=.git --exclude-dir=docs --exclude-dir=__pycache__ . || echo "host clean"
grep -rn 'Wax Wing\|Waxwing Landscaping Landscaping' --exclude-dir=.git . || echo "no doubled words"
python3 check_links.py

# 6. Re-check the title/description limits before publishing.
python3 - <<'PY'
import re,glob
bad=0
for f in glob.glob('**/*.html',recursive=True):
    t=re.search(r'<title>(.*?)</title>',open(f,encoding='utf-8').read(),re.S)
    d=re.search(r'<meta name="description" content="(.*?)"',open(f,encoding='utf-8').read(),re.S)
    if t and len(t.group(1))>60: print(f"TITLE {len(t.group(1)):3} {f}"); bad+=1
    if d and len(d.group(1))>160: print(f"DESC  {len(d.group(1)):3} {f}"); bad+=1
print("clean" if not bad else f"{bad} over limit")
PY
```

Then, outside the repo: point the domain at Netlify, 301 the old host, add
`waxwinglandscaping.com` as a Search Console property, submit the sitemap, request
indexing on the five money pages. The old host's Search Console property is empty
(0 impressions, nothing ever submitted), so there is no history to lose — but the
301 is still worth setting so any link or bookmark that exists resolves.

Two notes from the dry run. **`site.css` is not in the replace list** because it
carries no brand string — verified at 0 hits; `build.py` (5), `site.js` (1) and
`check_links.py` (1) do, and step 1 covers them. And **`theme-lab.html` is excluded
by being a lab page**: it is not in `sitemap.xml`, so the stale brand in it is
harmless, but delete the file rather than let it drift.

---

## 9. Claims to check before this goes live

Not copy problems, but the copy carries them and they belong in the same pass:

- **"Licensed & insured" — dropped 2026-11-21**, replaced site-wide with "Free on-site
  estimates · <area>". Insurance is not in place yet and Colorado does not license
  landscapers statewide; the replacement is already true of the business.
- **"10+ years" kept** (the owner's own words). **"100+ properties" removed 2026-11-21** —
  no record states a total, and the only one ever used was the placeholder's false `220+`.
  The stat now reads the site's own documented count, generated by the build from
  `case-studies/*.html` (11 on 2026-11-21), so adding a case study updates it automatically. The owner's "hundreds of jobs" is a career claim for the About
  prose, not the stat row.
- **The three homepage testimonials** — removed 2026-11-21. They were placeholders
  (D. Rasmussen, M. Keller, J. Tran), not real quotes. The section is out of
  `index.html`; put it back only with quotes you can point at a job for. Same for
  the one quoted in `social-post-series.md` §6, which is the same placeholder text.
- **`priceRange` — set to `"$$"` 2026-11-21** in all four schema blocks. It was a
  positioning claim, not a verified fact; "$$" is truer for a small crew doing free
  estimates.
