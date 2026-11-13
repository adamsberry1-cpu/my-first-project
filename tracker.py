"""A small web app that shows how many days are left until the end of the year.

Run it with:  python3 tracker.py
Then open:    http://localhost:8000
"""

import json
import os
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse


def days_until_end_of_year(today: date) -> int:
    """Return the number of days from today until December 31 of the same year."""
    end_of_year = date(today.year, 12, 31)
    return (end_of_year - today).days


def days_left_info(today: date) -> dict:
    """Build the data the page shows for a given day."""
    days_left = days_until_end_of_year(today)
    days_in_year = (date(today.year, 12, 31) - date(today.year, 1, 1)).days + 1
    day_of_year = today.timetuple().tm_yday
    return {
        "today": f"{today:%B} {today.day}, {today.year}",
        "year": today.year,
        "days_left": days_left,
        "day_word": "day" if days_left == 1 else "days",
        "percent_done": round(day_of_year / days_in_year * 100, 1),
    }


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Year Tracker</title>
<style>
  :root {
    --bg: #f4f1ea;
    --card: #ffffff;
    --ink: #1f2430;
    --muted: #6b7080;
    --accent: #2f6fed;
    --accent-dark: #1f55c4;
    --track: #e4e7ee;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    min-height: 100vh;
    display: grid;
    place-items: center;
    padding: 24px 16px;
    background: var(--bg);
    color: var(--ink);
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  }
  .card {
    width: 100%;
    max-width: 480px;
    background: var(--card);
    border-radius: 20px;
    padding: 40px 32px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(31, 36, 48, 0.08);
  }
  h1 { margin: 0 0 8px; font-size: 1.75rem; }
  .subtitle { margin: 0 0 32px; color: var(--muted); }
  button {
    width: 100%;
    padding: 22px 24px;
    font-size: 1.35rem;
    font-weight: 700;
    color: #fff;
    background: var(--accent);
    border: none;
    border-radius: 14px;
    cursor: pointer;
    transition: background 0.15s, transform 0.1s;
  }
  button:hover { background: var(--accent-dark); }
  button:active { transform: scale(0.98); }
  button:disabled { opacity: 0.7; cursor: wait; }
  .result { margin-top: 32px; display: none; }
  .result.show { display: block; }
  .today { color: var(--muted); margin: 0 0 8px; }
  .number {
    font-size: 5rem;
    font-weight: 800;
    line-height: 1;
    color: var(--accent);
    margin: 0;
  }
  .label { margin: 8px 0 24px; font-size: 1.1rem; }
  .bar { height: 12px; background: var(--track); border-radius: 999px; overflow: hidden; }
  .fill { height: 100%; width: 0; background: var(--accent); border-radius: 999px; transition: width 0.6s ease; }
  .percent { margin: 8px 0 0; color: var(--muted); font-size: 0.9rem; }
  .error { color: #c0392b; }
</style>
</head>
<body>
  <main class="card">
    <h1>Year Tracker</h1>
    <p class="subtitle">How much of the year is left?</p>
    <button id="check">Check Days Left</button>
    <section class="result" id="result" aria-live="polite">
      <p class="today" id="today"></p>
      <p class="number" id="number"></p>
      <p class="label" id="label"></p>
      <div class="bar"><div class="fill" id="fill"></div></div>
      <p class="percent" id="percent"></p>
    </section>
  </main>
<script>
  const button = document.getElementById("check");
  button.addEventListener("click", async () => {
    // Send the visitor's own date so the answer matches their time zone.
    const d = new Date();
    const local = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") +
                  "-" + String(d.getDate()).padStart(2, "0");
    button.disabled = true;
    try {
      const res = await fetch("/api/days-left?date=" + local);
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong");
      document.getElementById("today").textContent = "Today is " + data.today;
      document.getElementById("number").textContent = data.days_left;
      document.getElementById("label").textContent =
        data.day_word + " left until the end of " + data.year;
      document.getElementById("percent").textContent =
        data.percent_done + "% of " + data.year + " is done";
      document.getElementById("fill").style.width = data.percent_done + "%";
    } catch (err) {
      document.getElementById("today").innerHTML = '<span class="error">' + err.message + "</span>";
    } finally {
      document.getElementById("result").classList.add("show");
      button.disabled = false;
    }
  });
</script>
</body>
</html>
"""


class TrackerHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        url = urlparse(self.path)
        if url.path == "/":
            self._send(200, "text/html; charset=utf-8", PAGE.encode())
        elif url.path == "/api/days-left":
            raw = parse_qs(url.query).get("date", [None])[0]
            try:
                today = date.fromisoformat(raw) if raw else date.today()
            except ValueError:
                self._send_json(400, {"error": "Invalid date, use YYYY-MM-DD"})
                return
            self._send_json(200, days_left_info(today))
        else:
            self._send(404, "text/plain; charset=utf-8", b"Not found")

    def _send_json(self, status: int, data: dict) -> None:
        self._send(status, "application/json", json.dumps(data).encode())

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), TrackerHandler)
    print(f"Year tracker running at http://localhost:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
