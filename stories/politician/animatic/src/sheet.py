"""Contact sheet: python sheet.py out.png dir shot1 shot2 ... (first and last frame each)"""
import sys, os, glob
from PIL import Image, ImageDraw
out, root, shots = sys.argv[1], sys.argv[2], sys.argv[3:]
tiles = []
for s in shots:
    fs = sorted(glob.glob(f"{root}/{s}/[pf]_*.png"))
    if not fs: continue
    pick = [fs[0], fs[len(fs) // 2], fs[-1]] if len(fs) > 2 else fs
    for f in pick:
        im = Image.open(f).convert("RGB").resize((448, 192))
        ImageDraw.Draw(im).text((6, 4), s + " " + os.path.basename(f), fill=(255, 255, 0))
        tiles.append(im)
cols = 3
W = Image.new("RGB", (448 * cols, 192 * ((len(tiles) + cols - 1) // cols)))
for i, t in enumerate(tiles):
    W.paste(t, ((i % cols) * 448, (i // cols) * 192))
W.save(out); print(W.size)
