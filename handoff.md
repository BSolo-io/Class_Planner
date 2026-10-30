# Handoff: where the project stands (2026-10-30)

Read this together with `AGENTS.md` (repo root) and `server/AGENTS.md`.
The person you're working with prefers **short, plain-English answers**, and the
team has mixed experience. Work in small steps, and report back after each step.

## The app in one paragraph

Class Planner helps City Tech (CUNY) students find a career they like through a calm,
fun quiz, then plan the classes to get there. Students with 1+ semester done can
share a transcript instead. The tracker shows done / available / locked classes and a
suggested next semester. A key feature is **exploring without wasting money**: suggest
classes that fill a slot the student's major needs anyway *and* fit the career or
second major they're curious about. It's a **local desktop app**, not deployed.

## Decisions already made

| Decision | Why |
|---|---|
| Front end: React + Vite, JavaScript, Oxlint | Team knows JS |
| AI: Gemma 4 12B (`gemma4:12b`) in local Ollama | Free, private, reads images |
| **Code decides, AI explains** | Full-time checks, requirements, prerequisites and schedules are exact rules. **Do not train or fine-tune a model for them.** Gemma explains results, chats, reads transcripts, and later can call the planner as a tool. |
| Catalog data: a JSON snapshot made by a Python scraper | Fast lookups, works offline, one scrape per term |
| Scraper: Python + uv + Playwright, in `server/scraper/` | Already built and tested against a mock site |
| Never call `app.coursedog.com` directly | It answers `Unauthenticated` outside the catalog site. Don't fake headers. Read public pages only. |
| Transcripts never leave the machine; no real student data in the repo | Privacy (FERPA) |

**Not decided yet: the back-end language.** The recommendation is **Python (FastAPI)**,
because the scraper and the planner are Python data work and React just calls
`localhost`. Node (Express) is the alternative. **Ask the person to confirm before
scaffolding the back end.**

## Repo layout (check it; it changed during setup)

Expected now (repo root = the React app):

```
AGENTS.md, CLAUDE.md (should contain "@AGENTS.md"), docs/, public/, src/
server/
  AGENTS.md
  scraper/        scrape.py, transform.py, nuxt_payload.py, show.py, tests/, pyproject.toml, README.md
  data/citytech/2026-Fall/   (JSON output goes here; raw/ is git-ignored)
  src/            (back end, not built yet)
```

The root `AGENTS.md` and `docs/ARCHITECTURE.md` still use older paths like
`Class_Planner/src/...` and say prerequisite checks live in `src/lib/prereqs.js`.
Fix them to match the real layout and the decisions above (planner logic lives in
the back end). Make sure `CLAUDE.md` exists with `@AGENTS.md`.

## What we learned about the City Tech catalog

- Site: `https://citytech.catalog.cuny.edu`. It's a Coursedog (Nuxt) site; school id
  `nyt01`. `robots.txt` says `Allow: /`.
- Program pages: `/programs/{CODE}/general-aoYks`, `/requirements-psa8V`,
  `/degree-maps-MZNrs`. The tab endings are the same for every program.
  Codes look like `AC-AAS`, `ACP-BS`, `APM-BS`, `-BT`, `-MIN`, certificates.
- Program list: `/programs` shows 20 per page; page with the **"Next page"** button
  (161 programs total).
- Requirements page HTML embeds the program in `<script id="__NUXT_DATA__">`
  (devalue format), under `data["program-{CODE}-undefined"].program`, including
  `requisites.requisitesSimple` (rules) and `degreeMaps`.
- That page also loads the **full course list** (5,286 courses) and the **course lists**
  it references (CUNY core: "Flexible Core Scientific World", etc.).
- **Program rules point at courses by id, not code**: id `0370271` = `ACC 1201`.
  Course page: `/courses/{id}`.
- **Prerequisites exist only on course pages**, as a sentence, e.g. ACC 1201:
  "Pre-requisite of ACC 1101 AND pre/co-requisite of MAT 1275 are required."
  Course pages also show the Pathways (CUNY core) category.
- Programs have a CIP code (Accounting AAS = 52.0302); their `socCodes` field is
  empty. To link careers → programs: RIASEC → O\*NET occupations → SOC → CIP, using the
  NCES CIP-SOC crosswalk.
- Money rules to respect: for TAP, the 12 credits that make a student full-time must
  count toward their degree. CUNY core courses keep counting as core at any CUNY college.

## Your steps

### Step 1: run the scraper on the real site

```bash
cd server/scraper
uv sync
uv run playwright install chromium
uv run pytest            # should pass
uv run scrape.py         # program list + AC-AAS, ACP-BS, APM-BS
uv run show.py AC-AAS
```

It was only tested against a fake site, so expect small fixes. Check:
- `meta.json` warnings are empty; ~161 programs; ~5,286 courses.
- AC-AAS major requirements include ACC 1101, ACC 1201, ... MAT 1375, CST 2206.
- ACC 1201 `prereqText` matches the sentence above.
- Look at real `raw/` data for shapes the transform guessed at: the "Overall
  Requirements" rules (credit minimums), degree-map semester names, course-set format.

If something breaks: run with `--headed` to watch, fix `scrape.py` / `transform.py`,
rebuild with `uv run scrape.py --offline`, and add a test using a small trimmed real
sample. Report the results in a few lines before moving on.

### Step 2: turn prerequisite sentences into rules

Add a parser (code first, e.g. `server/scraper/prereqs.py`) that turns `prereqText`
into a structure like:

```json
{"all": [{"course": "ACC 1101"}, {"course": "MAT 1275", "coreqOk": true}]}
```

Support AND/OR, nesting, "pre/co-requisite", minimum grades, and non-course conditions
("departmental approval", placement), stored as text. Write sentences it can't parse
to a review file for a human. Test with real sentences from the data. Gemma may help
with leftovers **offline**, with a human check. Don't parse at runtime.

### Step 3: the planner (plain functions + tests, no web code)

- `remaining(program, completed)`: which requirement rules are still open
- `eligible(program, completed)`: courses whose prerequisites are met
- `next_semester(program, completed, target_credits)`: follow the degree-map order,
  fill to the target, and say which slot each course fills
- `full_time(plan)`: at least **12 credits that count toward the major**
- `graduation_estimate(program, completed, credits_per_term)`: e.g. 60 credits at
  12/term = 5 terms, at 15/term = 4 terms
- `explore(program, completed, other_program_or_career)`: courses that fill an open
  slot in the current major **and** count toward the other major
- Settings: `FULL_TIME_MIN = 12`, `DEFAULT_TARGET = 15`, `MAX_CREDITS = TODO`
  (confirm City Tech's per-term limit in the catalog's academic policies)
- Respect minimum grades (e.g. "C or higher" for ACC 1101 to progress)

### Step 4: the back end (after the person confirms the language)

Load the JSON into dictionaries at startup, then expose:

| Endpoint | Returns |
|---|---|
| `GET /api/programs` | All programs (code, name, degree, CIP), with search |
| `GET /api/programs/{code}` | Requirements with course codes and titles filled in |
| `GET /api/courses/{code}` | One course, with prerequisites |
| `POST /api/plan` | Body: major, finished courses (+grades), credit target, optional second major. Returns next semester, full-time yes/no, graduation estimate, explore picks. |

Allow the Vite dev server (`http://localhost:5173`) via CORS or a Vite `/api` proxy.
Add endpoint tests.

### Step 5: keep the docs true

Update `docs/DECISIONS.md` (Python scraper, JSON snapshot, back-end language),
`docs/ARCHITECTURE.md`, `docs/DEGREE_DATA.md` (real data shapes), and the root
`AGENTS.md` paths. Add `server/AGENTS.md` commands for the back end once it exists.

## Open questions to ask the person when they come up

- Back-end language (Python recommended)
- City Tech's maximum credits per semester
- Which catalog year a student follows (the one they started in)
- Repeated courses and transfer credits: which grade counts