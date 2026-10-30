"""Print one program from the saved JSON in plain English, to check the scrape.

    uv run show.py AC-AAS
    uv run show.py AC-AAS --term 2026-Fall
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def load(folder: Path, name: str):
    path = folder / name
    if not path.exists():
        sys.exit(f"Missing {path}. Run  uv run scrape.py  first.")
    return json.loads(path.read_text(encoding="utf-8"))


def course_line(cid: str, courses: dict) -> str:
    course = courses.get(cid)
    if not course:
        return f"(unknown course {cid})"
    credits = course.get("credits") or {}
    cr = credits.get("min")
    if credits.get("max") not in (None, cr):
        cr = f"{cr}-{credits['max']}"
    line = f"{course.get('code')} - {course.get('title')} ({cr} cr)"
    if course.get("prereqText"):
        line += f"\n        needs: {course['prereqText']}"
    return line


def print_rule(rule: dict, courses: dict, sets: dict, depth: int) -> None:
    pad = "  " * depth
    head = rule.get("name") or rule.get("condition") or "rule"
    if rule.get("count") is not None:
        head += f"  [{rule.get('condition')}: {rule['count']}]"
    elif rule.get("condition") and rule.get("name"):
        head += f"  [{rule['condition']}]"
    print(f"{pad}- {head}")
    for cid in rule.get("courses") or []:
        print(f"{pad}    {course_line(cid, courses)}")
    for sid in rule.get("courseSets") or []:
        course_set = sets.get(sid) or {}
        count = len(course_set.get("courseIds") or [])
        print(f"{pad}    list: {course_set.get('name') or sid} ({count} course{'' if count == 1 else 's'})")
    if rule.get("notes"):
        print(f"{pad}    note: {rule['notes'][:200]}")
    for key in ("valueType", "values", "value", "extra"):
        if rule.get(key):
            print(f"{pad}    {key}: {json.dumps(rule[key])[:200]}")
    for child in rule.get("rules") or []:
        print_rule(child, courses, sets, depth + 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("code")
    parser.add_argument("--term", default="2026-Fall")
    parser.add_argument("--out", help="data folder (default: server/data/citytech/<term>)")
    args = parser.parse_args()
    folder = Path(args.out) if args.out else SCRIPT_DIR.parent / "data" / "citytech" / args.term

    programs = load(folder, "programs.json")
    courses = load(folder, "courses.json")
    sets = load(folder, "course_sets.json")
    program = programs.get(args.code)
    if not program:
        sys.exit(f"{args.code} not found. Some codes: {', '.join(list(programs)[:10])}")

    print(f"{program['code']}: {program['name']} ({program.get('degree')})")
    print(f"CIP {program.get('cip')} · departments {', '.join(program.get('departments') or [])}")
    if not program.get("detailed"):
        print("Only list info saved. Run:  uv run scrape.py --programs " + program["code"])
        return
    for group in program.get("requirements") or []:
        print(f"\n## {group.get('name')}")
        for rule in group.get("rules") or []:
            print_rule(rule, courses, sets, 0)
    for degree_map in program.get("degreeMaps") or []:
        print(f"\n## Degree map: {degree_map['name']}")
        for semester in degree_map["semesters"]:
            print(f"  {semester['name']}")
            for slot in semester["slots"]:
                names = []
                for option in slot["options"]:
                    if option["type"] == "courseSets":
                        names.append((sets.get(option["id"]) or {}).get("name") or option["id"])
                    else:
                        names.append((courses.get(option["id"]) or {}).get("code") or option["id"])
                extra = f"  (min grade {slot['minGrade']})" if slot.get("minGrade") else ""
                print(f"    - {' OR '.join(names) or slot.get('text') or '?'}{extra}")


if __name__ == "__main__":
    main()
