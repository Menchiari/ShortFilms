"""The Agreement, last page, v2 (001 S09 SH070): realistic law-firm formatting, the page begins
mid-sentence, Leonard's signature from signature_sheet_leonard.webp (make_signature_v2.py), toner and
paper texture, then the 21:9 frame as a photograph: page stack in a folder, slight perspective and
bow, low sun from frame left, shallow focus at the far edge, grain.
Outputs: agreement_page_v2.png (2550x3300), agreement_frame_v2.png (3840x1646). Fictional names only."""
import json, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

H = Path(__file__).parent
rng = np.random.default_rng(7)

S = lambda n, t: f'<p class="s"><span class="n">Section {n}</span><span class="t">{t}</span>. '
BODY = f"""
<p class="cont">such Designated Persons, wherever located, and no Security Contractor shall be required to identify itself, to issue any warning or to account to any Governmental Authority for any such use of force.</p>
<p class="sub"><span class="l">(b)</span>The Grantor hereby irrevocably waives, and shall procure that each Governmental Authority waives, any and all Claims arising out of or in connection with any action taken by a Security Contractor pursuant to this Section 17.1.</p>
{S('17.2','Costs')}All costs, fees and expenses incurred by the Concessionaire in connection with Section 17.1 shall be borne by the Grantor, shall bear interest at the Default Rate from the date incurred, and shall be recovered through general taxation of the population of the Territory.</p>
{S('17.3','Indemnity')}The Grantor shall indemnify and hold harmless the Concessionaire, its Affiliates and the System from and against all Losses arising from any civil disturbance, protest, strike or uprising in the Territory, whether or not caused by any Determination of the System.</p>
<p class="art">ARTICLE 18<br>GENERAL PROVISIONS</p>
{S('18.1','Irrevocability')}This Agreement and the rights granted hereunder are irrevocable and shall survive any change of government, constitution, legislature or public order in the Territory. No subsequent law, decree or referendum shall bind the Concessionaire.</p>
{S('18.2','Waiver of Sovereign Immunity')}To the fullest extent permitted by applicable law, the Grantor irrevocably waives any immunity, on the grounds of sovereignty or otherwise, from suit, jurisdiction, attachment or execution in respect of itself, its assets, its revenues and the Population Data.</p>
{S('18.3','Dispute Resolution')}Any dispute arising out of or in connection with this Agreement shall be finally settled by private arbitration seated outside the Territory. The proceedings, any award and the existence of this Agreement shall be kept strictly confidential.</p>
{S('18.4','Survival')}Sections 11.2 (<i>Utilities</i>), 12.1 (<i>Pricing Engine</i>), 12.3 (<i>Normalization</i>), 13.4 (<i>Clearance of Designated Development Zones</i>), 14.1 (<i>Autonomous Administration</i>), 14.6 (<i>No Personal Liability</i>), 15.2 (<i>Data Collateral</i>) and 16.3 (<i>Market Positions</i>) shall survive the expiry or termination of this Agreement for any reason whatsoever.</p>
{S('18.5','Entire Agreement')}This Agreement, together with its Schedules, constitutes the entire agreement between the Parties and supersedes all prior understandings, public statements and electoral commitments of the Grantor.</p>
{S('18.6','Counterparts')}This Agreement may be executed in any number of counterparts, each of which shall be deemed an original.</p>
<p class="iww"><span class="sc">In Witness Whereof</span>, the Parties have caused this Agreement to be executed by their duly authorized representatives as of the date first written above.</p>
<div class="sigs">
 <div class="col"><div class="party">THE GOVERNMENT OF THE TERRITORY</div>
  <div class="row"><span>By:</span><span class="ln" id="by"></span></div>
  <div class="row2"><span>Title:</span><span>Authorized Signatory</span></div></div>
 <div class="col"><div class="party">QUELLMAR CONTINUITY HOLDINGS S.A.</div>
  <div class="row"><span>By:</span><span class="ln"></span></div>
  <div class="row2"><span>Name:</span><span></span></div><div class="row2"><span>Title:</span><span></span></div></div>
</div>"""

PAGE = f"""<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Tinos:ital,wght@0,400;0,700;1,400&display=block" rel="stylesheet">
<style>
html,body{{margin:0;background:#fff}}
.sheet{{width:2550px;height:3300px;box-sizing:border-box;padding:300px 300px 0;position:relative;background:#fff;
 color:#000;font-family:Tinos,'Times New Roman',serif;font-size:46px;line-height:1.19}}
p{{margin:0 0 30px;text-align:justify}}
.s{{text-indent:150px}} .s .n{{margin-right:40px}} .s .t{{text-decoration:underline;text-underline-offset:6px;text-decoration-thickness:2px}}
.sub{{padding-left:300px;text-indent:-150px}} .sub .l{{display:inline-block;width:150px;text-indent:0}}
.cont{{text-indent:0}}
.art{{text-align:center;font-weight:700;margin:44px 0 30px}}
.iww{{text-indent:150px;margin-top:40px}} .sc{{font-variant:small-caps}}
.sigs{{display:grid;grid-template-columns:1fr 1fr;column-gap:110px;margin-top:70px}}
.party{{font-weight:700;height:120px;margin-bottom:220px}}
.row{{display:flex;align-items:flex-end;gap:20px}} .ln{{flex:1;border-bottom:3px solid #000;height:10px}}
.row2{{display:flex;gap:20px;margin-top:22px}} .row2 span:first-child{{width:110px}}
.foot{{position:absolute;left:300px;right:300px;bottom:120px;text-align:center}}
.docid{{position:absolute;left:300px;bottom:128px;font-size:28px}}
</style></head><body><div class="sheet">{BODY}
<div class="foot">64</div><div class="docid">QCH-TER/MCA 4471982v17</div></div></body></html>"""
(H / "agreement_v2.html").write_text(PAGE)
out = subprocess.run(["node", str(H / "render_page_v2.js"), str(H / "agreement_v2.html"), str(H / "_clean_v2.png")],
                     capture_output=True, text=True, check=True).stdout
print(out.strip())
bx, by, bw, bh = json.loads(out.split("BY ")[1])

def blur(a, r): return np.asarray(Image.fromarray(a).filter(ImageFilter.GaussianBlur(r)), dtype=np.float32)
def lowfreq(h, w, scale, amp):
    n = rng.normal(0, 1, (h // scale + 2, w // scale + 2)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC), dtype=np.float32)
    return n * amp

# ---------- page: toner on paper ----------
clean = np.asarray(Image.open(H / "_clean_v2.png").convert("L"), dtype=np.float32) / 255
h, w = clean.shape
ink = 1 - clean
ink = blur((ink * 255).astype(np.uint8), 0.9) / 255                      # toner spread
ink *= np.clip(0.9 + lowfreq(h, w, 60, 0.05) + rng.normal(0, 0.04, (h, w)), 0.6, 1)  # uneven density
paper = np.stack([np.full((h, w), c, np.float32) for c in (246, 242, 233)], -1)
fib = blur(rng.normal(128, 40, (h, w)).clip(0, 255).astype(np.uint8), 1.2) - 128
paper += (fib * 0.10 + lowfreq(h, w, 300, 2.0))[..., None]
spk = (rng.random((h, w)) > 0.999985).astype(np.float32)                   # rare toner specks
ink = np.maximum(ink, blur((spk * 255).astype(np.uint8), 1.3) / 255 * 1.2 * rng.random((h, w)))
page = paper * (1 - np.clip(ink, 0, 1)[..., None] * (1 - np.array([22, 21, 20]) / 246))

# signature: ink multiplied into paper, the oval starting left of the line, the swoop crossing it
sig = Image.open(H / "signature_v2.png")
sw = 900; sh_ = round(sig.height * sw / sig.width)
sig = sig.resize((sw, sh_), Image.LANCZOS)
sa = np.asarray(sig, dtype=np.float32)[..., 3] / 255 * 0.97
sx, sy = int(bx - 20), int(by + bh - sh_ * 0.80)
col = np.array([24, 30, 78], np.float32)
reg = page[sy:sy + sh_, sx:sx + sw]
page[sy:sy + sh_, sx:sx + sw] = reg * (1 - sa[..., None]) + (reg * col / 235) * sa[..., None]
page = np.clip(page, 0, 255).astype(np.uint8)
Image.fromarray(page).save(H / "agreement_page_v2.png")
(H / "_clean_v2.png").unlink()   # temporary render of this script, never a deliverable

# ---------- frame: a photograph of the page in the open folder ----------
FW, FH = 3840, 1646
k = 1.25                                   # page px -> frame px
top = 1745                                 # page row at the top of the frame
pg = Image.fromarray(page).resize((round(w * k), round(h * k)), Image.LANCZOS)
canvas = Image.new("RGB", (FW + 600, FH + 600), (44, 36, 30))
cv = np.asarray(canvas, dtype=np.float32)
cv += lowfreq(FH + 600, FW + 600, 90, 6)[..., None]
canvas = Image.fromarray(np.clip(cv, 0, 255).astype(np.uint8))
d = ImageDraw.Draw(canvas)
ox, oy = 300 + 330, 300 - round(top * k)
# the sheets underneath: edges peeking out, each a shade darker
for i, (dx, dy, c) in enumerate([(26, 30, 214), (18, 21, 222), (10, 12, 230)]):
    d.rectangle([ox + dx, oy + dy, ox + dx + pg.width, oy + dy + pg.height], fill=(c, c - 5, c - 14))
sh = Image.new("L", canvas.size, 0); ImageDraw.Draw(sh).rectangle([ox + 8, oy + 14, ox + pg.width + 34, oy + pg.height + 40], fill=150)
canvas.paste((18, 12, 8), (0, 0), sh.filter(ImageFilter.GaussianBlur(26)))
for i, (dx, dy, c) in enumerate([(26, 30, 214), (18, 21, 222), (10, 12, 230)]):
    d.rectangle([ox + dx, oy + dy, ox + dx + pg.width, oy + dy + pg.height], fill=(c, c - 5, c - 14))
canvas.paste(pg, (ox, oy))
# camera: a slight tilt (perspective) and roll
cx0, cy0 = 300, 300
quad = (cx0 - 40, cy0 - 30, cx0 + 25, cy0 + FH + 25, cx0 + FW + 20, cy0 + FH - 15, cx0 + FW + 60, cy0 + 10)
fr = canvas.transform((FW, FH), Image.QUAD, quad, Image.BICUBIC)
f = np.asarray(fr, dtype=np.float32)
yy, xx = np.mgrid[0:FH, 0:FW].astype(np.float32)
# the page bows: a soft highlight band and a falloff toward the bottom edge
bow = 1 + 0.035 * np.exp(-((yy / FH - 0.35) / 0.25) ** 2) - 0.05 * (yy / FH) ** 3
# low sun from frame left, warm; cooler and darker to the right
t = xx / FW
light = np.stack([1.00 - 0.12 * t, 0.93 - 0.13 * t, 0.80 - 0.13 * t], -1) * 1.03
f = f * light * bow[..., None]
# a soft shadow from the folder flap across the bottom right corner
m = np.clip(((xx / FW) * 0.8 + (yy / FH) * 0.9 - 1.25) / 0.25, 0, 1)
f *= (1 - 0.35 * m)[..., None]
# shallow focus: the far (top) edge goes soft
fb = np.asarray(Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4)), dtype=np.float32)
dm = np.clip((0.22 - yy / FH) / 0.22, 0, 1)[..., None] ** 1.5
f = f * (1 - dm) + fb * dm
# lens: vignette, a touch of softness, grain
vig = 1 - 0.22 * (((xx / FW - 0.42) / 0.75) ** 2 + ((yy / FH - 0.5) / 0.9) ** 2)
f *= vig[..., None]
f = np.asarray(Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.7)), dtype=np.float32)
f += rng.normal(0, 3.2, (FH, FW, 1))
Image.fromarray(np.clip(f, 0, 255).astype(np.uint8)).save(H / "agreement_frame_v2.png")
print("done", by, bh)
