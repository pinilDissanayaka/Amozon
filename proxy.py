import http.server
import socketserver
import urllib.request
import urllib.parse
import sys

PORT = 8888

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            url = self.path
            if not url.startswith('http'):
                url = 'http://' + self.headers['Host'] + self.path

            self.send_response(200)
            self.end_headers()

            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(500, f"Error fetching URL: {e}")

with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
    print(f"🚀 Serving proxy on port {PORT}")
    httpd.serve_forever()
