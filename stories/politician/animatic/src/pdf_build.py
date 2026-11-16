import sys, html, json
sys.path.insert(0, sys.argv[0].rsplit("/", 1)[0])
from parse import parse, fmt
src, out_html = sys.argv[1], sys.argv[2]
meta, scenes = parse(src)
E = html.escape
nshots = sum(len(s["shots"]) for s in scenes)
total = sum(sh["sec"] for s in scenes for sh in s["shots"])

def change_html(c):
    if not c: return ""
    strong = any(k in c for k in ("NEW", "merged", "restaged", "split", "angle", "cut", "now on", "close", "wide to"))
    return f'<div class="chg{" strong" if strong else ""}">{E(c)}</div>'

rows, tc = [], 0
for sc in scenes:
    sd = sum(sh["sec"] for sh in sc["shots"])
    rows.append(f'<div class="scene"><div class="l"><b>{sc["id"]}</b><span>{sd}s</span><i>{fmt(tc)}</i></div>'
                f'<div class="m">{E(sc["heading"])}</div><div class="n"></div></div>')
    for sh in sc["shots"]:
        body = []
        for b in sh["blocks"]:
            if b[0] == "action":
                body.append(f'<p class="act">{E(b[1])}</p>')
            elif b[0] == "trans":
                body.append(f'<p class="trans">{E(b[1])}</p>')
            else:
                d = [f'<div class="cue">{E(b[1])}</div>']
                for k, v in b[2]:
                    d.append(f'<div class="{k}">{E(v)}</div>')
                body.append('<div class="dlg">' + "".join(d) + "</div>")
        note = f'<div class="note">{E(sh["note"])}</div>' if sh["note"] else ""
        rows.append(
            f'<div class="shot"><div class="l"><div class="id"><b>{sc["id"]} {sh["id"]}</b><span>{sh["sec"]}s</span></div>'
            f'<div class="tc">{fmt(tc)}</div><div>{E(sh["size"])}</div><div>{E(sh["move"])}</div>{note}{change_html(sh["change"])}</div>'
            f'<div class="m">{"".join(body)}</div><div class="n"></div></div>')
        tc += sh["sec"]

# shotlist table
trs, tc = [], 0
for sc in scenes:
    for sh in sc["shots"]:
        trs.append(f'<tr><td><b>{sc["id"]} {sh["id"]}</b></td><td>{fmt(tc)}</td><td>{sh["sec"]}s</td>'
                   f'<td>{E(sh["size"])}</td><td>{E(sh["move"])}</td><td class="c">{E(sh["change"])}</td><td class="w"></td></tr>')
        tc += sh["sec"]

doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>Politician shooting script draft 9</title><style>
@page {{ size: letter; margin: 0.55in 0.45in 0.6in 0.45in; }}
* {{ box-sizing: border-box; }}
body {{ font: 8.4pt/1.32 "DejaVu Sans", Arial, sans-serif; color: #111; margin: 0; }}
h1 {{ font: bold 15pt "DejaVu Sans Mono", "Courier New", monospace; margin: 0 0 2pt; letter-spacing: 1pt; }}
.sub {{ font-size: 9pt; margin-bottom: 6pt; }}
.legend {{ font-size: 7.6pt; color: #333; border: 0.6pt solid #999; padding: 4pt 6pt; margin-bottom: 10pt; }}
.legend .chg, .legend .note {{ display: inline; }}
.scene, .shot {{ display: grid; grid-template-columns: 1.78in 1fr 1.75in; break-inside: avoid; }}
.scene {{ background: #e6e6e6; border-top: 1.2pt solid #111; margin-top: 8pt; }}
.scene .l {{ padding: 4pt 5pt; display: flex; gap: 8pt; align-items: baseline; font-size: 9pt; }}
.scene .l span {{ font-weight: bold; }}
.scene .l i {{ color: #555; font-style: normal; font-size: 7.5pt; }}
.scene .m {{ padding: 4pt 7pt; font: bold 9.6pt "DejaVu Sans Mono", "Courier New", monospace; }}
.scene .n {{ border-left: 0.6pt solid #aaa; }}
.shot {{ border-top: 0.5pt solid #bbb; }}
.shot .l {{ padding: 4pt 5pt 6pt; border-right: 0.6pt solid #888; }}
.id {{ display: flex; justify-content: space-between; font-size: 8.8pt; }}
.id span {{ font-weight: bold; }}
.tc {{ color: #555; font-size: 7.2pt; margin-bottom: 1pt; }}
.note {{ color: #a3420a; font-style: italic; margin-top: 2pt; }}
.chg {{ color: #1d4f91; margin-top: 2pt; font-size: 7.6pt; }}
.chg.strong {{ font-weight: bold; }}
.shot .m {{ padding: 4pt 8pt 6pt; font: 9.4pt/1.3 "DejaVu Sans Mono", "Courier New", monospace; }}
.act {{ margin: 0 0 4pt; }}
.dlg {{ margin: 2pt 0 5pt 0.55in; width: 2.3in; }}
.cue {{ margin-left: 0.55in; }}
.paren {{ margin-left: 0.3in; }}
.trans {{ text-align: right; margin: 2pt 0 4pt; }}
.n {{ background: repeating-linear-gradient(to bottom, transparent 0, transparent 15.5pt, #c9c9c9 15.5pt, #c9c9c9 16pt); }}
.shot .n {{ border-left: 0.6pt solid #888; min-height: 34pt; }}
.end {{ height: 0.4in; }}
h2 {{ break-before: page; font: bold 12pt "DejaVu Sans Mono", monospace; margin: 0 0 6pt; }}
table {{ border-collapse: collapse; width: 100%; font-size: 7.6pt; }}
th, td {{ border-bottom: 0.5pt solid #bbb; padding: 2.6pt 4pt; text-align: left; vertical-align: top; }}
th {{ border-bottom: 1pt solid #111; }}
td.c {{ color: #1d4f91; }}
td:first-child, td:nth-child(2), td:nth-child(3) {{ white-space: nowrap; }}
td.w {{ width: 1.5in; }}
tr {{ break-inside: avoid; }}
</style></head><body>
<h1>POLITICIAN</h1>
<div class="sub">Shooting script, draft 9 &nbsp;|&nbsp; {E(meta.get("Draft date",""))} &nbsp;|&nbsp; 10 scenes, {nshots} shots, <b>{fmt(total)}</b> &nbsp;|&nbsp; contest limit 7:00, no title or end credits</div>
<div class="legend">Left column: shot, duration, timecode where it starts, size, movement, <span class="note">production note</span>, <span class="chg strong">change from draft 8</span>. Right column: your notes. The shotlist with timecodes is at the end.</div>
{''.join(rows)}
<h2>Shotlist, draft 9: {nshots} shots, {fmt(total)}</h2>
<table><tr><th>Shot</th><th>In</th><th>Dur</th><th>Size</th><th>Movement</th><th>Change from draft 8</th><th>Notes</th></tr>{''.join(trs)}</table>
</body></html>"""
open(out_html, "w", encoding="utf-8").write(doc)
print(nshots, fmt(total))
