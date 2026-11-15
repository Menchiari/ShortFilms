"""Jointed figures for the animatic: forward kinematics, gaits, poses, faces, per-frame mesh update.

Joints: 0 head, 1 neck, 2 pelvis, 3 lsh, 4 lel, 5 lha, 6 rsh, 7 rel, 8 rha, 9 lhip, 10 lkn, 11 lan, 12 lto,
        13 rhip, 14 rkn, 15 ran, 16 rto, 17 nose (a point in front of the face, gives the head its direction).
Yaw: 0 faces +y, positive turns left (counterclockwise). tilt +90 = lying on the back, -90 = face down.
"""
import math, random, os
import numpy as np
import bpy
from mathutils import Matrix
from core import MATS, srgb
import core

NJ = 18
HEAD, NECK, PELVIS, LSH, LEL, LHA, RSH, REL, RHA, LHIP, LKN, LAN, LTO, RHIP, RKN, RAN, RTO, NOSE = range(18)
L_SPINE, L_NECK, L_UA, L_FA, L_TH, L_SH = 0.55, 0.17, 0.29, 0.27, 0.44, 0.44

def R_x(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a); return np.array(((1, 0, 0), (0, c, -s), (0, s, c)))
def R_y(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a); return np.array(((c, 0, s), (0, 1, 0), (-s, 0, c)))
def R_z(a):
    a = math.radians(a); c, s = math.cos(a), math.sin(a); return np.array(((c, -s, 0), (s, c, 0), (0, 0, 1)))

BASE = dict(x=0.0, y=0.0, z=None, yaw=0.0, tilt=0.0, roll=0.0, spine=3.0, twist=0.0, side=0.0,
            hpitch=0.0, hyaw=0.0, hroll=0.0, la=(4.0, 6.0, 12.0), ra=(4.0, 6.0, 12.0), ll=(0.0, 3.0, 2.0), rl=(0.0, 3.0, 2.0),
            ground="feet", eyes=1.0, mouth=0.0, scale=1.0)

def fk(p):
    s = p.get("scale", 1.0)
    Rb = R_z(p["yaw"]) @ R_x(p["tilt"]) @ R_y(p["roll"])
    Rs = Rb @ R_z(p["twist"]) @ R_x(-p["spine"]) @ R_y(p["side"])
    J = np.zeros((NJ, 3))
    J[PELVIS] = (0, 0, 0)
    J[NECK] = Rs @ np.array((0, 0, L_SPINE * s))
    Rh = Rs @ R_z(p["hyaw"]) @ R_x(-p["hpitch"]) @ R_y(p["hroll"])
    J[HEAD] = J[NECK] + Rh @ np.array((0, 0.01, L_NECK * s))
    J[NOSE] = J[HEAD] + Rh @ np.array((0, 0.12 * s, 0))
    for side, (ish, iel, iha), (fl, ab, el) in ((1, (RSH, REL, RHA), p["ra"]), (-1, (LSH, LEL, LHA), p["la"])):
        J[ish] = J[NECK] + Rs @ np.array((side * 0.19 * s, 0, -0.045 * s))
        Rua = Rs @ R_y(-side * ab) @ R_x(fl)
        J[iel] = J[ish] + Rua @ np.array((0, 0, -L_UA * s))
        Rfa = Rua @ R_x(el)
        J[iha] = J[iel] + Rfa @ np.array((0, 0, -L_FA * s))
    for side, (ihp, ikn, ian, ito), (fl, ab, kn) in ((1, (RHIP, RKN, RAN, RTO), p["rl"]), (-1, (LHIP, LKN, LAN, LTO), p["ll"])):
        J[ihp] = Rb @ np.array((side * 0.095 * s, 0, -0.06 * s))
        Rth = Rb @ R_y(-side * ab) @ R_x(fl)
        J[ikn] = J[ihp] + Rth @ np.array((0, 0, -L_TH * s))
        Rsh = Rth @ R_x(-kn)
        J[ian] = J[ikn] + Rsh @ np.array((0, 0, -L_SH * s))
        J[ito] = J[ian] + Rsh @ R_x(-max(0, 90 - kn - fl) * 0.0) @ np.array((0, 0.15 * s, -0.03 * s))
    # placement
    g = p.get("ground", "feet")
    if p.get("z") is not None:
        dz = p["z"]
    elif g == "feet":
        dz = 0.03 - min(J[LAN, 2], J[RAN, 2], J[LTO, 2], J[RTO, 2])
    else:
        dz = 0.07 - J[:NOSE, 2].min()
    J += np.array((p["x"], p["y"], dz))
    return J

# ------------------------------------------------------------------ poses and gaits
POSES = {
    "stand": {},
    "stand_tense": dict(spine=8, la=(10, 10, 30), ra=(10, 10, 30), hpitch=-5),
    "sit_ground": dict(ll=(85, 8, 15), rl=(85, 8, 15), spine=15, la=(20, 15, 20), ra=(20, 15, 20), ground="all"),
    "sit_knees": dict(ll=(100, 10, 100), rl=(95, 10, 95), spine=25, la=(35, 12, 40), ra=(35, 12, 40), ground="all"),
    "lie_back": dict(tilt=88, spine=0, la=(10, 25, 10), ra=(10, 25, 10), ll=(0, 6, 5), rl=(0, 6, 5), ground="all"),
    "lie_front": dict(tilt=-88, la=(150, 30, 30), ra=(140, 30, 40), ll=(0, 8, 10), rl=(0, 8, 25), ground="all"),
    "lie_curl": dict(tilt=88, roll=80, spine=35, ll=(80, 5, 100), rl=(70, 5, 110), la=(70, 10, 120), ra=(80, 10, 110), hpitch=25, ground="all"),
    "lie_cover": dict(tilt=86, la=(10, 25, 10), ra=(150, 10, 150), ll=(15, 6, 25), rl=(5, 6, 10), hpitch=10, ground="all"),
    "prop_elbow": dict(tilt=55, spine=-10, la=(-50, 20, 100), ra=(30, 15, 40), ll=(10, 8, 20), rl=(25, 8, 50), ground="all"),
    "lean_curb": dict(tilt=32, spine=10, la=(-25, 25, 20), ra=(-25, 25, 20), ll=(70, 8, 10), rl=(55, 10, 35), ground="all"),
    "kneel": dict(ll=(90, 5, 90), rl=(-5, 5, 95), spine=10, la=(20, 10, 20), ra=(20, 10, 20), ground="all"),
    "crouch": dict(ll=(100, 10, 125), rl=(100, 10, 125), spine=35, la=(40, 12, 40), ra=(40, 12, 40)),
    "hands_knees": dict(tilt=-55, ll=(60, 5, 100), rl=(60, 5, 100), la=(90, 5, 10), ra=(90, 5, 10), spine=10, ground="all"),
    "drive": dict(z=0.62, ll=(85, 4, 80), rl=(85, 4, 80), la=(38, 12, 45), ra=(38, 12, 45), spine=-8),
    "seat": dict(z=0.58, ll=(88, 6, 88), rl=(88, 6, 88), la=(20, 10, 70), ra=(20, 10, 70), spine=-4),
    "gun_up": dict(ll=(85, 8, 15), rl=(85, 8, 15), spine=5, ra=(175, 8, 5), la=(25, 20, 30), ground="all"),
    "gun_point": dict(ll=(85, 8, 15), rl=(85, 8, 15), spine=8, ra=(88, 2, 5), la=(70, 5, 40), ground="all"),
    "gun_temple": dict(ll=(85, 8, 15), rl=(85, 8, 15), spine=12, ra=(95, 55, 145), la=(25, 20, 30), hroll=-8, ground="all"),
    "pull": dict(spine=-15, la=(80, 5, 30), ra=(70, 5, 40), ll=(25, 5, 30), rl=(-15, 5, 10)),
    "pipe_up": dict(la=(170, 10, 20), ra=(170, 10, 20), spine=-6),
    "pipe_down": dict(la=(60, 5, 10), ra=(60, 5, 10), spine=25),
    "throw_back": dict(ra=(150, 20, 60), la=(50, 10, 20), spine=-10, twist=-20),
    "throw_fwd": dict(ra=(80, 10, 10), la=(20, 10, 20), spine=15, twist=20),
    "phone": dict(ra=(35, 25, 150)),
    "aim": dict(z=0.6, ll=(88, 6, 88), rl=(88, 6, 88), la=(85, -10, 25), ra=(70, 5, 110), spine=12, hpitch=8),
    "point_chin": dict(hpitch=-18, spine=-5),
}

def pose(name, **kw):
    p = dict(BASE); p.update(POSES.get(name, {})); p.update(kw); return p

def lerp_pose(a, b, u):
    out = {}
    for k in BASE:
        va, vb = a.get(k, BASE[k]), b.get(k, BASE[k])
        if isinstance(va, tuple):
            out[k] = tuple(x + (y - x) * u for x, y in zip(va, vb))
        elif isinstance(va, (int, float)) and isinstance(vb, (int, float)):
            if k == "yaw":
                d = (vb - va + 180) % 360 - 180; out[k] = va + d * u
            else:
                out[k] = va + (vb - va) * u
        elif va is None or vb is None:
            out[k] = vb if u >= 0.5 else va
        else:
            out[k] = vb if u >= 0.5 else va
    return out

def ease(u, kind="io"):
    u = max(0.0, min(1.0, u))
    if kind == "io": return u * u * (3 - 2 * u)
    if kind == "in": return u * u
    if kind == "out": return 1 - (1 - u) * (1 - u)
    return u

def gait(kind, phase, w=1.0):
    """Leg and arm angles for a gait at phase (radians)."""
    s, c = math.sin(phase), math.cos(phase)
    s2, c2 = math.sin(phase + math.pi), math.cos(phase + math.pi)
    if kind == "run":
        hp, ko, kk, ar, el, sp = 36, 14, 85, 42, 88, 13
    elif kind == "jog":
        hp, ko, kk, ar, el, sp = 28, 10, 65, 30, 75, 9
    elif kind == "limp":
        hp, ko, kk, ar, el, sp = 16, 6, 30, 10, 20, 8
    else:
        hp, ko, kk, ar, el, sp = 22, 5, 42, 17, 18, 4
    ll = (hp * s * w + 4, 4, ko + kk * max(0.0, c) ** 1.4 * w)
    rl = (hp * s2 * w + 4, 4, ko + kk * max(0.0, c2) ** 1.4 * w)
    if kind == "limp":
        rl = (hp * 0.5 * s2 * w + 4, 6, 4)
    la = (-ar * s * w + 4, 7, el + 10 * max(0, -s))
    ra = (-ar * s2 * w + 4, 7, el + 10 * max(0, -s2))
    return dict(ll=ll, rl=rl, la=la, ra=ra, spine=sp, side=(4 * s if kind == "limp" else 0))

CYCLE = {"walk": 1.45, "jog": 2.2, "run": 2.8, "limp": 1.0}

# ------------------------------------------------------------------ actor timeline
class Actor:
    def __init__(self, name, costume, nf, lod="high"):
        self.name = name; self.c = costume; self.nf = nf; self.lod = lod
        self.style = costume.get("style", "detail")
        self.tracks = []          # (f0, f1, fn(f) -> params dict or ("J", joints), blend_frames)
        self.overlays = []        # (f0, f1, fn(f, params) -> params)
        self.J = None
        self.visible = np.ones(nf, bool)

    # tracks
    def hold(self, t0, t1, p, blend=0.0):
        self.tracks.append((F(t0), F(t1), lambda f, p=p: dict(p), F(blend)))
    def blend(self, t0, t1, a, b, kind="io", blend=0.0):
        f0, f1 = F(t0), F(t1)
        self.tracks.append((f0, f1, lambda f: lerp_pose(a, b, ease((f - f0) / max(1, f1 - f0), kind)), F(blend)))
    def seq(self, keys, kind="io", blend=0.0):
        """keys: [(t, params)] pose-to-pose with easing between keys, holds after the last key."""
        for (ta, a), (tb, b) in zip(keys, keys[1:]):
            self.blend(ta, tb, a, b, kind, blend if ta == keys[0][0] else 0.0)
    def path(self, t0, t1, pts, gaitkind="walk", speed="io", base=None, look=None, blend=0.25, yaw_fixed=None):
        """Move along a polyline from t0 to t1. speed: 'io' eases in and out, 'in' accelerates, 'lin' constant."""
        pts = [np.array(p[:2], float) for p in pts]
        segs = [np.linalg.norm(b - a) for a, b in zip(pts, pts[1:])]; L = sum(segs)
        f0, f1 = F(t0), F(t1); base = base or {}
        def at(sd):
            acc = 0.0
            for (a, b), sl in zip(zip(pts, pts[1:]), segs):
                if sd <= acc + sl or (b is pts[-1]):
                    u = (sd - acc) / sl if sl > 0 else 0.0
                    return a + (b - a) * min(1.0, max(0.0, u)), b - a
                acc += sl
            return pts[-1], pts[-1] - pts[-2]
        def fn(f):
            u = (f - f0) / max(1, f1 - f0)
            sd = L * (ease(u, speed) if speed != "lin" else u)
            pos, d = at(min(sd, L))
            pa, _ = at(min(L, sd + 0.7))
            dd = pa - pos if np.linalg.norm(pa - pos) > 0.05 else d
            yaw = math.degrees(math.atan2(-dd[0], dd[1])) if yaw_fixed is None else yaw_fixed
            # speed now (for gait weight)
            du = 1.0 / max(1, f1 - f0); sd2 = L * (ease(min(1, u + du), speed) if speed != "lin" else min(1, u + du))
            v = (sd2 - sd) * core.FPS
            w = max(0.0, min(1.0, v / 0.9)) if gaitkind in ("walk", "limp") else max(0.0, min(1.0, v / 2.0))
            p = dict(BASE); p.update(base); p.update(gait(gaitkind, 2 * math.pi * sd / CYCLE[gaitkind], w))
            p["x"], p["y"], p["yaw"] = float(pos[0]), float(pos[1]), yaw
            return p
        self.tracks.append((f0, f1, fn, F(blend)))
    def traj(self, t0, X, Y, YAW, SPEED, base=None, blend=0.2, kinds=("walk", "jog", "run")):
        """Follow a simulated trajectory (arrays at the frame rate starting at t0)."""
        f0 = F(t0); n = len(X); base = base or {}
        dist = np.concatenate([[0], np.cumsum(np.hypot(np.diff(X), np.diff(Y)))])
        def fn(f):
            i = min(n - 1, f - f0); v = SPEED[i]
            k = "run" if v > 3.0 else ("jog" if v > 1.9 else "walk")
            w = max(0.0, min(1.0, v / (0.9 if k == "walk" else 2.0)))
            p = dict(BASE); p.update(base); p.update(gait(k, 2 * math.pi * dist[i] / CYCLE[k], w))
            p["x"], p["y"], p["yaw"] = float(X[i]), float(Y[i]), float(YAW[i])
            return p
        self.tracks.append((f0, f0 + n - 1, fn, F(blend)))
    def joints(self, t0, JA, blend=0.0):
        f0 = F(t0); n = len(JA)
        self.tracks.append((f0, f0 + n - 1, lambda f: ("J", JA[min(n - 1, f - f0)]), F(blend)))
    # overlays
    def over(self, t0, t1, **kw):
        """Override parameters between t0 and t1 with a soft in/out (0.25 s)."""
        f0, f1 = F(t0), F(t1); r = F(0.25)
        def fn(f, p):
            w = min(1.0, (f - f0) / max(1, r), (f1 - f) / max(1, r)); w = ease(max(0, w))
            q = dict(p); tmp = dict(p); tmp.update(kw)
            return lerp_pose(q, tmp, w)
        self.overlays.append((f0, f1, fn))
    def look(self, t0, t1, target, strength=1.0):
        f0, f1 = F(t0), F(t1); r = F(0.3)
        tgt = np.array(target, float)
        def fn(f, p):
            w = min(1.0, (f - f0) / max(1, r), (f1 - f) / max(1, r)); w = ease(max(0, w)) * strength
            d = tgt[:2] - np.array((p["x"], p["y"]))
            want = math.degrees(math.atan2(-d[0], d[1]))
            rel = (want - p["yaw"] + 180) % 360 - 180
            hy = max(-80, min(80, rel)); tw = max(-35, min(35, rel - hy)) if abs(rel) > 80 else 0
            dz = (tgt[2] if len(tgt) > 2 else 1.6) - 1.6; dist = max(0.5, np.linalg.norm(d))
            hp = max(-35, min(35, -math.degrees(math.atan2(dz, dist))))
            q = dict(p); q["hyaw"] = p["hyaw"] + (hy - p["hyaw"]) * w; q["twist"] = p["twist"] + tw * w
            q["hpitch"] = p["hpitch"] + (hp - p["hpitch"]) * w
            return q
        self.overlays.append((f0, f1, fn))
    def face(self, t0, t1, eyes=None, mouth=None):
        f0, f1 = F(t0), F(t1)
        def fn(f, p):
            q = dict(p)
            if eyes is not None: q["eyes"] = eyes
            if mouth is not None: q["mouth"] = mouth
            return q
        self.overlays.append((f0, f1, fn))
    def talk(self, t0, t1):
        f0, f1 = F(t0), F(t1)
        self.overlays.append((f0, f1, lambda f, p: dict(p, mouth=0.25 + 0.75 * abs(math.sin(f * 1.9)))))
    def hide(self, t0, t1):
        self.visible[max(0, F(t0)):min(self.nf, F(t1) + 1)] = False

    def compute(self):
        J = np.zeros((self.nf, NJ, 3)); E = np.ones(self.nf); M = np.zeros(self.nf); K = np.zeros(self.nf, bool)
        last = None
        for f in range(self.nf):
            tr = None
            for t in self.tracks:
                if t[0] <= f <= t[1] or (f > t[1] and t is self.tracks[-1] and False):
                    tr = t
            if tr is None:
                # hold the closest earlier track's last frame, or the first track's first frame
                prev = [t for t in self.tracks if t[1] < f]
                tr = max(prev, key=lambda t: t[1]) if prev else min(self.tracks, key=lambda t: t[0])
                fe = tr[1] if prev else tr[0]
            else:
                fe = f
            r = tr[2](fe)
            if isinstance(r, tuple) and r[0] == "J":
                K[f] = True
                j = np.array(r[1]); q = dict(BASE)
                for (o0, o1, fn) in self.overlays:
                    if o0 <= f <= o1:
                        try:
                            q = fn(f, q)
                        except Exception:
                            pass
                e = q.get("eyes", 1.0); m = q.get("mouth", 0.0)
            else:
                p = r
                for (o0, o1, fn) in self.overlays:
                    if o0 <= f <= o1:
                        p = fn(f, p)
                j = fk(p); e = p.get("eyes", 1.0); m = p.get("mouth", 0.0)
            # blend in from the previous state at the start of a track
            if tr[3] > 0 and tr[0] <= f < tr[0] + tr[3] and last is not None and f > 0:
                if not hasattr(self, "_bstart") or self._bstart[0] != id(tr):
                    self._bstart = (id(tr), last.copy())
                u = ease((f - tr[0] + 1) / (tr[3] + 1)); j = self._bstart[1] * (1 - u) + j * u
            J[f] = j; E[f] = e; M[f] = m; last = j
        # nothing goes below the ground: lift each frame by what the meshes would sink (sidewalks are 0.15 high)
        rj = R_J * self.c.get("scale", 1.0); LEGS = ((LKN, LAN, LTO), (RKN, RAN, RTO))
        for f in range(self.nf):
            gz = core.ground_z(J[f, PELVIS, 0], J[f, PELVIS, 1])
            low = float(np.min(J[f, :, 2] - rj))
            if low < gz:
                J[f, :, 2] += gz - low
            # a curb under one joint: a standing figure steps that foot up, a figure low on the ground lies on top of it
            if not core.SIDEWALKS:
                continue
            need = np.array([core.ground_z(x, y) for x, y in J[f, :, :2]]) + rj - J[f, :, 2]
            if need.max() <= 1e-3:
                continue
            if J[f, PELVIS, 2] - gz < 0.55:
                J[f, :, 2] += need.max(); continue
            for (kn, an, to) in LEGS:
                up = max(0.0, need[an], need[to])
                if up > 0:
                    J[f, an, 2] += up; J[f, to, 2] += up; J[f, kn, 2] += up * 0.5
            rest = need.copy(); rest[[LKN, LAN, LTO, RKN, RAN, RTO]] = 0.0
            if rest.max() > 1e-3:
                J[f, :, 2] += rest.max()
        self.J = J; self.E = E; self.M = M; self.K = K
        return J

def F(t):
    return int(round(t * core.FPS))

# how far each joint's mesh reaches below the joint (head, neck, pelvis, arms, legs, nose)
R_J = np.array([0.12, 0.08, 0.14, 0.08, 0.055, 0.05, 0.08, 0.055, 0.05, 0.1, 0.075, 0.05, 0.05, 0.1, 0.075, 0.05, 0.05, 0.03])

# ------------------------------------------------------------------ meshes
COST = {
    "him": dict(style="shape", skin="#C9A085", hair="#5A3A22", shirt="#9DB8D6", sleeve="rolled", pants="#3C3C40", shoes="#6B4A33", scale=1.0),
    "fat": dict(style="shape", skin="#B88A6A", hair="#B88A6A", beard="#2A2420", shirt="#E9E5DA", sleeve="none", pants="#76767A", shoes="#3A3A3A", scale=1.07, wide=1.5, belly=True),
    "friend": dict(style="shape", skin="#B08868", hair="#2A2420", cap="#3A3A3A", shirt="#6E7A4A", sleeve="short", pants="#8A7A5A", shoes="#4A4A4A", scale=0.98),
    "lady": dict(style="shape", skin="#C8A48C", hair="#1E1A18", bun=True, shirt="#2E2E33", sleeve="long", pants="#2E2E33", shoes="#151515", scale=0.95),
    "roger": dict(style="shape", skin="#D2B09A", hair="#3A2E26", shirt="#1C1C1E", sleeve="long", pants="#1C1C1E", shoes="#151515", scale=1.0, headset=True),
    "pilot": dict(style="shape", skin="#C4A08A", hair="#2A2420", shirt="#5A5E64", sleeve="long", pants="#5A5E64", shoes="#151515", scale=1.0, headset=True),
}
CROWD_SHIRTS = ["#8A7A66", "#5E6B70", "#9C8C70", "#6E5A48", "#C9C1B0", "#7A4E3A", "#4E5A48", "#A89A80", "#3E4248", "#B5A58A", "#8C5A44", "#5A4E62"]
CROWD_PANTS = ["#3A3632", "#4A4640", "#5A5248", "#2E2C2A", "#6A6050"]
CROWD_SKIN = ["#B38A6A", "#9C7457", "#C49A7A", "#8A6448", "#A57B5C"]

def crowd_costume(rnd):
    return dict(skin=rnd.choice(CROWD_SKIN), hair=rnd.choice(["#1E1A16", "#2A2420", "#3A2E26", "#5A5450"]), shirt=rnd.choice(CROWD_SHIRTS),
                sleeve=rnd.choice(["short", "long", "rolled"]), pants=rnd.choice(CROWD_PANTS), shoes="#2A2622", scale=rnd.uniform(0.94, 1.06),
                wide=rnd.uniform(0.95, 1.15), cap=(rnd.choice(["#3A3A3A", "#C9C1B0", "#5E6B70"]) if rnd.random() < 0.15 else None))

def _mesh_box(name, sx, sy, z0, z1, taper=1.0):
    me = bpy.data.meshes.new(name)
    v = [(-sx, -sy, z0), (sx, -sy, z0), (sx, sy, z0), (-sx, sy, z0),
         (-sx * taper, -sy, z1), (sx * taper, -sy, z1), (sx * taper, sy, z1), (-sx * taper, sy, z1)]
    me.from_pydata(v, [], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]); me.update()
    return me

def _mesh_cyl(name, r0, r1, L, n=8):
    me = bpy.data.meshes.new(name); v = []; f = []
    for i in range(n):
        a = 2 * math.pi * i / n; v.append((r0 * math.cos(a), r0 * math.sin(a), 0))
    for i in range(n):
        a = 2 * math.pi * i / n; v.append((r1 * math.cos(a), r1 * math.sin(a), L))
    for i in range(n):
        j = (i + 1) % n; f.append((i, j, n + j, n + i))
    f.append(tuple(reversed(range(n)))); f.append(tuple(range(n, 2 * n)))
    me.from_pydata(v, [], f); me.update(); return me

def _mesh_sphere(name, r, sx=1, sy=1, sz=1, seg=10, rings=7):
    import bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    for vv in bm.verts:
        vv.co.x *= sx; vv.co.y *= sy; vv.co.z *= sz
    bm.to_mesh(me); bm.free(); return me

def _obj(name, me, col, parent=None):
    me.materials.append(core.MATS.get(col))
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if parent is not None:
        o.parent = parent
    return o

class Puppet:
    """Mesh parts for an Actor. apply(f) sets every part's world matrix from the actor's joints at frame f."""
    def __init__(self, actor):
        self.a = actor; c = actor.c; s = c.get("scale", 1.0); n = actor.name; wide = c.get("wide", 1.0)
        sk, sh, pa = c["skin"], c["shirt"], c["pants"]
        self.parts = {}
        P = self.parts
        P["torso"] = _obj(n + "_torso", _mesh_box(n + "_torso", 0.15 * s * wide, 0.1 * s * (1.25 if c.get("belly") else 1), 0.0, L_SPINE * s * 0.97, taper=1.3 / (1.15 if c.get("belly") else 1)), sh)
        if c.get("belly"):
            P["belly"] = _obj(n + "_belly", _mesh_sphere(n + "_belly", 0.2 * s, 1.15, 1.0, 1.0), sh)
        P["hips"] = _obj(n + "_hips", _mesh_box(n + "_hips", 0.155 * s * wide, 0.105 * s, -0.13 * s, 0.04 * s), pa)
        P["neck"] = _obj(n + "_neck", _mesh_cyl(n + "_neck", 0.05 * s, 0.05 * s, L_NECK * s * 0.7), sk)
        P["head"] = _obj(n + "_head", _mesh_sphere(n + "_head", 0.105 * s, 0.9, 0.98, 1.12, seg=12, rings=8), sk)
        hd = P["head"]
        sleeve = c.get("sleeve", "long")
        ua_col = sk if sleeve == "none" else sh
        fa_col = sh if sleeve == "long" else sk
        for side in ("l", "r"):
            P[side + "ua"] = _obj(n + side + "ua", _mesh_cyl(n + side + "ua", 0.055 * s * min(1.3, wide), 0.045 * s, L_UA * s), ua_col)
            P[side + "fa"] = _obj(n + side + "fa", _mesh_cyl(n + side + "fa", 0.043 * s, 0.035 * s, L_FA * s), fa_col)
            P[side + "ha"] = _obj(n + side + "ha", _mesh_sphere(n + side + "ha", 0.045 * s, 1, 0.8, 1.2, seg=8, rings=5), sk)
            P[side + "th"] = _obj(n + side + "th", _mesh_cyl(n + side + "th", 0.08 * s * min(1.25, wide), 0.06 * s, L_TH * s), pa)
            P[side + "sh"] = _obj(n + side + "sh", _mesh_cyl(n + side + "sh", 0.055 * s, 0.045 * s, L_SH * s), pa)
            P[side + "ft"] = _obj(n + side + "ft", _mesh_box(n + side + "ft", 0.05 * s, 0.045 * s, -0.04 * s, 0.2 * s), c.get("shoes", "#2A2622"))
        self.face = {}
        if actor.lod == "high":
            # face, parented to the head; head local axes: z up the head, y toward the nose
            hairc = c.get("hair", "#2A2420")
            self.face["hair"] = _obj(n + "_hair", _mesh_sphere(n + "_hair", 0.108 * s, 0.93, 1.0, 0.8, seg=12, rings=6), hairc, hd)
            self.face["hair"].location = (0, -0.018 * s, 0.035 * s)
            for side, x in (("l", -0.035), ("r", 0.035)):
                e = _obj(n + side + "eye", _mesh_sphere(n + side + "eye", 0.016 * s, 1.2, 0.6, 1.0, seg=8, rings=5), "#1A1512", hd)
                e.location = (x * s, 0.094 * s, 0.022 * s); self.face[side + "eye"] = e
                b = _obj(n + side + "brow", _mesh_box(n + side + "brow", 0.022 * s, 0.006 * s, -0.004 * s, 0.004 * s), hairc if hairc != sk else "#3A2E26", hd)
                b.location = (x * s, 0.1 * s, 0.05 * s); self.face[side + "brow"] = b
                ear = _obj(n + side + "ear", _mesh_sphere(n + side + "ear", 0.025 * s, 0.5, 0.8, 1.2, seg=6, rings=4), sk, hd)
                ear.location = (x / 0.035 * 0.092 * s, 0.0, 0.0)
            nose = _obj(n + "_nose", _mesh_box(n + "_nose", 0.012 * s, 0.02 * s, -0.025 * s, 0.01 * s), sk, hd)
            nose.location = (0, 0.105 * s, 0.0); self.face["nose"] = nose
            mo = _obj(n + "_mouth", _mesh_box(n + "_mouth", 0.03 * s, 0.008 * s, -0.007 * s, 0.007 * s), "#4A1E18", hd)
            mo.location = (0, 0.097 * s, -0.042 * s); self.face["mouth"] = mo
            if c.get("beard"):
                bd = _obj(n + "_beard", _mesh_sphere(n + "_beard", 0.075 * s, 1.0, 0.7, 0.6, seg=8, rings=5), c["beard"], hd)
                bd.location = (0, 0.05 * s, -0.06 * s)
            if c.get("bun"):
                bn = _obj(n + "_bun", _mesh_sphere(n + "_bun", 0.045 * s, seg=8, rings=5), hairc, hd); bn.location = (0, -0.1 * s, 0.02 * s)
            if c.get("cap"):
                cp = _obj(n + "_cap", _mesh_sphere(n + "_cap", 0.112 * s, 0.95, 1.0, 0.6, seg=10, rings=5), c["cap"], hd); cp.location = (0, -0.01 * s, 0.05 * s)
            if c.get("headset"):
                hs = _obj(n + "_headset", _mesh_box(n + "_headset", 0.11 * s, 0.015 * s, 0.0, 0.03 * s), "#1A1A1A", hd); hs.location = (0, 0, 0.1 * s)
        elif c.get("cap"):
            cp = _obj(n + "_cap", _mesh_sphere(n + "_cap", 0.112 * s, 0.95, 1.0, 0.6, seg=8, rings=4), c["cap"], hd); cp.location = (0, -0.01 * s, 0.05 * s)
        else:
            hr = _obj(n + "_hair", _mesh_sphere(n + "_hair", 0.108 * s, 0.93, 1.0, 0.8, seg=8, rings=4), c.get("hair", "#2A2420"), hd)
            hr.location = (0, -0.018 * s, 0.035 * s)
        P["blob"] = _obj(n + "_blob", _mesh_cyl(n + "_blob", 0.32 * s, 0.32 * s, 0.01, n=12), "#3E3226")
        self.s = s
        known = set(o.name for o in list(P.values()) + list(self.face.values()))
        self.acc = [o for o in hd.children_recursive if o.name not in known]

    @staticmethod
    def frame(z, xref):
        z = z / (np.linalg.norm(z) + 1e-9)
        x = xref - z * np.dot(xref, z)
        if np.linalg.norm(x) < 1e-6:
            x = np.cross(z, (0, 0, 1)) if abs(z[2]) < 0.9 else np.cross(z, (1, 0, 0))
        x = x / (np.linalg.norm(x) + 1e-9); y = np.cross(z, x)
        return np.stack([x, y, z], axis=1)

    @staticmethod
    def M(R, t):
        m = Matrix.Identity(4)
        for i in range(3):
            for k in range(3):
                m[i][k] = float(R[i, k])
            m[i][3] = float(t[i])
        return m

    def apply(self, f):
        a = self.a; P = self.parts
        vis = bool(a.visible[min(f, a.nf - 1)])
        for o in list(P.values()) + list(self.face.values()) + self.acc:
            o.hide_render = not vis
        if not vis:
            return
        J = a.J[min(f, a.nf - 1)]
        xr = J[RSH] - J[LSH]
        Rt = self.frame(J[NECK] - J[PELVIS], xr)
        P["torso"].matrix_world = self.M(Rt, J[PELVIS])
        if "belly" in P:
            P["belly"].matrix_world = self.M(Rt, J[PELVIS] + Rt @ np.array((0, 0.09 * self.s, 0.22 * self.s)))
        Rp = self.frame(J[NECK] - J[PELVIS], J[RHIP] - J[LHIP])
        P["hips"].matrix_world = self.M(Rp, J[PELVIS])
        P["neck"].matrix_world = self.M(self.frame(J[HEAD] - J[NECK], xr), J[NECK])
        # head: z from neck to head, y toward the nose
        z = J[HEAD] - J[NECK]; fwd = J[NOSE] - J[HEAD]
        Rz_ = self.frame(z, np.cross(fwd, z))
        P["head"].matrix_world = self.M(Rz_, J[HEAD])
        def limb(name, A, B):
            P[name].matrix_world = self.M(self.frame(J[B] - J[A], xr), J[A])
        limb("lua", LSH, LEL); limb("lfa", LEL, LHA); limb("rua", RSH, REL); limb("rfa", REL, RHA)
        limb("lth", LHIP, LKN); limb("lsh", LKN, LAN); limb("rth", RHIP, RKN); limb("rsh", RKN, RAN)
        for side, (el, ha) in (("l", (LEL, LHA)), ("r", (REL, RHA))):
            d = J[ha] - J[el]; P[side + "ha"].matrix_world = self.M(self.frame(d, xr), J[ha] + d / (np.linalg.norm(d) + 1e-9) * 0.04)
        for side, (an, to) in (("l", (LAN, LTO)), ("r", (RAN, RTO))):
            P[side + "ft"].matrix_world = self.M(self.frame(J[to] - J[an], xr), J[an] + np.array((0, 0, -0.02)))
        lowest = min(J[:, 2].min(), 2.0)
        P["blob"].matrix_world = self.M(np.eye(3), np.array((J[PELVIS, 0], J[PELVIS, 1], 0.17 if lowest > 0.12 else 0.004)))
        P["blob"].hide_render = bool(J[PELVIS, 2] > 3.0)
        if self.face:
            e = float(a.E[min(f, a.nf - 1)]); m = float(a.M[min(f, a.nf - 1)])
            for side in ("l", "r"):
                self.face[side + "eye"].scale = (1, 1, max(0.08, e))
            self.face["mouth"].scale = (1, 1, 1 + 4 * m)

class Stick:
    """A rope or rod between two moving points: fn(f) -> (A, B)."""
    def __init__(self, name, r, col, fn):
        self.fn = fn; self.o = _obj(name, _mesh_cyl(name, r, r, 1.0, n=6), col)
    def apply(self, f):
        A, B = self.fn(f)
        if A is None:
            self.o.hide_render = True; return
        self.o.hide_render = False
        A = np.array(A, float); B = np.array(B, float); d = B - A; L = np.linalg.norm(d)
        R = Puppet.frame(d, np.array((1.0, 0, 0)))
        m = Puppet.M(R, A); m = m @ Matrix.Diagonal((1, 1, max(L, 1e-3), 1))
        self.o.matrix_world = m


class ShapePuppet:
    """A plain moving shape for acting characters: body cylinder with flat shoulders, neck, head ball, one legs pill.
    No arms. A facing wedge on the head; eye and mouth slits instead when the head is big in frame (close shots)."""
    def __init__(self, actor):
        a = actor; c = a.c; s = c.get("scale", 1.0); n = a.name + "_shape"; wide = min(1.4, c.get("wide", 1.0))
        self.a = a; self.s = s
        self.rt = 0.17 * s * wide; self.rl = 0.13 * s * wide; self.rh = 0.112 * s
        self.torso = _obj(n + "_torso", _mesh_cyl(n + "_torso", self.rt, self.rt, 1.0, n=14), c["shirt"])
        self.top = _obj(n + "_top", _mesh_sphere(n + "_top", self.rt, 1, 1, 0.5, seg=14, rings=7), c["shirt"])
        self.bot = _obj(n + "_bot", _mesh_sphere(n + "_bot", self.rt, seg=14, rings=7), c["shirt"])
        self.legs = _obj(n + "_legs", _mesh_cyl(n + "_legs", self.rl, self.rl * 0.85, 1.0, n=12), c["pants"])
        self.foot = _obj(n + "_foot", _mesh_sphere(n + "_foot", self.rl * 0.85, seg=12, rings=6), c["pants"])
        self.neck = _obj(n + "_neck", _mesh_cyl(n + "_neck", 0.062 * s, 0.062 * s, 1.0, n=10), c["skin"])
        self.head = _obj(n + "_head", _mesh_sphere(n + "_head", self.rh, seg=16, rings=10), c["skin"])
        self.wedge = _obj(n + "_wedge", _mesh_box(n + "_wedge", 0.03 * s, 0.03 * s, 0.0, 0.1 * s), c.get("hair", "#2A2420"))
        self.eyes = [_obj(n + f"_eye{k}", _mesh_box(n + f"_eye{k}", 0.017 * s, 0.009 * s, -0.009 * s, 0.009 * s), "#161616", self.head) for k in (0, 1)]
        for o, x in zip(self.eyes, (-0.042, 0.042)):
            o.location = (x * s, 0.099 * s, 0.022 * s)
        self.mouth = _obj(n + "_mouth", _mesh_box(n + "_mouth", 0.03 * s, 0.009 * s, -0.005 * s, 0.005 * s), "#3A1A16", self.head)
        self.mouth.location = (0, 0.099 * s, -0.046 * s)
        self.face = self.eyes + [self.mouth]
        self.blob = _obj(n + "_blob", _mesh_cyl(n + "_blob", 0.32 * s, 0.32 * s, 0.01, n=12), "#3E3226")
        self.parts = [self.torso, self.top, self.bot, self.legs, self.foot, self.neck, self.head, self.wedge, self.blob]
    def show(self, on):
        for o in self.parts + self.face:
            o.hide_render = not on
    def apply(self, f, cam=None):
        ff = min(f, self.a.nf - 1); J = self.a.J[ff]; s = self.s
        up = J[NECK] - J[PELVIS]; u = up / (np.linalg.norm(up) + 1e-9)
        pel = J[PELVIS] + u * 0.02; top = J[NECK] - u * 0.065 * s
        feet = (J[LAN] + J[RAN]) / 2 + np.array((0, 0, 0.1 * s)); hipc = (J[LHIP] + J[RHIP]) / 2; head = J[HEAD].copy()
        # nothing of the shape sinks into the ground or a sidewalk
        gz = core.ground_z(J[PELVIS, 0], J[PELVIS, 1])
        low = min(pel[2] - self.rt, top[2] - self.rt, hipc[2] - self.rl, feet[2] - self.rl * 0.85, head[2] - self.rh)
        lift = np.array((0.0, 0.0, max(0.0, gz + 0.005 - low)))
        pel = pel + lift; top = top + lift; feet = feet + lift; hipc = hipc + lift; head = head + lift
        xr = J[RSH] - J[LSH]
        def seg(o, A, B):
            d = B - A; L = np.linalg.norm(d) + 1e-6
            o.matrix_world = Puppet.M(Puppet.frame(d, xr), A) @ Matrix.Diagonal((1, 1, L, 1))
        seg(self.torso, pel, top); seg(self.legs, hipc, feet); seg(self.neck, top, head)
        self.bot.matrix_world = Puppet.M(np.eye(3), pel)
        self.top.matrix_world = Puppet.M(Puppet.frame(top - pel, xr), top)
        self.foot.matrix_world = Puppet.M(np.eye(3), feet)
        z = J[HEAD] - J[NECK]; fwd = J[NOSE] - J[HEAD]
        self.head.matrix_world = Puppet.M(Puppet.frame(z, np.cross(fwd, z)), head)
        fw = fwd / (np.linalg.norm(fwd) + 1e-9)
        slits = False
        if cam is not None and os.environ.get("SHAPE_SLITS", "1") != "0":     # SHAPE_SLITS=0: no faces at all (Seedance references)
            dist = float(np.linalg.norm(np.array(cam[0], float) - head))
            slits = 2 * self.rh / max(1e-3, dist * 36.0 / cam[1] * 480 / 1120) > 0.3
        self.wedge.hide_render = slits
        for o in self.face:
            o.hide_render = not slits
        if slits:
            for o in self.eyes:
                o.scale = (1, 1, max(0.08, float(self.a.E[ff])))
            self.mouth.scale = (1, 1, 0.3 + 3.0 * float(self.a.M[ff]))
        else:
            self.wedge.matrix_world = Puppet.M(Puppet.frame(fw, xr), head + fw * 0.075 * s)
        self.blob.matrix_world = Puppet.M(np.eye(3), np.array((J[PELVIS, 0], J[PELVIS, 1], gz + 0.004)))
        self.blob.hide_render = bool(J[PELVIS, 2] > gz + 3.0)

class MixedPuppet:
    """Detailed figure while physics drives the body (ragdoll frames), plain shape while the character acts."""
    def __init__(self, actor):
        self.a = actor; self.d = Puppet(actor); self.sh = ShapePuppet(actor)
    def apply(self, f, cam=None):
        a = self.a; ff = min(f, a.nf - 1)
        vis = bool(a.visible[ff])
        if a.K[ff] or not vis:
            self.sh.show(False); self.d.apply(f)
        else:
            self.d.apply(f)
            for o in list(self.d.parts.values()) + list(self.d.face.values()) + self.d.acc:
                o.hide_render = True
            self.sh.show(True); self.sh.apply(f, cam)
