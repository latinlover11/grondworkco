# Brand and launch record

Captured 2026-11-13. Everything here was checked against a primary source; the
methods are listed so any claim can be re-run rather than trusted.

**Decision: the business name is Cottonwood & Stone.** It is not registered, not
filed, and no domain has been bought. Until an LLC is filed, this document is the
record of why the name was chosen — keep it in step with reality, and delete it
rather than let it drift into fiction.

---

## 1. Why the old name had to go

"Groundwork Landscaping" was a placeholder. Two real businesses share the word in
this market:

| Business | Where | Why it matters |
|---|---|---|
| Legacy Groundworks | Boulder, CO — full-service landscape contractor, ~20 years, serves Boulder County | Same trade, same county |
| Groundworks Foundation Repair | Denver branch with dedicated Longmont landing pages, ~2,746 reviews | Same city, high review volume |

A third Groundwork(s) within ~30 miles — one of them an incumbent in the same
trade — cannot win its own name in search, and the moment to change it is before
registration, GBP, lettering and citations, not after.

## 2. Names rejected, and by what evidence

| Candidate | Verdict | Evidence |
|---|---|---|
| **Switchback** | Dead | *Switchback Colorado Landscape & Sprinkler*, Commerce City — veteran-owned, ~93 Google reviews, does design, hardscape, fencing, irrigation, cleanups. A second Switchback exists in the Grand Valley. Name taken in the trade despite free domains. |
| **St. Vrain** | Weakened | St Vrain Arbor Care (140 Gay St, Longmont, ~30 yrs, tree/lawn), St Vrain Plant Health Care LLC, St Vrain Co (general contractor). Fourth use of the phrase. |
| **Blue Grama** | Rejected | `bluegramadesign.com` is live: "Native plant Landscape Design in Marfa, west Texas." Same two words, same service, commercially active — the confusingly-similar case that actually matters. Also descriptive (a grass, for a plant trade), which is the weakest kind of mark. |

## 3. Cottonwood & Stone — clearance evidence

### Colorado business registry

Source: the state's open-data copy of CDOS entities —
`https://data.colorado.gov/resource/4ykn-tg5h.json`, queried with SoQL
(`$where=upper(entityname) like '%COTTONWOOD%'`). This is a mirror of the
Secretary of State register, not a live name-availability ruling; the SOS decides
distinguishability at filing.

- **714** Colorado entity names contain "COTTONWOOD".
- Only two touch the trade, **and both are dead**: *Cottonwood Landscapes LLC*
  (delinquent since Sept 2020) and *Cottonwood Gardens Development Corp*
  (delinquent 2009).
- **Zero** entities match "COTTONWOOD STONE".
- "BLUE GRAMA" is used by 11 Colorado entities, several in good standing
  (Properties, Holdings, Consulting) — none in landscaping. That was not the
  disqualifier; §2 was.

### Federal trademark (USPTO)

Search: `cottonwood` in the USPTO's Trademark Search → **96 records, all 96
collected**, no duplicates. Status spread: 29 live/registered, 9 live/pending,
27 cancelled, 30 abandoned, 1 dead.

Records in the two classes this business would file under:

**Class 037 — building construction, repair, installation: 3 records, all dead**

| Mark | Serial | Status | Services |
|---|---|---|---|
| COTTONWOOD HILLS | 78341111 | Cancelled | Planning/laying out residential communities |
| COTTONWOOD RANCH | 74734548 | Cancelled | Residential community development |
| DEL WEBB'S COTTONWOOD RANCH | 75168811 | Cancelled | Residential community development |

**Class 044 — medical, veterinary, agriculture, horticulture: 5 records, 1 live**

| Mark | Serial | Status | Services |
|---|---|---|---|
| COTTONWOOD TUCSON | 88826117 | **Live/registered** | Addiction treatment |
| COTTONWOOD SPRINGS | 90605006 | Abandoned | Addiction/mental health |
| COTTONWOOD RETREAT | 88588348 | Abandoned | Massage, bodywork |
| COTTONWOOD PSYCHOLOGY CENTER | 97576716 | Abandoned | Maternal mental health |
| COTTONWOOD ANIMAL HOSPITAL | 85315729 | Cancelled | Veterinary |

The one live class-44 mark is healthcare in Tucson. Class 44 spans both medical
services and horticulture, so it shares a class number but not a market.

**Two facts that carry the decision:**

1. **No cottonwood mark contains "stone."** The composite is unclaimed.
2. **No cottonwood mark contains landscape, lawn, garden, hardscape, paver,
   nursery, irrigation or tree.** Nothing in the family competes in the trade.

For the record: the live marks cluster in finance/lending (8), plus candles,
fonts, golf clubs, hardware, wine, cakes, a church, a restaurant, a technology
fund and that one treatment centre. COTTONWOOD RESIDENTIAL is **class 036 only**
(serials 85346630, 85577044, 90543138, 88917857) — it is not a class-37 mark.

### Corrections made during the research

Keep these; they are the reason the headline numbers can be trusted.

1. An intermediate-mirror source listed COTTONWOOD RESIDENTIAL as class 037. The
   register says **036**. The caveat that an examiner might cite it in class 37
   was withdrawn.
2. An earlier 50-of-96 sample concluded "no live mark in class 44." The full
   sweep found **COTTONWOOD TUCSON** live in 44. Sampling, not the register, was
   wrong.

### Residual risk, stated plainly

"Cottonwood" is one of the most common words in Colorado business naming, so it
is a **weak mark**. It is fine for a local operator who needs a name, a domain and
a truck; it is not something to build a trademark portfolio on. It has not been
reviewed by an attorney, and no trademark application exists.

Still to be done by the owner, none of which can be done from this repo:

- **Re-check `cottonwoodandstone.com` immediately before buying.** It was
  unregistered on 2026-11-13 per Verisign RDAP
  (`https://rdap.verisign.com/com/v1/domain/cottonwoodandstone.com` — 404 means
  unregistered). That says nothing about next week.
- **Colorado SOS name search** at the moment of filing; "&" and "and" are treated
  as equivalent, so reserve it exactly as it will be printed.
- **USPTO search before any application** — an examiner reads the goods-and-
  services wording, and that wording is the part that decides the outcome.

## 4. How to re-run the checks

The register blocks automated clients: `tmsearch.uspto.gov` returns HTTP 405 from
its S3 front on every API route, `uspto.report` and `trademarks.justia.com/search`
return 403, `tmdn.org` WAF-rejects POST. The workable route is a headless browser.

```bash
python3 -m venv /tmp/pwenv            # this machine has no pip
/tmp/pwenv/bin/pip install playwright
/tmp/pwenv/bin/python -m playwright install firefox
```

Driving the site, and the two things that cost the most time to discover:

- The search box is `#searchbar`; Enter submits. Result rows are
  `[class*=card]` containing "Serial" and "Wordmark".
- **There is no next-page control and infinite scroll does nothing.** The list
  caps at 50 per page behind a page-size dropdown whose options are in the DOM but
  hidden. Click the trigger (`button:has-text('per page')`), then click the
  element whose text is exactly `100 per page` **and whose `offsetParent` is not
  null** — matching on text alone picks a hidden copy and times out.

Colorado entity data needs no browser:

```bash
curl -sG "https://data.colorado.gov/resource/4ykn-tg5h.json" \
  --data-urlencode "\$where=upper(entityname) like '%COTTONWOOD%'" \
  --data-urlencode '$limit=400'
```

Add `.com` status with:

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  "https://rdap.verisign.com/com/v1/domain/cottonwoodandstone.com"   # 404 = free
```

## 5. Launch sequence, and why this order

The business is not registered yet and is deliberately staying small for a few
months. That makes the ordering cheap rather than urgent — Colorado landscaping
demand resumes in March, so the real deadline is spring quote season.

1. **Name, then domain, then register.** The only steps that get expensive later.
2. **Content — done.** `fencing-longmont.html`,
   `sprinkler-repair-longmont.html`, `landscape-design-longmont.html` shipped in
   `6a4e7c7`. None of it depends on the hostname.
3. **Point the domain at Netlify, 301 the old host, rebuild canonicals and
   sitemap, create the new GSC property, submit, request indexing.**
4. **Register → business phone + insurance → Google Business Profile** as a
   service-area business with the address hidden → reviews from first real jobs.
5. **Rank tracking**, once positions mean something.

### State of the site as of 2026-11-13

- 38 indexable pages, `sitemap.xml` carrying 35 URLs, `check_links.py` green.
- `groundworkllc.netlify.app` is the only host. GitHub Pages was **disabled** on
  2026-11-13 (API 404, host 404) — it had been serving the repo root, a second
  public copy of every page.
- Search Console property `groundworkllc.netlify.app/` is **empty**: 0 impressions
  for 2025-07-14 → 2026-11-11, and six inspected URLs all return "URL is unknown
  to Google." **Nothing has ever been submitted**, so there is no indexing history
  to lose when the domain changes.

### Two mechanics that will bite on the domain move

- `https://groundworkllc.netlify.app` is hardcoded in **~50 files / 210
  occurrences** — canonicals, `og:url`, JSON-LD `provider.url`, `sitemap.xml`,
  `robots.txt`, `url.txt`. `build.py` has `SITE` but no shared template for page
  canonicals; `sitemap.xml` is a source file edited by hand. The move is a
  scripted replace plus a rebuild, not a rewrite.
- The phone number `(720) 893-0394` appears sitewide the same way. The business
  number will change (Google Voice), so **swap the phone number in the same pass
  as the hostname.**

### Site mechanic worth remembering

`site.js` applies `?service=` only if the value exists as an `<option>` in
`contact.html`, and the quote sheet reads `<body data-service>`. A new service
page without a matching option fails silently — the form just arrives unselected.

### Google Business Profile

The address is not the blocker: Google supports service-area businesses, where a
real address is required behind the scenes but hidden publicly and service areas
shown instead. A home address is the normal setup for a home-based contractor; PO
box, UPS Store and virtual office are prohibited. The actual blocker is
verification — video of vehicle, tools and workspace plus a business document —
for a business that is not registered and has no job history. A suspended Profile
stuck to a home address is worse than no Profile, so the Profile follows
registration and insurance.

Worth accumulating meanwhile, because it is the same evidence verification asks
for: before/after photo pairs per job, a dedicated business phone number, and
job dates with city-level locations.
