#!/usr/bin/env python3
"""Local browser UI for processing raw pasted Hawaii unclaimed-property claim text."""

from __future__ import annotations

import html
import json
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

from unclaimed_funds_lead_tool import build_lead_dataframe, read_raw_claim_text, write_browser_outputs

HOST = "127.0.0.1"
PORT = 8765
DEFAULT_OUTPUT_DIR = Path(r"C:\tmp\my_claim_report")

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Raw Claim Processor</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #f4f6f8; color: #1f2933; }
    main { max-width: 1100px; margin: 0 auto; padding: 28px; }
    h1 { margin: 0 0 8px; }
    p { color: #52606d; }
    textarea { width: 100%; min-height: 430px; box-sizing: border-box; font-family: Consolas, monospace; font-size: 14px; padding: 14px; border: 1px solid #bcccdc; background: #fff; }
    button { margin-top: 14px; padding: 11px 18px; border: 0; background: #0f4c81; color: #fff; font-size: 15px; cursor: pointer; }
    button:disabled { background: #829ab1; cursor: wait; }
    .status { margin-top: 16px; padding: 12px; background: #fff; border: 1px solid #d9e2ec; white-space: pre-wrap; }
    .error { border-color: #d64545; color: #9b1c1c; }
    .success { border-color: #2f855a; color: #22543d; }
  </style>
</head>
<body>
<main>
  <h1>Raw Hawaii Claim Processor</h1>
  <p>Paste copied claim rows from the Hawaii unclaimed-property site, then click Process. The report is written to C:\\tmp\\my_claim_report\\lead_report.html.</p>
  <textarea id="raw" spellcheck="false" placeholder="Paste raw scraped claim text here..."></textarea>
  <br>
  <button id="process">Process</button>
  <div id="status" class="status">Waiting for pasted claim text.</div>
</main>
<script>
const button = document.getElementById('process');
const statusBox = document.getElementById('status');
button.addEventListener('click', async () => {
  button.disabled = true;
  statusBox.className = 'status';
  statusBox.textContent = 'Processing...';
  try {
    const body = new URLSearchParams({ raw_text: document.getElementById('raw').value });
    const res = await fetch('/process', { method: 'POST', body });
    const data = await res.json();
    if (!res.ok || !data.ok) throw new Error(data.error || 'Processing failed');
    statusBox.className = 'status success';
    statusBox.textContent = `Processed ${data.records} records.\nReport: ${data.report_path}\nCSV folder: ${data.output_dir}`;
    window.open('/report', '_blank');
  } catch (err) {
    statusBox.className = 'status error';
    statusBox.textContent = err.message;
  } finally {
    button.disabled = false;
  }
});
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        return

    def send_text(self, body: str, status: int = 200, content_type: str = "text/html; charset=utf-8") -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def send_json(self, data: dict, status: int = 200) -> None:
        self.send_text(json.dumps(data), status=status, content_type="application/json; charset=utf-8")

    def do_GET(self) -> None:
        if self.path == "/" or self.path.startswith("/?"):
            self.send_text(PAGE)
            return
        if self.path == "/report":
            report = DEFAULT_OUTPUT_DIR / "lead_report.html"
            if report.exists():
                self.send_text(report.read_text(encoding="utf-8"))
            else:
                self.send_text("<h1>No report yet</h1><p>Paste claim text and click Process first.</p>", status=404)
            return
        self.send_text("Not found", status=404, content_type="text/plain; charset=utf-8")

    def do_POST(self) -> None:
        if self.path != "/process":
            self.send_json({"ok": False, "error": "Not found"}, status=404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        raw_text = parse_qs(body).get("raw_text", [""])[0]
        try:
            raw_df = read_raw_claim_text(raw_text)
            lead_df = build_lead_dataframe(raw_df, fuzzy_threshold=90)
            report_path, sections = write_browser_outputs(lead_df, DEFAULT_OUTPUT_DIR)
        except Exception as exc:
            self.send_json({"ok": False, "error": html.escape(str(exc))}, status=400)
            return
        self.send_json(
            {
                "ok": True,
                "records": int(len(lead_df)),
                "report_path": str(report_path),
                "output_dir": str(DEFAULT_OUTPUT_DIR),
                "csv_files": [str(DEFAULT_OUTPUT_DIR / section.filename) for section in sections],
            }
        )


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"Serving local claim processor at {url}")
    webbrowser.open(url)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
