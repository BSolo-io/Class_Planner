"""A tiny fake City Tech catalog, so the scraper can be tested without the real site.

It copies how the real site behaves: pages load their data in the background
from /api/... feeds, the program list pages with a "Next page" button, and the
requirements page embeds a Nuxt payload.
"""

from __future__ import annotations

import html
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import sample_data

PER_PAGE = 2

LIST_PAGE = """<!doctype html><html><body><main><h1>Programs</h1><ul id="list"><li>Loading results...</li></ul>
<button aria-label="Previous page">&lsaquo;</button><button aria-label="Next page" id="next">&rsaquo;</button></main>
<script>
let page = parseInt(new URLSearchParams(location.search).get('page') || '1');
async function load() {
  const r = await fetch(`/api/v1/cm/test01/programs/search/$filters?catalogId=CAT123&skip=${(page-1)*%PER%}&limit=%PER%&sortBy=name`);
  const j = await r.json();
  await new Promise(res => setTimeout(res, 150));
  document.getElementById('list').innerHTML = j.data.map(p => `<li><a href="/programs/${p.name}">${p.catalogDisplayName}</a></li>`).join('');
  document.getElementById('next').disabled = page * %PER% >= j.listLength;
}
document.getElementById('next').onclick = () => { page++; history.pushState({}, '', `/programs?page=${page}`); load(); };
load();
</script></body></html>""".replace("%PER%", str(PER_PAGE))

REQUIREMENTS_PAGE = """<!doctype html><html><body><article><h1>%TITLE%</h1><p>Requirements</p></article>
<script type="application/json" id="__NUXT_DATA__">%PAYLOAD%</script>
<script>
setTimeout(() => {
  fetch('/api/v1/cm/test01/courses/search/%24filters?catalogId=CAT123&skip=0&limit=50000&columns=code,longName');
  fetch('/api/v1/cm/test01/courses/search/%24filters?catalogId=CAT123&skip=0&limit=50000');
  fetch('/api/v1/cm/test01/courseSets?courseSetGroupIds=ivBZAeiOtdPN3jjTOmfk&courseSetGroupIds=WQNxggwvCK6XwdDOrj5x');
}, 300);
</script></body></html>"""


def _course_pages() -> dict[str, str]:
    pages = {"0370271": sample_data.ACC_1201_PAGE}
    for record in sample_data.COURSES:
        cid = record.get("courseGroupId") or record["id"].split("-")[0]
        pages.setdefault(cid, sample_data.simple_course_page(record["code"], record["longName"]))
    return pages


class Handler(BaseHTTPRequestHandler):
    requests_seen: list[str] = []

    def log_message(self, *args):  # keep test output quiet
        pass

    def _send(self, status: int, body: str, content_type: str = "text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, value):
        self._send(200, json.dumps(value), "application/json")

    def do_GET(self):
        url = urlparse(self.path)
        path, query = url.path, parse_qs(url.query)
        Handler.requests_seen.append(self.path)

        if path == "/robots.txt":
            return self._send(200, "User-agent: *\nAllow: /\n", "text/plain")
        if path == "/programs":
            return self._send(200, LIST_PAGE)
        if "/programs/search/" in path:
            skip = int(query.get("skip", ["0"])[0])
            limit = int(query.get("limit", ["20"])[0])
            return self._json({"listLength": len(sample_data.PROGRAM_LIST), "data": sample_data.PROGRAM_LIST[skip : skip + limit]})
        if "/courses/search/" in path:
            records = sample_data.COURSES
            if "columns" in query:
                records = [{k: r[k] for k in ("id", "code", "longName") if k in r} for r in records]
            return self._json({"listLength": len(records), "data": records})
        if path.endswith("/courseSets"):
            return self._json(sample_data.COURSE_SETS)

        parts = [p for p in path.split("/") if p]
        if len(parts) == 3 and parts[0] == "programs" and parts[1] == "AC-AAS":
            if parts[2] == "requirements-psa8V":
                payload = json.dumps(sample_data.page_payload()).replace("</", "<\\/")
                return self._send(200, REQUIREMENTS_PAGE.replace("%TITLE%", "Accounting - AAS").replace("%PAYLOAD%", payload))
            if parts[2] == "general-aoYks":
                return self._send(200, "<html><body><article><h1>Accounting - AAS</h1><p>Careers: bookkeeper, tax preparer.</p></article></body></html>")
        if len(parts) == 2 and parts[0] == "courses":
            text = _course_pages().get(parts[1])
            if text:
                lines = "".join(f"<div>{html.escape(line)}</div>" for line in text.splitlines())
                return self._send(200, f"<html><body><article>{lines}</article></body></html>")
        return self._send(404, "<html><body>Not found</body></html>")


class MockSite:
    def __enter__(self):
        Handler.requests_seen = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()

    @property
    def requests(self) -> list[str]:
        return Handler.requests_seen
