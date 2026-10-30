import json
import math

import nuxt_payload
from sample_data import PROGRAM, UNDEFINED, Raw, Wrap, encode, page_payload


def test_decode_round_trip_with_wrappers_and_specials():
    value = Wrap("ShallowReactive", {"a": 1, "b": [True, None, "x"], "d": Raw("Date", "2026-01-01"), "u": UNDEFINED})
    decoded = nuxt_payload.decode(encode(value))
    assert decoded == {"a": 1, "b": [True, None, "x"], "d": "2026-01-01", "u": None}


def test_special_negative_indexes():
    raw = [{"nan": -3, "inf": -4, "neg": -5, "undef": -1}]
    decoded = nuxt_payload.decode(raw)
    assert math.isnan(decoded["nan"]) and decoded["inf"] == math.inf and decoded["neg"] == -math.inf
    assert decoded["undef"] is None


def test_map_set_and_shared_references():
    raw = [{"m": 1, "s": 4, "x": 5, "y": 5}, ["Map", 2, 3], "key", 42, ["Set", 3], {"shared": 3}]
    decoded = nuxt_payload.decode(raw)
    assert decoded["m"] == {"key": 42}
    assert decoded["s"] == [42]
    assert decoded["x"] is decoded["y"]


def test_find_program_in_page_payload():
    payload = page_payload()
    # The real page puts the payload in a <script> tag as JSON text.
    root = nuxt_payload.decode(json.loads(json.dumps(payload)))
    program = nuxt_payload.find_program(root, "AC-AAS")
    assert program["code"] == "AC-AAS"
    assert program["requisites"]["requisitesSimple"][0]["name"] == PROGRAM["requisites"]["requisitesSimple"][0]["name"]
    assert nuxt_payload.find_program(root, "NOPE") == program  # falls back to the only program


def test_to_plain_breaks_loops():
    loop = {"a": 1}
    loop["self"] = loop
    assert nuxt_payload.to_plain(loop) == {"a": 1, "self": None}
    assert nuxt_payload.to_plain({"n": math.nan}) == {"n": None}
