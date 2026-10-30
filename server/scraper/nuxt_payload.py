"""Decode Nuxt page data (the `__NUXT_DATA__` script tag) into plain Python objects.

The City Tech catalog is a Nuxt website. Each page embeds its data as one flat
JSON array (the "devalue" format): objects and lists don't hold values directly,
they hold *positions* in that array. `decode()` follows those positions and
rebuilds normal dicts and lists.
"""

from __future__ import annotations

import math
import sys

# Vue/Nuxt wrapper types: keep only the value inside.
_WRAPPERS = {
    "Reactive",
    "ShallowReactive",
    "Ref",
    "ShallowRef",
    "EmptyRef",
    "EmptyShallowRef",
    "NuxtError",
    "Island",
}

# Negative positions are special values in devalue.
_SPECIAL = {
    -1: None,  # undefined
    -2: None,  # hole in an array
    -3: math.nan,
    -4: math.inf,
    -5: -math.inf,
    -6: -0.0,
}


def decode(raw: list):
    """Turn a devalue array (already parsed with json.loads) into Python objects."""
    if not isinstance(raw, list) or not raw:
        raise ValueError("This is not a Nuxt payload (expected a non-empty JSON array).")

    sys.setrecursionlimit(max(sys.getrecursionlimit(), 20000))
    memo: dict[int, object] = {}

    def rev(i):
        if isinstance(i, bool) or not isinstance(i, int):
            return i
        if i < 0:
            return _SPECIAL.get(i)
        if i in memo:
            return memo[i]
        value = raw[i]

        if isinstance(value, list):
            # A list that starts with a string is a tagged type, e.g. ["Date", "2026-01-01"].
            if value and isinstance(value[0], str):
                tag = value[0]
                if tag in _WRAPPERS:
                    result = rev(value[1]) if len(value) > 1 else None
                    memo[i] = result
                    return result
                if tag in ("Date", "RegExp", "URL"):
                    memo[i] = value[1] if len(value) > 1 else None
                    return memo[i]
                if tag == "BigInt":
                    memo[i] = int(value[1])
                    return memo[i]
                if tag == "Set":
                    out_list: list = []
                    memo[i] = out_list
                    out_list.extend(rev(x) for x in value[1:])
                    return out_list
                if tag in ("Map", "null"):
                    out_map: dict = {}
                    memo[i] = out_map
                    pairs = value[1:]
                    for k, v in zip(pairs[0::2], pairs[1::2]):
                        key = rev(k) if tag == "Map" else k
                        out_map[str(key)] = rev(v)
                    return out_map
            out_arr: list = []
            memo[i] = out_arr
            out_arr.extend(rev(x) for x in value)
            return out_arr

        if isinstance(value, dict):
            out_obj: dict = {}
            memo[i] = out_obj
            for key, idx in value.items():
                out_obj[key] = rev(idx)
            return out_obj

        memo[i] = value
        return value

    return rev(0)


def to_plain(obj, _seen: set[int] | None = None):
    """Deep-copy into JSON-safe data. Repeated references are copied; loops become None."""
    if _seen is None:
        _seen = set()
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if isinstance(obj, (dict, list)):
        if id(obj) in _seen:
            return None
        _seen.add(id(obj))
        try:
            if isinstance(obj, dict):
                return {str(k): to_plain(v, _seen) for k, v in obj.items()}
            return [to_plain(v, _seen) for v in obj]
        finally:
            _seen.discard(id(obj))
    return obj


def find_program(root, code: str | None = None) -> dict | None:
    """Find the program record inside a decoded catalog page payload."""
    data = root.get("data") if isinstance(root, dict) else None
    if not isinstance(data, dict):
        return None
    entries = [v for k, v in data.items() if k.startswith("program-") and isinstance(v, dict)]
    programs = [e["program"] for e in entries if isinstance(e.get("program"), dict)]
    for program in programs:
        if code is None or program.get("code") == code:
            return program
    return programs[0] if programs else None
