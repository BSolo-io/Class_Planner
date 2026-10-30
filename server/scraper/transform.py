"""Turn raw scraped catalog data into the slim JSON dictionaries the app uses.

Everything here is plain Python (no browser, no network), so it can be re-run
on saved raw data with `uv run scrape.py --offline` and tested easily.
"""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from urllib.parse import parse_qs, urlparse

# --------------------------------------------------------------------------- helpers

_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")
_COURSE_CODE_RE = re.compile(r"\b([A-Z]{2,5})\s*-?\s*(\d{4}[A-Z]{0,2})\b")
_NOT_SUBJECTS = {"AND", "OR", "NOT", "THE", "WITH", "FOR", "CUNY", "SUNY", "FALL", "SPRING"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def strip_html(value) -> str | None:
    """HTML → plain text, with whitespace tidied. Returns None for empty values."""
    if not isinstance(value, str):
        return None
    text = value.replace("<br>", "\n").replace("<br/>", "\n").replace("</p>", "\n")
    text = html.unescape(_TAG_RE.sub(" ", text))
    lines = [_SPACE_RE.sub(" ", line).strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)
    return text or None


def extract_course_codes(text: str | None) -> list[str]:
    """Find course codes like 'ACC 1101' or 'MAT-1275' in free text, in order, no repeats."""
    found: list[str] = []
    for match in _COURSE_CODE_RE.finditer(text or ""):
        subject, number = match.group(1), match.group(2)
        if subject in _NOT_SUBJECTS:
            continue
        code = f"{subject} {number}"
        if code not in found:
            found.append(code)
    return found


def query_param(url: str, name: str) -> str | None:
    values = parse_qs(urlparse(url).query).get(name)
    return values[0] if values else None


def program_code_from_href(href: str | None) -> str | None:
    """'/programs/AC-AAS' or a full URL → 'AC-AAS'. Returns None for other links."""
    if not href:
        return None
    parts = [p for p in urlparse(href).path.split("/") if p]
    if len(parts) >= 2 and parts[0] == "programs":
        return parts[1]
    return None


def department_ids(value) -> list[str]:
    """Departments come as ['BUS-NYT'] or as objects; always return a list of ids."""
    out: list[str] = []
    for item in value or []:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            dept = item.get("id") or item.get("_id") or item.get("deptId")
            if dept:
                out.append(str(dept))
    return out


def course_id(record: dict) -> str | None:
    """The id that program rules use to point at a course (e.g. '0370271')."""
    if record.get("courseGroupId"):
        return str(record["courseGroupId"])
    raw_id = str(record.get("id") or record.get("_id") or "")
    return raw_id.split("-")[0] or None


def _id_list(items) -> list[str]:
    out: list[str] = []
    for item in items or []:
        if isinstance(item, (str, int)):
            out.append(str(item))
        elif isinstance(item, dict):
            value = item.get("id") or item.get("value") or item.get("courseGroupId")
            if value:
                out.append(str(value))
    return out


# --------------------------------------------------------------------------- raw API data


def parse_course_records(data) -> list[dict]:
    """A captured courses response → list of course records."""
    if isinstance(data, dict) and isinstance(data.get("data"), list):
        return [r for r in data["data"] if isinstance(r, dict)]
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    return []


def merge_course_records(*record_lists: list[dict]) -> list[dict]:
    """Merge several course lists (e.g. a short and a full one); later fields win."""
    merged: dict[str, dict] = {}
    for records in record_lists:
        for record in records:
            key = str(record.get("id") or record.get("_id") or course_id(record))
            merged.setdefault(key, {}).update(record)
    return list(merged.values())


def parse_course_sets(data) -> dict[str, dict]:
    """A captured courseSets response → {courseSetGroupId: set}."""
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict) and isinstance(data.get("data"), list):
        items = data["data"]
    elif isinstance(data, dict):
        items = [v for v in data.values() if isinstance(v, dict)]
    else:
        items = []
    out: dict[str, dict] = {}
    for item in items:
        if isinstance(item, dict):
            key = item.get("courseSetGroupId") or item.get("id") or item.get("_id")
            if key:
                out[str(key)] = item
    return out


def slim_list_item(item: dict) -> dict:
    """Program info from the program list page's data."""
    return {
        "name": item.get("catalogDisplayName") or item.get("longName"),
        "longName": item.get("longName"),
        "degree": item.get("degreeDesignation"),
        "cip": item.get("cipCode"),
        "type": item.get("type"),
        "level": item.get("level"),
        "description": strip_html(item.get("catalogDescription")),
    }


# --------------------------------------------------------------------------- course pages

# Which labels on a course page we care about, matched by how the line starts.
_COURSE_PAGE_LABELS = [
    ("prerequisite", "prereq"),  # "Prerequisites & Corequisites"
    ("pathways category", "pathways"),
    ("is this a liberal arts", "liberalArts"),
    ("is this course always writing intensive", "writingIntensive"),
    ("course title", "title"),
    ("description", "description"),
    ("credit hours", "creditHours"),
    ("academic progress units", "progressUnits"),
    ("components", "components"),
    ("course schedule", "_tab"),
    ("dependencies", "_tab"),
    ("general", "_tab"),
]


def _label_key(line: str) -> str | None:
    lower = line.strip().lower()
    for prefix, key in _COURSE_PAGE_LABELS:
        if lower == prefix or (lower.startswith(prefix) and len(lower) < 60 and prefix != "general"):
            return key
    return None


def parse_course_page(text: str | None) -> dict[str, str]:
    """Course page text → {'prereq': ..., 'pathways': ..., ...} using the page's labels."""
    fields: dict[str, list[str]] = {}
    current: str | None = None
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        key = _label_key(line)
        if key:
            current = key
            fields.setdefault(key, [])
            continue
        if current and current != "_tab":
            fields[current].append(line)
    return {k: "\n".join(v).strip() for k, v in fields.items() if k != "_tab" and "\n".join(v).strip()}


def _yes_no(value: str | None) -> bool | None:
    if not value:
        return None
    first = value.strip().lower()
    if first.startswith("yes"):
        return True
    if first.startswith("no"):
        return False
    return None


# --------------------------------------------------------------------------- programs


def simplify_rule(rule: dict) -> dict:
    """One requirement rule → a small, readable dict. Unknown details go in 'extra'."""
    out: dict = {}
    if rule.get("name"):
        out["name"] = rule["name"]
    if rule.get("condition"):
        out["condition"] = rule["condition"]
    if rule.get("restriction") not in (None, ""):
        out["count"] = rule["restriction"]

    value = rule.get("value")
    if isinstance(value, dict):
        kind = value.get("condition")
        ids: list[str] = []
        for entry in value.get("values") or []:
            inner = entry.get("value") if isinstance(entry, dict) else entry
            if isinstance(inner, list):
                ids.extend(str(x) for x in inner)
            elif inner not in (None, ""):
                ids.append(str(inner))
        if kind == "courses":
            out["courses"] = ids
        elif kind == "courseSets":
            out["courseSets"] = ids
        else:
            if kind:
                out["valueType"] = kind
            if ids:
                out["values"] = ids
            extra = {
                k: v
                for k, v in value.items()
                if k not in ("condition", "values", "id", "subSelections") and v not in (None, "", [], {})
            }
            if extra:
                out.setdefault("extra", {}).update(extra)
    elif value not in (None, "", [], {}):
        out["value"] = value

    notes = strip_html(rule.get("notes"))
    if notes:
        out["notes"] = notes

    known = {"id", "name", "condition", "restriction", "value", "notes", "subRules", "showInCatalog"}
    for key, val in rule.items():
        if key not in known and isinstance(val, (str, int, float, bool)) and val not in ("", None):
            out.setdefault("extra", {})[key] = val

    children = [simplify_rule(r) for r in rule.get("subRules") or [] if isinstance(r, dict)]
    if children:
        out["rules"] = children
    return out


def simplify_requirements(program: dict) -> list[dict]:
    requisites = program.get("requisites") or {}
    groups = requisites.get("requisitesSimple") if isinstance(requisites, dict) else None
    out: list[dict] = []
    for group in groups or []:
        if not isinstance(group, dict):
            continue
        item = {
            "name": group.get("name"),
            "type": group.get("type"),
            "rules": [simplify_rule(r) for r in group.get("rules") or [] if isinstance(r, dict)],
        }
        notes = strip_html(group.get("notes"))
        if notes:
            item["notes"] = notes
        out.append(item)
    return out


def simplify_degree_maps(maps) -> list[dict]:
    out: list[dict] = []
    for degree_map in maps or []:
        if not isinstance(degree_map, dict):
            continue
        semesters = []
        for index, semester in enumerate(degree_map.get("semesters") or []):
            if not isinstance(semester, dict):
                continue
            slots = []
            for requirement in semester.get("requirements") or []:
                if not isinstance(requirement, dict):
                    continue
                options = [
                    {"type": sel.get("type") or "courses", "id": str(sel["value"])}
                    for sel in requirement.get("requirementSelect") or []
                    if isinstance(sel, dict) and sel.get("value")
                ]
                slot: dict = {"options": options}
                for src, dst in (
                    ("minimumGrade", "minGrade"),
                    ("minimumGpa", "minGpa"),
                    ("name", "name"),
                    ("area", "area"),
                    ("courseRequirementGroupFreeText", "text"),
                    ("notes", "notes"),
                ):
                    val = requirement.get(src)
                    val = strip_html(val) if isinstance(val, str) else val
                    if val not in (None, "", [], {}):
                        slot[dst] = val
                slots.append(slot)
            name = semester.get("name") or semester.get("semesterName") or semester.get("title")
            entry = {"name": name or f"Semester {index + 1}", "slots": slots}
            notes = strip_html(semester.get("notes"))
            if notes:
                entry["notes"] = notes
            semesters.append(entry)
        out.append({"name": degree_map.get("degreeMapName") or degree_map.get("name") or "Degree map", "semesters": semesters})
    return out


def referenced_ids(program: dict) -> tuple[list[str], list[str]]:
    """All course ids and course-set ids a simplified program points at."""
    courses: list[str] = []
    sets: list[str] = []

    def add(target: list[str], ids):
        for i in ids or []:
            if i not in target:
                target.append(i)

    def walk(rule: dict):
        add(courses, rule.get("courses"))
        add(sets, rule.get("courseSets"))
        for child in rule.get("rules") or []:
            walk(child)

    for group in program.get("requirements") or []:
        for rule in group.get("rules") or []:
            walk(rule)
    for degree_map in program.get("degreeMaps") or []:
        for semester in degree_map.get("semesters") or []:
            for slot in semester.get("slots") or []:
                for option in slot.get("options") or []:
                    if option.get("type") == "courseSets":
                        add(sets, [option["id"]])
                    else:
                        add(courses, [option["id"]])
    return courses, sets


def build_program(code: str, list_info: dict | None, raw: dict | None, base_url: str) -> dict:
    info = list_info or {}
    program = (raw or {}).get("program") or {}
    degree = program.get("degreeDesignation") or info.get("degree") or ""
    degree_type = degree.split(" - ")[0].strip() if degree else (code.rsplit("-", 1)[-1] if "-" in code else None)
    out = {
        "code": code,
        "name": program.get("catalogDisplayName") or info.get("name") or program.get("longName") or code,
        "longName": program.get("longName") or info.get("longName"),
        "degree": degree or None,
        "degreeType": degree_type,
        "cip": program.get("cipCode") or info.get("cip"),
        "departments": department_ids(program.get("departments")),
        "type": info.get("type") or program.get("type"),
        "level": info.get("level") or program.get("level"),
        "description": info.get("description") or strip_html(program.get("catalogDescription")),
        "url": f"{base_url}/programs/{code}",
        "detailed": bool(program),
    }
    if program:
        out["effectiveStartDate"] = program.get("effectiveStartDate")
        out["about"] = (raw or {}).get("generalText")
        out["requirements"] = simplify_requirements(program)
        out["degreeMaps"] = simplify_degree_maps(program.get("degreeMaps"))
    return out


# --------------------------------------------------------------------------- courses


def build_courses(records: list[dict], base_url: str) -> dict[str, dict]:
    courses: dict[str, dict] = {}
    for record in records:
        cid = course_id(record)
        if not cid:
            continue
        effective = record.get("effectiveStartDate") or ""
        previous = courses.get(cid)
        if previous and (previous.get("_effective") or "") > effective:
            continue  # keep the newest version of a course
        custom = record.get("customFields") or {}
        hours = (record.get("credits") or {}).get("creditHours") or {}
        attributes = [str(a) for a in custom.get("catalogAttributes") or []]
        courses[cid] = {
            "id": cid,
            "code": record.get("code"),
            "subject": record.get("subjectCode"),
            "number": record.get("courseNumber"),
            "title": record.get("longName") or record.get("name"),
            "credits": {"min": hours.get("min"), "max": hours.get("max")},
            "description": strip_html(record.get("description")),
            "departments": department_ids(record.get("departments")),
            "liberalArts": custom.get("cuLibartsFlag"),
            "writingIntensive": any(a.startswith("WRIC") for a in attributes),
            "attributes": attributes,
            "url": f"{base_url}/courses/{cid}",
            "_effective": effective,
        }
    for course in courses.values():
        course.pop("_effective", None)
    return courses


def add_course_page_details(courses: dict[str, dict], pages: dict[str, dict], base_url: str) -> None:
    """Add prerequisites and CUNY core (Pathways) category from scraped course pages."""
    code_to_id = {c["code"]: cid for cid, c in courses.items() if c.get("code")}
    for cid, page in pages.items():
        fields = parse_course_page(page.get("text"))
        course = courses.setdefault(cid, {"id": cid, "url": f"{base_url}/courses/{cid}"})
        prereq = fields.get("prereq")
        if prereq and prereq.strip().lower() in ("none", "n/a", "-", "no"):
            prereq = None
        codes = extract_course_codes(prereq)
        course["prereqText"] = prereq
        course["prereqCodes"] = [c for c in codes if c in code_to_id]
        course["prereqIds"] = [code_to_id[c] for c in codes if c in code_to_id]
        unknown = [c for c in codes if c not in code_to_id]
        if unknown:
            course["prereqUnknownCodes"] = unknown
        course["hasCoreq"] = bool(prereq and re.search(r"co-?\s?requisite", prereq, re.IGNORECASE))
        if fields.get("pathways"):
            course["pathwaysCategory"] = fields["pathways"]
        if course.get("liberalArts") is None:
            course["liberalArts"] = _yes_no(fields.get("liberalArts"))
        course["detailScraped"] = True


# --------------------------------------------------------------------------- course sets


def build_course_sets(raw_sets: dict[str, dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for gid, item in raw_sets.items():
        ids = item.get("dynamicCourseList") or item.get("courseList") or item.get("courses") or []
        out[gid] = {"id": gid, "name": item.get("name") or item.get("description"), "courseIds": _id_list(ids)}
    return out


# --------------------------------------------------------------------------- everything


def build_outputs(raw: dict, base_url: str, term: str) -> dict[str, object]:
    """raw = {'program_list', 'programs', 'courses', 'course_sets', 'course_pages'} → files to write."""
    program_list = raw.get("program_list") or {"codes": [], "meta": {}}
    raw_programs: dict[str, dict] = raw.get("programs") or {}

    codes = list(program_list.get("codes") or [])
    for code in raw_programs:
        if code not in codes:
            codes.append(code)
    programs = {
        code: build_program(code, (program_list.get("meta") or {}).get(code), raw_programs.get(code), base_url)
        for code in codes
    }

    courses = build_courses(raw.get("courses") or [], base_url)
    add_course_page_details(courses, raw.get("course_pages") or {}, base_url)
    course_codes = {c["code"]: cid for cid, c in sorted(courses.items()) if c.get("code")}
    course_sets = build_course_sets(raw.get("course_sets") or {})

    warnings: list[str] = []
    for code, program in programs.items():
        if not program["detailed"]:
            continue
        course_ids, set_ids = referenced_ids(program)
        missing_courses = [i for i in course_ids if i not in courses]
        missing_sets = [i for i in set_ids if i not in course_sets]
        if missing_courses:
            warnings.append(f"{code}: {len(missing_courses)} course id(s) not in the course list: {missing_courses[:5]}")
        if missing_sets:
            warnings.append(f"{code}: course list(s) not captured: {missing_sets}")

    meta = {
        "school": "New York City College of Technology (CUNY)",
        "source": base_url,
        "term": term,
        "catalogId": program_list.get("catalogId"),
        "builtAt": now_iso(),
        "counts": {
            "programs": len(programs),
            "programsDetailed": sum(1 for p in programs.values() if p["detailed"]),
            "courses": len(courses),
            "coursesWithPageDetails": sum(1 for c in courses.values() if c.get("detailScraped")),
            "courseSets": len(course_sets),
        },
        "detailedPrograms": [c for c, p in programs.items() if p["detailed"]],
        "warnings": warnings,
        "notes": [
            "prereqText is copied from each course page. prereqCodes lists every course code it mentions;"
            " it does not yet say which are AND / OR or co-requisites. Parse that in a later step.",
            "Data belongs to City Tech. Re-scrape at most once per term.",
        ],
    }
    return {
        "programs.json": programs,
        "courses.json": courses,
        "course_codes.json": course_codes,
        "course_sets.json": course_sets,
        "meta.json": meta,
    }
