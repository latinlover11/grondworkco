#!/usr/bin/env python3
"""Build the static Groundwork site into dist/.

Source HTML remains easy to edit, while the deployed pages receive one shared
header and footer so navigation changes only need to be made here.
"""
from pathlib import Path
import datetime
import re
import shutil
import subprocess

STYLE_RE = re.compile(r"<style(?:\s[^>]*)?>([\s\S]*?)</style>", re.IGNORECASE)

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
SKIP_DIRS = {".git", "dev-archive", "__pycache__", "dist"}
COPY_FILES = {"site.css", "site.js", "sitemap.xml", "robots.txt"}
COPY_DIRS = {"fonts"}

HEADER = '''<header>
  <nav class="nav">
    <a href="/index.html" class="brand"><svg class="brand-mark" width="28" height="28" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><g fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M10 48h44" stroke="#C16A2E" stroke-width="5"/><path d="M10 37h34" stroke="#C16A2E" stroke-width="5"/><path d="M10 26h24" stroke="#E08A3E" stroke-width="5"/><path d="M43 12c7 1 11 6 10 13-7 0-11-4-10-13Z" stroke="#6E8367" stroke-width="4"/><path d="M43 25c0-5 2-9 6-13" stroke="#6E8367" stroke-width="3"/></g></svg>Groundwork <span>Landscaping</span></a>
    <ul class="nav-links">
      <li><a href="/index.html#services">Services</a></li>
      <li><a href="/work.html">Our Work</a></li>
      <li><a href="/about.html">About Us</a></li>
      <li><a href="/blog/index.html">Blog</a></li>
    </ul>
    <a href="/contact.html" class="nav-cta">Get a quote</a>
    <button type="button" class="nav-toggle" id="nav-toggle" aria-label="Toggle menu" aria-expanded="false" aria-controls="nav-mobile-panel">
      <span></span><span></span><span></span>
    </button>
  </nav>
  <div class="nav-mobile-panel" id="nav-mobile-panel">
    <a href="/index.html#services">Services</a>
    <a href="/work.html">Our Work</a>
    <a href="/about.html">About Us</a>
    <a href="/blog/index.html">Blog</a>
    <a href="/contact.html" class="nav-cta">Get a quote</a>
  </div>
</header>'''

FOOTER = '''<footer>
  <div class="wrap">
    <div class="footer-row">
      <div>© <span id="current-year">2026</span> Groundwork Landscaping. All rights reserved.</div>
      <div>Serving Longmont &amp; Boulder County</div>
      <div>
        <a href="tel:+17207075411">(720) 707-5411</a><br>
        <a href="mailto:cmoneyq11@gmail.com">Email us</a>
      </div>
    </div>
  </div>
</footer>'''

ASSET_TAGS = '''<link rel="stylesheet" href="/site.css">
<script defer src="/site.js"></script>'''

FONT_TAGS = '''<link rel="preload" href="/fonts/fraunces-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/work-sans-var.woff2" as="font" type="font/woff2" crossorigin>'''


def minify_css(css: str) -> str:
    """Safe-for-this-site CSS minification: strip comments and redundant
    whitespace. Does not parse CSS, so it relies on the codebase's simple
    formatting (no strings containing '//' or '; ')."""
    css = re.sub(r"/\*[\s\S]*?\*/", "", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css)
    css = css.replace(";}", "}")
    return css.strip()


def inject_twitter_card(content: str) -> str:
    """Derive twitter:* tags from existing og: tags so card previews work on
    X/Slack/iMessage without every page hand-maintaining a second tag set."""
    if "twitter:card" in content:
        return content

    def grab(prop: str, default: str = "") -> str:
        m = re.search(rf'<meta property="{prop}" content="([^"]*)"', content)
        return m.group(1) if m else default

    title_m = re.search(r"<title>([^<]*)</title>", content)
    desc = grab("og:description") or grab("description")
    image = grab("og:image", "/img/og-image.jpg")
    if image.startswith("/"):
        image = "https://groundworkllc.netlify.app" + image
    tags = (
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{title_m.group(1) if title_m else "Groundwork Landscaping"}">\n'
        f'<meta name="twitter:description" content="{desc}">\n'
        f'<meta name="twitter:image" content="{image}">'
    )
    return content.replace("</head>", tags + "\n</head>", 1)


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def build_html(source: Path, target: Path) -> None:
    content = source.read_text(encoding="utf-8")
    # thank-you.html intentionally keeps its specialized confirmation shell.
    if source.name != "thank-you.html":
        content = re.sub(r"<header>[\s\S]*?</header>", HEADER, content, count=1)
        content = re.sub(r"<footer>[\s\S]*?</footer>", FOOTER, content, count=1)
        content = re.sub(r"<link rel=\"stylesheet\" href=\"/?site\.css\">\s*", "", content)
        content = re.sub(r"<script defer src=\"/?site\.js\"></script>\s*", "", content)
        styles = "\n\n".join(match.group(1).strip() for match in STYLE_RE.finditer(content))
        content = STYLE_RE.sub("", content)
        if styles:
            # Page CSS ships inline in <head>: one fewer render-blocking request,
            # no FOUC, and page-relative url()s keep working (no /generated/ move).
            content = content.replace("</head>", f"<style>{minify_css(styles)}</style>\n</head>", 1)
        content = content.replace("</head>", ASSET_TAGS + "\n</head>", 1)
    # Google-hosted font CSS is replaced by self-hosted @font-face rules in
    # site.css; drop the network requests (attribute order varies: some pages
    # use <link href=... rel=.../>, others rel=... href=...). Applied to every
    # page including thank-you.html.
    content = re.sub(r'<link[^>]*https://fonts[.]g(?:oogleapis|static)[.]com[^>]*/?>\s*', "", content)
    content = inject_twitter_card(content)
    content = content.replace("</head>", FONT_TAGS + "\n</head>", 1)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def git_lastmod(path: Path) -> str:
    """YYYY-MM-DD of the last commit touching this file; today if untracked."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", str(path.relative_to(ROOT))],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return out[:10] if out else datetime.date.today().isoformat()
    except Exception:
        return datetime.date.today().isoformat()


def build_sitemap() -> None:
    """Add <lastmod> to every sitemap URL from the page's git history."""
    source = ROOT / "sitemap.xml"
    content = source.read_text(encoding="utf-8")

    def add_lastmod(match: re.Match) -> str:
        loc = match.group(1)
        rel = loc.replace("https://groundworkllc.netlify.app/", "").lstrip("/")
        page = ROOT / (rel or "index.html")
        date = git_lastmod(page)
        return f"<url><loc>{loc}</loc><lastmod>{date}</lastmod></url>"

    content = re.sub(r"<url><loc>([^<]+)</loc></url>", add_lastmod, content)
    (DIST / "sitemap.xml").write_text(content, encoding="utf-8")


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
        elif path.name in COPY_FILES or relative.parts[0] in COPY_DIRS | {"img"}:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)

    # Minify the shared stylesheet too (page CSS is minified per-page above).
    site_css = DIST / "site.css"
    site_css.write_text(minify_css(site_css.read_text(encoding="utf-8")) + "\n", encoding="utf-8")

    build_sitemap()

    print(f"Built {sum(1 for _ in DIST.rglob('*.html'))} HTML pages into {DIST}")


if __name__ == "__main__":
    main()

