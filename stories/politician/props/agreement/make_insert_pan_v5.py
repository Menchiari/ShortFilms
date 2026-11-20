"""001 S09 SH070 T05: her point of view into the dark blue folder (SH060), no zoom: the framing and scale of
insert_end_v4.png for the whole shot. A slow handheld tilt from the top of the page down to the signature,
the page's upper half fluttering in the rotor wash (pinned at the bottom by her thumb, out of frame), the
sunlit ground far below entering at the end. Real text throughout. 0 credits.
Usage: python3 make_insert_pan_v5.py <out_dir> [frame ...]  (no frames given: renders all)"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

H = Path(__file__).parent
FW, FH, FPS = 3840, 1646, 24
DUR = 6.0                                   # 0.4 s on the top, pan, 1.2 s settled on the signature
N = int(DUR * FPS)
rng = np.random.default_rng(23)
page = Image.open(H / "agreement_page_v2.png").convert("RGB")
pw, ph = page.size

def gb(a, r):
    return np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), dtype=np.float32)

# ---------- the folder plane (page px), full page height ----------
X0, Y0 = -700, -500
PWd, PHd = 2700, 4020
pl = np.zeros((PHd, PWd, 4), np.float32)
navy = np.array([26, 56, 112], np.float32)
def rect(x0, y0, x1, y1, col):
    pl[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0] = [*col, 255]
rect(-700, -500, -40, 3390, navy * 0.80)
rect(-40, -500, 2000, 3390, navy)
card = gb(rng.normal(128, 30, (PHd, PWd)).astype(np.float32)[..., None].repeat(3, -1), 1.5)[..., 0] - 128
pl[..., :3] += (card * 0.10)[..., None] * (pl[..., 3:] > 0)
sx = -40 - X0
pl[:, sx - 10:sx + 10, :3] *= (0.78 + 0.22 * np.abs(np.linspace(-1, 1, 20)))[None, :, None]
psx = 30
shadow = np.zeros((PHd, PWd), np.float32)
shadow[0 - Y0 + 10:3300 - Y0 + 18, psx - X0 + 8:min(PWd, psx + pw - X0 + 8)] = 1
shadow = gb(shadow[..., None].repeat(3, -1) * 255, 10)[..., 0] / 255
pl[..., :3] *= (1 - 0.45 * shadow)[..., None]
cw = min(pw, PWd + X0 - psx)
pl[-Y0:-Y0 + ph, psx - X0:psx - X0 + cw, :3] = np.asarray(page.crop((0, 0, cw, ph)), dtype=np.float32)
pl[-Y0:-Y0 + ph, psx - X0:psx - X0 + cw, 3] = 255
pmask = np.zeros((PHd, PWd), np.float32); pmask[-Y0:-Y0 + ph, psx - X0:psx - X0 + cw] = 255
pl[..., 3] = gb(pl[..., 3:4].repeat(3, -1), 1.0)[..., 0]
plane = Image.fromarray(np.clip(pl, 0, 255).astype(np.uint8), "RGBA")
pmask_im = Image.fromarray(pmask.astype(np.uint8), "L")

# ---------- the ground far below, taller than the frame so it can drift with the pan ----------
gim = Image.open(H.parent.parent / "look" / "palette_ref_2_sunset.jpg").convert("RGB").crop((500, 520, 1400, 720)).resize((FW, int(FH * 1.6)), Image.BICUBIC)
bg_full = gb(np.asarray(gim, dtype=np.float32) * 1.9 + 70, 45)
for _ in range(120):
    x, y, r = rng.integers(0, FW), rng.integers(0, bg_full.shape[0]), rng.integers(12, 40)
    d = Image.new("L", (FW, bg_full.shape[0]), 0); ImageDraw.Draw(d).ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=int(rng.uniform(20, 60)))
    bg_full += np.asarray(d.filter(ImageFilter.GaussianBlur(3)), dtype=np.float32)[..., None] * np.array([1.0, 0.8, 0.55])

yy, xx = np.mgrid[0:FH, 0:FW].astype(np.float32)
shade = np.stack([0.84 - 0.04 * yy / FH, 0.80 - 0.04 * yy / FH, 0.76 - 0.03 * yy / FH], -1)
r2 = ((xx / FW - 0.5) / 0.7) ** 2 + ((yy / FH - 0.5) / 0.95) ** 2
vig = (1 - 0.28 * r2)[..., None]
sxm = {c: np.clip(((xx - FW / 2) / s + FW / 2).astype(int), 0, FW - 1) for c, s in ((0, 1.0012), (2, 0.9988))}
sym = {c: np.clip(((yy - FH / 2) / s + FH / 2).astype(int), 0, FH - 1) for c, s in ((0, 1.0012), (2, 0.9988))}
grains = [gb((rng.normal(0, 1, (FH, FW)) * 40 + 128)[..., None].repeat(3, -1), 0.8)[..., 0] - 128 for _ in range(6)]

# smooth handheld noise: a few slow sines per axis
def hand(t, seed, amp):
    r = np.random.default_rng(seed); s = 0.0
    for f in (0.35, 0.8, 1.7, 3.1):
        s += np.sin(2 * np.pi * f * t + r.uniform(0, 6.28)) * amp / f ** 0.7
    return s

def ease(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)

VH = 1100                                   # visible plane height (page px), the end frame's scale
Y_TOP, Y_END = -230, 2420                   # top of the visible window: page top edge in view, then the end frame
def frame(i):
    t = i / FPS
    u = ease((t - 0.4) / (DUR - 0.4 - 1.2))
    vy0 = Y_TOP + (Y_END - Y_TOP) * u - Y0
    vy1 = vy0 + VH
    vx0, vx1 = -330 - X0, 1720 - X0
    dx = 150
    hx, hy, hr = hand(t, 1, 6), hand(t, 2, 5), hand(t, 3, 0.12)
    q = [(vx0 - dx + hx, vy0 + hy), (vx0 + hx, vy1 + hy), (vx1 + hx, vy1 + hy), (vx1 + dx + hx, vy0 + hy)]
    cx_, cy_ = (vx0 + vx1) / 2, (vy0 + vy1) / 2
    th = np.radians(2.2 + hr)
    quad = tuple(v for x, y in q for v in (cx_ + (x - cx_) * np.cos(th) - (y - cy_) * np.sin(th),
                                          cy_ + (x - cx_) * np.sin(th) + (y - cy_) * np.cos(th)))
    w = np.asarray(plane.transform((FW, FH), Image.QUAD, quad, Image.BICUBIC), dtype=np.float32)
    pm = np.asarray(pmask_im.transform((FW, FH), Image.QUAD, quad, Image.BILINEAR), dtype=np.float32) / 255
    # rotor wash: a travelling ripple on the page, strong at the top of the page, pinned at the bottom
    py = vy0 + Y0 + (yy / FH) * VH                       # page y under each output row (approx.)
    A = 7.0 * np.clip(1 - py / 2300, 0, 1) ** 1.4 * (0.65 + 0.35 * np.sin(2 * np.pi * 0.9 * t))
    ph_ = 2 * np.pi * (xx / 1100 - 1.6 * t) + 0.8 * np.sin(2 * np.pi * (yy / 1500 + 0.5 * t))
    dy = A * np.sin(ph_) * pm
    ys = np.clip(yy + dy, 0, FH - 1.001); y0i = ys.astype(int); fy = (ys - y0i)[..., None]
    xi = xx.astype(int)
    w = w[y0i, xi] * (1 - fy) + w[y0i + 1, xi] * fy
    lit = 1 + 0.010 * A * np.cos(ph_) * pm                 # the ripple catches the light
    a = w[..., 3:] / 255
    fg = w[..., :3] * shade * lit[..., None] + np.array([18, 10, 2])
    off = int((bg_full.shape[0] - FH) * (1 - u) * 0.6)    # the ground drifts less than the folder (far away)
    bg = bg_full[off:off + FH]
    img = (bg * (1 - a) + fg * a) * np.array([1.0, 0.92, 0.80])
    out = img.copy()
    for c in (0, 2):
        out[..., c] = img[sym[c], sxm[c], c]
    img = out
    hi = np.clip(img[::4, ::4] - 205, 0, 255)
    img += np.asarray(Image.fromarray(gb(hi, 5).astype(np.uint8)).resize((FW, FH), Image.BILINEAR), dtype=np.float32) * np.array([0.6, 0.28, 0.08])
    img *= vig
    img += grains[i % 6][..., None] * (0.16 + 0.10 * (1 - img.mean(-1, keepdims=True) / 255)) * 0.9
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
idx = [int(a) for a in sys.argv[2:]] or range(N)
for i in idx:
    frame(i).save(out / f"f{i:04d}.png")
print("frames", len(list(idx)), "of", N)
