import transform
from sample_data import ACC_1201_PAGE, COURSE_SETS, COURSES, PROGRAM, PROGRAM_LIST, simple_course_page

BASE = "https://citytech.catalog.cuny.edu"


def test_strip_html():
    assert transform.strip_html("<p>Hello&nbsp;<b>world</b></p><p>Two</p>") == "Hello world\nTwo"
    assert transform.strip_html("") is None
    assert transform.strip_html(None) is None


def test_extract_course_codes():
    text = "Pre-requisite of ACC 1101 AND pre/co-requisite of MAT 1275 are required. Or MAT-1375, or ENG 1101CO."
    assert transform.extract_course_codes(text) == ["ACC 1101", "MAT 1275", "MAT 1375", "ENG 1101CO"]
    assert transform.extract_course_codes("CUNY 2020 policy") == []


def test_program_code_from_href():
    assert transform.program_code_from_href("/programs/AC-AAS") == "AC-AAS"
    assert transform.program_code_from_href("https://x.edu/programs/APM-BS/general-aoYks") == "APM-BS"
    assert transform.program_code_from_href("/programs") is None
    assert transform.program_code_from_href("/courses/123") is None


def test_parse_course_page_real_text():
    fields = transform.parse_course_page(ACC_1201_PAGE)
    assert fields["prereq"] == "Pre-requisite of ACC 1101 AND pre/co-requisite of MAT 1275 are required."
    assert fields["pathways"] == "Regular Non-Liberal Arts"
    assert fields["liberalArts"] == "No"
    assert fields["title"] == "Principles of Accounting II"


def test_simplify_requirements_and_refs():
    program = transform.build_program("AC-AAS", None, {"program": PROGRAM, "generalText": "About"}, BASE)
    groups = program["requirements"]
    assert [g["name"] for g in groups] == [
        "General Education Required and Flexible Common Core",
        "Major Requirements",
        "Overall Requirements",
    ]
    english, math = groups[0]["rules"][0]["rules"]
    assert english == {"name": "English Composition", "condition": "completedAtLeastXOf", "count": 1, "courseSets": ["ivBZAeiOtdPN3jjTOmfk"]}
    assert math["courses"] == ["0399021"] and math["notes"] == "or higher calculus-track mathematics course"
    overall = groups[2]["rules"][0]
    assert overall["valueType"] == "credits" and overall["extra"]["credits"] == 60

    semesters = program["degreeMaps"][0]["semesters"]
    assert semesters[0]["slots"][0] == {"options": [{"type": "courses", "id": "0370261"}], "minGrade": "C"}
    assert semesters[0]["name"] == "Semester 1"

    course_ids, set_ids = transform.referenced_ids(program)
    assert course_ids == ["0399021", "0370261", "0370271"]
    assert set_ids == ["ivBZAeiOtdPN3jjTOmfk", "WQNxggwvCK6XwdDOrj5x"]
    assert program["degreeType"] == "AAS" and program["cip"] == "52.0302" and program["about"] == "About"


def test_build_outputs_end_to_end():
    raw = {
        "program_list": {
            "codes": [p["name"] for p in PROGRAM_LIST],
            "meta": {p["name"]: transform.slim_list_item(p) for p in PROGRAM_LIST},
            "catalogId": "CAT123",
        },
        "programs": {"AC-AAS": {"program": PROGRAM, "generalText": "About accounting"}},
        "courses": transform.merge_course_records(COURSES),
        "course_sets": transform.parse_course_sets(COURSE_SETS),
        "course_pages": {
            "0370271": {"text": ACC_1201_PAGE},
            "0370261": {"text": simple_course_page("ACC 1101", "Principles of Accounting I")},
        },
    }
    out = transform.build_outputs(raw, BASE, "2026-Fall")
    programs, courses, codes, sets, meta = (out[k] for k in ("programs.json", "courses.json", "course_codes.json", "course_sets.json", "meta.json"))

    assert list(programs) == ["AC-AAS", "ACP-BS", "AHVC-MIN"]
    assert programs["ACP-BS"]["detailed"] is False and programs["ACP-BS"]["cip"] == "14.1201"
    assert programs["AHVC-MIN"]["degreeType"] == "MIN"

    acc = courses["0370271"]
    assert acc["title"] == "Principles of Accounting II"  # newest version wins
    assert acc["prereqCodes"] == ["ACC 1101", "MAT 1275"]
    assert acc["prereqIds"] == ["0370261", "0399011"]
    assert acc["hasCoreq"] is True and acc["pathwaysCategory"] == "Regular Non-Liberal Arts"
    assert courses["0370261"]["prereqText"] is None and courses["0370261"]["prereqCodes"] == []
    assert courses["0383531"]["writingIntensive"] is True  # id taken from "0383531-2025-01-01"

    assert codes["ACC 1201"] == "0370271"
    assert sets["WQNxggwvCK6XwdDOrj5x"] == {"id": "WQNxggwvCK6XwdDOrj5x", "name": "Flexible Core Scientific World", "courseIds": ["0399011", "0383531"]}
    assert meta["catalogId"] == "CAT123" and meta["counts"]["programsDetailed"] == 1
    assert meta["warnings"] == []


def test_warnings_for_missing_data():
    raw = {"programs": {"AC-AAS": {"program": PROGRAM}}, "courses": [], "course_sets": {}, "course_pages": {}}
    meta = transform.build_outputs(raw, BASE, "t")["meta.json"]
    assert any("not in the course list" in w for w in meta["warnings"])
    assert any("course list(s) not captured" in w for w in meta["warnings"])
