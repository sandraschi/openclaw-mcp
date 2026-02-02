"""
HTTP server that serves openclaw-mcp log file for the webapp Logger modal.

Run: python -m openclaw_mcp.serve_logs
Serves GET /api/logs?tail=500 with CORS. Default port 8765 (CLAWD_LOG_SERVER_PORT).
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from openclaw_mcp.logging_config import get_log_file_path


def tail_log_lines(path: Path, n: int = 500) -> list[dict]:
    """Read last n lines from log file; parse JSON lines into list of dicts."""
    if not path.exists():
        return []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return []
    out: list[dict] = []
    for line in lines[-n:]:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            out.append({"msg": line, "level": "RAW", "ts": None})
    return out


class LogsHandler(BaseHTTPRequestHandler):
    """Handler for GET /api/logs with CORS."""

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._send_cors()
        self.end_headers()

    def _send_cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/logs":
            self.send_response(404)
            self._send_cors()
            self.end_headers()
            return
        params = parse_qs(parsed.query)
        tail = 500
        if "tail" in params and params["tail"]:
            try:
                tail = max(1, min(10000, int(params["tail"][0])))
            except ValueError:
                pass
        log_path = get_log_file_path()
        entries = tail_log_lines(log_path, n=tail)
        body = json.dumps({"entries": entries, "source": str(log_path)}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._send_cors()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


def main() -> None:
    port = int(os.environ.get("CLAWD_LOG_SERVER_PORT", "8765"))
    host = os.environ.get("CLAWD_LOG_SERVER_HOST", "127.0.0.1")
    log_path = get_log_file_path()
    print(f"Log server: http://{host}:{port}/api/logs (tail from {log_path})")
    server = ThreadingHTTPServer((host, port), LogsHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
