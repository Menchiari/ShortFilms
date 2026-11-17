from sh import *
from shots_s05 import SQ_WALLS, people
from shots_s07 import ARM, TOP, HELI_AT, hanging, rope_stick, bodies_s07
import phys

CUES = {"S08_SH030": [[0, 4, "CABIN HUM"]], "S08_SH070": [[1.2, 1.5, "CRACK"]]}
HELI_FAR = np.array((150.0, 240.0, 150.0))   # d8 framing (d10 note): far beyond the rooftops, buildings around it (30 m higher than d8: today's roofs)

def sq(eye, sky="sunset"):
    reset(sky); return sets.square(eye)

def cabin_set():
    reset("sunset")
    mb = core.MB((0, 0, -140), haze=(60, 600), detail=False)
    rnd = random.Random(5)
    core.ground(mb, -800, 800, -800, 800, PAL["asphalt"], z=-140, tile=80)
    for i in range(500):
        x = rnd.uniform(-500, 500); y = rnd.uniform(-500, 500); s = rnd.uniform(10, 22)
        mb.box(x, x + s, y, y + s, -140, -140 + rnd.choice([12, 18, 24, 30, 36]), rnd.choice(PAL["wall"]))
    mb.build("below")
    m2 = core.MB(None, detail=False); cream = "#D6CCB6"; wall = "#CFC6B2"; dk = "#2C2C2E"
    m2.box(-1.2, 1.2, -2.6, 3.4, -0.1, 0.0, dk); m2.box(-1.2, 1.2, -2.6, 3.4, 1.62, 1.72, wall)
    m2.box(-1.3, -1.2, -2.6, 3.4, 0.0, 0.7, wall); m2.box(-1.3, -1.2, -2.6, 3.4, 1.4, 1.62, wall)
    for y0 in (-2.6, -0.4, 1.2, 2.6):
        m2.box(-1.3, -1.2, y0, y0 + 0.25, 0.7, 1.4, wall)
    m2.box(1.2, 1.3, -2.6, -1.6, 0.0, 1.62, wall); m2.box(1.2, 1.3, 0.6, 3.4, 0.0, 0.7, wall); m2.box(1.2, 1.3, 0.6, 3.4, 1.4, 1.62, wall)
    m2.box(1.2, 1.3, 1.2, 1.45, 0.7, 1.4, wall)
    m2.box(-1.2, 1.2, -2.7, -2.6, 0.0, 1.62, wall)
    m2.box(-1.1, 1.1, -2.5, -1.9, 0.0, 0.45, cream); m2.box(-1.1, 1.1, -2.6, -2.35, 0.45, 1.15, cream)
    for x in (-0.55, 0.55):
        m2.box(x - 0.3, x + 0.3, 1.7, 2.3, 0.0, 0.45, cream); m2.box(x - 0.3, x + 0.3, 1.55, 1.72, 0.45, 0.95, cream)
    m2.box(-1.15, 1.15, 2.95, 3.4, 0.0, 0.85, dk); m2.box(-1.15, 1.15, 3.35, 3.4, 1.35, 1.62, dk)
    m2.box(-0.1, 0.1, 3.3, 3.4, 0.85, 1.62, dk)
    m2.build("cabin")

def cabin_people(nf, lady_turn=None, roger_shift=None):
    r = Actor("roger", COST["roger"], nf)
    rp = dict(x=0.5, y=-0.75, yaw=-62.0)
    keys = [(0, pose("aim", **rp, z=0.45 + 0.17))]
    if roger_shift is not None:
        keys += [(roger_shift, pose("aim", **rp, z=0.62)), (roger_shift + 0.6, pose("aim", **dict(rp, yaw=-52.0), z=0.62))]
    r.seq(keys) if len(keys) > 1 else r.hold(0, nf / core.FPS, keys[0][1])
    pl = Actor("pilot", COST["pilot"], nf); pl.hold(0, nf / core.FPS, pose("seat", x=0.55, y=2.0, yaw=0.0, z=0.6, la=(60, 8, 40), ra=(60, 8, 40)))
    la = Actor("lady", COST["lady"], nf)
    lp = dict(x=-0.55, y=2.0, z=0.58)
    if lady_turn is None:
        la.hold(0, nf / core.FPS, pose("seat", **lp, yaw=0.0))
    else:
        la.seq([(0, pose("seat", **lp, yaw=0.0)), (lady_turn, pose("seat", **lp, yaw=0.0)), (lady_turn + 0.6, pose("seat", **lp, yaw=0.0, twist=-45, hyaw=-75))])
    for a in (r, pl, la): a.compute()
    def axis(f):
        """The rifle at his right cheek, level with his eye, pointing where he looks, tipped down a little."""
        J = r.J[min(f, nf - 1)]; d = J[NOSE] - J[HEAD]; d[2] = 0; d /= (np.linalg.norm(d) + 1e-9)
        d = d * math.cos(math.radians(4)) + np.array((0, 0, -math.sin(math.radians(4))))
        right = np.cross(d, (0, 0, 1.0)); right /= np.linalg.norm(right)
        return J[HEAD] + right * 0.075 - np.array((0, 0, 0.06)) - d * 0.32, d
    def part(a, b, lift=0.0):
        def fn(f):
            s0, d = axis(f); up = np.array((0, 0, lift))
            return tuple(s0 + d * a + up), tuple(s0 + d * b + up)
        return fn
    rf = [Stick("rifle_stock", 0.03, "#1A1A1A", part(0.0, 0.8)), Stick("rifle_barrel", 0.011, "#1A1A1A", part(0.8, 1.75))]
    return r, pl, la, rf

def S08_SH010(nf):
    """d8 framing: from the street, long lens, the helicopter far beyond the rooftops, just above them."""
    p = (-38.0, -6.0, 1.7); sq(p)
    h = PR.heli("heli")
    yaw = math.degrees(math.atan2(-(p[0] - HELI_FAR[0]), p[1] - HELI_FAR[1])) - 90
    path = lambda t: (HELI_FAR + np.array((1.5 * math.sin(t * 0.7), 0.0, 0.8 * math.sin(t * 0.5))), yaw + 2 * math.sin(t * 0.4), 0.0)
    return {"cam": cam(p, tuple(HELI_FAR + np.array((0, 0, -6))), 135), "callbacks": [PR.heli_cb(h, path)], "cues": [[0, 4, "THE CROWD BELOW, NO ROTOR"]]}

CAB_CAM = ((1.4, -1.1, 1.45), (-0.35, 2.0, 1.12), 18)     # d10: a little higher, so the rifle sits lower in frame; the lady centered

def S08_SH020(nf):
    """Left: Roger's face, cheek on the stock. Center: the lady in the front seat. Right: the front half of the rifle out of frame."""
    cabin_set(); r, pl, la, rf = cabin_people(nf)
    r.face(0, 4, mouth=0.15)
    return {"cam": cam(*CAB_CAM, hh=0.12), "actors": [r, pl, la], "sticks": rf, "cues": [[0, 4, "ROTORS, MUFFLED"]]}

def S08_SH050(nf):
    cabin_set(); r, pl, la, rf = cabin_people(nf, lady_turn=0.2)
    la.talk(1.0, 2.6)
    return {"cam": cam(*CAB_CAM, hh=0.12), "actors": [r, pl, la], "sticks": rf,
            "speakers": {"BUSINESS LADY": la}, "say": [[1.0, 2.7, "BUSINESS LADY"]]}

def S08_SH060(nf):
    cabin_set(); r, pl, la, rf = cabin_people(nf, roger_shift=1.4)
    r.face(0, 0.4, mouth=0.4); r.face(0.4, 1.0, mouth=0.0, eyes=1.2); r.face(1.0, 3.0, mouth=0.0)
    J = r.J[0]
    return {"cam": cam(tuple(J[HEAD] + np.array((1.0, 0.08, 0.02))), tuple(J[HEAD]), 50, hh=0.12), "actors": [r, pl, la], "sticks": rf}

SNIPE = [(1, 0.4), (4, 0.9), (7, 1.5), (10, 2.0), (13, 2.6), (16, 3.1)]
_SK = {}
def sniper_sim(T=4.0):
    if "sim" in _SK: return _SK["sim"]
    rng = np.random.default_rng(201); n = 30
    P0 = falloff((ARM[0], ARM[1]), n, r_min=2.6, lam=2.4, arc=(100, 380), seed=202, walls=SQ_WALLS, max_r=22)
    out = P0 - ARM[:2][None]; out /= np.linalg.norm(out, axis=1)[:, None]
    T_ = P0 + out * 30
    cr = Crowd(P0, rng.uniform(3.6, 5.2, n), walls=SQ_WALLS, space_k=0.0, seed=203, start=rng.uniform(0.0, 0.8, n))
    _SK["sim"] = cr.run(T, lambda t, P, V: (seek(P, T_, cr.v0, 1.0), T_)); return _SK["sim"]

def sniper_kills():
    """The people the sniper drops in the square: where they are when hit, and the fall (MuJoCo)."""
    if "k" in _SK: return _SK["k"]
    X, Y, YW, SP = sniper_sim(); out = []
    for i, t in SNIPE:
        f = F(t)
        if math.hypot(X[f, i] - (-39.6), Y[f, i] - (-6.55)) < 4.0:
            continue
        fwd = np.array((-math.sin(math.radians(YW[f, i])), math.cos(math.radians(YW[f, i]))))
        JA = phys.death((float(X[f, i]), float(Y[f, i])), float(YW[f, i]), 3.5, speed=float(SP[f, i]), hit=(fwd[0] * 1.5, fwd[1] * 1.5, -0.8), buckle=SP[f, i] < 2.0, seed=60 + i)
        out.append((i, t, JA))
    _SK["k"] = out; return out

def sniper_dead(nf):
    acts = []
    rnd = random.Random(204); costs = [crowd_costume(rnd) for _ in range(30)]       # the same clothes as in SH040
    for i, t, JA in sniper_kills():
        a = Actor(f"sd{i}", costs[i], nf); a.joints(0, [JA[-1]] * nf); acts.append(a)
    return acts

def off_bodies(sim, keep, bodies, r=0.5, t_stand=4.0):
    """d10 body map: nobody stands on or runs over the dead. A person who comes on a body is moved off it (his whole path,
    a few decimetres); the sniper's victims (keep) are untouched, so the body map of S09 stays the same."""
    X, Y, YW, SP = [np.array(a, float).copy() for a in sim]
    pts = np.concatenate([np.asarray(b)[:, :2] for b in bodies]); fs = slice(0, F(t_stand) + 1)
    for i in range(X.shape[1]):
        if i in keep: continue
        for _ in range(4):
            d = np.hypot(pts[None, :, 0] - X[fs, i, None], pts[None, :, 1] - Y[fs, i, None])
            f, k = np.unravel_index(np.argmin(d), d.shape)
            if d[f, k] >= r: break
            v = np.array((X[f, i] - pts[k, 0], Y[f, i] - pts[k, 1])); n = np.linalg.norm(v)
            v = v / n if n > 1e-6 else np.array((1.0, 0.0))
            X[:, i] += v[0] * (r - d[f, k] + 0.05); Y[:, i] += v[1] * (r - d[f, k] + 0.05)
    return X, Y, YW, SP

def S08_SH040(nf):
    """From the street, long lens: cracks from the sky. People fall, the rest run, some fall while they run. The dead stay down."""
    p = (-22.0, 10.0, 1.6); sq(p)
    JA = hanging(nf / core.FPS, struggle=0.2, seed=21); him = Actor("him", COST["him"], nf); him.joints(0, JA)
    acts = people("c", off_bodies(sniper_sim(), {i for i, _, _ in sniper_kills()}, [a.J[-1] if a.J is not None else a.compute()[-1] for a in bodies_s07(nf)]), nf, 204)
    for i, t, JD in sniper_kills():
        acts[i].joints(t, JD)
    cues = [[t, t + 0.2, "CRACK"] for _, t, _ in sniper_kills()]
    return {"cam": cam(p, (-40.0, -7.0, 2.4), 50), "actors": [him] + acts + bodies_s07(nf), "sticks": [rope_stick(JA)], "cues": cues}

def S08_SH080(nf):
    p = (ARM[0] + 0.85, ARM[1] + 1.25, ARM[2] - 1.28); sq(p)
    def upper(f):
        t = f / core.FPS; return (tuple(ARM), tuple(ARM - np.array((0, 0, 2.2 if t < 0.4 else 1.0))))
    def lower(f):
        t = f / core.FPS
        if t < 0.4: return (tuple(ARM - np.array((0, 0, 2.2))), tuple(TOP))
        u = (t - 0.4); dz = 4.9 * u * u
        return (tuple(ARM - np.array((0, 0, 1.15 + dz))), tuple(TOP - np.array((0, 0, dz))))
    return {"cam": cam(p, (ARM[0], ARM[1], ARM[2] - 1.08), 50), "sticks": [Stick("ropeu", 0.045, "#E2CFA0", upper), Stick("ropel", 0.045, "#E2CFA0", lower)],
            "cues": [[0.35, 0.6, "SNAP"]]}
