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
    (18.0, 3.0, 9.0, 2.6, 2, "SH020"), (19.0, -0.5, 8.0, 5.4, 3, "SH020"), (16.5, 6.0, 7.5, 7.6, 4, "SH020"),
    (17.5, 1.5, 6.5, 9.3, 5, "SH020"), (15.0, 4.5, 6.0, 10.6, 6, "SH020"), (13.0, 2.2, 5.0, 1.1, 7, "SH040"), (12.0, -0.6, 4.2, 2.5, 8, "SH040")]
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

def S06_SH010(nf):
    """Medium, frontal, from the crowd's side: standing at the corner, the gun on them. They back away past the camera."""
    p = (FALL[0] - 3.6, FALL[1] + 0.4, 1.65); sq(p)
    him = standing(nf); him.talk(0.6, 2.2); him.talk(3.3, 5.6); him.face(0, 6, eyes=1.4)
    rng = np.random.default_rng(31)
    camp = np.array(p[:2]); sight = [(tuple(camp + (np.array(FALL) - camp) * u), 0.9) for u in np.linspace(0, 0.8, 7)]
    P0 = falloff(FALL, 18, r_min=1.6, lam=1.8, arc=(90, 300), seed=31, walls=SQ_WALLS, avoid=sight, max_r=14)
    d = P0 - np.array(FALL)[None]; r = np.linalg.norm(d, axis=1)
    T_ = np.array(FALL)[None] + d / r[:, None] * (6.0 + 1.5 * r)[:, None]
    cr = Crowd(P0, rng.uniform(0.9, 1.8, len(P0)), walls=SQ_WALLS, space_k=0.0, seed=33, start=rng.uniform(2.9, 4.2, len(P0)))
    look = np.repeat(np.array(FALL)[None], len(P0), 0)
    acts = people("c", cr.run(nf / core.FPS, lambda t, P, V: (seek(P, T_, cr.v0, 1.0), look)), nf, 34)
    for a in acts: a.overlays.append((0, nf, lambda f, q: dict(q, spine=q["spine"] - 6)))
    # the ones right beside the camera: shoulders at the frame edges, backing off past the lens
    for i, (dx, dy) in enumerate(((1.0, 0.62), (1.15, -0.66), (1.9, 0.95))):
        x0, y0 = p[0] + dx, p[1] + dy
        a = Actor(f"fg{i}", crowd_costume(random.Random(37 + i)), nf); yw = fdir((x0, y0), FALL)
        a.hold(0, 3.0 + 0.3 * i, pose("stand", x=x0, y=y0, yaw=yw, spine=-5))
        a.path(3.0 + 0.3 * i, 6.0, [(x0, y0), (x0 - 2.5, y0 + 0.9 * np.sign(dy))], "walk", speed="io", yaw_fixed=yw)
        acts.append(a)
    return {"cam": cam(p, (FALL[0], FALL[1], 1.55), 35, hh=0.6), "actors": [him] + acts, "speakers": {"OLD MAN": him},
            "say": [[0.6, 2.2, "OLD MAN"], [3.3, 5.6, "OLD MAN"]], "callbacks": [gun_on(him)], "cues": [[0, 1.5, "EARS RINGING, SMOKE FROM THE MUZZLE"]]}

def S06_SH020(nf):
    """Side view: the crowd still. One man yells and runs at him: shot, he drops. Another. Closer and closer together."""
    sq(SIDE[0])
    ks = [k for k in kills() if k["shot"] == "SH020"]
    him = Actor("him", COST["him"], nf)
    keys = [(0.0, pose("stand", **STAND, yaw=FACE, ra=(85, 4, 4)))]
    for k in ks:
        keys.append((k["ts"] - 0.35, pose("stand", **STAND, yaw=fdir(FALL, k["hit"]), ra=(88, 4, 4))))
        keys.append((k["ts"] + 0.15, pose("stand", **STAND, yaw=fdir(FALL, k["hit"]), ra=(98, 4, 4), spine=-4)))
    him.seq(keys)
    acts = [victim_actor(k, nf) for k in ks] + street_crowd(30, 61, nf, near=10.0, lam=3.0)
    for a in acts[len(ks):]:
        for k in ks:
            f0 = F(k["ts"]); a.overlays.append((f0, min(nf, f0 + F(0.8)), lambda f, q, f0=f0: dict(q, spine=q["spine"] - 10 * math.sin(math.pi * min(1, (f - f0) / 10)))))
    cues = [[k["ts"] - 1.2, k["ts"] - 0.6, "A YELL"] for k in ks[:2]] + [[k["ts"], k["ts"] + 0.25, f"SHOT {k['n']}"] for k in ks]
    return {"cam": cam(*SIDE, hh=0.2), "actors": [him] + acts, "callbacks": [gun_on(him)], "cues": cues}

def S06_SH030(nf):
    """Distant view, long lens: the crowd comes at him, not together: one after another."""
    p = (FALL[0] + 42.0, FALL[1] + 7.0, 1.8); sq(p)
    him = standing(nf)
    rng = np.random.default_rng(71); n = 10
    P0 = band(FALL[0] - 12, n, 4.0, -5.5, 6.0, seed=71, dirx=-1.0, walls=SQ_WALLS)
    start = np.sort(rng.uniform(0.0, 3.4, n))
    cr = Crowd(P0, rng.uniform(3.2, 5.0, n), walls=SQ_WALLS, space_k=0.0, seed=72, start=start, bubble=lambda t: (FALL, 3.5))
    T_ = np.repeat(np.array(FALL)[None], n, 0)
    acts = people("r", cr.run(nf / core.FPS, lambda t, P, V: (seek(P, T_, cr.v0, 1.0), T_)), nf, 73)
    acts += street_crowd(26, 74, nf, near=16.0) + dead_actors(nf, upto=6)
    return {"cam": cam(p, (FALL[0] - 12.0, FALL[1] + 1.5, 1.0), 85, hh=0.3), "actors": [him] + acts, "callbacks": [gun_on(him)]}

def lips(nf, word_t):
    him = Actor("him", COST["him"], nf)
    him.hold(0, nf / core.FPS, pose("stand", x=FALL[0], y=FALL[1], yaw=FACE, ra=(85, 4, 4)))
    him.compute()
    h = him.J[0, HEAD]; fwd = np.array((-1.0, 0.0, 0.0))
    p = tuple(h + fwd * 0.95 + np.array((0, 0.28, -0.08)))
    sq(p)
    him2 = Actor("him", COST["him"], nf); him2.hold(0, nf / core.FPS, pose("stand", x=FALL[0], y=FALL[1], yaw=FACE, ra=(85, 4, 4)))
    for (a, b) in word_t: him2.talk(a, b)
    return {"cam": cam(p, tuple(h + fwd * 0.1 + np.array((0, 0, -0.05))), 75, hh=0.15), "actors": [him2], "speakers": {"OLD MAN": him2}}


def S06_SH040(nf):
    """One shot, his lips: three (a shot), two (a shot), one."""
    d = lips(nf, [(0.2, 0.9), (1.6, 2.3), (3.0, 3.6)])
    d["say"] = [[0.15, 0.95, "OLD MAN"], [1.55, 2.35, "OLD MAN"], [2.95, 3.7, "OLD MAN"]]
    d["cues"] = [[1.1, 1.35, "SHOT 7"], [2.5, 2.75, "SHOT 8"]]
    return d

def S06_SH050(nf):
    """Close: eyes shut tight, the gun comes up to his temple. Click. Nothing. A second. He understands."""
    h0 = standing(nf); h0.compute(); h = h0.J[0, HEAD]
    p = tuple(h + np.array((-0.85, 0.22, 0.04))); sq(p)
    him = standing(nf)
    him.face(0.9, 3.4, eyes=0.08); him.face(3.4, 4.3, eyes=0.5); him.face(4.3, 6, eyes=1.75, mouth=0.5)
    g = PR.hand_prop("gun", "gun")
    return {"cam": cam(p, tuple(h + np.array((0, 0, -0.02))), 45, hh=0.3), "actors": [him], "callbacks": [gun_temple_cb(g, him, 0.5, 1.4)],
            "cues": [[0, 3.3, "ONLY HIS BREATHING"], [3.3, 3.6, "CLICK"], [4.3, 6, "SILENCE, THEN THE CROWD"]]}

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
