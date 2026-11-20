"""001 S09 SH070, v3 plates: the start and end frames for a start-and-end-frame generation.
Leonard 2026-11-20: held by her, rotor wash moves the paper, dirt out of focus behind it, the camera
skims fast down the page and stops on the signature; real depth of field, lens artifacts, film grain.
Frames: insert_start_v3.png (top of the page), insert_end_v3.png (the signature, readable), 3840x1646.
The page is agreement_page_v2.png, bowed like paper held by its sides, in front of the sunset ground
(look/palette_ref_2_sunset.jpg, defocused). Start: page edges in frame. End: tight, sides out of frame."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

H = Path(__file__).parent
rng = np.random.default_rng(11)
FW, FH = 3840, 1646
page = np.asarray(Image.open(H / "agreement_page_v2.png").convert("RGB"), dtype=np.float32)
ph, pw = page.shape[:2]

def gblur(a, r):
    return np.asarray(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)), dtype=np.float32)

def background():
    im = Image.open(H.parent.parent / "look" / "palette_ref_2_sunset.jpg").convert("RGB")
    im = im.crop((300, 330, 1500, 720)).resize((FW, FH), Image.BICUBIC)       # the dusty ground and haze
    b = gblur(np.asarray(im, dtype=np.float32), 38)
    # out-of-focus dust and grit catching the sun: soft discs
    disc = np.zeros((FH, FW), np.float32)
    for _ in range(140):
        x, y, r = rng.integers(0, FW), rng.integers(0, FH), rng.integers(10, 46)
        yy, xx = np.ogrid[max(0, y - r):min(FH, y + r), max(0, x - r):min(FW, x + r)]
        m = ((xx - x) ** 2 + (yy - y) ** 2 <= r * r).astype(np.float32)
        disc[max(0, y - r):min(FH, y + r), max(0, x - r):min(FW, x + r)] += m * rng.uniform(0.05, 0.22)
    disc = gblur(disc[..., None].repeat(3, -1) * 255, 3)[..., 0] / 255
    b = b * 1.25 + 18
    return np.clip(b * 0.9 + disc[..., None] * np.array([255, 190, 120]) * 0.6, 0, 255)

def bowed_page(top_px, k, cx=FW / 2):
    """Sample the page into the frame with a horizontal bow: the sides come toward the lens (bigger,
    curving up), the middle falls back. top_px: frame y of the page's top edge."""
    yy, xx = np.mgrid[0:FH, 0:FW].astype(np.float32)
    u = (xx - cx) / (pw * k / 2)                      # -1..1 across the page
    bow = 1 + 0.035 * u ** 2                          # sides nearer: magnified
    sx = cx + (xx - cx) / bow
    lift = 38 * u ** 2                                # sides curl up in frame
    py = (yy + lift - top_px) / (k * bow)
    px = (sx - (cx - pw * k / 2)) / k
    inside = (px >= 0) & (px < pw - 1) & (py >= 0) & (py < ph - 1)
    x0 = np.clip(px.astype(int), 0, pw - 2); y0 = np.clip(py.astype(int), 0, ph - 2)
    fx = (px - x0)[..., None]; fy = (py - y0)[..., None]
    s = (page[y0, x0] * (1 - fx) * (1 - fy) + page[y0, x0 + 1] * fx * (1 - fy)
         + page[y0 + 1, x0] * (1 - fx) * fy + page[y0 + 1, x0 + 1] * fx * fy)
    # light: low sun from frame left grazing the bow; the right half turns away and darkens
    shade = 1.02 - 0.10 * (u + 1) / 2 - 0.06 * np.clip(u, 0, 1) ** 2
    s *= shade[..., None]
    a = inside.astype(np.float32)
    a = gblur(a[..., None].repeat(3, -1) * 255, 1.2)[..., :1] / 255     # soft paper edge
    # focus falls off toward the curled sides
    sb = gblur(s, 3.0)
    f = np.clip(np.abs(u) - 0.55, 0, 1)[..., None] / 0.45
    return s * (1 - f) + sb * f, a

def lens(img):
    yy, xx = np.mgrid[0:FH, 0:FW].astype(np.float32)
    # warm sunset grade
    img = img * np.array([1.0, 0.90, 0.74])
    # chromatic aberration: red out, blue in, growing toward the corners
    out = img.copy()
    for ch, sc in ((0, 1.0012), (2, 0.9988)):
        cx, cy = FW / 2, FH / 2
        sx = np.clip(((xx - cx) / sc + cx).astype(int), 0, FW - 1)
        sy = np.clip(((yy - cy) / sc + cy).astype(int), 0, FH - 1)
        out[..., ch] = img[sy, sx, ch]
    img = out
    # halation: highlights bleed warm
    hi = np.clip(img - 200, 0, 255)
    img = img + gblur(hi, 18) * np.array([0.55, 0.25, 0.08])
    # vignette and a soft veiling flare from frame left
    r2 = ((xx / FW - 0.5) / 0.7) ** 2 + ((yy / FH - 0.5) / 0.95) ** 2
    img *= (1 - 0.30 * r2)[..., None]
    img += (np.exp(-(((xx / FW + 0.05) / 0.35) ** 2)) * 22)[..., None] * np.array([1, 0.7, 0.4])
    # 35mm grain: luminance-weighted, slightly clumped
    g = rng.normal(0, 1, (FH, FW)).astype(np.float32)
    g = gblur((g * 40 + 128)[..., None].repeat(3, -1), 0.8)[..., 0] - 128
    lum = img.mean(-1, keepdims=True) / 255
    img += g[..., None] * (0.16 + 0.10 * (1 - lum)) * 0.9
    return np.clip(img, 0, 255).astype(np.uint8)

bg = background()
k = 0.80 * FW / pw
# start: the top of the page, both side edges in frame (her thumbs there in a generated frame)
# end: tight on the signature, the page sides out of frame (her hands have left it), the bottom edge
# and the dirt below it in frame
k2 = 1.15 * FW / pw
for name, top, kk, cx in (("insert_start_v3.png", 120, k, FW / 2),
                          ("insert_end_v3.png", FH - 240 - ph * k2, k2, 1200 + (pw / 2 - 800) * k2)):
    pg, a = bowed_page(top, kk, cx)
    Image.fromarray(lens(bg * (1 - a) + pg * a)).save(H / name)
    print(name, round(top))
