#!/usr/bin/env python3
"""Franklin County Public Improvement Bond prop: engraved-style SVG/HTML at 300 dpi.
Usage: make_bond.py out.html [serial] [vignette.png]"""
import math, sys, html

OUT = sys.argv[1]
SERIAL = sys.argv[2] if len(sys.argv) > 2 else "A 017"
VIGNETTE = sys.argv[3] if len(sys.argv) > 3 else ""

W, H_BOND, H_CP = 2550, 3960, 1420
H = H_BOND + H_CP
GREEN = "#2C6E45"; GREEN_D = "#1D4D30"; GREEN_L = "#CFE3D3"; RED = "#A3271D"; INK = "#151515"; PAPER = "#F7F4EA"

def poly(pts, w=1.0, col=GREEN, op=1.0):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" opacity="{op}"/>'

def band(x0, y0, x1, y1, thick, n=18, wave=70.0, amp=None, w=1.1, col=GREEN):
    """Woven lathe ribbon along a straight segment, lines offset to both sides of the centre line."""
    out = []
    L = math.hypot(x1 - x0, y1 - y0); ux, uy = (x1 - x0) / L, (y1 - y0) / L; nx, ny = -uy, ux
    amp = amp if amp is not None else thick / 2 * 0.92
    steps = int(L / 3)
    for i in range(n):
        ph = 2 * math.pi * i / n
        pts = []
        for s in range(steps + 1):
            t = s * L / steps
            o = amp * math.sin(2 * math.pi * t / wave + ph) * (0.55 + 0.45 * math.cos(2 * math.pi * t / (wave * 3.0) + ph / 2))
            pts.append((x0 + ux * t + nx * o, y0 + uy * t + ny * o))
        out.append(poly(pts, w, col))
    return "".join(out)

def rosette(cx, cy, R, A, n, k, w=0.9, col=GREEN, m=0, B=0.0):
    """Lathe rosette: k copies of r = R + A sin(n t) + B sin(m t), rotated."""
    out = []
    for j in range(k):
        rot = 2 * math.pi * j / (k * max(n, 1))
        pts = []
        for s in range(0, 721):
            t = 2 * math.pi * s / 720
            r = R + A * math.sin(n * t) + (B * math.sin(m * t) if m else 0)
            pts.append((cx + r * math.cos(t + rot), cy + r * math.sin(t + rot)))
        out.append(poly(pts, w, col))
    return "".join(out)

def ring_text(cx, cy, r, text, size, col=GREEN_D, start=-90, span=360, ident="rt"):
    pid = f"p{ident}"
    a0 = math.radians(start)
    d = f"M {cx + r*math.cos(a0):.1f},{cy + r*math.sin(a0):.1f} A {r},{r} 0 1,1 {cx + r*math.cos(a0+math.radians(359.9)):.1f},{cy + r*math.sin(a0+math.radians(359.9)):.1f}"
    return (f'<defs><path id="{pid}" d="{d}"/></defs><text font-family="Libre Caslon Text" font-weight="700" font-size="{size}" '
            f'letter-spacing="6" fill="{col}"><textPath href="#{pid}" startOffset="0">{html.escape(text)}</textPath></text>')

svg = []
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>')
# ---------- border ----------
M, T = 70, 175                       # outer margin, band thickness
x0, y0, x1, y1 = M, M, W - M, H_BOND - M
svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" stroke="{GREEN_D}" stroke-width="7"/>')
svg.append(f'<rect x="{x0+T}" y="{y0+T}" width="{x1-x0-2*T}" height="{y1-y0-2*T}" fill="none" stroke="{GREEN_D}" stroke-width="5"/>')
svg.append(f'<rect x="{x0+T+14}" y="{y0+T+14}" width="{x1-x0-2*T-28}" height="{y1-y0-2*T-28}" fill="none" stroke="{GREEN}" stroke-width="2"/>')
c = T / 2
for (ax, ay, bx, by) in [(x0, y0 + c, x1, y0 + c), (x0, y1 - c, x1, y1 - c), (x0 + c, y0, x0 + c, y1), (x1 - c, y0, x1 - c, y1)]:
    svg.append(band(ax, ay, bx, by, T - 26, n=22, wave=64))
    svg.append(band(ax, ay, bx, by, T - 26, n=10, wave=150, w=0.8, col=GREEN_D))
# repeated small rosettes inside the band
for cxx in range(x0 + 300, x1 - 220, 250):
    for cyy in (y0 + c, y1 - c):
        svg.append(f'<circle cx="{cxx}" cy="{cyy}" r="52" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="3"/>' + rosette(cxx, cyy, 30, 14, 9, 6, 0.8))
for cyy in range(y0 + 330, y1 - 220, 250):
    for cxx in (x0 + c, x1 - c):
        svg.append(f'<circle cx="{cxx}" cy="{cyy}" r="52" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="3"/>' + rosette(cxx, cyy, 30, 14, 9, 6, 0.8))
# corner rosettes
for (cx, cy) in [(x0 + c, y0 + c), (x1 - c, y0 + c), (x0 + c, y1 - c), (x1 - c, y1 - c)]:
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{T*0.62:.0f}" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="6"/>')
    svg.append(rosette(cx, cy, T * 0.38, T * 0.17, 11, 9, 0.9))
    svg.append(rosette(cx, cy, T * 0.16, T * 0.06, 7, 5, 0.8, GREEN_D))
# top tablet: UNITED STATES OF AMERICA
tx0, tx1, ty0, ty1 = 820, W - 820, y0 + 28, y0 + T - 28
svg.append(f'<rect x="{tx0}" y="{ty0}" width="{tx1-tx0}" height="{ty1-ty0}" fill="{GREEN_L}" stroke="{GREEN_D}" stroke-width="5"/>')
svg.append(f'<text x="{W/2+4}" y="{(ty0+ty1)/2+26}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="70" letter-spacing="8" fill="#ffffff" opacity=".6">UNITED STATES OF AMERICA</text>')
svg.append(f'<text x="{W/2}" y="{(ty0+ty1)/2+22}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="70" letter-spacing="8" fill="{GREEN_D}">UNITED STATES OF AMERICA</text>')

# ---------- underprint ----------
svg.append(f'<text x="{W/2}" y="2560" text-anchor="middle" font-family="Playfair Display" font-weight="900" font-size="1050" fill="{GREEN}" opacity=".085" letter-spacing="-20">500</text>')
svg.append(rosette(W / 2, 2240, 560, 90, 24, 10, 0.7, GREEN, op=1) if False else "")

# ---------- serial and amount tablets ----------
def tablet(x, y, w, h, label, value, vcol, vsize):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{GREEN_L}" stroke="{GREEN_D}" stroke-width="4"/>'
            f'<text x="{x+w/2}" y="{y+44}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="30" letter-spacing="6" fill="{GREEN_D}">{label}</text>'
            f'<text x="{x+w/2}" y="{y+h-26}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="{vsize}" letter-spacing="4" fill="{vcol}">{value}</text>')
svg.append(tablet(300, 300, 380, 170, "NUMBER", html.escape(SERIAL), RED, 80))
svg.append(tablet(W - 680, 300, 380, 170, "DOLLARS", "500,000", INK, 78))

# ---------- counters ----------
for cx in (520, W - 520):
    cy = 720
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="205" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="6"/>')
    svg.append(rosette(cx, cy, 150, 48, 18, 10, 0.75))
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="112" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="4"/>')
    svg.append(f'<text x="{cx+4}" y="{cy+28}" text-anchor="middle" font-family="Playfair Display" font-weight="900" font-size="92" fill="#9a9a9a">500</text>')
    svg.append(f'<text x="{cx}" y="{cy+24}" text-anchor="middle" font-family="Playfair Display" font-weight="900" font-size="92" fill="{INK}">500</text>')
    svg.append(f'<text x="{cx}" y="{cy+72}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="20" letter-spacing="5" fill="{GREEN_D}">THOUSAND</text>')

# ---------- vignette ----------
VX, VY, VRX, VRY = W / 2, 690, 470, 300
if VIGNETTE:
    vw = 1150; vh = round(vw * 850 / 1280)
    svg.append(f'<image href="{VIGNETTE}" x="{W/2 - vw/2}" y="292" width="{vw}" height="{vh}" preserveAspectRatio="xMidYMid meet" style="mix-blend-mode:multiply"/>')
else:
    svg.append(f'<ellipse cx="{VX}" cy="{VY}" rx="{VRX}" ry="{VRY}" fill="none" stroke="#999" stroke-width="3" stroke-dasharray="14 10"/>')
    svg.append(f'<text x="{VX}" y="{VY-10}" text-anchor="middle" font-family="Inter" font-size="40" fill="#888">YOUR ENGRAVED VIGNETTE</text>')
    svg.append(f'<text x="{VX}" y="{VY+45}" text-anchor="middle" font-family="Inter" font-size="30" fill="#999">road and bridge under construction</text>')

# ---------- title ----------
svg.append(f'<text x="{W/2+9}" y="1262" text-anchor="middle" font-family="UnifrakturMaguntia" font-size="230" fill="#8d8d8d">County of Franklin</text>')
svg.append(f'<text x="{W/2}" y="1254" text-anchor="middle" font-family="UnifrakturMaguntia" font-size="230" fill="{INK}" stroke="{INK}" stroke-width="1.5">County of Franklin</text>')
svg.append(f'<text x="{W/2+5}" y="1384" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="104" letter-spacing="10" fill="#9a9a9a">PUBLIC IMPROVEMENT BOND</text>')
svg.append(f'<text x="{W/2}" y="1379" text-anchor="middle" font-family="Oswald" font-weight="700" font-size="104" letter-spacing="10" fill="{INK}">PUBLIC IMPROVEMENT BOND</text>')
svg.append(f'<text x="{W/2}" y="1448" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="44" letter-spacing="14" fill="{GREEN_D}">SERIES A</text>')

# ---------- signatures, seal ----------
def sig(img, x, y, w, label, label2=""):
    return (f'<image href="{img}" x="{x}" y="{y}" width="{w}" preserveAspectRatio="xMidYMid meet" style="mix-blend-mode:multiply"/>')
svg.append(sig("sig4_rising.png", 430, 3385, 250, ""))
svg.append(sig("sig1_loop.png", 1640, 3300, 360, ""))
svg.append(sig("sig2_strike.png", 1650, 3520, 340, ""))
# seal
sx, sy = W / 2, 3560
svg.append(f'<circle cx="{sx}" cy="{sy}" r="150" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="4"/>')
svg.append(rosette(sx, sy, 92, 30, 20, 8, 0.75))
svg.append(f'<circle cx="{sx}" cy="{sy}" r="54" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="3"/>')
svg.append(f'<text x="{sx}" y="{sy+22}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="58" fill="{GREEN_D}">&#9733;</text>')
svg.append(ring_text(sx, sy, 126, "SEAL OF THE COUNTY OF FRANKLIN · 1948 · ", 22, ident="seal"))

# ---------- coupons ----------
PY = H_BOND + 10
svg.append(f'<line x1="60" y1="{PY}" x2="{W-60}" y2="{PY}" stroke="{GREEN_D}" stroke-width="4" stroke-dasharray="18 12"/>')
months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
def due(k):
    tot = 6 * k; y = 1948 + (2 + tot) // 12; m = (2 + tot) % 12
    return months[m], y
CW, CH = (W - 2 * 90) / 4, (H_CP - 90) / 2
coupon_html = []
for idx, k in enumerate(range(33, 41)):
    col, row = idx % 4, idx // 4
    cx0 = 90 + col * CW; cy0 = PY + 40 + row * CH
    svg.append(f'<rect x="{cx0+14}" y="{cy0+12}" width="{CW-28}" height="{CH-24}" fill="none" stroke="{GREEN_D}" stroke-width="4"/>')
    svg.append(band(cx0 + 14, cy0 + 40, cx0 + CW - 14, cy0 + 40, 40, n=10, wave=46, w=0.8))
    svg.append(band(cx0 + 14, cy0 + CH - 40, cx0 + CW - 14, cy0 + CH - 40, 40, n=10, wave=46, w=0.8))
    rx, ry = cx0 + 110, cy0 + 150
    svg.append(f'<circle cx="{rx}" cy="{ry}" r="62" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="3"/>' + rosette(rx, ry, 42, 14, 12, 7, 0.7))
    svg.append(f'<circle cx="{rx}" cy="{ry}" r="28" fill="{PAPER}" stroke="{GREEN_D}" stroke-width="2"/>')
    svg.append(f'<text x="{rx}" y="{ry+12}" text-anchor="middle" font-family="Libre Caslon Text" font-weight="700" font-size="34" fill="{INK}">{k}</text>')
    svg.append(f'<text x="{cx0+CW-40}" y="{cy0+130}" text-anchor="end" font-family="Libre Caslon Text" font-weight="700" font-size="30" letter-spacing="4" fill="{RED}">No. {k}</text>')
    svg.append(f'<text x="{cx0+CW-40}" y="{cy0+200}" text-anchor="end" font-family="Playfair Display" font-weight="900" font-size="68" fill="{GREEN_D}">$6,250</text>')
    if k == 33:
        svg.append(f'<line x1="{cx0+CW-14}" y1="{cy0}" x2="{cx0+CW-14}" y2="{cy0+CH}" stroke="none"/>')
    if col < 3:
        svg.append(f'<line x1="{cx0+CW}" y1="{cy0+8}" x2="{cx0+CW}" y2="{cy0+CH-8}" stroke="{GREEN_D}" stroke-width="3" stroke-dasharray="12 9" opacity=".7"/>')
    mname, yy = due(k)
    coupon_html.append(f'''<div class="cp" style="left:{cx0+40:.0f}px;top:{cy0+232:.0f}px;width:{CW-80:.0f}px;">
<div class="cpt">FRANKLIN COUNTY</div>
<div class="cpb">On the first day of {mname}, {yy}, Franklin County will pay to bearer, at the office of the County Treasurer, upon surrender of this coupon, Six Thousand Two Hundred Fifty Dollars ($6,250) in lawful money of the United States of America, being six months' interest then due on its Public Improvement Bond dated March&nbsp;1,&nbsp;1948, No.&nbsp;{html.escape(SERIAL).replace(' ', '&nbsp;')}.</div>
<div class="cps"><img src="sig2_strike.png"><div>County Treasurer</div></div></div>''')
    if row == 0:
        svg.append(f'<line x1="90" y1="{PY+40+CH}" x2="{W-90}" y2="{PY+40+CH}" stroke="{GREEN_D}" stroke-width="3" stroke-dasharray="12 9" opacity=".7"/>')

BODY = f"""
<p><span class="sc">Franklin County</span>, a political subdivision duly organized and existing under the Constitution and laws of the State, for value received, hereby acknowledges itself indebted and promises to pay to the bearer of this bond, or, if it be registered, to the registered holder hereof, on the first day of March, 1968, the principal sum of</p>
<p class="amt">FIVE HUNDRED THOUSAND DOLLARS ($500,000)</p>
<p>in lawful money of the United States of America, and to pay interest thereon from the date hereof until payment of said principal sum at the rate of two and one-half per centum (2&frac12;%) per annum, payable semi-annually on the first days of March and September in each year, upon presentation and surrender of the interest coupons hereto annexed as they severally become due. Both principal and interest are payable at the office of the County Treasurer of Franklin County or, at the option of the holder, at the Fiscal Agency of the County in the City and State of New York.</p>
<p>This bond is one of an authorized issue of bonds of like date and tenor, except as to maturity, aggregating Twenty Million Dollars ($20,000,000), issued for the purpose of constructing, widening and paving public highways, roads, bridges and streets within the County, pursuant to the Constitution and statutes of the State and to a resolution of the Board of Supervisors duly adopted on the twelfth day of January, 1948, and approved by more than two-thirds of the qualified electors of the County voting at a special election duly called and held for that purpose.</p>
<p>This bond is transferable by delivery, unless registered as to principal in the name of the holder on the books of the County Treasurer, such registration being noted hereon; after such registration no transfer shall be valid unless made on said books and similarly noted hereon. Such registration shall not affect the negotiability of the coupons, which shall continue to pass by delivery.</p>
<p>It is hereby certified, recited and declared that all acts, conditions and things required to exist, happen and be performed precedent to and in the issuance of this bond have existed, happened and been performed in due time, form and manner as required by law; that the total indebtedness of said County, including this bond, does not exceed any constitutional or statutory limitation; and that provision has been made for the levy and collection of an annual tax sufficient to pay the principal of and interest on this bond as the same become due. The full faith and credit of Franklin County are hereby irrevocably pledged for the punctual payment of the principal of and interest on this bond.</p>
<p><span class="sc">In Witness Whereof</span>, Franklin County has caused this bond to be signed by the Chairman of its Board of Supervisors and by its County Treasurer, and countersigned by the Clerk of said Board, and its corporate seal to be hereunto affixed, and the interest coupons hereto annexed to be authenticated by the facsimile signature of its County Treasurer, and this bond to be dated the first day of March, 1948.</p>
"""

page = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=IM+Fell+English:ital@0;1&family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=Oswald:wght@700&family=Playfair+Display:wght@900&family=UnifrakturMaguntia&family=Inter&display=block" rel="stylesheet">
<style>
html,body{{margin:0;padding:0;}}
.sheet{{position:relative;width:{W}px;height:{H}px;background:{PAPER};overflow:hidden;}}
.sheet svg{{position:absolute;left:0;top:0;}}
.body{{position:absolute;left:330px;top:1500px;width:{W-660}px;font-family:'IM Fell English';font-style:italic;font-size:43px;line-height:1.42;color:{INK};text-align:justify;hyphens:auto;}}
.body p{{margin:0 0 14px 0;text-indent:60px;}}
.body p.amt{{text-indent:0;text-align:center;font-style:normal;font-family:'Libre Caslon Text';font-weight:700;font-size:58px;letter-spacing:4px;margin:6px 0 10px;}}
.sc{{font-variant:small-caps;font-style:normal;letter-spacing:2px;}}
.lab{{position:absolute;font-family:'IM Fell English';font-style:italic;font-size:38px;color:{INK};}}
.labr{{position:absolute;font-family:'Libre Caslon Text';font-weight:700;font-size:26px;letter-spacing:4px;color:{INK};text-transform:uppercase;}}
.imp{{position:absolute;left:0;width:{W}px;text-align:center;font-family:'Libre Caslon Text';font-weight:700;font-size:20px;letter-spacing:6px;color:#444;}}
.cp{{position:absolute;text-align:center;}}
.cpt{{font-family:'Libre Caslon Text';font-weight:700;font-size:30px;letter-spacing:6px;color:{INK};margin-bottom:8px;}}
.cpb{{font-family:'IM Fell English';font-style:italic;font-size:25px;line-height:1.35;color:{INK};text-align:justify;}}
.cps img{{width:230px;display:block;margin:4px auto -10px auto;mix-blend-mode:multiply;}}
.cps div{{border-top:2px solid {INK};margin:0 50px;padding-top:4px;font-family:'Libre Caslon Text';font-weight:700;font-size:18px;letter-spacing:4px;text-transform:uppercase;}}
</style></head><body><div class="sheet">
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{''.join(svg)}</svg>
<div class="body">{BODY}</div>
<div class="lab" style="left:360px;top:3330px;">Countersigned:</div>
<div class="labr" style="left:330px;top:3560px;width:420px;border-top:3px solid {INK};padding-top:8px;text-align:center;">Clerk of the Board<br>of Supervisors</div>
<div class="labr" style="left:1440px;top:3462px;width:780px;border-top:3px solid {INK};padding-top:8px;text-align:center;">Chairman, Board of Supervisors</div>
<div class="labr" style="left:1440px;top:3630px;width:780px;border-top:3px solid {INK};padding-top:8px;text-align:center;">County Treasurer</div>
<div class="imp" style="top:{H_BOND-56}px;">WHITCOMBE &amp; GRAY BANK NOTE COMPANY, NEW YORK &middot; FOR MOTION PICTURE USE ONLY &middot; NOT NEGOTIABLE</div>
{''.join(coupon_html)}
</div></body></html>"""
open(OUT, "w", encoding="utf-8").write(page)
print("ok", W, H)
