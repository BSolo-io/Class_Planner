# Degree data

How we store degrees, classes and prerequisites, and the rules the tracker follows.

## The big rule

**Code checks prerequisites. Gemma never does.** `src/lib/prereqs.js` decides what a
student can take. Gemma only receives the result and explains it in plain English.

## Key terms

- **Degree:** e.g. "BS Computer Science," made of requirement groups
- **Requirement group:** core, general education, major, electives. Each needs a set of
  classes or a number of credits.
- **Course:** has a code, title, credits and (optionally) prerequisites
- **Prerequisite:** must be completed *before* the course
- **Corequisite:** can be taken *before or in the same semester*
- **Catalog year:** requirements change over time. Students follow the catalog from the
  year they started.

## Files

- `src/data/courses/<school>.json`: every course at that school
- `src/data/degrees/<school>-<degree>-<catalogYear>.json`: requirements that point to
  course codes

Start with **one school and one degree**. Enter it by hand from the public course catalog.

## Course format

```json
{
  "code": "CS 201",
  "title": "Data Structures",
  "credits": 3,
  "prereqs": { "all": ["CS 101", { "any": ["MATH 120", "MATH 151"] }] },
  "coreqs": [],
  "minGrade": "C",
  "termsOffered": ["Fall", "Spring"]
}
```

**Prerequisite logic:** `all` means every item is required, `any` means one is enough.
They can be nested. The example reads: CS 101 **and** (MATH 120 **or** MATH 151).
Use `null` for no prerequisites.

## Degree format

```json
{
  "id": "example-u-bs-cs-2026",
  "school": "Example University",
  "degree": "BS Computer Science",
  "catalogYear": "2026-2027",
  "source": "https://catalog.example.edu/...",
  "totalCredits": 120,
  "groups": [
    {
      "name": "Core",
      "type": "allOf",
      "courses": ["CS 101", "CS 201", "CS 301"]
    },
    {
      "name": "Math",
      "type": "allOf",
      "courses": ["MATH 151", "MATH 152"]
    },
    {
      "name": "Electives",
      "type": "credits",
      "credits": 12,
      "from": ["CS 350", "CS 360", "CS 370", "CS 380"]
    }
  ]
}
```

Always fill in `source` and `catalogYear` so anyone can double-check the data.

## Functions in `src/lib/prereqs.js`

| Function | Returns |
|---|---|
| `canTake(courseCode, completed)` | `{ ok: true }` or `{ ok: false, missing: [...] }` |
| `availableNow(degree, completed)` | courses whose prerequisites are met |
| `lockedCourses(degree, completed)` | courses still blocked, with what's missing |
| `progress(degree, completed)` | credits done vs. needed, per group |
| `planSemesters(degree, completed, maxCredits)` | semesters in order, prerequisites first |

- `completed` is a list of `{ code, grade }`. A course counts only if the grade meets
  `minGrade`.
- If the data has a loop (A needs B, B needs A), throw a clear error. That's a data bug.
- Default credit limit per semester: 15 (TODO: confirm).

## Data checks (planned)

A script or test that confirms:

- every course code a degree references exists in the courses file
- no prerequisite loops
- group credits add up to `totalCredits` or less

## Always show

"This plan is a guide. Confirm it with your academic advisor."
