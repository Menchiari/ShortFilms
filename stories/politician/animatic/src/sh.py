"""Shot authoring helpers."""
import math, random
import numpy as np
import bpy
import core
from core import reset, PAL
import sets
from puppet import *
from sim import *
import props as PR

def cam(pos, tgt, lens=35, hh=0.0, roll=0):
    return {"keys": [(0, pos, tgt, lens)], "hh": hh, "roll": roll}

def move(keys, hh=0.0, ease="io", spline=False, roll=0):
    return {"keys": keys, "hh": hh, "ease": ease, "spline": spline, "roll": roll}

def follow(actor, pos, lens=50, offset=(0, 0, 0.6), lag=0.3, hh=0.0, joint=PELVIS):
    return {"follow": actor, "pos": pos, "lens": lens, "offset": offset, "lag": lag, "hh": hh, "joint": joint}

def fdir(a, b):
    return math.degrees(math.atan2(-(b[0] - a[0]), b[1] - a[1]))

def screen_x(pos, tgt, pt):
    f = np.array(tgt[:2], float) - np.array(pos[:2], float); f /= np.linalg.norm(f)
    right = np.array((f[1], -f[0])); return float(np.dot(np.array(pt[:2], float) - np.array(pos[:2], float), right))

def slots(center, n, r0=1.4, dr=0.85, arc=(0, 360), seed=0, spacing=1.0):
    """Ring slots around center, inner rings first, spread over arc (degrees)."""
    rng = np.random.default_rng(seed); out = []; r = r0
    while len(out) < n:
        span = math.radians(arc[1] - arc[0]); k = max(1, int(span * r / spacing))
        for i in range(k):
            a = math.radians(arc[0]) + span * (i + 0.5) / k + rng.uniform(-0.12, 0.12)
            rr = r + rng.uniform(-0.15, 0.25)
            out.append((center[0] + rr * math.cos(a), center[1] + rr * math.sin(a)))
            if len(out) == n:
                break
        r += dr
    return np.array(out)

def assign(P0, S, center):
    """Closest agents take the inner slots."""
    d0 = np.linalg.norm(P0 - np.array(center)[None], axis=1); ds = np.linalg.norm(S - np.array(center)[None], axis=1)
    order_a = np.argsort(d0); order_s = np.argsort(ds); T = np.zeros_like(P0)
    for a, s in zip(order_a, order_s):
        T[a] = S[s]
    return T

def ride(actor, t0, t1, path_fn, base="drive", seat=(-0.42, -0.25), **kw):
    """Seat an actor in the car. path_fn(t) -> (pos, yaw)."""
    f0, f1 = F(t0), F(t1)
    def fn(f):
        pos, yaw = path_fn(f / core.FPS); w = PR.car_world(pos, yaw, seat[0], seat[1])
        p = pose(base, x=float(w[0]), y=float(w[1]), yaw=yaw); p.update(kw); return p
    actor.tracks.append((f0, f1, fn, 0))

def car_cb(o, path_fn):
    def cb(f):
        pos, yaw = path_fn(f / core.FPS); PR.place(o, (pos[0], pos[1], 0), yaw)
    return cb

def hide_obj(o):
    o.hide_render = True
    for c in o.children_recursive:
        c.hide_render = True

def crowd_people(prefix, n, nf, seed, lod="low"):
    rnd = random.Random(seed)
    return [crowd_costume(rnd) for _ in range(n)]

def _inside(p, walls, m=0.4):
    return any(x0 - m < p[0] < x1 + m and y0 - m < p[1] < y1 + m for (x0, x1, y0, y1) in walls)

def falloff(center, n, r_min=1.2, lam=2.4, arc=(0, 360), seed=0, min_sep=0.7, walls=(), groups=0.35, max_r=60.0, avoid=()):
    """Where a crowd stands: density falls off with distance from the focus (radial pdf ~ r * exp(-r / lam)).
    About half in the dense core, the rest spread around, alone or in small groups. Spacing grows with distance."""
    rng = np.random.default_rng(seed); pts = []; tries = 0; c = np.array(center[:2], float)
    def ok(p, sep):
        if _inside(p, walls): return False
        if any(np.linalg.norm(p - np.array(a[:2])) < r for a, r in avoid): return False
        return all(np.linalg.norm(p - q) >= sep for q in pts)
    while len(pts) < n and tries < n * 600:
        tries += 1
        r = r_min + rng.gamma(2.0, lam)
        if r > max_r: continue
        a = math.radians(rng.uniform(*arc)); p = c + r * np.array((math.cos(a), math.sin(a)))
        if not ok(p, min_sep * (1 + 0.07 * (r - r_min))): continue
        pts.append(p)
        if r > r_min + 1.7 * lam and rng.random() < groups:
            for _ in range(int(rng.integers(1, 3))):
                if len(pts) >= n: break
                q = p + rng.normal(0, 0.65, 2)
                if 0.5 < np.linalg.norm(q - p) < 1.4 and ok(q, 0.5): pts.append(q)
    while len(pts) < n:
        pts.append(c + rng.normal(0, max(3.0, lam * 3), 2))
    return np.array(pts[:n])

def band(front, n, lam, y_lo, y_hi, seed=0, dirx=-1.0, min_sep=0.75, walls=(), groups=0.3):
    """A crowd in a street: dense at the front line x = front, thinning out behind it (exponential gaps)."""
    rng = np.random.default_rng(seed); pts = []; tries = 0
    while len(pts) < n and tries < n * 600:
        tries += 1
        d = rng.gamma(2.0, lam) if rng.random() > 0.15 else rng.exponential(lam * 3)
        p = np.array((front + dirx * d, rng.uniform(y_lo, y_hi)))
        if _inside(p, walls): continue
        if any(np.linalg.norm(p - q) < min_sep * (1 + 0.05 * d) for q in pts): continue
        pts.append(p)
        if d > 2 * lam and rng.random() < groups and len(pts) < n:
            q = p + rng.normal(0, 0.6, 2)
            if not _inside(q, walls) and all(np.linalg.norm(q - z) >= 0.5 for z in pts): pts.append(q)
    while len(pts) < n:
        pts.append(np.array((front + dirx * rng.gamma(2.0, lam), rng.uniform(y_lo, y_hi))))
    return np.array(pts[:n])
