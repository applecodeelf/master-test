from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import json
import os
import signal
import socket
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "pocketorigin"
WEB = PACKAGE / "web"
STATE_DIR = ROOT / ".pocketorigin"
LOG_DIR = STATE_DIR / "logs"
PID_FILE = STATE_DIR / "services.json"


def ensure_state():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not PID_FILE.exists():
        PID_FILE.write_text("{}", encoding="utf-8")


def load_state():
    ensure_state()
    try:
        return json.loads(PID_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_state(state):
    ensure_state()
    PID_FILE.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def service_specs():
    return {
        "file-server": {
            "name": "File Server",
            "description": "Share /sdcard/codexfiles over HTTP",
            "port": 8081,
            "cwd": "/sdcard/codexfiles",
            "cmd": [sys.executable, "-m", "http.server", "8081", "--bind", "0.0.0.0"],
        },
        "hello-api": {
            "name": "Hello API",
            "description": "Tiny JSON API demo",
            "port": 8082,
            "cwd": str(ROOT),
            "cmd": [sys.executable, str(PACKAGE / "templates" / "hello_api.py"), "8082"],
        },
        "webhook": {
            "name": "Webhook Receiver",
            "description": "Log incoming POST bodies",
            "port": 8083,
            "cwd": str(ROOT),
            "cmd": [sys.executable, str(PACKAGE / "templates" / "webhook_receiver.py"), "8083"],
        },
        "mc-1710": {
            "name": "Minecraft 1.7.10",
            "description": "Use existing vanilla server in /sdcard/codexfiles/mc-1.7.10-server",
            "port": 25565,
            "cwd": "/sdcard/codexfiles/mc-1.7.10-server",
            "cmd": ["sh", "start.sh"],
        },
    }


def is_running(pid):
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def start_service(service_id):
    specs = service_specs()
    if service_id not in specs:
        raise ValueError("unknown service")

    state = load_state()
    existing = state.get(service_id, {})
    if is_running(existing.get("pid")):
        return existing

    spec = specs[service_id]
    cwd = Path(spec["cwd"])
    if not cwd.exists():
        raise FileNotFoundError(f"missing working directory: {cwd}")

    log_path = LOG_DIR / f"{service_id}.log"
    log_file = log_path.open("ab")
    process = subprocess.Popen(
        spec["cmd"],
        cwd=str(cwd),
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    state[service_id] = {
        "pid": process.pid,
        "log": str(log_path),
        "started_at": int(time.time()),
    }
    save_state(state)
    return state[service_id]


def stop_service(service_id):
    state = load_state()
    entry = state.get(service_id, {})
    pid = entry.get("pid")
    if pid and is_running(pid):
        os.killpg(os.getpgid(int(pid)), signal.SIGTERM)
        time.sleep(0.3)
        if is_running(pid):
            os.killpg(os.getpgid(int(pid)), signal.SIGKILL)
    state.pop(service_id, None)
    save_state(state)


def read_log(service_id, limit=12000):
    state = load_state()
    path = state.get(service_id, {}).get("log")
    if not path:
        path = str(LOG_DIR / f"{service_id}.log")
    log_path = Path(path)
    if not log_path.exists():
        return ""
    data = log_path.read_bytes()[-limit:]
    return data.decode("utf-8", "replace")


def storage_free():
    try:
        stat = os.statvfs("/sdcard" if Path("/sdcard").exists() else str(ROOT))
        free = stat.f_bavail * stat.f_frsize
        return human_bytes(free)
    except OSError:
        return "unknown"


def memory_free():
    try:
        meminfo = Path("/proc/meminfo").read_text(encoding="utf-8", errors="ignore")
        for line in meminfo.splitlines():
            if line.startswith("MemAvailable:"):
                kb = int(line.split()[1])
                return human_bytes(kb * 1024)
    except OSError:
        pass
    return "unknown"


def battery():
    base = Path("/sys/class/power_supply")
    for item in base.glob("battery*/capacity"):
        try:
            return item.read_text().strip() + "%"
        except OSError:
            pass
    return "unknown"


def uptime():
    try:
        seconds = float(Path("/proc/uptime").read_text().split()[0])
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
    except OSError:
        return "unknown"


def human_bytes(value):
    size = float(value)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024


def host_name():
    try:
        return socket.gethostname()
    except OSError:
        return "android"


def json_response(handler, payload, status=200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def text_response(handler, text, status=200):
    body = text.encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "text/plain; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            return self.serve_file(WEB / "index.html", "text/html; charset=utf-8")
        if parsed.path == "/static/style.css":
            return self.serve_file(WEB / "style.css", "text/css; charset=utf-8")
        if parsed.path == "/static/app.js":
            return self.serve_file(WEB / "app.js", "application/javascript; charset=utf-8")
        if parsed.path == "/api/status":
            return json_response(self, {
                "battery": battery(),
                "storage_free": storage_free(),
                "memory_free": memory_free(),
                "uptime": uptime(),
                "host": host_name(),
            })
        if parsed.path == "/api/services":
            return json_response(self, {"services": self.service_list()})
        if parsed.path.startswith("/api/services/") and parsed.path.endswith("/log"):
            service_id = parsed.path.split("/")[3]
            return json_response(self, {"log": read_log(service_id)})
        return text_response(self, "not found", 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if len(parts) == 4 and parts[:2] == ["api", "services"]:
            service_id = parts[2]
            action = parts[3]
            try:
                if action == "start":
                    return json_response(self, {"ok": True, "service": start_service(service_id)})
                if action == "stop":
                    stop_service(service_id)
                    return json_response(self, {"ok": True})
            except Exception as exc:
                return json_response(self, {"ok": False, "error": str(exc)}, 500)
        return text_response(self, "not found", 404)

    def serve_file(self, path, content_type):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def service_list(self):
        state = load_state()
        services = []
        for service_id, spec in service_specs().items():
            entry = state.get(service_id, {})
            pid = entry.get("pid")
            running = is_running(pid)
            services.append({
                "id": service_id,
                "name": spec["name"],
                "description": spec["description"],
                "port": spec["port"],
                "pid": pid if running else None,
                "running": running,
            })
        return services

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args), flush=True)


def main():
    ensure_state()
    port = int(os.environ.get("POCKETORIGIN_PORT", "7860"))
    host = os.environ.get("POCKETORIGIN_HOST", "0.0.0.0")
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"PocketOrigin listening on http://{host}:{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
