"""Rebuild dropped frames: measure per-frame motion, give each frame its true time, resample to
constant motion with optical-flow interpolation.
Usage: dejudder.py in.mp4 out.mp4 [--metric pan|flow]
pan: whole-frame camera motion (pans, tilts). flow: motion inside the frame (locked-off shots, people)."""
import cv2, numpy as np, sys, subprocess, os
src, dst = sys.argv[1], sys.argv[2]
metric = sys.argv[sys.argv.index('--metric') + 1] if '--metric' in sys.argv else 'pan'
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS); frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
n = len(frames); h, w = frames[0].shape[:2]
gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]
d = []
for a, b in zip(gray, gray[1:]):
    if metric == 'pan':
        (dx, dy), _ = cv2.phaseCorrelate(a.astype(np.float32), b.astype(np.float32)); d.append(np.hypot(dx, dy))
    else:
        f = cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 4, 25, 4, 7, 1.5, 0)
        d.append(np.percentile(np.hypot(f[..., 0], f[..., 1]), 95))
d = np.array(d)
# a step about twice its neighbours' speed is a dropped frame and counts as 2 units
if metric == 'pan':
    ref = np.array([np.median(d[max(0, i-3):i+4]) for i in range(len(d))])
    units = np.where((ref > 0.5) & (d > 1.55 * ref), 2, 1)
else:
    # people move unevenly: each step lasts as long as its motion against its neighbours' speed
    ref = np.array([np.median(np.r_[d[max(0, i-4):i], d[i+1:i+5]]) for i in range(len(d))])
    units = np.where(ref > 1.0, np.clip(d / np.maximum(ref, 1e-6), 0.5, 2.5), 1.0)
print('steps retimed:', [(int(i), round(float(u), 2)) for i, u in enumerate(units) if abs(u - 1) > 0.25])
t = np.concatenate([[0], np.cumsum(units)]).astype(float)

T = np.linspace(0, t[-1], n)  # same frame count and duration, uniform true time
def flow(a, b): return cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 4, 25, 4, 7, 1.5, 0)
gx, gy = np.meshgrid(np.arange(w), np.arange(h)); gx = gx.astype(np.float32); gy = gy.astype(np.float32)
cache = {}
tmp = dst + '.video.mp4'
vw = cv2.VideoWriter(tmp, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
for k, tk in enumerate(T):
    i = min(np.searchsorted(t, tk, side='right') - 1, n - 2)
    a = float((tk - t[i]) / max(t[i+1] - t[i], 1e-6))
    if a < 1e-3: vw.write(frames[i]); continue
    if a > 1 - 1e-3: vw.write(frames[i+1]); continue
    if i not in cache: cache = {i: (flow(gray[i], gray[i+1]), flow(gray[i+1], gray[i]))}
    fab, fba = cache[i]
    A = cv2.remap(frames[i], (gx - a * fab[..., 0]).astype(np.float32), (gy - a * fab[..., 1]).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    B = cv2.remap(frames[i+1], (gx - (1 - a) * fba[..., 0]).astype(np.float32), (gy - (1 - a) * fba[..., 1]).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    vw.write(cv2.addWeighted(A, 1 - a, B, a, 0))
vw.release()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', tmp, '-i', src, '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264',
                '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-crf', '16', '-r', str(fps), '-c:a', 'copy', dst], check=True)
os.remove(tmp); print('wrote', dst)
