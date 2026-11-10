#!/usr/bin/env python3
"""Build the one-page Shot Language cheat sheet: a single HTML file with fonts embedded.

Usage: python3 tools/cheatsheet/build.py <out.html> <font_dir>
The font dir is filled from Google Fonts (Barlow, OFL) on first run.
Print the HTML to PDF (A4 or Letter, landscape, no margins) with any Chromium.
"""
import base64
import math
import pathlib
import re
import subprocess
import sys

OUT = pathlib.Path(sys.argv[1])
FONTS = pathlib.Path(sys.argv[2])

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
CSS_URL = ("https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700"
           "&family=Barlow+Semi+Condensed:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap")


def font_faces():
    FONTS.mkdir(parents=True, exist_ok=True)
    css_file = FONTS / "fonts.css"
    if not css_file.exists():
        subprocess.run(["curl", "-sS", "-A", UA, CSS_URL, "-o", str(css_file)], check=True)
    css = css_file.read_text()
    faces = []
    for b in re.findall(r"/\* latin \*/\s*@font-face\s*\{(.*?)\}", css, re.S):
        fam = re.search(r"font-family: '([^']+)'", b).group(1)
        st = re.search(r"font-style: (\w+)", b).group(1)
        w = re.search(r"font-weight: (\d+)", b).group(1)
        url = re.search(r"url\((.*?)\)", b).group(1)
        rng = re.search(r"unicode-range: ([^;]+);", b).group(1)
        fn = FONTS / f"{fam.replace(' ', '')}-{w}-{st}.woff2"
        if not fn.exists():
            subprocess.run(["curl", "-sS", url, "-o", str(fn)], check=True)
        data = base64.b64encode(fn.read_bytes()).decode()
        faces.append(f"@font-face{{font-family:'{fam}';font-style:{st};font-weight:{w};"
                     f"font-display:block;src:url(data:font/woff2;base64,{data}) format('woff2');"
                     f"unicode-range:{rng};}}")
    return "\n".join(faces)


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def pts(seq):
    return " ".join(f"{f(x)},{f(y)}" for x, y in seq)


# ---------------------------------------------------------------- shared art
INK, BLUE, RED, TAN = "var(--ink)", "var(--blue)", "var(--red)", "var(--tan)"

R_HALF = [(3, 16.5), (3.2, 20.5), (10, 22), (12.8, 24.5), (13.8, 34), (14, 46), (13.6, 57),
          (12.2, 60.5), (10.4, 59.5), (10.0, 57), (9.6, 58), (9.2, 72), (8.2, 86), (7.8, 96),
          (9.6, 99.2), (9.0, 100), (3.0, 100), (2.8, 96), (2.4, 80), (1.6, 64)]
BODY = R_HALF + [(0, 60)] + [(-x, y) for x, y in reversed(R_HALF)]

# figure: 100 units tall, feet at y=100, centred on x=0, eyes at y=8.2
DEFS = f"""
<svg class="defs" width="0" height="0" aria-hidden="true" focusable="false">
 <defs>
  <g id="fig">
   <polygon points="{pts(BODY)}" fill="var(--ink)"/>
   <ellipse cx="0" cy="8.6" rx="6.6" ry="8.3" fill="var(--ink)"/>
   <ellipse cx="-2.7" cy="8.2" rx="1.2" ry="0.85" fill="var(--paper)"/>
   <ellipse cx="2.7" cy="8.2" rx="1.2" ry="0.85" fill="var(--paper)"/>
   <circle cx="-2.6" cy="8.25" r="0.48" fill="var(--ink)"/>
   <circle cx="2.8" cy="8.25" r="0.48" fill="var(--ink)"/>
   <path d="M-4.1 6.2 Q-2.7 5.5 -1.3 6.1 M1.3 6.1 Q2.7 5.5 4.1 6.2" stroke="var(--paper)" stroke-width="0.45" fill="none"/>
  </g>
  <marker id="ah" viewBox="0 0 6 6" refX="4.6" refY="3" markerWidth="2.6" markerHeight="2.6" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0,0 L6,3 L0,6 z" fill="var(--ink)"/></marker>
  <marker id="ahb" viewBox="0 0 6 6" refX="4.6" refY="3" markerWidth="2.6" markerHeight="2.6" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0,0 L6,3 L0,6 z" fill="var(--blue)"/></marker>
  <marker id="ahm" viewBox="0 0 6 6" refX="4.6" refY="3" markerWidth="1.5" markerHeight="1.5" markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0,0 L6,3 L0,6 z" fill="var(--blue)"/></marker>
  <pattern id="hatch" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
   <line x1="0" y1="0" x2="0" y2="1.6" stroke="var(--red)" stroke-width="0.35"/>
  </pattern>
 </defs>
</svg>"""


def cam_side(x, y, s=1.0, rot=0.0, flip=False, color=INK):
    """Film camera seen from the side, lens to the right (or left when flipped)."""
    sx = -s if flip else s
    return (f'<g transform="translate({f(x)},{f(y)}) rotate({f(rot)}) scale({f(sx)},{f(s)})">'
            f'<circle cx="-1.9" cy="-3.6" r="1.55" fill="var(--paper)" stroke="{color}" stroke-width="0.6"/>'
            f'<circle cx="1.5" cy="-3.6" r="1.55" fill="var(--paper)" stroke="{color}" stroke-width="0.6"/>'
            f'<rect x="-3.6" y="-2.2" width="7.2" height="4.4" rx="0.7" fill="{color}"/>'
            f'<polygon points="3.4,-1.2 6,-2.3 6,2.3 3.4,1.2" fill="{color}"/></g>')


def cam_top(x, y, s=1.0, ang=0.0, color=INK):
    """Camera seen from above, lens pointing at angle ang (degrees, 0 = right)."""
    return (f'<g transform="translate({f(x)},{f(y)}) rotate({f(ang)}) scale({f(s)})">'
            f'<rect x="-3" y="-2" width="6" height="4" rx="0.6" fill="{color}"/>'
            f'<polygon points="2.8,-1 5.4,-2.1 5.4,2.1 2.8,1" fill="{color}"/></g>')


def person_top(x, y, s=1.0, color=INK):
    return (f'<g transform="translate({f(x)},{f(y)}) scale({f(s)})">'
            f'<ellipse cx="0" cy="0" rx="3.3" ry="1.9" fill="{color}" opacity="0.55"/>'
            f'<circle cx="0" cy="0" r="1.6" fill="{color}"/></g>')


def bust(cx, cy, s=1.0, color=INK, eyes=True):
    """Head and shoulders, head centre at (cx, cy)."""
    e = ""
    if eyes:
        e = (f'<circle cx="{f(cx - 0.9 * s)}" cy="{f(cy - 0.1 * s)}" r="{f(0.34 * s)}" fill="var(--paper)"/>'
             f'<circle cx="{f(cx + 0.9 * s)}" cy="{f(cy - 0.1 * s)}" r="{f(0.34 * s)}" fill="var(--paper)"/>')
    sh = (f'M{f(cx - 4.4 * s)},{f(cy + 6.5 * s)} Q{f(cx - 4.2 * s)},{f(cy + 3.0 * s)} {f(cx)},{f(cy + 2.8 * s)} '
          f'Q{f(cx + 4.2 * s)},{f(cy + 3.0 * s)} {f(cx + 4.4 * s)},{f(cy + 6.5 * s)} Z')
    return (f'<path d="{sh}" fill="{color}"/><ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(2.05 * s)}" '
            f'ry="{f(2.45 * s)}" fill="{color}"/>{e}')


def arrow(d, color="ah", w=0.55, dash=None, both=False, stroke=INK):
    da = f' stroke-dasharray="{dash}"' if dash else ""
    ms = f' marker-start="url(#{color})"' if both else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}"{da}{ms} marker-end="url(#{color})"/>'


# ---------------------------------------------------------------- 2 SIZE
def size_thumb(kind):
    if kind == "EWS":
        h = 520.0
        y0 = -330.0
    else:
        h, y0 = {"WS": (170, -55), "FS": (110, -6), "MLS": (89, -4), "COWBOY": (74, -3.5),
                 "MS": (54, -3.5), "MCU": (39, -3), "CU": (24, -2.2), "ECU": (8.4, 4.0)}[kind]
    w = h * 16 / 9
    x0 = -w / 2
    if kind == "ECU":
        x0 = -w / 2
    bg = ""
    if kind == "EWS":
        bg = (f'<polygon points="{pts([(x0, 100), (x0, 40), (x0 + 120, -10), (x0 + 260, 60), (x0 + 420, -40), (x0 + 600, 50), (x0 + w, 20), (x0 + w, 100)])}" fill="var(--map2)"/>'
              f'<rect x="{f(x0)}" y="100" width="{f(w)}" height="{f(y0 + h - 100)}" fill="var(--map)"/>'
              f'<path d="M-4 100 L-60 {f(y0 + h)} M4 100 L60 {f(y0 + h)}" stroke="var(--map3)" stroke-width="5" fill="none"/>')
    elif kind in ("WS", "FS"):
        bg = (f'<rect x="{f(x0)}" y="100" width="{f(w)}" height="{f(y0 + h - 100)}" fill="var(--map)"/>'
              f'<line x1="{f(x0)}" y1="100" x2="{f(x0 + w)}" y2="100" stroke="var(--map3)" stroke-width="{f(h / 110)}"/>')
        if kind == "WS":
            bg += ('<rect x="32" y="14" width="34" height="86" fill="none" stroke="var(--map3)" stroke-width="2.4"/>'
                   '<rect x="-92" y="24" width="40" height="30" fill="none" stroke="var(--map3)" stroke-width="2.4"/>')
    return (f'<svg class="thumb" viewBox="{f(x0)} {f(y0)} {f(w)} {f(h)}" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'<rect x="{f(x0)}" y="{f(y0)}" width="{f(w)}" height="{f(h)}" fill="var(--tint)"/>{bg}'
            f'<use href="#fig"/></svg>')


SIZES = [
    ("EWS", "extreme wide", "place and scale"),
    ("WS", "wide", "who is where"),
    ("FS", "full", "walk, stance"),
    ("MLS", "medium long", "standing talk"),
    ("COWBOY", "cowboy", "a reach, a draw"),
    ("MS", "medium", "talk with hands"),
    ("MCU", "medium close-up", "dialogue"),
    ("CU", "close-up", "the reaction"),
    ("ECU", "extreme close-up", "one detail"),
]


def size_grid():
    cells = []
    for k, name, use in SIZES:
        label = "" if k == "COWBOY" else f"<b>{k}</b> "
        if k == "COWBOY":
            name = "<b>COWBOY</b>"
        cells.append(f'<figure class="sz">{size_thumb(k)}<figcaption>{label}{name}'
                     f'<i>{use}</i></figcaption></figure>')
    return '<div class="szgrid">' + "".join(cells) + "</div>"


# ---------------------------------------------------------------- 3 ANGLE / FRAMING
def angle_icon(kind):
    vb = "0 0 30 22"
    ground = '<line x1="0" y1="20.5" x2="30" y2="20.5" stroke="var(--map3)" stroke-width="0.6"/>'
    fig = '<use href="#fig" transform="translate(22,2.5) scale(0.18)"/>'
    eye = (22, 4.0)
    if kind == "eye":
        art = ground + fig + cam_side(6.5, 4.6, 0.62) + arrow("M10.6 4.3 L18.6 4.3", "ahm", 0.4, "1 0.7")
    elif kind == "high":
        art = ground + fig + cam_side(5.4, 2.6, 0.58, 28) + arrow("M9 4.6 L18.7 9.6", "ahm", 0.4, "1 0.7")
    elif kind == "low":
        art = ground + fig + cam_side(5.6, 18.2, 0.58, -32) + arrow("M9.2 15.9 L18.8 8.8", "ahm", 0.4, "1 0.7")
    elif kind == "over":
        art = ('<rect x="5" y="1" width="20" height="20" fill="var(--map)" stroke="var(--map3)" stroke-width="0.4"/>'
               '<path d="M5 8 H25 M5 15 H25 M12 1 V21 M19 1 V21" stroke="var(--map2)" stroke-width="0.4"/>'
               + person_top(15, 11, 1.25))
    else:  # dutch
        art = ('<g transform="rotate(-16 15 11)"><rect x="4" y="2.5" width="22" height="17" fill="var(--tint)" '
               'stroke="var(--ink)" stroke-width="0.5"/><line x1="4" y1="14" x2="26" y2="14" stroke="var(--map3)" stroke-width="0.6"/>'
               '<use href="#fig" transform="translate(15,4.5) scale(0.145)"/></g>')
    return f'<svg class="ico" viewBox="{vb}" aria-hidden="true">{art}</svg>'


ANGLES = [("eye", "Eye level", "neutral"),
          ("high", "High", "exposed"),
          ("low", "Low", "imposing"),
          ("over", "Overhead", "a map"),
          ("dutch", "Dutch", "unease")]


def frame_icon(kind):
    bg = '<rect x="0" y="0" width="32" height="18" fill="var(--tint)"/>'
    if kind == "single":
        art = bust(16, 7.5, 1.35)
    elif kind == "two":
        art = bust(10, 8.5, 1.0) + bust(22, 8.5, 1.0)
    elif kind == "ots":
        art = bust(20, 7.6, 1.05) + (
            '<path d="M-2 18 Q-1 10 6 9.6 Q9.6 9.6 10.6 12 Q12 18 12 18 Z" fill="var(--map3)"/>'
            '<ellipse cx="6.2" cy="5.6" rx="3.6" ry="4.4" fill="var(--map3)"/>')
    else:  # pov
        art = (bust(16, 6.6, 1.0) +
               '<path d="M5 18 Q6 13.6 9 13.4 Q11.4 13.6 11.6 18 Z M27 18 Q26 13.6 23 13.4 Q20.6 13.6 20.4 18 Z" fill="var(--map3)"/>'
               '<rect x="12.6" y="12.6" width="6.8" height="5.4" rx="0.8" fill="var(--paper)" stroke="var(--map3)" stroke-width="0.6"/>')
    return (f'<svg class="frm" viewBox="0 0 32 18" aria-hidden="true">{bg}{art}'
            f'<rect x="0.25" y="0.25" width="31.5" height="17.5" fill="none" stroke="var(--ink)" stroke-width="0.5"/></svg>')


FRAMES = [("single", "Single", "one person"),
          ("two", "Two-shot", "two together"),
          ("ots", "OTS", "over a shoulder"),
          ("pov", "POV", "their eyes")]


# ---------------------------------------------------------------- 4 MOVE
def move_icon(kind):
    subj = '<circle cx="{x}" cy="{y}" r="1.7" fill="var(--blue)"/>'
    a = ""
    if kind == "static":
        a = (cam_side(12, 5.5, 0.62) +
             '<path d="M12 7 L8 15 M12 7 L16 15 M12 7 L12 15" stroke="var(--ink)" stroke-width="0.5"/>')
    elif kind == "pan":
        a = cam_top(12, 9, 0.7, -90) + arrow("M5.6 5.4 A7 7 0 0 1 18.4 5.4", "ah", 0.5, both=True)
    elif kind == "tilt":
        a = cam_side(9, 8, 0.62) + arrow("M15.6 3.2 A7 7 0 0 1 15.6 12.8", "ah", 0.5, both=True)
    elif kind == "dolly":
        a = ('<path d="M2 6 H17 M2 10 H17" stroke="var(--map3)" stroke-width="0.5"/>'
             '<path d="M4 5.4 V10.6 M7 5.4 V10.6 M10 5.4 V10.6 M13 5.4 V10.6 M16 5.4 V10.6" stroke="var(--map3)" stroke-width="0.35"/>'
             + cam_top(6, 8, 0.7, 0) + arrow("M10.5 8 H17.4", "ah", 0.55, both=True) + subj.format(x=21.5, y=8))
    elif kind == "truck":
        a = cam_top(8, 11, 0.7, -90) + arrow("M11.5 13.6 H21", "ah", 0.55) + subj.format(x=12, y=3)
    elif kind == "track":
        a = (subj.format(x=12, y=3.6) + arrow("M15 3.6 H21.6", "ahb", 0.5, stroke=BLUE) +
             cam_top(12, 12.4, 0.7, -90) + arrow("M15 12.4 H21.6", "ah", 0.55))
    elif kind == "arc":
        a = (subj.format(x=12, y=6) + arrow("M5.5 9.5 A7 7 0 0 0 18.5 9.5", "ah", 0.5, "1 0.6") +
             cam_top(5.6, 11.8, 0.62, -60))
    elif kind == "crane":
        a = (cam_side(8, 5, 0.6) + '<path d="M8 7.4 L13 15.4" stroke="var(--ink)" stroke-width="0.7"/>' +
             arrow("M18 14.6 V2.4", "ah", 0.55, both=True))
    elif kind == "zoom":
        a = (cam_top(4.6, 8, 0.65, 0) +
             '<path d="M8.4 8 L22 1 M8.4 8 L22 15" stroke="var(--map3)" stroke-width="0.45" stroke-dasharray="1 0.6"/>'
             '<path d="M8.4 8 L22 5.2 M8.4 8 L22 10.8" stroke="var(--ink)" stroke-width="0.5"/>' +
             arrow("M19.4 2.6 Q20.6 4 20.3 5.2", "ah", 0.4))
    elif kind == "dzoom":
        a = (cam_top(8, 8, 0.65, 0) + arrow("M6.5 12.6 H1.4", "ah", 0.5) +
             '<path d="M11.8 8 L21.5 5.4 M11.8 8 L21.5 10.6" stroke="var(--ink)" stroke-width="0.5"/>' +
             subj.format(x=21.2, y=8))
    elif kind == "hand":
        a = (cam_side(12, 6, 0.62, -8) +
             '<path d="M2 13 Q4.5 10.5 7 13 T12 13 T17 13 T22 13" fill="none" stroke="var(--ink)" stroke-width="0.5"/>')
    elif kind == "whip":
        a = (cam_top(12, 10, 0.7, -90) + arrow("M4.6 7.6 A8 8 0 0 1 19.4 7.6", "ah", 0.6) +
             '<path d="M6 3 L9.6 3.8 M8.8 1.4 L12 2.6 M12.4 0.8 L15 2" stroke="var(--ink)" stroke-width="0.4"/>')
    else:  # roll
        a = ('<g transform="rotate(-18 12 8)"><rect x="5" y="3.6" width="14" height="8.8" fill="var(--tint)" stroke="var(--ink)" stroke-width="0.45"/>'
             '<line x1="5" y1="9" x2="19" y2="9" stroke="var(--map3)" stroke-width="0.5"/></g>' +
             arrow("M20.6 4.4 A9 9 0 0 1 20.2 12.4", "ah", 0.5))
    return f'<svg class="mico" viewBox="0 0 24 16" aria-hidden="true">{a}</svg>'


MOVES = [("static", "Static", "frame holds still"),
         ("pan", "Pan", "turns left or right"),
         ("tilt", "Tilt", "looks up or down"),
         ("dolly", "Dolly in / out", "travels closer, away"),
         ("truck", "Truck", "slides sideways"),
         ("track", "Track / follow", "travels with them"),
         ("arc", "Arc / orbit", "circles around"),
         ("crane", "Crane / pedestal", "rises or lowers"),
         ("zoom", "Zoom", "lens tightens"),
         ("dzoom", "Dolly zoom", "the room warps"),
         ("hand", "Handheld", "alive, nervous"),
         ("whip", "Whip pan", "snap turn, blur"),
         ("roll", "Roll", "horizon rotates")]


# ---------------------------------------------------------------- 5 LENS
def lens_fan():
    cx, cy, R = 3.4, 9.0, 12.5
    lenses = [18, 24, 35, 50, 85, 135]
    shades = ["var(--fan1)", "var(--fan2)", "var(--fan3)", "var(--fan4)", "var(--fan5)", "var(--fan6)"]
    rows = [1.7, 4.2, 7.6, 10.1, 13.5, 16.0]
    out = []
    for i, mm in enumerate(lenses):
        a = math.atan(18 / mm)
        x1, y1 = cx + R * math.cos(a), cy - R * math.sin(a)
        x2, y2 = cx + R * math.cos(a), cy + R * math.sin(a)
        out.append(f'<path d="M{f(cx)},{f(cy)} L{f(x1)},{f(y1)} A{R},{R} 0 0 1 {f(x2)},{f(y2)} Z" '
                   f'fill="{shades[i]}" stroke="var(--paper)" stroke-width="0.25"/>')
    for i, mm in enumerate(lenses):
        a = math.atan(18 / mm)
        x1, y1 = cx + R * math.cos(a), cy - R * math.sin(a)
        ly = rows[i]
        out.append(f'<path d="M{f(x1)},{f(y1)} L18.6,{f(ly - 0.6)} H19.4" stroke="var(--ink2)" stroke-width="0.2" fill="none"/>'
                   f'<circle cx="{f(x1)}" cy="{f(y1)}" r="0.32" fill="var(--ink)"/>'
                   f'<text x="19.8" y="{f(ly)}" class="t-lab">{mm}mm</text>'
                   f'<text x="26.6" y="{f(ly)}" class="t-num">{round(2 * math.degrees(a))}°</text>')
    groups = [(0, "WIDE", "the room grows, edges bend"), (2, "NORMAL", "close to the human eye"),
              (4, "LONG", "faces flatten, background close")]
    for i, tag, txt in groups:
        y1, y2 = rows[i] - 2.0, rows[i + 1] + 0.5
        out.append(f'<path d="M30.6,{f(y1)} h0.8 V{f(y2)} h-0.8" stroke="var(--blue)" stroke-width="0.3" fill="none"/>'
                   f'<text x="32.6" y="{f(rows[i])}" class="t-tag">{tag}</text>'
                   f'<text x="32.6" y="{f(rows[i + 1])}" class="t-sub2">{txt}</text>')
    out.append(cam_top(cx - 0.4, cy, 0.55, 0))
    return f'<svg class="fan" viewBox="0 0 61 17.4" aria-hidden="true">{"".join(out)}</svg>'


# ---------------------------------------------------------------- 6 LIGHT
def light_plot():
    a = ['<rect x="0" y="0" width="26" height="23" rx="1" fill="var(--tint)"/>']
    # rays
    a.append('<path d="M5.4 5.2 L11.4 10.2 M6.6 4 L12.4 9.4" stroke="var(--warm2)" stroke-width="0.9"/>')
    a.append('<path d="M20.4 10.6 L15 11.6" stroke="var(--warm2)" stroke-width="0.6" stroke-dasharray="0.8 0.6"/>')
    a.append('<path d="M15.2 2.6 L13.6 8.2" stroke="var(--warm2)" stroke-width="0.6"/>')
    # lights
    for x, y, r in ((4.6, 4.2, 2.1), (21.4, 10.6, 1.5), (15.6, 1.9, 1.3)):
        a.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="var(--warm)" stroke="var(--ink)" stroke-width="0.35"/>')
    a.append(person_top(13, 11.4, 1.0))
    a.append('<path d="M13 12.9 L13 13.9" stroke="var(--ink)" stroke-width="0.6"/>')
    a.append(cam_top(13, 20.2, 0.6, -90))
    a.append('<text x="1" y="9.6" class="t-lab">KEY</text><text x="18.6" y="14.6" class="t-lab">FILL</text>'
             '<text x="18" y="2.9" class="t-lab">BACK</text><text x="16" y="21.6" class="t-lab">CAM</text>')
    return f'<svg class="plot" viewBox="0 0 26 23" aria-hidden="true">{"".join(a)}</svg>'


# ---------------------------------------------------------------- 10 CUT
def jl(kind):
    if kind == "J":
        aud = ('<rect x="0.3" y="5.2" width="10" height="3.2" fill="var(--map3)"/>'
               '<rect x="10.3" y="5.2" width="15.4" height="3.2" fill="var(--ink2)"/>')
    else:
        aud = ('<rect x="0.3" y="5.2" width="17" height="3.2" fill="var(--map3)"/>'
               '<rect x="17.3" y="5.2" width="8.4" height="3.2" fill="var(--ink2)"/>')
    return (f'<svg class="jl" viewBox="0 0 32 9" aria-hidden="true">'
            '<rect x="0.3" y="0.6" width="13" height="3.6" fill="var(--tan)"/>'
            '<rect x="13.3" y="0.6" width="12.4" height="3.6" fill="var(--tan2)"/>'
            '<text x="5.6" y="3.4" class="t-lab">A</text><text x="18.6" y="3.4" class="t-lab">B</text>'
            f'{aud}<text x="27" y="3.4" class="t-lab">PIC</text><text x="27" y="8" class="t-lab">SND</text></svg>')


# ---------------------------------------------------------------- 1 THE SET (isometric map)
S_ = 0.72
CX, SY = math.cos(math.radians(30)) * S_, 0.5 * S_
OX, OY = 51.9, 12.0


def iso(x, y, z=0.0):
    return (OX + (x - y) * CX, OY + (x + y) * SY - z * S_)


def ipoly(seq, **kw):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<polygon points="{pts([iso(*p) for p in seq])}" {attrs}/>'


def iline(p, q, **kw):
    attrs = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in kw.items())
    (x1, y1), (x2, y2) = iso(*p), iso(*q)
    return f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" {attrs}/>'


def floor_text(x, y, text, cls, size=3.4):
    px, py = iso(x, y)
    m = f"matrix({f(CX / S_ * S_)},{f(SY)},{f(-CX)},{f(SY)},{f(px)},{f(py)})"
    return f'<text transform="{m}" class="{cls}" style="font-size:{size}px">{text}</text>'


def cone(x, y, ang, half, length, color="var(--blue)", op=0.13):
    a1, a2 = math.radians(ang - half), math.radians(ang + half)
    p1 = (x + length * math.cos(a1), y + length * math.sin(a1))
    p2 = (x + length * math.cos(a2), y + length * math.sin(a2))
    return ipoly([(x, y), p1, p2], fill=color, fill_opacity=op, stroke=color, stroke_width="0.25",
                 stroke_opacity="0.6")


def iso_cam(x, y, z, facing_screen_right, color=INK, legs=True):
    px, py = iso(x, y, z)
    g = ""
    if legs:
        for dx, dy in ((-2.2, 1.2), (2.2, 1.2), (0, -2.4)):
            fx, fy = iso(x + dx, y + dy, 0)
            g += f'<line x1="{f(px)}" y1="{f(py + 1.2)}" x2="{f(fx)}" y2="{f(fy)}" stroke="{color}" stroke-width="0.32"/>'
    return g + cam_side(px, py, 0.5, 0, not facing_screen_right, color)


def iso_person(x, y, label):
    px, py = iso(x, y)
    hgt = 14 * S_
    k = hgt / 100
    return (f'<ellipse cx="{f(px)}" cy="{f(py)}" rx="2.2" ry="1.1" fill="var(--ink)" opacity="0.18"/>'
            f'<use href="#fig" transform="translate({f(px)},{f(py - hgt)}) scale({f(k)})"/>'
            f'<circle cx="{f(px)}" cy="{f(py - hgt - 2.6)}" r="1.75" fill="var(--paper)" stroke="var(--ink)" stroke-width="0.35"/>'
            f'<text x="{f(px)}" y="{f(py - hgt - 1.85)}" class="t-badge">{label}</text>')


def leader(tx, ty, start, ax, ay, text, anchor="start", cls="t-lab", sub=None, color="var(--ink2)"):
    lines = f'<text x="{f(tx)}" y="{f(ty)}" class="{cls}" text-anchor="{anchor}">{text}</text>'
    if sub:
        lines += f'<text x="{f(tx)}" y="{f(ty + 2.3)}" class="t-sub" text-anchor="{anchor}">{sub}</text>'
    sx, sy = start
    return (f'<path d="M{f(sx)},{f(sy)} L{f(ax)},{f(ay)}" stroke="{color}" stroke-width="0.22" fill="none"/>'
            f'<circle cx="{f(ax)}" cy="{f(ay)}" r="0.45" fill="var(--ink)"/>' + lines)


def mini_frame(x, y, crossed=False):
    w, h = 31.0, 17.4
    a = [f'<g transform="translate({f(x)},{f(y)})">',
         f'<rect x="0" y="0" width="{w}" height="{h}" fill="var(--tint)"/>',
         f'<rect x="0" y="11.6" width="{w}" height="{f(h - 11.6)}" fill="var(--map)"/>']
    if not crossed:
        a.append('<rect x="0" y="2" width="2.6" height="8" fill="var(--warm)" opacity="0.9"/>')
    left, right = ("B", "A") if crossed else ("A", "B")
    a.append('<rect x="11.4" y="10" width="8.2" height="2.6" fill="var(--map3)"/>')
    a.append('<use href="#fig" transform="translate(8,3.2) scale(0.1)"/>')
    a.append('<use href="#fig" transform="translate(23,3.2) scale(0.1)"/>')
    a.append(f'<text x="8" y="2.6" class="t-badge2">{left}</text><text x="23" y="2.6" class="t-badge2">{right}</text>')
    stroke = "var(--red)" if crossed else "var(--ink)"
    a.append(f'<rect x="0.2" y="0.2" width="{w - 0.4}" height="{h - 0.4}" fill="none" stroke="{stroke}" stroke-width="0.5"/>')
    if crossed:
        a.append('<path d="M26.6 1.6 L29.6 4.6 M29.6 1.6 L26.6 4.6" stroke="var(--red)" stroke-width="0.7"/>')
    a.append("</g>")
    return "".join(a)


def set_map():
    W, H = 127, 88
    o = [f'<svg class="map" viewBox="0 0 {W} {H}" role="img" aria-label="Isometric set plan: two people at a table, '
         'the 180 degree line between them, camera setups on one side, a window as key light.">']
    # walls
    o.append(ipoly([(0, 0, 0), (0, 64, 0), (0, 64, 14), (0, 0, 14)], fill="var(--wall1)", stroke="var(--map3)", stroke_width="0.3"))
    o.append(ipoly([(0, 0, 0), (100, 0, 0), (100, 0, 14), (0, 0, 14)], fill="var(--wall2)", stroke="var(--map3)", stroke_width="0.3"))
    # window (left wall) and door (back wall)
    o.append(ipoly([(0, 38, 4.5), (0, 52, 4.5), (0, 52, 12), (0, 38, 12)], fill="var(--warm)", stroke="var(--ink2)", stroke_width="0.3"))
    o.append(iline((0, 45, 4.5), (0, 45, 12), stroke="var(--ink2)", stroke_width="0.25"))
    o.append(ipoly([(70, 0, 0), (81, 0, 0), (81, 0, 11), (70, 0, 11)], fill="var(--map3)", stroke="var(--ink2)", stroke_width="0.3"))
    # floor and grid
    o.append(ipoly([(0, 0), (100, 0), (100, 64), (0, 64)], fill="var(--map)", stroke="var(--map3)", stroke_width="0.35"))
    for gx in range(10, 100, 10):
        o.append(iline((gx, 0), (gx, 64), stroke="var(--map2)", stroke_width="0.2"))
    for gy in range(8, 64, 8):
        o.append(iline((0, gy), (100, gy), stroke="var(--map2)", stroke_width="0.2"))
    # forbidden half
    o.append(ipoly([(0, 0), (100, 0), (100, 30), (0, 30)], fill="url(#hatch)", opacity="0.45"))
    # window light on the floor
    o.append(ipoly([(0, 38), (0, 52), (33, 41), (33, 27)], fill="var(--warm)", opacity="0.55"))
    # floor words
    o.append(floor_text(6, 58, "CAMERA SIDE", "t-floor"))
    o.append(floor_text(54, 8.5, "OTHER SIDE", "t-floorr"))
    # cones
    o.append(cone(50, 57, -90, 30, 20))
    o.append(cone(25, 37, -9, 17, 30))
    o.append(cone(82, 40, 192, 15, 32))
    o.append(cone(50, 6, 90, 24, 18, "var(--red)", 0.1))
    # dolly track
    for xx in (47.6, 52.4):
        o.append(iline((xx, 47), (xx, 63), stroke="var(--ink2)", stroke_width="0.35"))
    for yy in range(48, 64, 2):
        o.append(iline((46.8, yy), (53.2, yy), stroke="var(--ink2)", stroke_width="0.2"))
    ax1, ay1 = iso(56, 58)
    ax2, ay2 = iso(56, 48)
    o.append(arrow(f"M{f(ax1)} {f(ay1)} L{f(ax2)} {f(ay2)}", "ahb", 0.45, stroke=BLUE))
    # the line
    o.append(iline((0, 30), (100, 30), stroke="var(--red)", stroke_width="0.7", stroke_dasharray="2 1.2"))
    # objects, back to front
    objs = []
    # lamp (practical)
    lx, ly = iso(92, 9)
    tx, ty = iso(92, 9, 12)
    objs.append((101, f'<circle cx="{f(tx)}" cy="{f(ty + 0.6)}" r="4.2" fill="var(--warm)" opacity="0.6"/>'
                      f'<line x1="{f(lx)}" y1="{f(ly)}" x2="{f(tx)}" y2="{f(ty)}" stroke="var(--ink)" stroke-width="0.4"/>'
                      f'<polygon points="{f(tx - 1.6)},{f(ty + 0.9)} {f(tx + 1.6)},{f(ty + 0.9)} {f(tx + 1)},{f(ty - 1.3)} {f(tx - 1)},{f(ty - 1.3)}" fill="var(--ink)"/>'))
    # crossed camera (forbidden side), faces +y: screen down-left
    objs.append((56, iso_cam(50, 6, 9, False, "var(--red)")))
    # table
    tb = ("".join([
        ipoly([(43, 35, 0), (57, 35, 0), (57, 35, 7.5), (43, 35, 7.5)], fill="var(--map3)", stroke="var(--ink2)", stroke_width="0.25"),
        ipoly([(57, 25, 0), (57, 35, 0), (57, 35, 7.5), (57, 25, 7.5)], fill="var(--wall1)", stroke="var(--ink2)", stroke_width="0.25"),
        ipoly([(43, 25, 7.5), (57, 25, 7.5), (57, 35, 7.5), (43, 35, 7.5)], fill="var(--paper)", stroke="var(--ink2)", stroke_width="0.25"),
    ]))
    kx, ky = iso(51, 30, 7.5)
    tb += f'<circle cx="{f(kx)}" cy="{f(ky)}" r="0.9" fill="var(--gold)" stroke="var(--ink)" stroke-width="0.25"/>'
    objs.append((80, tb))
    objs.append((66, iso_person(36, 30, "A")))
    objs.append((94, iso_person(64, 30, "B")))
    objs.append((62, iso_cam(25, 37, 9.5, True)))
    objs.append((122, iso_cam(82, 40, 9.5, False)))
    objs.append((110, iso_cam(50, 57, 9.5, True)))
    for _, svg in sorted(objs, key=lambda t: t[0]):
        o.append(svg)
    # eyeline
    ea = iso(36, 30, 13)
    eb = iso(64, 30, 13)
    o.append(f'<path d="M{f(ea[0] + 1.2)} {f(ea[1] + 0.7)} L{f(eb[0] - 1.2)} {f(eb[1] - 0.7)}" stroke="var(--blue)" '
             f'stroke-width="0.4" stroke-dasharray="0.9 0.6" marker-start="url(#ahm)" marker-end="url(#ahm)" fill="none"/>')
    o.append(f'<text x="{f((ea[0] + eb[0]) / 2 + 1.6)}" y="{f((ea[1] + eb[1]) / 2 - 1.2)}" class="t-eye">EYELINE</text>')
    # insert camera above the table
    ix, iy = iso(51, 30, 33)
    o.append(f'<line x1="{f(ix)}" y1="{f(iy + 3)}" x2="{f(kx)}" y2="{f(ky - 1.2)}" stroke="var(--blue)" stroke-width="0.35" stroke-dasharray="0.9 0.6"/>')
    o.append(cam_side(ix, iy, 0.5, 90))
    # labels (engine-cutaway style)
    wx, wy = iso(0, 45, 9)
    o.append(leader(2, 4.5, (9, 7.4), wx, wy, "KEY LIGHT · WINDOW", sub="screen-left in the master"))
    o.append(leader(124, 4.5, (100.4, 3.9), ix + 2.6, iy, "INSERT · FROM ABOVE", "end", sub="a detail: the keys"))
    cxr, cyr = iso(50, 6, 9)
    o.append(leader(124, 12, (96.8, 11.4), cxr + 2.6, cyr - 1, "CROSSED THE LINE", "end", cls="t-labr",
                    sub="A and B swap sides on screen"))
    lpx, lpy = iso(92, 9, 13)
    o.append(leader(124, 20, (112, 23.3), lpx + 1.6, lpy - 1.4, "PRACTICAL · LAMP", "end", sub="a light you can see"))
    c1 = iso(25, 37, 9.5)
    o.append(leader(2, 42, (12.6, 41.4), c1[0] - 3, c1[1] + 0.5, "OTS ON B", sub="over A's shoulder"))
    c2 = iso(82, 40, 9.5)
    o.append(leader(124, 55, (106.8, 54.4), c2[0] + 3.2, c2[1] + 0.2, "OTS ON A", "end", sub="over B's shoulder"))
    l1 = iso(99, 30)
    o.append(leader(124, 61, (100.4, 60.4), l1[0], l1[1], "THE LINE · 180° RULE", "end", cls="t-labr",
                    sub="cameras stay on one side"))
    c3 = iso(50, 57, 9.5)
    o.append(leader(40, 79.5, (44, 77.4), c3[0] - 1, c3[1] + 2.4, "MASTER · WIDE", sub="the whole scene, one take"))
    dt = iso(52.4, 62)
    o.append(leader(70, 79.5, (69.2, 78.9), dt[0] + 0.4, dt[1] + 0.2, "DOLLY TRACK", sub="push in toward the table"))
    # insets
    o.append(mini_frame(2, 58.4))
    o.append('<text x="2" y="57.4" class="t-lab">WHAT THE MASTER SEES</text>')
    o.append('<text x="2" y="78.4" class="t-sub">screen-left</text><text x="33" y="78.4" class="t-sub" text-anchor="end">screen-right</text>')
    o.append(mini_frame(93, 65, crossed=True))
    o.append('<text x="124" y="85" class="t-labr" text-anchor="end">FROM THE OTHER SIDE</text>')
    o.append('<text x="124" y="87.3" class="t-sub" text-anchor="end">same scene, A and B flipped</text>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- 7 BEATS (Minard band)
def beats():
    x0, k = 15.0, 11.55  # x = x0 + t*k, t in seconds, 0..8

    def X(t):
        return x0 + t * k
    o = ['<svg class="beats" viewBox="0 0 127 27" role="img" aria-label="A shot timeline of 8 seconds in three beats.">']
    # picture band, Minard tan
    o.append(f'<polygon points="{f(X(0))},8.6 {f(X(8))},9.6 {f(X(8))},14 {f(X(0))},15" fill="var(--tan)" stroke="var(--tanline)" stroke-width="0.3"/>')
    for t in (3, 6):
        o.append(f'<line x1="{f(X(t))}" y1="7.6" x2="{f(X(t))}" y2="20.4" stroke="var(--ink)" stroke-width="0.3" stroke-dasharray="0.8 0.5"/>')
    # sound band, Minard black
    o.append(f'<rect x="{f(X(0))}" y="16.6" width="{f(8 * k)}" height="1.1" fill="var(--ink)"/>')
    for t1, t2, who in ((1, 3, "A"), (6, 8, "B")):
        o.append(f'<rect x="{f(X(t1))}" y="15.8" width="{f((t2 - t1) * k)}" height="2.7" rx="0.4" fill="var(--ink)"/>'
                 f'<text x="{f(X(t1) + 1)}" y="17.85" class="t-inv">{who} {{line}} {t1}-{t2}s</text>')
    # axis
    o.append(f'<line x1="{f(X(0))}" y1="21.6" x2="{f(X(8))}" y2="21.6" stroke="var(--ink2)" stroke-width="0.25"/>')
    for t in range(9):
        o.append(f'<line x1="{f(X(t))}" y1="21" x2="{f(X(t))}" y2="22.2" stroke="var(--ink2)" stroke-width="0.25"/>'
                 f'<text x="{f(X(t))}" y="24.6" class="t-sub" text-anchor="middle">{t}s</text>')
    o.append('<text x="0.5" y="12.8" class="t-lab">PICTURE</text><text x="0.5" y="18" class="t-lab">SOUND</text>'
             '<text x="0.5" y="24.6" class="t-lab">TIME</text>')
    caps = [(0, "0-3s · MS, eye level, static", "A holds the keys"),
            (3, "3-6s · A sets them down", "the metal taps on wood"),
            (6, "6-8s · B looks", "at the keys, then at A")]
    for t, l1, l2 in caps:
        o.append(f'<text x="{f(X(t) + 0.8)}" y="3" class="t-lab">{l1}</text>'
                 f'<text x="{f(X(t) + 0.8)}" y="5.6" class="t-sub">{l2}</text>')
    # final frame card
    o.append(f'<path d="M{f(X(8))} 11.8 H110.4" stroke="var(--ink)" stroke-width="0.35" marker-end="url(#ah)"/>')
    o.append('<rect x="110.6" y="5" width="16" height="13.4" rx="0.8" fill="var(--paper)" stroke="var(--ink)" stroke-width="0.4"/>'
             '<text x="118.6" y="8.6" class="t-lab" text-anchor="middle">FINAL FRAME</text>'
             '<text x="118.6" y="11.4" class="t-sub" text-anchor="middle">A\'s hand on keys</text>'
             '<text x="118.6" y="13.8" class="t-sub" text-anchor="middle">their eyes meet</text>'
             '<text x="118.6" y="16.2" class="t-sub" text-anchor="middle">camera unmoved</text>')
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- page
CSS = r"""
:root{
  /* Layout: one landscape print sheet, 269 x 200 mm (fits A4 and US Letter): a level-design map in the
     centre (the set), numbered boxes around it, numbered in the order a brief is written. */
  --paper:#fdfdfb; --ink:#17191d; --ink2:#555b63; --rule:#aab6c1; --tint:#eef1f3;
  --blue:#2a5fa5; --blue-t:#edf2f9; --red:#c03a2b; --tan:#e0c194; --tan2:#cfa86f; --tanline:#9d7a4c;
  --map:#e6e9ec; --map2:#d3d8dd; --map3:#b6bec6; --wall1:#cfd5db; --wall2:#dde2e6;
  --warm:#f6dc8f; --warm2:#e7bd4a; --gold:#d9a52b; --desk:#d7dbdf;
  --fan1:#e5ebf2; --fan2:#cfdbe9; --fan3:#adc3dc; --fan4:#86a6cb; --fan5:#5b84b6; --fan6:#2a5fa5;
  --f-head:"Barlow Condensed","Roboto Condensed","Arial Narrow",sans-serif;
  --f-body:"Barlow Semi Condensed","Roboto Condensed","Arial Narrow",Arial,sans-serif;
  color-scheme:light;
}
html,body{background:var(--desk);color:var(--ink)}
body{margin:0}
.desk{padding-block:24px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
.sheet{background:var(--paper);color:var(--ink);font-family:var(--f-body);font-size:6.7pt;line-height:1.2;
  margin:0 auto;max-width:269mm;box-shadow:0 2px 14px rgba(20,30,40,.18);padding:4mm;display:flex;flex-direction:column;gap:3mm}
.defs{position:absolute;width:0;height:0;overflow:hidden}
b{font-weight:600}
i{font-style:italic}
.head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:2mm 6mm;border-bottom:.35mm solid var(--ink);padding-bottom:1.2mm}
.head h1{font:700 17pt/0.9 var(--f-head);letter-spacing:.05em;margin:0;text-transform:uppercase}
.head .sub{font:italic 500 6.6pt/1.15 var(--f-body);color:var(--blue);margin-top:.5mm}
.facts{display:flex;flex-wrap:wrap;gap:1.2mm;justify-content:flex-end;max-width:205mm}
.facts span{border:.25mm solid var(--rule);border-radius:1.2mm;padding:.5mm 1.4mm;font-size:6.3pt;white-space:nowrap}
.cols{display:flex;flex-direction:column;gap:2.4mm}
.col{display:flex;flex-direction:column;gap:2.2mm;min-width:0}
.col>.box:last-child{flex:1}
.box{border:.3mm solid var(--rule);border-radius:2.2mm;padding:1.2mm 1.9mm 1.4mm;min-width:0}
.box.key{border:.55mm solid var(--blue);background:var(--blue-t)}
.bh{display:flex;align-items:baseline;gap:1.4mm;margin-bottom:1mm;flex-wrap:wrap}
.num{width:4.2mm;height:4.2mm;border-radius:50%;background:var(--ink);color:var(--paper);font:700 7.6pt/4.2mm var(--f-head);text-align:center;flex:none;align-self:center}
.key .num{background:var(--blue)}
.bh h2{font:700 10.4pt/1 var(--f-head);letter-spacing:.05em;text-transform:uppercase;margin:0}
.eye{font:italic 500 6.4pt/1.1 var(--f-body);color:var(--blue)}
.note{margin:1mm 0 0;color:var(--ink)}
.note b{color:var(--ink)}
.rule{margin:.9mm 0 0;padding-top:.7mm;border-top:.2mm dashed var(--rule);font-weight:500}
/* 2 size */
.szgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.1mm 1.6mm}
.sz{margin:0;min-width:0}
.thumb{display:block;width:100%;aspect-ratio:16/9;border:.25mm solid var(--ink);box-sizing:border-box}
.sz figcaption{margin-top:.4mm;font-size:6.2pt;line-height:1.1;white-space:nowrap}
.sz figcaption b{font-family:var(--f-head);font-weight:700;font-size:7pt;letter-spacing:.03em}
.sz figcaption i{display:block;color:var(--ink2)}
/* 3 angle */
.angrow{display:grid;grid-template-columns:repeat(5,1fr);gap:1.2mm}
.ang{min-width:0;font-size:6.1pt;line-height:1.1}
.ico{display:block;width:100%;aspect-ratio:30/22;margin-bottom:.4mm}
.ang b{display:block;font-family:var(--f-head);font-weight:700;font-size:6.9pt;letter-spacing:.03em}
.ang i{color:var(--ink2)}
.frrow{display:grid;grid-template-columns:repeat(4,1fr);gap:1.4mm;margin-top:1.4mm}
.frm{display:block;width:100%;aspect-ratio:16/9;margin-bottom:.4mm}
.sublab{font:600 6.4pt/1 var(--f-head);letter-spacing:.08em;color:var(--blue);text-transform:uppercase;margin:1.4mm 0 .2mm}
.terms{margin:.7mm 0 0;padding:0;list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:.15mm 2mm}
.terms li{min-width:0}
.terms.one{grid-template-columns:1fr}
/* 4 move */
.mvgrid{display:grid;grid-template-columns:1fr 1fr;gap:.7mm 1.8mm}
.mv{display:grid;grid-template-columns:9.4mm 1fr;gap:1.1mm;align-items:center;min-width:0;line-height:1.1}
.mico{width:9.4mm;height:6.3mm;display:block;background:var(--tint);border-radius:.8mm}
.mv b{display:block;font-family:var(--f-head);font-weight:700;font-size:6.8pt;letter-spacing:.02em;line-height:1.05}
.mv i{color:var(--ink2);font-size:6.1pt}
/* 5 lens / 6 light */
.split{display:grid;grid-template-columns:20mm 1fr;gap:1.8mm;align-items:start}
.fan,.plot{display:block;width:100%}
.lensfeel{margin:0;padding:0;list-style:none;display:grid;gap:.6mm}
.tag{display:inline-block;font:700 6.5pt/1 var(--f-head);letter-spacing:.06em;color:var(--blue);margin-right:.6mm}
/* 1 map */
.map{display:block;width:100%;max-width:119mm;margin:0 auto;height:auto}
.t-lab{font:600 2.15px var(--f-head);letter-spacing:.06em;fill:var(--ink)}
.t-labr{font:600 2.15px var(--f-head);letter-spacing:.06em;fill:var(--red)}
.t-sub{font:italic 400 1.95px var(--f-body);fill:var(--ink2)}
.t-num{font:500 2.05px var(--f-body);fill:var(--ink2)}
.t-badge{font:700 2.3px var(--f-head);fill:var(--ink);text-anchor:middle}
.t-badge2{font:700 2.2px var(--f-head);fill:var(--ink);text-anchor:middle}
.t-eye{font:600 1.9px var(--f-head);letter-spacing:.08em;fill:var(--blue)}
.t-floor{font-family:var(--f-head);font-weight:700;letter-spacing:.12em;fill:var(--blue);opacity:.75}
.t-floorr{font-family:var(--f-head);font-weight:700;letter-spacing:.12em;fill:var(--red);opacity:.8}
.t-inv{font:600 1.75px var(--f-head);letter-spacing:.04em;fill:var(--paper)}
.fan .t-lab,.plot .t-lab,.jl .t-lab{font-size:2.05px}
.fan .t-num{font-size:2px}
.t-tag{font:700 2.1px var(--f-head);letter-spacing:.08em;fill:var(--blue)}
.t-sub2{font:400 2.1px var(--f-body);fill:var(--ink)}
.beats{display:block;width:100%;height:auto}
/* 8 sound */
.say{display:grid;grid-template-columns:1fr;gap:.55mm;margin:0;padding:0;list-style:none}
.say li{display:flex;flex-wrap:wrap;align-items:baseline;gap:.2mm 1.2mm}
.code{background:var(--tint);border-radius:.8mm;padding:.3mm 1mm;font-weight:500;justify-self:start}
.code .br{color:var(--blue);font-weight:600}
.say i{color:var(--ink2)}
.warn{color:var(--red);font-weight:600}
/* 9 acting */
.ladder{display:grid;grid-template-columns:repeat(5,1fr);gap:1.6mm;margin:.2mm 0 .8mm}
.step{position:relative;border:.25mm solid var(--ink);border-radius:1mm;padding:.6mm .7mm;background:var(--paper);min-width:0;font-size:5.9pt;line-height:1.08}
.step b{display:block;font-family:var(--f-head);font-weight:700;font-size:6.5pt;letter-spacing:.02em}
.step:not(:last-child)::after{content:"";position:absolute;right:-1.55mm;top:50%;border:.75mm solid transparent;border-left-color:var(--ink);transform:translateY(-50%)}
.step.t{border-color:var(--blue);background:var(--blue-t)}
.verbs{color:var(--blue);font-weight:600}
.say-side{color:var(--blue);font-weight:600;margin-top:.4mm}
/* 10 cut */
.jlrow{display:grid;grid-template-columns:1fr 1fr;gap:2mm;margin:.3mm 0 .8mm}
.jl{display:block;width:100%}
.jlrow div{font-size:6.1pt;line-height:1.1}
/* 11 brief */
.brief{display:grid;grid-template-columns:auto 1fr auto 1fr;gap:.45mm 1.6mm;align-items:baseline}
.brief dt{font:700 6.6pt/1.15 var(--f-head);letter-spacing:.04em;white-space:nowrap;display:flex;align-items:center;gap:.8mm}
.brief dd{margin:0;font-size:6.6pt}
.bn{display:inline-block;width:3.3mm;height:3.3mm;border-radius:50%;background:var(--ink);color:var(--paper);font:700 5.8pt/3.3mm var(--f-head);text-align:center}
.short{margin-top:.9mm;padding:.8mm 1.2mm;background:var(--paper);border-radius:1mm;border:.2mm dashed var(--blue);font-weight:500}
.after{display:grid;grid-template-columns:1fr 1fr;gap:1.6mm;margin-top:.8mm}
@media print, (min-width:1100px){
  .desk{display:grid;place-items:center;padding-block:40px}
  .sheet{width:269mm;height:200mm;max-width:none;box-sizing:border-box;padding:0;
    box-shadow:0 0 0 5mm var(--paper),0 6px 30px 5mm rgba(20,30,40,.16)}
  .cols{flex:1;min-height:0;display:grid;grid-template-columns:65mm 133mm 65mm;gap:3mm}
}
@media screen and (max-width:1099px){
  .sheet{font-size:9.5pt}
}
@media print{
  @page{margin:0}
  html,body{background:#fff}
  .desk{padding:0;min-height:100vh}
  .sheet{box-shadow:none}
}
"""


def box(n, eyebrow, title, body, cls=""):
    return (f'<section class="box {cls}"><div class="bh"><span class="num">{n}</span><h2>{title}</h2>'
            f'<span class="eye">{eyebrow}</span></div>{body}</section>')


def page():
    angles = "".join(f'<div class="ang">{angle_icon(k)}<b>{n}</b><i>{d}</i></div>' for k, n, d in ANGLES)
    frames = "".join(f'<div class="ang">{frame_icon(k)}<b>{n}</b><i>{d}</i></div>' for k, n, d in FRAMES)
    moves = "".join(f'<div class="mv">{move_icon(k)}<div><b>{n}</b><i>{d}</i></div></div>' for k, n, d in MOVES)

    b2 = box(2, "how much of the person we see", "Size",
             size_grid() + '<p class="rule">Size is how much we see. The lens (5) is a separate choice.</p>')
    b3 = box(3, "where the lens looks from", "Angle &amp; framing",
             f'<div class="angrow">{angles}</div><div class="frrow">{frames}</div>'
             '<ul class="terms"><li><b>Insert</b> a detail (the keys)</li><li><b>Cutaway</b> something nearby</li>'
             '<li><b>Reaction</b> the listener</li><li><b>Establishing</b> where we are</li>'
             '<li><b>Master</b> whole scene, wide</li><li><b>Coverage</b> every angle</li></ul>')
    b4 = box(4, "how the camera travels", "Move",
             f'<div class="mvgrid">{moves}</div>'
             '<p class="rule">Every move: a <b>pace</b>, what stays <b>steady</b>, where it <b>stops</b>.</p>')
    b1 = box(1, "the set from above, planned like a level map", "Who &amp; where",
             set_map() + '<p class="rule">Every shot: each person\'s <b>screen side</b> and <b>where they look</b>. '
             'The model remembers nothing between shots.</p>')
    b7 = box(7, "time inside one take, beat by beat", "Beats",
             beats() + '<p class="rule">Whole seconds, no gaps · one change per beat · start where the last beat ended · '
             'end on a final frame.</p>')
    b5 = box(5, "how the space feels", "Lens",
             lens_fan() +
             '<ul class="terms"><li><b>Depth of field</b> what is sharp</li>'
             '<li><b>Rack focus</b> focus jumps</li></ul>')
    b6 = box(6, "where the light comes from", "Light",
             f'<div class="split"><div>{light_plot()}</div><ul class="terms one">'
             '<li><b>Key</b> the main light</li><li><b>Fill</b> softens the shadows</li>'
             '<li><b>Back / rim</b> lifts them off the background</li>'
             '<li><b>Practical</b> a lamp you can see</li><li><b>Motivated</b> light with a source</li>'
             '<li><b>Hard / soft</b> crisp or gentle shadows</li>'
             '<li><b>High-key / low-key</b> bright or dark</li>'
             '<li><b>Golden / blue hour</b> low sun / after sunset</li>'
             '<li class="say-side">Say the side: key from screen-left.</li></ul></div>')
    b8 = box(8, "what we hear", "Lines &amp; sound",
             '<ul class="say">'
             '<li><span class="code">Language: English, light Neapolitan accent.</span><i>once, first</i></li>'
             '<li><span class="code">2-4s, Marta\'s line (testing him): <span class="br">{</span>I thought you weren\'t coming.<span class="br">}</span></span>'
             '<i>time · who · a verb, not a feeling · words</i></li>'
             '<li><span class="code">Luca keeps his mouth closed.</span><i>whoever is silent</i>'
             '<span class="code"><span class="br">【</span>TITLE<span class="br">】</span></span><i>text meant to be seen</i></li>'
             '</ul>'
             '<ul class="terms"><li><b>Diegetic</b> heard in the world</li><li><b>Room tone</b> the room\'s own sound</li>'
             '<li><b>Foley</b> sounds made in post</li><li><b>Guide track</b> rough sound</li></ul>'
             '<p class="rule"><span class="warn">No music in shots</span> (score comes later). Avoid: water, waves, echo · '
             '"fanatical", "extremely shocked".</p>')
    b9 = box(9, "what they fight for, in this order", "Acting task",
             '<div class="ladder">'
             '<div class="step"><b>Direction</b>shared, unspoken</div>'
             '<div class="step"><b>Motive</b>each one\'s fuel</div>'
             '<div class="step"><b>Goal</b>their own fight</div>'
             '<div class="step"><b>Obstacle</b>one crack, it ends</div>'
             '<div class="step t"><b>Tactic</b>done to the partner</div></div>'
             '<p class="note">Play the direction, never the emotion. The tactic lives in the eyes. Verbs at the partner: '
             '<span class="verbs">test · reassure · corner · dodge · tease · warn · comfort · provoke · plead · '
             'charm · probe · stall</span>. Not "sadly", "nervously".</p>'
             '<p class="rule">Listeners get a task too. Dead eyes: a task, not catchlights.</p>')
    b10 = box(10, "how this shot joins the next", "Cut",
              f'<div class="jlrow"><div>{jl("J")}<b>J-cut</b> next sound comes first</div>'
              f'<div>{jl("L")}<b>L-cut</b> sound carries over</div></div>'
              '<ul class="terms"><li><b>Cut on action</b> mid-move</li><li><b>Match cut</b> shapes rhyme</li>'
              '<li><b>Jump cut</b> time skips</li><li><b>Cross-cut</b> two places, in turn</li>'
              '<li><b>Smash cut</b> abrupt contrast</li><li><b>Dissolve / fade</b> melt / black</li></ul>'
              '<p class="rule">Every take is a new performance: cut to the <b>listener</b>.</p>')
    b11 = box(11, "what to write to Claude, in number order", "The brief",
              '<dl class="brief">'
              '<dt>SHOT</dt><dd>S03 SH020 · 6 s</dd>'
              '<dt><span class="bn">6</span>LIGHT</dt><dd>key from the window, screen-left</dd>'
              '<dt><span class="bn">1</span>WHO &amp; WHERE</dt><dd>Marta at the window, night; Luca at the door</dd>'
              '<dt><span class="bn">7</span>BEATS</dt><dd>0-2 watches the street · 2-4 hears him · 4-6 turns</dd>'
              '<dt><span class="bn">2</span>SIZE</dt><dd>MCU on Marta</dd>'
              '<dt><span class="bn">8</span>LINES</dt><dd>4-6 Marta (testing him): I thought you weren\'t coming.</dd>'
              '<dt><span class="bn">3</span>ANGLE</dt><dd>eye level, over Luca\'s shoulder</dd>'
              '<dt><span class="bn">9</span>TASK</dt><dd>she wants him to admit he almost stayed away</dd>'
              '<dt><span class="bn">4</span>MOVE</dt><dd>slow push in, stops as she turns</dd>'
              '<dt><span class="bn">10</span>CUT</dt><dd>on her turn, to Luca\'s single</dd>'
              '<dt><span class="bn">5</span>LENS</dt><dd>long, shallow focus</dd>'
              '<dt>END FRAME</dt><dd>she faces him, hands on the sill</dd></dl>'
              '<div class="short"><b>Shorthand works:</b> S03 SH020 6s · MCU Marta · eye, OTS Luca · push in, stop on turn · '
              'long, shallow · key L window · (testing) "I thought you weren\'t coming" · cut on turn</div>'
              '<div class="after"><div><b>Skip a field</b> and I choose, marked [ASSUMPTION].</div>'
              '<div><b>After a take:</b> what I saw, then what I want. One change per take.</div></div>',
              "key")
    head = ('<header class="head"><div><h1>Shot Language</h1>'
            '<div class="sub">Field guide for briefing AI shots · Seedance 2.5 on Higgsfield · November 2026</div></div>'
            '<div class="facts"><span>4-30 s per take, whole seconds</span><span>24 fps timeline</span>'
            '<span>credits per second: 480p 3 · 720p 7 · 1080p 16</span><span>one model per film</span>'
            '<span>one change per take</span><span>boxes 1-10 = brief order · template in 11</span></div></header>')
    body = (f'<div class="cols"><div class="col">{b2}{b3}{b4}</div>'
            f'<div class="col">{b1}{b7}{b11}</div>'
            f'<div class="col">{b5}{b6}{b8}{b9}{b10}</div></div>')
    return (f'<title>Shot Language Field Guide</title>\n'
            f'<meta name="claude:viewport-fit-sides" content="cover">\n'
            f'<style>\n{font_faces()}\n{CSS}</style>\n{DEFS}\n'
            f'<main class="desk"><article class="sheet">{head}{body}</article></main>\n')


OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(page(), encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")
