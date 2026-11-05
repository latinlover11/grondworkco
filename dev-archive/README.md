# Dev Archive

## Overview

Frozen one-off audit, fix, and debug scripts from past modernization passes,
kept for provenance. Nothing here runs in the build, the link checker, or on
the live site. Treat the directory as read-only history: read a script before
running it — the fixers rewrite site HTML in place by design.

## Interface

- Audit / report scripts: `audit_site.py`, `audit_site_corrected.py`,
  `audit_site_fixed.py`, `audit_site_final.py`, `audit_site_final_report.py`,
  `performance_audit.py`, `detailed_performance_check.py`
- One-shot fixers: `fix_navigation.py`, `fix_blog_links.py`,
  `fix_case_studies.py`, `fix_case_study_anchors.py`, `add_alt_attributes.py`,
  `add_schema.py`, `remove_nav_items.py`, `remove_nav_items_v2.py`,
  `optimize_performance.py`, plus the `fix_nav*.sh` / `standardize_*.sh` shell
  variants
- Debug helpers: `debug_case_study.py`, `debug_links.py`
- Historical summaries (developer notes, preserved): `AUDIT_SUMMARY.md`,
  `AUDIT_FIX_SUMMARY.md`, `COMPLETION_SUMMARY.md`, `IMPROVEMENTS.md`,
  `OPTIMIZATION_SUMMARY.md`, `nav_consistency_report.md`
- Backup snapshots: `river-rock-parking-pad.html.backup`,
  `river-rock-parking-pad.html.bak`
- `.freebuff/` (hidden) — a tool artifact directory holding a single
  `project-id` file; not part of the archive proper, and already
  special-cased by `check_links.py` (line 150).

## Invariants

- Never imported or executed by the build: `build.py` line 14 lists
  `dev-archive` in `SKIP_DIRS`, and `check_links.py` skips the directory when
  crawling.
- Superseded work lives in `../docs/MODERNIZATION_PLAN.md`; these scripts are
  the record of what was already applied, not a pipeline to re-run.
- The `.backup` / `.bak` snapshots are historical references — do not delete
  or regenerate them.

## Side Effects

- The Python fixers anchor on this directory (`BASE_DIR =
  os.path.dirname(os.path.abspath(__file__))`), which contains no `.html`
  files — run today they would touch nothing outside `dev-archive/`.
- The `.sh` fixers use relative globs (`*.html blog/*.html
  case-studies/*.html`), so running one from the repo root would rewrite
  site HTML in place — that is what they did during their original pass.

## Verification

- None. This directory is deliberately outside every verification path.
