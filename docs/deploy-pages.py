#!/usr/bin/env python3
"""Publish the built site to Cloudflare Pages and attach the domain.

  --plan    Print what would happen. No network, no token.
  --apply   Create the Pages project if needed, upload dist/, attach the domain.
  --check   Public verification only (DNS + HTTPS). No token, safe any time.

Token: `secretctl get cloudflare` -> ~/.secrets/cloudflare.key
Needs permissions: Account -> Cloudflare Pages: Edit, Zone -> DNS: Edit, and
Zone -> Zone: Read (only used to discover the account id from the zone).

Two deliberate choices:

1. **Direct upload, not a git-connected build.** The repo never got a GitHub App
   installation for Netlify, and linking Pages to the repo needs the same OAuth
   hand-off that no API can perform. So the build runs here - where `build.py`
   is already verified - and only `dist/` is uploaded. Add a GitHub Action later
   if push-to-deploy matters.

2. **The apex is the custom domain.** Every canonical on the site is
   https://waxwinglandscaping.com, so the apex has to be what Pages serves rather
   than a redirect target. Because the zone is already on Cloudflare in the same
   account, Pages creates the record itself (CNAME flattening, proxied) and issues
   the certificate - no A record, no grey cloud, no DNS challenge to satisfy.

The token is passed to wrangler in the child process environment, never in argv,
so it cannot land in shell history or a process listing.

A token that cannot reach Pages is not the same as a missing token: an
account-scoped token without `Cloudflare Pages: Edit` is accepted by `/accounts`
and `/zones` and still refused by `/accounts/{id}/pages/projects`. So the
capability is proved before the upload, and when it is missing the deploy falls
back to the wrangler OAuth session (`wrangler login`) rather than stopping. Both
paths upload the same `dist/`; only the project-create and domain-attach steps
need the API, so those are skipped with a note in OAuth mode.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
PROJECT = "waxwing"
DOMAIN = "waxwinglandscaping.com"
WWW = "www." + DOMAIN
API = "https://api.cloudflare.com/client/v4"
UA = "waxwing-pages-deploy/1.0"
# Pages appends a suffix when the bare project name is already taken, so the
# preview host is not derivable from PROJECT: it is waxwing-dc3, not waxwing.
PAGES_HOST = "waxwing-dc3.pages.dev"


def secret(name: str) -> str | None:
    try:
        out = subprocess.run(
            ["secretctl", "get", name], capture_output=True, text=True, timeout=15
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    value = out.stdout.strip()
    return value if out.returncode == 0 and value else None


def api(method: str, path: str, token: str, body: dict | None = None) -> dict:
    """Call the Cloudflare API. Returns the parsed envelope, success or not."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode(errors="replace")
        try:
            return json.loads(raw)
        except ValueError:
            return {"success": False, "errors": [{"message": f"HTTP {exc.code}: {raw[:200]}"}]}
    except urllib.error.URLError as exc:
        return {"success": False, "errors": [{"message": str(exc.reason)}]}


def errors(res: dict) -> str:
    return "; ".join(e.get("message", "?") for e in res.get("errors") or []) or "unknown error"


def pages_access(acct: str, token: str) -> bool:
    """Prove the token can see Pages before handing it to wrangler."""
    return bool(api("GET", f"/accounts/{acct}/pages/projects", token).get("success"))


def oauth_session() -> bool:
    """True when wrangler holds an OAuth session that can reach Pages."""
    try:
        out = subprocess.run(
            ["npx", "--yes", "wrangler", "whoami"],
            capture_output=True, text=True, timeout=300,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False
    return out.returncode == 0


def account_id(token: str) -> str:
    """Discover the account id. The zone carries it, so Zone:Read is enough."""
    res = api("GET", f"/zones?name={DOMAIN}", token)
    zones = res.get("result") or []
    if zones:
        return zones[0]["account"]["id"]
    res = api("GET", "/accounts", token)
    accounts = res.get("result") or []
    if accounts:
        return accounts[0]["id"]
    raise SystemExit(f"  ! cannot find the account id: {errors(res)}")


def ensure_project(acct: str, token: str) -> None:
    res = api("GET", f"/accounts/{acct}/pages/projects/{PROJECT}", token)
    if res.get("success"):
        print(f"  project {PROJECT} already exists")
        return
    res = api("POST", f"/accounts/{acct}/pages/projects", token,
              {"name": PROJECT, "production_branch": "main"})
    if not res.get("success"):
        raise SystemExit(f"  ! could not create project {PROJECT}: {errors(res)}")
    print(f"  created project {PROJECT} -> {res['result'].get('subdomain')}")


def upload(acct: str | None, token: str | None) -> None:
    if not DIST.is_dir():
        raise SystemExit("  ! dist/ is missing - run `python3 build.py` first")
    if not (DIST / "_headers").exists():
        raise SystemExit(
            "  ! dist/_headers is missing - the build predates build_headers(); "
            "re-run `python3 build.py` or the cache rules will not ship"
        )
    files = sum(1 for p in DIST.rglob("*") if p.is_file())
    print(f"  uploading {files} files via wrangler"
          f" ({'API token' if token else 'OAuth session'})")
    # In OAuth mode the two variables must be absent, not empty: wrangler prefers
    # an env token over its session, so leaving them set reproduces the very
    # failure this fallback exists to survive.
    env = {k: v for k, v in os.environ.items()
           if k not in {"CLOUDFLARE_API_TOKEN", "CLOUDFLARE_ACCOUNT_ID"}}
    env["CI"] = "1"
    if token:
        env["CLOUDFLARE_API_TOKEN"] = token
        env["CLOUDFLARE_ACCOUNT_ID"] = acct
    proc = subprocess.run(
        ["npx", "--yes", "wrangler", "pages", "deploy", str(DIST),
         "--project-name", PROJECT, "--branch", "main", "--commit-dirty=true"],
        cwd=ROOT, env=env, capture_output=True, text=True,
    )
    tail = (proc.stdout + proc.stderr).strip().splitlines()[-12:]
    print("\n".join("    " + line for line in tail))
    if proc.returncode != 0:
        raise SystemExit(f"  ! wrangler exited {proc.returncode}")


def attach_domain(acct: str, token: str, name: str) -> None:
    res = api("POST", f"/accounts/{acct}/pages/projects/{PROJECT}/domains", token, {"name": name})
    if res.get("success"):
        print(f"  attached {name}")
    elif "already" in errors(res).lower():
        print(f"  {name} already attached")
    else:
        raise SystemExit(f"  ! could not attach {name}: {errors(res)}")


def check() -> int:
    print("Public verification (no credentials used)\n")
    failures = 0

    def dig(*args: str) -> str:
        try:
            out = subprocess.run(["dig", "+short", *args, "@1.1.1.1"],
                                 capture_output=True, text=True, timeout=20)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return ""
        return " ".join(out.stdout.split())

    for label, args in (("apex A", ("A", DOMAIN)), ("www", ("A", WWW)),
                        ("apex NS", ("NS", DOMAIN))):
        value = dig(*args)
        print(f"  {label:8} {value or '(none)'}")
        if not value:
            failures += 1

    print("\n  HTTPS:")
    for url in (f"https://{DOMAIN}/work.html", f"https://{PAGES_HOST}/work.html",
                f"https://{WWW}/work.html"):
        try:
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", UA)
            with urllib.request.urlopen(req, timeout=25) as resp:
                code, loc = resp.status, resp.headers.get("Location") or ""
        except urllib.error.HTTPError as exc:
            code, loc = exc.code, exc.headers.get("Location") or ""
        except Exception as exc:
            print(f"    {url:46} -> {exc}")
            failures += 1
            continue
        ok = code == 200
        failures += 0 if ok else 1
        print(f"    {url:46} -> {code}{' OK' if ok else '  expected 200'}"
              + (f" -> {loc}" if loc else ""))

    print(f"\n  {'PASS' if not failures else f'{failures} check(s) not passing yet'}")
    return 1 if failures else 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--plan"
    if mode not in {"--plan", "--apply", "--check"}:
        raise SystemExit(__doc__)

    if mode == "--check":
        return check()

    if mode == "--plan":
        print(f"Plan: publish dist/ to Cloudflare Pages project '{PROJECT}'\n")
        print(f"1. GET  /accounts/{{id}}/pages/projects/{PROJECT}   (create if absent)")
        print(f"2. npx wrangler pages deploy dist --project-name {PROJECT} --branch main")
        print(f"3. POST /accounts/{{id}}/pages/projects/{PROJECT}/domains  {{\"name\": \"{DOMAIN}\"}}")
        print(f"4. same for {WWW}")
        print("   Cloudflare then creates the proxied CNAME itself and issues the cert.\n")
        print("5. Verify: python3 docs/deploy-pages.py --check")
        print("\nSteps 1, 3 and 4 need an API token with Cloudflare Pages: Edit. Without")
        print("one, --apply uploads via the wrangler OAuth session and skips them.")
        return 0

    token = secret("cloudflare")
    acct = ""
    if token:
        try:
            acct = account_id(token)
        except SystemExit:
            acct = ""
        if acct and pages_access(acct, token):
            print(f"Account {acct}")
            print("\nProject")
            ensure_project(acct, token)
            print("\nUpload")
            upload(acct, token)
            print("\nDomain")
            attach_domain(acct, token, DOMAIN)
            attach_domain(acct, token, WWW)
            print("\nDone. Cloudflare creates the DNS record and certificate; then run:")
            print("  python3 docs/deploy-pages.py --check")
            return 0
        print("\n  ! the token in ~/.secrets/cloudflare.key cannot reach Pages"
              f" ({'no account id' if not acct else 'Cloudflare Pages: Edit missing'}).")
        print("    Prove it any time with:  python3 docs/handshake.py --receipt")
    else:
        print("No token in ~/.secrets/cloudflare.key")

    print("\nFalling back to the wrangler OAuth session")
    if not oauth_session():
        raise SystemExit(
            "  ! no usable credential. Either log in once:\n"
            "      npx wrangler login\n"
            "    or save a token with Account -> Cloudflare Pages: Edit,\n"
            "    Zone -> DNS: Edit, Zone -> Zone: Read to ~/.secrets/cloudflare.key\n"
            "    (python3 docs/handshake.py proves it before you deploy)."
        )
    print("  session ok (domains are managed in the dashboard on this path)\n")
    print("Upload")
    upload(None, None)
    print("\nDomain")
    print(f"  skipped: attaching {DOMAIN}/{WWW} needs the API token.")
    print("  Already attached if `python3 docs/deploy-pages.py --check` passes.")
    print("\nDone. Verify with:  python3 docs/deploy-pages.py --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
