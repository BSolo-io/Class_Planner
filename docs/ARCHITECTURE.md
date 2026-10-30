# Architecture

## Today

- **Front end:** React + Vite, JavaScript, Oxlint
- **AI:** Gemma 4 12B (`gemma4:12b`) running locally in Ollama
- **Back end:** none yet (see Open decisions)
- **Data:** JSON files in `src/data/`

## Folder layout

```
src/
  components/        reusable UI (Button, ProgressBar, CourseCard...)
  pages/             Welcome, Quiz, Results, Tracker, Transcript
  lib/
    riasec.js        quiz scoring (pure functions)
    careers.js       match interest code → careers
    prereqs.js       prerequisite checks + semester planning (pure functions)
    ollama.js        the only file that talks to Ollama
  prompts/           one file per prompt (see PROMPTS.md)
  data/
    quiz/            questions.json
    careers/         careers.json
    degrees/         one JSON file per degree
    courses/         one JSON file per school
    samples/         FAKE transcripts and students for testing
```

**Rule:** files in `lib/` are plain functions with no React and no network calls, except
`ollama.js`. That keeps the important logic easy to test.

## How data flows

**Quiz:**
`questions.json` → student answers → `riasec.js` scores → top 3 types →
`careers.js` matches careers → Gemma writes a friendly summary → Results screen

**Transcript:**
upload → PDF pages turned into images → `ollama.js` sends them to Gemma with a JSON
schema → output checked in code → student reviews and edits → class codes matched
to `courses/` → `prereqs.js` builds the plan → Gemma explains the plan → Tracker

**Tracker:**
degree JSON + completed classes → `prereqs.js` → done / available / locked / suggested

## Talking to Gemma (Ollama)

- Endpoint: `POST http://localhost:11434/api/chat`
- Model: `gemma4:12b`
- **Structured output:** pass a JSON schema in the `format` field so Gemma returns
  JSON we can check.
- **Images:** send base64 images in the message's `images` array. Ollama doesn't take
  PDFs directly, so convert PDF pages to images first (e.g. with pdf.js).
- **Context size:** Ollama's default context window is much smaller than Gemma's 256K
  maximum. If long transcripts get cut off, raise `options.num_ctx`.
- **Settings:** start with Google's recommended values (temperature 1.0, top_p 0.95,
  top_k 64). If extraction is inconsistent, test a lower temperature and record the
  result in [DECISIONS.md](DECISIONS.md).
- **CORS:** Ollama allows `localhost` origins by default. If the browser blocks
  requests, set the `OLLAMA_ORIGINS` environment variable.
- **Never** send transcript data anywhere except this local endpoint.

## Open decisions

1. **Back end or not?**
   - (a) Browser calls local Ollama directly: simplest, fine for local demos.
   - (b) Small API server (Node or Python) that calls Ollama: needed before real users.
   A hosted website can't reach a student's own Ollama. To keep "transcripts stay local,"
   either the app runs on the student's machine, or we run Ollama on our own server.
2. **Where progress is saved in v1:** browser `localStorage` or a database.
3. **Testing:** add Vitest for `lib/` functions (recommended first tests: scoring and
   prerequisite checks).

Record each answer in [DECISIONS.md](DECISIONS.md).
