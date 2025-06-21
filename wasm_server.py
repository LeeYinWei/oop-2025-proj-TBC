import http.server
import socketserver
import mimetypes

PORT = 8000
DIRECTORY = "build/web"

# 加上對 .wasm 的 MIME 支援
mimetypes.add_type('application/wasm', '.wasm')

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
