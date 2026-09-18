#!/usr/bin/env python3
"""Build the static Groundwork site into dist/.

Source HTML remains easy to edit, while the deployed pages receive one shared
header and footer so navigation changes only need to be made here.
"""
from pathlib import Path
import re
import shutil

STYLE_RE = re.compile(r"<style(?:\s[^>]*)?>([\s\S]*?)</style>", re.IGNORECASE)

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
SKIP_DIRS = {".git", "dev-archive", "__pycache__", "dist"}
COPY_FILES = {"site.css", "site.js", "sitemap.xml", "robots.txt"}

HEADER = '''<header>
  <nav class="nav">
    <a href="/index.html" class="brand">Groundwork <span>Outdoor Co.</span></a>
    <ul class="nav-links">
      <li><a href="/index.html#services">Services</a></li>
      <li><a href="/work.html">Our Work</a></li>
      <li><a href="/about.html">About Us</a></li>
      <li><a href="/blog/index.html">Blog</a></li>
    </ul>
    <a href="/contact.html" class="nav-cta" data-analytics="quote">Get a quote</a>
    <button type="button" class="nav-toggle" id="nav-toggle" aria-label="Toggle menu" aria-expanded="false" aria-controls="nav-mobile-panel">
      <span></span><span></span><span></span>
    </button>
  </nav>
  <div class="nav-mobile-panel" id="nav-mobile-panel">
    <a href="/index.html#services">Services</a>
    <a href="/work.html">Our Work</a>
    <a href="/about.html">About Us</a>
    <a href="/blog/index.html">Blog</a>
    <a href="/contact.html" class="nav-cta" data-analytics="quote">Get a quote</a>
  </div>
</header>'''

FOOTER = '''<footer>
  <div class="wrap">
    <div class="footer-row">
      <div>© <span id="current-year">2026</span> Groundwork Outdoor Co. All rights reserved.</div>
      <div>Serving Longmont &amp; Boulder County</div>
      <div>
        <a href="tel:+17207075411" data-analytics="phone">(720) 707-5411</a><br>
        <a href="mailto:cmoneyq11@gmail.com">Email us</a>
      </div>
    </div>
  </div>
</footer>'''

ASSET_TAGS = '''<link rel="stylesheet" href="/site.css">
<script defer data-domain="groundworkoutdoor.co" src="https://plausible.io/js/script.js"></script>
<script defer src="/site.js"></script>'''


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def build_html(source: Path, target: Path) -> None:
    content = source.read_text(encoding="utf-8")
    # thank-you.html intentionally keeps its specialized confirmation shell.
    if source.name != "thank-you.html":
        content = re.sub(r"<header>[\s\S]*?</header>", HEADER, content, count=1)
        content = re.sub(r"<footer>[\s\S]*?</footer>", FOOTER, content, count=1)
        content = re.sub(r"<link rel=\"stylesheet\" href=\"/?site\.css\">\s*", "", content)
        content = re.sub(r"<script defer data-domain=\"groundworkoutdoor\.co\" src=\"https://plausible\.io/js/script\.js\"></script>\s*", "", content)
        content = re.sub(r"<script defer src=\"/?site\.js\"></script>\s*", "", content)
        styles = "\n\n".join(match.group(1).strip() for match in STYLE_RE.finditer(content))
        content = STYLE_RE.sub("", content)
        if styles:
            css_name = "__".join(source.relative_to(ROOT).with_suffix(".css").parts)
            css_target = DIST / "generated" / css_name
            css_target.parent.mkdir(parents=True, exist_ok=True)
            css_target.write_text(styles + "\n", encoding="utf-8")
            content = content.replace("</head>", f'<link rel="stylesheet" href="/generated/{css_name}">\n</head>', 1)
        content = content.replace("</head>", ASSET_TAGS + "\n</head>", 1)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    for path in ROOT.rglob("*"):
        if path.is_dir() or path == Path(__file__) or should_skip(path.relative_to(ROOT)):
            continue
        relative = path.relative_to(ROOT)
        destination = DIST / relative
        if path.suffix.lower() in {".html", ".htm"}:
            build_html(path, destination)
        elif path.name in COPY_FILES or relative.parts[0] == "img":
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)

    print(f"Built {sum(1 for _ in DIST.rglob('*.html'))} HTML pages into {DIST}")


if __name__ == "__main__":
    main()
