#!/usr/bin/env python3
"""Git merge driver for film.json and shotlist.json: three-way merge by structure, not by line.

  git config merge.filmjson.driver "python3 tools/jsonmerge.py %O %A %B"
  (.gitattributes: films/*/film.json merge=filmjson, films/*/shotlist.json merge=filmjson)

Objects merge key by key. Lists of objects with an "id" (scenes, shots, takes) merge by id. Other
lists (the log) keep the additions of both sides. A value changed differently on both sides is a
real conflict: exit 1, git marks the file as conflicted. Python 3 standard library only.
"""

import json
import re
import sys

NONE = object()


class Conflict(Exception):
    pass


def by_id(items):
    return isinstance(items, list) and all(isinstance(x, dict) and "id" in x for x in items)


def merge(base, ours, theirs, path):
    if ours == theirs:
        return ours
    if ours == base:
        return theirs
    if theirs == base:
        return ours
    if isinstance(ours, dict) and isinstance(theirs, dict):
        b = base if isinstance(base, dict) else {}
        out = {}
        for k in list(ours) + [k for k in theirs if k not in ours]:
            if k in ours and k in theirs:
                out[k] = merge(b.get(k, NONE), ours[k], theirs[k], path + [k])
            elif k in ours:
                if not (k in b and b[k] == ours[k]):   # kept unless the other side deleted it unchanged
                    out[k] = ours[k]
            elif not (k in b and b[k] == theirs[k]):
                out[k] = theirs[k]
        return out
    if isinstance(ours, list) and isinstance(theirs, list):
        b = base if isinstance(base, list) else []
        if by_id(ours) and by_id(theirs) and by_id(b) and (ours or theirs):
            bi = {x["id"]: x for x in b}
            oi = {x["id"]: x for x in ours}
            ti = {x["id"]: x for x in theirs}
            out = []
            for i in [x["id"] for x in ours] + [x["id"] for x in theirs if x["id"] not in oi]:
                if i in oi and i in ti:
                    out.append(merge(bi.get(i, NONE), oi[i], ti[i], path + [i]))
                elif i in oi:
                    if not (i in bi and bi[i] == oi[i]):
                        out.append(oi[i])
                elif not (i in bi and bi[i] == ti[i]):
                    out.append(ti[i])
            if all(re.fullmatch(r"T\d+", str(x["id"])) for x in out):
                out.sort(key=lambda x: int(x["id"][1:]))
            return out
        out = list(ours) + [x for x in theirs if x not in b and x not in ours]
        return [x for x in out if not (x in b and (x not in ours or x not in theirs))]
    raise Conflict("/".join(map(str, path)) or "(root)")


def main():
    o, a, b = sys.argv[1:4]
    try:
        docs = [json.load(open(p, encoding="utf-8")) for p in (o, a, b)]
    except (OSError, ValueError) as e:
        print(f"jsonmerge: cannot read JSON ({e})", file=sys.stderr)
        return 1
    try:
        result = merge(*docs, [])
    except Conflict as e:
        print(f"jsonmerge: both sides changed {e} differently", file=sys.stderr)
        return 1
    with open(a, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
