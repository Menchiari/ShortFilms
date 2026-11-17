from sh import *
from shots_s05 import SQ_WALLS, FALL, gather_sim, people
import phys
import mjdoll as M
from shots_s06 import dead_actors, kills

CUES = {"S07_SH040": [[0, 3, "THE CROWD, MUFFLED"]]}
ARM = phys.ARM; TOP = phys.TOP; LIE = phys.LIE
HELI_AT = np.array((40.0, 80.0, 170.0))   # the helicopter hovering over the square, north-east, high
PIPE_AT = (-38.45, -6.35)         # the fat man with the pipe, beside him on the road (he drops there: the body next to him in S09)
DOWN_AT = (FALL[0] + 1.3, FALL[1] + 0.1)

def sq(eye, sky="warm"):
    reset(sky); return sets.square(eye)

def haul(): return phys.haul()
def hanging(T, **kw): return phys.hanging(T, **kw)

def rope_stick(JA, t0=0.0):
    return Stick("rope", 0.018, PAL["rope"], lambda f: (tuple(ARM), tuple(JA[min(len(JA) - 1, f)][RAN])))

def fat_man(nf, keys):
    """The fat man from S04, a shape, both hands on the pipe."""
    a = Actor("fat", COST["fat"], nf); yaw = fdir(PIPE_AT, (ARM[0], ARM[1]))
    a.seq([(t, pose(n, x=PIPE_AT[0], y=PIPE_AT[1], yaw=yaw)) for t, n in keys]); return a

def pipe_stick(a, angle):
    """The pipe in both hands at his right shoulder. angle(t) in degrees: -40 cocked back over the shoulder, 0 straight up, 100 swung through."""
    def fn(f):
        J = a.J[min(f, a.nf - 1)]; t = f / core.FPS
        up = J[NECK] - J[PELVIS]; up /= np.linalg.norm(up)
        fwd = J[NOSE] - J[HEAD]; fwd -= up * np.dot(fwd, up); fwd /= np.linalg.norm(fwd); right = np.cross(fwd, up)
        th = math.radians(angle(t)); d = up * math.cos(th) + fwd * math.sin(th)
        grip = J[RSH] + fwd * 0.22 - up * 0.12 + right * 0.04
        return tuple(grip - d * 0.15), tuple(grip + d * 1.15)
    return Stick("pipe_bar", 0.025, "#8A8A8E", fn)

def swing(t_cock=0.0, t_swing=None, t_hit=None, hold=-40.0, at=108.0):
    """Cocked back, held; the swing stops on the hit (his forearm) and bounces back a little."""
    def ang(t):
        if t_swing is None or t < t_swing: return hold
        if t <= t_hit:
            u = (t - t_swing) / max(0.05, t_hit - t_swing); return hold + (at - hold) * u * u
        return at - 25 * min(1.0, (t - t_hit) / 0.35)
    return ang

_FD = {}
def fat_death():
    """The sniper's bullet: the fat man drops where he stands (MuJoCo)."""
    if "J" not in _FD:
        _FD["J"] = phys.death(PIPE_AT, fdir(PIPE_AT, (ARM[0], ARM[1])), 4.0, hit=(0.0, 0.4, -1.0), buckle=True, scale=1.07, wide=1.4, seed=7,
                              q={"lsh_x": 160, "rsh_x": 160, "lel_x": 40, "rel_x": 40})
    return _FD["J"]

SECOND = (-35.2, -2.1)
_SV = {}
def second_death():
    if "J" not in _SV:
        _SV["J"] = phys.death(SECOND, fdir(SECOND, ARM[:2]) + 180, 4.0, hit=(0.6, 0.3, -0.4), buckle=True, seed=11)
    return _SV["J"]

def bodies_s07(nf, fat=True, second=True):
    """Everyone dead by the end of S07: his kills, the fat man, the second man."""
    acts = dead_actors(nf)
    if fat:
        a = Actor("fatdead", COST["fat"], nf); a.joints(0, [fat_death()[-1]] * nf); acts.append(a)
    if second:
        a = Actor("seconddead", crowd_costume(random.Random(171)), nf); a.joints(0, [second_death()[-1]] * nf); acts.append(a)
    return acts

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


# ---------------------------------------------------------------- d10: bodies as obstacles, keyed poses, the pipe rig
def body_boxes(pad=0.25):
    """Floor boxes around the S06 dead: crowds walk around them and nobody is placed on them."""
    out = []
    for k in kills():
        J = k["JA"][-1]; out.append((float(J[:, 0].min()) - pad, float(J[:, 0].max()) + pad, float(J[:, 1].min()) - pad, float(J[:, 1].max()) + pad))
    return out

def ez(u, k):
    u = min(1.0, max(0.0, u))
    if k == "in": return u * u
    if k == "out": return 1 - (1 - u) ** 2
    if k == "lin": return u
    return u * u * (3 - 2 * u)

def keyed(a, keys, t0=0.0):
    """Pose to pose on the scene clock: keys [(t, pose, ease into this key)]. The shot starts at scene time t0."""
    def fn(f):
        t = f / core.FPS + t0
        if t <= keys[0][0]: return dict(keys[0][1])
        for (ta, pa, _), (tb, pb, kb) in zip(keys, keys[1:]):
            if t <= tb: return lerp_pose(pa, pb, ez((t - ta) / max(1e-6, tb - ta), kb))
        return dict(keys[-1][1])
    a.tracks.append((0, a.nf - 1, fn, 0))

def bframe(J):
    """Up, forward, right of the chest (follows lean and twist)."""
    up = J[NECK] - J[PELVIS]; up = up / np.linalg.norm(up)
    rt = J[RSH] - J[LSH]; rt = rt - up * np.dot(rt, up); rt = rt / np.linalg.norm(rt)
    return up, np.cross(up, rt), rt

PIPE_BACK, PIPE_FRONT = 0.2, 1.15     # pipe length behind and in front of the hands

def pipe_pose(J, k):
    """k = (th, tl, gf, gu, gr): th 0 = straight up, + toward the front; tl tips the swing plane to his right;
    the hands (both on the pipe) at the neck + forward gf, up gu, right gr. Returns butt, tip, grip, direction."""
    th, tl, gf, gu, gr = k; up, fw, rt = bframe(J)
    a, b = math.radians(th), math.radians(tl)
    d = (up * math.cos(b) + rt * math.sin(b)) * math.cos(a) + fw * math.sin(a)
    G = J[NECK] + fw * gf + up * gu + rt * gr
    return G - d * PIPE_BACK, G + d * PIPE_FRONT, G, d

def pkey(keys, t):
    """keys [(t, (th, tl, gf, gu, gr), ease into this key)] -> interpolated pipe key."""
    if t <= keys[0][0]: return keys[0][1]
    for (ta, ka, _), (tb, kb, e) in zip(keys, keys[1:]):
        if t <= tb:
            u = ez((t - ta) / max(1e-6, tb - ta), e); return tuple(x + (y - x) * u for x, y in zip(ka, kb))
    return keys[-1][1]

def solve_contact(J, P, gf, tl=80.0, gr=0.05):
    """The pipe key whose shaft passes through P. The swing plane keeps its tilt tl (90 = level, a flat swing at his
    head, under the hanging body); the hands go to the height that puts P in that plane. Returns the key and how far
    along the pipe P is."""
    up, fw, rt = bframe(J); b = math.radians(tl)
    nn = rt * math.cos(b) - up * math.sin(b); e1 = up * math.cos(b) + rt * math.sin(b)
    gu = float(np.clip((gr * math.cos(b) - float((np.array(P) - J[NECK]) @ nn)) / math.sin(b), -0.75, 0.1))
    G = J[NECK] + fw * gf + up * gu + rt * gr; v = np.array(P) - G
    th = math.degrees(math.atan2(float(v @ fw), float(v @ e1)))
    return (th, tl, gf, gu, gr), float(np.linalg.norm(v))

def rod_fall(A0, B0, T, v0=(0.0, 0.0, 0.0), e=0.35, r=0.03):
    """The dropped pipe: two ends with a fixed distance, gravity, bounces on the asphalt (it rings), slides to rest."""
    dt = 1 / 480.0; X = np.array([A0, B0], float); L = float(np.linalg.norm(X[1] - X[0]))
    Xp = X - np.array(v0, float) * dt; g = np.array((0, 0, -9.81)); out = []; every = int(round(1 / (core.FPS * dt)))
    for k in range(int(round(T / dt)) + 1):
        if k % every == 0: out.append(X.copy())
        V = X - Xp; Xp = X.copy(); X = X + V * 0.999 + g * dt * dt
        for _ in range(4):
            d = X[1] - X[0]; dl = np.linalg.norm(d) + 1e-9; c = (dl - L) / dl * 0.5; X[0] += d * c; X[1] -= d * c
            for i in (0, 1):
                h = core.ground_z(X[i, 0], X[i, 1]) + r
                if X[i, 2] < h:
                    X[i, 2] = h; Xp[i, 2] = h + V[i, 2] * e if V[i, 2] < 0 else h
                    Xp[i, :2] = X[i, :2] - V[i, :2] * 0.7
    return np.array(out)

def watchers(nf, n, seed, avoid=(), r_min=2.4, lam=2.6, max_r=16, center=None):
    """People standing around the corner, watching him hang; nobody on the dead."""
    c = center if center is not None else (ARM[0], ARM[1])
    P = falloff(c, n, r_min=r_min, lam=lam, arc=(-180, 180), seed=seed, walls=SQ_WALLS + body_boxes(), max_r=max_r, avoid=list(avoid))
    rng = np.random.default_rng(seed); out = []
    for i, (x, y) in enumerate(P):
        a = Actor(f"w{i}", crowd_costume(random.Random(seed * 10 + i)), nf)
        a.hold(0, nf / core.FPS, pose("stand", x=float(x), y=float(y), yaw=fdir((x, y), ARM[:2]) + rng.uniform(-15, 15), hpitch=-12, spine=rng.uniform(-3, 8)))
        ph = rng.uniform(0, 6.28); fr = rng.uniform(0.1, 0.3)
        a.overlays.append((0, nf, lambda f, q, ph=ph, fr=fr: dict(q, hyaw=q["hyaw"] + 10 * math.sin(2 * math.pi * fr * f / core.FPS + ph))))
        out.append(a)
    return out

def dies(a, t, JA):
    """Physics from time t (shot time) on, and the body stays down after the simulation ends."""
    a.joints(t, JA); a.joints(t + (len(JA) - 1) / core.FPS, [JA[-1]] * (a.nf + 1))

def fat_actor(nf, keys, t0=0.0):
    a = Actor("fat", COST["fat"], nf); keyed(a, keys, t0); return a

def pipe_track(a, keys, t0=0.0, after=None):
    """The pipe in his hands on the scene clock; after = (t_shot, frames of the dropped pipe) once he is shot."""
    def fn(f):
        t = f / core.FPS
        if after is not None and t >= after[0]:
            R = after[1][min(len(after[1]) - 1, F(t - after[0]))]; return tuple(R[0]), tuple(R[1])
        A, B, _, _ = pipe_pose(a.J[min(f, a.nf - 1)], pkey(keys, t + t0)); return tuple(A), tuple(B)
    return Stick("pipe_bar", 0.03, "#8A8A8E", fn)

# The blow (SH050 and SH060 are two angles of one blow, on one clock: SH050 starts at 0, SH060 at H - 0.8)
H = 4.0                     # contact, SH050 time
SW_T = 5.4                  # length of the simulated hang around the blow
STEADY = 1.5
LOW = (150.0, 0.0, 0.42, -0.62, -0.12)       # pipe held low in front, both hands at the belly
COCK = (-20.0, -45.0, 0.12, -0.02, -0.28)    # cocked back over his shoulder (the left: he swings left to right, his forearm comes first)
ANTIC = (-38.0, -52.0, 0.05, 0.0, -0.30)     # coiled a little further before the swing
READY = (-15.0, -12.0, 0.25, -0.12, -0.18)   # after the blow: back up at the shoulder, ready again
_SW = {}
def swing_plan():
    """Where his forearm is at the blow, the fat man's moves, the pipe keys, and the hang with the blow in it."""
    if "plan" in _SW: return _SW["plan"]
    pre = phys.hanging(SW_T, struggle=0.15, seed=12, protect=0.3, steady=STEADY)
    fH = F(H); J = pre[fH]; FM = np.array(PIPE_AT)
    uh = (J[HEAD, :2] - FM) / np.linalg.norm(J[HEAD, :2] - FM); rgt = np.array((uh[1], -uh[0]))
    cand = []
    for side, (e, h) in (("lfarm", (LEL, LHA)), ("rfarm", (REL, RHA))):
        P = J[e] * 0.45 + J[h] * 0.55
        cand.append((float((P[:2] - FM) @ rgt), side, P))      # the swing comes from his left: the leftmost forearm meets it first
    _, side, P = min(cand, key=lambda c: c[0])
    yaw = fdir(PIPE_AT, P[:2]); u = (P[:2] - FM) / np.linalg.norm(P[:2] - FM); nrm = np.array((-u[1], u[0]))
    W = FM - u * 0.6                                    # wind-up spot: he steps into the blow
    S0 = W - nrm * 1.6 - u * 0.5                        # he comes in from the side, out of the crowd
    st = lambda x, y, **kw: pose("stand", x=float(x), y=float(y), **dict(dict(yaw=yaw), **kw))
    body = [(0.0, st(*S0, yaw=fdir(S0, W)), "io"), (1.2, st(*W), "io"),
            (2.5, st(*W, spine=-5, twist=16), "io"), (3.5, st(*W, spine=-4, twist=18), "io"),
            (3.72, st(*(W + u * 0.15), spine=-9, twist=30), "io"), (H, st(*FM, spine=10, twist=-22), "io"),
            (H + 0.2, st(*FM, spine=3, twist=-12), "out"), (H + 1.4, st(*FM, spine=2, twist=8), "io")]
    fm = Actor("fatplan", COST["fat"], F(SW_T) + 1); keyed(fm, body); fm.compute()
    CON, L = solve_contact(fm.J[fH], P, 0.42, tl=-80.0, gr=-0.05)
    # cocked high, the pipe drops behind him into a flat swing at his head height (under the hanging body, so the
    # forearm is the first thing it meets); it accelerates into the contact (ease in: fastest at the hit), then
    # rebounds with the restitution e: the angular speed reverses at e times the speed it came in with
    t_a = 3.72; t_s = 3.84; SLOT = (-40.0, -70.0, 0.22, -0.32, -0.24)
    e = 0.3; w_in = 2 * (CON[0] - SLOT[0]) / (H - t_s); D2 = 0.22; dth = e * w_in * D2 / 2
    REB = (CON[0] - dth, CON[1], CON[2] - 0.14, CON[3] + 0.05, CON[4] - 0.05)
    keys = [(0.0, LOW, "io"), (1.1, LOW, "io"), (2.5, COCK, "io"), (3.5, (-22.0, -46.0, 0.12, -0.01, -0.28), "io"),
            (t_a, ANTIC, "io"), (t_s, SLOT, "in"), (H, CON, "in"), (H + D2, REB, "out"), (H + 1.3, READY, "io")]
    # the blow pushes where the pipe moves at contact
    A1, B1, G1, d1 = pipe_pose(fm.J[fH], CON); A0, B0, G0, d0 = pipe_pose(fm.J[fH - 1], pkey(keys, H - 1 / core.FPS))
    hd = (G1 + d1 * L) - (G0 + d0 * L); hd[2] = min(hd[2], 0.0)
    JA = phys.hanging(SW_T, struggle=0.15, seed=12, protect=0.3, steady=STEADY, hits=(H,), hit_body=side, hit_dir=tuple(hd))
    _SW["plan"] = dict(JA=JA, body=body, keys=keys, P=P, side=side, L=L, CON=CON, W=W, S0=S0, yaw=yaw, hd=hd, w_in=w_in, dth=dth)
    return _SW["plan"]

# The kill (SH070 and SH080 are two angles of one kill, on one clock: SH070 starts at 0, SH080 at KC - 0.8)
KC = 2.65                   # the crack, SH070 time
HIGH = (-30.0, 0.0, 0.12, 0.60, -0.03)         # the pipe high over his head, both hands up
HIGH2 = (-58.0, 0.0, 0.04, 0.66, -0.03)        # stretched back to strike: the anticipation
KILL_YAW = fdir(PIPE_AT, (ARM[0], ARM[1]))
def kill_body():
    st = lambda **kw: pose("stand", x=PIPE_AT[0], y=PIPE_AT[1], yaw=KILL_YAW, **kw)
    return [(0.0, st(spine=2, twist=8), "io"), (0.3, st(spine=2, twist=8), "io"), (2.0, st(spine=-6), "io"), (KC, st(spine=-12), "io")]
KILL_KEYS = [(0.0, READY, "io"), (0.3, READY, "io"), (2.0, HIGH, "io"), (KC, HIGH2, "io")]
_KP = {}
def kill_pipe():
    """The pipe at the crack, then dropped: it falls, rings on the asphalt, rolls to rest (the same in SH070 and SH080)."""
    if "R" not in _KP:
        fm = fat_actor(F(KC) + 2, kill_body()); fm.compute()
        A, B, _, _ = pipe_pose(fm.J[F(KC)], pkey(KILL_KEYS, KC))
        _KP["R"] = rod_fall(A, B, 3.0, v0=(0.25 * math.sin(math.radians(KILL_YAW)), -0.25 * math.cos(math.radians(KILL_YAW)), 0.3))
    return _KP["R"]


def S07_SH010(nf):
    """From far above: the mob closes over him at the corner; more keep coming from every street; the dead lie where they fell."""
    p = (-20.0, 16.0, 26.0); sq(p)
    him = Actor("him", COST["him"], nf); him.hold(0, nf / core.FPS, pose("lie_curl", x=DOWN_AT[0], y=DOWN_AT[1], yaw=90))
    rng = np.random.default_rng(81); n = 60
    BW = SQ_WALLS + body_boxes()
    P0 = falloff(DOWN_AT, n, r_min=4.0, lam=2.6, arc=(-180, 180), seed=81, walls=BW, max_r=24)
    S = falloff(DOWN_AT, n, r_min=0.8, lam=1.4, arc=(-180, 180), seed=82, walls=BW, max_r=12)
    T_ = assign(P0, S, DOWN_AT)
    cr = Crowd(P0, rng.uniform(1.5, 4.5, n), focus=DOWN_AT, space_k=0.02, walls=BW, bubble=lambda t: (DOWN_AT, 0.65), seed=83, start=rng.uniform(0, 1.2, n))
    look = np.repeat(np.array(DOWN_AT)[None], n, 0)
    acts = people("c", cr.run(nf / core.FPS, lambda t, P, V: (seek(P, T_, cr.v0, 2.0), look)), nf, 84)
    strikers(acts, 0.6)
    # more people arriving from the streets and the square, each at his own pace, and the ones who just watch
    m = 70
    Q0 = falloff(DOWN_AT, m, r_min=14.0, lam=9.0, arc=(-180, 180), seed=85, walls=BW, max_r=60)
    Q1 = falloff(DOWN_AT, m, r_min=4.0, lam=4.0, arc=(-180, 180), seed=86, walls=BW, max_r=30); QT = assign(Q0, Q1, DOWN_AT)
    cr2 = Crowd(Q0, rng.uniform(0.6, 3.0, m), walls=BW, space_k=0.0, seed=87, start=rng.uniform(0, 3.5, m))
    acts += people("o", cr2.run(nf / core.FPS, lambda t, P, V: (seek(P, QT, cr2.v0, 2.0), np.repeat(np.array(DOWN_AT)[None], m, 0))), nf, 88)
    return {"cam": cam(p, (-41, -8, 0.5), 35), "actors": [him] + acts + dead_actors(nf), "cues": [[0, 5, "ROAR, FISTS AND KICKS"]]}

def S07_SH020(nf):
    """Insert at the street light: the rope whips over the arm and is pulled tight."""
    p = tuple(ARM + np.array((1.25, 1.45, -0.55))); sq(p)
    coil = PR._obj("coil", PR._mesh_sphere("coil", 0.09, seg=8, rings=5), PAL["rope"])
    low = np.array((-38.1, -5.0, 1.6)); over = ARM + np.array((0.05, 0.05, 0.3)); fall = ARM + np.array((-0.05, -0.1, -2.6))
    def cpos(f):
        t = f / core.FPS
        if t < 0.9:
            u = t / 0.9; return low + (over - low) * u + np.array((0, 0, 2.0 * u * (1 - u)))
        u = min(1, (t - 0.9) / 0.6); return over + (fall - over) * (u * u)
    def coil_cb(f): coil.location = tuple(cpos(f)); coil.hide_render = f >= F(1.5)
    s1 = Stick("rope1", 0.016, PAL["rope"], lambda f: (tuple(low), tuple(cpos(f) if f < F(0.9) else over)))
    s2 = Stick("rope2", 0.016, PAL["rope"], lambda f: (None, None) if f < F(0.9) else (tuple(over), tuple(cpos(f) if f < F(1.5) else fall)))
    wrap = Stick("wrap", 0.03, PAL["rope"], lambda f: (None, None) if f < F(1.6) else (tuple(ARM + np.array((0.12, 0.12, 0.02))), tuple(ARM - np.array((0.12, 0.12, -0.02)))))
    tight = lambda f: 0.0 if f < F(1.6) else 1.0
    return {"cam": cam(p, tuple(ARM - np.array((0.2, 0.2, 0.25))), 45, hh=0.3), "sticks": [s1, s2, wrap],
            "callbacks": [coil_cb], "cues": [[0.2, 1.0, "THE ROPE WHIPS OVER"], [1.6, 2.0, "PULLED TIGHT"]]}

_HM = {}
def haul_more(T, seed=31):
    """d11: after the haul (unchanged), the same body keeps going on the rope: twisting, clawing, kicking."""
    key = (round(T, 3), seed)
    if key not in _HM:
        phys.haul(); rng = np.random.default_rng(seed)
        d = M.Doll(rope=tuple(ARM), sidewalks=phys.CORNER); d.set_state(phys._C["haul_state"]); d.set_rope(phys.ROPE_FINAL)
        kicks = tuple(sorted(rng.uniform(0.0, T, 4))); reach = tuple(sorted(rng.uniform(0.0, T - 0.6, 2))); crunch = (rng.uniform(0.3, max(0.4, T - 1.0)),)
        ctrl = lambda t, dd: phys._tone_live(t, dd, crunch=crunch, kicks=kicks, reach=reach)
        _HM[key] = d.run(T, ctrl=ctrl, rope_fn=lambda t: phys.ROPE_FINAL, tone=20)
    return _HM[key]

def S07_SH030(nf):
    """Through heads and shoulders: they haul him up by one ankle, beside the curb. Real weight. Then he hangs there,
    twisting, clawing at the rope, the free leg kicking (d11: longer; the haul itself is unchanged)."""
    p = (-36.4, -3.6, 1.85); sq(p)
    JH = haul(); T = nf / core.FPS
    JA = np.concatenate([JH[:len(JH) - 1], haul_more(T - (len(JH) - 1) / core.FPS + 0.1)])[:nf] if T > 4.0 + 1e-6 else JH
    him = Actor("him", COST["him"], nf); him.joints(0, JA)
    him.face(0, T, eyes=1.3, mouth=0.5)
    pullers = []
    for i, (x, y) in enumerate([(-38.2, -3.2), (-37.6, -2.5), (-37.0, -1.8)]):
        a = Actor(f"pull{i}", crowd_costume(random.Random(100 + i)), nf); a.style = "shape"
        yaw = fdir((x, y), ARM[:2])
        a.hold(0, 0.5, pose("pull", x=x, y=y, yaw=yaw))
        a.path(0.5, 3.2, [(x, y), (x + 0.6, y + 1.2)], "walk", speed="io", base=POSES["pull"], yaw_fixed=yaw)
        a.hold(3.2, T, pose("pull", x=x + 0.6, y=y + 1.2, yaw=yaw)); pullers.append(a)
    for a in pullers: a.compute()
    s1 = rope_stick(JA)
    s2 = Stick("rope2", 0.018, PAL["rope"], lambda f: (tuple(ARM), tuple(pullers[0].J[min(f, nf - 1)][RHA])))
    near = []
    for i, (x, y) in enumerate([(-37.6, -4.9), (-38.0, -5.4), (-38.6, -4.7), (-37.3, -5.6), (-38.9, -5.8)]):
        a = Actor(f"n{i}", crowd_costume(random.Random(110 + i)), nf); a.hold(0, T, pose("stand", x=x, y=y, yaw=fdir((x, y), (ARM[0], ARM[1])), hpitch=-15)); near.append(a)
    ring = []
    for i, (x, y) in enumerate(falloff((ARM[0], ARM[1]), 22, r_min=2.0, lam=2.2, arc=(-180, 180), seed=121, walls=SQ_WALLS + body_boxes(), max_r=18, avoid=[((-36.4, -3.6), 1.5)])):
        a = Actor(f"r{i}", crowd_costume(random.Random(130 + i)), nf); a.hold(0, T, pose("stand", x=x, y=y, yaw=fdir((x, y), ARM[:2]))); ring.append(a)
    return {"cam": cam(p, (ARM[0], ARM[1], 2.2), 30, hh=0.7), "actors": [him] + pullers + near + ring + dead_actors(nf), "sticks": [s1, s2],
            "cues": [[0.5, 3.1, "THEY HAUL HIM UP BY ONE ANKLE"], [4.0, T, "HE TWISTS AND FIGHTS ON THE ROPE"]]}

_PN = {}
PANIC = 1.3                 # SH040: dazed until he gets one eye open, then panic takes him
def hang_panic(T, seed=11):
    """d11 SH040: first dazed, still; once he gets an eye open, panic: he twists on the rope, the head turns and
    searches for a way out, the free leg kicks. The sideways swing is damped (as in SH050) so the close stays on his face."""
    key = (round(T, 3), seed)
    if key not in _PN:
        phys.haul(); rng = np.random.default_rng(seed)
        d = M.Doll(rope=tuple(ARM), sidewalks=phys.CORNER); d.set_state(phys._C["settled"]); d.set_rope(phys.ROPE_FINAL)
        kicks = tuple(sorted(rng.uniform(PANIC, T, 4))); reach = (2.3,); ph = rng.uniform(0, 6.28, 4)
        def ctrl(t, dd):
            g = phys._tone_live(t, dd, kicks=kicks, reach=reach)
            w = min(1.0, max(0.0, (t - PANIC) / 0.35))
            g["neck_z"] = (w * (38 * math.sin(2.6 * t + ph[0]) + 16 * math.sin(5.9 * t + ph[1])), 12)
            g["neck_y"] = (w * 12 * math.sin(3.7 * t + ph[2]), 10)
            g["neck_x"] = (-20 + w * 15 * math.sin(4.1 * t + ph[3]), 12)
            return g
        def forces(t, dd):
            v = dd.d.qvel[0:3].copy(); v[2] = 0.0
            return [("pelvis", -STEADY * 60.0 * v), ("torso", -STEADY * 30.0 * v)]
        _PN[key] = d.run(T, ctrl=ctrl, rope_fn=lambda t: phys.ROPE_FINAL, tone=20, forces=forces)
    return _PN[key]

def S07_SH040(nf):
    """Close on the front of his face, upside down: bruised. With effort he opens one eye, then panic takes him: he twists
    on the rope, gasping, eyes darting for a way out.
    The camera eases round with his slow turn on the rope, so it stays on his face."""
    T = nf / core.FPS; JA = hang_panic(T)
    D = np.array([(J[NOSE] - J[HEAD])[:2] / (np.linalg.norm((J[NOSE] - J[HEAD])[:2]) + 1e-9) for J in JA])
    k = 9; Dp = np.concatenate([D[:1].repeat(k, 0), D, D[-1:].repeat(k, 0)])
    Ds = np.array([Dp[i:i + 2 * k + 1].mean(axis=0) for i in range(len(D))]); Ds /= np.linalg.norm(Ds, axis=1)[:, None]
    Hp = np.concatenate([JA[:1, HEAD].repeat(k, 0), JA[:, HEAD], JA[-1:, HEAD].repeat(k, 0)])
    Hs = np.array([Hp[i:i + 2 * k + 1].mean(axis=0) for i in range(len(D))])
    def pos(t):
        f = min(len(D) - 1, int(round(t * core.FPS))); return Hs[f] + np.array((Ds[f][0] * 2.1, Ds[f][1] * 2.1, 0.05))
    p = tuple(pos(0)); sq(p)
    him = Actor("him", COST["him"], nf); him.joints(0, JA)
    him.face(0, 0.7, eyes=0.08, mouth=0.1); him.face(0.7, PANIC, eyes=0.45, mouth=0.15)                # with effort, an eye opens
    him.face(PANIC, T, eyes=1.15)                                                                      # then wide, darting
    him.overlays.append((F(PANIC), nf, lambda f, q: dict(q, mouth=0.25 + 0.45 * abs(math.sin(f * 1.1)))))   # gasping
    return {"cam": follow(him, pos, lens=70, offset=(0, 0, 0), lag=0.35, joint=HEAD), "actors": [him], "sticks": [rope_stick(JA)]}

def _seg(a, b, k=6, r=0.9):
    a = np.array(a[:2], float); b = np.array(b[:2], float); return [(tuple(a + (b - a) * u), r) for u in np.linspace(0, 1, k)]

def S07_SH050(nf):
    """His upside-down view: the fat man steps in, the pipe low in both hands, slowly lifts it back over his shoulder,
    holds it there, waits, then swings hard straight at him. The pipe cracks on his forearm and bounces back."""
    pl = swing_plan(); JA = pl["JA"]
    sq(tuple(JA[0][HEAD]))
    fm = fat_actor(nf, pl["body"]); fm.compute()
    him = Actor("him", COST["him"], nf); him.joints(0, JA[:nf]); him.hide(0, nf / core.FPS)
    tgt = np.array((pl["W"][0], pl["W"][1], 1.2))
    side = np.array((-(tgt[1] - JA[0][HEAD][1]), tgt[0] - JA[0][HEAD][0], 0.0)); side /= np.linalg.norm(side)
    def camfn(t):
        f = int(round(t * core.FPS)); pts = []
        for k in range(-1, 2):
            J = JA[min(len(JA) - 1, max(0, f + k))]; pts.append(J[HEAD] + (J[NOSE] - J[HEAD]) * 0.8)
        jolt = 0.0 if t <= H + 0.01 else 0.3 * math.exp(-(t - H) / 0.2) * math.cos((t - H - 0.08) * 30)     # the blow snaps his head
        return np.mean(pts, axis=0), tgt + side * jolt, 16, 180 + 25 * jolt
    crowd = watchers(nf, 26, 61, avoid=_seg(ARM, pl["W"]) + _seg(pl["S0"], pl["W"]) + [(tuple(pl["W"]), 1.6)])
    return {"cam": {"fn": camfn}, "actors": [him, fm] + crowd + dead_actors(nf), "sticks": [pipe_track(fm, pl["keys"])],
            "cues": [[H, H + 0.25, "CRACK ON THE FOREARM"]]}

def S07_SH060(nf):
    """Close, handheld, from the side: the pipe slams into his forearm, raised over his head, and bounces back off it."""
    pl = swing_plan(); t0 = H - 0.8; f0 = F(t0); JA = pl["JA"][f0:f0 + nf]
    P = pl["P"]; u = (P[:2] - np.array(PIPE_AT)); u /= np.linalg.norm(u); n = np.array((-u[1], u[0]))
    dv = u * 0.75 + n * 1.0; dv /= np.linalg.norm(dv)
    p = np.array((P[0] + dv[0] * 1.8, P[1] + dv[1] * 1.8, P[2] + 0.3)); sq(tuple(p))
    him = Actor("him", COST["him"], nf); him.joints(0, JA); him.face(0, 0.8, eyes=0.2); him.face(0.8, 2, eyes=0.0)
    fm = fat_actor(nf, pl["body"], t0); fm.compute()
    crowd = watchers(nf, 18, 62, avoid=_seg(p, P, r=1.0) + [(tuple(PIPE_AT), 1.4), (tuple(pl["W"]), 1.2)])
    tgt = (P[0] + u[0] * 0.05, P[1] + u[1] * 0.05, P[2] + 0.12)
    return {"cam": cam(tuple(p), tgt, 28, hh=0.4), "actors": [him, fm] + crowd + dead_actors(nf),
            "sticks": [pipe_track(fm, pl["keys"], t0), rope_stick(JA)], "cues": [[0.8, 1.05, "CRACK ON THE FOREARM"]]}

def _kill_hang(T, seed):
    return phys.hanging(T, struggle=0.12, seed=seed, steady=STEADY)

def S07_SH070(nf):
    """Low and close on the fat man alone, the sky behind him, like a finishing move: he slowly lifts the pipe high over
    his head with both hands, taking his time, ready. As he is about to swing: a crack. He drops out of the frame where
    he stands; the pipe falls and rings on the asphalt. A cheat: the hanging man is left out (only him, the pipe, the sky)."""
    fv = np.array((-math.sin(math.radians(KILL_YAW)), math.cos(math.radians(KILL_YAW))))
    a = math.radians(15); cd = np.array((fv[0] * math.cos(a) - fv[1] * math.sin(a), fv[0] * math.sin(a) + fv[1] * math.cos(a)))
    b = np.array(PIPE_AT) + cd * 1.7
    p = (float(b[0]), float(b[1]), 0.5); sq(p)
    fm = fat_actor(nf, kill_body()); dies(fm, KC, fat_death()); fm.compute()
    return {"cam": cam(p, (PIPE_AT[0], PIPE_AT[1], 1.75), 20), "actors": [fm],
            "sticks": [pipe_track(fm, KILL_KEYS, 0.0, after=(KC, kill_pipe()))],
            "cues": [[KC, KC + 0.3, "A CRACK FROM THE SKY"], [KC + 0.6, 4, "THE PIPE RINGS ON THE ASPHALT"]]}

def S07_SH080(nf):
    """High and in front: the crack, the fat man drops, the pipe rings. The crowd steps back, confused, looking around.
    Seconds later another man drops. A few run. Then others."""
    p = (-30.6, -9.0, 6.2); sq(p)
    shot = 0.8; shot2 = 3.0; t0 = KC - shot
    fm = fat_actor(nf, kill_body(), t0); dies(fm, shot, fat_death()); fm.compute()
    JA = _kill_hang(nf / core.FPS, 14); him = Actor("him", COST["him"], nf); him.joints(0, JA)
    rng = np.random.default_rng(171); n = 64
    P0 = falloff((ARM[0], ARM[1]), n, r_min=2.4, lam=3.0, arc=(-180, 180), seed=172, walls=SQ_WALLS + body_boxes(), max_r=26,
                 avoid=[(tuple(PIPE_AT), 1.3), (SECOND, 1.3), (p[:2], 5.5)] + _seg(p, SECOND, k=8, r=0.8) + _seg(p, PIPE_AT, k=10, r=0.6))
    out = P0 - ARM[:2][None]; out /= np.linalg.norm(out, axis=1)[:, None]
    back = P0 + out * rng.uniform(0.6, 2.0, n)[:, None]
    far = P0 + out * 30.0
    dsec = np.linalg.norm(P0 - np.array(SECOND)[None], axis=1)
    away2 = P0 + (P0 - np.array(SECOND)[None]) / dsec[:, None] * rng.uniform(1.5, 3.0, n)[:, None]
    near2 = dsec < 3.5
    react = shot + rng.uniform(0.25, 0.9, n)
    react2 = shot2 + rng.uniform(0.15, 0.5, n)
    t_run = np.full(n, 99.0); order = [i for i in rng.permutation(n)]
    for j, i in enumerate(order[:5]):
        t_run[i] = shot2 + 0.35 + 0.2 * j + rng.uniform(0, 0.15)              # a few run
    for j, i in enumerate(order[5:30]):
        t_run[i] = shot2 + 1.15 + 0.035 * j + rng.uniform(0, 0.35)            # then others
    v_back = rng.uniform(0.8, 1.3, n); v_run = rng.uniform(3.4, 5.0, n)
    v0 = np.where(t_run < 50, v_run, np.maximum(v_back, 1.6))
    def brain(t, P, V):
        T = back.copy(); sp = v_back.copy()
        m2 = near2 & (t >= react2); T[m2] = away2[m2]; sp[m2] = 1.6
        r = t >= t_run; T[r] = far[r]; sp[r] = v_run[r]
        Vd = seek(P, T, sp, 0.8); Vd[t < react] = 0.0
        return Vd, np.repeat(ARM[:2][None], n, 0)
    cr = Crowd(P0, v0, walls=SQ_WALLS + body_boxes(), space_k=0.0, seed=173)
    X, Y, YW, SP = cr.run(nf / core.FPS, brain)
    # stepping back they keep their eyes on the corner (a step back, not a turn away); runners face where they run
    for i in range(n):
        for f in range(X.shape[0]):
            t = f / core.FPS
            if t < t_run[i] and not (near2[i] and t >= react2[i]):
                YW[f, i] = fdir((X[f, i], Y[f, i]), ARM[:2])
    acts = people("c", (X, Y, YW, SP), nf, 174)
    for i, a in enumerate(acts):
        # confused: looking around and up at the sky, each on his own beat
        s1, s2, pt = rng.uniform(-70, 70), rng.uniform(-70, 70), rng.uniform(-40, -10); tl = react[i] + rng.uniform(0.3, 1.2)
        def look(f, q, s1=s1, s2=s2, pt=pt, tl=tl, r0=react[i], tr=t_run[i]):
            t = f / core.FPS
            if t < r0 or t >= tr: return q
            w = ez((t - r0) / 0.4, "io"); s = s1 if t < tl else s2
            return dict(q, hyaw=q["hyaw"] + s * w, hpitch=q["hpitch"] + pt * w)
        a.overlays.append((0, nf, look))
    sec = Actor("second", crowd_costume(random.Random(171)), nf)
    sec.hold(0, shot2, pose("stand", x=SECOND[0], y=SECOND[1], yaw=fdir(SECOND, ARM[:2]) + 180)); dies(sec, shot2, second_death())
    sec.overlays.append((F(shot + 0.5), F(shot2), lambda f, q: dict(q, hyaw=q["hyaw"] + 40 * math.sin(f * 0.25), hpitch=-25)))
    return {"cam": cam(p, (-36.9, -4.3, 1.0), 26), "actors": [fm, him, sec] + acts + dead_actors(nf),
            "sticks": [rope_stick(JA), pipe_track(fm, KILL_KEYS, t0, after=(shot, kill_pipe()))],
            "cues": [[shot, shot + 0.3, "A CRACK FROM THE SKY"], [shot + 0.5, shot + 1.2, "THE PIPE RINGS"], [shot2, shot2 + 0.3, "ANOTHER CRACK"]]}
