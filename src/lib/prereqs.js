// Plain functions: no React, no network. Degree requirements and prerequisite
// rules decide what a student can take next - never an AI model.

function flatten(req) {
  if (!req) return [];
  const items = req.all ?? req.any ?? [];
  return items.flatMap((item) => (typeof item === "string" ? [item] : flatten(item)));
}

function satisfied(req, completed) {
  if (!req) return true;
  if (req.all) return req.all.every((item) => (typeof item === "string" ? completed.has(item) : satisfied(item, completed)));
  if (req.any) return req.any.some((item) => (typeof item === "string" ? completed.has(item) : satisfied(item, completed)));
  return true;
}

/** Turns free-typed course codes ("acc1101", "ENG 1101,MAT1275") into known course codes. */
export function parseCompleted(text, courses) {
  if (!text) return [];
  const codes = text
    .split(/[\n,]+/)
    .map((raw) => raw.trim().toUpperCase().replace(/^([A-Z]+)\s*(\d.*)$/, "$1 $2"))
    .filter(Boolean);
  return [...new Set(codes)].filter((code) => courses[code]);
}

/** Whether a course's prerequisites are met yet. */
export function canTake(code, completedSet, courses) {
  const course = courses[code];
  if (!course) return { ok: false, missing: [code] };
  if (completedSet.has(code)) return { ok: true, missing: [] };
  if (satisfied(course.prereqs, completedSet)) return { ok: true, missing: [] };
  return { ok: false, missing: flatten(course.prereqs).filter((dep) => !completedSet.has(dep)) };
}

/** Credits done vs. needed, per requirement group and overall. */
export function progress(degree, completedSet, courses) {
  let creditsDone = 0;
  const groups = degree.groups.map((group) => {
    const pool = group.type === "allOf" ? group.courses : group.from;
    const creditsNeeded = group.type === "allOf"
      ? pool.reduce((sum, code) => sum + (courses[code]?.credits ?? 0), 0)
      : group.credits;
    const earnedFromPool = pool
      .filter((code) => completedSet.has(code))
      .reduce((sum, code) => sum + (courses[code]?.credits ?? 0), 0);
    const creditsEarned = group.type === "allOf" ? earnedFromPool : Math.min(group.credits, earnedFromPool);
    creditsDone += creditsEarned;
    return { name: group.name, creditsEarned, creditsNeeded };
  });
  return { creditsDone, creditsNeeded: degree.totalCredits, groups };
}

/**
 * A simple (not optimal) pick for next semester: go through each requirement
 * group in order and take available, not-yet-done courses until the credit
 * cap is reached.
 */
export function nextSemester(degree, completedSet, courses, maxCredits = 15) {
  const picked = [];
  let credits = 0;
  for (const group of degree.groups) {
    const pool = group.type === "allOf" ? group.courses : group.from;
    for (const code of pool) {
      if (completedSet.has(code) || picked.some((p) => p.code === code)) continue;
      const course = courses[code];
      if (!course) continue;
      if (credits + course.credits > maxCredits && picked.length > 0) continue;
      if (!canTake(code, completedSet, courses).ok) continue;
      picked.push({ ...course, group: group.name });
      credits += course.credits;
      if (credits >= maxCredits) return { courses: picked, credits };
    }
  }
  return { courses: picked, credits };
}
