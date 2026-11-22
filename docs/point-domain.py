#!/usr/bin/env python3
"""Point waxwinglandscaping.com at the Netlify site (site `groundworkllc`).

Three modes:

  --plan   (default) Print the exact API calls and DNS records. No network, no tokens.
  --apply  Do it: add the custom domain in Netlify, then create the two Cloudflare
           records. Idempotent: re-running updates rather than duplicating.
  --check  Public verification only (DNS + HTTPS). No tokens, safe to run any time.

Tokens are read from the secret store, never from argv or the environment, so
neither value can land in shell history:

  secretctl get netlify      -> ~/.secrets/netlify.key      (Netlify PAT)
  secretctl get cloudflare   -> ~/.secrets/cloudflare.key   (Zone.DNS:Edit token)

Why these exact records (Netlify "external DNS", standard network):

  apex  A      75.2.60.5                        one A record, exactly one
  www   CNAME  groundworkllc.netlify.app

Cloudflare also supports CNAME flattening at the apex, which Netlify would prefer,
but its own SSL troubleshooting doc checks for the A record -> 75.2.60.5, so the A
record keeps this setup diagnosable against the documentation.

TWO CONSTRAINTS THAT WILL BREAK HTTPS IF IGNORED:

  1. Proxy must be OFF (grey cloud, `proxied: false`) on both records. An orange
     cloud puts Cloudflare in front of Netlify, and Netlify then cannot complete
     its Let's Encrypt HTTP-01 challenge for the domain.
  2. There must be no AAAA record on the apex. Netlify's load balancer has no
     IPv6; IPv6 for a Netlify site requires Netlify DNS. The zone is empty today,
     so this is a guard, not a fix.

The apex is the Netlify *primary* domain on purpose: every canonical on the site
points at https://waxwinglandscaping.com (build.py's SITE constant), so if Netlify
redirected the apex to www, the canonicals would all 301 somewhere else.
"""

from __future__ import annotations

import json
import subprocess
import sys
import urllib.error
import urllib.request

SITE_ID = "38200c77-154d-4ee6-a062-578b904cec1a"
SITE_SLUG = "groundworkllc"
DOMAIN = "waxwinglandscaping.com"
WWW = "www." + DOMAIN
NETLIFY_SUBDOMAIN = SITE_SLUG + ".netlify.app"
APEX_IP = "75.2.60.5"
NETLIFY_API = "https://api.netlify.com/api/v1"
CF_API = "https://api.cloudflare.com/client/v4"
UA = "waxwing-domain-runner/1.0"


# ---------------------------------------------------------------- secret store

def secret(name: str) -> str | None:
    """Read a key through secretctl. Returns None when it is not there."""
    try:
        out = subprocess.run(
            ["secretctl", "get", name], capture_output=True, text=True, timeout=15
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    value = out.stdout.strip()
    return value if out.returncode == 0 and value else None


# ----------------------------------------------------------------------- http

def call(method: str, url: str, token: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:400]
        raise SystemExit(f"{method} {url} -> HTTP {exc.code}\n{detail}") from None
    except urllib.error.URLError as exc:
        raise SystemExit(f"{method} {url} -> {exc.reason}") from None


# --------------------------------------------------------------------- netlify

def netlify_apply(token: str) -> None:
    site_url = f"{NETLIFY_API}/sites/{SITE_ID}"
    site = call("GET", site_url, token)

    current = site.get("custom_domain") or ""
    aliases = list(site.get("domain_aliases") or [])
    print(f"  before: custom_domain={current!r} aliases={aliases!r}")

    if DOMAIN not in aliases and current != DOMAIN:
        aliases.append(DOMAIN)
    if WWW not in aliases and current != WWW:
        aliases.append(WWW)

    # The apex must be the primary domain so the site's own canonicals (all
    # https://waxwinglandscaping.com) are the URLs Netlify serves, not redirects.
    patch = {"custom_domain": DOMAIN, "domain_aliases": aliases}
    after = call("PATCH", site_url, token, patch)
    print(f"  after:  custom_domain={after.get('custom_domain')!r} "
          f"aliases={after.get('domain_aliases')!r}")
    if after.get("custom_domain") != DOMAIN:
        raise SystemExit("  ! Netlify did not accept the apex as primary domain")


# ------------------------------------------------------------------ cloudflare

def cf_zone(token: str) -> str:
    res = call("GET", f"{CF_API}/zones?name={DOMAIN}", token)
    zones = res.get("result") or []
    if not zones:
        raise SystemExit(f"  ! zone {DOMAIN} is not in this Cloudflare account")
    return zones[0]["id"]


def cf_records(token: str, zone: str) -> list[dict]:
    res = call("GET", f"{CF_API}/zones/{zone}/dns_records?per_page=100", token)
    return res.get("result") or []


def cloudflare_apply(token: str) -> None:
    zone = cf_zone(token)
    existing = cf_records(token, zone)
    print(f"  zone {zone} has {len(existing)} record(s): "
          f"{[(r['type'], r['name']) for r in existing] or 'none'}")

    stale_aaaa = [r for r in existing
                  if r["type"] == "AAAA" and r["name"] in (DOMAIN, WWW)]
    for rec in stale_aaaa:
        call("DELETE", f"{CF_API}/zones/{zone}/dns_records/{rec['id']}", token)
        print(f"  deleted AAAA {rec['name']} (Netlify has no IPv6 on this network)")

    wanted = [
        {"type": "A", "name": DOMAIN, "content": APEX_IP,
         "ttl": 1, "proxied": False, "comment": "Netlify load balancer"},
        {"type": "CNAME", "name": WWW, "content": NETLIFY_SUBDOMAIN,
         "ttl": 1, "proxied": False, "comment": "Netlify site"},
    ]

    for want in wanted:
        same_name = [r for r in existing if r["name"] == want["name"]]
        keep = next((r for r in same_name if r["type"] == want["type"]), None)
        for other in same_name:
            if other is not keep and other["type"] != want["type"]:
                call("DELETE", f"{CF_API}/zones/{zone}/dns_records/{other['id']}", token)
                print(f"  deleted conflicting {other['type']} {other['name']}")

        if keep is None:
            call("POST", f"{CF_API}/zones/{zone}/dns_records", token, want)
            print(f"  created {want['type']:5} {want['name']:28} -> {want['content']}")
        else:
            want_id = dict(want, id=keep["id"])
            call("PUT", f"{CF_API}/zones/{zone}/dns_records/{keep['id']}", token, want_id)
            print(f"  updated {want['type']:5} {want['name']:28} -> {want['content']}")

    for rec in cf_records(token, zone):
        flag = "PROXIED - must be grey cloud!" if rec.get("proxied") else "dns-only"
        print(f"  verify: {rec['type']:5} {rec['name']:28} {rec['content']:28} {flag}")


# ------------------------------------------------------- public verification

def dig(*args: str) -> str:
    try:
        out = subprocess.run(["dig", "+short", *args, "@1.1.1.1"],
                             capture_output=True, text=True, timeout=20)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    return " ".join(out.stdout.split())


def check() -> int:
    print("Public verification (no credentials used)\n")
    a = dig("A", DOMAIN)
    cname = dig("CNAME", WWW)
    aaaa = dig("AAAA", DOMAIN)

    print(f"  apex A     {a or '(none)'}        {'OK' if APEX_IP in a.split() else 'not pointed'}")
    print(f"  www CNAME  {cname or '(none)'}    "
          f"{'OK' if NETLIFY_SUBDOMAIN in cname else 'not pointed'}")
    print(f"  apex AAAA  {aaaa or '(none)'}        "
          f"{'OK' if not aaaa else 'REMOVE - breaks Netlify HTTPS'}")

    if not a and not cname:
        print("\n  Nothing resolves yet: the zone is empty, so no request can reach Netlify.")
        return 1

    print("\n  HTTPS:")
    failures = 0
    for url, want in ((f"https://{DOMAIN}/work.html", 200),
                      (f"https://{NETLIFY_SUBDOMAIN}/work.html", 301)):
        try:
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", UA)
            with urllib.request.urlopen(req, timeout=25) as resp:
                code, loc = resp.status, resp.headers.get("Location") or ""
        except urllib.error.HTTPError as exc:
            code, loc = exc.code, exc.headers.get("Location") or ""
        except Exception as exc:  # DNS, TLS, timeout
            print(f"    {url:48} -> {exc}")
            failures += 1
            continue
        ok = code == want
        failures += 0 if ok else 1
        print(f"    {url:48} -> {code} {'OK' if ok else f'expected {want}'}"
              + (f" -> {loc}" if loc else ""))

    return 1 if failures else 0


# ----------------------------------------------------------------------- main

def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--plan"
    if mode not in {"--plan", "--apply", "--check"}:
        raise SystemExit(__doc__)

    if mode == "--check":
        return check()

    if mode == "--plan":
        print(f"Plan: {DOMAIN} -> Netlify site {SITE_SLUG} ({SITE_ID})\n")
        print("1. Netlify: PATCH /sites/{id}")
        print(f'     {{"custom_domain": "{DOMAIN}", "domain_aliases": ["{WWW}"]}}\n')
        print("2. Cloudflare DNS (proxy OFF on both):")
        print(f"     A      {DOMAIN:28} -> {APEX_IP}")
        print(f"     CNAME  {WWW:28} -> {NETLIFY_SUBDOMAIN}")
        print("     no AAAA on the apex\n")
        print("3. Verify: python3 docs/point-domain.py --check")
        return 0

    netlify_token = secret("netlify")
    cf_token = secret("cloudflare")
    if not netlify_token:
        raise SystemExit(
            "No Netlify token. Save one to ~/.secrets/netlify.key first:\n"
            "  secretctl add netlify --stdin < /path/to/token-file\n"
            "(Netlify -> User settings -> Applications -> Personal access tokens)"
        )
    if not cf_token:
        raise SystemExit(
            "No Cloudflare token. Save one to ~/.secrets/cloudflare.key first:\n"
            "  secretctl add cloudflare --stdin < /path/to/token-file\n"
            "(Cloudflare -> My Profile -> API Tokens -> Create: Zone.DNS:Edit, "
            f"zone {DOMAIN})"
        )

    print("Netlify: add the custom domain")
    netlify_apply(netlify_token)
    print("\nCloudflare: create the records")
    cloudflare_apply(cf_token)
    print("\nDone. Certificate issuance takes a few minutes; then run:")
    print("  python3 docs/point-domain.py --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
