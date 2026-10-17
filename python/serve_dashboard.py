"""
RetailPulse: Live Interactive Web Dashboard Server
Launches a lightweight local HTTP server to view the executive analytics dashboard.
"""

import http.server
import socketserver
import webbrowser
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = PROJECT_ROOT / "web"
PORT = 8080


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def log_message(self, format, *args):
        # Keep terminal output clean
        pass


def run_server():
    print("=" * 65)
    print(" RetailPulse — Interactive Executive Dashboard Server")
    print("=" * 65)
    print(f"\n[*] Serving dashboard files from:\n    {WEB_DIR}")

    # Find open port if 8080 is occupied
    actual_port = PORT
    for attempt_port in range(PORT, PORT + 10):
        try:
            with socketserver.TCPServer(("", attempt_port), QuietHandler) as httpd:
                url = f"http://localhost:{attempt_port}"
                print(f"\n[+] Dashboard is LIVE at: {url}")
                print("    Press Ctrl + C in this terminal to stop the server at any time.\n")
                print("=" * 65)

                # Attempt to open default browser
                try:
                    webbrowser.open(url)
                except Exception:
                    pass

                httpd.serve_forever()
                break
        except OSError:
            print(f"[!] Port {attempt_port} is busy, trying port {attempt_port + 1}...")
            continue


if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        print("\n[*] RetailPulse Dashboard server stopped successfully.")
        sys.exit(0)
