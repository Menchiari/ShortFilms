"""QC sheets from the finished composite: 3 frames per shot (15%, 50%, 85%). python3 qc.py film.mp4 outprefix"""
import sys, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from parse import parse
from PIL import Image, ImageDraw
mp4, pre = sys.argv[1], sys.argv[2]
meta, scenes = parse(os.path.join(HERE, "..", "..", "screenplay.fountain"))
shots = []; tc = 0.0
for s in scenes:
    for sh in s["shots"]:
        shots.append((f"{s['id']}_{sh['id']}", tc, sh["sec"])); tc += sh["sec"]
tmp = pre + "_tmp"; os.makedirs(tmp, exist_ok=True)
tiles = []
for sid, t0, sec in shots:
    row = []
    for k, u in enumerate((0.15, 0.5, 0.85)):
        fn = f"{tmp}/{sid}_{k}.png"
        if not os.path.exists(fn):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0 + sec * u:.3f}", "-i", mp4, "-frames:v", "1", "-vf", "scale=448:-2", fn], check=True)
        row.append(Image.open(fn).convert("RGB"))
    tiles.append((sid, row))
per = 12
for p in range(0, len(tiles), per):
    chunk = tiles[p:p + per]; h = chunk[0][1][0].height
    W = Image.new("RGB", (448 * 3, h * len(chunk)))
    for i, (sid, row) in enumerate(chunk):
        for k, im in enumerate(row):
            W.paste(im, (448 * k, h * i))
    W.save(f"{pre}_{p // per}.png")
print(len(tiles), "shots,", (len(tiles) + per - 1) // per, "sheets, total", round(tc, 1), "s")
