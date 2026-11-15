"""Composite the animatic: rendered frames or cards + shot label + subtitles above speakers + sound cues.
Usage: python3 comp.py <out_dir> <dest.mp4> [shot ids to limit]"""
import sys, os, json, glob, re, subprocess, textwrap
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from PIL import Image, ImageDraw, ImageFont
from parse import parse, fmt

FPS, W, H = 12, 1120, 480
SCRIPT = "/home/user/ShortFilms/stories/politician/screenplay.fountain"
FD = "/usr/share/fonts/truetype/dejavu/"
F_LAB = ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 17)
F_LAB2 = ImageFont.truetype(FD + "DejaVuSans.ttf", 12)
F_SUB = ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 19)
F_SUBI = ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 17)
F_CUE = ImageFont.truetype(FD + "DejaVuSansMono-Bold.ttf", 13)
F_CARD = ImageFont.truetype(FD + "DejaVuSansMono.ttf", 21)
F_CARDH = ImageFont.truetype(FD + "DejaVuSans-Bold.ttf", 15)
OFF = ("V.O.", "VOICES", "O.S.", "NEWS")
ANCHOR = "NEWS ANCHORS (V.O.)"
FRAG = ["...protests in more than forty countries...", "...the index lost another eleven percent...", "...fuel up again overnight..."]
OVERRIDE = {"S01_SH010": [(0, 2, ANCHOR, FRAG[0])], "S01_SH020": [(0, 2, ANCHOR, FRAG[0])],
            "S01_SH030": [(0.5, 3, ANCHOR, FRAG[1])], "S01_SH040": [(0, 1, ANCHOR, FRAG[1])], "S01_SH050": [(0, 2, ANCHOR, FRAG[1])],
            "S01_SH060": [(0.3, 2, ANCHOR, FRAG[2])], "S01_SH070": [(0, 2, ANCHOR, FRAG[2])], "S01_SH080": [], "S01_SH090": [],
            "S01_SH100": [], "S01_SH110": []}
IMAGES = {"S05_SH050": "/home/user/ShortFilms/stories/politician/prop-bearer-bond_v2.png"}

def chunks(text, maxc=100):
    parts = re.split(r"(?<=[.!?])\s+(?=\S)", text.strip())
    out, cur = [], ""
    for p in parts:
        if len(cur) + len(p) + 1 <= maxc:
            cur = (cur + " " + p).strip()
        else:
            if cur: out.append(cur)
            while len(p) > maxc:
                cut = p.rfind(" ", 0, maxc); out.append(p[:cut]); p = p[cut + 1:]
            cur = p
    if cur: out.append(cur)
    return out

def dialogue(shot):
    out = []
    for b in shot["blocks"]:
        if b[0] == "dialogue":
            txt = " ".join(v for k, v in b[2] if k == "line")
            out.append((b[1], txt))
    return out

def timeline(shot, info, sid=None):
    """List of (t0, t1, char, text) subtitle events."""
    if sid in OVERRIDE:
        return OVERRIDE[sid]
    lines = dialogue(shot); sec = shot["sec"]; ev = []
    say = info.get("say")
    if not say or len(say) != len(lines):
        total = sum(len(t) for _, t in lines) or 1; t = 0.25; span = sec - 0.45
        say = []
        for ch, tx in lines:
            d = span * len(tx) / total; say.append([t, t + d, ch]); t += d
    for (t0, t1, _), (ch, tx) in zip(say, lines):
        cs = chunks(tx); tot = sum(len(c) for c in cs) or 1; t = t0
        for c in cs:
            d = (t1 - t0) * len(c) / tot; ev.append((t, t + d, ch, c)); t += d
    return ev

def outline(dr, xy, text, font, fill=(255, 255, 255), stroke=3, anchor="la"):
    dr.text(xy, text, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0), anchor=anchor)

def wrap_px(dr, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        tst = (cur + " " + w).strip()
        if dr.textlength(tst, font=font) <= maxw: cur = tst
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def card(shot, scid, sid=None):
    im = Image.new("RGB", (W, H), (22, 21, 20)); dr = ImageDraw.Draw(im)
    if sid in IMAGES and os.path.exists(IMAGES[sid]):
        pic = Image.open(IMAGES[sid]).convert("RGB"); pic.thumbnail((W - 160, H - 150))
        im.paste(pic, ((W - pic.width) // 2, 120))
        dr.text((W // 2, 80), f"{shot['size']}  |  {shot['move']}".upper(), font=F_CARDH, fill=(200, 170, 120), anchor="ma")
        return im
    dr.rectangle([6, 6, W - 7, H - 7], outline=(70, 66, 60), width=2)
    head = f"{shot['size']}  |  {shot['move']}".upper()
    dr.text((W // 2, 92), head, font=F_CARDH, fill=(200, 170, 120), anchor="ma")
    act = " ".join(b[1] for b in shot["blocks"] if b[0] == "action")
    y = 140
    for ln in wrap_px(dr, act, F_CARD, W - 220)[:8]:
        dr.text((W // 2, y), ln, font=F_CARD, fill=(235, 230, 220), anchor="ma"); y += 30
    return im

def main():
    out_dir, dest = sys.argv[1], sys.argv[2]; limit = sys.argv[3:]
    meta, scenes = parse(SCRIPT)
    total = sum(sh["sec"] for s in scenes for sh in s["shots"])
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-r", "24", "-c:v", "libx264", "-crf", "21", "-preset", "medium",
                           "-pix_fmt", "yuv420p", "-movflags", "+faststart", dest], stdin=subprocess.PIPE)
    tc = 0
    for sc in scenes:
        for sh in sc["shots"]:
            sid = f"{sc['id']}_{sh['id']}"
            if limit and sid not in limit:
                tc += sh["sec"]; continue
            mp = os.path.join(out_dir, sid, "meta.json")
            info = json.load(open(mp)) if os.path.exists(mp) else {"card": True}
            frames = sorted(glob.glob(os.path.join(out_dir, sid, "f_*.png")))
            nf = int(round(sh["sec"] * FPS))
            base_card = card(sh, sc["id"], sid) if (info.get("card") or not frames) else None
            ev = timeline(sh, info, sid); cues = info.get("cues", []); anc = info.get("anchors", [])
            for f in range(nf):
                t = f / FPS
                im = base_card.copy() if base_card else Image.open(frames[min(f, len(frames) - 1)]).convert("RGB")
                dr = ImageDraw.Draw(im)
                # label
                dr.rectangle([0, 0, 252, 44], fill=(0, 0, 0))
                dr.text((10, 5), f"{sc['id']} {sh['id']}", font=F_LAB, fill=(255, 255, 255))
                dr.text((132, 5), f"{sh['sec']}s", font=F_LAB, fill=(255, 205, 90))
                dr.text((10, 26), f"{fmt(tc + t)} / {fmt(total)}", font=F_LAB2, fill=(190, 190, 190))
                # cues
                cy = H - 22
                for c0, c1, txt in cues:
                    if c0 <= t < c1:
                        outline(dr, (12, cy), f"[{txt.upper()}]", F_CUE, (255, 220, 90), 2); cy -= 18
                # subtitles
                for t0, t1, ch, txt in ev:
                    if not (t0 <= t < t1):
                        continue
                    a = anc[f].get(ch) if f < len(anc) else None
                    lines = wrap_px(dr, txt, F_SUB, 520)
                    off = any(k in ch for k in OFF) or a is None or not (0.03 < a[0] < 0.97 and 0.05 < a[1] < 1.0 and a[2] > 0)
                    if off or base_card:
                        name = ch.replace(" (V.O.)", "").replace(" (O.S.)", "")
                        lines = wrap_px(dr, f"{name}: {txt}", F_SUBI, 760)
                        y = H - 30 - 22 * len(lines)
                        for ln in lines:
                            outline(dr, (W // 2, y), ln, F_SUBI, (255, 255, 255), 3, "ma"); y += 22
                    else:
                        x = min(max(a[0] * W, 270), W - 270)
                        y = a[1] * H - 34 - 24 * len(lines)
                        y = min(max(y, 50), H - 30 - 24 * len(lines))
                        for ln in lines:
                            outline(dr, (x, y), ln, F_SUB, (255, 255, 255), 3, "ma"); y += 24
                ff.stdin.write(im.tobytes())
            tc += sh["sec"]
            print("comp", sid, flush=True)
    ff.stdin.close(); ff.wait()

main()
