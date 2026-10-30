"""Snapshot the City Tech public catalog into JSON files for Class Planner.

It opens the public catalog pages in a hidden browser, like a normal visitor,
one page at a time. It saves what each page loads under raw/, then builds slim
JSON dictionaries next to it.

Run from server/scraper:
    uv run scrape.py                          # program list + 3 sample programs
    uv run scrape.py --programs CST-BT EET-AAS
    uv run scrape.py --with-core              # also prerequisites for CUNY core course lists
    uv run scrape.py --all                    # every program (slow: about 1 page per second)
    uv run scrape.py --offline                # rebuild the JSON from saved raw data, no browser
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.robotparser import RobotFileParser

import nuxt_payload
import transform

BASE_URL = "https://citytech.catalog.cuny.edu"
GENERAL_TAB = "general-aoYks"
REQUIREMENTS_TAB = "requirements-psa8V"
DEFAULT_PROGRAMS = ["AC-AAS", "ACP-BS", "APM-BS"]
DEFAULT_TERM = "2026-Fall"
SCRIPT_DIR = Path(__file__).resolve().parent

# Data the catalog pages load in the background, matched by URL path.
DATA_FEEDS = {
    "program_list": "/programs/search/",
    "courses": "/courses/search/",
    "course_sets": "/courseSets",
}


def log(message: str) -> None:
    print(message, flush=True)


class PageError(Exception):
    pass


# --------------------------------------------------------------------------- raw storage


class RawStore:
    """Reads and writes the raw/ folder, so runs can resume and rebuild offline."""

    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.raw_dir = out_dir / "raw"
        (self.raw_dir / "programs").mkdir(parents=True, exist_ok=True)
        (self.raw_dir / "course_pages").mkdir(parents=True, exist_ok=True)

    def path(self, *parts: str) -> Path:
        return self.raw_dir.joinpath(*parts)

    def has(self, *parts: str) -> bool:
        return self.path(*parts).exists()

    def read(self, *parts: str, default=None):
        p = self.path(*parts)
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

    def write(self, data, *parts: str) -> None:
        p = self.path(*parts)
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(p)

    def load_all(self) -> dict:
        programs = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(self.path("programs").glob("*.json"))}
        pages = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(self.path("course_pages").glob("*.json"))}
        return {
            "program_list": self.read("program_list.json"),
            "programs": programs,
            "courses": (self.read("courses_all.json") or {}).get("data") or [],
            "course_sets": self.read("course_sets.json") or {},
            "course_pages": pages,
        }


# --------------------------------------------------------------------------- browser


class CatalogBrowser:
    """One hidden browser tab that visits catalog pages slowly and keeps their data."""

    def __init__(self, base_url: str, delay: float, headed: bool):
        try:
            from playwright.sync_api import TimeoutError as PlaywrightTimeout
            from playwright.sync_api import sync_playwright
        except ImportError:
            sys.exit("Playwright is not installed. Run:  uv sync  then  uv run playwright install chromium")
        self.Timeout = PlaywrightTimeout
        self.base_url = base_url.rstrip("/")
        self.delay = delay
        self._last_load = 0.0
        self._responses: list = []
        self._pw = sync_playwright().start()
        try:
            self._browser = self._pw.chromium.launch(headless=not headed)
        except Exception as error:  # usually: browser not downloaded yet
            self._pw.stop()
            sys.exit(f"Could not start Chromium ({error}).\nRun:  uv run playwright install chromium")
        self.page = self._browser.new_page()
        self.page.set_default_timeout(45_000)
        self.page.on("response", self._on_response)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self._browser.close()
        self._pw.stop()

    def _on_response(self, response) -> None:
        if response.request.method == "GET" and any(p in response.url for p in DATA_FEEDS.values()):
            self._responses.append(response)

    def _pause(self) -> None:
        wait = self.delay - (time.monotonic() - self._last_load)
        if wait > 0:
            time.sleep(wait)

    def open(self, path: str) -> None:
        """Go to a catalog page (politely spaced) and wait for its HTML."""
        self._pause()
        self._responses.clear()
        url = self.base_url + path
        try:
            response = self.page.goto(url, wait_until="domcontentloaded")
        except self.Timeout as error:
            raise PageError(f"timed out loading {url}") from error
        finally:
            self._last_load = time.monotonic()
        if response is None or not response.ok:
            raise PageError(f"{url} answered {response.status if response else 'nothing'}")

    def settle(self, seconds: float) -> None:
        """Wait while still letting the page finish loading data."""
        self.page.wait_for_timeout(int(seconds * 1000))

    def wait_for_feeds(self, kinds: list[str], timeout: float) -> bool:
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if all(any(DATA_FEEDS[k] in r.url for r in self._responses) for k in kinds):
                return True
            self.page.wait_for_timeout(250)
        return False

    def feed_data(self, kind: str) -> list[tuple[str, object]]:
        out = []
        for response in self._responses:
            if DATA_FEEDS[kind] in response.url:
                try:
                    out.append((response.url, response.json()))
                except Exception as error:
                    log(f"    (could not read {kind} data: {error})")
        return out

    def nuxt_payload(self) -> str | None:
        return self.page.evaluate("() => document.getElementById('__NUXT_DATA__')?.textContent ?? null")

    def hrefs(self, prefix: str) -> list[str]:
        return self.page.eval_on_selector_all(f'a[href^="{prefix}"]', "els => els.map(e => e.getAttribute('href'))")

    def wait_for(self, selector: str, timeout: float) -> bool:
        try:
            self.page.wait_for_selector(selector, timeout=int(timeout * 1000))
            return True
        except self.Timeout:
            return False

    def main_text(self) -> str:
        for selector in ("article", "main", "body"):
            locator = self.page.locator(selector).first
            if locator.count():
                return locator.inner_text()
        return ""

    def click_next_page(self) -> bool:
        """Click the program list's 'Next page' button. False when there is no next page."""
        button = self.page.get_by_role("button", name="Next page")
        if not button.count() or not button.first.is_enabled():
            return False
        first = (self.hrefs("/programs/") or [None])[0]
        self._pause()
        self._responses.clear()
        button.first.click()
        self._last_load = time.monotonic()
        try:
            self.page.wait_for_function(
                "first => (document.querySelector('a[href^=\"/programs/\"]')?.getAttribute('href') ?? null) !== first",
                arg=first,
                timeout=20_000,
            )
        except self.Timeout:
            return False
        return True

    def robots_allows(self, paths: list[str]) -> bool:
        try:
            response = self.page.request.get(self.base_url + "/robots.txt")
            text = response.text() if response.ok else ""
        except Exception:
            text = ""
        parser = RobotFileParser()
        parser.parse(text.splitlines())
        return all(parser.can_fetch("*", self.base_url + p) for p in paths)


# --------------------------------------------------------------------------- steps


def scrape_program_list(browser: CatalogBrowser, store: RawStore, refresh: bool) -> dict:
    if not refresh and store.has("program_list.json"):
        saved = store.read("program_list.json")
        log(f"Program list: using saved copy ({len(saved['codes'])} programs). Use --refresh to update.")
        return saved

    log("Program list: reading /programs ...")
    codes: list[str] = []
    meta: dict[str, dict] = {}
    catalog_id = None
    total = None
    browser.open("/programs")
    for page_number in range(1, 60):
        if not browser.wait_for('a[href^="/programs/"]', 25):
            log("  no program links found on the page")
            break
        browser.wait_for_feeds(["program_list"], 8)
        for url, data in browser.feed_data("program_list"):
            catalog_id = catalog_id or transform.query_param(url, "catalogId")
            if isinstance(data, dict):
                total = data.get("listLength", total)
                for item in data.get("data") or []:
                    code = item.get("code") or item.get("name")
                    if code:
                        meta[code] = transform.slim_list_item(item)
        new = 0
        for href in browser.hrefs("/programs/"):
            code = transform.program_code_from_href(href)
            if code and code not in codes:
                codes.append(code)
                new += 1
        log(f"  page {page_number}: +{new} (have {len(codes)}{f' of {total}' if total else ''})")
        if new == 0 or (total and len(codes) >= total):
            break
        if not browser.click_next_page():
            break

    result = {"codes": codes, "meta": meta, "catalogId": catalog_id, "scrapedAt": transform.now_iso()}
    store.write(result, "program_list.json")
    return result


def scrape_program(browser: CatalogBrowser, store: RawStore, code: str, refresh: bool, state: dict) -> None:
    if not refresh and store.has("programs", f"{code}.json"):
        log(f"  {code}: already saved")
        return
    log(f"  {code}: requirements page")
    browser.open(f"/programs/{code}/{REQUIREMENTS_TAB}")
    payload_text = browser.nuxt_payload()

    need_courses = (refresh and not state.get("courses_this_run")) or not store.has("courses_all.json")
    if need_courses:
        browser.wait_for_feeds(["courses"], 40)
        browser.settle(3)  # the page loads a short and a full course list; give the second one time
    browser.wait_for_feeds(["course_sets"], 6)
    browser.settle(1)

    program = None
    if payload_text:
        try:
            program = nuxt_payload.find_program(nuxt_payload.decode(json.loads(payload_text)), code)
        except (ValueError, json.JSONDecodeError) as error:
            log(f"    could not read the page data: {error}")
    if not program:
        log(f"    no program data found for {code}; skipping (check the code on the catalog site)")
        return

    if need_courses:
        lists = [transform.parse_course_records(data) for _, data in browser.feed_data("courses")]
        records = transform.merge_course_records(*lists)
        if records:
            store.write({"capturedAt": transform.now_iso(), "count": len(records), "data": records}, "courses_all.json")
            state["courses_this_run"] = True
            log(f"    saved the full course list ({len(records)} courses)")
        else:
            log("    the course list did not load on this page; will try again on the next program")

    sets = store.read("course_sets.json") or {}
    new_sets = {}
    for _, data in browser.feed_data("course_sets"):
        new_sets.update(transform.parse_course_sets(data))
    if new_sets:
        sets.update(new_sets)
        store.write(sets, "course_sets.json")
        log(f"    saved {len(new_sets)} course list(s): " + ", ".join(str(s.get("name")) for s in new_sets.values()))

    general_text = None
    try:
        browser.open(f"/programs/{code}/{GENERAL_TAB}")
        browser.wait_for("article", 15)
        general_text = browser.main_text()
    except PageError as error:
        log(f"    (general tab skipped: {error})")

    store.write(
        {"code": code, "scrapedAt": transform.now_iso(), "program": nuxt_payload.to_plain(program), "generalText": general_text},
        "programs",
        f"{code}.json",
    )


def needed_course_ids(store: RawStore, codes: list[str], with_core: bool, base_url: str) -> list[str]:
    raw = store.load_all()
    sets = transform.build_course_sets(raw["course_sets"])
    needed: list[str] = []
    for code in codes:
        raw_program = raw["programs"].get(code)
        if not raw_program:
            continue
        program = transform.build_program(code, None, raw_program, base_url)
        course_ids, set_ids = transform.referenced_ids(program)
        if with_core:
            for set_id in set_ids:
                course_ids += sets.get(set_id, {}).get("courseIds", [])
        for cid in course_ids:
            if cid not in needed:
                needed.append(cid)
    return needed


def scrape_course_pages(browser: CatalogBrowser, store: RawStore, ids: list[str], refresh: bool) -> None:
    known = {transform.course_id(r): r.get("code") for r in (store.read("courses_all.json") or {}).get("data") or []}
    todo = [cid for cid in ids if refresh or not store.has("course_pages", f"{cid}.json")]
    log(f"Course pages: {len(todo)} to read, {len(ids) - len(todo)} already saved")
    for number, cid in enumerate(todo, 1):
        label = known.get(cid) or cid
        try:
            browser.open(f"/courses/{cid}")
            browser.wait_for("article", 15)
            text = browser.main_text()
            if "requisite" not in text.lower():
                browser.settle(1.5)
                text = browser.main_text()
        except PageError as error:
            log(f"  [{number}/{len(todo)}] {label}: skipped ({error})")
            continue
        store.write({"id": cid, "scrapedAt": transform.now_iso(), "text": text}, "course_pages", f"{cid}.json")
        log(f"  [{number}/{len(todo)}] {label}")


# --------------------------------------------------------------------------- output


def write_outputs(store: RawStore, base_url: str, term: str) -> dict:
    outputs = transform.build_outputs(store.load_all(), base_url, term)
    for name, data in outputs.items():
        path = store.out_dir / name
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(path)
    gitignore = store.out_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("# Raw page data is large and can be re-downloaded.\nraw/\n", encoding="utf-8")
    return outputs


def print_summary(outputs: dict, out_dir: Path) -> None:
    meta = outputs["meta.json"]
    counts = meta["counts"]
    log("\nDone.")
    log(f"  Programs:   {counts['programs']} listed, {counts['programsDetailed']} with full requirements")
    log(f"  Courses:    {counts['courses']} ({counts['coursesWithPageDetails']} with prerequisites read)")
    log(f"  CUNY core / course lists: {counts['courseSets']}")
    for warning in meta["warnings"]:
        log(f"  ! {warning}")
    log(f"  Saved to:   {out_dir}")
    if meta["detailedPrograms"]:
        log(f"  Check one:  uv run show.py {meta['detailedPrograms'][0]}")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Snapshot the City Tech catalog into JSON.")
    parser.add_argument("--programs", nargs="+", metavar="CODE", help=f"program codes to read in full (default: {' '.join(DEFAULT_PROGRAMS)})")
    parser.add_argument("--all", action="store_true", help="read every program in full (slow)")
    parser.add_argument("--with-core", action="store_true", help="also read prerequisites for courses in CUNY core lists")
    parser.add_argument("--refresh", action="store_true", help="download again even if saved")
    parser.add_argument("--offline", action="store_true", help="no browser: rebuild JSON from saved raw data")
    parser.add_argument("--delay", type=float, default=1.0, help="seconds between page loads (default 1.0; please keep it >= 1)")
    parser.add_argument("--headed", action="store_true", help="show the browser window while it works")
    parser.add_argument("--term", default=DEFAULT_TERM, help=f"folder name for this snapshot (default {DEFAULT_TERM})")
    parser.add_argument("--out", help="output folder (default: server/data/citytech/<term>)")
    parser.add_argument("--base-url", default=BASE_URL, help=argparse.SUPPRESS)  # for tests
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    out_dir = Path(args.out).resolve() if args.out else (SCRIPT_DIR.parent / "data" / "citytech" / args.term).resolve()
    store = RawStore(out_dir)
    base_url = args.base_url.rstrip("/")

    if not args.offline:
        with CatalogBrowser(base_url, args.delay, args.headed) as browser:
            if not browser.robots_allows(["/programs", "/courses/"]):
                log("The site's robots.txt does not allow this. Stopping.")
                return 1
            program_list = scrape_program_list(browser, store, args.refresh)
            codes = list(program_list["codes"]) if args.all else (args.programs or DEFAULT_PROGRAMS)
            unknown = [c for c in codes if program_list["codes"] and c not in program_list["codes"]]
            if unknown:
                log(f"Not in the program list (will still try): {', '.join(unknown)}")
            log(f"Programs: reading {len(codes)} in full")
            state: dict = {}
            for code in codes:
                try:
                    scrape_program(browser, store, code, args.refresh, state)
                except PageError as error:
                    log(f"  {code}: skipped ({error})")
            ids = needed_course_ids(store, codes, args.with_core, base_url)
            scrape_course_pages(browser, store, ids, args.refresh)

    outputs = write_outputs(store, base_url, args.term)
    print_summary(outputs, out_dir)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        log("\nStopped. Everything read so far is saved; run the same command again to continue.")
        sys.exit(130)
