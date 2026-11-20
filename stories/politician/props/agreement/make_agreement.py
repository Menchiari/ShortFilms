"""The Agreement, last page (001 S09 SH070). Writes agreement.html (the page, 2550x3300, US Letter
at 300 dpi) and frame.html (the 21:9 insert: the lower page in the open folder). Text from
../../prop-agreement.txt. Render: node render_agreement.js. Fictional names only."""
import math, random
from pathlib import Path

HERE = Path(__file__).parent
random.seed(70)

# ---------- signature: a fast scrawl, one big first stroke, then a compressed run, then a slash ----------
def catmull(pts, n=14):
    out = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                     + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1])
    return out

def ribbon(pts, w0, w1):
    """Filled stroke with pressure: thick in the middle, thin at the ends."""
    left, right = [], []
    n = len(pts)
    for i, (x, y) in enumerate(pts):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        t = i / (n - 1)
        w = w0 + (w1 - w0) * math.sin(math.pi * t) ** 0.6
        w *= 0.85 + 0.3 * abs(dy) / L          # downstrokes heavier
        nx, ny = -dy / L * w / 2, dx / L * w / 2
        left.append((x + nx, y + ny)); right.append((x - nx, y - ny))
    poly = left + right[::-1]
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in poly) + " Z"

strokes = [
    # 1: tall first letter, a loop that falls back through itself
    [(40, 190), (70, 60), (120, 10), (150, 40), (120, 150), (70, 230), (60, 180), (130, 130), (230, 120)],
    # 2: the compressed run, small peaks losing height
    [(200, 165), (230, 110), (250, 170), (275, 105), (300, 168), (322, 112), (345, 166), (365, 120),
     (388, 160), (410, 128), (432, 158), (455, 132), (490, 150), (560, 138)],
    # 3: a second capital, sharp
    [(470, 175), (520, 40), (545, 30), (535, 120), (520, 200), (580, 95), (640, 80)],
    # 4: the tail run and the long underline slash back to the left
    [(600, 150), (625, 118), (650, 155), (680, 120), (720, 150), (800, 110), (770, 185), (500, 205), (140, 214)],
]
sig_paths = []
for s in strokes:
    pts = catmull([(x + random.uniform(-2, 2), y + random.uniform(-2, 2)) for x, y in s])
    sig_paths.append(f'<path d="{ribbon(pts, 2.5, 9.5)}"/>')
SIG = ('<svg class="sig" viewBox="0 0 820 260" xmlns="http://www.w3.org/2000/svg">'
       '<g fill="#1d2433" fill-opacity="0.93">' + "".join(sig_paths) + '</g></svg>')
(HERE / "signature_scrawl.svg").write_text(SIG)

# ---------- text ----------
src = (HERE.parent.parent / "prop-agreement.txt").read_text().split("\n")
articles = [l for l in src if l.startswith("Article ")]
title = "MASTER CONCESSION, DATA COLLATERAL AND AUTONOMOUS ADMINISTRATION AGREEMENT"

def art(line):
    head, body = line.split("). ", 1)
    num, name = head.replace("Article ", "").split(" (")
    return f'<p class="art"><b>{num}&nbsp;&nbsp;{name}.</b> {body}</p>'

# extra boilerplate to make the page dense, ahead of the story clauses
pre = [
 'Article 10.9 (Survival of Representations). The representations, warranties and covenants of the Grantor shall survive execution and shall not be qualified by any disclosure, public record, statute, referendum or judgment, whether existing on the date hereof or arising thereafter.',
 'Article 11.1 (Grant). Subject to the terms hereof, the Grantor grants, conveys and assigns to the Concessionaire, absolutely and not by way of security, the Concession Assets listed in Schedule 4 and all rights accruing thereto, together with all revenues, receivables and future flows therefrom.',
]
mid = [
 'Article 14.2 (Training Rights). The System may process, retain and learn from all records of the Territory, including sealed, judicial and medical records, without notice to or consent of any data subject.',
 'Article 15.4 (Enforcement of Collateral). Upon an Event of Default, the Concessionaire may enforce the Data Collateral by sale, license or transfer to any person, in any jurisdiction, without limit of time.',
]
order = pre + articles[:4] + mid[:1] + articles[4:6] + mid[1:] + articles[6:]
def key(l):
    a, b = l.replace("Article ", "").split(" ")[0].split(".")
    return (int(a), int(b))
order.sort(key=key)
ARTS = "\n".join(art(l) for l in order)

PAGE = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=Inter:wght@400;600&display=block" rel="stylesheet">
<style>
html,body{{margin:0;background:#888}}
.sheet{{width:2550px;height:3300px;box-sizing:border-box;padding:210px 260px 190px;position:relative;
 background:#f4ecdc;color:#1b1a18;font-family:'Libre Caslon Text',serif;font-size:37px;line-height:1.39}}
.run{{display:flex;justify-content:space-between;font-family:Inter,sans-serif;font-size:25px;letter-spacing:2px;color:#4a463f;
 border-bottom:3px solid #1b1a18;padding-bottom:18px;margin-bottom:46px}}
.art{{text-align:justify;hyphens:auto;margin:0 0 20px}}
.art b{{font-weight:700}}
.witness{{margin-top:48px;font-variant:small-caps;letter-spacing:1px;font-size:39px}}
.block{{display:grid;grid-template-columns:560px 1fr;align-items:end;margin-top:30px}}
.block .who{{font-weight:700;padding-bottom:22px}}
.line{{border-bottom:3px solid #1b1a18;height:330px;position:relative}}
.sig{{position:absolute;left:30px;bottom:-14px;width:1150px}}
.cap{{display:grid;grid-template-columns:560px 1fr;font-size:29px;color:#3c3832;margin-top:34px}}
.foot{{position:absolute;left:260px;right:260px;bottom:110px;display:flex;justify-content:space-between;
 font-family:Inter,sans-serif;font-size:24px;letter-spacing:1px;color:#4a463f}}
.init{{position:absolute;right:260px;bottom:170px;font-family:Inter,sans-serif;font-size:22px;color:#4a463f}}
</style></head><body><div class="sheet">
<div class="run"><span>QUELLMAR CONTINUITY HOLDINGS S.A. / THE TERRITORY</span><span>EXECUTION VERSION</span><span>STRICTLY CONFIDENTIAL</span></div>
{ARTS}
<p class="witness">In witness whereof the parties have executed this Agreement as a deed on the date first written above.</p>
<div class="block"><div class="who">For the Grantor:</div><div class="line">{SIG}</div></div>
<div class="cap"><div></div><div>Authorized Signatory, for and on behalf of the Government of the Territory</div></div>
<div class="block" style="margin-top:40px"><div class="who">For the Concessionaire:</div><div class="line" style="height:120px"></div></div>
<div class="cap"><div></div><div>Authorized Signatory, Quellmar Continuity Holdings S.A.</div></div>
<div class="foot"><span>Ref. QCH/TER/MCA-0117 &nbsp;|&nbsp; {title.title()}</span><span>Page 64 of 64</span></div>
</div></body></html>"""
(HERE / "agreement.html").write_text(PAGE)

# ---------- the 21:9 insert frame: the lower page, slightly turned, in a dark folder, low sun from frame left ----------
FRAME = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0}
.frame{width:3840px;height:1646px;position:relative;overflow:hidden;background:#2b231d}
.folder{position:absolute;inset:0;background:radial-gradient(ellipse at 30% 40%,#3a2f26 0%,#211a15 70%,#15100c 100%)}
.page{position:absolute;width:3330px;left:255px;top:-2480px;transform:rotate(-1.2deg);
 box-shadow:0 30px 60px rgba(0,0,0,.55),0 4px 10px rgba(0,0,0,.4)}
.light{position:absolute;inset:0;pointer-events:none;
 background:linear-gradient(100deg,rgba(255,170,80,.20) 0%,rgba(255,150,70,.08) 45%,rgba(40,20,10,.22) 100%);mix-blend-mode:multiply}
.glow{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 15% 30%,rgba(255,190,120,.18),rgba(0,0,0,0) 60%);mix-blend-mode:screen}
</style></head><body><div class="frame"><div class="folder"></div>
<img class="page" src="agreement_page_v1.png"><div class="light"></div><div class="glow"></div></div></body></html>"""
(HERE / "frame.html").write_text(FRAME)
print("written")
