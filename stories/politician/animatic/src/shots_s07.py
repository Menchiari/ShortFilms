from sh import *
from shots_s05 import SQ_WALLS, FALL, gather_sim, people
import phys
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


def S07_SH010(nf):
    """From far above: the mob closes over him at the corner; more keep coming from every street; the dead lie where they fell."""
    p = (-20.0, 16.0, 26.0); sq(p)
    him = Actor("him", COST["him"], nf); him.hold(0, nf / core.FPS, pose("lie_curl", x=DOWN_AT[0], y=DOWN_AT[1], yaw=90))
    rng = np.random.default_rng(81); n = 60
    P0 = falloff(DOWN_AT, n, r_min=4.0, lam=2.6, arc=(-180, 180), seed=81, walls=SQ_WALLS, max_r=24)
    S = falloff(DOWN_AT, n, r_min=0.8, lam=1.4, arc=(-180, 180), seed=82, walls=SQ_WALLS, max_r=12)
    T_ = assign(P0, S, DOWN_AT)
    cr = Crowd(P0, rng.uniform(1.5, 4.5, n), focus=DOWN_AT, space_k=0.02, walls=SQ_WALLS, bubble=lambda t: (DOWN_AT, 0.65), seed=83, start=rng.uniform(0, 1.2, n))
    look = np.repeat(np.array(DOWN_AT)[None], n, 0)
    acts = people("c", cr.run(nf / core.FPS, lambda t, P, V: (seek(P, T_, cr.v0, 2.0), look)), nf, 84)
    strikers(acts, 0.6)
    # more people arriving from the streets and the square, each at his own pace, and the ones who just watch
    m = 70
    Q0 = falloff(DOWN_AT, m, r_min=14.0, lam=9.0, arc=(-180, 180), seed=85, walls=SQ_WALLS, max_r=60)
    Q1 = falloff(DOWN_AT, m, r_min=4.0, lam=4.0, arc=(-180, 180), seed=86, walls=SQ_WALLS, max_r=30); QT = assign(Q0, Q1, DOWN_AT)
    cr2 = Crowd(Q0, rng.uniform(0.6, 3.0, m), walls=SQ_WALLS, space_k=0.0, seed=87, start=rng.uniform(0, 3.5, m))
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

def S07_SH030(nf):
    """Through heads and shoulders: they haul him up by one ankle, beside the curb. Real weight."""
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
    near = []
    for i, (x, y) in enumerate([(-37.6, -4.9), (-38.0, -5.4), (-38.6, -4.7), (-37.3, -5.6), (-38.9, -5.8)]):
        a = Actor(f"n{i}", crowd_costume(random.Random(110 + i)), nf); a.hold(0, 4, pose("stand", x=x, y=y, yaw=fdir((x, y), (ARM[0], ARM[1])), hpitch=-15)); near.append(a)
    ring = []
    for i, (x, y) in enumerate(falloff((ARM[0], ARM[1]), 22, r_min=2.0, lam=2.2, arc=(-180, 180), seed=121, walls=SQ_WALLS, max_r=18, avoid=[((-36.4, -3.6), 1.5)])):
        a = Actor(f"r{i}", crowd_costume(random.Random(130 + i)), nf); a.hold(0, 4, pose("stand", x=x, y=y, yaw=fdir((x, y), ARM[:2]))); ring.append(a)
    return {"cam": cam(p, (ARM[0], ARM[1], 2.2), 30, hh=0.7), "actors": [him] + pullers + near + ring, "sticks": [s1, s2],
            "cues": [[0.5, 3.1, "THEY HAUL HIM UP BY ONE ANKLE"]]}

def S07_SH040(nf):
    JA = hanging(nf / core.FPS, struggle=0.08, seed=11)
    head0 = JA[0][HEAD]
    p = tuple(head0 + np.array((2.1, 3.3, 0.15))); sq(p)
    him = Actor("him", COST["him"], nf); him.joints(0, JA)
    him.face(0, 1.2, eyes=0.1); him.face(1.2, 3.0, eyes=0.55)
    return {"cam": follow(him, p, lens=150, offset=(0, 0, 0), lag=0.2, joint=HEAD), "actors": [him], "sticks": [rope_stick(JA)]}

def S07_SH050(nf):
    """His upside-down view: the fat man, the pipe cocked over his shoulder. He holds it. Waits. Swings."""
    T = nf / core.FPS; hit = 3.05
    JA = hanging(T, hits=(hit,), struggle=0.15, seed=12, protect=0.2)
    sq(tuple(JA[0][HEAD]))
    fm = fat_man(nf, [(0, "stand"), (3.0, "stand")]); fm.compute()
    him = Actor("him", COST["him"], nf); him.joints(0, JA); him.hide(0, T)
    def camfn(t):
        f = min(len(JA) - 1, int(round(t * core.FPS))); J = JA[f]
        pos = J[HEAD] + (J[NOSE] - J[HEAD]) * 0.8
        return pos, np.array((PIPE_AT[0], PIPE_AT[1], 1.45)), 24, 180
    return {"cam": {"fn": camfn}, "actors": [him, fm], "sticks": [pipe_stick(fm, swing(t_swing=2.6, t_hit=hit))], "cues": [[hit, hit + 0.25, "HIT"]]}

def S07_SH060(nf):
    """Close: the pipe slams into his forearm, raised over his head."""
    hit = 0.8
    JA = hanging(nf / core.FPS, hits=(hit,), struggle=0.0, seed=16, protect=0.0)
    head0 = JA[0][HEAD]; p = tuple(head0 + np.array((-0.6, 2.3, 0.4))); sq(p)
    him = Actor("him", COST["him"], nf); him.joints(0, JA); him.face(0, 2, eyes=0.1)
    fm = fat_man(nf, [(0, "stand"), (2.0, "stand")]); fm.compute()
    return {"cam": cam(p, tuple(head0 + np.array((0.45, 0.0, 0.25))), 35, hh=0.4), "actors": [him, fm],
            "sticks": [pipe_stick(fm, swing(t_swing=0.45, t_hit=hit)), rope_stick(JA)], "cues": [[hit, hit + 0.25, "CRACK ON THE FOREARM"]]}

def S07_SH070(nf):
    """Low, looking up: the pipe high against the sky, held with both hands. A crack. He drops where he stands."""
    p = (-39.2, -4.7, 0.35); sq(p)
    shot = 1.3
    fm = fat_man(nf, [(0, "stand")]); fm.joints(shot, fat_death()); fm.compute()
    JA = hanging(nf / core.FPS, struggle=0.1, seed=13); him = Actor("him", COST["him"], nf); him.joints(0, JA)
    stick = pipe_stick(fm, lambda t: -8.0); orig = stick.fn
    def pipe(f):
        t = f / core.FPS
        if t < shot: return orig(f)
        a, b = [np.array(v) for v in orig(F(shot) - 1)]; u = min(1, (t - shot) / 0.6)
        return tuple(a + np.array((0.2, 0.3, -a[2] + 0.03)) * u), tuple(b + np.array((0.9, 0.4, -b[2] + 0.03)) * u)
    stick.fn = pipe
    return {"cam": cam(p, (PIPE_AT[0], PIPE_AT[1], 2.4), 24), "actors": [fm, him], "sticks": [stick, rope_stick(JA)],
            "cues": [[shot, shot + 0.3, "A CRACK FROM THE SKY"], [shot + 0.6, 3, "THE PIPE RINGS ON THE ASPHALT"]]}

def S07_SH080(nf):
    """High and in front: the crack, the fat man drops, the pipe rings. The crowd steps back, confused. Seconds later another man drops."""
    p = (-31.5, -1.5, 8.5); sq(p)
    shot = 0.6; shot2 = 3.6
    fm = fat_man(nf, [(0, "stand")]); fm.joints(shot, fat_death())
    JA = hanging(nf / core.FPS, struggle=0.15, seed=14); him = Actor("him", COST["him"], nf); him.joints(0, JA)
    rng = np.random.default_rng(171); n = 70
    P0 = falloff((ARM[0], ARM[1]), n, r_min=2.4, lam=3.0, arc=(-180, 180), seed=172, walls=SQ_WALLS, max_r=30)
    out = P0 - ARM[:2][None]; out /= np.linalg.norm(out, axis=1)[:, None]
    T_ = P0 + out * rng.uniform(0.6, 2.2, n)[:, None]
    cr = Crowd(P0, rng.uniform(0.6, 1.3, n), walls=SQ_WALLS, space_k=0.0, seed=173, start=shot + rng.uniform(0.3, 1.2, n))
    look = np.repeat(ARM[:2][None], n, 0)
    acts = people("c", cr.run(nf / core.FPS, lambda t, P, V: (seek(P, T_, cr.v0, 0.8), look)), nf, 174)
    for i, a in enumerate(acts):
        a.overlays.append((F(shot + 0.4), nf, lambda f, q, s=rng.uniform(-60, 60), pt=rng.uniform(-40, -10): dict(q, hyaw=q["hyaw"] + s, hpitch=pt)))
    sec = Actor("second", crowd_costume(random.Random(171)), nf); sec.hold(0, shot2, pose("stand", x=SECOND[0], y=SECOND[1], yaw=fdir(SECOND, ARM[:2]) + 180)); sec.joints(shot2, second_death())
    pipe = Stick("pipe_bar", 0.025, "#8A8A8E", lambda f: ((PIPE_AT[0] + 0.3, PIPE_AT[1] + 0.4, 1.9), (PIPE_AT[0] + 0.4, PIPE_AT[1] + 0.5, 3.0)) if f < F(shot)
                 else ((PIPE_AT[0] + 0.4, PIPE_AT[1] + 0.6, 0.03), (PIPE_AT[0] + 1.3, PIPE_AT[1] + 1.0, 0.03)))
    return {"cam": cam(p, (-40, -6.5, 3.0), 35), "actors": [fm, him, sec] + acts + dead_actors(nf), "sticks": [rope_stick(JA), pipe],
            "cues": [[shot, shot + 0.3, "A CRACK FROM THE SKY"], [shot + 0.5, shot + 1.2, "THE PIPE RINGS"], [shot2, shot2 + 0.3, "ANOTHER CRACK"]]}
