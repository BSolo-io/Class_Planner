# AGENTS.md — Class Planner

The shared rulebook for every AI coding assistant in this repo (Claude Code, Cursor,
Copilot, Codex, Gemini and others). Humans: read it too.

## What we're building

A web app that helps students:

1. **Find a career they actually like** through a short, calm, fun quiz.
2. **Follow a degree tracker** that plans classes in the right order
   (degree requirements, prerequisites, core classes).
3. **Skip ahead if already enrolled:** students with 1+ semester done can take the quiz
   or upload a transcript and get a suggested path from Gemma 4.

Full details: [docs/PRODUCT.md](docs/PRODUCT.md)

## Stack

- React + Vite, **JavaScript** (no TypeScript)
- Linter: Oxlint
- AI: Gemma 4 (`gemma4:12b`) running **locally** in Ollama at `http://localhost:11434`
- Node 22+, npm

## Commands

```bash
npm install              # install dependencies
npm run dev              # run the app at http://localhost:5173
npm run lint             # check code with Oxlint
npm run build            # production build (must pass before you finish)
ollama pull gemma4:12b   # one-time model download
```

- Use `npm`, not yarn or pnpm.
- Don't add a new package without saying why in your summary.

## Where things go

```
src/
  components/   reusable UI pieces
  pages/        one file per screen (Quiz, Results, Tracker, Transcript)
  lib/          plain logic: quiz scoring, prerequisite checks, Ollama client
  prompts/      Gemma prompt templates
  data/         quiz questions, careers, degrees (JSON); samples/ = fake test data
docs/           deeper guides (see Docs index below)
```

Create folders as you need them. Follow this layout.

## Hard rules

1. **Code decides, AI explains.** Prerequisite checks, credit totals and eligibility are
   plain JavaScript in `src/lib/`. Gemma only suggests, summarizes and explains. A model's
   answer is never the final word on whether a student can take a class.
2. **Transcripts stay local.** Transcript files and their contents go only to the local
   Ollama model. Never send them to a cloud AI service, analytics tool or log.
3. **No real student data in the repo.** Use fake data in `src/data/samples/`. Never commit
   real transcripts, names, emails or student IDs.
4. **Degree data is data.** Requirements and prerequisites live in JSON under
   `src/data/degrees/`. Don't hard-code them in components or prompts.
5. **Quiz tone matters.** Any question or results text follows
   [docs/QUIZ_GUIDE.md](docs/QUIZ_GUIDE.md).
6. **Prompts live in `src/prompts/`** and are listed in [docs/PROMPTS.md](docs/PROMPTS.md).
   Don't bury prompt text inside components.

## How to work

- Keep changes small: one feature or fix per branch.
- Before changing an area, read its doc in `docs/`.
- Copy the patterns in nearby files before inventing new ones.
- Ask before deleting files or rewriting large parts of the app.
- If something is unclear or a doc is missing, stop and ask. Don't guess.
- When you make a real choice (library, data shape, user flow), add a row to
  [docs/DECISIONS.md](docs/DECISIONS.md).

## Definition of done

Before saying a task is finished:

- [ ] `npm run lint` passes
- [ ] `npm run build` passes
- [ ] You ran `npm run dev` and the changed screen works
- [ ] Tests pass (once we have them)
- [ ] Your summary says **what** changed, **why**, and **how to check it**, in plain
      English. Our team has mixed experience, so write for a beginner.

## Git

- Branches: `feature/short-name` or `fix/short-name`
- Commits: short and plain, e.g. `Add quiz progress bar`
- Never commit `.env` files, `node_modules/` or real student data
- Never force-push to `main`

## Docs index

| Doc | Read it when you are... |
|---|---|
| [PRODUCT.md](docs/PRODUCT.md) | building any user-facing feature |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | adding files or services, or calling Gemma |
| [QUIZ_GUIDE.md](docs/QUIZ_GUIDE.md) | writing quiz questions or results text |
| [DEGREE_DATA.md](docs/DEGREE_DATA.md) | touching degrees, classes, prerequisites or the tracker |
| [TRANSCRIPT.md](docs/TRANSCRIPT.md) | working on transcript upload or analysis |
| [PROMPTS.md](docs/PROMPTS.md) | writing or changing a Gemma prompt |
| [DECISIONS.md](docs/DECISIONS.md) | wondering why something is the way it is |

## Keep this file healthy

- Keep it under ~150 lines. Details belong in `docs/`.
- If an AI keeps making the same mistake, add one line here to prevent it.
- Changes to this file are approved by: **TODO: owner name**
