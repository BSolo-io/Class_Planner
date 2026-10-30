# City Tech catalog scraper

Copies the public City Tech catalog into JSON files the app can load as dictionaries.

It opens the catalog pages in a hidden browser, like a normal visitor, one page per
second. The site's `robots.txt` allows this (`Allow: /`), and the script checks it
again before every run.

## Setup (once)

```bash
cd server/scraper
uv sync                            # installs Playwright + pytest into .venv
uv run playwright install chromium # downloads the browser it uses (~150 MB)
```

## Run

```bash
uv run scrape.py                         # program list + AC-AAS, ACP-BS, APM-BS in full
uv run show.py AC-AAS                    # print one program to check it
```

More options:

| Command | What it does |
|---|---|
| `uv run scrape.py --programs CST-BT EET-AAS` | Read these programs in full |
| `uv run scrape.py --with-core` | Also read prerequisites for courses in CUNY core lists (Flexible Core etc.) |
| `uv run scrape.py --all` | Every program in full. Slow (thousands of pages). Run at most once per term. |
| `uv run scrape.py --refresh` | Download again even if already saved |
| `uv run scrape.py --offline` | No browser: rebuild the JSON from saved raw data (after changing `transform.py`) |
| `uv run scrape.py --headed` | Show the browser window while it works |
| `uv run scrape.py --term 2027-Spring` | Save into a different term folder |

If it stops halfway (Ctrl+C, Wi-Fi drops), run the same command again. It skips
everything already saved.

## What you get

Saved in `server/data/citytech/2026-Fall/`:

| File | Contents | Look up by |
|---|---|---|
| `programs.json` | Every program: name, degree, CIP code, department. Programs read in full also have `requirements`, `degreeMaps` and `about` (General tab text). | program code, e.g. `"AC-AAS"` |
| `courses.json` | Every course: code, title, credits, description, liberal arts flag, Writing Intensive. Courses whose page was read also have `prereqText`, `prereqCodes`, `prereqIds`, `hasCoreq`, `pathwaysCategory`. | course id, e.g. `"0370271"` |
| `course_codes.json` | Course code → course id | `"ACC 1201"` → `"0370271"` |
| `course_sets.json` | CUNY core and other course lists, with their course ids | list id |
| `meta.json` | When it ran, counts, and warnings about missing data | |
| `raw/` | What each page loaded, kept so runs can resume and rebuild offline. Ignored by git. | |

Program requirements point at courses by **id**, not code. Use `courses.json` to get
the code and title, and `course_sets.json` for lists like "Flexible Core Scientific World".

### Requirement rules

Each requirement group has `rules`. A rule can have:

- `condition`: `allOf`, `completedAllOf`, `completedAtLeastXOf`, ...
- `count`: how many are needed (for "at least X")
- `courses`: course ids, or `courseSets`: course list ids
- `rules`: nested rules
- `notes`: plain-text notes from the catalog
- `extra` / `valueType`: anything else the catalog stored, kept as-is

## Known gaps

- **Prerequisite logic isn't parsed yet.** `prereqText` is the exact sentence from the
  course page. `prereqCodes` lists every course it mentions, but doesn't say which
  are AND/OR or co-requisites. That's the next step (code first, Gemma for odd cases,
  then a human check). See `docs/DEGREE_DATA.md`.
- **Semester names** in degree maps are `Semester 1`, `Semester 2`... unless the
  catalog provides names.
- If the catalog site changes its layout, check `meta.json` warnings, then run with
  `--headed` to watch what happens.

## Code map

| File | Job |
|---|---|
| `scrape.py` | Command line + the browser steps |
| `nuxt_payload.py` | Reads the data the catalog embeds in each page |
| `transform.py` | Raw data → slim JSON (no browser, easy to test) |
| `show.py` | Prints a program to check the results |
| `tests/` | `uv run pytest`: unit tests + a full run against a fake catalog site |

## Be polite

Keep `--delay` at 1 second or more, don't run `--all` more than once per term, and
remember the data belongs to City Tech. Ask the registrar for an official data
export if the project grows.
