from sh import *
from shots_s05 import SQ_WALLS, FALL, gather_sim, people

CUES = {}
FACE = 90.0                     # he faces west, toward the crowd
D = np.array((-1.0, 0.0))       # toward the crowd

def sq(eye, sky="warm"):
    reset(sky); return sets.square(eye)

def sitter(nf, pose_name="gun_up", **kw):
    a = Actor("him", COST["him"], nf); a.hold(0, nf / core.FPS, pose(pose_name, x=FALL[0], y=FALL[1], yaw=FACE, **kw)); return a

def gun_on(a):
    g = PR.hand_prop("gun", "gun"); return PR.attach(g, a, offset=(0, 0.02, 0))

def line_crowd(n, r0, r1, T, seed, spread=7.0, speed=None, start=0.0, falls=()):
    """People in the street west of him at distance r0, moving to r1 (meters from him)."""
    rng = np.random.default_rng(seed)
    P0 = np.stack([FALL[0] - rng.uniform(r0 - 3, r0 + 3, n), FALL[1] + 1.5 + rng.uniform(-spread, spread, n) * 0.5], 1)
    P0[:, 1] = np.clip(P0[:, 1], -9.5, 9.5)
    T_ = np.stack([FALL[0] - (r1 + (np.abs(P0[:, 0] - FALL[0]) - r0) * 0.6), P0[:, 1] * 0.8 + FALL[1] * 0.2], 1)
    v = np.full(n, abs(r0 - r1) / max(0.5, T - start)) if speed is None else np.full(n, speed)
    cr = Crowd(P0, v, walls=SQ_WALLS, space_k=0.0, seed=seed)
    look = np.repeat(np.array(FALL)[None], n, 0)
    def brain(t, P, V):
        Vd = seek(P, T_, cr.v0, 1.0)
        if t < start: Vd[:] = 0
        return Vd, look
    sim = cr.run(T, brain)
    return sim

def collapse_actor(a, t, sim_i, sim):
    """Replace a crowd actor's motion with a ragdoll collapse at time t."""
    X, Y, YW, SP = sim; f = F(t)
    p = dict(BASE); p.update(gait("run", 1.0, 1.0)); p.update(x=float(X[f, sim_i]), y=float(Y[f, sim_i]), yaw=float(YW[f, sim_i]))
    J0 = fk(p); fwd = np.array((-math.sin(math.radians(p["yaw"])), math.cos(math.radians(p["yaw"]))))
    V0 = np.zeros_like(J0); V0[:, 0] = fwd[0] * 3.5; V0[:, 1] = fwd[1] * 3.5
    V0[HEAD] -= (fwd[0] * 2.0, fwd[1] * 2.0, 0)
    rd = Ragdoll(J0, V0); JA = rd.run(a.nf / core.FPS - t + 0.1)
    a.joints(t, JA)

def S06_SH010(nf):
    p = (-43.6, -6.9, 1.8); sq(p)
    him = Actor("him", COST["him"], nf)
    base = dict(x=FALL[0], y=FALL[1], yaw=FACE)
    him.seq([(0, pose("gun_up", **base)), (2.6, pose("gun_up", **base)), (3.2, pose("gun_point", **base, ra=(80, 5, 5)))])
    him.talk(0.6, 2.2); him.talk(3.3, 5.6); him.face(0, 6, eyes=1.4)
    rng = np.random.default_rng(31)
    P0 = np.concatenate([slots(FALL, 8, r0=1.5, dr=0.8, arc=(95, 138), seed=31), slots(FALL, 8, r0=1.5, dr=0.8, arc=(178, 290), seed=32)])
    cr = Crowd(P0, rng.uniform(1.2, 1.8, len(P0)), walls=SQ_WALLS, space_k=0.0, seed=33)
    T_ = np.array(FALL)[None] + (P0 - np.array(FALL)[None]) / np.linalg.norm(P0 - np.array(FALL)[None], axis=1)[:, None] * rng.uniform(7, 10, len(P0))[:, None]
    look = np.repeat(np.array(FALL)[None], len(P0), 0)
    def brain(t, P, V):
        Vd = seek(P, T_, cr.v0, 1.0)
        if t < 3.1: Vd[:] = 0
        return Vd, look
    acts = people("c", cr.run(nf / core.FPS, brain), nf, 34)
    return {"cam": cam(p, (FALL[0], FALL[1], 0.75), 32, hh=0.6), "actors": [him] + acts, "speakers": {"OLD MAN": him},
            "say": [[0.6, 2.2, "OLD MAN"], [3.3, 5.6, "OLD MAN"]], "callbacks": [gun_on(him)], "cues": [[0, 1.5, "EARS RINGING, SMOKE FROM THE MUZZLE"]]}

def S06_SH020(nf):
    p0 = (-38.0, -6.8, 1.45); sq(p0)
    him = sitter(nf, "gun_point", ra=(80, 5, 5))
    back = line_crowd(24, 38, 44, 5.0, 41, spread=12)
    tough = line_crowd(6, 37, 33, 5.0, 42, spread=5, start=0.5)
    acts = people("b", back, nf, 43) + people("t", tough, nf, 44)
    return {"cam": move([(0, p0, (-75, -6.5, 1.3), 35), (5, (-38.4, -6.9, 1.45), (-75, -6.5, 1.3), 40)], ease="io"), "actors": [him] + acts, "callbacks": [gun_on(him)]}

def S06_SH030(nf):
    mid = (FALL[0] - 21, FALL[1] + 5.5); sq((mid[0], mid[1], 30))
    him = sitter(nf, "gun_point", ra=(80, 5, 5))
    rng = np.random.default_rng(51); n = 28
    P0 = np.stack([FALL[0] - np.concatenate([rng.uniform(32, 35, 6), rng.uniform(38, 46, n - 6)]), FALL[1] + 1.5 + rng.uniform(-6, 6, n)], 1)
    P0[:, 1] = np.clip(P0[:, 1], -9.5, 9.5)
    cr = Crowd(P0, np.full(n, 1.0), walls=SQ_WALLS, space_k=0.0, seed=52)
    look = np.repeat(np.array(FALL)[None], n, 0)
    def brain(t, P, V):
        T_ = np.stack([np.full(n, FALL[0] - 3.0), P[:, 1] * 0.7 + FALL[1] * 0.3], 1)
        sp = np.where(np.arange(n) < 6, 0.9, 0.0) if t < 2.5 else np.full(n, 5.2)
        cr.v0[:] = np.maximum(sp, 0.01)
        Vd = seek(P, T_, sp, 1.0)
        return Vd, look
    sim = cr.run(nf / core.FPS, brain)
    acts = people("c", sim, nf, 53)
    collapse_actor(acts[0], 1.0, 0, sim); collapse_actor(acts[1], 2.0, 1, sim)
    return {"cam": {"keys": [(0, (mid[0], mid[1], 30.0), (mid[0], mid[1], 0.0), 22)], "euler": (0, 0, 180)},
            "actors": [him] + acts, "callbacks": [gun_on(him)], "cues": [[1.0, 1.3, "SHOT 2"], [2.0, 2.3, "SHOT 3"], [2.6, 4, "THE REST SPRINT"]]}

def behind(nf, r0, r1, shots):
    p = (FALL[0] + 1.1, FALL[1] + 0.35, 1.1); sq(p)
    him = sitter(nf, "gun_point", ra=(82, 4, 4))
    T = nf / core.FPS
    run = line_crowd(26, r0, r1, T, 61 + int(r0), spread=12, speed=abs(r0 - r1) / T)
    cues = [[t, t + 0.3, f"SHOT {n}"] for n, t in shots]
    return {"cam": cam(p, (FALL[0] - 25, FALL[1] - 1.6, 0.9), 70, hh=0.5), "actors": [him] + people("r", run, nf, 62), "callbacks": [gun_on(him)], "cues": cues}

def S06_SH040(nf): return behind(nf, 28, 22, [(4, 1.0), (5, 2.2)])
def S06_SH060(nf): return behind(nf, 21, 19, [(6, 0.2)])
def S06_SH080(nf): return behind(nf, 18, 16.5, [(7, 0.2)])

def lips(nf, word_t):
    him = Actor("him", COST["him"], nf)
    him.hold(0, nf / core.FPS, pose("gun_point", x=FALL[0], y=FALL[1], yaw=FACE, ra=(82, 4, 4)))
    him.compute()
    h = him.J[0, HEAD]; fwd = np.array((-1.0, 0.0, 0.0))
    p = tuple(h + fwd * 0.95 + np.array((0, 0.28, -0.08)))
    sq(p)
    him2 = Actor("him", COST["him"], nf); him2.hold(0, nf / core.FPS, pose("gun_point", x=FALL[0], y=FALL[1], yaw=FACE, ra=(82, 4, 4)))
    for (a, b) in word_t: him2.talk(a, b)
    return {"cam": cam(p, tuple(h + fwd * 0.1 + np.array((0, 0, -0.05))), 75, hh=0.15), "actors": [him2], "speakers": {"OLD MAN": him2}}

def S06_SH050(nf): d = lips(nf, [(0.1, 0.8)]); d["say"] = [[0.05, 0.95, "OLD MAN"]]; return d
def S06_SH070(nf): d = lips(nf, [(0.1, 0.8)]); d["say"] = [[0.05, 0.95, "OLD MAN"]]; return d
def S06_SH090(nf): d = lips(nf, [(0.1, 0.8)]); d["say"] = [[0.05, 0.95, "OLD MAN"]]; return d
def S06_SH100(nf):
    d = lips(nf, [(0.6, 1.4)]); d["say"] = [[0.5, 1.9, "OLD MAN"]]; d["cues"] = [[0, 0.3, "SHOT 8"]]; return d

def S06_SH110(nf):
    p0 = (FALL[0] + 0.75, FALL[1] + 0.15, 1.0); sq(p0)
    him = Actor("him", COST["him"], nf)
    base = dict(x=FALL[0], y=FALL[1], yaw=FACE)
    him.seq([(0, pose("gun_point", **base, ra=(82, 4, 4))), (0.8, pose("sit_ground", **base, ra=(30, 15, 40), hpitch=8)), (4.1, pose("sit_ground", **base, ra=(30, 15, 40), hpitch=8)),
             (4.9, pose("gun_temple", **base))])
    T = nf / core.FPS
    rng = np.random.default_rng(71)
    P0 = np.stack([FALL[0] - rng.uniform(22, 26, 26), FALL[1] + rng.uniform(-5, 6, 26)], 1)
    cr = Crowd(P0, np.full(26, 1.0), walls=SQ_WALLS, space_k=0.0, seed=72)
    look = np.repeat(np.array(FALL)[None], 26, 0)
    def brain(t, P, V):
        sp = 3.0 * max(0.15, 1 - t / 2.5)
        T_ = np.stack([np.full(26, FALL[0] - 19.5), P[:, 1]], 1); cr.v0[:] = sp
        return seek(P, T_, cr.v0, 1.0), look
    acts = people("c", cr.run(T, brain), nf, 73)
    g = PR.hand_prop("gun", "gun")
    return {"cam": move([(0, p0, (FALL[0] - 22, FALL[1] - 0.75, 0.95), 60), (5, (FALL[0] + 0.6, FALL[1] + 0.12, 1.0), (FALL[0] - 22, FALL[1] - 0.75, 0.95), 60)], ease="io"),
            "actors": [him] + acts, "callbacks": [PR.attach(g, him, offset=(0, 0.02, 0))], "cues": [[0, 5, "THE SOUND DRAINS TO HIS BREATHING"]]}

def S06_SH120(nf):
    him0 = Actor("h0", COST["him"], nf); him0.hold(0, 6, pose("gun_temple", x=FALL[0], y=FALL[1], yaw=FACE)); him0.compute()
    h = him0.J[0, HEAD]
    p = tuple(h + np.array((-0.85, 0.22, 0.04))); sq(p)
    him = Actor("him", COST["him"], nf); him.hold(0, 6, pose("gun_temple", x=FALL[0], y=FALL[1], yaw=FACE))
    him.face(0, 2.25, eyes=0.08); him.face(2.25, 2.6, eyes=0.5); him.face(2.6, 6, eyes=1.75, mouth=0.6)
    return {"cam": cam(p, tuple(h + np.array((0, 0, -0.02))), 45, hh=0.3), "actors": [him], "callbacks": [gun_on(him)],
            "cues": [[0, 2.2, "ONLY HIS BREATHING"], [2.2, 2.6, "CLICK"], [2.8, 6, "THE ROAR CRASHES BACK IN"]]}
