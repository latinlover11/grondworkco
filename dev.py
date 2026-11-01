#!/usr/bin/env python3
"""Build and serve the site locally.

Run from the project root:
    python3 dev.py
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
PORT = 8000

subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)
os.chdir(DIST)


class NoCacheHandler(SimpleHTTPRequestHandler):
    """Serve rebuilt files, never a cached copy.

    SimpleHTTPRequestHandler answers with Last-Modified and no Cache-Control,
    so browsers may reuse a stale page after build.py rewrites dist/.
    """

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()


server = ThreadingHTTPServer(("127.0.0.1", PORT), NoCacheHandler)
print(f"Serving {DIST} at http://127.0.0.1:{PORT}")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopping development server.")
finally:
    server.server_close()
