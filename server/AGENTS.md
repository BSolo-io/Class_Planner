# server/ — rules for AI assistants

Read the root `AGENTS.md` first. This file adds rules for the `server/` folder only.

## What's here

```
scraper/                     Python: copies the public City Tech catalog into JSON
data/citytech/<term>/        the JSON snapshot the app reads (raw/ is not committed)
src/                         app server code (not set up yet)
```

## Scraper commands (run inside server/scraper)

```bash
uv sync                              # first time only
uv run playwright install chromium   # first time only
uv run scrape.py                     # program list + 3 sample programs
uv run show.py AC-AAS                # print one program to check it
uv run pytest                        # tests (includes a run against a fake site)
```

## Rules

1. **Never hit the catalog site from app code.** The app reads the JSON snapshot only.
   Only the scraper talks to the site, and only at about 1 page per second or slower.
2. **Don't call the catalog's data feed (app.coursedog.com) directly** or fake
   headers to get past its login. The scraper reads public pages like a normal visitor.
3. **Change the JSON shape in `transform.py`**, then rebuild with
   `uv run scrape.py --offline`. Don't hand-edit files in `data/`.
4. Keep `transform.py` free of browser and network code so it stays easy to test.
5. Add or update a test in `scraper/tests/` for any change to `transform.py` or
   `nuxt_payload.py`, and run `uv run pytest` before finishing.
6. Program rules refer to courses by **id** (e.g. `0370271`), not code (`ACC 1201`).
   Use `course_codes.json` to translate.
