from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import sys


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps({
            "ok": True,
            "service": "hello-api",
            "message": "Hello from an Android phone"
        }).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8082
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"hello-api listening on 0.0.0.0:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()

