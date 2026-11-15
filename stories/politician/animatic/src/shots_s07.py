from sh import *
from shots_s05 import SQ_WALLS, FALL, gather_sim, people

CUES = {"S07_SH040": [[0, 3, "THE CROWD, MUFFLED"]]}
ARM = np.array((-39.62, -6.62, 8.75))
TOP = np.array((ARM[0], ARM[1], 2.75))
HELI_AT = np.array((40.0, 80.0, 170.0))   # the helicopter hovering over the square, north-east, high
LIE = (-39.9, -5.6)            # where he lies before the haul, feet toward the arm
PIPE_AT = (-39.55, -5.05)       # the man with the pipe, north of him

def sq(eye, sky="warm"):
    reset(sky); return sets.square(eye)

_H = {}
def haul(T=4.0):
    """Ragdoll: lying on the road, hauled up by the right ankle, fighting to free himself."""
    if "haul" in _H: return _H["haul"]
    J0 = fk(pose("lie_back", x=LIE[0], y=LIE[1], yaw=180))
    rd = Ragdoll(J0); a0 = J0[RAN].copy()
    keys = [(0.0, 0.0), (0.5, 0.0), (0.9, 0.25), (1.2, 0.3), (1.6, 0.55), (1.9, 0.6), (2.4, 0.85), (2.7, 0.92), (3.1, 1.0)]
    def pin(t):
        u = float(np.interp(t, [k[0] for k in keys], [k[1] for k in keys]))
        return a0 + (TOP - a0) * u
    rd.pins[RAN] = pin
    rd.muscles.append(pulses([LHA, RHA, LEL, REL], 0.6, T, 0.28, 34, seed=3))
    rd.muscles.append(pulses([LAN, LKN, LTO], 0.8, T, 0.35, 30, seed=4))
    rd.muscles.append(toward([HEAD, NECK, LSH, RSH], lambda t, x: x[RAN] if (2.9 < t < 3.5) else None, 30))
    rd.muscles.append(toward([LHA, RHA], lambda t, x: x[RAN] if (3.0 < t < 3.6) else None, 40))
    JA = rd.run(T); _H["haul"] = JA; _H["state"] = (rd.x.copy(), rd.xp.copy()); return JA

def hanging(T, hits=(), struggle=0.4, seed=7, protect=None):
    """Continue hanging from the end of the haul: gentle swing, optional pipe hits (impulses on the left shoulder)."""
    haul()
    if "settled" not in _H:
        x0, xp0 = _H["state"]; s = Ragdoll(x0); s.xp = x0 * 0.5 + xp0 * 0.5; s.pins[RAN] = lambda t: TOP
        for _ in range(int(3.0 / s.dt)):
            s.xp = s.x * 0.04 + s.xp * 0.96; s.step()
        _H["settled"] = s.x.copy()
    x = _H["settled"]
    rd = Ragdoll(x); rd.xp = x.copy(); rd.pins[RAN] = lambda t: TOP
    if struggle:
        rd.muscles.append(pulses([LHA, RHA, LEL, REL], 0.0, T, 0.45, 18 * struggle, seed=seed))
    if protect is not None:
        rd.muscles.append(toward([LHA, RHA], lambda t, x_: x_[HEAD] + np.array((0, 0, -0.15)) if t > protect else None, 25))
    for th in hits:
        rd.muscles.append(impulse([LSH, LEL, NECK], th, (0.0, -2.2, 0.6), dur=0.08))
    return rd.run(T)

def rope_stick(JA, t0=0.0):
    return Stick("rope", 0.018, PAL["rope"], lambda f: (tuple(ARM), tuple(JA[min(len(JA) - 1, f)][RAN])))

def strikers(acts, t0=0.6):
    for i, a in enumerate(acts[:14]):
        ph = (i * 0.37) % 1.0
        def fn(f, q, ph=ph, side=i % 2):
            t = f / core.FPS
            if t < t0: return q
            s = 0.5 + 0.5 * math.sin((t * 2.6 + ph) * 2 * math.pi)
            arm = (40 + 130 * s, 15, 40 + 60 * (1 - s))
            return dict(q, ra=arm, spine=q["spine"] + 15 * s) if side else dict(q, la=arm, spine=q["spine"] + 15 * s)
        a.overlays.append((0, a.nf, fn))

def S07_SH010(nf):
    p = (-20.0, 16.0, 26.0); sq(p)
    him = Actor("him", COST["him"], nf)
    him.seq([(0, pose("sit_ground", x=FALL[0], y=FALL[1], yaw=90)), (1.2, pose("lie_curl", x=FALL[0], y=FALL[1], yaw=90))])
    rng = np.random.default_rng(81); n = 44
    P0 = falloff(FALL, n, r_min=6.0, lam=3.0, arc=(100, 300), seed=81, walls=SQ_WALLS, max_r=30)
    S = falloff(FALL, n, r_min=0.85, lam=1.5, arc=(-120, 200), seed=82, walls=SQ_WALLS, max_r=16)
    T_ = assign(P0, S, FALL)
    cr = Crowd(P0, rng.uniform(3.5, 5.0, n), focus=FALL, space_k=0.02, walls=SQ_WALLS, bubble=lambda t: (FALL, 0.65), seed=83)
    look = np.repeat(np.array(FALL)[None], n, 0)
    acts = people("c", cr.run(nf / core.FPS, lambda t, P, V: (seek(P, T_, cr.v0, 2.0), look)), nf, 84)
    strikers(acts, 1.0)
    return {"cam": cam(p, (-41, -8, 0.5), 35), "actors": [him] + acts, "cues": [[0, 5, "ROAR, FISTS AND KICKS"]]}

def S07_SH020(nf):
    p = (-35.2, -2.9, 1.7); sq(p)
    th = Actor("thrower", crowd_costume(random.Random(91)), nf, lod="high"); th.style = "shape"
    tp = (-38.1, -5.0); yaw = fdir(tp, ARM)
    th.seq([(0, pose("stand", x=tp[0], y=tp[1], yaw=yaw)), (0.3, pose("throw_back", x=tp[0], y=tp[1], yaw=yaw, ra=(165, 15, 40))),
            (0.75, pose("throw_fwd", x=tp[0], y=tp[1], yaw=yaw, ra=(150, 10, 5))), (1.6, pose("stand", x=tp[0], y=tp[1], yaw=yaw, hpitch=-40))])
    th.look(0.8, 3, tuple(ARM))
    him = Actor("him", COST["him"], nf); him.hold(0, 3, pose("lie_back", x=LIE[0], y=LIE[1], yaw=180))
    th.compute()
    coil = PR._obj("coil", PR._mesh_sphere("coil", 0.14, seg=8, rings=5), PAL["rope"])
    end = np.array((-40.3, -7.3, 1.0))
    def cpos(f):
        t = f / core.FPS; hand = th.J[min(f, nf - 1)][RHA]
        if t < 0.75: return hand
        if t < 1.35:
            u = (t - 0.75) / 0.6; a = hand; b = ARM + np.array((0, 0, 0.35))
            return a + (b - a) * u + np.array((0, 0, 1.2 * u * (1 - u)))
        u = min(1, (t - 1.35) / 0.7); return ARM + (end - ARM) * (u * u)
    def coil_cb(f): coil.location = tuple(cpos(f))
    s1 = Stick("rope1", 0.016, PAL["rope"], lambda f: (tuple(th.J[min(f, nf - 1)][RHA]), tuple(cpos(f) if f < F(1.35) else ARM)))
    s2 = Stick("rope2", 0.016, PAL["rope"], lambda f: (None, None) if f < F(1.35) else (tuple(ARM), tuple(cpos(f))))
    rng = np.random.default_rng(92)
    others = []
    for i, (x, y) in enumerate([(-37.2, -4.2), (-36.6, -5.9), (-38.6, -3.9), (-37.6, -7.0)]):
        a = Actor(f"o{i}", crowd_costume(random.Random(93 + i)), nf); a.hold(0, 3, pose("stand", x=x, y=y, yaw=fdir((x, y), LIE))); a.look(0.8, 3, tuple(ARM)); others.append(a)
    return {"cam": cam(p, (-39.0, -6.2, 3.2), 24, hh=0.6), "actors": [th, him] + others, "sticks": [s1, s2], "callbacks": [coil_cb],
            "cues": [[0.5, 2.1, "A ROPE SAILS OVER THE ARM"]]}

def S07_SH030(nf):
    p = (-36.4, -3.6, 1.85); sq(p)
    JA = haul(); him = Actor("him", COST["him"], nf); him.joints(0, JA)
    him.face(0, 4, eyes=1.3, mouth=0.5)
    pullers = []
    for i, (x, y) in enumerate([(-38.2, -3.2), (-37.6, -2.5), (-37.0, -1.8)]):
        a = Actor(f"pull{i}", crowd_costume(random.Random(100 + i)), nf); a.style = "shape"
        yaw = fdir((x, y), ARM[:2])
        a.hold(0, 0.5, pose("pull", x=x, y=y, yaw=yaw))
        a.path(0.5, 3.2, [(x, y), (x + 0.6, y + 1.2)], "walk", speed="io", base=POSES["pull"], yaw_fixed=yaw)
        a.hold(3.2, 4, pose("pull", x=x + 0.6, y=y + 1.2, yaw=yaw)); pullers.append(a)
    for a in pullers: a.compute()
    s1 = rope_stick(JA)
    s2 = Stick("rope2", 0.018, PAL["rope"], lambda f: (tuple(ARM), tuple(pullers[0].J[min(f, nf - 1)][RHA])))
    s3 = Stick("rope3", 0.018, PAL["rope"], lambda f: (tuple(pullers[0].J[min(f, nf - 1)][RHA]), tuple(pullers[2].J[min(f, nf - 1)][RHA])))
    near = []
    for i, (x, y) in enumerate([(-37.6, -4.9), (-38.0, -5.4), (-38.6, -4.7), (-37.3, -5.6), (-38.9, -5.8)]):
        a = Actor(f"n{i}", crowd_costume(random.Random(110 + i)), nf); a.hold(0, 4, pose("stand", x=x, y=y, yaw=fdir((x, y), (ARM[0], ARM[1])), hpitch=-15)); near.append(a)
    rng = np.random.default_rng(120)
    ring = []
    for i, (x, y) in enumerate(falloff((ARM[0], ARM[1]), 16, r_min=2.0, lam=1.8, arc=(150, 330), seed=121, walls=SQ_WALLS, max_r=16)):
        a = Actor(f"r{i}", crowd_costume(random.Random(130 + i)), nf); a.hold(0, 4, pose("stand", x=x, y=y, yaw=fdir((x, y), ARM[:2]))); ring.append(a)
    return {"cam": cam(p, (ARM[0], ARM[1], 2.2), 30, hh=0.7), "actors": [him] + pullers + near + ring, "sticks": [s1, s2, s3],
            "cues": [[0.5, 3.1, "THEY HAUL HIM UP BY ONE ANKLE"]]}

def S07_SH040(nf):
    JA = hanging(nf / core.FPS, struggle=0.04, seed=11)
    head0 = JA[0][HEAD]
    p = tuple(head0 + np.array((0.55, 0.85, 0.05))); sq(p)
    him = Actor("him", COST["him"], nf); him.joints(0, JA)
    him.face(0, 1.2, eyes=0.1); him.face(1.2, 3.0, eyes=0.55)
    return {"cam": follow(him, p, lens=50, offset=(0, 0, 0), lag=0.2, joint=HEAD), "actors": [him], "sticks": [rope_stick(JA)]}

def pipe_man(nf, keys):
    a = Actor("pipe", crowd_costume(random.Random(141)), nf, lod="high"); a.style = "shape"; yaw = fdir(PIPE_AT, (ARM[0], ARM[1]))
    a.seq([(t, pose(n, x=PIPE_AT[0], y=PIPE_AT[1], yaw=yaw)) for t, n in keys]); return a

def pipe_stick(a):
    def fn(f):
        J = a.J[min(f, a.nf - 1)]; m = (J[LHA] + J[RHA]) / 2; d = J[RHA] - J[LHA]
        fwd = (J[LHA] + J[RHA]) / 2 - (J[LSH] + J[RSH]) / 2; fwd /= (np.linalg.norm(fwd) + 1e-9)
        return tuple(m - fwd * 0.15), tuple(m + fwd * 1.0)
    return Stick("pipe_bar", 0.025, "#8A8A8E", fn)

def S07_SH050(nf):
    T = nf / core.FPS
    JA = hanging(T, hits=(1.0, 2.1), struggle=0.3, seed=12, protect=0.2)
    sq(tuple(JA[0][HEAD]))
    pm = pipe_man(nf, [(0, "pipe_down"), (0.6, "pipe_up"), (1.0, "pipe_down"), (1.7, "pipe_up"), (2.1, "pipe_down"), (3.0, "pipe_down")])
    him = Actor("him", COST["him"], nf); him.joints(0, JA); him.hide(0, T)
    def camfn(t):
        f = min(len(JA) - 1, int(round(t * core.FPS))); J = JA[f]
        pos = J[HEAD] + (J[NOSE] - J[HEAD]) * 0.8
        return pos, np.array((PIPE_AT[0], PIPE_AT[1], 1.3)), 24, 180
    return {"cam": {"fn": camfn}, "actors": [him, pm], "sticks": [pipe_stick(pm)], "cues": [[1.0, 1.2, "HIT"], [2.1, 2.3, "HIT"]]}

def S07_SH060(nf):
    p = (-38.9, -5.75, 0.35); sq(p)
    pm = pipe_man(nf, [(0, "pipe_down"), (1.0, "pipe_up"), (2.0, "pipe_up")])
    JA = hanging(nf / core.FPS, struggle=0.2, seed=13); him = Actor("him", COST["him"], nf); him.joints(0, JA)
    return {"cam": cam(p, (PIPE_AT[0], PIPE_AT[1], 2.4), 24), "actors": [pm, him], "sticks": [pipe_stick(pm), rope_stick(JA)]}

_PM = {}
def pipe_fall(nf):
    if "J" in _PM: return _PM["J"]
    yaw = fdir(PIPE_AT, (ARM[0], ARM[1]))
    J0 = fk(pose("pipe_up", x=PIPE_AT[0], y=PIPE_AT[1], yaw=yaw))
    back = -np.array((-math.sin(math.radians(yaw)), math.cos(math.radians(yaw)), 0))
    V0 = np.zeros_like(J0); V0[HEAD] = back * 4.0 + (0, 0, 0.5); V0[NOSE] = V0[HEAD]; V0[NECK] = back * 2.0
    rd = Ragdoll(J0, V0); _PM["J"] = rd.run(2.2); return _PM["J"]

def S07_SH070(nf):
    p = (-31.5, -1.5, 8.5); sq(p)
    pm = Actor("pipe", crowd_costume(random.Random(141)), nf, lod="high"); pm.style = "shape"; yaw = fdir(PIPE_AT, (ARM[0], ARM[1]))
    pm.hold(0, 1.0, pose("pipe_up", x=PIPE_AT[0], y=PIPE_AT[1], yaw=yaw)); pm.joints(1.0, pipe_fall(nf))
    pm.compute()
    JA = hanging(nf / core.FPS, struggle=0.2, seed=14); him = Actor("him", COST["him"], nf); him.joints(0, JA)
    def pfn(f):
        t = f / core.FPS
        if t < 1.05:
            J = pm.J[min(f, nf - 1)]; m = (J[LHA] + J[RHA]) / 2; return tuple(m), tuple(m + np.array((0, 0, 1.0)))
        u = min(1, (t - 1.05) / 0.5); a = np.array((-39.3, -4.4, 2.4)); b = np.array((-39.0, -4.0, 0.05))
        s = a + (b - a) * u * u; return tuple(s), tuple(s + np.array((0.9 * u, 0.3 * u, (1 - u) * 1.0)))
    ring = []
    for i, (x, y) in enumerate(falloff((ARM[0], ARM[1]), 16, r_min=2.4, lam=1.8, arc=(140, 340), seed=151, walls=SQ_WALLS, max_r=16)):
        a = Actor(f"r{i}", crowd_costume(random.Random(160 + i)), nf); d = np.array((x, y)) - ARM[:2]; d /= np.linalg.norm(d)
        a.hold(0, 1.0, pose("stand", x=x, y=y, yaw=fdir((x, y), ARM[:2]))); a.path(1.0, 3.0, [(x, y), (x + d[0] * 1.2, y + d[1] * 1.2)], "walk", speed="out", yaw_fixed=fdir((x, y), ARM[:2]))
        ring.append(a)
    return {"cam": cam(p, (-39.6, -6.2, 1.4), 28), "actors": [pm, him] + ring, "sticks": [Stick("pipe_bar", 0.03, "#8A8A8E", pfn), rope_stick(JA)],
            "cues": [[1.0, 1.2, "CRACK FROM THE SKY"], [1.4, 2.4, "THE PIPE RINGS ON THE ASPHALT"]]}

def S07_SH080(nf):
    p = (-27.0, 7.0, 1.7); sq(p)
    JA = hanging(nf / core.FPS, struggle=0.15, seed=15); him = Actor("him", COST["him"], nf); him.joints(0, JA)
    body = Actor("pipe", crowd_costume(random.Random(141)), nf, lod="high"); body.joints(0, [pipe_fall(nf)[-1]] * nf)
    rng = np.random.default_rng(171); n = 26
    P0 = falloff((ARM[0], ARM[1]), n, r_min=2.0, lam=1.9, arc=(120, 360), seed=172, walls=SQ_WALLS, max_r=16)
    T_ = np.array(ARM[:2])[None] + (P0 - ARM[:2][None]) * rng.uniform(1.8, 2.6, n)[:, None]
    cr = Crowd(P0, rng.uniform(1.0, 1.6, n), walls=SQ_WALLS, space_k=0.0, seed=173)
    look = np.repeat(ARM[:2][None], n, 0)
    def brain(t, P, V):
        Vd = seek(P, T_, cr.v0, 1.0)
        if t < 0.3: Vd[:] = 0
        return Vd, look
    acts = people("c", cr.run(nf / core.FPS, brain), nf, 174)
    for a in acts:
        a.look(0.2, 3.0, tuple(HELI_AT))
    return {"cam": cam(p, (-40, -6.5, 3.0), 35), "actors": [him, body] + acts, "sticks": [rope_stick(JA)], "cues": [[0, 3, "SILENCE, A FAINT ROTOR FAR AWAY"]]}
