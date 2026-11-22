# Replace the balcony man's head and shoulders during his turn with the same region from an earlier moment of the same take.
# Run: python3 001_S03_SH050_T05_comp.py <T05.mp4> <out.mp4> <debug dir> 8.3334 13.7084 5.3334
import cv2, numpy as np, sys, subprocess
SRC, OUT, DBG = sys.argv[1:4]
A, B, SHIFT = float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])  # replace [A,B] s with frames from t-SHIFT
c = cv2.VideoCapture(SRC); fr = []
while True:
    ok, f = c.read()
    if not ok: break
    fr.append(f)
H, W = fr[0].shape[:2]
mask = np.zeros((H, W), np.float32)
cv2.ellipse(mask, (int(W * 0.115), int(H * 0.40)), (int(W * 0.12), int(H * 0.30)), 0, 0, 360, 1, -1)
mask = cv2.GaussianBlur(mask, (0, 0), 18)[..., None]
cv2.imwrite(DBG + "/hold_mask.png", (mask[..., 0] * 255).astype(np.uint8))
a, b, s, fade = int(A * 24), int(B * 24), int(round(SHIFT * 24)), 8
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "24", "-i", "-",
                      "-i", SRC, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "14", "-preset", "slow",
                      "-pix_fmt", "yuv420p", "-c:a", "copy", OUT], stdin=subprocess.PIPE)
for i, f in enumerate(fr):
    if a <= i <= b:
        t = min(1.0, (i - a + 1) / fade, (b - i + 1) / fade)
        o = f.astype(np.float32) * (1 - mask * t) + fr[i - s].astype(np.float32) * (mask * t)
        f = np.clip(o, 0, 255).astype(np.uint8)
        if (i - a) % 12 == 0: cv2.imwrite(f"{DBG}/hold_{i}.jpg", f[100:630, 0:520])
    p.stdin.write(f.tobytes())
p.stdin.close(); p.wait(); print("done", len(fr), a, b, s)
