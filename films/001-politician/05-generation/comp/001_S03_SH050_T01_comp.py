import cv2, numpy as np, sys, subprocess
V, PA, OUT, S = sys.argv[1:5]
cap = cv2.VideoCapture(V); frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
N = len(frames); H, W = frames[0].shape[:2]
ref = frames[24].astype(np.float32)
plate = cv2.imread(PA).astype(np.float32)
blur = lambda a, s: cv2.GaussianBlur(a, (0, 0), s)
# colour: per-channel gain on far buildings (unchanged region)
reg = (slice(0, int(H*0.25)), slice(int(W*0.35), int(W*0.95)))
gain = ref[reg].reshape(-1, 3).mean(0) / plate[reg].reshape(-1, 3).mean(0)
print("plate gain BGR", gain.round(3))
plate *= gain
# grain level: temporal std of the video in a quiet area (top middle)
stack = np.stack([f[reg].astype(np.float32) for f in frames[::6]])
sig = float(stack.std(0).mean()); print("grain sigma (temporal)", round(sig, 2))
# per-frame global exposure flicker
qm = [f[reg].astype(np.float32).mean() for f in frames]
refm = ref[reg].mean()
# masks vs the reference frame (the plate base)
rg = blur(cv2.cvtColor(frames[24], cv2.COLOR_BGR2GRAY).astype(np.float32), 1.5)
soft, tight = [], []
for f in frames:
    d = np.abs(blur(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype(np.float32), 1.5) - rg)
    m = cv2.morphologyEx((d > 6).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    soft.append(cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))))
    t = cv2.morphologyEx((d > 20).astype(np.uint8), cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    tight.append(cv2.dilate(t, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))))
soft, tight = np.stack(soft), np.stack(tight)
box = np.zeros((H, W), np.uint8)
poly = np.array([(0,330),(60,320),(95,300),(105,270),(150,258),(200,265),(225,295),(225,345),(250,360),(270,380),(300,425),(330,470),(345,520),(345,545),(400,575),(470,630),(0,630)], np.int32)
cv2.fillPoly(box, [poly], 1)
box = cv2.dilate(box, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))).astype(np.float32)
box = blur(box, 3)
rng = np.random.default_rng(1)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "24", "-i", "-",
                      "-i", V, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p",
                      "-c:a", "copy", OUT], stdin=subprocess.PIPE)
prev = []
for i, f in enumerate(frames):
    ff = f.astype(np.float32)
    A = blur(soft[max(0, i-4):i+5].max(0).astype(np.float32), 7)[..., None]
    B = np.maximum(blur(tight[max(0, i-2):i+3].max(0).astype(np.float32), 2.5), box)[..., None]
    pl = plate * (qm[i] / refm)
    noise = blur(rng.normal(0, 1, (H, W)).astype(np.float32), 0.6)[..., None]
    pl = pl + noise / noise.std() * sig
    out = (1 - B) * (pl + A * (ff - ref)) + B * ff
    o = np.clip(out, 0, 255).astype(np.uint8)
    p.stdin.write(o.tobytes())
    if i in (0, 72, 150, 240, 300, 336):
        cv2.imwrite(f"{S}/out_{i}.jpg", o); cv2.imwrite(f"{S}/mask_{i}.jpg", (np.concatenate([A[...,0],B[...,0]],1)*255).astype(np.uint8))
p.stdin.close(); p.wait()
print("done", N)
