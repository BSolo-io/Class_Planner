# Decisions

A short log of real choices and the reason for each, so nobody (human or AI) has to guess
later. Add a row whenever you choose a library, data shape or user flow.
Don't edit old rows. If a decision changes, add a new row that replaces it.

| # | Date | Decision | Why | Who |
|---|---|---|---|---|
| 001 | 2026-10-30 | React + Vite, JavaScript | Simple setup; easier for a mixed-skill team | Team |
| 002 | 2026-10-30 | Oxlint for linting | Fast, Vite's default; enough for a small project | Team |
| 003 | 2026-10-30 | Gemma 4 12B in local Ollama | Free, private (data stays local), reads images | Team |
| 004 | 2026-10-30 | `AGENTS.md` is the one rulebook for all AI tools | The team uses different AI assistants | Team |
| 005 | 2026-10-30 | Quiz based on RIASEC (Holland codes) | Well researched; links to O\*NET occupations | Team |
| 006 | 2026-10-30 | Code checks prerequisites; AI only explains | AI can be wrong; eligibility must be exact | Team |
| 007 | 2026-10-30 | Students confirm extracted transcript data | Extraction can misread; the student is in control | Team |

## Waiting on a decision

- Back end or not (see [ARCHITECTURE.md](ARCHITECTURE.md))
- Where progress is saved in v1
- First school and degree to model
- Semester credit limit
