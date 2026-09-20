#!/usr/bin/env python3
"""Build the static Groundwork site into dist/."""
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
    <a href="/index.html" class="brand" style="color:inherit;text-decoration:none"><svg class="brand-mark" width="28" height="28" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><circle cx="32" cy="32" r="25" fill="#C87955"/><path d="M13 45 26 26l7 9 7-11 12 21H13Z" fill="#3B2A22"/><path d="M34 29c.8-8 5-13 12-15 .8 7.5-3.1 13-12 15Z" fill="#78836B"/><path d="M34 29c1.8-5.2 5.2-9.2 9.6-12.2" fill="none" stroke="#FFF9F0" stroke-width="2.3" stroke-linecap="round"/></svg>Groundwork <span>Landscaping</span></a>
    <ul class="nav-links">
      <li><a href="/index.html#services">Services</a></li>
      <li><a href="/work.html">Our Work</a></li>
      <li><a href="/about.html">About Us</a></li>
      <li><a href="/blog/index.html">Blog</a></li>
    </ul>
    <a href="/contact.html" class="nav-cta">Get a quote</a>
    <button type="button" class="nav-toggle" id="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="nav-mobile-panel">
      <span></span><span></span><span></span>
    </button>
  </nav>
  <div class="nav-mobile-panel" id="nav-mobile-panel" aria-hidden="true">
    <a href="/index.html#services">Services</a>
    <a href="/work.html">Our Work</a>
    <a href="/about.html">About Us</a>
    <a href="/blog/index.html">Blog</a>
    <a href="/contact.html" class="nav-cta">Get a quote</a>
  </div>
</header>'''

FOOTER = '''<footer class="site-footer">
  <div class="wrap">
    <div class="site-footer-grid">
      <div class="site-footer-brand">
        <a href="/index.html">Groundwork <span>Landscaping</span></a>
        <p>Hardscaping, fencing, and lawn care built for Colorado properties.</p>
      </div>
      <nav class="site-footer-links" aria-label="Footer navigation">
        <a href="/index.html#services">Services</a>
        <a href="/work.html">Our Work</a>
        <a href="/about.html">About Us</a>
        <a href="/blog/index.html">Blog</a>
      </nav>
      <div class="site-footer-contact">
        <a href="tel:+17207075411">(720) 707-5411</a>
        <a href="mailto:cmoneyq11@gmail.com">Email us</a>
        <span>Longmont &amp; Boulder County</span>
      </div>
    </div>
    <div class="site-footer-bottom">
      <span>© <span id="current-year">2026</span> Groundwork Landscaping</span>
      <a href="/contact.html">Request a quote →</a>
    </div>
  </div>
</footer>'''

ASSET_TAGS = '''<link rel="stylesheet" href="/site.css?v=earthy-v2">
<script defer src="/site.js"></script>'''
FONT_TAGS = '''<link rel="preload" href="/fonts/fraunces-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/work-sans-var.woff2" as="font" type="font/woff2" crossorigin>'''


def minify_css(css: str) -> str:
    css = re.sub(r"/\*[\s\S]*?\*/", "", css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{}:;,>])\s*", r"\1", css)
    css = css.replace(";}", "}")
    return css.strip()


def inject_twitter_card(content: str) -> str:
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
    tags = (f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:title" content="{title_m.group(1) if title_m else "Groundwork Landscaping"}">\n'
            f'<meta name="twitter:description" content="{desc}">\n'
            f'<meta name="twitter:image" content="{image}">')
    return content.replace("</head>", tags + "\n</head>", 1)


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def transform_gallery_markup(content: str) -> str:
    """Convert legacy gallery inline handlers into declarative attributes."""
    def switch_photo(match: re.Match) -> str:
        case_id, src, caption = match.groups()
        return f' data-gallery-id="{case_id}" data-gallery-src="{src}" data-gallery-caption="{caption}"'

    content = re.sub(
        r"\s+onclick=\"switchCasePhoto\('([^']+)',\s*'([^']+)',\s*'([^']*)',\s*this\)\"",
        switch_photo,
        content,
    )

    def open_photo(match: re.Match) -> str:
        src, caption = match.groups()
        return f' data-lightbox-src="{src}" data-lightbox-caption="{caption}"'

    content = re.sub(
        r"\s+onclick=\"openLightbox\('([^']+)',\s*'([^']*)'\)\"",
        open_photo,
        content,
    )
    content = re.sub(r"\s+onclick=\"openLightbox\(this(?:\.src,\s*this\.alt)?\)\"", " data-lightbox-trigger", content)
    content = re.sub(r'id="([^\"]+)-main-img" data-lightbox-trigger', r'id="\1-main-img" data-gallery-id="\1" data-lightbox-trigger', content)
    content = re.sub(r"\s+onclick=\"closeLightbox\(event\)\"", "", content)

    def add_trigger_semantics(match: re.Match) -> str:
        return match.group(1) + ' role="button" tabindex="0" ' + match.group(2)

    content = re.sub(
        r'(<(?:div|figure)\s+class="gallery-card[^>]*)(data-lightbox-src=|data-lightbox-trigger)',
        add_trigger_semantics,
        content,
    )

    def card_button(match: re.Match) -> str:
        attrs, body = match.groups()
        return f'<button type="button"{attrs}>{body}</button>'

    content = re.sub(r'<figure(\s+class="gallery-card[^>]*data-lightbox[^>]*)>(.*?)</figure>', card_button, content, flags=re.DOTALL)
    return content


def build_html(source: Path, target: Path) -> None:
    content = source.read_text(encoding="utf-8")
    if source.name != "thank-you.html":
        content = re.sub(r"<header(?:\s[^>]*)?>[\s\S]*?</header>", HEADER, content, count=1)
        content = re.sub(r"<footer(?:\s[^>]*)?>[\s\S]*?</footer>", FOOTER, content, count=1)
        content = re.sub(r"<link rel=\"stylesheet\" href=\"/?site\.css\">\s*", "", content)
        content = re.sub(r"<script defer src=\"/?site\.js\"></script>\s*", "", content)
        styles = "\n\n".join(match.group(1).strip() for match in STYLE_RE.finditer(content))
        content = STYLE_RE.sub("", content)
        if styles:
            content = content.replace("</head>", f"<style>{minify_css(styles)}</style>\n</head>", 1)
        content = content.replace("</head>", ASSET_TAGS + "\n</head>", 1)
    content = transform_gallery_markup(content)
    content = re.sub(r'<link[^>]*https://fonts[.]g(?:oogleapis|static)[.]com[^>]*/?>\s*', "", content)
    content = inject_twitter_card(content)
    content = content.replace("</head>", FONT_TAGS + "\n</head>", 1)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def git_lastmod(path: Path) -> str:
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cI", "--", str(path.relative_to(ROOT))], capture_output=True, text=True, check=True).stdout.strip()
        return out[:10] if out else datetime.date.today().isoformat()
    except Exception:
        return datetime.date.today().isoformat()


def build_sitemap() -> None:
    source = ROOT / "sitemap.xml"
    content = source.read_text(encoding="utf-8")

    def add_lastmod(match: re.Match) -> str:
        loc = match.group(1)
        rel = loc.replace("https://groundworkllc.netlify.app/", "").lstrip("/")
        page = ROOT / (rel or "index.html")
        return f"<url><loc>{loc}</loc><lastmod>{git_lastmod(page)}</lastmod></url>"

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
    site_css = DIST / "site.css"
    site_css.write_text(minify_css(site_css.read_text(encoding="utf-8")) + "\n", encoding="utf-8")
    build_sitemap()
    print(f"Built {sum(1 for _ in DIST.rglob('*.html'))} HTML pages into {DIST}")


if __name__ == "__main__":
    main()
