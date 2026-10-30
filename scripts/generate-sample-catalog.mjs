// Generates placeholder (fake) course + degree data so the front end has
// something realistic to work with while the real scraper is blocked by the
// catalog site's bot protection (see handoff.md). Re-run after editing this
// file: `node scripts/generate-sample-catalog.mjs`.
//
// Output follows the shape documented in docs/DEGREE_DATA.md:
//   src/data/courses/citytech.json        - every course
//   src/data/degrees/<slug>-2026-2027.json - one file per degree

import { mkdirSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = dirname(dirname(fileURLToPath(import.meta.url)));
const COURSES_DIR = join(ROOT, "src/data/courses");
const DEGREES_DIR = join(ROOT, "src/data/degrees");

const SOURCE_NOTE =
  "PLACEHOLDER DATA - generated for front-end development, not the real " +
  "City Tech catalog. The real scraper (server/scraper/) is blocked by the " +
  "catalog site's bot protection; replace this once that's resolved. See handoff.md.";
const CATALOG_YEAR = "2026-2027 (placeholder)";
const SCHOOL = "New York City College of Technology (CUNY)";

const ASSOCIATE_CREDITS = 30;
const BACHELOR_CREDITS = 60;

// ---------------------------------------------------------------- courses

/** @type {Record<string, {title: string, credits: number, prereqs?: object|null, coreqs?: string[], minGrade?: string, termsOffered?: string[]}>} */
const C = {};

function course(code, title, credits, opts = {}) {
  C[code] = {
    code,
    title,
    credits,
    prereqs: opts.prereqs ?? null,
    coreqs: opts.coreqs ?? [],
    minGrade: opts.minGrade ?? null,
    termsOffered: opts.termsOffered ?? ["Fall", "Spring"],
  };
}

const allOf = (...courses) => ({ all: courses });
const anyOf = (...courses) => ({ any: courses });

// -- General education (shared by every degree) ---------------------------
course("ENG 1101", "English Composition I", 3);
course("ENG 1121", "English Composition II", 3, { prereqs: allOf("ENG 1101") });
course("COM 1330", "Speech: Oral Communication", 3);
course("MAT 1275", "College Algebra and Trigonometry", 4);
course("SCI 1101", "Introduction to the Physical World", 3);
course("HUM 1101", "Introduction to the Humanities", 3);
course("SOC 1101", "Introduction to Sociology", 3);
course("ART 1101", "Introduction to Visual Arts", 3);
course("HIS 1101", "World History Since 1500", 3);
course("ECO 1101", "Principles of Economics", 3);
course("PSY 1101", "Introduction to Psychology", 3);
const FREE_ELECTIVE_POOL = ["HUM 1101", "SOC 1101", "ART 1101", "HIS 1101", "ECO 1101", "PSY 1101", "CIS 1101", "BUS 1101"];

// -- Accounting (ACC) -------------------------------------------------------
course("ACC 1101", "Principles of Accounting I", 4);
course("ACC 1201", "Principles of Accounting II", 4, { prereqs: allOf("ACC 1101"), minGrade: "C" });
course("ACC 2101", "Intermediate Accounting I", 4, { prereqs: allOf("ACC 1201"), minGrade: "C" });
course("ACC 2201", "Intermediate Accounting II", 4, { prereqs: allOf("ACC 2101") });
course("ACC 3101", "Cost Accounting", 3, { prereqs: allOf("ACC 2101") });
course("ACC 3201", "Auditing", 3, { prereqs: allOf("ACC 2201") });
course("ACC 4101", "Advanced Accounting", 3, { prereqs: allOf("ACC 3101", "ACC 3201"), termsOffered: ["Spring"] });
course("CIS 1101", "Introduction to Computer Information Systems", 3);

// -- Business (BUS) ----------------------------------------------------------
course("BUS 1101", "Introduction to Business", 3);
course("BUS 2101", "Business Law I", 3, { prereqs: allOf("BUS 1101") });
course("BUS 2201", "Principles of Marketing", 3, { prereqs: allOf("BUS 1101") });
course("BUS 2301", "Principles of Management", 3, { prereqs: allOf("BUS 1101") });
course("BUS 3101", "Corporate Finance", 3, { prereqs: allOf("ACC 1201", "ECO 1101") });
course("BUS 3201", "Organizational Behavior", 3, { prereqs: allOf("BUS 2301") });
course("BUS 4101", "Strategic Management Capstone", 3, { prereqs: allOf("BUS 3101", "BUS 3201"), termsOffered: ["Spring"] });

// -- Computer Systems / Computer Science (CST / CSCI) ------------------------
course("CST 1101", "Introduction to Computer Systems", 3);
course("CSCI 1111", "Computer Programming I", 4, { coreqs: ["MAT 1275"] });
course("CSCI 2112", "Computer Programming II", 4, { prereqs: allOf("CSCI 1111"), minGrade: "C" });
course("CSCI 2113", "Data Structures", 4, { prereqs: allOf("CSCI 2112"), minGrade: "C" });
course("CSCI 3114", "Algorithms", 3, { prereqs: allOf("CSCI 2113") });
course("CSCI 3214", "Database Systems", 3, { prereqs: allOf("CSCI 2113") });
course("CSCI 3314", "Operating Systems", 3, { prereqs: allOf("CSCI 2113", "CST 1101") });
course("CSCI 4998", "Senior Capstone", 3, { prereqs: allOf("CSCI 3114"), termsOffered: ["Spring"] });
course("MAT 1475", "Calculus I", 4, { prereqs: allOf("MAT 1275"), minGrade: "C" });
course("MAT 2440", "Discrete Mathematics", 3, { prereqs: allOf("MAT 1275") });

// -- Electrical / Computer Engineering Technology (ELT / CET) -----------------
course("ELT 1101", "Circuit Analysis I", 4, { prereqs: allOf("MAT 1275") });
course("ELT 2101", "Digital Logic Design", 4, { prereqs: allOf("ELT 1101") });
course("ELT 3101", "Electric Circuits II", 4, { prereqs: allOf("ELT 1101") });
course("ELT 3201", "Signals and Systems", 3, { prereqs: allOf("ELT 3101", "MAT 1475") });
course("ELT 4101", "Senior Project", 3, { prereqs: allOf("ELT 3201"), termsOffered: ["Spring"] });
course("CET 2201", "Microprocessors", 3, { prereqs: allOf("ELT 2101", "CSCI 1111") });

// -- Mechanical Engineering (MEC) ---------------------------------------------
course("MEC 1101", "Engineering Drawing", 3);
course("MEC 1201", "Mechanics I: Statics", 3, { prereqs: allOf("MAT 1275") });
course("MEC 2101", "Mechanics II: Dynamics", 3, { prereqs: allOf("MEC 1201") });
course("MEC 2201", "Strength of Materials", 3, { prereqs: allOf("MEC 2101") });
course("MEC 3101", "Thermodynamics", 3, { prereqs: allOf("PHYS 1101", "MAT 1475") });
course("MEC 3201", "Fluid Mechanics", 3, { prereqs: allOf("MEC 2201") });
course("MEC 4101", "Senior Design Project", 3, { prereqs: allOf("MEC 3101", "MEC 3201"), termsOffered: ["Spring"] });
course("PHYS 1101", "General Physics I", 4, { prereqs: allOf("MAT 1275") });
course("PHYS 1201", "General Physics II", 4, { prereqs: allOf("PHYS 1101", "MAT 1475") });

// -- Applied Mathematics (MAT) -------------------------------------------------
course("MAT 1575", "Calculus II", 4, { prereqs: allOf("MAT 1475"), minGrade: "C" });
course("MAT 2675", "Calculus III", 4, { prereqs: allOf("MAT 1575") });
course("MAT 2680", "Differential Equations", 3, { prereqs: allOf("MAT 1575") });
course("MAT 3050", "Linear Algebra", 3, { prereqs: allOf("MAT 1575") });
course("MAT 3200", "Probability and Statistics", 3, { prereqs: allOf("MAT 1575") });
course("MAT 4900", "Mathematics Capstone", 3, { prereqs: allOf("MAT 3050", "MAT 3200"), termsOffered: ["Spring"] });

// -- Nursing (NUR) ---------------------------------------------------------------
course("BIO 1101", "Anatomy and Physiology I", 4);
course("BIO 1201", "Anatomy and Physiology II", 4, { prereqs: allOf("BIO 1101") });
course("CHEM 1101", "General Chemistry I", 4);
course("NUR 1101", "Foundations of Nursing", 6, { prereqs: allOf("BIO 1101", "CHEM 1101"), minGrade: "C" });
course("NUR 1201", "Adult Health Nursing I", 6, { prereqs: allOf("NUR 1101"), minGrade: "C" });
course("NUR 2101", "Adult Health Nursing II", 6, { prereqs: allOf("NUR 1201"), minGrade: "C" });
course("NUR 3101", "Community Health Nursing", 3, { prereqs: allOf("NUR 2101") });
course("NUR 4101", "Nursing Leadership and Management", 3, { prereqs: allOf("NUR 3101"), termsOffered: ["Spring"] });

// -- Communication Design (COMD) -------------------------------------------------
course("COMD 1101", "Design Fundamentals I", 3);
course("COMD 1201", "Design Fundamentals II", 3, { prereqs: allOf("COMD 1101") });
course("COMD 2101", "Typography", 3, { prereqs: allOf("COMD 1201") });
course("COMD 2201", "Digital Imaging", 3, { prereqs: allOf("COMD 1201") });
course("COMD 3101", "Branding and Identity", 3, { prereqs: allOf("COMD 2101") });
course("COMD 3201", "Web Design", 3, { prereqs: allOf("COMD 2201") });
course("COMD 4101", "Portfolio and Capstone", 3, { prereqs: allOf("COMD 3101", "COMD 3201"), termsOffered: ["Spring"] });

// -- Psychology (PSY) -----------------------------------------------------------
course("PSY 2101", "Developmental Psychology", 3, { prereqs: allOf("PSY 1101") });
course("PSY 2201", "Social Psychology", 3, { prereqs: allOf("PSY 1101") });
course("PSY 3101", "Research Methods", 4, { prereqs: allOf("PSY 1101", "MAT 1275") });
course("PSY 3201", "Abnormal Psychology", 3, { prereqs: allOf("PSY 1101") });
course("PSY 4101", "Senior Seminar", 3, { prereqs: allOf("PSY 3101"), termsOffered: ["Spring"] });

// -- Environmental Science (ENVS) ------------------------------------------------
course("ENVS 1101", "Introduction to Environmental Science", 3);
course("ENVS 2101", "Ecology", 4, { prereqs: allOf("BIO 1101") });
course("ENVS 3101", "Environmental Policy", 3, { prereqs: allOf("ENVS 1101") });
course("ENVS 3201", "Environmental Data Analysis", 3, { prereqs: allOf("ENVS 1101", "MAT 1275") });
course("ENVS 4101", "Capstone Research", 3, { prereqs: allOf("ENVS 2101", "ENVS 3201"), termsOffered: ["Spring"] });
course("CHEM 1201", "General Chemistry II", 4, { prereqs: allOf("CHEM 1101") });

// -- Architectural Technology (ARCH) ----------------------------------------------
course("ARCH 1101", "Architectural Drafting I", 3);
course("ARCH 1201", "Architectural Drafting II", 3, { prereqs: allOf("ARCH 1101") });
course("ARCH 2101", "Building Materials and Methods", 3, { prereqs: allOf("ARCH 1201") });
course("ARCH 2201", "Structures I", 3, { prereqs: anyOf("MEC 1201", "MAT 1275") });
course("ARCH 3101", "Architectural Design Studio I", 4, { prereqs: allOf("ARCH 2101") });
course("ARCH 3201", "Building Systems", 3, { prereqs: allOf("ARCH 2201") });
course("ARCH 4101", "Architectural Design Capstone", 4, { prereqs: allOf("ARCH 3101", "ARCH 3201"), termsOffered: ["Spring"] });

// -- Construction Management (CON) -------------------------------------------------
course("CON 1101", "Introduction to Construction Management", 3);
course("CON 1201", "Construction Materials", 3, { prereqs: allOf("CON 1101") });
course("CON 2101", "Construction Estimating", 3, { prereqs: allOf("CON 1201") });
course("CON 2201", "Construction Scheduling", 3, { prereqs: allOf("CON 1101") });
course("CON 3101", "Construction Law and Contracts", 3, { prereqs: anyOf("BUS 2101", "CON 2101") });
course("CON 3201", "Project Management", 3, { prereqs: allOf("CON 2101", "CON 2201") });
course("CON 4101", "Capstone Project", 3, { prereqs: allOf("CON 3101", "CON 3201"), termsOffered: ["Spring"] });

// -- Hospitality Management (HMGT) --------------------------------------------------
course("HMGT 1101", "Introduction to Hospitality Management", 3);
course("HMGT 1201", "Food and Beverage Operations", 3, { prereqs: allOf("HMGT 1101") });
course("HMGT 2101", "Lodging Operations", 3, { prereqs: allOf("HMGT 1101") });
course("HMGT 2201", "Hospitality Marketing", 3, { prereqs: allOf("HMGT 1101") });
course("HMGT 3101", "Event Planning", 3, { prereqs: allOf("HMGT 2101") });
course("HMGT 3201", "Hospitality Law", 3, { prereqs: allOf("HMGT 2101") });
course("HMGT 4101", "Hospitality Strategic Management", 3, { prereqs: allOf("HMGT 3101", "HMGT 3201"), termsOffered: ["Spring"] });

// -- Health Informatics (HIM) ------------------------------------------------------
course("HIM 1101", "Introduction to Health Informatics", 3);
course("HIM 2101", "Health Data Standards", 3, { prereqs: allOf("HIM 1101") });
course("HIM 3101", "Clinical Database Systems", 3, { prereqs: allOf("HIM 2101", "CSCI 1111") });
course("HIM 3201", "Health Information Privacy and Security", 3, { prereqs: allOf("HIM 2101") });
course("HIM 4101", "Health Informatics Capstone", 3, { prereqs: allOf("HIM 3101", "HIM 3201"), termsOffered: ["Spring"] });

// ---------------------------------------------------------------- degrees

function creditsOf(codes) {
  return codes.reduce((sum, code) => {
    if (!C[code]) throw new Error(`unknown course code: ${code}`);
    return sum + C[code].credits;
  }, 0);
}

function degree({ id, name, kind, major, science = true }) {
  const target = kind === "AAS" ? ASSOCIATE_CREDITS : BACHELOR_CREDITS;

  const groups = [
    { name: "English Composition", type: "allOf", courses: ["ENG 1101", "ENG 1121"] },
    { name: "Oral Communication", type: "allOf", courses: ["COM 1330"] },
    { name: "Math and Quantitative Reasoning", type: "allOf", courses: ["MAT 1275"] },
  ];
  if (science) groups.push({ name: "Life and Physical Sciences", type: "allOf", courses: ["SCI 1101"] });
  groups.push({ name: "Major Requirements", type: "allOf", courses: major });

  const fixed = creditsOf(["ENG 1101", "ENG 1121", "COM 1330", "MAT 1275"]) + (science ? creditsOf(["SCI 1101"]) : 0);
  const electiveCredits = target - fixed - creditsOf(major);
  if (electiveCredits < 0) {
    throw new Error(`${id}: major + required gen ed already exceeds ${target} credits by ${-electiveCredits}`);
  }
  if (electiveCredits > 0) {
    groups.push({ name: "Electives", type: "credits", credits: electiveCredits, from: FREE_ELECTIVE_POOL });
  }

  return {
    id,
    school: SCHOOL,
    degree: name,
    kind,
    catalogYear: CATALOG_YEAR,
    source: SOURCE_NOTE,
    isPlaceholder: true,
    totalCredits: target,
    groups,
  };
}

const DEGREES = [
  // -- Associate's (AAS), ~30 credits --------------------------------------
  degree({
    id: "citytech-aas-accounting",
    name: "Accounting (AAS)",
    kind: "AAS",
    major: ["ACC 1101", "ACC 1201", "BUS 1101"],
  }),
  degree({
    id: "citytech-aas-computer-systems-technology",
    name: "Computer Systems Technology (AAS)",
    kind: "AAS",
    major: ["CST 1101", "CSCI 1111", "CSCI 2112"],
  }),
  degree({
    id: "citytech-aas-mechanical-engineering-technology",
    name: "Mechanical Engineering Technology (AAS)",
    kind: "AAS",
    major: ["MEC 1101", "MEC 1201", "MEC 2101", "PHYS 1101"],
    science: false,
  }),
  degree({
    id: "citytech-aas-nursing",
    name: "Nursing (AAS)",
    kind: "AAS",
    major: ["BIO 1101", "CHEM 1101", "NUR 1101"],
    science: false,
  }),
  degree({
    id: "citytech-aas-hospitality-management",
    name: "Hospitality Management (AAS)",
    kind: "AAS",
    major: ["HMGT 1101", "HMGT 1201", "HMGT 2101"],
  }),

  // -- Bachelor's (BS/BA), ~60 credits -------------------------------------
  degree({
    id: "citytech-bs-computer-science",
    name: "Computer Science (BS)",
    kind: "BS",
    major: ["CST 1101", "CSCI 1111", "CSCI 2112", "CSCI 2113", "CSCI 3114", "MAT 1475"],
  }),
  degree({
    id: "citytech-bs-computer-engineering-technology",
    name: "Computer Engineering Technology (BS)",
    kind: "BS",
    major: ["CST 1101", "CSCI 1111", "ELT 1101", "ELT 2101", "CET 2201"],
    science: false,
  }),
  degree({
    id: "citytech-bs-electrical-engineering-technology",
    name: "Electrical Engineering Technology (BS)",
    kind: "BS",
    major: ["ELT 1101", "ELT 2101", "ELT 3101", "ELT 3201", "ELT 4101", "MAT 1475"],
    science: false,
  }),
  degree({
    id: "citytech-bs-mechanical-engineering",
    name: "Mechanical Engineering (BS)",
    kind: "BS",
    major: ["MEC 1101", "MEC 1201", "MEC 2101", "MEC 2201", "PHYS 1101", "MAT 1475"],
    science: false,
  }),
  degree({
    id: "citytech-bs-applied-mathematics",
    name: "Applied Mathematics (BS)",
    kind: "BS",
    major: ["MAT 1475", "MAT 1575", "MAT 2680", "MAT 3050", "MAT 3200"],
    science: false,
  }),
  degree({
    id: "citytech-bs-accounting",
    name: "Accounting (BS)",
    kind: "BS",
    major: ["ACC 1101", "ACC 1201", "ACC 2101", "ACC 2201", "ACC 3101", "BUS 1101"],
  }),
  degree({
    id: "citytech-bs-business-administration",
    name: "Business Administration (BS)",
    kind: "BS",
    major: ["BUS 1101", "BUS 2101", "BUS 2201", "BUS 2301", "ACC 1101", "ECO 1101"],
  }),
  degree({
    id: "citytech-bs-nursing",
    name: "Nursing (BS)",
    kind: "BS",
    major: ["BIO 1101", "CHEM 1101", "NUR 1101", "NUR 1201", "NUR 3101"],
    science: false,
  }),
  degree({
    id: "citytech-bs-communication-design",
    name: "Communication Design (BS)",
    kind: "BS",
    major: ["COMD 1101", "COMD 1201", "COMD 2101", "COMD 2201", "COMD 3101"],
  }),
  degree({
    id: "citytech-ba-psychology",
    name: "Psychology (BA)",
    kind: "BA",
    major: ["PSY 1101", "PSY 2101", "PSY 2201", "PSY 3101", "PSY 3201"],
  }),
  degree({
    id: "citytech-bs-environmental-science",
    name: "Environmental Science (BS)",
    kind: "BS",
    major: ["BIO 1101", "CHEM 1101", "ENVS 1101", "ENVS 2101", "ENVS 3101"],
    science: false,
  }),
  degree({
    id: "citytech-bs-architectural-technology",
    name: "Architectural Technology (BS)",
    kind: "BS",
    major: ["ARCH 1101", "ARCH 1201", "ARCH 2101", "ARCH 2201", "ARCH 3101"],
  }),
  degree({
    id: "citytech-bs-construction-management",
    name: "Construction Management (BS)",
    kind: "BS",
    major: ["CON 1101", "CON 1201", "CON 2101", "CON 2201", "CON 3101"],
  }),
  degree({
    id: "citytech-bs-hospitality-management",
    name: "Hospitality Management (BS)",
    kind: "BS",
    major: ["HMGT 1101", "HMGT 1201", "HMGT 2101", "HMGT 2201", "HMGT 3101"],
  }),
  degree({
    id: "citytech-bs-health-informatics",
    name: "Health Informatics (BS)",
    kind: "BS",
    major: ["HIM 1101", "HIM 2101", "HIM 3101", "HIM 3201", "BIO 1101"],
    science: false,
  }),
];

// ---------------------------------------------------------------- validate

function validate() {
  const errors = [];

  const flatten = (req) => {
    if (!req) return [];
    return (req.all ?? req.any ?? []).flatMap((i) => (typeof i === "string" ? [i] : flatten(i)));
  };

  for (const [code, c] of Object.entries(C)) {
    for (const dep of flatten(c.prereqs)) {
      if (!C[dep]) errors.push(`${code}: prereq references unknown course ${dep}`);
    }
    for (const co of c.coreqs) if (!C[co]) errors.push(`${code}: coreq references unknown course ${co}`);
  }

  const visiting = new Set();
  const done = new Set();
  function visit(code, path) {
    if (done.has(code)) return;
    if (visiting.has(code)) {
      errors.push(`prerequisite cycle: ${[...path, code].join(" -> ")}`);
      return;
    }
    visiting.add(code);
    for (const dep of flatten(C[code]?.prereqs)) visit(dep, [...path, code]);
    visiting.delete(code);
    done.add(code);
  }
  for (const code of Object.keys(C)) visit(code, []);

  for (const d of DEGREES) {
    let sum = 0;
    for (const g of d.groups) {
      const codes = g.type === "allOf" ? g.courses : g.from;
      for (const code of codes) {
        if (!C[code]) errors.push(`${d.id}: group "${g.name}" references unknown course ${code}`);
      }
      sum += g.type === "allOf" ? creditsOf(g.courses.filter((code) => C[code])) : g.credits;
    }
    if (sum !== d.totalCredits) {
      errors.push(`${d.id}: groups sum to ${sum} credits but totalCredits is ${d.totalCredits}`);
    }
  }

  if (errors.length) {
    throw new Error("sample data failed validation:\n" + errors.map((e) => "  - " + e).join("\n"));
  }
}

// ---------------------------------------------------------------- write

validate();

mkdirSync(COURSES_DIR, { recursive: true });
mkdirSync(DEGREES_DIR, { recursive: true });

const courseList = Object.values(C).sort((a, b) => a.code.localeCompare(b.code));
writeFileSync(
  join(COURSES_DIR, "citytech.json"),
  JSON.stringify(
    {
      school: SCHOOL,
      source: SOURCE_NOTE,
      isPlaceholder: true,
      catalogYear: CATALOG_YEAR,
      courses: courseList,
    },
    null,
    2,
  ) + "\n",
);

for (const d of DEGREES) {
  writeFileSync(join(DEGREES_DIR, `${d.id}-2026-2027.json`), JSON.stringify(d, null, 2) + "\n");
}

console.log(`Wrote ${courseList.length} courses to src/data/courses/citytech.json`);
console.log(`Wrote ${DEGREES.length} degrees to src/data/degrees/`);
for (const d of DEGREES) {
  console.log(`  ${d.kind.padEnd(3)} ${d.totalCredits}cr  ${d.degree}`);
}
