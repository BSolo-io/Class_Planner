# Transcript analysis

For students with at least one semester done. They upload a transcript, Gemma reads it,
they confirm the class list, and the tracker builds their path.

## Flow

1. Student uploads a **PDF or photo**
2. PDF pages are turned into images (e.g. with pdf.js)
3. `src/lib/ollama.js` sends the images to Gemma with the `transcript-extract` prompt
   and a JSON schema (see [PROMPTS.md](PROMPTS.md))
4. Code checks the output (rules below)
5. **The student reviews a table of classes and can fix, add or remove rows**
6. Class codes are matched to `src/data/courses/` (see [DEGREE_DATA.md](DEGREE_DATA.md))
7. `prereqs.js` builds the plan; Gemma explains it (`path-explain` prompt)

Step 5 is required. Never use extracted data the student hasn't confirmed.

## Extraction output

```json
{
  "school": "Example University",
  "terms": [
    {
      "term": "Fall 2025",
      "courses": [
        {
          "code": "MATH 151",
          "title": "Calculus I",
          "credits": 4,
          "grade": "B+",
          "status": "completed"
        }
      ]
    }
  ],
  "warnings": ["Page 2 is blurry; two grades may be wrong."]
}
```

`status` is one of: `completed`, `in_progress`, `withdrawn`, `failed`, `transfer`.

## Checks in code

- `credits` is a number from 0 to 6
- `grade` is in the allowed list (A–F with +/–, P, NP, W, I, IP, TR) or `null`
- Codes are normalized in code: `"MAT-151"`, `"math151"` → `"MATH 151"`
- Unknown course codes are **flagged for the student**, never silently dropped
- Gemma must **never invent** a course. If something is unreadable, it leaves the field
  `null` and adds a warning.

## Hard cases to test

- Multi-page transcripts
- Crooked or blurry phone photos
- Transfer credits and AP credit
- Repeated courses (use the latest or highest grade, following the school's rule)
- Pass/fail classes
- Different code formats between schools

Keep fake examples of each in `src/data/samples/`.

## Privacy rules (non-negotiable)

1. Transcripts go **only** to the local Ollama model, never to a cloud AI service.
2. Process in memory. Don't save the file after extraction unless the student chooses to.
3. Never log transcript contents, even while debugging.
4. Give the student a clear "Delete my data" button.
5. **No real transcripts in the repo, ever.** Only fake samples.

FERPA is the U.S. law that protects student education records. It mainly binds schools
and the companies working for them. If we ever partner with a school, stricter contract
rules apply. Get proper legal advice before launching with real students.

## Gemma tips

- Put images **before** the text in the prompt (Google's guidance for Gemma 4).
- Use one image per page, in order.
- Raise `num_ctx` in Ollama for long transcripts (see [ARCHITECTURE.md](ARCHITECTURE.md)).
