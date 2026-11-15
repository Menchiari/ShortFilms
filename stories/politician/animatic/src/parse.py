"""Parse screenplay.fountain (draft 7 shot-note format) into scenes and shots."""
import re

def parse(path):
    t = open(path, encoding="utf-8").read()
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    head, body = t.split("\n\n", 1)
    meta = dict(l.split(": ", 1) for l in head.strip().split("\n") if ": " in l)
    scenes = []
    for chunk in re.split(r"\n(?=\.[A-Z])", "\n" + body):
        chunk = chunk.strip()
        if not chunk.startswith("."):
            continue
        first, rest = chunk.split("\n", 1)
        m = re.match(r"\.(.*?)\s*#(S\d+)#", first)
        sc = {"id": m.group(2), "heading": m.group(1), "shots": []}
        parts = re.split(r"\[\[(.*?)\]\]", rest)
        for i in range(1, len(parts), 2):
            f = [x.strip() for x in parts[i].split("|")]
            blocks = [b.strip("\n") for b in re.split(r"\n\s*\n", parts[i + 1]) if b.strip()]
            sc["shots"].append({"id": f[0], "sec": int(f[1]), "size": f[2], "move": f[3],
                                "note": f[4], "change": f[5], "blocks": classify(blocks)})
        scenes.append(sc)
    return meta, scenes

def classify(blocks):
    out = []
    for b in blocks:
        rows = b.split("\n")
        r0 = rows[0].strip()
        if r0.startswith(">"):
            out.append(("trans", r0.lstrip("> ").strip()))
        elif len(rows) == 1 and r0.isupper() and r0.endswith("TO:"):
            out.append(("trans", r0))
        elif len(rows) > 1 and re.fullmatch(r"[A-Z][A-Z .'()0-9-]+", r0):
            paren, lines = None, []
            for r in rows[1:]:
                (lines.append(("paren", r)) if r.startswith("(") else lines.append(("line", r)))
            out.append(("dialogue", r0, lines))
        else:
            out.append(("action", " ".join(rows)))
    return out

def fmt(s):
    s = int(round(s))
    return f"{s//60}:{s%60:02d}"
