#!/usr/bin/env python3
"""Franklin County Public Improvement Bond, landscape (briefcase) format, 300 dpi.
Bond body 11.5 x 8.5 in, coupons attached at the right (2 x 4), total 15.6 x 8.5 in.
Usage: make_bond_wide.py out.html [serial] [vignette.png]"""
import math, sys, html

OUT = sys.argv[1]
SERIAL = sys.argv[2] if len(sys.argv) > 2 else "A 017"
VIGNETTE = sys.argv[3] if len(sys.argv) > 3 else ""

WB, H, WC = 3450, 2550, 1230
W = WB + WC
GREEN = "#2C6E45"; GREEN_D = "#1D4D30"; GREEN_L = "#CFE3D3"; RED = "#A3271D"; INK = "#151515"; PAPER = "#F7F4EA"

def poly(pts, w=1.0, col=GREEN):
    return '<path d="M' + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f'" fill="none" stroke="{col}" stroke-width="{w}"/>'

def band(x0, y0, x1, y1, thick, n=18, wave=70.0, w=1.1, col=GREEN):
    out = []
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    amp = thick / 2 * 0.92; steps = int(L / 3)
    for i in range(n):
        ph = 2 * math.pi * i / n
        pts = []
        for s in range(steps + 1):
            t = s * L / steps
            o = amp * math.sin(2 * math.pi * t / wave + ph) * (0.55 + 0.45 * math.cos(2 * math.pi * t / (wave * 3.0) + ph / 2))
            pts.append((x0 + ux * t + nx * o, y0 + uy * t + ny * o))
        out.append(poly(pts, w, col))
    return "".join(out)

def rosette(cx, cy, R, A, n, k, w=0.9, col=GREEN):
    out = []
    for j in range(k):
        rot = 2 * math.pi * j / (k * max(n, 1))
        pts = [(cx + (R + A * math.sin(n * t)) * math.cos(t + rot), cy + (R + A * math.sin(n * t)) * math.sin(t + rot))
               for t in (2 * math.pi * s / 720 for s in range(721))]
        out.append(poly(pts, w, col))
    return "".join(out)

def ring_text(cx, cy, r, text, size, ident):
    a0 = math.radians(-90)
    d = f"M {cx + r*math.cos(a0):.1f},{cy + r*math.sin(a0):.1f} A {r},{r} 0 1,1 {cx + r*math.cos(a0+math.radians(359.9)):.1f},{cy + r*math.sin(a0+math.radians(359.9)):.1f}"
    return (f'<defs><path id="p{ident}" d="{d}"/></defs><text font-family="Libre Caslon Text" font-weight="700" font-size="{size}" '
            f'letter-spacing="6" fill="{GREEN_D}"><textPath href="#p{ident}">{html.escape(text)}</textPath></text>')

svg = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>']
# ---------- border of the bond body ----------
M, T = 70, 175
x0, y0, x1, y1 = M, M, WB - M, H - M
c = T / 2
svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" stroke="{GREEN_D}" stroke-width="7"/>')
svg.append(f'<rect x="{x0+T}" y="{y0+T}" width="{x1-x0-2*T}" height="{y1-y0-2*T}" fill="none" stroke="{GREEN_D}" stroke-width="5"/>')
svg.append(f'<rect x="{x0+T+14}" y="{y0+T+14}" width="{x1-x0-2*T-28}" height="{y1-y0-2*T-28}" fill="none" stroke="{GREEN}" stroke-width="2"/>')
for (ax, ay, bx, by) in [(x0, y0 + c, x1, y0 + c), (x0, y1 - c, x1, y1 - c), (x0 + c, y0, x0 + c, y1), (x1 - c, y0, x1 - c, y1)]:
    svg.append(band(ax, ay, bx, by, T - 26, n=22, wave=64))
    svg.append(band(ax, ay, bx, by, T - 26, n=10, wave=150, w=0.8, col=GREEN_D))
for cxx in range(x0 + 300, x1 - 220, 250):
    for cyy in (y0 + c, y1 - c):
        if abs(cxx - WB / 2) < 860 and cyy < H / 2:
            continue  # leave room for the top tablet
        svg.append(f'<circle cx="{cxx}" cy="{cyy}" r="52" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="3"/>' + rosette(cxx, cyy, 30, 14, 9, 6, 0.8))
for cyy in range(y0 + 330, y1 - 220, 250):
    for cxx in (x0 + c, x1 - c):
        svg.append(f'<circle cx="{cxx}" cy="{cyy}" r="52" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="3"/>' + rosette(cxx, cyy, 30, 14, 9, 6, 0.8))
for (cx, cy) in [(x0 + c, y0 + c), (x1 - c, y0 + c), (x0 + c, y1 - c), (x1 - c, y1 - c)]:
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{T*0.62:.0f}" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="6"/>')
    svg.append(rosette(cx, cy, T * 0.38, T * 0.17, 11, 9, 0.9))
    svg.append(rosette(cx, cy, T * 0.16, T * 0.06, 7, 5, 0.8, GREEN_D))
tx0, tx1, ty0, ty1 = WB / 2 - 760, WB / 2 + 760, y0 + 28, y0 + T - 28
svg.append(f'<rect x="{tx0}" y="{ty0}" width="{tx1-tx0}" height="{ty1-ty0}" fill="{GREEN_L}" stroke="{GREEN_D}" stroke-width="5"/>')
svg.append(f'<text x="{WB/2}" y="{(ty0+ty1)/2+24}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="64" letter-spacing="6" fill="{GREEN_D}" textLength="1240" lengthAdjust="spacing">UNITED STATES OF AMERICA</text>')

# underprint
if VIGNETTE:
    bw = 2800; bh = round(bw * 1700 / 2560)
    svg.append(f'<image href="{VIGNETTE}" x="{WB/2 - bw/2}" y="215" width="{bw}" height="{bh}" preserveAspectRatio="xMidYMid meet"/>')

def tablet(x, y, w, h, label, value, vcol, vsize):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{GREEN_L}" stroke="{GREEN_D}" stroke-width="4"/>'
            f'<text x="{x+w/2}" y="{y+44}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="30" letter-spacing="6" fill="{GREEN_D}">{label}</text>'
            f'<text x="{x+w/2}" y="{y+h-26}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="{vsize}" letter-spacing="4" fill="{vcol}">{value}</text>')
svg.append(tablet(300, 290, 280, 120, "NUMBER", html.escape(SERIAL), RED, 46))
svg.append(tablet(WB - 820, 290, 520, 190, "DOLLARS", "$500,000", INK, 96))

def counter(cx, cy):
    s = f'<circle cx="{cx}" cy="{cy}" r="205" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="6"/>' + rosette(cx, cy, 150, 48, 18, 10, 0.75)
    s += f'<circle cx="{cx}" cy="{cy}" r="112" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="4"/>'
    s += f'<text x="{cx+4}" y="{cy+28}" text-anchor="middle" font-family="Playfair Display" font-weight="900" style="font-variant-numeric:lining-nums" font-size="92" fill="#9a9a9a">500</text>'
    s += f'<text x="{cx}" y="{cy+24}" text-anchor="middle" font-family="Playfair Display" font-weight="900" style="font-variant-numeric:lining-nums" font-size="92" fill="{INK}">500</text>'
    s += f'<text x="{cx}" y="{cy+72}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="20" letter-spacing="5" fill="{GREEN_D}">THOUSAND</text>'
    return s
svg.append(counter(500, 720)); svg.append(counter(WB - 500, 720))

# vignette
if VIGNETTE:
    pass

# title block, to the sides of nothing: below the vignette
svg.append(f'<text x="{WB/2+9}" y="1158" text-anchor="middle" font-family="UnifrakturMaguntia" font-size="185" fill="#8d8d8d">County of Franklin</text>')
svg.append(f'<text x="{WB/2}" y="1150" text-anchor="middle" font-family="UnifrakturMaguntia" font-size="185" fill="{INK}" stroke="{INK}" stroke-width="1.5">County of Franklin</text>')
svg.append(f'<text x="{WB/2+5}" y="1253" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="80" letter-spacing="10" fill="#9a9a9a">PUBLIC IMPROVEMENT BOND</text>')
svg.append(f'<text x="{WB/2}" y="1248" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="80" letter-spacing="10" fill="{INK}">PUBLIC IMPROVEMENT BOND</text>')
svg.append(f'<text x="{WB/2}" y="1302" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="34" letter-spacing="14" fill="{GREEN_D}">SERIES A &#183; DATED MARCH 1, 1948</text>')

# amount tablet
svg.append(f'<rect x="{WB/2-800}" y="1322" width="1600" height="262" rx="20" fill="{GREEN_L}" stroke="{GREEN_D}" stroke-width="6"/>')
svg.append(f'<rect x="{WB/2-786}" y="1336" width="1572" height="234" rx="14" fill="none" stroke="{GREEN_D}" stroke-width="2"/>')
svg.append(band(WB/2-786, 1453, WB/2+786, 1453, 220, n=16, wave=90, w=0.7, col="#9cc2a6"))
# signatures and seal (bottom row)
def sig(img, x, y, w):
    return f'<image href="{img}" x="{x}" y="{y}" width="{w}" preserveAspectRatio="xMidYMid meet" style="mix-blend-mode:multiply"/>'
SY = 2068
svg.append(sig("sig4_rising.png", 500, SY + 30, 190))
svg.append(sig("sig1_loop.png", 2080, SY - 30, 330))
svg.append(sig("sig2_strike.png", 2620, SY + 20, 330))
sx, sy = WB / 2 - 120, SY + 130
svg.append(f'<circle cx="{sx}" cy="{sy}" r="140" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="4"/>' + rosette(sx, sy, 86, 28, 20, 8, 0.75))
svg.append(f'<circle cx="{sx}" cy="{sy}" r="50" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="3"/>')
svg.append(f'<text x="{sx}" y="{sy+20}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="54" fill="{GREEN_D}">&#9733;</text>')
svg.append(ring_text(sx, sy, 117, "SEAL OF THE COUNTY OF FRANKLIN · 1948 · ", 20, "seal"))

# coupons at the right
PX = WB + 8
svg.append(f'<line x1="{PX}" y1="50" x2="{PX}" y2="{H-50}" stroke="{GREEN_D}" stroke-width="4" stroke-dasharray="18 12"/>')
months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
def due(k):
    tot = 6 * k; return months[(2 + tot) % 12], 1948 + (2 + tot) // 12
CX0, CY0 = WB + 40, 60
CW, CH = (WC - 70) / 2, (H - 120) / 4
coupon_html = []
for idx, k in enumerate(range(33, 41)):
    col, row = idx % 2, idx // 2
    cx0 = CX0 + col * CW; cy0 = CY0 + row * CH
    svg.append(f'<rect x="{cx0+10}" y="{cy0+10}" width="{CW-20}" height="{CH-20}" fill="none" stroke="{GREEN_D}" stroke-width="4"/>')
    svg.append(band(cx0 + 10, cy0 + 34, cx0 + CW - 10, cy0 + 34, 34, n=10, wave=44, w=0.8))
    svg.append(band(cx0 + 10, cy0 + CH - 34, cx0 + CW - 10, cy0 + CH - 34, 34, n=10, wave=44, w=0.8))
    rx, ry = cx0 + 92, cy0 + 125
    svg.append(f'<circle cx="{rx}" cy="{ry}" r="52" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="3"/>' + rosette(rx, ry, 35, 12, 12, 7, 0.7))
    svg.append(f'<circle cx="{rx}" cy="{ry}" r="24" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="2"/>')
    svg.append(f'<text x="{rx}" y="{ry+11}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="30" fill="{INK}">{k}</text>')
    svg.append(f'<text x="{cx0+CW-34}" y="{cy0+105}" text-anchor="end" font-family="Libre Caslon Text" font-weight="700" font-size="26" letter-spacing="4" fill="{RED}">No. {k}</text>')
    svg.append(f'<text x="{cx0+CW-34}" y="{cy0+165}" text-anchor="end" font-family="Playfair Display" font-weight="900" style="font-variant-numeric:lining-nums" font-size="58" fill="{GREEN_D}">$6,250</text>')
    if col == 0:
        svg.append(f'<line x1="{cx0+CW}" y1="{cy0+6}" x2="{cx0+CW}" y2="{cy0+CH-6}" stroke="{GREEN_D}" stroke-width="3" stroke-dasharray="12 9" opacity=".7"/>')
    if row < 3 and col == 0:
        svg.append(f'<line x1="{CX0}" y1="{cy0+CH}" x2="{CX0+2*CW}" y2="{cy0+CH}" stroke="{GREEN_D}" stroke-width="3" stroke-dasharray="12 9" opacity=".7"/>')
    mname, yy = due(k)
    coupon_html.append(f'''<div class="cp" style="left:{cx0+34:.0f}px;top:{cy0+192:.0f}px;width:{CW-68:.0f}px;">
<div class="cpt">FRANKLIN COUNTY</div>
<div class="cpb">On the first day of {mname}, {yy}, Franklin County will pay to bearer, at the office of the County Treasurer, upon surrender of this coupon, Six Thousand Two Hundred Fifty Dollars ($6,250), being six months' interest then due on its Public Improvement Bond dated March&nbsp;1,&nbsp;1948, No.&nbsp;{html.escape(SERIAL).replace(' ', '&nbsp;')}.</div>
<div class="cps"><img src="sig2_strike.png"><div>County Treasurer</div></div></div>''')

P1 = """<span class="sc">Franklin County</span>, a political subdivision duly organized and existing under the Constitution and laws of the State, for value received, hereby acknowledges itself indebted and promises to pay to the bearer of this bond, or, if it be registered, to the registered holder hereof, on the first day of March, 1968, the principal sum of <b class=\"sc\" style=\"font-weight:700\">Five Hundred Thousand Dollars ($500,000)</b>"""
COLS = """<p>in lawful money of the United States of America, and to pay interest thereon from the date hereof at the rate of two and one-half per centum (2&frac12;%) per annum, payable semi-annually on the first days of March and September in each year, upon presentation and surrender of the interest coupons hereto annexed as they severally become due. Both principal and interest are payable at the office of the County Treasurer of Franklin County or, at the option of the holder, at the Fiscal Agency of the County in the City and State of New York.</p>
<p>This bond is one of an authorized issue of bonds of like date and tenor, except as to maturity, aggregating Twenty Million Dollars ($20,000,000), issued for the purpose of constructing, widening and paving public highways, roads, bridges and streets within the County, pursuant to the Constitution and statutes of the State and to a resolution of the Board of Supervisors duly adopted on the twelfth day of January, 1948, and approved by more than two-thirds of the qualified electors of the County voting at a special election duly called and held for that purpose.</p>
<p>This bond is transferable by delivery, unless registered as to principal in the name of the holder on the books of the County Treasurer, such registration being noted hereon. Such registration shall not affect the negotiability of the coupons, which shall continue to pass by delivery.</p>
<p>It is hereby certified, recited and declared that all acts, conditions and things required to exist, happen and be performed precedent to and in the issuance of this bond have existed, happened and been performed in due time, form and manner as required by law; that the total indebtedness of said County, including this bond, does not exceed any constitutional or statutory limitation; and that provision has been made for the levy of an annual tax sufficient to pay the principal of and interest on this bond as the same become due. The full faith and credit of Franklin County are hereby irrevocably pledged for the punctual payment of the principal of and interest on this bond.</p>
<p><span class="sc">In Witness Whereof</span>, Franklin County has caused this bond to be signed by the Chairman of its Board of Supervisors and by its County Treasurer, countersigned by the Clerk of said Board, its corporate seal to be hereunto affixed, and the interest coupons hereto annexed to be authenticated by the facsimile signature of its County Treasurer, and this bond to be dated the first day of March, 1948.</p>"""

page = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=Oswald:wght@700&family=Playfair+Display:wght@900&family=UnifrakturMaguntia&display=block" rel="stylesheet">
<style>
html,body{{margin:0;padding:0;}}
.sheet{{position:relative;width:{W}px;height:{H}px;background:{PAPER};overflow:hidden;}}
.sheet svg{{position:absolute;left:0;top:0;}}
.p1{{position:absolute;left:300px;top:1598px;width:{WB-600}px;font-family:'IM Fell English';font-style:italic;font-size:29px;line-height:1.38;color:{INK};text-align:justify;text-indent:60px;}}
.amt{{position:absolute;left:{WB/2-760}px;top:1330px;width:1520px;height:250px;text-align:center;color:{INK};}} .amt .big{{font-family:'Playfair Display';font-weight:900;font-variant-numeric:lining-nums;font-size:250px;line-height:1;color:{GREEN_D};text-shadow:7px 7px 0 #b9b9b9;}} .amt .words{{font-family:'Libre Caslon Text';font-weight:700;font-size:40px;letter-spacing:6px;margin-top:4px;}}
.cols{{position:absolute;left:300px;top:1700px;width:{WB-600}px;column-count:2;column-gap:70px;column-rule:2px solid {GREEN_L};font-family:'IM Fell English';font-style:italic;font-size:24px;line-height:1.27;color:{INK};text-align:justify;hyphens:auto;}}
.cols p{{margin:0 0 6px 0;text-indent:44px;}}
.sc{{font-variant:small-caps;font-style:normal;letter-spacing:2px;}}
.lab{{position:absolute;font-family:'IM Fell English';font-style:italic;font-size:32px;color:{INK};}}
.labr{{position:absolute;font-family:'Libre Caslon Text';font-weight:700;font-size:22px;letter-spacing:4px;color:{INK};text-transform:uppercase;border-top:3px solid {INK};padding-top:6px;text-align:center;}}
.imp{{position:absolute;left:0;width:{WB}px;text-align:center;font-family:'Libre Caslon Text';font-weight:700;font-size:18px;letter-spacing:6px;color:#444;}}
.cp{{position:absolute;text-align:center;}}
.cpt{{font-family:'Libre Caslon Text';font-weight:700;font-size:26px;letter-spacing:5px;color:{INK};margin-bottom:6px;}}
.cpb{{font-family:'IM Fell English';font-style:italic;font-size:22px;line-height:1.32;color:{INK};text-align:justify;}}
.cps img{{width:200px;display:block;margin:2px auto -8px auto;mix-blend-mode:multiply;}}
.cps div{{border-top:2px solid {INK};margin:0 40px;padding-top:3px;font-family:'Libre Caslon Text';font-weight:700;font-size:16px;letter-spacing:4px;text-transform:uppercase;}}
</style></head><body><div class="sheet">
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{''.join(svg)}</svg>
<div class="p1">{P1}</div>
<div class="amt"><div class="big">$500,000</div></div>
<div class="cols">{COLS}</div>
<div class="lab" style="left:330px;top:{SY}px;">Countersigned:</div>
<div class="labr" style="left:330px;top:{SY+165}px;width:480px;">Clerk of the Board of Supervisors</div>
<div class="labr" style="left:1990px;top:{SY+165}px;width:520px;">Chairman, Board of Supervisors</div>
<div class="labr" style="left:2600px;top:{SY+165}px;width:420px;">County Treasurer</div>
<div class="imp" style="top:{H-56}px;">WHITCOMBE &amp; GRAY BANK NOTE COMPANY, NEW YORK &middot; FOR MOTION PICTURE USE ONLY &middot; NOT NEGOTIABLE</div>
{''.join(coupon_html)}
</div></body></html>"""
open(OUT, "w", encoding="utf-8").write(page)
print("ok", W, H)
