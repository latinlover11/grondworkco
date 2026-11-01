# Fall campaign — checklist

Audit of the Fall Reset kit against what the site and the print pieces actually
do. `[x]` = done in this pass, `[ ]` = needs the owner (accounts, print, sending).

Status: 1 November 2026. The campaign was written for a mid-October freeze; the
copy still assumes the freeze hasn't happened (see §5).

---

## 1. The landing page was orphaned — fixed

Before this pass, `fall-cleanup-longmont.html` was linked only from itself, the
lawn care page, and one blog post. The homepage had no link at all.

- [x] **Fall cleanup is in the site nav.** Added to `HEADER` in `build.py`, so it
      lands on every generated page (desktop nav + mobile panel).
- [x] **Homepage banner** above the services grid, linking the page with
      `?src=home-banner`.
- [ ] Remove the nav item after the season — it is marked with a comment in
      `build.py` (`Seasonal: remove the Fall cleanup item...`) so it is one edit.
- [ ] Consider `work.html` too, if the campaign runs past November.

## 2. Attribution — was a dead field, now wired

`contact.html` had a hidden `source` input that nothing ever wrote to, and there
was no analytics anywhere in the markup.

- [x] **`site.js` now fills `source`** from `?src=` (preferred) or `utm_source`,
      plus `utm_campaign`/`utm_medium`, and records the page it came from, e.g.
      `nextdoor -> fall-cleanup-longmont.html` or `direct -> contact.html`.
      Every Formspree submission now carries the channel.
- [x] **Internal CTAs tagged:** homepage banner (`src=home-banner`), fall page
      CTAs (`src=fall-page`).
- [ ] **Use tagged links in every post.** Ops out of habit spend money on
      channels they cannot see:

      nextdoor  .../fall-cleanup-longmont.html?src=nextdoor
      facebook  .../fall-cleanup-longmont.html?src=facebook
      gbp       .../fall-cleanup-longmont.html?src=gbp
      hanger    .../fall-cleanup-longmont.html?src=hangar
      qr        (already points at the page; QR scans arrive as `direct` unless
                the QR encodes `?src=qr` — regenerate if you want them split out)
      truck     .../fall-cleanup-longmont.html?src=truck

- [ ] **Verify on the first lead:** submit a test through the form with
      `?src=test` and confirm `source` shows up in the Formspree email.
- [ ] **Add free analytics** so you stop guessing: Cloudflare Web Analytics or
      Netlify Analytics — both work without a cookie banner and need no site
      changes beyond the snippet. GA4 is the alternative if you want event-level
      reporting and can live with consent.
- [ ] Optional but the only clean answer for phone leads: a call-tracking number
      for the campaign, kept separate from the GBP number.

## 3. Print — proof added, PDF regeneration blocked

- [x] **QR code generated**: `docs/marketing/qr-fall-page.png`, 296×296, points
      at the Fall Reset page.
- [x] **Real before/after strip** added to `flyer-fall-cleanup.html` — the corner
      lot pair, captioned "Before / After — same corner, one visit".
- [x] QR block sits beside the phone number ("scan for real job photos"), and the
      headline came down from 42pt to 36pt so the page still fits letter.
- [ ] **BLOCKED: the PDFs cannot be regenerated on this machine.**
      `build.py` needs weasyprint (or a `/tmp/pdfgen` venv); neither exists, and
      there is no chromium/wkhtmltopdf on PATH. So `flyer-fall-cleanup.pdf` is
      still the old all-type version. Install weasyprint (`pip install weasyprint`
      into `/tmp/pdfgen` or the system python), then `python3 build.py`
      regenerates only the PDFs whose HTML is newer. Until then, print from the
      HTML via a browser's "Save as PDF" and check it is one page.
- [ ] Same treatment for `flyer-door-hanger.html` (it also has zero photos) once
      the renderer is back — a hanger with one real yard photo beats copy.

## 4. The offer is still thin

Nothing here is a copy edit I can make honestly — these need your numbers.

- [ ] **A real deadline.** "Before the first freeze" has expired. Name a date:
      "booking through 15 November" or "last aeration week of the season."
- [ ] **Capacity, stated plainly.** "Eight cleanups left this season" is the most
      believable scarcity you own and it costs nothing to say.
- [ ] **A price band, if you'll allow one** — not a quote: "most Longmont lots
      land between $X and $Y, quoted on the walk-through." Kills the "what will
      this cost me" hang-up without committing you.
- [ ] **Sell the gutter at the reset price point.** Right now gutters only exist
      inside the Total Winterize, so a reset buyer never hears about them. One
      sentence on the walk-through and one line on the quote.
- [ ] **Neighbour-batch or referral offer**, e.g. "two houses on the same street
      booked together, the second one gets the blowout thrown in" — matches how
      the hanger ring already works.

## 5. Post-freeze pivot

The flyer and page both lean on "the first hard freeze usually lands by
mid-October". On 1 November that reads as either out of date or as though you
weren't paying attention. Keep the deadline, move the tense.

- [ ] Page: lead with leaves, gutters, and "what a freeze did to the lines you
      didn't purge" rather than "before the freeze".
- [ ] Retire kit Post 3 ("this week and next are the safe window") — do not post
      it as written.
- Ready-to-send variants:

      POST — post-freeze, cleanup still open
      The freeze is behind us, the leaves aren't. We're still hauling cleanups
      through November — leaves off the lawn and beds, gutters cleared, and a
      look at whether the sprinkler lines made it. Free estimates, Longmont &
      Boulder County: (720) 707-5411.

      POST — post-freeze, damage control
      If you didn't get the blowout in: a split backflow preventer is the usual
      casualty, and it's cheap to fix now and a plumber's bill in April. We'll
      check the system while we're there for the leaf cleanup. (720) 707-5411.

      DM/REPLY — to anyone who asked in October and went quiet
      Still want the yard done before the snow? We have room this week and the
      leaves are the easy part now they're down. (720) 707-5411.

## 6. Past clients — the cheapest money in the plan

- [x] Templates written: `docs/marketing/past-client-outreach.md`
      (text, email, review ask, referral ask, reactivation).
- [ ] Build the list: every job in the last 24 months, plus this season's case
      studies. A sheet with name / phone / email / last job / date is enough.
- [ ] Send 10 texts a day for a week. Text beats email for this trade.
- [ ] Log replies against the same sheet so §9 has numbers to read.

## 7. Reviews

The GBP checklist calls reviews the top ranking mover, and a fall cleanup ends
with a happy homeowner standing in a clean yard — that is the moment.

- [ ] Send the review ask (script in the outreach doc) the same evening as the
      walk-through, not weeks later.
- [ ] Reply to every review inside 48h, first name, neighbourhood mentioned.

## 8. Production — the campaign's proof supply

Evidence from this season's photo folders: three of four sets had no matched
before/after, and usable frames were lost to crew faces, licence plates, street
signs, and neighbour clutter. The campaign is only as good as the photos.

- [ ] **Photo standard for the crew**, one line to remember: *same spot, before
      and after, wide enough to show the fence line.*
- [ ] Phones out before the first rake, again before the truck leaves.
- [ ] Never shoot the street signs, house numbers, plates, or the neighbour's
      driveway.
- [ ] **Yard sign** — a "Fall Reset — done here" board at every fall job beats a
      hanger per impression, because it stays up for weeks. Copy:

      FALL RESET DONE HERE
      Leaves hauled · beds re-edged · aerated + overseeded
      Groundwork Landscaping · (720) 707-5411

## 9. Weekly scorecard

Ten minutes every Sunday. The kit says "log every lead" — this is what you log
into, otherwise it stays a notebook.

| Week | Posts sent | Hangers dropped | Calls | Quotes | Jobs booked | Avg ticket | Best source |
|---|---|---|---|---|---|---|---|
| Nov 1–7  |  |  |  |  |  |  |  |
| Nov 8–14 |  |  |  |  |  |  |  |
| Nov 15–21|  |  |  |  |  |  |  |

Rule: a channel with zero calls across two weeks of honest effort gets dropped
from the rotation, not defended.

---

## Gaps that need money or accounts, not code

- Google Business Profile: still the `gbp-setup-checklist.md` list; reviews are
  the whole game and none of it is automated here.
- Local Services Ads: needs licence/insurance verification and a budget.
- Email/SMS sending tool: nothing in the repo sends mail. A phone and a sheet
  work for a season; anything bigger wants a real tool.
- Realtor/pre-listing fall offer and HOA leaf contracts: both in
  `door-hanger-copy.md` as ideas, neither is a page or a flyer yet.
