#!/usr/bin/env python3
"""Start a local server for the Apple Park Kids site."""

import http.server
import os
import socketserver
import webbrowser

PORT = 8080
DIR = os.path.dirname(os.path.abspath(__file__))

os.chdir(DIR)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    url = f"http://localhost:{PORT}"
    print(f"Serving Apple Park Kids at {url}")
    print("Press Ctrl+C to stop.")
    webbrowser.open(url)
    httpd.serve_forever()
