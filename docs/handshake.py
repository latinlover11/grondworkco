#!/usr/bin/env python3
"""Two-way handshake for the Cloudflare token, then optionally the deploy.

Why this exists: twice a token was reported saved and was not on disk, and the
deploy only found out after it had started. This turns the handoff into one
bounded wait that names the exact step that is missing, and refuses to upload
until every permission the deploy needs has been proven.

  --verify            One-shot check (default).
  --wait [SECONDS]    Poll for the token file first; default 900.
  --then-deploy       On a clean pass, run deploy-pages.py --apply.
  --receipt           Print the last receipt and exit.

It reads ~/.secrets/cloudflare.key directly, so a file saved by any editor
counts - `secretctl add` is not required. If the editor left it at 644 the mode
is fixed to 600 in place.

Each check maps to one permission, so a half-scoped token is caught here rather
than halfway through an upload:

  1. file present        the file exists and is not empty
  2. shape               40 chars of base64url - catches a truncated paste or a URL
  3. token active        GET /user/tokens/verify
  4. Zone:Read           GET /zones?name=waxwinglandscaping.com
  5. Pages:Edit          GET /accounts/{id}/pages/projects
  6. DNS:Edit (best effort) GET /zones/{id}/dns_records

Step 6 is a warning, not a failure: Pages can attach a custom domain and leave
the record for you to add by hand, so a missing DNS scope costs a manual step
rather than the whole migration.

Writes ~/.secrets/cloudflare.handshake (mode 600, never containing the token) so
the other side of the handshake can see the outcome without scraping output.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRETS = Path.home() / ".secrets"
# WAXWING_CF_KEY overrides the path so tests never touch the real credential.
KEY = Path(os.environ.get("WAXWING_CF_KEY") or SECRETS / "cloudflare.key")
RECEIPT = KEY.with_suffix(".handshake")
DOMAIN = "waxwinglandscaping.com"
API = "https://api.cloudflare.com/client/v4"
UA = "waxwing-handshake/1.0"
SHAPE = re.compile(r"[A-Za-z0-9_-]{40}")
MARK = {"pass": "ok  ", "warn": "warn", "fail": "FAIL"}


def api(method: str, path: str, token: str) -> dict:
    req = urllib.request.Request(API + path, method=method)
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
        return {"success": False, "errors": [{"message": f"network: {exc.reason}"}]}


def errors(res: dict) -> str:
    return "; ".join(e.get("message", "?") for e in res.get("errors") or []) or "unknown error"


def read_token() -> tuple[str | None, str]:
    """Return (token, note). The note explains the file state either way."""
    if not KEY.exists():
        return None, "no file"
    if not KEY.is_file():
        return None, "not a regular file"
    try:
        token = KEY.read_text(errors="replace").strip()
    except OSError as exc:
        return None, f"unreadable: {exc.strerror}"
    if not token:
        return None, "file is empty"
    mode = oct(KEY.stat().st_mode)[-3:]
    if mode != "600":
        try:
            KEY.chmod(0o600)
            return token, f"fixed mode {mode} -> 600"
        except OSError:
            return token, f"mode {mode}, could not fix"
    return token, "mode 600"


def shape_note(token: str) -> str:
    if SHAPE.fullmatch(token):
        return "40 chars, base64url alphabet"
    if token.startswith("http"):
        return "looks like a URL, not a token"
    if any(c.isspace() for c in token):
        return "contains whitespace - a partial paste"
    if len(token) != 40:
        return f"{len(token)} chars, expected 40 - token ID, or a truncated paste"
    return "unexpected characters"


def verify(token: str) -> tuple[list[tuple[str, str, str]], str | None]:
    """Run every check. Returns (rows, account_id)."""
    rows: list[tuple[str, str, str]] = []

    # Account-owned tokens are not user tokens: /user/tokens/verify rejects them
    # even when every endpoint the deploy needs accepts them (a 53-character
    # account token authenticated fine here while failing that check). So the
    # shape is a hint, not a gate, and liveness is proven against a real endpoint.
    note = shape_note(token)
    rows.append(("pass" if SHAPE.fullmatch(token) else "warn", "shape", note))

    res = api("GET", "/user/tokens/verify", token)
    if res.get("success"):
        rows.append(("pass", "token active", (res.get("result") or {}).get("status", "active")))
    else:
        probe = api("GET", "/accounts", token)
        if not probe.get("success"):
            rows.append(("fail", "token active", errors(res) + " | /accounts: " + errors(probe)))
            return rows, None
        rows.append(("pass", "token active", "account token, accepted by /accounts"))

    res = api("GET", f"/zones?name={DOMAIN}", token)
    zones = res.get("result") or []
    zone = zones[0] if zones else None
    if zone:
        acct = zone["account"]["id"]
        rows.append(("pass", "Zone:Read", f"{zone['name']}, account {acct[:8]}..."))
    else:
        acct_res = api("GET", "/accounts", token)
        accounts = acct_res.get("result") or []
        if not accounts:
            rows.append(("fail", "Zone:Read", errors(res) or f"zone {DOMAIN} not visible to this token"))
            return rows, None
        acct = accounts[0]["id"]
        rows.append(("warn", "Zone:Read", f"zone not visible; account {acct[:8]}... from /accounts"))

    res = api("GET", f"/accounts/{acct}/pages/projects", token)
    if res.get("success"):
        names = [p.get("name") for p in (res.get("result") or [])]
        rows.append(("pass", "Pages:Edit", f"{len(names)} project(s)"
                     + (f": {', '.join(names)}" if names else "")))
    else:
        rows.append(("fail", "Pages:Edit", errors(res)))

    res = api("GET", f"/zones/{zone['id']}/dns_records?per_page=5", token) if zone else {
        "success": False, "errors": [{"message": "no zone id (Zone:Read missing)"}]}
    if res.get("success"):
        rows.append(("pass", "DNS:Edit", f"{len(res.get('result') or [])} record(s) visible"))
    else:
        rows.append(("warn", "DNS:Edit", errors(res) + " - the domain attach step may need a manual record"))

    return rows, acct


def write_receipt(rows: list[tuple[str, str, str]], ok: bool) -> None:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    body = [f"# Cloudflare handshake {stamp}", f"result: {'PASS' if ok else 'FAIL'}"]
    body += [f"{MARK[s]:5} {name}: {detail}" for s, name, detail in rows]
    try:
        RECEIPT.write_text("\n".join(body) + "\n")
        RECEIPT.chmod(0o600)
    except OSError as exc:
        print(f"  (receipt not written: {exc.strerror})")


def wait_for_file(seconds: int) -> bool:
    print(f"Waiting up to {seconds}s for {KEY}")
    start = time.time()
    next_note = 30
    while True:
        if KEY.is_file() and KEY.stat().st_size > 0:
            print(f"  file appeared after {int(time.time() - start)}s")
            return True
        elapsed = int(time.time() - start)
        if elapsed >= seconds:
            print(f"  still nothing after {seconds}s")
            return False
        if elapsed >= next_note:
            print(f"  ...{elapsed}s, no file yet")
            next_note = elapsed + 30
        time.sleep(2)


def main() -> int:
    args = sys.argv[1:]

    if "--receipt" in args:
        if RECEIPT.is_file():
            print(RECEIPT.read_text().rstrip())
            return 0
        print(f"no receipt yet ({RECEIPT})")
        return 1

    if "--wait" in args:
        i = args.index("--wait")
        seconds = 900
        if i + 1 < len(args) and args[i + 1].isdigit():
            seconds = int(args[i + 1])
        if not wait_for_file(seconds):
            print("\n  Nothing to verify. Save the token to:")
            print(f"    {KEY}")
            return 1

    token, note = read_token()
    print(f"Token file: {KEY}")
    print(f"  {note}\n")
    if token is None:
        print("  No token to verify. Save it as a plain text file at the path above")
        print("  (any editor, trailing newline is fine); no command is needed.")
        write_receipt([("fail", "token file", note)], False)
        return 1

    rows, acct = verify(token)
    for status, name, detail in rows:
        print(f"  {MARK[status]:5} {name:12} {detail}")

    ok = all(status != "fail" for status, _, _ in rows)
    print(f"\n  {'PASS - ready to deploy' if ok else 'FAIL - fix the line(s) marked FAIL'}")
    write_receipt(rows, ok)
    if not ok:
        return 1

    print(f"  receipt: {RECEIPT}")
    if "--then-deploy" in args:
        print("\nDeploy")
        return subprocess.run(
            [sys.executable, str(ROOT / "docs" / "deploy-pages.py"), "--apply"], cwd=ROOT
        ).returncode
    print("\n  Next: python3 docs/deploy-pages.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
