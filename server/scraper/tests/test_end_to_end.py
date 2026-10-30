"""Runs the real scraper, with a real browser, against the fake catalog in mock_site.py."""

import json

import pytest

import scrape
from mock_site import MockSite


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            p.chromium.launch().close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _chromium_available(), reason="Chromium for Playwright is not installed")


def _load(folder, name):
    return json.loads((folder / name).read_text(encoding="utf-8"))


def test_scrape_mock_site(tmp_path, capsys):
    out = tmp_path / "2026-Fall"
    with MockSite() as site:
        code = scrape.main(["--base-url", site.url, "--out", str(out), "--programs", "AC-AAS", "NOPE-XX", "--delay", "0"])
        assert code == 0
        first_run_requests = len(site.requests)

        # A second run reuses everything already saved: no program or course pages again.
        scrape.main(["--base-url", site.url, "--out", str(out), "--programs", "AC-AAS", "--delay", "0"])
        second_run = site.requests[first_run_requests:]
        assert not any(r.startswith("/courses/") or "requirements" in r for r in second_run)

    programs = _load(out, "programs.json")
    courses = _load(out, "courses.json")
    sets = _load(out, "course_sets.json")
    meta = _load(out, "meta.json")

    # All 3 programs came from the paged list (2 per page), with list details.
    assert list(programs) == ["AC-AAS", "ACP-BS", "AHVC-MIN"]
    assert programs["ACP-BS"]["cip"] == "14.1201" and programs["ACP-BS"]["detailed"] is False
    assert meta["catalogId"] == "CAT123"

    ac = programs["AC-AAS"]
    assert ac["detailed"] is True
    assert len(ac["requirements"]) == 3
    assert "bookkeeper" in ac["about"]

    acc = courses["0370271"]
    assert acc["code"] == "ACC 1201" and acc["title"] == "Principles of Accounting II"
    assert acc["prereqCodes"] == ["ACC 1101", "MAT 1275"]
    assert acc["pathwaysCategory"] == "Regular Non-Liberal Arts"
    assert courses["0370261"]["detailScraped"] is True  # program courses got their pages read
    assert "detailScraped" not in courses["0300001"]  # core-list courses only with --with-core

    assert sets["WQNxggwvCK6XwdDOrj5x"]["name"] == "Flexible Core Scientific World"
    assert meta["warnings"] == []
    assert (out / ".gitignore").read_text().strip().endswith("raw/")

    log = capsys.readouterr().out
    assert "NOPE-XX: skipped" in log


def test_with_core_and_offline_rebuild(tmp_path):
    out = tmp_path / "snap"
    with MockSite() as site:
        scrape.main(["--base-url", site.url, "--out", str(out), "--programs", "AC-AAS", "--with-core", "--delay", "0"])
    courses = _load(out, "courses.json")
    assert courses["0300001"]["detailScraped"] is True  # English Composition list course

    (out / "programs.json").unlink()
    assert scrape.main(["--offline", "--out", str(out)]) == 0  # no browser, no site
    assert _load(out, "programs.json")["AC-AAS"]["detailed"] is True
