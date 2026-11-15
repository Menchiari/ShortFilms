"""Crowd simulation (social forces with personal space) and a verlet ragdoll."""
import math
import numpy as np
import core
from puppet import *

# ------------------------------------------------------------------ crowd
class Crowd:
    """Agents in 2D. brain(t, P, V) -> (desired velocity (n,2), look points (n,2)).
    Personal space grows with distance from `focus`: the further back, the harder it is to be close."""
    def __init__(self, P0, v0, radius=0.26, seed=0, focus=None, space_k=0.02, walls=(), bubble=None):
        self.P = np.array(P0, float); self.n = len(self.P); self.V = np.zeros_like(self.P)
        self.v0 = np.array(v0, float) if np.ndim(v0) else np.full(self.n, v0)
        self.r = np.full(self.n, radius); self.rnd = np.random.default_rng(seed)
        self.focus = focus; self.space_k = space_k; self.walls = list(walls); self.bubble = bubble
        self.yaw = np.zeros(self.n)

    def forces(self, t, P, V, Vd):
        n = self.n; Fz = (Vd - V) / 0.45
        D = P[:, None, :] - P[None, :, :]; d = np.linalg.norm(D, axis=2) + np.eye(n) * 1e6
        Nrm = D / d[..., None]
        extra = 0.0
        if self.focus is not None:
            fc = self.focus(t) if callable(self.focus) else self.focus
            df = np.linalg.norm(P - np.array(fc)[None, :2], axis=1)
            extra = np.minimum(0.55, self.space_k * df)
            rij = self.r[:, None] + self.r[None, :] + 0.5 * (extra[:, None] + extra[None, :])
        else:
            rij = self.r[:, None] + self.r[None, :] + 0.12
        rep = 2.4 * np.exp((rij - d) / 0.3)
        rep[d > 4.0] = 0.0
        contact = np.where(d < rij, 70.0 * (rij - d), 0.0)
        Fz += ((rep + contact)[..., None] * Nrm).sum(axis=1)
        for (x0, x1, y0, y1) in self.walls:
            cx = np.clip(P[:, 0], x0, x1); cy = np.clip(P[:, 1], y0, y1)
            dv = P - np.stack([cx, cy], 1); dd = np.linalg.norm(dv, axis=1)
            inside = (P[:, 0] > x0) & (P[:, 0] < x1) & (P[:, 1] > y0) & (P[:, 1] < y1)
            nn = np.where(dd[:, None] > 1e-6, dv / np.maximum(dd, 1e-6)[:, None], 0)
            Fz += (5.0 * np.exp((0.35 - dd) / 0.2))[:, None] * nn * (dd < 2.0)[:, None]
            if inside.any():
                mid = np.array(((x0 + x1) / 2, (y0 + y1) / 2))
                Fz[inside] += (P[inside] - mid) * 40
        if self.bubble is not None:
            c, R = self.bubble(t)
            if R > 0:
                dv = P - np.array(c)[None, :2]; dd = np.linalg.norm(dv, axis=1) + 1e-6
                Fz += (4.0 * np.exp((R - dd) / 0.35))[:, None] * dv / dd[:, None] * (dd < R + 2.5)[:, None]
        return Fz

    def run(self, T, brain, dt=1 / 48):
        steps = int(round(T / dt)); every = int(round(1 / (core.FPS * dt)))
        X, Y, YW, SP = [], [], [], []
        yaw = self.yaw.copy(); turn = math.radians(220) * dt
        for k in range(steps + 1):
            t = k * dt
            Vd, look = brain(t, self.P, self.V)
            Fz = self.forces(t, self.P, self.V, Vd)
            self.V += Fz * dt
            sp = np.linalg.norm(self.V, axis=1); vmax = self.v0 * 1.35 + 0.2
            over = sp > vmax; self.V[over] *= (vmax[over] / sp[over])[:, None]
            self.P += self.V * dt
            sp = np.linalg.norm(self.V, axis=1)
            want = np.where(sp > 0.35, np.degrees(np.arctan2(-self.V[:, 0], self.V[:, 1])),
                            np.degrees(np.arctan2(-(look[:, 0] - self.P[:, 0]), look[:, 1] - self.P[:, 1])))
            dlt = (want - yaw + 180) % 360 - 180
            yaw += np.clip(dlt, -math.degrees(turn), math.degrees(turn))
            if k % every == 0:
                X.append(self.P[:, 0].copy()); Y.append(self.P[:, 1].copy()); YW.append(yaw.copy()); SP.append(sp.copy())
        return np.array(X), np.array(Y), np.array(YW), np.array(SP)

def ring_targets(center, radius, n, a0=0, a1=360, jitter=0.0, seed=0):
    rng = np.random.default_rng(seed)
    a = np.radians(np.linspace(a0, a1, n, endpoint=(a1 - a0) % 360 != 0)) + rng.uniform(-jitter, jitter, n)
    rr = radius + rng.uniform(-0.3, 0.6, n)
    return np.stack([center[0] + rr * np.cos(a), center[1] + rr * np.sin(a)], 1)

def seek(P, T, speed, arrive=1.5):
    d = T - P; dist = np.linalg.norm(d, axis=1) + 1e-6
    s = speed * np.minimum(1.0, dist / arrive)
    return d / dist[:, None] * s[:, None]

def crowd_actors(prefix, sim_out, t0=0.0, nf=0, rnd=None, lod="low", costumes=None):
    X, Y, YW, SP = sim_out; acts = []
    for i in range(X.shape[1]):
        cst = costumes[i] if costumes else crowd_costume(rnd)
        a = Actor(f"{prefix}{i:02d}", cst, nf, lod=lod)
        a.traj(t0, X[:, i], Y[:, i], YW[:, i], SP[:, i], blend=0.0)
        acts.append(a)
    return acts

# ------------------------------------------------------------------ ragdoll
BONES = [(HEAD, NECK), (NECK, PELVIS), (NECK, LSH), (NECK, RSH), (LSH, RSH), (LSH, LEL), (LEL, LHA), (RSH, REL), (REL, RHA),
         (PELVIS, LHIP), (PELVIS, RHIP), (LHIP, RHIP), (LHIP, LKN), (LKN, LAN), (LAN, LTO), (RHIP, RKN), (RKN, RAN), (RAN, RTO),
         (HEAD, NOSE), (NECK, NOSE), (LSH, LHIP), (RSH, RHIP), (LSH, RHIP), (RSH, LHIP), (LSH, PELVIS), (RSH, PELVIS),
         (NECK, LHIP), (NECK, RHIP), (LKN, LTO), (RKN, RTO)]
SOFT = [(HEAD, LSH), (HEAD, RSH), (NOSE, LSH), (NOSE, RSH), (NOSE, PELVIS)]
MINS = [(LHIP, LAN, 0.38), (RHIP, RAN, 0.38), (LSH, LHA, 0.2), (RSH, RHA, 0.2), (HEAD, PELVIS, 0.62), (LKN, RKN, 0.12), (LHA, RHA, 0.1)]
RAD = np.array([0.1, 0.06, 0.12, 0.06, 0.05, 0.05, 0.06, 0.05, 0.05, 0.08, 0.06, 0.05, 0.04, 0.08, 0.06, 0.05, 0.04, 0.05])

class Ragdoll:
    def __init__(self, J0, V0=None, dt=1 / 240):
        self.x = np.array(J0, float); self.dt = dt
        self.xp = self.x - (np.zeros_like(self.x) if V0 is None else np.array(V0, float) * dt)
        self.rest = [(i, j, np.linalg.norm(self.x[i] - self.x[j])) for i, j in BONES]
        self.soft = [(i, j, np.linalg.norm(self.x[i] - self.x[j])) for i, j in SOFT]
        self.pins = {}; self.muscles = []; self.t = 0.0; self.ground = True; self.walls = []

    def step(self):
        dt = self.dt; acc = np.zeros_like(self.x); acc[:, 2] -= 9.81
        for m in self.muscles:
            acc += m(self.t, self.x)
        v = (self.x - self.xp) * 0.996
        nx = self.x + v + acc * dt * dt
        self.xp = self.x; self.x = nx
        for _ in range(10):
            for i, j, L in self.rest:
                d = self.x[j] - self.x[i]; dl = np.linalg.norm(d) + 1e-9; c = (dl - L) / dl * 0.5
                self.x[i] += d * c; self.x[j] -= d * c
            for i, j, L in self.soft:
                d = self.x[j] - self.x[i]; dl = np.linalg.norm(d) + 1e-9; c = (dl - L) / dl * 0.2
                self.x[i] += d * c; self.x[j] -= d * c
            for i, j, L in MINS:
                d = self.x[j] - self.x[i]; dl = np.linalg.norm(d) + 1e-9
                if dl < L:
                    c = (dl - L) / dl * 0.5; self.x[i] += d * c; self.x[j] -= d * c
            for k, fn in self.pins.items():
                p = fn(self.t)
                if p is not None:
                    self.x[k] = p
            if self.ground:
                low = self.x[:, 2] < RAD
                if low.any():
                    self.x[low, 2] = RAD[low]
                    self.xp[low, 0] = self.xp[low, 0] * 0.7 + self.x[low, 0] * 0.3
                    self.xp[low, 1] = self.xp[low, 1] * 0.7 + self.x[low, 1] * 0.3
            for (x0, x1, y0, y1, z1) in self.walls:
                inside = (self.x[:, 0] > x0) & (self.x[:, 0] < x1) & (self.x[:, 1] > y0) & (self.x[:, 1] < y1) & (self.x[:, 2] < z1)
                if inside.any():
                    self.x[inside, 2] = np.maximum(self.x[inside, 2], z1)
        self.t += dt

    def run(self, T):
        out = []; every = int(round(1 / (core.FPS * self.dt))); steps = int(round(T / self.dt))
        for k in range(steps + 1):
            if k % every == 0:
                out.append(self.x.copy())
            self.step()
        return np.array(out)

def toward(idx, target_fn, k):
    """Muscle: accelerate joints idx toward target_fn(t, x) with gain k (m/s^2 per m)."""
    def m(t, x):
        a = np.zeros_like(x); T = target_fn(t, x)
        if T is None:
            return a
        for i in idx:
            a[i] += (np.array(T) - x[i]) * k
        return a
    return m

def pulses(idx, t0, t1, period, mag, seed=0):
    """Muscle: random flailing bursts on joints idx between t0 and t1."""
    rng = np.random.default_rng(seed); n = int((t1 - t0) / period) + 2
    dirs = rng.normal(size=(n, len(idx), 3)); dirs[..., 2] = np.abs(dirs[..., 2]) * 0.6
    def m(t, x):
        a = np.zeros_like(x)
        if t0 <= t <= t1:
            k = int((t - t0) / period); ph = ((t - t0) % period) / period
            w = math.sin(math.pi * ph)
            for n_, i in enumerate(idx):
                a[i] += dirs[k, n_] * mag * w
        return a
    return m

def impulse(idx, t_hit, dv, dur=0.06):
    def m(t, x):
        a = np.zeros_like(x)
        if t_hit <= t < t_hit + dur:
            for i in idx:
                a[i] += np.array(dv) / dur
        return a
    return m
