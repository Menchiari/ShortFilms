"""001 S09 SH070 v4 end frame: her point of view, looking down into the open dark blue folder of S09 SH060
T01 (ref_sh060_T01_3s.png). The last page lies on the folder's right panel; the frame lands tight on the
signature: the folder's left panel and spine at frame left, the page's bottom edge and a strip of the
folder below it, the sunlit dusty ground far below and out of focus beyond. The sun is behind her (SH060):
the folder lies in her shade, the ground beyond glows. Her hands are out of frame at this point.
Output: insert_end_v4.png, 3840x1646."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

H = Path(__file__).parent
rng = np.random.default_rng(23)
FW, FH = 3840, 1646
page = Image.open(H / "agreement_page_v2.png").convert("RGB")
pw, ph = page.size

def gb(a, r):
    return np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), dtype=np.float32)

# ---------- the folder plane, in page pixels, origin shifted so the folder's left panel fits ----------
X0, Y0 = -700, 2250                       # plane-image origin in page coords
PWd, PHd = 2700, 1250                     # plane image size
pl = np.zeros((PHd, PWd, 4), np.float32)
navy = np.array([26, 56, 112], np.float32)
def rect(x0, y0, x1, y1, col, a=255):
    pl[max(0, y0 - Y0):max(0, y1 - Y0), max(0, x0 - X0):max(0, x1 - X0)] = [*col, a]
rect(-700, 2250, -40, 3390, navy * 0.80)          # left panel, tilted up, a little darker
rect(-40, 2250, 2620, 3390, navy)                 # right panel under the page
card = gb(rng.normal(128, 30, (PHd, PWd)).astype(np.float32)[..., None].repeat(3, -1), 1.5)[..., 0] - 128
pl[..., :3] += (card * 0.10)[..., None] * (pl[..., 3:] > 0)
# the spine crease
sx = -40 - X0
pl[:, sx - 10:sx + 10, :3] *= (0.78 + 0.22 * np.abs(np.linspace(-1, 1, 20)))[None, :, None]
# page shadow on the folder, then the page (sitting 30 px right of the spine)
psx, psy = 30, 0
shadow = np.zeros((PHd, PWd), np.float32)
shadow[max(0, psy - Y0 + 10):3300 - Y0 + 18, psx - X0 + 8:min(PWd, psx + pw - X0 + 8)] = 1
shadow = gb(shadow[..., None].repeat(3, -1) * 255, 10)[..., 0] / 255
pl[..., :3] *= (1 - 0.45 * shadow)[..., None]
crop = np.asarray(page.crop((0, Y0, min(pw, PWd + X0 - psx), 3300)), dtype=np.float32)
pl[0:crop.shape[0], psx - X0:psx - X0 + crop.shape[1], :3] = crop
pl[0:crop.shape[0], psx - X0:psx - X0 + crop.shape[1], 3] = 255
# soft edges
pl[..., 3] = gb(pl[..., 3:4].repeat(3, -1), 1.0)[..., 0]
plane = Image.fromarray(np.clip(pl, 0, 255).astype(np.uint8), "RGBA")

# ---------- camera: looking down from her eyes, the far (top) side narrower ----------
vx0, vx1 = -330 - X0, 1720 - X0           # visible plane x at the bottom of frame
vy0, vy1 = 2420 - Y0, 3520 - Y0           # visible plane y, top to bottom (beyond 3390: no folder)
dx = 150
quad = [(vx0 - dx, vy0), (vx0, vy1), (vx1, vy1), (vx1 + dx, vy0)]
# a slight roll: her hands are not a tripod
cx_, cy_ = (vx0 + vx1) / 2, (vy0 + vy1) / 2
th = np.radians(2.2)
quad = tuple(v for x, y in quad for v in (cx_ + (x - cx_) * np.cos(th) - (y - cy_) * np.sin(th),
                                          cy_ + (x - cx_) * np.sin(th) + (y - cy_) * np.cos(th)))
warped = plane.transform((FW, FH), Image.QUAD, quad, Image.BICUBIC)
w = np.asarray(warped, dtype=np.float32)
a = w[..., 3:] / 255
fg = w[..., :3]

# ---------- the ground far below: sunlit dust, defocused ----------
gim = Image.open(H.parent.parent / "look" / "palette_ref_2_sunset.jpg").convert("RGB").crop((500, 560, 1400, 720)).resize((FW, FH), Image.BICUBIC)
bg = gb(np.asarray(gim, dtype=np.float32) * 1.9 + 70, 45)
for _ in range(90):
    x, y, r = rng.integers(0, FW), rng.integers(0, FH), rng.integers(12, 40)
    d = Image.new("L", (FW, FH), 0); ImageDraw.Draw(d).ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=int(rng.uniform(20, 60)))
    bg += np.asarray(d.filter(ImageFilter.GaussianBlur(3)), dtype=np.float32)[..., None] * np.array([1.0, 0.8, 0.55])

# ---------- light: the folder in her own shade, cooler and soft; warm bounce from the square ----------
yy, xx = np.mgrid[0:FH, 0:FW].astype(np.float32)
shade = np.stack([0.84 - 0.04 * yy / FH, 0.80 - 0.04 * yy / FH, 0.76 - 0.03 * yy / FH], -1)
fg = fg * shade + np.array([18, 10, 2])
# depth of field: the far edge of the folder softens a little
fgb = gb(fg, 2.5)
m = np.clip((0.18 - yy / FH) / 0.18, 0, 1)[..., None]
fg = fg * (1 - m) + fgb * m
img = bg * (1 - a) + fg * a

# ---------- lens and film ----------
img = img * np.array([1.0, 0.92, 0.80])
out = img.copy()
for ch, sc in ((0, 1.0012), (2, 0.9988)):
    sxm = np.clip(((xx - FW / 2) / sc + FW / 2).astype(int), 0, FW - 1)
    sym = np.clip(((yy - FH / 2) / sc + FH / 2).astype(int), 0, FH - 1)
    out[..., ch] = img[sym, sxm, ch]
img = out
img += gb(np.clip(img - 205, 0, 255), 20) * np.array([0.6, 0.28, 0.08])
r2 = ((xx / FW - 0.5) / 0.7) ** 2 + ((yy / FH - 0.5) / 0.95) ** 2
img *= (1 - 0.28 * r2)[..., None]
g = gb((rng.normal(0, 1, (FH, FW)) * 40 + 128)[..., None].repeat(3, -1), 0.8)[..., 0] - 128
img += g[..., None] * (0.16 + 0.10 * (1 - img.mean(-1, keepdims=True) / 255)) * 0.9
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(H / "insert_end_v4.png")
print("ok")
