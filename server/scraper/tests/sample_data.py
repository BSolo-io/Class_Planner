"""Small sample data shaped like what the real City Tech catalog returns (Oct 2026)."""

# --- a tiny devalue encoder, so tests can build Nuxt payloads like the real site's


class Wrap:
    """Encodes as [tag, <index of value>], e.g. ["ShallowReactive", 3]."""

    def __init__(self, tag, value):
        self.tag, self.value = tag, value


class Raw:
    """Encodes as [tag, *values] with raw values, e.g. ["Date", "2026-07-01"]."""

    def __init__(self, tag, *values):
        self.tag, self.values = tag, values


UNDEFINED = object()


def encode(value) -> list:
    out: list = []

    def add(v):
        if v is UNDEFINED:
            return -1
        index = len(out)
        out.append(None)
        if isinstance(v, Wrap):
            out[index] = [v.tag, add(v.value)]
        elif isinstance(v, Raw):
            out[index] = [v.tag, *v.values]
        elif isinstance(v, dict):
            out[index] = {k: add(x) for k, x in v.items()}
        elif isinstance(v, list):
            out[index] = [add(x) for x in v]
        else:
            out[index] = v
        return index

    add(value)
    return out


# --- catalog-shaped samples

PROGRAM = {
    "code": "AC-AAS",
    "longName": "Accounting AAS",
    "catalogDisplayName": "Accounting",
    "cipCode": "52.0302",
    "degreeDesignation": "AAS - Associate in Applied Science",
    "departments": ["BUS-NYT"],
    "effectiveStartDate": "2026-07-01",
    "careerPaths": [],
    "socCodes": [],
    "requisites": {
        "requisitesSimple": [
            {
                "id": "r6aDxf8K",
                "name": "General Education Required and Flexible Common Core",
                "type": "Completion Requirement",
                "rules": [
                    {
                        "id": "MGyrkMh8",
                        "condition": "allOf",
                        "name": "Required Common Core",
                        "subRules": [
                            {
                                "condition": "completedAtLeastXOf",
                                "value": {
                                    "condition": "courseSets",
                                    "values": [{"value": ["ivBZAeiOtdPN3jjTOmfk"], "logic": "and"}],
                                    "id": "glr96PM5",
                                    "subSelections": [],
                                },
                                "id": "DoTHV47F",
                                "name": "English Composition",
                                "restriction": 1,
                            },
                            {
                                "condition": "completedAllOf",
                                "value": {
                                    "condition": "courses",
                                    "values": [{"value": ["0399021"], "logic": "and"}],
                                    "id": "Sq7UcPDF",
                                    "subSelections": [],
                                },
                                "id": "ApUiQ9Sm",
                                "name": "Math and Quantitative Reasoning",
                                "notes": "<p>or higher calculus-track mathematics course</p>",
                            },
                        ],
                    }
                ],
            },
            {
                "id": "maj1",
                "name": "Major Requirements",
                "type": "Completion Requirement",
                "rules": [
                    {
                        "id": "m1",
                        "condition": "completedAllOf",
                        "value": {"condition": "courses", "values": [{"value": ["0370261", "0370271"], "logic": "and"}]},
                    }
                ],
            },
            {
                "id": "ovr1",
                "name": "Overall Requirements",
                "type": "Completion Requirement",
                "rules": [{"id": "o1", "condition": "minimumCredits", "value": {"condition": "credits", "values": [], "credits": 60}}],
            },
        ]
    },
    "degreeMaps": [
        {
            "degreeMapName": "Accounting",
            "semesters": [
                {
                    "requirements": [
                        {
                            "requirementSelect": [{"type": "courses", "value": "0370261", "code": ""}],
                            "id": "ZtFj7k8KUZ",
                            "sisId": "",
                            "name": "",
                            "minimumGrade": "C",
                            "minimumGpa": "",
                            "area": "",
                            "courseRequirementGroupFreeText": "",
                        },
                        {
                            "requirementSelect": [{"type": "courseSets", "value": "WQNxggwvCK6XwdDOrj5x", "code": ""}],
                            "id": "Wy8pZjIZQl",
                            "name": "",
                            "minimumGrade": "",
                            "courseRequirementGroupFreeText": "",
                        },
                    ]
                },
                {"requirements": [{"requirementSelect": [{"type": "courses", "value": "0370271"}], "id": "x", "minimumGrade": ""}]},
            ],
        }
    ],
}


def page_payload(program=PROGRAM) -> list:
    """A Nuxt payload shaped like the real requirements page."""
    root = Wrap(
        "ShallowReactive",
        {
            "data": Wrap(
                "ShallowReactive",
                {
                    f"program-{program['code']}-undefined": {
                        "program": {**program, "createdAt": Raw("Date", "2026-07-01T00:00:00.000Z")},
                        "terms": [],
                        "semesterNames": UNDEFINED,
                        "rootRevision": None,
                    }
                },
            ),
            "state": {},
            "serverRendered": True,
        },
    )
    return encode(root)


def course(group_id, code, title, credits, effective="2025-01-01", lib=False, attrs=None, with_group=True):
    subject, number = code.split(" ")
    record = {
        "_id": f"{group_id}-{effective}",
        "id": f"{group_id}-{effective}",
        "code": code,
        "subjectCode": subject,
        "courseNumber": number,
        "longName": title,
        "credits": {"creditHours": {"min": credits, "max": credits, "operator": ""}},
        "customFields": {"cuLibartsFlag": lib, "catalogAttributes": attrs or []},
        "departments": ["BUS-NYT"],
        "description": f"<p>About {title}.</p>",
        "effectiveStartDate": effective,
    }
    if with_group:
        record["courseGroupId"] = group_id
    return record


COURSES = [
    course("0370261", "ACC 1101", "Principles of Accounting I", 4),
    course("0370271", "ACC 1201", "Principles of Accounting II (old title)", 4, effective="2009-01-01"),
    course("0370271", "ACC 1201", "Principles of Accounting II", 4, effective="2025-01-01"),
    course("0399021", "MAT 1375", "Precalculus", 4, lib=True),
    course("0399011", "MAT 1275", "College Algebra and Trigonometry", 4, lib=True),
    course("0383531", "ECON 1401", "Microeconomics", 3, lib=True, attrs=["WRIC - WRIC (Writing Intensive)"], with_group=False),
    course("0300001", "ENG 1101", "English Composition I", 3, lib=True),
]

COURSE_SETS = [
    {
        "_id": "GQC8ygA7xGUDwYRmPRF3",
        "id": "GQC8ygA7xGUDwYRmPRF3",
        "courseSetGroupId": "ivBZAeiOtdPN3jjTOmfk",
        "name": "Required Core English Composition",
        "dynamicCourseList": ["0300001"],
    },
    {
        "_id": "PPealERsYDhhCFcRhqVL",
        "id": "PPealERsYDhhCFcRhqVL",
        "courseSetGroupId": "WQNxggwvCK6XwdDOrj5x",
        "name": "Flexible Core Scientific World",
        "dynamicCourseList": ["0399011", "0383531"],
    },
]

PROGRAM_LIST = [
    {"name": "AC-AAS", "catalogDisplayName": "Accounting", "longName": "Accounting AAS",
     "degreeDesignation": "AAS - Associate in Applied Science", "cipCode": "52.0302", "type": "Major", "level": "Undergraduate"},
    {"name": "ACP-BS", "catalogDisplayName": "Applied Computational Physics", "longName": "Applied Computational Physics BS",
     "degreeDesignation": "BS - Bachelor of Science", "cipCode": "14.1201", "type": "Major", "level": "Undergraduate"},
    {"name": "AHVC-MIN", "catalogDisplayName": "Art History", "longName": "Art History Minor",
     "degreeDesignation": "", "cipCode": "50.0703", "type": "Minor", "level": "Undergraduate"},
]

# Text of the real ACC 1201 course page, as the browser reads it.
ACC_1201_PAGE = """ACC 1201
Download as PDF
ACC 1201 - Principles of Accounting II (4 cr)
BusinessPROF - School of Professional Studies
General
Course Schedule
Dependencies
Course Title
Principles of Accounting II
Description
"The accounting cycle, including a practice set; payroll accounting."
Prerequisites & Corequisites
Pre-requisite of ACC 1101 AND pre/co-requisite of MAT 1275 are required.
Is this a liberal arts and sciences course?
No
Is this course always writing intensive?
No
Pathways Category
Regular Non-Liberal Arts
Credit Hours
Minimum
4
Max
4
Academic Progress Units
4
Components
Name
Laboratory
Name
Lecture"""


def simple_course_page(code, title, prereq="None", pathways="Regular Non-Liberal Arts"):
    return (
        f"{code}\nDownload as PDF\n{code} - {title}\nGeneral\nCourse Schedule\nDependencies\n"
        f"Course Title\n{title}\nDescription\nAbout {title}.\nPrerequisites & Corequisites\n{prereq}\n"
        f"Pathways Category\n{pathways}\nCredit Hours\nMinimum\n3\nMax\n3"
    )
