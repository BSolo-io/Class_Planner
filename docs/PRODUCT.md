# Product

## One line

Help students find a career they actually like, then plan the classes to get there.

## Who it's for

- **New students** who haven't picked a major, or aren't sure about the one they picked.
- **Enrolled students** (1+ semester done) who want to check they're on the right path.

## The problem we're solving

Career quizzes are usually long and boring, so students quit halfway or click randomly.
Degree requirements are confusing: prerequisites, core classes and electives are spread
across catalogs and PDFs. We fix both: a quiz people *finish*, and a tracker that shows
exactly what to take next.

## The three flows

### Flow A: New student → career → tracker

1. Welcome screen: "Have you finished at least one semester?" → **No**
2. Career quiz: short, calm, fun (see [QUIZ_GUIDE.md](QUIZ_GUIDE.md))
3. Results: top interest types + matching careers
4. "Does this feel right?"
   - **Yes** → pick a degree that leads there → Tracker
   - **Not quite** → explore other matches or retake the quiz

### Flow B: Enrolled student → transcript → tracker

1. Welcome screen: "Have you finished at least one semester?" → **Yes**
2. Choice: **Take the career quiz** (goes to Flow A) or **Share my transcript**
3. Upload transcript (PDF or photo)
4. Gemma reads it; the student **reviews and fixes** the class list (see [TRANSCRIPT.md](TRANSCRIPT.md))
5. The app compares completed classes to the degree requirements
6. Suggested path → Tracker

### Flow C: Tracker

Shows, for the chosen degree:

- **Done:** completed classes
- **Available now:** prerequisites met
- **Locked:** missing prerequisites (and which ones)
- **Suggested next semester:** a balanced list within a credit limit
- Progress by requirement group (core, general education, electives)

Rules for the tracker are in [DEGREE_DATA.md](DEGREE_DATA.md).

## Product principles

1. **Keep attention.** Short screens, progress bar, a little humor, no walls of text.
2. **Calm, never pushy.** No timers, no "wrong answers," no pressure to decide today.
3. **The student is in control.** They confirm anything the AI produces.
4. **Explain the why.** Every suggestion says why it was made.
5. **Honest limits.** Results are a starting point. Always remind students to confirm
   plans with their academic advisor.

## Not in version 1

TODO (team to confirm): user accounts and login, real school system integrations,
class registration, financial aid, multiple schools.

## How we'll know it works

- Quiz completion rate (goal: TODO %)
- Median time to finish the quiz (goal: under TODO minutes)
- % of students who answer "Yes, this feels right"
- % of transcript uploads where the student accepts the class list with few edits

## Open questions

- Which school and degree do we model first?
- Where is progress saved in v1 (browser only, or a server)?
- Do we support high school students, or college only?
