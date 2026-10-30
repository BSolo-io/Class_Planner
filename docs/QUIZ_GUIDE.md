# Quiz guide

The quiz has one job: get students to **finish** it with honest answers. Boring
questions lose attention, and lost attention means bad results.

## The model: RIASEC (Holland codes)

Every question measures one of six interest types. Use these friendly names in the UI:

| Code | Type | Friendly name | Enjoys... |
|---|---|---|---|
| R | Realistic | The Doer | hands-on work, tools, building, being outdoors |
| I | Investigative | The Thinker | puzzles, research, science, figuring out why |
| A | Artistic | The Creator | design, writing, music, self-expression |
| S | Social | The Helper | teaching, caring, coaching, supporting people |
| E | Enterprising | The Persuader | leading, pitching, selling, starting things |
| C | Conventional | The Organizer | order, data, details, clear systems |

Careers have RIASEC codes in O\*NET data, so our results can link to real occupations.

**Important:** we write our own questions. That makes this an *exploration* tool, not the
validated O\*NET assessment. In the UI, say "explore" or "your interests point toward...",
never "the test proves..."

## Format rules

- **30 questions max**, 5 per type, so the types stay balanced
- One question per screen, with a progress bar
- Answer scale (5 points): Love it · Like it · Not sure · Not for me · No way
- Students can go back, pause and resume. No timers.
- Every ~8 questions, show a short encouraging break line
  ("Halfway there. Your brain deserves a snack.")

## Writing rules

1. **Ask about activities, not jobs or skills.**
   ✅ "Would you enjoy fixing a wobbly table so it never wobbles again?"
   ❌ "Do you want to be a carpenter?" (job title)
   ❌ "Are you good with tools?" (skill, not interest)
2. **Short:** under 20 words, about an 8th-grade reading level.
3. **Concrete:** a small, specific scene beats a vague category.
   ❌ "Do you like science?"
4. **Light humor:** joke about situations, never about people or groups.
5. **No stereotypes** about gender, race, culture, money, ability, or any career or major.
6. **No pressure.** ❌ "Ready to stop wasting time and pick a real career?"
7. **Don't assume** money, family situation, hobbies or background.
8. **Skip niche pop-culture references.** They age fast and leave people out.

## Good examples (one per type)

- **R:** Would you enjoy fixing a wobbly table so it never wobbles again?
- **I:** Would you enjoy figuring out, with actual science, why your plant keeps dying?
- **A:** Would you enjoy designing a poster that makes people stop and look?
- **S:** Would you enjoy helping a friend finally "get" a tricky math problem?
- **E:** Would you enjoy pitching an idea and getting everyone excited about it?
- **C:** Would you enjoy turning a chaotic group-chat plan into a clear schedule?

## Question data format

`src/data/quiz/questions.json`:

```json
[
  {
    "id": "q01",
    "type": "R",
    "text": "Would you enjoy fixing a wobbly table so it never wobbles again?"
  }
]
```

## Scoring (in code, not AI)

- Answers map to 0–4 points (No way = 0 … Love it = 4), summed per type in `src/lib/riasec.js`.
- The top 3 types form the student's code (e.g. "SAI").
- Ties: show both types and treat them as equal.
- Gemma **does not** score. It only writes the friendly results summary
  (see [PROMPTS.md](PROMPTS.md)).

## Results screen

- Top 3 types with friendly names and a one-line description each
- 5–10 matching careers, each with a short "why it fits"
- "Does this feel right?" → **Yes** / **Not quite**
- Framing: a starting point, not a verdict

## Using AI to write questions

Allowed. But a human checks every question against this guide before it goes into
`questions.json`.

## Attribution

If we use O\*NET data (career lists, RIASEC codes), follow the license and attribution
rules on the O\*NET website. TODO: add the exact attribution line once chosen.
