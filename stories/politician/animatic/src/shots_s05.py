from sh import *

CUES = {"S05_SH070": [[0, 4, "HIS BREATH, FEET COMING"]]}
SQ_WALLS = [(-220, -43.5, -140, -10.5), (-220, -43.5, 10.5, 140), (-43.5, -11.5, -140, -31.5), (-43.5, -11.5, 31.5, 140),
            (11.5, 43.5, 31.5, 140), (11.5, 43.5, -140, -31.5), (43.5, 220, 10.5, 140), (43.5, 220, -140, -10.5)]
ST_WALLS = [(-220, 80, 5.5, 60), (-64.5, 80, -60, -5.5), (-220, -75.5, -60, -5.5)]
FALL = (-40.8, -8.1)

def street(eye):
    reset("day"); return sets.streets(eye)

def runners_sim(n, x0, x1, y0, y1, T, speed, target_fn, seed, walls=ST_WALLS, start=None):
    rng = np.random.default_rng(seed)
    P0 = band(x1, n, max(1.5, (x1 - x0) / 4), y0, y1, seed=seed, dirx=-1.0, walls=walls)
    rank = np.argsort(np.argsort(-P0[:, 0])) / max(1, n - 1)
    cr = Crowd(P0, speed[1] - (speed[1] - speed[0]) * rank + rng.uniform(-0.15, 0.15, n), walls=walls, space_k=0.0, seed=seed)
    st = start if start is not None else np.zeros(n)
    def brain(t, P, V):
        T_ = target_fn(t, P); Vd = seek(P, T_, cr.v0, arrive=2.0); Vd[st > t] = 0
        return Vd, T_
    return cr.run(T, brain)

def people(prefix, sim, nf, seed, hide_before=None):
    acts = crowd_actors(prefix, sim, 0, nf, rnd=random.Random(seed))
    if hide_before is not None:
        for a, t in zip(acts, hide_before):
            if t > 0: a.hide(0, t)
    return acts

def square_set(eye, sky="day"):
    reset(sky); return sets.square(eye)

def gather_sim(n, T, seed, start_box=(-100, -70, -6, 6), arc=(-110, 190), r0=1.4, dr=0.8, speed=(3.4, 4.4), center=FALL):
    rng = np.random.default_rng(seed)
    P0 = band(start_box[1], n, 4.0, start_box[2], start_box[3], seed=seed, dirx=-1.0, walls=SQ_WALLS)
    S = falloff(center, n, r_min=1.3, lam=2.0, arc=arc, seed=seed, walls=SQ_WALLS, max_r=18)
    T_ = assign(P0, S, center)
    cr = Crowd(P0, rng.uniform(*speed, n), focus=center, space_k=0.03, walls=SQ_WALLS, bubble=lambda t: (center, 1.0), seed=seed)
    look = np.repeat(np.array(center)[None], n, 0)
    def brain(t, P, V):
        return seek(P, T_, cr.v0, arrive=2.5), look
    return cr.run(T, brain)


def S05_SH010(nf):
    p0 = (-54.6, 1.6, 1.6); street(p0)
    him = Actor("him", COST["him"], nf); him.path(0, 3, [(-58, -1), (-49, -1)], "run", speed="lin")
    case = PR.hand_prop("case", "case")
    return {"cam": move([(0, p0, (-58, -1, 1.3), 35), (3, (-45.6, 1.6, 1.6), (-49, -1, 1.3), 35)], hh=0.9, ease="lin"), "actors": [him],
            "callbacks": [PR.chest(case, him)], "cues": [[0, 3, "A POT BANGS ON A RAILING, A WHISTLE"]]}

DOORS = [(-52, -5.0), (-47, 5.0), (-44, -5.0), (-40, 5.0), (-37, -5.0), (-50, 5.0), (-45.5, -5.0), (-42, 5.0), (-35, 5.0), (-33, -5.0),
         (-56, 5.0), (-54, -5.0), (-38.5, 5.0), (-30, -5.0), (-48.5, -5.0), (-31.5, 5.0)]
def S05_SH020(nf):
    """Top view: him down the middle of the street; people step out of their doorways and drift toward him, each at his own pace."""
    p = (-41.0, -3.0, 30.0); street(p)
    him = Actor("him", COST["him"], nf); him.path(0, 4, [(-50, -0.6), (-36, -0.6)], "run", speed="lin")
    rng = np.random.default_rng(31); P0 = np.array(DOORS, float)
    start = rng.uniform(0.0, 2.2, len(P0)); v = rng.uniform(0.9, 2.4, len(P0))
    cr = Crowd(P0, v, walls=ST_WALLS, space_k=0.0, seed=31, start=start)
    def brain(t, P, V):
        hx = -50 + 3.5 * t; T_ = np.stack([np.full(len(P), hx + 2.0), np.zeros(len(P)) + np.clip(P[:, 1], -2.5, 2.5) * 0.4], 1)
        return seek(P, T_, cr.v0, 1.5), T_
    acts = people("door", cr.run(nf / core.FPS, brain), nf, 33)
    case = PR.hand_prop("case", "case")
    return {"cam": cam(p, (-41.0, -0.5, 0.0), 30), "actors": [him] + acts, "callbacks": [PR.chest(case, him)],
            "cues": [[0, 4, "DOORS, VOICES"]]}

def S05_SH030(nf):
    """Close on him running at the lens; the street behind fills with people, soft, none of them in step."""
    street((-17.0, -0.9, 1.7))
    him = Actor("him", COST["him"], nf); him.path(0, 3, [(-27, -0.9), (-18.5, -0.9)], "run", speed="lin")
    rng = np.random.default_rng(41); n = 30
    P0 = band(-33, n, 3.0, -3.0, 3.0, seed=41, dirx=-1.0, walls=ST_WALLS)
    cr = Crowd(P0, rng.uniform(2.2, 4.6, n), walls=ST_WALLS, space_k=0.0, seed=41, start=rng.uniform(0, 1.2, n))
    def brain(t, P, V):
        T_ = np.stack([P[:, 0] + 25, P[:, 1]], 1); return seek(P, T_, cr.v0, 2.0), T_
    acts = people("c", cr.run(nf / core.FPS, brain), nf, 42)
    case = PR.hand_prop("case", "case"); him.compute()
    def pos(t):
        f = min(nf - 1, int(round(t * core.FPS))); return np.array((him.J[f, PELVIS, 0] + 3.2, -0.6, 1.65))
    return {"cam": dof(follow(him, pos, lens=55, offset=(0, 0, 0.62), lag=0.2, hh=1.0, joint=PELVIS), (him, HEAD), 1.6), "actors": [him] + acts,
            "callbacks": [PR.chest(case, him)]}

def S05_SH040(nf):
    """He trips and goes down on the case. It stays shut. (A shape: the fall is Seedance's.)"""
    p = (-16.6, 2.4, 1.0); street(p)
    him = Actor("him", COST["him"], nf); him.path(0, 0.7, [(-20.6, -1.0), (-18.4, -1.0)], "run", speed="lin")
    him.seq([(0.7, pose("stand", x=-18.2, y=-1.0, yaw=-90, spine=35, hpitch=-20)), (1.15, pose("lie_front", x=-17.3, y=-1.0, yaw=-90)), (2.0, pose("lie_front", x=-17.3, y=-1.0, yaw=-90))])
    case = PR.hand_prop("case", "case")
    return {"cam": cam(p, (-17.5, -1, 0.6), 30, hh=0.8), "actors": [him], "callbacks": [PR.chest(case, him, out=0.24)], "cues": [[1.0, 1.3, "HE HITS THE ASPHALT"]]}

def S05_SH050(nf):
    """He gets up and runs on, the case in his arms. Behind him nobody runs together: fast walkers, a few runners, some stop."""
    p = (-9.5, 3.2, 1.7); street(p)
    him = Actor("him", COST["him"], nf)
    him.seq([(0, pose("lie_front", x=-17.3, y=-1.0, yaw=-90)), (0.5, pose("hands_knees", x=-17.0, y=-1.0, yaw=-90)), (1.0, pose("stand", x=-16.6, y=-1.0, yaw=-90))])
    him.path(1.0, 3.0, [(-16.6, -1.0), (-11.0, -0.8)], "run", speed="in")
    rng = np.random.default_rng(51); n = 26
    P0 = band(-30, n, 4.0, -3.0, 3.0, seed=51, dirx=-1.0, walls=ST_WALLS)
    cr = Crowd(P0, rng.uniform(0.8, 3.6, n), walls=ST_WALLS, space_k=0.0, seed=51, start=rng.uniform(0, 1.5, n))
    stop = rng.uniform(1.5, 4.0, n) * (rng.random(n) < 0.3) + 99 * (rng.random(n) >= 0.3)
    def brain(t, P, V):
        T_ = np.stack([P[:, 0] + 20, P[:, 1] * 0.9], 1); Vd = seek(P, T_, cr.v0, 2.0); Vd[stop < t] *= 0.15
        return Vd, np.stack([np.full(n, -14.0), np.full(n, -1.0)], 1)
    acts = people("c", cr.run(nf / core.FPS, brain), nf, 52)
    case = PR.hand_prop("case", "case")
    return {"cam": cam(p, (-17, -0.5, 1.0), 26, hh=0.7), "actors": [him] + acts, "callbacks": [PR.chest(case, him)]}

def phone_run(nf, x0, x1, look_at=None):
    p0 = (x0 + 2.2, 0.2, 1.65); square_set(p0)
    him = Actor("him", COST["him"], nf); him.path(0, nf / core.FPS, [(x0, -2.0), (x1, -2.4)], "run", speed="lin")
    case = PR.hand_prop("case", "case"); phone = PR.hand_prop("phone", "phone")
    ear = PR.at_ear(phone, him, side=1.0)
    him.compute()
    def pos(t):
        f = min(nf - 1, int(round(t * core.FPS))); return np.array((him.J[f, PELVIS, 0] + 2.2, 0.2, 1.65))
    return him, case, phone, ear, pos

def S05_SH060(nf):
    """Close, running: phone to his ear. Hello? Nothing. He looks at the screen."""
    him, case, phone, ear, pos = phone_run(nf, -80.0, -71.0)
    him.talk(0.6, 1.8); him.over(2.0, 3.0, hpitch=25, hyaw=10)
    def ph(f):
        t = f / core.FPS
        if t < 2.0: ear(f); return
        ear(f); m = phone.matrix_world.copy()
        J = him.J[min(f, nf - 1)]; fwd = J[NOSE] - J[HEAD]; fwd /= np.linalg.norm(fwd)
        u = min(1.0, (t - 2.0) / 0.4); pos_ = Vector(tuple(J[HEAD] + fwd * 0.35 - np.array((0, 0, 0.12))))
        phone.matrix_world = m.lerp(Matrix.Translation(pos_) @ m.to_3x3().to_4x4(), u)
    return {"cam": follow(him, pos, lens=40, offset=(0, 0, 0.6), lag=0.2, hh=0.9), "actors": [him], "speakers": {"OLD MAN": him}, "say": [[0.6, 1.8, "OLD MAN"]],
            "callbacks": [PR.chest(case, him), ph]}

def S05_SH080(nf):
    """Same frame: the call. Mid-sentence, a rock hits him between the phone and his ear."""
    him, case, phone, ear, pos = phone_run(nf, -71.0, -52.5)
    him.talk(0.3, 4.9); hit = 5.2
    him.over(hit, nf / core.FPS, hroll=28, hyaw=35, spine=18)
    rock = PR._obj("rock", PR._mesh_sphere("rock", 0.07, seg=8, rings=5), "#7A6A58")
    def rock_cb(f):
        t = f / core.FPS; J = him.J[min(f, him.nf - 1)]
        if t < hit - 0.5: rock.hide_render = True; return
        rock.hide_render = False
        if t <= hit:
            u = (t - hit + 0.5) / 0.5; s = J[HEAD] + np.array((-6.0, 2.0, 1.4)); e = J[HEAD] + np.array((0.0, 0.12, 0.0))
            rock.location = tuple(s + (e - s) * u)
        else:
            u = min(1, (t - hit) / 0.4); rock.location = (J[HEAD][0] - 0.3 * u, J[HEAD][1] + 0.4 + 0.3 * u, max(0.07, J[HEAD][2] * (1 - u)))
    return {"cam": follow(him, pos, lens=40, offset=(0, 0, 0.6), lag=0.2, hh=0.9), "actors": [him], "speakers": {"OLD MAN": him}, "say": [[0.3, 4.9, "OLD MAN"]],
            "callbacks": [PR.chest(case, him), PR.at_ear(phone, him, visible=lambda f: f < F(hit + 0.1)), rock_cb], "cues": [[hit, hit + 0.3, "CRACK OF STONE ON BONE"]]}

CASE_AT = (-51.2, -2.6)          # where the case falls and bursts open when the rock hits him
def S05_SH090(nf):
    """Ground level: the case hits the asphalt and bursts open."""
    p = (CASE_AT[0] + 1.3, CASE_AT[1] - 0.9, 0.12); square_set(p)
    shut = PR.briefcase("case"); open_ = PR.briefcase("case_open", opened=True)
    burst = PR.papers("bond", 24, CASE_AT, 0.25, 0.75, 2.0, rise=0.9, seed=8, drift=(0.6, 0.2), hidden_before=True)
    def cb(f):
        t = f / core.FPS
        if t < 0.7:
            u = t / 0.7; shut.hide_render = False; open_.hide_render = True
            PR.place(shut, (CASE_AT[0], CASE_AT[1], 1.0 * (1 - u * u)), 40 + 40 * u)
        else:
            shut.hide_render = True; open_.hide_render = False; PR.place(open_, (CASE_AT[0], CASE_AT[1], 0.0), 80)
        burst(f)
    return {"cam": cam(p, (CASE_AT[0], CASE_AT[1], 0.2), 28), "callbacks": [cb], "cues": [[0.7, 1.0, "THE CASE BURSTS OPEN"]]}

def S05_SH100(nf):
    """The wind takes the certificates: they lift and fly. One tumbles past the lens (the bond, shown as an inset)."""
    p = (CASE_AT[0] - 2.6, CASE_AT[1] + 0.8, 0.25); square_set(p)
    open_ = PR.briefcase("case_open", opened=True); PR.place(open_, (CASE_AT[0], CASE_AT[1], 0.0), 80)
    fly = PR.papers("bond", 70, CASE_AT, 1.2, 0.0, 3.0, rise=3.5, seed=9, drift=(-2.5, 0.8))
    return {"cam": cam(p, (CASE_AT[0] + 0.5, CASE_AT[1], 1.2), 24), "callbacks": [fly], "cues": [[0, 3, "WIND, PAPER"]]}

def S05_SH110(nf):
    """People stop and look up at the paper flying over their heads."""
    p = (-58.0, 3.2, 0.6); square_set(p)
    rng = np.random.default_rng(61); n = 22
    P0 = band(-47.0, n, 2.5, -5.0, 4.5, seed=61, dirx=-1.0, walls=SQ_WALLS)
    cr = Crowd(P0, rng.uniform(1.2, 3.0, n), walls=SQ_WALLS, space_k=0.0, seed=61, start=rng.uniform(0, 0.5, n))
    slow = rng.uniform(0.6, 1.8, n)
    def brain(t, P, V):
        T_ = np.stack([P[:, 0] + 15, P[:, 1]], 1); Vd = seek(P, T_, cr.v0, 2.0); Vd *= np.clip(1 - t / slow, 0, 1)[:, None]; return Vd, T_
    acts = people("c", cr.run(nf / core.FPS, brain), nf, 62)
    for i, a in enumerate(acts):
        a.over(float(slow[i]) * 0.7, nf / core.FPS, hpitch=-50 - rng.uniform(0, 15))
    fly = PR.papers("bond", 60, (-52.0, -1.0), 4.0, 0.0, 0.5, rise=4.5, seed=10, drift=(-1.5, 0.5))
    return {"cam": cam(p, (-50.5, -1.0, 3.2), 24, hh=0.5), "actors": acts, "callbacks": [fly]}

def S05_SH120(nf):
    """Close: he gets up from the asphalt (Seedance does the getting up)."""
    hp = (CASE_AT[0] + 0.9, CASE_AT[1] - 0.6)
    p = (hp[0] + 2.2, hp[1] + 1.2, 1.05); square_set(p)
    him = Actor("him", COST["him"], nf)
    him.seq([(0, pose("lie_front", x=hp[0], y=hp[1], yaw=-90)), (0.8, pose("hands_knees", x=hp[0], y=hp[1], yaw=-90)), (1.8, pose("kneel", x=hp[0], y=hp[1], yaw=-60)),
             (2.6, pose("stand", x=hp[0], y=hp[1], yaw=-60, spine=12, hpitch=10))], blend=0.3)
    him.face(0, 3, eyes=0.6)
    return {"cam": follow(him, p, lens=40, offset=(0, 0, -0.1), lag=0.4, hh=0.6, joint=HEAD), "actors": [him], "cues": [[0, 3, "EARS RINGING, VOICES CLOSE"]]}

def S05_SH130(nf):
    """POV: faces close in around him, slowly, from every side, while he staggers toward the corner."""
    a0 = np.array((CASE_AT[0] + 0.9, CASE_AT[1] - 0.6)); a1 = np.array(FALL)
    eye = lambda t: a0 + (a1 - a0) * min(1.0, t / 4.0) * 0.45
    square_set((a0[0], a0[1], 1.6))
    rng = np.random.default_rng(71); n = 28
    P0 = falloff(tuple(a0), n, r_min=4.0, lam=2.5, seed=71, walls=SQ_WALLS, max_r=14)
    cr = Crowd(P0, rng.uniform(0.5, 1.2, n), walls=SQ_WALLS, space_k=0.0, seed=71, start=rng.uniform(0, 1.0, n), bubble=lambda t: (eye(t), 1.6))
    def brain(t, P, V):
        c = eye(t); d = P - c[None]; r = np.linalg.norm(d, axis=1)[:, None] + 1e-6
        T_ = c[None] + d / r * 2.0; return seek(P, T_, cr.v0, 1.0), np.repeat(c[None], n, 0)
    acts = people("c", cr.run(nf / core.FPS, brain), nf, 72)
    def camfn(t):
        c = eye(t); a = math.radians(-60 + 70 * t / 4.0)
        return np.array((c[0], c[1], 1.62)), np.array((c[0] + 6 * math.cos(a), c[1] + 6 * math.sin(a), 1.5)), 30, 0
    return {"cam": {"fn": camfn, "hh": 0.8}, "actors": acts, "cues": [[0, 4, "BREATHING, THE CROWD MUTTERS"]]}

def S05_SH140(nf):
    """The corner of the square, under the street light by the sidewalk: the crowd thickens around him. A shot. They burst apart."""
    p = (-31.0, 9.0, 2.3); square_set(p)
    him = Actor("him", COST["him"], nf); him.hold(0, nf / core.FPS, pose("stand", x=FALL[0], y=FALL[1], yaw=90, spine=10))
    him.over(4.2, nf / core.FPS, ra=(170, 5, 5))
    n = 50; rng = np.random.default_rng(81)
    P0 = falloff(FALL, n, r_min=3.5, lam=3.0, arc=(-110, 200), seed=81, walls=SQ_WALLS, max_r=25)
    S = falloff(FALL, n, r_min=1.0, lam=1.6, arc=(-110, 200), seed=82, walls=SQ_WALLS, max_r=12); T_ = assign(P0, S, FALL)
    cr = Crowd(P0, rng.uniform(0.8, 2.0, n), walls=SQ_WALLS, space_k=0.03, focus=FALL, seed=81, start=rng.uniform(0, 1.5, n), bubble=lambda t: (FALL, 0.8))
    shot = 4.4; flee = rng.uniform(5, 9, n)
    def brain(t, P, V):
        if t < shot:
            return seek(P, T_, cr.v0, 2.0), np.repeat(np.array(FALL)[None], n, 0)
        d = P - np.array(FALL)[None]; r = np.linalg.norm(d, axis=1)[:, None] + 1e-6
        out = np.array(FALL)[None] + d / r * (r + flee[:, None]); cr.v0[:] = np.maximum(cr.v0, 4.0)
        return seek(P, out, cr.v0, 1.0), out
    acts = people("c", cr.run(nf / core.FPS, brain), nf, 83)
    g = PR.hand_prop("gun", "gun")
    return {"cam": cam(p, (FALL[0], FALL[1], 1.0), 30), "actors": [him] + acts, "callbacks": [PR.attach(g, him, offset=(0, 0.02, 0), visible=lambda f: f >= F(4.2))],
            "cues": [[0, 4.2, "THE YELLING CLOSES IN"], [4.4, 4.7, "GUNSHOT, INTO THE AIR"], [4.7, 6, "SCREAMS, FEET"]]}
