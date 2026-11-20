"""Extract Leonard's chosen signature (bottom centre of signature_sheet_leonard.webp) as ink alpha.
Writes signature_v2.png: RGBA, blue-black ink, alpha from the stroke darkness, 2x upscaled."""
import numpy as np
from PIL import Image, ImageFilter
from pathlib import Path
H = Path(__file__).parent
im = Image.open(H / "signature_sheet_leonard.webp").convert("L").crop((820, 1090, 1530, 1430))
g = np.asarray(im, dtype=np.float32)
bg = np.asarray(im.filter(ImageFilter.GaussianBlur(40)), dtype=np.float32)  # flatten the paper
d = np.clip((bg - g) / 150.0, 0, 1)
d = np.clip((d - 0.05) / 0.6, 0, 1) ** 0.55                                    # kill paper noise, keep pressure
a = Image.fromarray((d * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(3)).resize((im.width * 2, im.height * 2), Image.LANCZOS)
A = np.asarray(a.filter(ImageFilter.GaussianBlur(1.6)), dtype=np.float32) / 255
solid = np.clip((A - 0.18) / 0.30, 0, 1)                                      # ballpoint: a solid core
a = Image.fromarray((np.maximum(solid * 0.88, np.asarray(a, dtype=np.float32) / 255) * 255).astype(np.uint8))
ink = Image.new("RGBA", a.size, (24, 30, 78, 0))
ink.putalpha(a)
ink.save(H / "signature_v2.png")
print(a.size)
