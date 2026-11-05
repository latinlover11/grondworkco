#!/usr/bin/env python3
"""Build and serve the site locally.

Run from the project root:
    python3 dev.py          # picks the first free port from 8010
    python3 dev.py 8080     # or name a port explicitly
"""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from functools import partial
import socket
import subprocess
import sys

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
# Not 8000: Paperless-ngx publishes 8000 on this machine, so the old default
# sent the browser to a different app entirely. 8010 keeps the port memorable
# without colliding with it.
PORT = 8010
PORT_ATTEMPTS = 20


def pick_port(start: int) -> int:
    """Return start if it can be bound, else the next free port after it.

    Probing by binding 127.0.0.1 mirrors what the server itself will do, so a
    port held by a Docker proxy or another dev server is detected rather than
    crashing us with EADDRINUSE after the site has already been rebuilt.
    """
    for port in range(start, start + PORT_ATTEMPTS):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                probe.bind(("127.0.0.1", port))
            except OSError:
                continue
        return port
    print(f"No free port between {start} and {start + PORT_ATTEMPTS - 1}.", file=sys.stderr)
    raise SystemExit(1)


subprocess.run([sys.executable, str(ROOT / "build.py")], check=True)


class NoCacheHandler(SimpleHTTPRequestHandler):
    """Serve rebuilt files, never a cached copy.

    SimpleHTTPRequestHandler answers with Last-Modified and no Cache-Control,
    so browsers may reuse a stale page after build.py rewrites dist/.
    """

    def end_headers(self):
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()


requested = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
port = pick_port(requested)
if port != requested:
    print(f"Port {requested} is already in use; using {port} instead.")

# Serve dist/ by argument instead of chdir: build.py replaces the dist
# directory, which would delete the server's working directory out from under
# it and make every later request fail on os.getcwd().
handler = partial(NoCacheHandler, directory=str(DIST))
server = ThreadingHTTPServer(("127.0.0.1", port), handler)
print(f"Serving {DIST} at http://127.0.0.1:{port}")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("\nStopping development server.")
finally:
    server.server_close()
