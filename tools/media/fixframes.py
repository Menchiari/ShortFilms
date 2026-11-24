"""Fix skipped frames at known places, touching only the frames around each skip.

Usage:
  python tools/media/fixframes.py find take.mp4              list likely skips (frame numbers)
  python tools/media/fixframes.py fix take.mp4 out.mp4 24 48 72   fix the skips that land on these frames
  python tools/media/fixframes.py fix take.mp4 out.mp4 --every 24 fix a skip at every second
  python tools/media/fixframes.py smooth take.mp4 out.mp4 5 19     even out frames 5 to 19 (held frames and skips mixed)

Frame N means the first frame after the jump (0 = first frame of the clip; frame 24 = 1 s at 24 fps).
Around each skip a 6-frame window is retimed so the lost step is shared out; the first and last
frames of the window and every frame outside it stay original. Same frame count, same duration,
audio copied. Needs: pip install opencv-python-headless numpy (and ffmpeg)."""
import cv2, numpy as np, sys, subprocess

def read(path):
    cap = cv2.VideoCapture(path); fps = cap.get(cv2.CAP_PROP_FPS); fr = []
    while True:
        ok, f = cap.read()
        if not ok: break
        fr.append(f)
    return fr, fps

def motion(frames):
    g = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames]; d = []
    for a, b in zip(g, g[1:]):
        fl = cv2.calcOpticalFlowFarneback(a, b, None, 0.5, 4, 25, 4, 7, 1.5, 0)
        d.append(np.percentile(np.hypot(fl[..., 0], fl[..., 1]), 95))
    return np.array(d)

def find(path):
    frames, fps = read(path); d = motion(frames)
    ref = np.array([np.median(np.r_[d[max(0, i-4):i], d[i+1:i+5]]) for i in range(len(d))])
    hits = [(i + 1, d[i] / ref[i]) for i in range(len(d)) if ref[i] > 1.0 and d[i] > 1.6 * ref[i]]
    for n, r in hits:
        print('frame %d (%d s %d f): motion %.1fx its neighbours' % (n, n // round(fps), n % round(fps), r))
    if not hits: print('no clear skips')

def interp(A, B, t):
    ga, gb = cv2.cvtColor(A, cv2.COLOR_BGR2GRAY), cv2.cvtColor(B, cv2.COLOR_BGR2GRAY)
    dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    f01, f10 = dis.calc(ga, gb, None), dis.calc(gb, ga, None)
    ft0 = -(1 - t) * t * f01 + t * t * f10           # flow from the new frame back to A
    ft1 = (1 - t) * (1 - t) * f01 - t * (1 - t) * f10  # and forward to B
    h, w = ga.shape; gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    wa = cv2.remap(A, gx + ft0[..., 0], gy + ft0[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    wb = cv2.remap(B, gx + ft1[..., 0], gy + ft1[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    return cv2.addWeighted(wa, 1 - t, wb, t, 0)

def write(out, fps, src, dst):
    """Raw frames piped straight into x264 at near-lossless quality, audio copied from the source."""
    h, w = out[0].shape[:2]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{w}x{h}', '-r', str(fps),
                          '-i', '-', '-i', src, '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264', '-preset', 'slow',
                          '-crf', '12', '-pix_fmt', 'yuv420p', '-c:a', 'copy', dst], stdin=subprocess.PIPE)
    for f in out: p.stdin.write(f.tobytes())
    p.stdin.close()
    if p.wait(): raise SystemExit('ffmpeg failed')

def smooth(src, dst, a, b):
    """Frames a..b: each step gets its measured length (a held frame ~0, a skip ~2), then the stretch
    is resampled to even motion. Frames a and b and everything outside stay original."""
    frames, fps = read(src); n = len(frames); b = min(b, n - 1)
    d = motion(frames)
    seg = d[a:b]
    base = np.median(seg[seg > 0.2 * np.median(seg)])
    units = np.clip(seg / base, 0, 2.5)
    t = np.concatenate([[0], np.cumsum(units)])
    T = np.linspace(0, t[-1], b - a + 1)
    out = list(frames)
    for k in range(1, b - a):
        i = min(np.searchsorted(t, T[k], side='right') - 1, b - a - 1)
        span = t[i + 1] - t[i]
        x = 0.0 if span < 1e-6 else float((T[k] - t[i]) / span)
        A, B = frames[a + i], frames[a + i + 1]
        out[a + k] = A if x < 1e-3 else B if x > 1 - 1e-3 else interp(A, B, x)
    write(out, fps, src, dst)
    print('smoothed frames %d to %d (steps measured: %s) - wrote %s' % (a, b, ' '.join('%.1f' % u for u in units), dst))

def fix(src, dst, marks):
    frames, fps = read(src); n = len(frames)
    units = np.ones(n - 1)
    for m in marks:
        if 1 <= m < n: units[m - 1] = 2
    t = np.concatenate([[0], np.cumsum(units)])
    out = list(frames); done = []
    wins = []  # windows around each skip, merged when they touch
    for m in sorted(marks):
        w0, w1 = max(0, m - 3), min(n - 1, m + 2)
        if wins and w0 <= wins[-1][1]: wins[-1][1] = max(wins[-1][1], w1)
        else: wins.append([w0, w1])
    for w0, w1 in wins:
        if w1 - w0 < 2: continue
        T = np.linspace(t[w0], t[w1], w1 - w0 + 1)
        for k in range(w0 + 1, w1):
            i = min(np.searchsorted(t, T[k - w0], side='right') - 1, n - 2)
            a = float((T[k - w0] - t[i]) / (t[i + 1] - t[i]))
            out[k] = frames[i] if a < 1e-3 else frames[i + 1] if a > 1 - 1e-3 else interp(frames[i], frames[i + 1], a)
            done.append(k)
    write(out, fps, src, dst)
    print('fixed skips at frames', sorted(marks), '- rebuilt frames', sorted(set(done)), '- wrote', dst)

if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'find': find(sys.argv[2])
    elif len(sys.argv) == 6 and sys.argv[1] == 'smooth': smooth(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
    elif len(sys.argv) >= 5 and sys.argv[1] == 'fix':
        src, dst, rest = sys.argv[2], sys.argv[3], sys.argv[4:]
        if rest[0] == '--every':
            step = int(rest[1]); cap = cv2.VideoCapture(src); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            marks = list(range(step, n, step))
        else: marks = [int(x) for x in rest]
        fix(src, dst, marks)
    else: print(__doc__)
