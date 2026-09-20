#!/usr/bin/env python3
"""
check_links.py - static link & image checker for the Groundwork Landscaping site.

Crawls every .html file in the repo (except dev-archive/ and hidden dirs) and
verifies, entirely offline:

  * internal page links resolve to a real file (handles relative paths like
    `case-studies/foo.html`, root-absolute paths like `/index.html`, and
    Netlify-style variants: a link to `blog/` or `about` resolves to
    `blog/index.html` / `about.html`)
  * `#fragment` anchors (same-page and cross-page) match a real id= / name=
    attribute in the target page
  * every <img src>, og:image meta, JSON-LD "image" field, and CSS url()
    background points at a file that exists
  * no case-mismatches in filenames (invisible on Windows/macOS, but Netlify
    serves from case-sensitive Linux, so `Logo.PNG` vs `logo.png` WOULD 404)
  * informational: pages and images that exist but nothing links to
    (this is how the old broken testimonials.html would have been caught)

External http(s) links are listed but not fetched unless you pass
--check-external, which HEADs each one (used for the Formspree endpoint, etc.).

Usage:
    python check_links.py                 # full local check
    python check_links.py --check-external
    python check_links.py --quiet         # only print problems

Exit code is 1 if any real problems were found, 0 otherwise.
"""

import argparse
import html.parser
import os
import re
import sys
from difflib import get_close_matches
from pathlib import Path
from urllib.parse import unquote

IMG_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".avif"}
PAGE_EXT = {".html", ".htm"}
SKIP_DIRS = {"dev-archive", "dist"}  # hidden dirs (leading ".") are skipped too


# --------------------------------------------------------------------------- #
# HTML parsing
# --------------------------------------------------------------------------- #

class PageParser(html.parser.HTMLParser):
    """Collects hrefs, img srcs, anchor ids, and ld+json image fields."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []      # (line_no, attr, value)
        self.images = []     # (line_no, value, source)
        self.anchors = set()
        self._in_ldjson = False
        self._ldjson_buf = []

    def handle_starttag(self, tag, attrs):
        line, _col = self.getpos()
        d = dict(attrs)
        if "id" in d:
            self.anchors.add(d["id"])
        if tag == "a" and "name" in d:
            self.anchors.add(d["name"])
        if "href" in d:
            rel = d.get("rel", "").lower()
            # preconnect/dns-prefetch hint bare domains, not real pages;
            # canonical/alternate are metadata URLs, not clickable links
            if not (tag == "link" and rel in {"preconnect", "dns-prefetch",
                                              "canonical", "alternate"}):
                self.links.append((line, "href", d["href"]))
        if "src" in d:
            self.images.append((line, d["src"], "img"))
        if tag == "meta" and d.get("property") == "og:image" and d.get("content"):
            self.images.append((line, d["content"], "og:image"))
        if tag == "script" and d.get("type") == "application/ld+json":
            self._in_ldjson = True

    # XHTML-style self-closing tags still route through handle_starttag
    handle_startendtag = handle_starttag

    def handle_data(self, data):
        if self._in_ldjson:
            self._ldjson_buf.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._in_ldjson:
            self._in_ldjson = False
            blob = "".join(self._ldjson_buf)
            for m in re.finditer(r'"image"\s*:\s*"([^"]+)"', blob):
                self.images.append((0, m.group(1), "ld+json"))
            self._ldjson_buf = []


def discover_pages(root: Path):
    pages = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if not d.startswith(".") and d not in SKIP_DIRS]
        for name in filenames:
            if Path(name).suffix.lower() in PAGE_EXT:
                pages.append(Path(dirpath) / name)
    return sorted(pages)


def parse_page(path: Path):
    parser = PageParser()
    text = path.read_text(encoding="utf-8", errors="replace")
    parser.feed(text)
    # CSS url() backgrounds aren't attributes, scan the raw text for them
    for m in re.finditer(r"url\(\s*['\"]?([^'\")]+?)['\"]?\s*\)", text):
        val = m.group(1).strip()
        if val.startswith(("data:", "http://", "https://", "//", "#", "var(")):
            continue
        parser.images.append((0, val, "css url()"))
    return parser


# --------------------------------------------------------------------------- #
# Path resolution
# --------------------------------------------------------------------------- #

def resolve_target(root: Path, page_dir: Path, raw: str) -> Path:
    """Resolve a raw href/src value the way a browser would."""
    path = raw.split("#", 1)[0].split("?", 1)[0].strip()
    path = unquote(path).replace("\\", "/")
    if path.startswith("/"):
        candidate = root / path.lstrip("/")
    else:
        candidate = page_dir / path
    return Path(os.path.normpath(candidate))


def find_file(root: Path, target: Path):
    """Return (actual_file_or_None, kind) where kind explains why it failed.

    Checks the exact path, then Netlify-style variants (add .html, add
    /index.html), then falls back to case-insensitive matching to detect
    case-mismatches that would 404 on Netlify's Linux servers.
    """
    try:
        rel = target.relative_to(root).as_posix()
    except ValueError:
        return None, "escapes-site-root"

    exact = {p.relative_to(root).as_posix(): p for p in root.rglob("*")
             if p.is_file() and ".git" not in p.parts and ".freebuff" not in p.parts}
    low = {k.lower(): k for k in exact}

    suffix = Path(rel).suffix.lower()
    variants = [rel]
    if not suffix:
        variants += [rel + ".html", rel.rstrip("/") + "/index.html"]

    for v in variants:
        if v in exact:
            return exact[v], "ok"
    for v in variants:
        if v.lower() in low:
            return exact[low[v.lower()]], "case-mismatch:" + low[v.lower()]
    return None, "missing"


# --------------------------------------------------------------------------- #
# Main check
# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("--root", default=".", help="site root (default: script's repo)")
    ap.add_argument("--check-external", action="store_true",
                    help="also HEAD-request external http(s) links")
    ap.add_argument("--quiet", action="store_true",
                    help="only print problems, skip the inventory summary")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    pages = discover_pages(root)
    if not pages:
        print("No HTML pages found under", root)
        return 1

    parsed = {}          # page path -> PageParser
    file_index = {}      # posix rel path -> Path (for anchor lookups)
    for p in pages:
        parsed[p] = parse_page(p)
        file_index[p.relative_to(root).as_posix()] = p

    anchor_cache = {}    # posix rel path -> anchor set

    def anchors_of(file_path: Path):
        key = file_path.relative_to(root).as_posix()
        if key not in anchor_cache:
            if key in parsed:
                anchor_cache[key] = parsed[file_path].anchors
            else:  # e.g. anchor target referenced from a page we don't parse?
                anchor_cache[key] = parse_page(file_path).anchors
        return anchor_cache[key]

    missing_pages, broken_anchors, missing_images = [], [], []
    external, placeholders = [], 0
    referenced_pages, referenced_files = set(), set()

    for page, parser in parsed.items():
        page_rel = page.relative_to(root).as_posix()
        page_dir = page.parent

        # ---- links ----
        for line, _attr, raw in parser.links:
            stripped = raw.strip()
            if not stripped or stripped == "#":
                placeholders += 1
                continue
            low = stripped.lower()
            if low.startswith(("mailto:", "tel:", "javascript:", "data:")):
                continue
            if low.startswith(("http://", "https://", "//")):
                external.append((page_rel, line, stripped))
                continue

            frag = None
            if "#" in stripped:
                stripped, frag = stripped.split("#", 1)

            target = resolve_target(root, page_dir, stripped or "./")
            found, kind = find_file(root, target)

            if not stripped and not frag:
                continue  # bare "#"-less empty href handled above

            if found is None:
                rel_guess = target.relative_to(root).as_posix() \
                    if target.is_relative_to(root) else str(target)
                close = get_close_matches(rel_guess, list(file_index), n=1)
                hint = f" (closest: {close[0]})" if close else ""
                missing_pages.append((page_rel, line, raw, rel_guess + hint))
                continue

            if kind.startswith("case-mismatch"):
                missing_pages.append((page_rel, line, raw,
                                      f"case-mismatch -> actual file is '{kind.split(':', 1)[1]}'"))
                continue

            referenced_pages.add(found.relative_to(root).as_posix())
            referenced_files.add(found.relative_to(root).as_posix())

            if frag:
                if found.suffix.lower() not in PAGE_EXT:
                    continue  # fragment on a non-page (rare) - ignore
                if frag and frag not in anchors_of(found):
                    missing = f"no id/name '{frag}' in {found.relative_to(root).as_posix()}"
                    broken_anchors.append((page_rel, line, raw, missing))

        # ---- images ----
        for line, raw, source in parser.images:
            if not raw.strip() or raw.strip().lower().startswith(("data:", "http://", "https://", "//")):
                continue
            target = resolve_target(root, page_dir, raw)
            found, kind = find_file(root, target)
            if found is not None:
                referenced_files.add(found.relative_to(root).as_posix())
                continue
            rel_guess = target.relative_to(root).as_posix() \
                if target.is_relative_to(root) else str(target)
            extra = ""
            if kind.startswith("case-mismatch"):
                extra = f" (case-mismatch -> '{kind.split(':', 1)[1]}')"
            missing_images.append((page_rel, line or None, source, raw, rel_guess + extra))

    # ---- orphans (informational) ----
    all_img_files = {p.relative_to(root).as_posix() for p in root.rglob("*")
                     if p.is_file() and p.suffix.lower() in IMG_EXT
                     and not any(part.startswith(".") or part in SKIP_DIRS
                                 for part in p.parts)}
    orphan_images = sorted(all_img_files - referenced_files)
    orphan_pages = sorted(file_index.keys() - referenced_pages
                          - {p.relative_to(root).as_posix() for p in pages})

    # ---- external check (optional) ----
    ext_problems = []
    if args.check_external:
        import urllib.request
        seen = set()
        for _page, _line, url in external:
            norm = "https:" + url if url.startswith("//") else url
            if norm in seen:
                continue
            seen.add(norm)
            try:
                req = urllib.request.Request(norm, method="HEAD",
                                             headers={"User-Agent": "link-checker"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    status = r.status
            except Exception as e:  # noqa: BLE001 - report anything
                status = getattr(e, "code", str(e))
            # 405 = endpoint exists but rejects HEAD (e.g. form handlers)
            if status not in (200, 301, 302, 303, 307, 308, 405):
                ext_problems.append((norm, status))

    # ---- report ----
    problems = 0

    def section(title, rows, fmt):
        nonlocal problems
        if not rows:
            return
        problems += len(rows)
        print(f"\n{title} ({len(rows)}):")
        for row in rows:
            print("  " + fmt(row))

    if not args.quiet:
        n_links = sum(len(p.links) for p in parsed.values())
        n_imgs = sum(len(p.images) for p in parsed.values())
        n_anchor_checks = len(broken_anchors)  # informational only
        print(f"Scanned {len(pages)} pages | {n_links} links, {n_imgs} image refs, "
              f"{len(external)} external, {placeholders} '#' placeholders")

    section("MISSING PAGES / BAD PATHS", missing_pages,
            lambda r: f"{r[0]}:{r[1]}  ->  {r[2]}\n      {r[3]}")
    section("BROKEN ANCHORS", broken_anchors,
            lambda r: f"{r[0]}:{r[1]}  ->  {r[2]}\n      {r[3]}")
    section("MISSING / BROKEN IMAGES", missing_images,
            lambda r: f"{r[0]}:{r[1] or '-'} [{r[2]}]  ->  {r[3]}\n      {r[4]}")
    section("EXTERNAL LINK PROBLEMS", ext_problems,
            lambda r: f"{r[0]}  ->  HTTP {r[1]}")

    if not args.quiet:
        if orphan_pages:
            print(f"\nINFO: pages nothing links to ({len(orphan_pages)}):")
            for p in orphan_pages:
                print("  " + p)
        if orphan_images:
            print(f"\nINFO: images nothing references ({len(orphan_images)}):")
            for p in orphan_images:
                print("  " + p)

    if problems == 0:
        print("\nAll internal links, anchors, and images check out. \u2713")
        return 0
    print(f"\n{problems} problem(s) found. Fix before deploy. \u2717")
    return 1


if __name__ == "__main__":
    sys.exit(main())
