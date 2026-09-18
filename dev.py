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
server = ThreadingHTTPServer(("127.0.0.1", PORT), SimpleHTTPRequestHandler)
print(f"Serving {DIST} at http://127.0.0.1:{PORT}")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopping development server.")
finally:
    server.server_close()
