from sh import *
from shots_s05 import SQ_WALLS, people
from shots_s07 import ARM, TOP, HELI_AT, hanging, rope_stick, bodies_s07
import phys

CUES = {"S08_SH070": [[1.2, 1.5, "CRACK"]]}
HELI_FAR = np.array((150.0, 240.0, 160.0))   # d8 framing (d10 note): far beyond the rooftops, buildings around it; high enough (d11) that
                                              # Roger's scope sees the corner over the roofs (40 m higher than d8: today's roofs)

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

def cabin_cam(T, seed=0, push=0.07):
    """d11: handheld in the cabin, same composition: a slow drift forward and sway, plus the cabin's fine vibration."""
    P0, T0, lens = CAB_CAM; ph = np.random.default_rng(seed).uniform(0, 6.28, 9)
    def fn(t):
        u = t / max(T, 1e-6)
        drift = np.array((0.02 * math.sin(0.45 * t + ph[0]), push * (u - 0.5), 0.015 * math.sin(0.6 * t + ph[1])))
        vib = np.array([0.006 * math.sin(2 * math.pi * 9.3 * t + ph[2 + k]) + 0.003 * math.sin(2 * math.pi * 15.7 * t + ph[5 + k]) for k in range(3)])
        tg = np.array(T0) + np.array((0.05 * math.sin(0.35 * t + ph[8]), 0.0, 0.03 * math.sin(0.5 * t + ph[3])))
        return np.array(P0) + drift + vib, tg + vib * 4, lens, 0
    return {"fn": fn, "hh": 0.35}

def S08_SH020(nf):
    """Left: Roger's face, cheek on the stock. Center: the lady in the front seat. Right: the front half of the rifle out of frame.
    Handheld: a slow drift and the cabin vibration."""
    cabin_set(); r, pl, la, rf = cabin_people(nf)
    r.face(0, 4, mouth=0.15)
    return {"cam": cabin_cam(nf / core.FPS, 20), "actors": [r, pl, la], "sticks": rf, "cues": [[0, 4, "ROTORS, MUFFLED"]]}

def S08_SH050(nf):
    """Same setup as SH020, handheld: she turns over her right shoulder to him."""
    cabin_set(); r, pl, la, rf = cabin_people(nf, lady_turn=0.2)
    la.talk(1.0, 2.6)
    return {"cam": cabin_cam(nf / core.FPS, 50, push=0.05), "actors": [r, pl, la], "sticks": rf,
            "speakers": {"BUSINESS LADY": la}, "say": [[1.0, 2.7, "BUSINESS LADY"]]}

def S08_SH060(nf):
    cabin_set(); r, pl, la, rf = cabin_people(nf, roger_shift=1.4)
    r.face(0, 0.4, mouth=0.4); r.face(0.4, 1.0, mouth=0.0, eyes=1.2); r.face(1.0, 3.0, mouth=0.0)
    J = r.J[0]
    return {"cam": cam(tuple(J[HEAD] + np.array((1.0, 0.08, 0.02))), tuple(J[HEAD]), 50, hh=0.12), "actors": [r, pl, la], "sticks": rf}

# ---------------------------------------------------------------- d11 SH030: the scope POV, staged in 3D
SCOPE_AT = HELI_FAR + np.array((0.0, 0.0, -0.8))     # Roger at the open door of the helicopter of SH010
SCOPE_LENS = 600.0
HUD_D = 10.0                                          # the scope's reticle and boxes drawn on planes just in front of the lens
def _basis(pos, tgt):
    fw = np.array(tgt, float) - np.array(pos, float); fw /= np.linalg.norm(fw)
    rt = np.cross(fw, (0.0, 0.0, 1.0)); rt /= np.linalg.norm(rt); return fw, rt, np.cross(rt, fw)

def _ring(name, r0, r1, col, n=72):
    """A flat black ring (the scope's mask) in its local XY plane."""
    v = []; f = []
    for i in range(n):
        a = 2 * math.pi * i / n; v += [(r0 * math.cos(a), r0 * math.sin(a), 0.0), (r1 * math.cos(a), r1 * math.sin(a), 0.0)]
    for i in range(n):
        j = (i + 1) % n; f.append((2 * i, 2 * i + 1, 2 * j + 1, 2 * j))
    me = bpy.data.meshes.new(name); me.from_pydata(v, [], f); me.update()
    return PR._obj(name, me, col)

def S08_SH030(nf):
    """Through his scope, from the helicopter: the square far below. A thin red box frames every face; one box, upside
    down under the street light, is green. The crosshair moves from red box to red box and settles on the first man to die."""
    T = nf / core.FPS; reset("sunset"); sets.square((-32.0, -2.0, 30.0))      # the eye for haze and detail sits over the square: crisp, as through glass
    X, Y, YW, SP = sniper_sim(); n = X.shape[1]
    st = (np.repeat(X[:1], nf, 0), np.repeat(Y[:1], nf, 0), np.array([[fdir((X[0, i], Y[0, i]), ARM[:2]) for i in range(n)]] * nf), np.zeros((nf, n)))
    acts = people("c", st, nf, 204)                       # the same people, where they stand when the shooting starts
    for a in acts: a.compute()
    JA = hanging(T, struggle=0.2, seed=21); him = Actor("him", COST["him"], nf); him.joints(0, JA); him.compute()
    K = [i for i, _, _ in sniper_kills()]
    order = [K[2], K[1], next(i for i in range(n) if i not in K and math.hypot(X[0, i] - ARM[0], Y[0, i] - ARM[1]) < 9.0), K[0]]
    keys = [(0.0, order[0]), (0.75, order[0]), (1.2, order[1]), (1.8, order[1]), (2.25, order[2]), (2.8, order[2]), (3.25, order[3])]
    head = lambda i, f: acts[i].J[min(f, nf - 1)][HEAD]
    def aim(t):
        f = min(nf - 1, int(round(t * core.FPS)))
        for (ta, ia), (tb, ib) in zip(keys, keys[1:]):
            if t <= tb:
                u = (t - ta) / (tb - ta); u = u * u * (3 - 2 * u); return head(ia, f) * (1 - u) + head(ib, f) * u
        return head(keys[-1][1], f)
    def camfn(t): return SCOPE_AT, aim(t), SCOPE_LENS, 0
    def state(f):
        t = f / core.FPS; tg = aim(t); fw, rt, up = _basis(SCOPE_AT, tg); return fw, rt, up
    hh = HUD_D * 7.7 / SCOPE_LENS                          # half the frame height on the HUD plane
    mask = _ring("scope_mask", hh * 0.94, hh * 30, "#000000")
    for m in mask.data.materials:
        m.roughness = 1.0; m.metallic = 0.0; m.specular_intensity = 0.0
    def mask_cb(f):
        fw, rt, up = state(f); c = SCOPE_AT + fw * (HUD_D * 0.99)
        mask.matrix_world = Matrix(((rt[0], up[0], -fw[0], c[0]), (rt[1], up[1], -fw[1], c[1]), (rt[2], up[2], -fw[2], c[2]), (0, 0, 0, 1)))
    px = HUD_D * 36.0 / SCOPE_LENS / 1120                   # one pixel on the HUD plane
    def hair(u0, u1, v0, v1):
        def fn(f):
            fw, rt, up = state(f); c = SCOPE_AT + fw * (HUD_D * 0.995)
            return tuple(c + rt * (u0 * hh) + up * (v0 * hh)), tuple(c + rt * (u1 * hh) + up * (v1 * hh))
        return fn
    sticks = [Stick("xh1", px * 0.9, "#141414", hair(-0.94, 0.94, 0, 0)), Stick("xh2", px * 0.9, "#141414", hair(0, 0, -0.94, 0.94)),
              Stick("xp1", px * 2.6, "#141414", hair(-0.94, -0.42, 0, 0)), Stick("xp2", px * 2.6, "#141414", hair(0.42, 0.94, 0, 0)),
              Stick("xp3", px * 2.6, "#141414", hair(0, 0, -0.94, -0.42))]
    def box(get, col, name, w=0.2, h=0.25):
        def side(k):
            def fn(f):
                fw, rt, up = state(f); v = get(f) - SCOPE_AT; dep = float(v @ fw)
                if dep <= 1.0: return None, None
                c = SCOPE_AT + v * (HUD_D / dep); sw, shh = w * HUD_D / dep, h * HUD_D / dep
                C = [c - rt * sw - up * shh, c + rt * sw - up * shh, c + rt * sw + up * shh, c - rt * sw + up * shh]
                return tuple(C[k]), tuple(C[(k + 1) % 4])
            return fn
        return [Stick(f"{name}_{k}", px * 0.8, col, side(k)) for k in range(4)]
    dg = bpy.context.evaluated_depsgraph_get()
    def seen(q):                                          # a box only where the scope can see the face (not behind a roof)
        d = np.array(q) - SCOPE_AT; L = float(np.linalg.norm(d))
        return not bpy.context.scene.ray_cast(dg, Vector(SCOPE_AT), Vector(d / L), distance=L - 0.4)[0]
    for i in range(n):
        if seen(head(i, 0)): sticks += box(lambda f, i=i: head(i, f), "#E2312A", f"bx{i}")
    sticks += box(lambda f: him.J[min(f, nf - 1)][HEAD], "#2EE05A", "bxhim")
    sticks.append(rope_stick(JA))
    return {"cam": {"fn": camfn}, "actors": [him] + acts + bodies_s07(nf), "sticks": sticks, "callbacks": [mask_cb],
            "cues": [[0, T, "CABIN HUM"]]}

# d11: three kills in SH040, one every two seconds; the rest run. sniper_kills() is the body map S09 reads.
KILL_T = (1.0, 3.0, 5.0)
SH040_T = 7.0
CAM040 = ((-22.0, 10.0, 1.6), (-40.0, -7.0, 2.4), 50)
N_SQ = 30
_SK = {}

def dead_before():
    """Final poses of everyone already dead when the sniper starts (S06 kills, the fat man, the second man)."""
    if "before" not in _SK:
        _SK["before"] = [a.J[-1] if a.J is not None else a.compute()[-1] for a in bodies_s07(2)]
    return _SK["before"]

def _boxes(bodies, pad=0.3):
    return [(float(J[:, 0].min()) - pad, float(J[:, 0].max()) + pad, float(J[:, 1].min()) - pad, float(J[:, 1].max()) + pad) for J in bodies]

def sniper_sim(T=SH040_T):
    """The crowd around the corner when the shooting starts: a few already running, most bolt at the first crack,
    some freeze until the second. They run around the dead, never over them."""
    if "sim" in _SK: return _SK["sim"]
    rng = np.random.default_rng(201); n = N_SQ; W = SQ_WALLS + _boxes(dead_before())
    P0 = falloff((ARM[0], ARM[1]), n, r_min=2.6, lam=2.4, arc=(100, 380), seed=202, walls=W, max_r=22)
    out = P0 - ARM[:2][None]; out /= np.linalg.norm(out, axis=1)[:, None]
    # each runs for the open way out that lies most away from the corner: the west street, the square, the south street
    EX = [lambda: (-85.0, rng.uniform(-6, 6)), lambda: (rng.uniform(-15, 25), rng.uniform(-12, 18)), lambda: (rng.uniform(-8, 8), -70.0),
          lambda: (rng.uniform(-8, 8), 70.0)]
    T_ = np.zeros_like(P0)
    for i in range(n):
        opts = [np.array(e()) for e in EX]
        sc = [float((o - P0[i]) @ out[i]) / np.linalg.norm(o - P0[i]) + rng.uniform(0, 0.5) for o in opts]
        T_[i] = opts[int(np.argmax(sc))]
    st = KILL_T[0] + rng.uniform(0.15, 0.9, n)
    u = rng.random(n); st[u < 0.25] = rng.uniform(0.0, 0.6, n)[u < 0.25]; st[u > 0.7] = KILL_T[1] + rng.uniform(0.1, 0.9, n)[u > 0.7]
    cr = Crowd(P0, rng.uniform(3.0, 5.2, n), walls=W, space_k=0.0, seed=203, start=st)
    X, Y, YW, SP = cr.run(T, lambda t, P, V: (seek(P, T_, cr.v0, 1.0), T_))
    for i in range(n):                      # before he runs, he faces the man on the rope
        for f in range(min(len(X), F(st[i]))):
            YW[f, i] = fdir((X[f, i], Y[f, i]), ARM[:2])
    _SK["sim"] = (X, Y, YW, SP); _SK["start"] = st; return _SK["sim"]

def _hidden(XS, YS, i, r=0.55):
    """Someone stands between the lens and person i."""
    c = np.array(CAM040[0][:2]); v = np.array((XS[i], YS[i])) - c; L = np.linalg.norm(v); v /= L
    for j in range(len(XS)):
        if j == i: continue
        w = np.array((XS[j], YS[j])) - c; a = float(w @ v)
        if 0.5 < a < L - 0.4 and abs(float(w[0] * v[1] - w[1] * v[0])) < r: return True
    return False

def _in_view(x, y, margin=0.75):
    p, t, lens = CAM040; v = np.array(t[:2]) - np.array(p[:2]); v /= np.linalg.norm(v)
    d = np.array((x - p[0], y - p[1])); dist = np.linalg.norm(d)
    ang = math.degrees(math.acos(max(-1.0, min(1.0, float(d @ v) / dist))))
    return ang < math.degrees(math.atan(18.0 / lens)) * margin and 8.0 < dist < 45.0, ang

def sniper_kills():
    """The three people the sniper drops (one every two seconds): each is in the long lens when hit, away from the
    man on the rope, and falls clear of every body already down (MuJoCo). Returns [(agent, time, joints)]."""
    if "k" in _SK: return _SK["k"]
    X, Y, YW, SP = sniper_sim(); out = []
    down = [J[:, :2] for J in dead_before()]
    for t in KILL_T:
        f = F(t); cand = []
        for i in range(X.shape[1]):
            if any(i == o[0] for o in out): continue
            x, y = float(X[f, i]), float(Y[f, i]); ok, ang = _in_view(x, y)
            if not ok or math.hypot(x - ARM[0], y - ARM[1]) < 4.0: continue
            if min(float(np.min(np.hypot(D[:, 0] - x, D[:, 1] - y))) for D in down) < 2.0: continue
            spread = min([math.hypot(x - float(X[F(o[1]), o[0]]), y - float(Y[F(o[1]), o[0]])) for o in out] + [9.0])
            if _hidden(X[f], Y[f], i): continue
            dist = math.hypot(x - CAM040[0][0], y - CAM040[0][1])
            cand.append((ang + 0.15 * dist - 1.0 * min(spread, 9.0) - (4.0 if (t > KILL_T[0] and SP[f, i] > 2.5) else 0.0), i))   # near, central, the later ones running
        for _, i in sorted(cand):
            fwd = np.array((-math.sin(math.radians(YW[f, i])), math.cos(math.radians(YW[f, i]))))
            JA = phys.death((float(X[f, i]), float(Y[f, i])), float(YW[f, i]), 3.5, speed=float(SP[f, i]),
                            hit=(fwd[0] * 1.5, fwd[1] * 1.5, -0.8), buckle=SP[f, i] < 2.0, seed=60 + i)
            E = JA[-1]
            if min(float(np.min(np.hypot(D[:, None, 0] - E[None, :, 0], D[:, None, 1] - E[None, :, 1]))) for D in down) < 0.8:
                continue
            if any(((E[:, 0] > x0 - 0.15) & (E[:, 0] < x1 + 0.15) & (E[:, 1] > y0 - 0.15) & (E[:, 1] < y1 + 0.15)).any() for (x0, x1, y0, y1) in SQ_WALLS):
                continue                                    # never into a facade
            out.append((i, t, JA)); down.append(E[:, :2]); break
    _SK["k"] = out; return out

def sniper_dead(nf):
    acts = []
    rnd = random.Random(204); costs = [crowd_costume(rnd) for _ in range(N_SQ)]       # the same clothes as in SH040
    for i, t, JA in sniper_kills():
        a = Actor(f"sd{i}", costs[i], nf); a.joints(0, [JA[-1]] * nf); acts.append(a)
    return acts

def off_bodies(sim, keep, bodies, r=0.5):
    """Nobody stands on or runs over the dead. bodies: [(final joints, time it lies there)]. A person who comes on a
    body is moved off it (his whole path, a few decimetres); the sniper's victims (keep) are untouched."""
    X, Y, YW, SP = [np.array(a, float).copy() for a in sim]
    for i in range(X.shape[1]):
        if i in keep: continue
        for _ in range(4):
            worst = None
            for J, t0 in bodies:
                f0 = F(t0); d = np.hypot(J[None, :, 0] - X[f0:, i, None], J[None, :, 1] - Y[f0:, i, None])
                if d.size == 0: continue
                f, k = np.unravel_index(np.argmin(d), d.shape)
                if d[f, k] < r and (worst is None or d[f, k] < worst[0]): worst = (d[f, k], f0 + f, J[k])
            if worst is None: break
            dd, f, q = worst; v = np.array((X[f, i] - q[0], Y[f, i] - q[1])); n = np.linalg.norm(v)
            v = v / n if n > 1e-6 else np.array((1.0, 0.0))
            X[:, i] += v[0] * (r - dd + 0.05); Y[:, i] += v[1] * (r - dd + 0.05)
    return X, Y, YW, SP

def S08_SH040(nf):
    """From the street, long lens: a crack from the sky, then another every two seconds. Three people drop, one after
    another; the rest run. The dead stay down."""
    p, tgt, lens = CAM040; sq(p)
    JA = hanging(nf / core.FPS, struggle=0.2, seed=21); him = Actor("him", COST["him"], nf); him.joints(0, JA)
    K = sniper_kills()
    bodies = [(J, 0.0) for J in dead_before()] + [(JD[-1], t + 1.0) for _, t, JD in K]
    acts = people("c", off_bodies(sniper_sim(), {i for i, _, _ in K}, bodies), nf, 204)
    for i, t, JD in K:
        acts[i].joints(t, JD); acts[i].joints(t + (len(JD) - 1) / core.FPS, [JD[-1]] * (nf + 1))
    cues = [[t, t + 0.2, "CRACK"] for _, t, _ in K]
    return {"cam": cam(p, tgt, lens), "actors": [him] + acts + bodies_s07(nf), "sticks": [rope_stick(JA)], "cues": cues}

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
