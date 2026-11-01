#!/usr/bin/env python3
"""Build the static Groundwork site into dist/."""
from pathlib import Path
import os
import datetime
import re
import shutil
import subprocess

STYLE_RE = re.compile(r"<style(?:\s[^>]*)?>([\s\S]*?)</style>", re.IGNORECASE)
ROOT = Path(__file__).parent
DIST = ROOT / "dist"
SKIP_DIRS = {".git", "dev-archive", "__pycache__", "dist", "docs"}
COPY_FILES = {"site.css", "site.js", "sitemap.xml", "robots.txt", "favicon.ico"}
COPY_DIRS = {"fonts"}

# Print PDFs regenerated from their HTML sources on every build.
PDF_JOBS = [
    (ROOT / "docs/marketing/flyer-door-hanger.html",
     ROOT / "docs/marketing/flyer-door-hanger.pdf"),
    (ROOT / "docs/marketing/flyer-fall-cleanup.html",
     ROOT / "docs/marketing/flyer-fall-cleanup.pdf"),
    (ROOT / "docs/marketing/realtor-counter-card.html",
     ROOT / "docs/marketing/realtor-counter-card.pdf"),
    (ROOT / "docs/marketing/quote-calibration-worksheet.html",
     ROOT / "docs/marketing/quote-calibration-worksheet.pdf"),
    (ROOT / "docs/marketing/quote-calibration-worksheet-example.html",
     ROOT / "docs/marketing/quote-calibration-worksheet-example.pdf"),
]

HEADER = '''<header>
  <nav class="nav">
    <a href="/index.html" class="brand" style="text-decoration:none"><svg class="brand-mark" width="28" height="28" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><circle cx="32" cy="32" r="25" fill="#C87955"/><path d="M13 45 26 26l7 9 7-11 12 21H13Z" fill="#3B2A22"/><path d="M34 29c.8-8 5-13 12-15 .8 7.5-3.1 13-12 15Z" fill="#78836B"/><path d="M34 29c1.8-5.2 5.2-9.2 9.6-12.2" fill="none" stroke="#FFF9F0" stroke-width="2.3" stroke-linecap="round"/></svg>Groundwork <span>Landscaping</span></a>
    <ul class="nav-links">
      <!-- Seasonal: remove the Fall cleanup item after the campaign ends. -->
      <li><a href="/fall-cleanup-longmont.html" class="nav-campaign">Fall cleanup</a></li>
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
    <a href="/fall-cleanup-longmont.html" class="nav-campaign">Fall cleanup</a>
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
        <a href="/privacy.html">Privacy</a>
        <a href="/accessibility.html">Accessibility</a>
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

# Server-rendered so the phone's best conversion element survives a slow or
# blocked script. site.js only wires behaviour onto these buttons.
MOBILE_CTA = '''<div class="mobile-cta" id="mobile-cta" aria-label="Quick contact">
  <a href="tel:+17207075411">Call</a>
  <button type="button" class="mobile-cta-quote">Get a quote</button>
  <button type="button" aria-label="Hide quick contact bar">×</button>
</div>'''

ASSET_TAGS = '''<link rel="stylesheet" href="/site.css?v=earthy-v3">
<script defer src="/site.js?v=earthy-v3"></script>'''
FONT_TAGS = '''<link rel="preload" href="/fonts/fraunces-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/work-sans-var.woff2" as="font" type="font/woff2" crossorigin>'''
ICON_TAGS = '''<link rel="icon" href="/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/img/favicon-32.png" sizes="32x32" type="image/png">
<link rel="icon" href="/img/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">'''

SITE = "https://groundworkllc.netlify.app"

# Case-study pages link to their siblings, so the eleven projects form a set
# instead of eleven dead ends. Topics come from the filename: a fence page pairs
# with fence pages first, then with the nearest other work.
CASE_TOPICS = {
    "fence": ("fence", "privacy", "property-line", "cedar"),
    "drainage": ("drainage", "downspout", "channel", "grade"),
    "stone": ("flagstone", "gravel", "river-rock", "bluestone", "edging", "steps"),
    "hardscape": ("patio", "wall", "terrace", "pad", "entry"),
    "planting": ("xeriscape", "planting", "cleanup", "bed"),
}


def case_topics(path: Path) -> set[str]:
    return {tag for tag, words in CASE_TOPICS.items() if any(word in path.stem for word in words)}


def case_label(path: Path) -> str:
    """The page's own <title>, minus the site suffix."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return path.stem.replace("-", " ").title()
    match = re.search(r"<title>([^<]*)</title>", text)
    if not match:
        return path.stem.replace("-", " ").title()
    return match.group(1).split("|")[0].strip().replace("&amp;", "&")


def inject_case_related(content: str, source: Path) -> str:
    if source.parent.name != "case-studies" or "</main>" not in content:
        return content
    mine = case_topics(source)
    siblings = [path for path in sorted(source.parent.glob("*.html")) if path != source]
    ranked = sorted(siblings, key=lambda path: (-len(mine & case_topics(path)), path.name))[:3]
    if not ranked:
        return content
    blocks = "".join(
        f'<div class="service-related"><div><h3>{case_label(other)}</h3>'
        f'<p>Another finished project from the same kind of work.</p></div>'
        f'<a href="{other.name}">Open the case study →</a></div>'
        for other in ranked
    )
    return content.replace("</main>", f'<section class="service-page-section">{blocks}</section></main>', 1)


def page_url(relative: Path) -> str:
    posix = relative.as_posix()
    return SITE + ("/" if posix == "index.html" else "/" + posix)


def first_content_image(content: str) -> str:
    """The page's own first photograph — never an icon, a logo or the shared default."""
    skip = ("favicon", "logo", "apple-touch-icon", "hero-landscape")
    for match in re.finditer(r'<img[^>]+src="([^"]+)"', content, re.IGNORECASE):
        src = match.group(1)
        if src.startswith("/") and not any(word in src.lower() for word in skip):
            return src
    return ""


def inject_og_tags(content: str, relative: Path) -> str:
    """Give every page its own social card: title, description, url and a real photo.

    Only a handful of pages carried og:* tags, so most shared links showed
    nothing at all. A page with its own photograph uses it; anything else falls
    back to the site image rather than inventing one.
    """
    if "</head>" not in content:
        return content

    def current(prop: str) -> str | None:
        match = re.search(rf'<meta property="og:{prop}" content="([^"]*)"', content)
        return match.group(1) if match else None

    def put(prop: str, value: str) -> None:
        nonlocal content
        tag = f'<meta property="og:{prop}" content="{value}">'
        existing = re.search(rf'<meta property="og:{prop}" content="[^"]*">', content)
        if existing:
            content = content.replace(existing.group(0), tag, 1)
        else:
            content = content.replace("</head>", tag + "\n</head>", 1)

    title_match = re.search(r"<title>([^<]*)</title>", content)
    desc_match = re.search(r'<meta name="description" content="([^"]*)"', content)
    if not current("title") and title_match:
        put("title", title_match.group(1))
    if not current("description") and desc_match:
        put("description", desc_match.group(1))
    if not current("type"):
        put("type", "website")
    if not current("url"):
        put("url", page_url(relative))

    image = current("image")
    placeholder = {"/img/og-image.jpg", SITE + "/img/og-image.jpg"}
    if not image or image.rstrip("/") in placeholder:
        chosen = first_content_image(content) or "/img/og-image.jpg"
        put("image", chosen if chosen.startswith("http") else SITE + chosen)
    elif image.startswith("/"):
        put("image", SITE + image)
    return content


# Cloudflare Web Analytics: cookieless, aggregate page counts only.
# Set the token from the Cloudflare dashboard (Web Analytics -> Add a site -> JS install):
#   CF_ANALYTICS_TOKEN=your_token python3 build.py
# While the token is unset nothing is injected, so no third-party request is made.
# NOTE: when this goes live, privacy.html's "Cookies and analytics" section must be
# updated in the same change - it currently states no analytics platform is in use.
ANALYTICS_TOKEN = os.environ.get("CF_ANALYTICS_TOKEN", "").strip()
# Byte-for-byte the block from Cloudflare's "Install JS Snippet" panel, including
# the identifying comments, so what ships is what the dashboard shows you. The
# module script is deferred without a defer attribute. The token is public - it
# ends up in every page - so it comes from an env var, never from the repo.
ANALYTICS_TAGS = (
    "<!-- Cloudflare Web Analytics -->"
    "<script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' "
    "data-cf-beacon='{\"token\": \"" + ANALYTICS_TOKEN + "\"}'></script>"
    "<!-- End Cloudflare Web Analytics -->"
) if ANALYTICS_TOKEN else ""


# privacy.html has to describe what the build actually ships. The paragraph between
# these markers is chosen from ANALYTICS_TAGS at build time, so the beacon and the
# notice can never disagree - and the build fails if the markers ever go missing.
POLICY_START = "<!-- analytics-policy:start -->"
POLICY_END = "<!-- analytics-policy:end -->"
ANALYTICS_POLICY_OFF = """    <p>This site does not currently use advertising cookies or a third-party analytics platform. Your browser may still retain ordinary technical data required to load and operate the site.</p>"""
ANALYTICS_POLICY_ON = """    <p>We use Cloudflare Web Analytics to count page views. It sets no cookies, does not follow you across other sites, and does not build an advertising profile. It records the page you requested, the site that referred you, and general details such as browser, device type, and country &mdash; in aggregate, and only so we can tell which pages and services people look for.</p>
    <p>There are no advertising cookies or tracking pixels on this site, and we do not sell visitor data. Cloudflare processes these measurements on our behalf; see <a href="https://www.cloudflare.com/privacypolicy/">Cloudflare\u2019s privacy policy</a>. Your browser may still retain ordinary technical data required to load and operate the site.</p>"""


def apply_analytics_policy(content: str) -> str:
    pattern = re.compile(re.escape(POLICY_START) + r".*?" + re.escape(POLICY_END), re.DOTALL)
    if not pattern.search(content):
        raise RuntimeError(
            "privacy.html is missing the analytics-policy markers: refusing to ship "
            "an analytics beacon that the privacy notice does not describe."
        )
    block = ANALYTICS_POLICY_ON if ANALYTICS_TAGS else ANALYTICS_POLICY_OFF
    return pattern.sub(block, content, count=1)


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


def inject_skip_link(content: str) -> str:
    """Put a skip link first in the document and give the page a target for it."""
    main = re.search(r"<main\b([^>]*)>", content)
    if main:
        attrs = main.group(1)
    else:
        # index.html is section-per-band rather than <main>-wrapped.
        main = re.search(r"<section\b([^>]*)>", content)
        if not main:
            return content
        attrs = main.group(1)

    existing = re.search(r'\sid="([^"]+)"', attrs)
    if existing:
        target = existing.group(1)
    else:
        target = "main"
        tag_name = re.match(r"<(\w+)", main.group(0)).group(1)
        content = content.replace(main.group(0), f'<{tag_name} id="main" tabindex="-1"{attrs}>', 1)

    link = f'<a class="skip-link" href="#{target}">Skip to content</a>\n'
    content = re.sub(r"(<body\b[^>]*>)", lambda m: m.group(1) + "\n" + link, content, count=1)

    if "id=\"mobile-cta\"" not in content:
        content = content.replace("</body>", MOBILE_CTA + "\n</body>", 1)
    return content


def build_html(source: Path, target: Path) -> None:
    content = source.read_text(encoding="utf-8")
    if source.name != "thank-you.html":
        content = re.sub(r"<header(?:\s[^>]*)?>[\s\S]*?</header>", HEADER, content, count=1)
        content = re.sub(r"<footer(?:\s[^>]*)?>[\s\S]*?</footer>", FOOTER, content, count=1)
        content = re.sub(r"<link rel=\"stylesheet\" href=\"/?site\.css(?:\?[^\"]*)?\">\s*", "", content)
        content = re.sub(r"<script defer src=\"/?site\.js\"></script>\s*", "", content)
        styles = "\n\n".join(match.group(1).strip() for match in STYLE_RE.finditer(content))
        content = STYLE_RE.sub("", content)
        if styles:
            content = content.replace("</head>", f"<style>{minify_css(styles)}</style>\n</head>", 1)
        content = content.replace("</head>", ASSET_TAGS + "\n</head>", 1)
    content = transform_gallery_markup(content)
    content = re.sub(r'<link[^>]*https://fonts[.]g(?:oogleapis|static)[.]com[^>]*/?>\s*', "", content)
    content = inject_og_tags(content, source.relative_to(ROOT))
    content = inject_case_related(content, source)
    content = inject_twitter_card(content)
    content = content.replace("</head>", FONT_TAGS + "\n</head>", 1)
    content = content.replace("</head>", ICON_TAGS + "\n</head>", 1)
    if ANALYTICS_TAGS:
        content = content.replace("</head>", ANALYTICS_TAGS + "\n</head>", 1)
    content = inject_skip_link(content)
    if source.name == "privacy.html":
        content = apply_analytics_policy(content)
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


def _run_pdf_writer() -> object:
    """Return a callable(src, dst) that renders src.html to dst.pdf, or None."""
    try:
        from weasyprint import HTML
        return lambda src, dst: HTML(str(src)).write_pdf(str(dst))
    except ImportError:
        pass
    venv_python = Path("/tmp/pdfgen/bin/python")
    if venv_python.exists():
        code = "import sys; from weasyprint import HTML; HTML(sys.argv[1]).write_pdf(sys.argv[2])"
        return lambda src, dst, _p=venv_python, _c=code: subprocess.run(
            [str(_p), "-c", _c, str(src), str(dst)], check=True, capture_output=True
        )
    return None


def build_pdfs() -> None:
    """Regenerate marketing PDFs from their HTML sources; never break the site build."""
    writer = _run_pdf_writer()
    if writer is None:
        print("PDF: weasyprint not installed and no /tmp/pdfgen venv found; PDFs left untouched")
        return
    for src, dst in PDF_JOBS:
        if not src.exists():
            print(f"PDF: source {src.name} missing; left {dst.name} untouched")
            continue
        try:
            # Only re-render when the HTML is newer than the existing PDF.
            if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
                print(f"PDF: {dst.name} already up to date")
                continue
            writer(src, dst)
            print(f"PDF: regenerated {dst.name}")
        except Exception as exc:  # noqa: BLE001 - site build must not die on print output
            print(f"PDF: FAILED to regenerate {dst.name}: {exc}")


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
    build_pdfs()


if __name__ == "__main__":
    main()
