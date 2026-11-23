#!/usr/bin/env python3
"""Build the static Waxwing site into dist/."""
from pathlib import Path
import os
import datetime
import hashlib
import re
import shutil
import subprocess

STYLE_RE = re.compile(r"<style(?:\s[^>]*)?>([\s\S]*?)</style>", re.IGNORECASE)
ROOT = Path(__file__).parent
DIST = ROOT / "dist"
SKIP_DIRS = {".git", "dev-archive", "claudplan4gg", "__pycache__", "dist", "docs"}
# Originals kept in the repo but never shipped: pages reference the .webp
# twins (only og-image.jpg is referenced anywhere), so copying these to
# dist/ is ~3.3 MB of dead deploy weight.
IMG_EXCLUDE = {
    "img/case-studies/cedar-fence.jpg",
    "img/case-studies/fort-collins-retaining-wall-patio/9-final-look-planted-bed.jpg",
    "img/case-studies/cleanup-corner-after.jpg",
    "img/case-studies/river-rock-after.jpg",
    "img/case-studies/cleanup-corner-before.jpg",
    "img/case-studies/lafayette-cedar-fence/5-completed-front-cedar-fence.jpg",
}
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
    <a href="/index.html" class="brand" style="text-decoration:none"><svg class="brand-mark" width="28" height="28" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><circle cx="32" cy="32" r="26" fill="#C87955"/><g fill="#FFF9F0"><circle cx="30" cy="36" r="12"/><circle cx="44" cy="23" r="7.5"/><path d="M37 17.5 43 8l5 8Z"/><path d="M51 20.5 60 23.5l-9 3Z"/><path d="M20 41 8 50l13-4Z"/></g><circle cx="47" cy="21" r="1.4" fill="#3B2A22"/></svg>Waxwing <span>Landscaping</span></a>
    <ul class="nav-links">
      <!-- Seasonal: remove the Fall cleanup item after the campaign ends. -->
      <li><a href="/fall-cleanup-longmont.html" class="nav-campaign">Fall cleanup</a></li>
      <li><a href="/services.html">Services</a></li>
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
    <a href="/services.html">Services</a>
    <a href="/work.html">Our Work</a>
    <a href="/about.html">About Us</a>
    <a href="/blog/index.html">Blog</a>
    <a href="/fall-cleanup-longmont.html" class="nav-campaign">Fall cleanup</a>
    <a href="/contact.html" class="nav-cta">Get a quote</a>
  </div>
</header>'''

FOOTER = '''<footer class="site-footer">
  <div class="wrap">
    <div class="site-footer-grid">
      <div class="site-footer-brand">
        <a href="/index.html">Waxwing <span>Landscaping</span></a>
        <p>Hardscaping, fencing, and lawn care built for Colorado properties.</p>
      </div>
      <nav class="site-footer-links" aria-label="Footer navigation">
        <a href="/services.html">Services</a>
        <a href="/work.html">Our Work</a>
        <a href="/about.html">About Us</a>
        <a href="/blog/index.html">Blog</a>
        <a href="/privacy.html">Privacy</a>
        <a href="/accessibility.html">Accessibility</a>
      </nav>
      <div class="site-footer-contact">
        <a href="tel:+17208930394">(720) 893-0394</a>
        <a href="mailto:cmoneyq11@gmail.com">Email us</a>
        <span>Free on-site estimates</span>
        <span>Longmont &amp; Boulder County</span>
      </div>
    </div>
    <div class="site-footer-bottom">
      <span>© <span id="current-year">2026</span> Waxwing Landscaping</span>
      <a href="/contact.html">Request a quote →</a>
    </div>
  </div>
</footer>'''

# Server-rendered so the phone's best conversion element survives a slow or
# blocked script. site.js only wires behaviour onto these buttons.
MOBILE_CTA = '''<div class="mobile-cta" id="mobile-cta" aria-label="Quick contact">
  <a href="tel:+17208930394">Call</a>
  <button type="button" class="mobile-cta-quote">Get a quote</button>
  <button type="button" aria-label="Hide quick contact bar">×</button>
</div>'''

def asset_version(name: str) -> str:
    """Short content hash, so changing an asset changes its URL.

    netlify.toml marks /site.css and /site.js immutable for a year. With a
    hand-written ?v= token the URL never changes, so a fix that ships never
    reaches anyone who has already visited — the browser keeps the old script
    from disk cache. Hashing the bytes makes the URL change exactly when the
    file does, and stay identical when it does not.
    """
    try:
        return hashlib.sha256((ROOT / name).read_bytes()).hexdigest()[:8]
    except OSError:
        return "dev"


def asset_tags() -> str:
    return (
        f'<link rel="stylesheet" href="/site.css?v={asset_version("site.css")}">\n'
        f'<script defer src="/site.js?v={asset_version("site.js")}"></script>'
    )
FONT_NAMES = ("fraunces-var.woff2", "fraunces-italic-var.woff2", "work-sans-var.woff2")
FONT_TAGS = "\n".join(f'<link rel="preload" href="/fonts/{name}?v={asset_version("fonts/" + name)}" as="font" type="font/woff2" crossorigin>' for name in FONT_NAMES)
# The icon set lives under /img/*, which HEADERS_RULES serves immutable for a
# year, so these four carry the same content hash every other image URL gets.
ICON_TAGS = (
    f'<link rel="icon" href="/img/favicon.svg?v={asset_version("img/favicon.svg")}" type="image/svg+xml">\n'
    f'<link rel="icon" href="/img/favicon-32.png?v={asset_version("img/favicon-32.png")}" sizes="32x32" type="image/png">\n'
    f'<link rel="icon" href="/img/favicon-48.png?v={asset_version("img/favicon-48.png")}" sizes="48x48" type="image/png">\n'
    f'<link rel="apple-touch-icon" href="/img/apple-touch-icon.png?v={asset_version("img/apple-touch-icon.png")}">'
)

# The one place the public origin lives. Every absolute URL the build emits —
# sitemap <loc>s, og:url, twitter:image — is derived from this, so a domain
# switch is this constant plus the hand-written canonicals and JSON-LD urls in
# the page sources (docs/HANDOFF.md §4 has the ordered flip).
SITE = "https://waxwinglandscaping.com"

# The project stat is the number of case studies that actually ship, not a figure
# typed into three pages by hand: work.html announced "10 projects" for weeks after
# the eleventh shipped. An element tagged data-project-count gets the number;
# data-project-count-text gets "<n> projects".
PROJECT_COUNT = len(list((ROOT / "case-studies").glob("*.html")))

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


# Cloudflare Pages answers /page.html with a 308 to /page, and /dir/index.html
# with /dir/ - so every internal URL the build emits has to already be in the
# form Pages serves. Leaving .html in the markup puts a permanent redirect in
# front of every click and makes each canonical name a URL that redirects
# somewhere else.
PAGE_LINK_RE = re.compile(r'(\bhref=)(["\'])([^"\']+)\2')
# JSON-LD page URLs appear under more than one key: "url" on the entity,
# "item" in a breadcrumb list, "@id" when the page is its own identifier.
LD_URL_RE = re.compile(r'("(?:url|item|@id)"\s*:\s*")([^"]+)(")')
# og:url is a page URL in a meta tag, not an href, so it needs its own pass:
# existing tags are left alone by inject_og_tags() and would otherwise keep .html.
OG_URL_RE = re.compile(r'<meta[^>]*property="og:url"[^>]*>', re.IGNORECASE)
OG_CONTENT_RE = re.compile(r'(content=")([^"]*)(")')
EXTERNAL_RE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//)", re.IGNORECASE)


def page_href(url: str) -> str:
    """Rewrite one internal page URL to the extensionless form Pages serves.

    Other origins, assets, mailto:/tel: links and bare fragments come back
    untouched, as does anything that is not an .html page. Query strings and
    fragments are preserved.
    """
    if not url or url.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
        return url
    prefix, rest = "", url
    if rest.startswith(SITE + "/") or rest == SITE:
        prefix, rest = SITE, rest[len(SITE):]
    elif EXTERNAL_RE.match(rest):
        return url  # another origin is not ours to rewrite
    match = re.match(r"^([^?#]*)(.*)$", rest)
    path, tail = match.group(1), match.group(2)
    if not path.endswith(".html"):
        return url
    stem = path[: -len(".html")]
    if stem.endswith("/index"):
        stem = stem[: -len("index")]
    elif stem == "index":
        stem = "./"
    return prefix + stem + tail


def rewrite_page_urls(content: str) -> str:
    """Apply page_href() to every href, JSON-LD "url" field and og:url tag."""
    content = PAGE_LINK_RE.sub(
        lambda m: m.group(1) + m.group(2) + page_href(m.group(3)) + m.group(2), content
    )
    content = LD_URL_RE.sub(lambda m: m.group(1) + page_href(m.group(2)) + m.group(3), content)
    return OG_URL_RE.sub(
        lambda m: OG_CONTENT_RE.sub(
            lambda c: c.group(1) + page_href(c.group(2)) + c.group(3), m.group(0), count=1
        ),
        content,
    )


def page_url(relative: Path) -> str:
    posix = relative.as_posix()
    return page_href(SITE + ("/" if posix == "index.html" else "/" + posix))


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
    desc_match = re.search(r'<meta\s+(?:name="description"\s+content="([^"]*)"|content="([^"]*)"\s+name="description")', content)
    if not current("title") and title_match:
        put("title", title_match.group(1))
    if not current("description") and desc_match:
        put("description", desc_match.group(1) or desc_match.group(2))
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
#
# Two ways the beacon can reach a page, and they are not interchangeable:
#   1. Edge injection - the zone's Web Analytics / RUM setting is ON, so Cloudflare
#      appends the beacon to the HTML as it leaves the edge. Nothing in this repo
#      or in dist/ contains it, so the build cannot see it. EDGE_ANALYTICS records
#      the fact so privacy.html still describes what actually ships.
#   2. The JS snippet - CF_ANALYTICS_TOKEN is set and the tag is written into every
#      page below. Use this only if RUM is NOT enabled at the edge, or the site will
#      carry two beacons.
def _analytics_token() -> str:
    """The Web Analytics site token: env var first, then an untracked file.

    This token is not a secret in the usual sense - it is written into every page
    and readable by anyone who views source. It stays out of git so the repo is
    never the thing that silently changes what is measured. The file fallback
    exists because a deploy run without the env var used to drop the beacon while
    privacy.html went on claiming analytics was on.
    """
    env = os.environ.get("CF_ANALYTICS_TOKEN", "").strip()
    if env:
        return env
    try:
        return (ROOT / ".analytics-token").read_text(encoding="utf-8").strip()
    except OSError:
        return ""


ANALYTICS_TOKEN = _analytics_token()

# Measured 2026-11-22: RUM enabled at the zone level (Analytics -> Web Analytics)
# does NOT inject a beacon into this site. Cloudflare Pages serves the HTML, and
# injection comes from the Pages project's own Metrics -> Web Analytics toggle on
# a later deployment; ten requests across two deploys returned zero beacons. The
# site therefore ships the snippet itself from ANALYTICS_TOKEN. Leave this False
# unless injection is actually observed in a live page's source.
EDGE_ANALYTICS = False
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

# Google Analytics 4: the one thing on this site that sets a cookie.
#
# Off unless GA4_MEASUREMENT_ID is set (env var first, then an untracked .ga4-id
# file), the same pattern as the Cloudflare token. The tag ships with Google
# Signals and ad personalisation denied, which is what keeps the notice's "no
# advertising cookies" sentence true: _ga is a first-party analytics cookie, not
# an ad cookie.
#
# CONSENT STANCE (draft, 2026-11-22; not legal advice):
#   No consent banner. Under the Colorado Privacy Act the duties attach to a
#   controller handling 100k+ consumers a year, or 25k+ while selling data; a
#   two-county landscaping business is far below that, nothing here is used for
#   targeted advertising, and nothing is sold. The notice discloses the cookie and
#   offers a refusal route instead.
#   Revisit, in order of likelihood, before shipping under any of:
#     1. EEA/UK traffic becomes material - ePrivacy/PECR wants prior consent for
#        analytics cookies, and no US-default banner satisfies it.
#     2. Ads or remarketing are enabled, or audience data is shared.
#     3. The CPA thresholds above are met.
#   Each of those calls for a banner (or Consent Mode with denied defaults), not a
#   quieter sentence in the notice.
GA4_ID_RE = re.compile(r"^G-[A-Z0-9]{4,}$")


def _ga4_measurement_id() -> str:
    """The GA4 web stream ID: env var first, then an untracked file.

    Mirrors _analytics_token(). The value is public - it ships in every page - but
    keeping it out of git means a clone cannot silently start measuring.
    """
    env = os.environ.get("GA4_MEASUREMENT_ID", "").strip()
    if env:
        return env
    try:
        return (ROOT / ".ga4-id").read_text(encoding="utf-8").strip()
    except OSError:
        return ""


GA4_MEASUREMENT_ID = _ga4_measurement_id()
if GA4_MEASUREMENT_ID and not GA4_ID_RE.match(GA4_MEASUREMENT_ID):
    raise RuntimeError(
        "GA4_MEASUREMENT_ID is not a GA4 web stream ID (expected G-XXXXXXXXXX, got "
        f"{GA4_MEASUREMENT_ID[:12]!r}): refusing to ship a tag that collects nothing."
    )
# Consent defaults go in first, so they are queued before the config call below.
# ad_* denied is the honest default for a site that runs no ads and no remarketing.
GA4_TAGS = (
    "<!-- Google Analytics 4 -->"
    "<script>"
    "window.dataLayer=window.dataLayer||[];"
    "function gtag(){dataLayer.push(arguments);}"
    "gtag('consent','default',{'ad_storage':'denied','ad_user_data':'denied',"
    "'ad_personalization':'denied'});"
    "gtag('js',new Date());"
    "gtag('config','" + GA4_MEASUREMENT_ID + "',{'allow_google_signals':false,"
    "'allow_ad_personalization_signals':false});"
    "</script>"
    "<script async src='https://www.googletagmanager.com/gtag/js?id=" + GA4_MEASUREMENT_ID + "'></script>"
    "<!-- End Google Analytics 4 -->"
) if GA4_MEASUREMENT_ID else ""

# The conversion. Both quote paths - the contact form and the mobile quote sheet -
# POST to Formspree and then land on /thank-you, so one event there counts both and
# neither form needs instrumenting. generate_lead is GA4's recommended name; marking
# it as a key event is a click in the GA4 UI, not something a static build can do.
# No form contents are sent, only that a lead reached the confirmation page.
GA4_LEAD_EVENT = (
    "<script>"
    "gtag('event','generate_lead',{"
    "'lead_source':'quote_form',"
    "'page_location':location.origin+location.pathname"
    "});"
    "</script>"
) if GA4_TAGS else ""

# Anything that measures has to be described in privacy.html - either the tag this
# build emits or the beacon the edge adds behind its back.
ANALYTICS_ACTIVE = bool(ANALYTICS_TAGS) or EDGE_ANALYTICS or bool(GA4_TAGS)


# privacy.html has to describe what the build actually ships. The paragraph between
# these markers is chosen from ANALYTICS_ACTIVE at build time, so the beacon and the
# notice can never disagree - and the build fails if the markers ever go missing.
POLICY_START = "<!-- analytics-policy:start -->"
POLICY_END = "<!-- analytics-policy:end -->"
ANALYTICS_POLICY_OFF = """    <p>This site does not currently use advertising cookies or a third-party analytics platform. Your browser may still retain ordinary technical data required to load and operate the site.</p>"""
ANALYTICS_POLICY_ON = """    <p>We use Cloudflare Web Analytics to count page views. It sets no cookies, does not follow you across other sites, and does not build an advertising profile. It records the page you requested, the site that referred you, and general details such as browser, device type, and country &mdash; in aggregate, and only so we can tell which pages and services people look for.</p>
    <p>There are no advertising cookies or tracking pixels on this site, and we do not sell visitor data. Cloudflare processes these measurements on our behalf; see <a href="https://www.cloudflare.com/privacypolicy/">Cloudflare\u2019s privacy policy</a>. Your browser may still retain ordinary technical data required to load and operate the site.</p>"""


# GA4 is the only state that sets a cookie, so it cannot reuse the Cloudflare
# paragraph - that one correctly says "sets no cookies". Cloudflare gets its own
# short paragraph when it is also on, so enabling GA4 never quietly drops it.
ANALYTICS_POLICY_GA4 = """    <p>We use Google Analytics 4 to see which pages people find and read. It sets one first-party cookie, <code>_ga</code>, which tells one browser apart from another for up to two years; it does not tell us who you are. Google Signals and ad personalisation are turned off, so the measurements are not used to build an advertising profile or to target ads, and we do not sell or share them for advertising.</p>
    <p>What is recorded is mostly anonymous and always aggregate: the page you requested, the site or search that referred you, an approximate location derived from your IP address (Google truncates it before storing), device and browser type, and how long a visit lasted. Google processes these measurements on our behalf; see <a href="https://policies.google.com/privacy">Google\u2019s privacy policy</a>. You can refuse the cookie by blocking cookies for this site or installing <a href="https://tools.google.com/dlpage/gaoptout">Google\u2019s opt-out add-on</a>; the site works the same either way and a quote request never depends on it.</p>"""
ANALYTICS_POLICY_CF_ALONGSIDE = """    <p>We also use Cloudflare Web Analytics, which counts page views without setting a cookie, does not follow you across other sites, and does not build an advertising profile. Cloudflare processes those measurements on our behalf; see <a href="https://www.cloudflare.com/privacypolicy/">Cloudflare\u2019s privacy policy</a>. Your browser may still retain ordinary technical data required to load and operate the site.</p>"""


def analytics_policy_block() -> str:
    """The paragraph(s) privacy.html ships, chosen from what this build emits."""
    if not ANALYTICS_ACTIVE:
        return ANALYTICS_POLICY_OFF
    if not GA4_TAGS:
        return ANALYTICS_POLICY_ON
    block = ANALYTICS_POLICY_GA4
    if ANALYTICS_TAGS or EDGE_ANALYTICS:
        block += "\n" + ANALYTICS_POLICY_CF_ALONGSIDE
    return block


def apply_analytics_policy(content: str) -> str:
    pattern = re.compile(re.escape(POLICY_START) + r".*?" + re.escape(POLICY_END), re.DOTALL)
    if not pattern.search(content):
        raise RuntimeError(
            "privacy.html is missing the analytics-policy markers: refusing to ship "
            "an analytics beacon that the privacy notice does not describe."
        )
    block = analytics_policy_block()
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
        image = SITE + image
    tags = (f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:title" content="{title_m.group(1) if title_m else "Waxwing Landscaping"}">\n'
            f'<meta name="twitter:description" content="{desc}">\n'
            f'<meta name="twitter:image" content="{image}">')
    return content.replace("</head>", tags + "\n</head>", 1)


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


# --- intrinsic image dimensions --------------------------------------------
# Every <img> needs width/height or the browser cannot reserve space, so the
# gallery strips and case-study photo rows reflow as each file lands (the audit
# counted 142 of these across 14 pages). The numbers come from the files at
# build time, not from values typed by hand, so swapping a photo cannot leave a
# stale size behind. site.css pairs this with `:where(img[width][height]){
# height:auto}` so the intrinsic ratio is kept without out-ranking the rules
# that crop a photo on purpose.
IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
IMG_SRC_RE = re.compile(r'\ssrc="([^"]+)"')
IMG_DIM_RE = re.compile(r"\s(?:width|height)=\"[\d.]*\"")
# Pages repeat the same photographs, so each file is read once per build.
_IMAGE_SIZE_CACHE: dict[str, tuple[int, int] | None] = {}


def image_size(path: Path) -> tuple[int, int] | None:
    """Intrinsic pixel size of a WebP/JPEG/PNG/SVG, read from its header only."""
    try:
        data = path.read_bytes()
    except OSError:
        return None

    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        chunk = data[12:16]
        if chunk == b"VP8X":
            return (int.from_bytes(data[24:27], "little") + 1,
                    int.from_bytes(data[27:30], "little") + 1)
        if chunk == b"VP8L":
            bits = int.from_bytes(data[21:25], "little")
            return ((bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1)
        if chunk == b"VP8 ":
            start = data.find(b"\x9d\x01\x2a", 20)
            if start < 0:
                return None
            return (int.from_bytes(data[start + 3:start + 5], "little") & 0x3FFF,
                    int.from_bytes(data[start + 5:start + 7], "little") & 0x3FFF)
        return None

    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                          0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                return (int.from_bytes(data[i + 7:i + 9], "big"),
                        int.from_bytes(data[i + 5:i + 7], "big"))
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            i += 2 + int.from_bytes(data[i + 2:i + 4], "big")
        return None

    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return (int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big"))

    if b"<svg" in data[:400]:
        text = data[:1000].decode("utf-8", "ignore")
        width = re.search(r'\bwidth="(\d+)', text)
        height = re.search(r'\bheight="(\d+)', text)
        if width and height:
            return (int(width.group(1)), int(height.group(1)))
        box = re.search(r'viewBox="([^"]+)"', text)
        if box:
            parts = [p for p in re.split(r"[\s,]+", box.group(1).strip()) if p]
            if len(parts) == 4:
                return (round(float(parts[2])), round(float(parts[3])))
    return None


def inject_img_dimensions(content: str, source: Path) -> str:
    """Set width/height on every image tag from the file the tag points at.

    Existing values are replaced when they disagree with the file: twenty-eight
    tags in the source declared an aspect ratio their photograph never had
    (blog images said 1200x800 while the file is 1376x768), which reserves the
    wrong box and shifts the page as the photo lands. A tag whose src cannot be
    resolved - the lightbox placeholder with src="" - is left exactly as it is,
    because there is no file to measure.
    """
    def patch(match: re.Match) -> str:
        tag = match.group(0)
        src = IMG_SRC_RE.search(tag)
        if not src or not src.group(1).strip() or src.group(1).startswith(("http", "//", "data:")):
            return tag
        raw = src.group(1).split("?")[0]
        # Site-root references (/img/...) resolve against ROOT; everything else
        # is relative to the page that names it.
        target = ((ROOT / raw.lstrip("/")) if raw.startswith("/") else (source.parent / raw)).resolve()
        key = str(target)
        if key not in _IMAGE_SIZE_CACHE:
            _IMAGE_SIZE_CACHE[key] = image_size(target) if target.is_file() else None
        size = _IMAGE_SIZE_CACHE[key]
        if not size or not all(size):
            return tag
        tag = IMG_DIM_RE.sub("", tag).rstrip()
        return tag[:-1].rstrip().removesuffix("/") + f' width="{size[0]}" height="{size[1]}">'

    return IMG_TAG_RE.sub(patch, content)


# --- versioned image URLs ---------------------------------------------------
# /img/* is served `immutable, max-age=31536000` by HEADERS_RULES below, and the
# comment there says that is only safe because asset URLs carry a content hash.
# That was true of site.css, site.js and the fonts and false of every photograph,
# so a recompressed file kept its old bytes alive in a returning visitor's cache
# for a year behind an unchanged URL. Hashing the bytes a tag actually points at
# makes the URL change exactly when the file does, and stay identical when it
# does not - the same invariant, finally enforced for images.
_IMAGE_HASH_CACHE: dict[str, str] = {}
IMG_OR_SOURCE_TAG_RE = re.compile(r"<(?:img|source)\b[^>]*>", re.IGNORECASE)
# Longest alternative first: `srcset` contains the word `src`.
IMG_URL_ATTR_RE = re.compile(r'\b(srcset|src)="([^"]*)"')
# The gallery and lightbox URLs are not on <img> at all - site.js copies them
# into img.src from the <button> that carries them, so they are matched across
# the whole document rather than inside an image tag.
GALLERY_URL_ATTR_RE = re.compile(r'\b(data-gallery-src|data-lightbox-src)="([^"]*)"')
CSS_IMG_URL_RE = re.compile(r"url\(\s*(['\"]?)([^)'\"]+)\1\s*\)")


def image_version(raw: str, source: Path) -> str:
    """Content hash for a site-local image reference, or "" when there is none.

    data: URIs, remote URLs and the lightbox's empty src have no bytes in the
    repo to hash. Root-absolute references (/img/...) resolve against ROOT and
    everything else against the page that names it - the same rule
    inject_img_dimensions uses, so a tag's URL and its width/height always
    describe one file.
    """
    path_only = raw.split("#", 1)[0].split("?", 1)[0].strip()
    if not path_only or path_only.startswith(("data:", "http:", "https:", "//", "blob:")):
        return ""
    target = ((ROOT / path_only.lstrip("/")) if path_only.startswith("/") else (source.parent / path_only)).resolve()
    key = str(target)
    if key not in _IMAGE_HASH_CACHE:
        try:
            _IMAGE_HASH_CACHE[key] = hashlib.sha256(target.read_bytes()).hexdigest()[:8] if target.is_file() else ""
        except OSError:
            _IMAGE_HASH_CACHE[key] = ""
    return _IMAGE_HASH_CACHE[key]


def versioned_image_url(raw: str, source: Path) -> str:
    version = image_version(raw, source)
    if not version:
        return raw
    return f"{raw}{'&' if '?' in raw else '?'}v={version}"


def versioned_srcset(value: str, source: Path) -> str:
    """Version every candidate, keeping its width or density descriptor."""
    out = []
    for candidate in value.split(","):
        parts = candidate.strip().split()
        if parts:
            parts[0] = versioned_image_url(parts[0], source)
        out.append(" ".join(parts))
    return ", ".join(out)


def version_image_urls(content: str, source: Path) -> str:
    """Give every image reference the ?v= its file's bytes dictate.

    Covers src, srcset candidates, the two data-* attributes site.js copies into
    img.src for the gallery and lightbox, and the photographs still referenced
    from inlined page CSS. og:image, twitter:image and JSON-LD image are left
    unversioned on purpose: they are absolute URLs only a crawler fetches, and a
    stable address is worth more there than a cache refresh.
    """
    def patch_tag(match: re.Match) -> str:
        def patch_attr(attr_match: re.Match) -> str:
            attr, value = attr_match.group(1), attr_match.group(2)
            value = versioned_srcset(value, source) if attr == "srcset" else versioned_image_url(value, source)
            return f'{attr}="{value}"'

        return IMG_URL_ATTR_RE.sub(patch_attr, match.group(0))

    content = IMG_OR_SOURCE_TAG_RE.sub(patch_tag, content)

    def patch_gallery(attr_match: re.Match) -> str:
        attr, value = attr_match.group(1), attr_match.group(2)
        return f'{attr}="{versioned_image_url(value, source)}"'

    content = GALLERY_URL_ATTR_RE.sub(patch_gallery, content)

    def patch_css(match: re.Match) -> str:
        quote, value = match.group(1), match.group(2)
        # Fonts are reached through site.css, which is itself versioned; only
        # photographs need the hash here.
        if "/img/" not in value:
            return match.group(0)
        return f"url({quote}{versioned_image_url(value, source)}{quote})"

    return CSS_IMG_URL_RE.sub(patch_css, content)


# index.html chooses its hero photograph in JavaScript and composes the URL at
# runtime (`base + '-800' + '.webp'`), so no attribute exists for the patcher
# above to version - and those three photos were recompressed too, which left
# the most-seen hero on the site pinned to last year's bytes. The page asks the
# build for a hash map instead; it is emitted as the first script in the page so
# the preload script that follows can use it.
SCRIPT_BLOCK_RE = re.compile(r"<script\b([^>]*)>(.*?)</script>", re.S | re.IGNORECASE)
IMG_LITERAL_RE = re.compile(r"['\"](/img/[A-Za-z0-9._/-]+)['\"]")
SCRIPT_IMG_VARIANTS = ("", "-800", "-400", "-250")
IMAGE_EXTS = (".webp", ".jpg", ".jpeg", ".png", ".avif", ".svg")


def inject_script_image_versions(content: str) -> str:
    """Emit window.__imgV for image paths a page script builds itself."""
    literal = re.search(r"<(?:script\b)", content)
    paths: dict[str, str] = {}
    for block in SCRIPT_BLOCK_RE.finditer(content):
        if "ld+json" in block.group(1).lower():
            continue  # crawler-facing, deliberately unversioned
        for match in IMG_LITERAL_RE.finditer(block.group(2)):
            base = match.group(1)
            has_ext = base.rsplit("/", 1)[-1].endswith(IMAGE_EXTS)
            candidates = [base] if has_ext else [base + suffix + ".webp" for suffix in SCRIPT_IMG_VARIANTS]
            for candidate in candidates:
                target = (ROOT / candidate.lstrip("/"))
                if not target.is_file():
                    continue
                version = image_version(candidate, ROOT / "index.html")
                if version:
                    paths[candidate] = version
    if not paths:
        return content
    body = ",".join(f'"{path}":"{version}"' for path, version in paths.items())
    tag = f'<script>window.__imgV={{{body}}};</script>\n'
    if not literal:
        return content
    return content[:literal.start()] + tag + content[literal.start():]


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


def apply_project_count(content: str) -> str:
    """Set the shipped-project stat from the case-studies folder.

    The lookahead keeps data-project-count-text from matching the plain attribute.
    """
    content = re.sub(
        r"(<[a-z]+\b[^>]*\bdata-project-count-text\b[^>]*>)[^<]*(</)",
        lambda m: f"{m.group(1)}{PROJECT_COUNT} projects{m.group(2)}",
        content,
    )
    return re.sub(
        r"(<[a-z]+\b[^>]*\bdata-project-count\b(?!-)[^>]*>)[^<]*(</)",
        lambda m: f"{m.group(1)}{PROJECT_COUNT}{m.group(2)}",
        content,
    )


def build_html(source: Path, target: Path) -> None:
    content = source.read_text(encoding="utf-8")
    content = apply_project_count(content)
    if source.name != "thank-you.html":
        content = re.sub(r"<header(?:\s[^>]*)?>[\s\S]*?</header>", HEADER, content, count=1)
        content = re.sub(r"<footer(?:\s[^>]*)?>[\s\S]*?</footer>", FOOTER, content, count=1)
        styles = "\n\n".join(match.group(1).strip() for match in STYLE_RE.finditer(content))
        content = STYLE_RE.sub("", content)
        if styles:
            content = content.replace("</head>", f"<style>{minify_css(styles)}</style>\n</head>", 1)
    # Versioned asset URLs on every page, thank-you.html included: netlify.toml
    # caches /site.css and /site.js immutable for a year, so an unversioned
    # reference would pin returning visitors to a stale script or stylesheet.
    content = re.sub(r"<link rel=\"stylesheet\" href=\"/?site\.css(?:\?[^\"]*)?\">\s*", "", content)
    content = re.sub(r"<script defer src=\"/?site\.js\"></script>\s*", "", content)
    content = content.replace("</head>", asset_tags() + "\n</head>", 1)
    content = transform_gallery_markup(content)
    content = inject_img_dimensions(content, source)
    content = re.sub(r'<link[^>]*https://fonts[.]g(?:oogleapis|static)[.]com[^>]*/?>\s*', "", content)
    content = inject_og_tags(content, source.relative_to(ROOT))
    content = inject_case_related(content, source)
    content = inject_twitter_card(content)
    content = content.replace("</head>", FONT_TAGS + "\n</head>", 1)
    content = content.replace("</head>", ICON_TAGS + "\n</head>", 1)
    if ANALYTICS_TAGS:
        content = content.replace("</head>", ANALYTICS_TAGS + "\n</head>", 1)
    if GA4_TAGS:
        content = content.replace("</head>", GA4_TAGS + "\n</head>", 1)
    if GA4_LEAD_EVENT and source.name == "thank-you.html":
        content = content.replace("</body>", GA4_LEAD_EVENT + "\n</body>", 1)
    content = inject_skip_link(content)
    if source.name == "privacy.html":
        content = apply_analytics_policy(content)
    content = rewrite_page_urls(content)
    # Last, so the og:image and JSON-LD decisions above still see the clean path
    # and only the URLs a browser actually fetches carry the hash.
    content = version_image_urls(content, source)
    content = inject_script_image_versions(content)
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
        # The host written in sitemap.xml is ignored: every <loc> is re-rooted on
        # SITE, so a domain switch never has to edit 35 source URLs and the two
        # cannot drift apart.
        rel = re.sub(r"^https?://[^/]+/", "", match.group(1))
        page = ROOT / (rel or "index.html")
        loc = page_href(f"{SITE}/{rel}")
        return f"<url><loc>{loc}</loc><lastmod>{git_lastmod(page)}</lastmod></url>"

    content = re.sub(r"<url><loc>([^<]+)</loc></url>", add_lastmod, content)
    (DIST / "sitemap.xml").write_text(content, encoding="utf-8")


# Cloudflare Pages reads `_headers` from the publish directory, and Netlify reads
# the same filename, so both hosts get identical rules from this one table instead
# of a second hand-maintained copy of the netlify.toml blocks. `immutable` is only
# safe because the asset URLs carry a content hash (?v=<sha256[:8]>) that changes
# when the file does - the same invariant site.css/site.js already rely on.
HEADERS_RULES = [
    ("/*.html", {"Cache-Control": "public, max-age=0, must-revalidate"}),
    ("/img/*", {"Cache-Control": "public, max-age=31536000, immutable"}),
    ("/site.css", {"Cache-Control": "public, max-age=31536000, immutable"}),
    ("/site.js", {"Cache-Control": "public, max-age=31536000, immutable"}),
    ("/fonts/*", {"Cache-Control": "public, max-age=31536000, immutable"}),
    ("/*", {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    }),
]


def build_headers() -> None:
    """Write dist/_headers so a host that reads it applies the netlify.toml rules.

    No `_redirects` is generated on purpose. The only redirect this site has is
    the old netlify.app host -> waxwinglandscaping.com 301, and Cloudflare Pages
    does not support domain-level redirects, so that rule has to keep running on
    the Netlify site rather than move here.
    """
    lines = [
        "# Generated by build.py - edit build.py, not dist/_headers.",
        "# Mirrors the [[headers]] blocks in netlify.toml so both hosts agree.",
        "",
    ]
    for path, rules in HEADERS_RULES:
        lines.append(path)
        for name, value in rules.items():
            lines.append(f"  {name}: {value}")
        lines.append("")
    (DIST / "_headers").write_text("\n".join(lines), encoding="utf-8")


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
        elif path.name in COPY_FILES or (relative.parts[0] in COPY_DIRS | {"img"} and relative.as_posix() not in IMG_EXCLUDE and not relative.as_posix().startswith("img/photos-to-sort/")):
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    site_css = DIST / "site.css"
    # netlify.toml (and the generated _headers) serve /fonts/* immutable, so the @font-face URLs get the same
    # content hash the preloads carry -- an unversioned immutable font would
    # never reach a visitor who already had it cached.
    site_css.write_text(re.sub(r"/fonts/([\w.-]+\.woff2)", lambda m: f"/fonts/{m.group(1)}?v={asset_version('fonts/' + m.group(1))}", minify_css(site_css.read_text(encoding="utf-8"))) + "\n", encoding="utf-8")
    build_sitemap()
    build_headers()
    print(f"Built {sum(1 for _ in DIST.rglob('*.html'))} HTML pages into {DIST}")
    build_pdfs()


if __name__ == "__main__":
    main()
