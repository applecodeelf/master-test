from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
import sys


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", "replace")
        print(f"[{datetime.now().isoformat()}] {self.path} {body}", flush=True)
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        body = b"PocketOrigin webhook receiver is running.\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8083
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"webhook receiver listening on 0.0.0.0:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

