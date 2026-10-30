import coursesData from "../data/courses/citytech.json";

const degreeModules = import.meta.glob("../data/degrees/*.json", { eager: true });

export const COURSES = Object.fromEntries(coursesData.courses.map((course) => [course.code, course]));

export const DEGREES = Object.values(degreeModules)
  .map((mod) => mod.default ?? mod)
  .sort((a, b) => a.degree.localeCompare(b.degree));
