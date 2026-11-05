# Docs

## Overview

Planning and marketing documents. Not part of the deployed site — `build.py`
line 14 lists `docs` in `SKIP_DIRS` — but not fully detached from it either:
the marketing flyers are build inputs for print-PDF regeneration.

## Subdirectories & Boundaries

- `marketing/` (no contract; content package) — campaign copy, checklists,
  a QR code asset (`qr-fall-page.png`), and the flyer/worksheet HTML sources
  that `build.py` renders to PDF, next to the generated PDFs themselves.

## Key Files

- `MODERNIZATION_PLAN.md` — September 2026 modernization plan (referenced by
  the root README's photo-checklist section, §2.1).
- `WEBSITE_IMPROVEMENT_PLAN.md` — October 2026 improvement plan (the later
  of the two).

## Invariants

- `build.py` lines 19–30 (`PDF_JOBS`) regenerate five PDFs in
  `docs/marketing/` (`flyer-door-hanger.pdf`, `flyer-fall-cleanup.pdf`,
  `realtor-counter-card.pdf`, `quote-calibration-worksheet.pdf`,
  `quote-calibration-worksheet-example.pdf`) from their same-named `.html`
  sources on every build — but only when the HTML is newer than the PDF
  (`build.py` lines 450–452), and a rendering failure never fails the site
  build (`build.py` line 455).
- Editing a flyer `.html` here changes a file in the *source tree* on the
  next build — the PDFs are not build artifacts in `dist/`.

## Side Effects

- None at rest. A build writes into `docs/marketing/*.pdf` (see above).

## Verification

- Run: `python3 build.py` (PDF regeneration is part of the build output).
