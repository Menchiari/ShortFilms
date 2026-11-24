"""Frame Fix: step through a take, mark the bad frames yourself, rebuild them with RIFE.

Open:   python3 tools/media/framefix.py path/to/take.mp4
Keys:   right / left arrow (or . and ,)  one frame        shift+arrow (or > and <)  ten frames
        space  play / pause at 24 fps
        d  this frame is a DUPLICATE (or a glitch): rebuilt from the frames on either side
        s  the motion SKIPS into this frame: the few frames around it are rebuilt so the jump is spread out
        x  CUT this frame (for a frozen tail); the audio is cut with it
        u  undo the last mark        c  clear all marks
        r  RENDER: writes <take>_ff.mp4 next to the take (never overwrites), from the original, in one pass
        q  quit
Without the window (same marks): python3 tools/media/framefix.py take.mp4 --marks "d:12 s:24 s:33 x:92-95"

Setup once on a Mac:  brew install ffmpeg
                      python3 -m pip install torch numpy opencv-python
                      python3 tools/media/rife.py setup
"""
import os, sys, subprocess
import numpy as np, cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixframes import read

LEFT = {63234, 65361, 2424832, ord(',')}; RIGHT = {63235, 65363, 2555904, ord('.')}
LEFT10 = {ord('<')}; RIGHT10 = {ord('>')}

def tc(k, fps):
    f = round(fps); return '%02d:%02d:%02d' % (k // f // 60, k // f % 60, k % f)

def parse(spec):
    marks = {}
    for item in spec.split():
        kind, rng = item.split(':'); a, _, b = rng.partition('-')
        for k in range(int(a), int(b or a) + 1): marks[k] = kind
    return marks

def render(src, frames, fps, marks):
    import rife
    n = len(frames); out = list(frames); done = []
    # duplicates: each run of marked frames is rebuilt between the good frames around it
    k = 0
    while k < n:
        if marks.get(k) == 'd':
            m = k
            while m + 1 < n and marks.get(m + 1) == 'd': m += 1
            a, b = k - 1, m + 1
            if a >= 0 and b < n:
                for j in range(k, m + 1):
                    out[j] = rife.interp(frames[a], frames[b], (j - a) / (b - a)); done.append(j)
            k = m + 1
        else: k += 1
    # skips: the missing step is shared out over a 6-frame window, ends of the window stay original
    units = np.ones(n - 1)
    for k, v in marks.items():
        if v == 's' and 1 <= k < n: units[k - 1] = 2
    t = np.concatenate([[0], np.cumsum(units)])
    wins = []
    for k in sorted(k for k, v in marks.items() if v == 's'):
        w0, w1 = max(0, k - 3), min(n - 1, k + 2)
        if wins and w0 <= wins[-1][1]: wins[-1][1] = max(wins[-1][1], w1)
        else: wins.append([w0, w1])
    for w0, w1 in wins:
        T = np.linspace(t[w0], t[w1], w1 - w0 + 1)
        for j in range(w0 + 1, w1):
            i = min(np.searchsorted(t, T[j - w0], side='right') - 1, n - 2)
            a = float((T[j - w0] - t[i]) / (t[i + 1] - t[i]))
            out[j] = frames[i] if a < 1e-3 else frames[i + 1] if a > 1 - 1e-3 else rife.interp(frames[i], frames[i + 1], a)
            done.append(j)
    cuts = sorted(k for k, v in marks.items() if v == 'x')
    keep = [j for j in range(n) if j not in cuts]
    base, _ = os.path.splitext(src); dst = base + '_ff.mp4'; i = 2
    while os.path.exists(dst): dst = base + '_ff%d.mp4' % i; i += 1
    h, w = frames[0].shape[:2]
    gone = ''.join('+between(t,%.6f,%.6f)' % (c / fps, (c + 1) / fps - 1e-6) for c in cuts)
    afilter = ['-af', "aselect='not(0%s)',asetpts=N/SR/TB" % gone] if cuts else []
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{w}x{h}', '-r', str(fps),
                          '-i', '-', '-i', src, '-map', '0:v', '-map', '1:a?', '-c:v', 'libx264', '-preset', 'slow', '-crf', '12',
                          '-pix_fmt', 'yuv420p', *afilter, '-c:a', 'aac', '-b:a', '256k', '-t', '%.6f' % (len(keep) / fps), dst],
                         stdin=subprocess.PIPE)
    for j in keep: p.stdin.write(out[j].tobytes())
    p.stdin.close()
    if p.wait(): raise SystemExit('ffmpeg failed')
    with open(os.path.splitext(dst)[0] + '_marks.txt', 'w') as f:
        f.write('source: %s\nmarks: %s\nrebuilt: %s\ncut: %s\n' % (os.path.basename(src),
                ' '.join('%s:%d' % (v, k) for k, v in sorted(marks.items())), sorted(set(done)), cuts))
    print('wrote', dst, '- rebuilt frames', sorted(set(done)), '- cut', cuts)
    return dst

def gui(src, frames, fps):
    n = len(frames); k = 0; marks = {}; history = []; playing = False; msg = ''
    h, w = frames[0].shape[:2]; sc = min(1.0, 1400 / w)
    cv2.namedWindow('Frame Fix', cv2.WINDOW_AUTOSIZE)
    col = {'d': (0, 165, 255), 's': (255, 200, 0), 'x': (0, 0, 255)}
    name = {'d': 'DUPLICATE', 's': 'SKIP INTO', 'x': 'CUT'}
    while True:
        img = cv2.resize(frames[k], None, fx=sc, fy=sc) if sc < 1 else frames[k].copy()
        bar = np.zeros((70, img.shape[1], 3), np.uint8)
        cv2.putText(bar, 'frame %d / %d   %s   %s' % (k, n - 1, tc(k, fps), name.get(marks.get(k), '')), (10, 28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, col.get(marks.get(k), (255, 255, 255)), 2)
        cv2.putText(bar, msg or 'arrows step  space play  d dup  s skip  x cut  u undo  r render  q quit', (10, 58),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (180, 180, 180), 1)
        for j, v in marks.items():  # marks on a timeline under the picture
            x = int(j / max(n - 1, 1) * (img.shape[1] - 1)); cv2.line(bar, (x, 62), (x, 69), col[v], 2)
        cv2.imshow('Frame Fix', np.vstack([img, bar]))
        key = cv2.waitKeyEx(int(1000 / fps) if playing else 0)
        if playing and key == -1: k = (k + 1) % n; continue
        if key == -1: continue
        c = key & 0xFF if key < 256 else None; msg = ''
        if key in RIGHT: k = min(n - 1, k + 1)
        elif key in LEFT: k = max(0, k - 1)
        elif key in RIGHT10: k = min(n - 1, k + 10)
        elif key in LEFT10: k = max(0, k - 10)
        elif c == ord(' '): playing = not playing
        elif c in (ord('d'), ord('s'), ord('x')):
            marks[k] = chr(c); history.append(k)
        elif c == ord('u') and history: marks.pop(history.pop(), None)
        elif c == ord('c'): marks.clear(); history.clear()
        elif c == ord('r'):
            if not marks: msg = 'no marks yet'; continue
            msg = 'rendering...'; cv2.waitKey(1)
            dst = render(src, frames, fps, marks); msg = 'saved ' + os.path.basename(dst)
        elif c in (ord('q'), 27): break
    cv2.destroyAllWindows()

if __name__ == '__main__':
    if len(sys.argv) < 2: print(__doc__); sys.exit()
    src = sys.argv[1]; frames, fps = read(src)
    if '--marks' in sys.argv: render(src, frames, fps, parse(sys.argv[sys.argv.index('--marks') + 1]))
    else: gui(src, frames, fps)
