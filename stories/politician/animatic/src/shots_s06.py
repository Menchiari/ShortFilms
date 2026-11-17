from sh import *
from shots_s05 import SQ_WALLS, FALL, gather_sim, people, flinch

CUES = {}
FACE = 90.0                     # he faces west, toward the crowd
D = np.array((-1.0, 0.0))       # toward the crowd

def sq(eye, sky="warm"):
    reset(sky); return sets.square(eye)

def sitter(nf, pose_name="gun_up", **kw):
    a = Actor("him", COST["him"], nf); a.hold(0, nf / core.FPS, pose(pose_name, x=FALL[0], y=FALL[1], yaw=FACE, **kw)); return a

def gun_on(a):
    g = PR.hand_prop("gun", "gun"); return PR.attach(g, a, offset=(0, 0.02, 0))

def gun_temple_cb(g, a, t_from=None, t_to=None):
    """The muzzle pressed to his right temple. Between t_from and t_to it travels there from his hand."""
    hand = PR.attach(g, a, offset=(0, 0.02, 0))
    def at_temple(f):
        J = a.J[min(f, a.nf - 1)]
        up = J[HEAD] - J[NECK]; up = up / np.linalg.norm(up)
        right = J[RSH] - J[LSH]; right = right - up * np.dot(right, up); right = right / np.linalg.norm(right)
        y = -right; z = up; x = np.cross(y, z)
        tip = J[HEAD] + right * 0.1 + up * 0.03
        return Puppet.M(np.stack([x, y, z], 1), tip - y * 0.13)
    def cb(f):
        t = f / core.FPS
        if t_from is None or t >= t_to:
            g.hide_render = False; g.matrix_world = at_temple(f); return
        hand(f)
        if t > t_from:
            u = (t - t_from) / (t_to - t_from); u = u * u * (3 - 2 * u)
            g.matrix_world = g.matrix_world.lerp(at_temple(f), u)
    return cb

import phys

STAND = dict(x=FALL[0], y=FALL[1])
def standing(nf):
    a = Actor("him", COST["him"], nf); a.hold(0, nf / core.FPS, pose("stand", **STAND, yaw=FACE, ra=(85, 4, 4))); return a

# ---------------------------------------------------------------- the dead: one body map for every later shot
# SH020: shots 2..6 (runners, each dropped where he is hit). SH040: shots 7 and 8, off screen (two runners from SH030).
VICTIMS = [  # (start offset west of him, start offset north, hit distance, shot time, shot number, shot in)
    # d10: spread in a fan across the street and the square edge, each at his own distance: no pile
    (20.0, 14.0, 13.0, 2.6, 2, "SH020"), (19.0, -1.5, 9.5, 5.4, 3, "SH020"), (8.0, 16.0, 9.0, 7.6, 4, "SH020"),
    (17.0, 6.0, 5.5, 9.3, 5, "SH020"), (10.0, 4.0, 3.5, 10.6, 6, "SH020"), (12.0, 10.0, 6.5, 1.1, 7, "SH040"), (6.0, 12.0, 4.5, 2.5, 8, "SH040")]
RUN = 4.6
_K = {}
def kills():
    """Every man he kills: where he started, where he dropped, and the fall (MuJoCo), cached."""
    if "k" in _K: return _K["k"]
    out = []
    for i, (dx, dy, dh, ts, n, shot) in enumerate(VICTIMS):
        start = np.array((FALL[0] - dx, FALL[1] + dy)); him = np.array(FALL)
        d = him - start; L = np.linalg.norm(d); u = d / L
        hitp = him - u * dh; t0 = ts - (L - dh) / RUN
        yaw = fdir(start, FALL)
        JA = phys.death((float(hitp[0]), float(hitp[1])), yaw, 4.0, speed=RUN, hit=tuple(-u * 1.0) + (0.3,), buckle=False, seed=40 + i)
        out.append(dict(i=i, start=start, hit=hitp, t0=t0, ts=ts, n=n, shot=shot, yaw=yaw, JA=JA, cost=crowd_costume(random.Random(500 + i))))
    _K["k"] = out; return out

def dead_actors(nf, upto=99, prefix="dead"):
    """The bodies that lie where they fell (shot number <= upto)."""
    acts = []
    for k in kills():
        if k["n"] <= upto:
            a = Actor(f"{prefix}{k['i']}", k["cost"], nf); a.joints(0, [k["JA"][-1]] * nf); acts.append(a)
    return acts

def victim_actor(k, nf, t_shift=0.0):
    """A runner: stands in the crowd, runs at him, drops where the bullet hits (times relative to this shot)."""
    a = Actor(f"v{k['i']}", k["cost"], nf); t0 = k["t0"] - t_shift; ts = k["ts"] - t_shift
    if t0 > 0: a.hold(0, t0, pose("stand", x=float(k["start"][0]), y=float(k["start"][1]), yaw=k["yaw"]))
    a.path(max(0.0, t0), ts, [tuple(k["start"]), tuple(k["hit"])], "run", speed="lin")
    a.joints(ts, k["JA"])
    return a

def street_crowd(n, seed, nf, near=11.0, lam=4.0):
    """The crowd standing in the street west of him, looking at him, never in step."""
    P = band(FALL[0] - near, n, lam, -6.5, 6.8, seed=seed, dirx=-1.0, walls=SQ_WALLS)
    rng = np.random.default_rng(seed); acts = []
    for i, (x, y) in enumerate(P):
        a = Actor(f"s{i}", crowd_costume(random.Random(seed * 100 + i)), nf)
        a.hold(0, nf / core.FPS, pose("stand", x=float(x), y=float(y), yaw=fdir((x, y), FALL), spine=rng.uniform(-3, 8)))
        ph = rng.uniform(0, 6.28); fr = rng.uniform(0.1, 0.3)
        a.overlays.append((0, nf, lambda f, q, ph=ph, fr=fr: dict(q, hyaw=q["hyaw"] + 10 * math.sin(2 * math.pi * fr * f / core.FPS + ph))))
        acts.append(a)
    return acts

SIDE = ((FALL[0] - 8.5, FALL[1] + 16.0, 1.8), (FALL[0] - 8.5, FALL[1] + 1.0, 1.0), 22)

# ---------------------------------------------------------------- the pistol: Walther PPK/S, nickel; the slide kicks back and locks open on the last round
def pistol(name, hand=False):
    """Local axes as PR.hand_prop("gun"): the barrel along +y, up +z, origin at the top of the grip (in his hand).
    Returns a dict: root (frame and grip), slide (moves back along -y), flash (one frame per shot), and set(back, flash)."""
    mb = core.MB(None, detail=False)
    mb.box(-0.011, 0.011, -0.004, 0.104, -0.018, 0.0, "#B9B9B9")                      # frame
    mb.obox((0, -0.02, -0.052), (0.028, 0.034, 0.09), core.rotx(math.radians(-14)), "#2A2420")   # grip
    mb.box(-0.004, 0.004, 0.006, 0.05, -0.034, -0.03, "#A8A8A8"); mb.box(-0.004, 0.004, 0.046, 0.05, -0.034, -0.018, "#A8A8A8")   # trigger guard
    mb.box(-0.002, 0.002, 0.018, 0.024, -0.03, -0.016, "#5A5A5A")                      # trigger
    root = PR.mesh_obj(name, mb)
    br = PR._obj(name + "_barrel", PR._mesh_cyl(name + "_barrel", 0.0058, 0.0058, 0.064, n=10), "#8C8C8C", root)
    br.rotation_euler = (math.radians(-90), 0, 0); br.location = (0, 0.058, 0.016)
    ms = core.MB(None, detail=False)
    ms.box(-0.0125, 0.0125, -0.036, 0.121, 0.0, 0.031, "#D4D4D4")                      # slide
    ms.box(0.0124, 0.0132, 0.028, 0.06, 0.012, 0.026, "#1E1E1E")                       # ejection port (right side)
    ms.box(-0.004, 0.004, 0.1205, 0.1215, 0.011, 0.021, "#1E1E1E")                     # muzzle
    for k in range(5): ms.box(-0.013, 0.013, -0.03 + 0.005 * k, -0.028 + 0.005 * k, 0.004, 0.028, "#9A9A9A")   # serrations
    slide = PR.mesh_obj(name + "_slide", ms); slide.parent = root
    mf = core.MB(None, detail=False)
    flash = PR._obj(name + "_flash", PR._mesh_sphere(name + "_flash", 0.023, 1.0, 2.4, 1.0, seg=10, rings=6), "#FFF2B8", root)   # the flash: a hot blob
    flash.location = (0, 0.19, 0.016); flash.hide_render = True
    spikes = []
    for k in range(4):                                                                  # and four short spikes
        sp = PR._obj(name + f"_spike{k}", PR._mesh_sphere(name + f"_spike{k}", 0.012, 1.0, 1.0, 4.0, seg=6, rings=4), "#FFE7A0", flash)
        sp.rotation_euler = (0, math.radians(45 + 90 * k), 0); sp.location = (0, -0.03, 0); sp.hide_render = True; spikes.append(sp)
    parts = [root, br, slide, flash]
    if hand:
        mh = core.MB(None, detail=False); sk = COST["him"]["skin"]
        mh.obox((0, -0.022, -0.05), (0.05, 0.05, 0.085), core.rotx(math.radians(-14)), sk)      # fist round the grip
        mh.obox((0.0, 0.03, -0.035), (0.016, 0.03, 0.018), np.eye(3), sk)                         # finger on the trigger
        mh.obox((-0.018, 0.0, -0.006), (0.016, 0.05, 0.016), np.eye(3), sk)                       # thumb
        mh.obox((0, -0.19, -0.11), (0.07, 0.3, 0.07), core.rotx(math.radians(-20)), sk)           # forearm
        hand_o = PR.mesh_obj(name + "_hand", mh); hand_o.parent = root; parts.append(hand_o)
    def set_(back=0.0, fl=False):
        slide.location = (0, -0.026 * back, 0)
        for o in [flash] + spikes: o.hide_render = not fl or root.hide_render
    def show(on):
        for o in parts: o.hide_render = not on
        for o in [flash] + spikes: o.hide_render = True
    return {"root": root, "slide": slide, "flash": flash, "set": set_, "show": show}

def casing(name):
    return PR._obj(name, PR._mesh_cyl(name, 0.0045, 0.0045, 0.017, n=8), "#C9A048")

def gun_hand_cb(G, a, shots=(), locked_after=None, smoke_until=0.0):
    """The pistol in his right hand, along the forearm (PR.attach). A flash and the slide kick on each shot; locked back after locked_after."""
    hold = PR.attach(G["root"], a, offset=(0, 0.02, 0))
    fr = [F(t) for t in shots]
    def cb(f):
        hold(f); G["show"](True)
        back = 1.0 if (locked_after is not None and f / core.FPS >= locked_after) else 0.0
        for k in fr:
            if f == k: back = 1.0
            elif f == k + 1: back = max(back, 0.5)
        G["set"](back, f in fr)
    return cb

def muzzle(G):
    """The muzzle tip of the pistol in world space (after the callbacks placed it)."""
    m = G["root"].matrix_world; return np.array(m @ Vector((0, 0.125, 0.016)))

def smoke_cb(G, t1=2.6, n=8, seed=3):
    """Smoke curling from the muzzle after the shot into the air: small puffs that rise, drift and swell."""
    rng = np.random.default_rng(seed); objs = [PR._obj(f"smoke{i}", PR._mesh_sphere(f"smoke{i}", 1.0, seg=8, rings=5), "#C9C3B8") for i in range(n)]
    drift = rng.normal(0, 0.05, (n, 2)); born = np.linspace(0, t1 * 0.7, n); hist = {}
    def cb(f):
        t = f / core.FPS; hist[f] = muzzle(G)
        for i, o in enumerate(objs):
            age = t - born[i]
            if age < 0 or t > t1 + 0.4: o.hide_render = True; continue
            src = hist.get(F(born[i]), hist[f]); o.hide_render = False
            o.location = (src[0] + drift[i, 0] * age + 0.03 * math.sin(age * 5 + i), src[1] + drift[i, 1] * age, src[2] + 0.22 * age)
            r = 0.012 + 0.03 * min(1.0, age / 1.5) * max(0.0, 1 - max(0.0, t - t1) / 0.4); o.scale = (r, r, r * 0.8)
    return cb

# ---------------------------------------------------------------- SH010: frontal from the crowd's side, the corner facade a few steps behind him
CAM10 = (FALL[0] + 3.6 * math.cos(math.radians(75)), FALL[1] + 3.6 * math.sin(math.radians(75)), 1.6)
YAW0 = fdir(FALL, CAM10)          # he faces the camera in SH010 and at the start of SH020; the corner is at his back

def S06_SH010(nf):
    """Medium, frontal: at the corner, the facade a few steps behind him, the street light beside him (never in front).
    A few people near the camera run off past it; the rest freeze, then back away past the camera."""
    p = CAM10; sq(p); T = nf / core.FPS
    f_ = np.array(FALL) - np.array(p[:2]); f_ /= np.linalg.norm(f_); r_ = np.array((f_[1], -f_[0]))
    him = Actor("him", COST["him"], nf)
    him.seq([(0, pose("stand", **STAND, yaw=YAW0, ra=(85, 4, 4))), (1.6, pose("stand", **STAND, yaw=YAW0 + 12, ra=(88, 4, 4))),
             (3.2, pose("stand", **STAND, yaw=YAW0 - 14, ra=(86, 4, 4))), (5.0, pose("stand", **STAND, yaw=YAW0 + 4, ra=(87, 4, 4)))])
    him.talk(0.6, 2.2); him.talk(3.3, 5.6); him.face(0, 6, eyes=1.4)
    rng = np.random.default_rng(31)
    camp = np.array(p[:2]); sight = [(tuple(camp + (np.array(FALL) - camp) * u), 0.9) for u in np.linspace(0, 0.85, 8)]
    P0 = falloff(FALL, 20, r_min=1.8, lam=1.8, arc=(-75, 195), seed=31, walls=SQ_WALLS, avoid=sight, max_r=14)
    d = P0 - np.array(FALL)[None]; r = np.linalg.norm(d, axis=1)
    T_ = np.array(FALL)[None] + d / r[:, None] * (6.0 + 1.5 * r)[:, None]
    cr = Crowd(P0, rng.uniform(0.9, 1.8, len(P0)), walls=SQ_WALLS, space_k=0.0, seed=33, start=rng.uniform(2.9, 4.2, len(P0)))
    look = np.repeat(np.array(FALL)[None], len(P0), 0)
    X, Y, YW, SP = cr.run(T, lambda t, P, V: (seek(P, T_, cr.v0, 1.0), look))
    YW = np.degrees(np.arctan2(-(FALL[0] - X), FALL[1] - Y))           # they back away facing him
    acts = people("c", (X, Y, YW, SP), nf, 34)
    for a in acts: a.overlays.append((0, nf, lambda f, q: dict(q, spine=q["spine"] - 6)))
    # the ones near the camera: already running when the shot starts, off past the lens
    for i, (s0, lat, v, t0) in enumerate(((1.1, -0.45, 4.2, 0.0), (1.6, 0.55, 3.8, 0.0), (2.2, -0.85, 4.4, 0.25), (2.6, 0.95, 3.6, 0.5))):
        a0 = camp + f_ * s0 + r_ * lat; a1 = camp - f_ * 3.5 + r_ * lat * 2.6
        a = Actor(f"fg{i}", crowd_costume(random.Random(37 + i)), nf)
        if t0 > 0: a.hold(0, t0, pose("stand", x=float(a0[0]), y=float(a0[1]), yaw=fdir(a0, a1), spine=12))
        a.path(t0, t0 + float(np.linalg.norm(a1 - a0)) / v, [tuple(a0), tuple(a1)], "run", speed="lin" if t0 == 0 else "in")
        a.hide(t0 + float(np.linalg.norm(a1 - a0)) / v + 0.05, T)
        acts.append(a)
    # frozen at the frame edges, close to him; they back away past the camera when he yells again
    for i, (s0, lat, t0) in enumerate(((3.0, -1.35, 3.3), (2.7, 1.45, 3.0), (3.7, 1.9, 3.6), (3.4, -2.0, 3.9))):
        a0 = camp + f_ * s0 + r_ * lat; a1 = camp - f_ * 1.5 + r_ * lat * 1.6; yw = fdir(a0, FALL)
        a = Actor(f"fz{i}", crowd_costume(random.Random(71 + i)), nf)
        a.hold(0, t0, pose("stand", x=float(a0[0]), y=float(a0[1]), yaw=yw, spine=-6, la=(20, 15, 40), ra=(25, 15, 35)))
        a.path(t0, t0 + float(np.linalg.norm(a1 - a0)) / 1.1, [tuple(a0), tuple(a1)], "walk", speed="io", yaw_fixed=yw, base=dict(spine=-8))
        acts.append(a)
    G = pistol("gun")
    tgt = (FALL[0] + r_[0] * 0.25, FALL[1] + r_[1] * 0.25, 1.45)
    return {"cam": cam(p, tgt, 35, hh=0.6), "actors": [him] + acts, "speakers": {"OLD MAN": him},
            "say": [[0.6, 2.2, "OLD MAN"], [3.3, 5.6, "OLD MAN"]], "callbacks": [gun_hand_cb(G, him), smoke_cb(G)],
            "cues": [[0, 1.5, "EARS RINGING, SMOKE FROM THE MUZZLE"]]}

# ---------------------------------------------------------------- SH020: third person, close behind him, turning with him as he aims
def reacting_crowd(n, seed, nf, shots, r_min=5.0, keep_clear=()):
    """Around him, nobody standing still: some back off and then run (at a shot, early or late), some creep forward very slowly and
    freeze at each shot, some crouch and shuffle back low, some panic (dart one way, then another, hands on their heads).
    Everyone flinches at every shot."""
    rng = np.random.default_rng(seed); T = nf / core.FPS
    P0 = falloff(FALL, n, r_min=r_min, lam=3.2, arc=(-70, 200), seed=seed, walls=SQ_WALLS, max_r=24, avoid=keep_clear)
    role = rng.choice(4, n, p=(0.32, 0.26, 0.18, 0.24))                 # 0 back off then run, 1 creep, 2 crouch, 3 panic
    go = np.array([shots[min(len(shots) - 1, int(rng.integers(0, 3)))] + rng.uniform(0.15, 1.2) for _ in range(n)])
    v_run = rng.uniform(3.0, 5.0, n); v_slow = rng.uniform(0.3, 0.55, n); v_creep = rng.uniform(0.25, 0.45, n); v_dart = rng.uniform(2.0, 3.4, n)
    cr = Crowd(P0, v_slow.copy(), walls=SQ_WALLS, space_k=0.0, seed=seed)
    c = np.array(FALL); d0 = P0 - c[None]; u0 = d0 / np.linalg.norm(d0, axis=1)[:, None]
    away = c[None] + u0 * (np.linalg.norm(d0, axis=1)[:, None] + 25) + rng.normal(0, 3, (n, 2))
    side = np.stack([-u0[:, 1], u0[:, 0]], 1) * rng.choice((-1, 1), n)[:, None]
    wp = [P0 + rng.normal(0, 3.5, (n, 2)) for _ in range(8)]; hop = rng.uniform(0.9, 1.6, n); ph = rng.uniform(0, 6.28, n)
    def brain(t, P, V):
        Vd = np.zeros((n, 2)); look = np.repeat(c[None], n, 0); first = t >= shots[0]
        dist = np.linalg.norm(P - c[None], axis=1)[:, None] + 1e-6; out = (P - c[None]) / dist
        frozen = np.any([(t > s_) & (t < s_ + 0.8) for s_ in shots], axis=0)
        wave = (0.55 + 0.45 * np.sin(1.9 * t + ph))[:, None]
        back = out * v_slow[:, None] * wave                               # edging back, a step at a time, facing him
        cr.v0[:] = v_slow
        m = role == 0; Vd[m] = back[m]
        r_ = m & (t >= go); Vd[r_] = seek(P[r_], away[r_], v_run[r_], 1.0); look[r_] = away[r_]; cr.v0[r_] = v_run[r_]
        m = role == 1; cv = -out * v_creep[:, None] * wave; cv[dist[:, 0] < 3.5] = 0.0
        Vd[m] = 0.0 if frozen else cv[m]; cr.v0[m] = v_creep[m]
        m = role == 2; Vd[m] = (back[m] * 0.6) if first else (side[m] * 0.35 * wave[m])
        m = role == 3
        if first:
            k = (np.floor(t / hop) % 8).astype(int); W = np.stack([wp[k[i]][i] for i in range(n)])
            Vd[m] = seek(P[m], W[m], v_dart[m], 0.6); look[m] = W[m]; cr.v0[m] = v_dart[m]
        else:
            Vd[m] = side[m] * 0.5 * np.sin(1.3 * t + ph[m])[:, None]
        return Vd, look
    X, Y, YW, SP = cr.run(T, brain)
    for i in np.where(role != 3)[0]:                                     # the ones backing off or creeping keep their eyes on him
        mv = SP[:, i] < 1.2
        YW[mv, i] = np.degrees(np.arctan2(-(c[0] - X[mv, i]), c[1] - Y[mv, i]))
    acts = people("r", (X, Y, YW, SP), nf, seed + 1)
    for i, a in enumerate(acts):
        for s_ in shots:
            flinch(a, s_ + rng.uniform(0.0, 0.12), 0.7, amt=rng.uniform(0.4, 0.9), hands=role[i] != 1)
        if role[i] == 2:                                                  # crouched, arms over the head, from his first shot on
            t0 = shots[0] + rng.uniform(0.2, 0.6)
            a.over(t0, T + 0.5, ll=(105, 10, 125), rl=(100, 10, 128), spine=38, la=(150, 30, 125), ra=(150, 30, 125), hpitch=25)
        if role[i] == 3:
            a.over(shots[0] + 0.3, T + 0.5, la=(160, 40, 130), ra=(160, 40, 130))
        if role[i] == 1:
            a.overlays.append((0, nf, lambda f, q: dict(q, spine=q["spine"] - 4, la=(20, 12, 35), ra=(20, 12, 35))))
    _K["roles"] = (role, SP)
    return acts

def S06_SH020(nf):
    """Third person, close behind him over his right shoulder, turning with him as he aims. Shots 2 to 6: each man drops where he is hit."""
    sq((FALL[0] + 2.0, FALL[1] + 1.0, 1.7)); T = nf / core.FPS
    ks = [k for k in kills() if k["shot"] == "SH020"]
    him = Actor("him", COST["him"], nf)
    keys = [(0.0, pose("stand", **STAND, yaw=YAW0, ra=(85, 4, 4)))]
    for k in ks:
        ya = fdir(FALL, k["hit"])
        keys.append((max(0.3, k["ts"] - 0.9), pose("stand", **STAND, yaw=ya + 8, ra=(80, 4, 4))))
        keys.append((k["ts"] - 0.3, pose("stand", **STAND, yaw=ya, ra=(88, 4, 4))))
        keys.append((k["ts"] + 0.12, pose("stand", **STAND, yaw=ya, ra=(99, 4, 4), spine=-4)))
    him.seq(sorted(keys, key=lambda kk: kk[0]))
    lines = [(tuple(np.array(k["start"]) + (np.array(k["hit"]) - np.array(k["start"])) * u), 1.0) for k in ks for u in np.linspace(0, 1, 6)]
    acts = [victim_actor(k, nf) for k in ks] + reacting_crowd(40, 61, nf, [k["ts"] for k in ks], keep_clear=lines)
    G = pistol("gun"); him.compute()
    yaws = np.array([math.degrees(math.atan2(-(J[NOSE, 0] - J[HEAD, 0]), J[NOSE, 1] - J[HEAD, 1])) for J in him.J])
    yaws = np.degrees(np.unwrap(np.radians(yaws)))
    def camfn(t):
        f = min(nf - 1, int(round(t * core.FPS))); lag = [yaws[max(0, f - k)] for k in range(4)]; y = math.radians(float(np.mean(lag)))
        fw = np.array((-math.sin(y), math.cos(y))); rt = np.array((fw[1], -fw[0]))
        c = np.array(FALL)
        pos = c - fw * 1.9 + rt * 0.55; tgt = c + fw * 8.0 + rt * 0.3
        return np.array((pos[0], pos[1], 1.86)), np.array((tgt[0], tgt[1], 1.2)), 28, 0
    cues = [[k["ts"] - 1.2, k["ts"] - 0.6, "A YELL"] for k in ks[:2]] + [[k["ts"], k["ts"] + 0.25, f"SHOT {k['n']}"] for k in ks]
    return {"cam": {"fn": camfn, "hh": 0.9}, "actors": [him] + acts, "callbacks": [gun_hand_cb(G, him, shots=[k["ts"] for k in ks])], "cues": cues}

# ---------------------------------------------------------------- SH025: insert, the pistol firing again and again
SH025_SHOTS = [4 / 12, 11 / 12, 17 / 12, 24 / 12, 30 / 12]
def S06_SH025(nf):
    """Insert, locked-off, on the ejection-port side: the flash, the slide kicking back, a casing spinning away, five times."""
    ya = 72.0; fw = np.array((-math.sin(math.radians(ya)), math.cos(math.radians(ya)), 0.0)); rt = np.array((fw[1], -fw[0], 0.0))
    g0 = np.array((FALL[0], FALL[1], 1.42)) + fw * 0.55 + rt * 0.12
    p = tuple(g0 + rt * 0.52 + fw * 0.1 + np.array((0, 0, 0.05))); sq(p)
    G = pistol("gun", hand=True); root = G["root"]
    R = np.stack([rt, fw, np.array((0, 0, 1.0))], 1)
    cas = [casing(f"casing{i}") for i in range(len(SH025_SHOTS))]; rng = np.random.default_rng(25)
    cv = [rt * rng.uniform(1.0, 1.4) - fw * rng.uniform(0.2, 0.5) + np.array((0, 0, rng.uniform(0.5, 0.8))) for _ in cas]
    crowd = street_crowd(18, 251, nf, near=9.0, lam=3.0)
    def cb(f):
        t = f / core.FPS; kick = 0.0; back = 0.0; fl = False
        for s in SH025_SHOTS:
            dt = t - s
            if -0.01 <= dt < 0.25: kick = max(kick, math.exp(-max(0.0, dt) / 0.07))
            if abs(dt) < 0.01: back, fl = 1.0, True
            elif 0.07 < dt < 0.1: back = max(back, 0.5)
        Rk = R @ core.rotx(math.radians(11 * kick))
        root.matrix_world = Puppet.M(Rk, g0 - fw * 0.018 * kick); G["show"](True); G["set"](back, fl)
        for i, (o, s) in enumerate(zip(cas, SH025_SHOTS)):
            dt = t - s - 0.04
            if dt < 0: o.hide_render = True; continue
            port = g0 + rt * 0.014 + fw * 0.045 + np.array((0, 0, 0.02))
            q = port + cv[i] * dt + np.array((0, 0, -4.9 * dt * dt)); o.hide_render = bool(q[2] < 0.0)
            o.location = tuple(q); o.rotation_euler = (dt * 31, dt * 17, dt * 9)
    return {"cam": cam(p, tuple(g0 + fw * 0.06), 50, focus=float(np.linalg.norm(np.array(p) - g0)), fstop=2.8), "actors": crowd, "callbacks": [cb],
            "cues": [[s, s + 0.15, "SHOT"] for s in SH025_SHOTS]}

# ---------------------------------------------------------------- SH030: the side view: past the dead, they come at him again, one after another
def S06_SH030(nf):
    """Wide side view (him screen left, the crowd screen right), locked-off. The dead lie where they fell. One breaks into a run
    (the man shot on "three"), then another (the man shot on "two"), then more."""
    sq(SIDE[0]); T = nf / core.FPS
    last = [k for k in kills() if k["shot"] == "SH020"][-1]
    him = standing(nf); him.tracks.clear(); him.hold(0, T, pose("stand", **STAND, yaw=fdir(FALL, last["hit"]), ra=(86, 4, 4)))
    him.over(0.8, T, yaw=fdir(FALL, last["hit"]) + 25)
    acts = []
    for k, (t_c, t_r, t_h) in zip([k for k in kills() if k["shot"] == "SH040"], ((0.3, 1.1, 4.4), (0.9, 1.9, 5.2))):
        a = Actor(f"v{k['i']}", k["cost"], nf); S0 = np.array(k["start"]); H = np.array(k["hit"]); u = (H - S0) / np.linalg.norm(H - S0)
        C = S0 + u * 0.35 * (t_r - t_c)                                 # a few hesitant steps, then he breaks into a run
        a.hold(0, t_c, pose("stand", x=float(S0[0]), y=float(S0[1]), yaw=k["yaw"], spine=6))
        a.path(t_c, t_r, [tuple(S0), tuple(C)], "walk", speed="io")
        a.path(t_r, t_h, [tuple(C), tuple(H)], "run", speed="in")
        acts.append(a)
    # the crowd: edging in, each at his own pace; then more break into a run
    rng = np.random.default_rng(74); n = 36
    P0 = band(FALL[0] - 11.0, n, 2.6, -6.5, 6.8, seed=74, dirx=-1.0, walls=SQ_WALLS)
    run_at = np.where(rng.random(n) < 0.25, rng.uniform(2.4, 3.6, n), 99.0)
    v_edge = rng.uniform(0.1, 0.45, n); v_run = rng.uniform(3.2, 4.6, n)
    cr = Crowd(P0, v_edge.copy(), walls=SQ_WALLS, space_k=0.0, seed=75, start=rng.uniform(0, 1.5, n))
    c = np.array(FALL)[None]
    def brain(t, P, V):
        cr.v0[:] = np.where(t >= run_at, v_run, v_edge)
        return seek(P, np.repeat(c, n, 0) + (P - c) * np.where(t >= run_at, 0.15, 0.6)[:, None], cr.v0, 1.5), np.repeat(c, n, 0)
    acts += people("w", cr.run(T, brain), nf, 76)
    acts += dead_actors(nf, upto=6)
    G = pistol("gun")
    return {"cam": cam(*SIDE), "actors": [him] + acts, "callbacks": [gun_hand_cb(G, him)],
            "cues": [[1.1, 1.6, "A YELL, HE RUNS"], [1.9, 2.4, "ANOTHER"], [2.4, T, "MORE FEET"]]}

# ---------------------------------------------------------------- SH040: his lips, from the side, the lens right at his mouth
COUNT = [(0.2, 0.6), (1.15, 1.55), (2.1, 2.55)]          # three / two / one, whispered, faster
COUNT_SHOTS = [0.85, 1.8]                                # shots 7 and 8, off screen

def S06_SH040(nf):
    """One shot, extreme close on his lips from his left side: three (a shot), two (a shot), one."""
    sq((FALL[0] - 1.0, FALL[1], 1.6)); h0 = standing(nf); h0.compute(); J = h0.J[0]
    up = J[HEAD] - J[NECK]; up /= np.linalg.norm(up); fw = J[NOSE] - J[HEAD]; fw -= up * np.dot(fw, up); fw /= np.linalg.norm(fw)
    left = np.cross(up, fw); mouth = J[HEAD] + fw * 0.1 - up * 0.046
    a = math.radians(74); p = tuple(mouth + (fw * math.cos(a) + left * math.sin(a)) * 0.27 + up * 0.012); sq(p)
    him = standing(nf)
    for (t0, t1) in COUNT: him.talk(t0, t1)
    him.face(0, nf / core.FPS, eyes=0.35)
    return {"cam": cam(p, tuple(mouth + fw * 0.03), 30, hh=0.12, focus=0.27, fstop=2.8), "actors": [him], "speakers": {"OLD MAN": him},
            "say": [[t0 - 0.05, t1 + 0.05, "OLD MAN"] for (t0, t1) in COUNT],
            "cues": [[COUNT_SHOTS[0], COUNT_SHOTS[0] + 0.25, "SHOT 7 (OFF)"], [COUNT_SHOTS[1], COUNT_SHOTS[1] + 0.25, "SHOT 8 (OFF): THE SLIDE LOCKS OPEN"]]}

# ---------------------------------------------------------------- SH050: fully frontal; the slide is locked open, nothing fires
def S06_SH050(nf):
    """Close, fully frontal: eyes shut tight, the muzzle to his temple. He squeezes: nothing. He opens his eyes and looks at the gun:
    the slide locked back, the barrel bare. He understands."""
    sq((FALL[0] - 1.0, FALL[1], 1.6)); h0 = standing(nf); h0.compute(); J0 = h0.J[0]; h = J0[HEAD]
    fwd0 = J0[NOSE] - J0[HEAD]; fwd0[2] = 0; fwd0 /= np.linalg.norm(fwd0)
    p = tuple(h + fwd0 * 0.85 + np.array((0, 0, 0.01))); sq(p)
    him = standing(nf)
    him.face(0, 3.3, eyes=0.08); him.face(3.3, 4.1, eyes=1.0); him.face(4.1, 6, eyes=1.75, mouth=0.4)
    him.over(3.6, 6.5, hpitch=14, hyaw=-14)
    G = pistol("gun"); hand = PR.attach(G["root"], him, offset=(0, 0.02, 0))
    def frames(f):
        J = him.J[0]
        up = J[HEAD] - J[NECK]; up /= np.linalg.norm(up)
        right = J[RSH] - J[LSH]; right -= up * np.dot(right, up); right /= np.linalg.norm(right); fw = np.cross(up, right)
        y = -right; z = up; x = np.cross(y, z)
        temple = Puppet.M(np.stack([x, y, z], 1), J[HEAD] + right * 0.1 + up * 0.03 - y * 0.125)
        # in front of his chin, turned so the barrel crosses to his left: we see the port side, the slide locked back
        yb = -right * 0.7 + fw * 0.7; yb /= np.linalg.norm(yb); xb = np.cross(yb, up)
        look = Puppet.M(np.stack([xb, yb, up], 1) @ core.rotx(math.radians(12)), J[HEAD] + fw * 0.27 + right * 0.15 - up * 0.07)
        return temple, look
    def cb(f):
        t = f / core.FPS; G["show"](True); G["set"](1.0, False)
        temple, look = frames(f)
        if t < 0.5: hand(f); return
        if t < 1.4:
            hand(f); u = (t - 0.5) / 0.9; u = u * u * (3 - 2 * u); G["root"].matrix_world = G["root"].matrix_world.lerp(temple, u); return
        if t < 3.6:
            m = temple
            if 2.3 <= t < 2.5: m = temple @ Matrix.Translation(Vector((0, 0.004, 0)))          # the squeeze: a twitch, nothing fires
            G["root"].matrix_world = m; return
        u = min(1.0, (t - 3.6) / 0.7); u = u * u * (3 - 2 * u); G["root"].matrix_world = temple.lerp(look, u)
    return {"cam": cam(p, tuple(h + np.array((0, 0, -0.03))), 40, hh=0.0), "actors": [him], "callbacks": [cb],
            "cues": [[0, 2.3, "ONLY HIS BREATHING"], [2.3, 2.6, "THE TRIGGER: NOTHING"], [3.9, 6, "THE SOUND SLAMS BACK IN"]]}

def S06_SH060(nf):
    """Side view: the crowd hits him like a wave and throws him to the ground."""
    sq(SIDE[0])
    him = Actor("him", COST["him"], nf)
    him.seq([(0, pose("stand", **STAND, yaw=FACE, ra=(60, 4, 4))), (1.45, pose("stand", **STAND, yaw=FACE, ra=(60, 4, 4))),
             (1.7, pose("stand", x=FALL[0] + 0.6, y=FALL[1], yaw=FACE, spine=-35, hpitch=-30)), (2.2, pose("lie_back", x=FALL[0] + 1.3, y=FALL[1] + 0.1, yaw=FACE))])
    rng = np.random.default_rng(81); n = 46
    P0 = band(FALL[0] - 7, n, 3.0, -6.5, 6.8, seed=81, dirx=-1.0, walls=SQ_WALLS)
    S = falloff(FALL, n, r_min=0.6, lam=1.3, arc=(90, 290), seed=82, walls=SQ_WALLS, max_r=10); T_ = assign(P0, S, FALL)
    cr = Crowd(P0, rng.uniform(4.0, 5.6, n), walls=SQ_WALLS, space_k=0.02, focus=FALL, seed=83, start=rng.uniform(0, 0.7, n))
    acts = people("w", cr.run(nf / core.FPS, lambda t, P, V: (seek(P, T_, cr.v0, 1.2), np.repeat(np.array(FALL)[None], n, 0))), nf, 84)
    return {"cam": cam(*SIDE, hh=0.3), "actors": [him] + acts + dead_actors(nf), "cues": [[0, 4, "THE ROAR"], [1.5, 1.8, "IMPACT"]]}
