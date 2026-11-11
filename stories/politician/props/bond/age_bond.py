#!/usr/bin/env python3
"""Age a rendered bond: paper toning, foxing, folds, a water stain, edge wear, a bank stamp.
Usage: age_bond.py clean.png out.png level(1-3) seed [bond_width_px]"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

src, out, level, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
WB = int(sys.argv[5]) if len(sys.argv) > 5 else 3450
rng = np.random.default_rng(seed)
im = Image.open(src).convert("RGB")
w, h = im.size
a = np.asarray(im).astype(np.float32) / 255.0
L = level / 3.0

def lfn(scale, octaves=3):
    acc = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        s = max(4, int(scale / (2 ** o)))
        small = rng.random((h // s + 3, w // s + 3)).astype(np.float32)
        up = np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w + 3 * s, h + 3 * s), Image.BICUBIC)).astype(np.float32)[:h, :w] / 255.0
        acc += amp * up; tot += amp; amp *= 0.5
    return acc / tot

yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
dist_edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))

# 1. paper toning, stronger toward the edges
edge = np.clip(1 - dist_edge / 420.0, 0, 1) ** 2
tone = L * (0.09 + 0.28 * edge + 0.12 * lfn(260))
a *= 1 - tone[..., None] * np.array([0.22, 0.50, 1.0], np.float32)

# 2. foxing spots
fox = Image.new("L", (w, h), 0); d = ImageDraw.Draw(fox)
for _ in range(int(60 + 260 * L)):
    cx, cy = rng.integers(0, w), rng.integers(0, h)
    if rng.random() < 0.6:  # clusters near edges
        side = rng.integers(0, 4)
        if side == 0: cx = rng.integers(0, 380)
        elif side == 1: cx = w - rng.integers(0, 380)
        elif side == 2: cy = rng.integers(0, 380)
        else: cy = h - rng.integers(0, 380)
    r = float(rng.choice([2, 3, 4, 6, 9, 14], p=[.3, .25, .2, .13, .08, .04]))
    d.ellipse([cx - r, cy - r * rng.uniform(.7, 1.3), cx + r, cy + r * rng.uniform(.7, 1.3)], fill=int(rng.uniform(60, 200)))
fox = np.asarray(fox.filter(ImageFilter.GaussianBlur(2.2))).astype(np.float32) / 255.0 * (0.25 + 0.45 * L)
brown = np.array([0.58, 0.40, 0.22], np.float32)
a = a * (1 - fox[..., None]) + a * brown * fox[..., None]

# 3. water stain (levels 2 and 3)
if level >= 2:
    for _ in range(level - 1):
        cx, cy = rng.uniform(0.15, 0.85) * WB, rng.uniform(0.25, 0.85) * h
        R = rng.uniform(220, 420)
        blob = (lfn(140, 2) * 0.5 + 0.5 * np.clip(1 - np.hypot(xx - cx, yy - cy) / R, 0, 1)) > 0.57
        m = np.asarray(Image.fromarray((blob * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32) / 255.0
        rim = np.clip(m - np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255.0, 0, 1)
        a *= 1 - (0.07 * m + 0.30 * rim)[..., None] * np.array([0.3, 0.55, 1.0], np.float32)

# 4. folds: the coupon fold always; a center fold from level 2; a horizontal fold at level 3
folds = [("v", WB + 8)]
if level >= 2: folds.append(("v", WB / 2))
if level >= 3: folds.append(("h", h / 2))
for kind, pos in folds:
    t = (xx - pos) if kind == "v" else (yy - pos)
    jitter = (lfn(400, 2) - 0.5) * 6
    t = t + jitter
    crease = np.exp(-(t ** 2) / (2 * 1.3 ** 2)) * (0.22 + 0.25 * L)
    shade = np.clip(-t / 40.0, 0, 1) * np.exp(-np.abs(t) / 40.0) * 0.07 * (0.6 + L)
    light = np.clip(t / 30.0, 0, 1) * np.exp(-np.abs(t) / 30.0) * 0.05
    a = a * (1 - crease - shade)[..., None] + light[..., None] * (1 - a)
    specks = (rng.random((h, w)) < 0.012 * L) & (np.abs(t) < 2.5)
    a[specks] = a[specks] * 0.4 + 0.6 * np.array([0.93, 0.90, 0.82], np.float32)

# 5. bank stamp (levels 2 and 3)
if level >= 2:
    st = Image.new("L", (900, 360), 0); sd = ImageDraw.Draw(st)
    fb = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 46)
    fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 34)
    sd.rounded_rectangle([10, 10, 890, 350], 22, outline=255, width=8)
    sd.rounded_rectangle([26, 26, 874, 334], 16, outline=255, width=3)
    for txt, y, f in [("RECEIVED FOR SAFEKEEPING", 50, fs), ("MAR 4 1964", 130, fb), ("FARMERS & MERCHANTS BANK", 250, fs)]:
        tw = sd.textlength(txt, font=f); sd.text(((900 - tw) / 2, y), txt, font=f, fill=255)
    st = st.rotate(rng.uniform(-14, -6), expand=True, resample=Image.BICUBIC)
    sw, sh = st.size
    grunge = (np.asarray(Image.fromarray((rng.random((sh // 6 + 2, sw // 6 + 2)) * 255).astype(np.uint8)).resize((sw, sh), Image.BICUBIC)).astype(np.float32) / 255.0)
    sm = np.asarray(st).astype(np.float32) / 255.0 * np.clip((grunge - 0.18) * 1.8, 0, 1) * (0.55 + 0.15 * L)
    px, py = int(rng.uniform(380, 900)), int(rng.uniform(1400, 1650))
    region = a[py:py + sh, px:px + sw]
    purple = np.array([0.42, 0.28, 0.58], np.float32)
    m = sm[:region.shape[0], :region.shape[1], None]
    a[py:py + sh, px:px + sw] = region * (1 - m) + region * purple * m

# 6. ink softening and grain
a = np.clip(a, 0, 1)
img = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.45))
a = np.asarray(img).astype(np.float32) / 255.0
a += rng.normal(0, 0.010 + 0.006 * L, (h, w, 1)).astype(np.float32)
a *= 1 - (np.clip(1 - dist_edge / 25.0, 0, 1) * 0.25 * L)[..., None]

# 7. worn edges: alpha with jagged boundary, a nicked corner at level 3
jag = (lfn(30, 2) - 0.5) * (4 + 10 * L) + 2
alpha = (dist_edge > jag).astype(np.float32)
if level >= 3:
    cx, cy = (w - 1, 0) if rng.random() < 0.5 else (0, h - 1)
    cut = np.hypot(xx - cx, yy - cy) < 70 + (lfn(20, 2) - 0.5) * 40
    alpha[cut] = 0
alpha = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)))
rgba = np.dstack([(np.clip(a, 0, 1) * 255).astype(np.uint8), alpha])
Image.fromarray(rgba, "RGBA").save(out, optimize=True)
print("saved", out)
