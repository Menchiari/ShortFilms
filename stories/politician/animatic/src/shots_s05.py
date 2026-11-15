from sh import *

CUES = {"S05_SH050": [[0, 3, "PAPER ON ASPHALT"]], "S05_SH080": [[0, 4, "HIS BREATH, FEET COMING"]]}
SQ_WALLS = [(-220, -43.5, -140, -10.5), (-220, -43.5, 10.5, 140), (-43.5, -11.5, -140, -31.5), (-43.5, -11.5, 31.5, 140),
            (11.5, 43.5, 31.5, 140), (11.5, 43.5, -140, -31.5), (43.5, 220, 10.5, 140), (43.5, 220, -140, -10.5)]
ST_WALLS = [(-220, 80, 5.5, 60), (-64.5, 80, -60, -5.5), (-220, -75.5, -60, -5.5)]
FALL = (-40.8, -8.1)

def street(eye):
    reset("day"); return sets.streets(eye)

def runners_sim(n, x0, x1, y0, y1, T, speed, target_fn, seed, walls=ST_WALLS, start=None):
    rng = np.random.default_rng(seed)
    P0 = np.stack([rng.uniform(x0, x1, n), rng.uniform(y0, y1, n)], 1)
    cr = Crowd(P0, rng.uniform(*speed, n), walls=walls, space_k=0.0, seed=seed)
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

def S05_SH010(nf):
    p0 = (-54.6, 1.6, 1.6); street(p0)
    him = Actor("him", COST["him"], nf); him.path(0, 3, [(-58, -1), (-49, -1)], "run", speed="lin", base=dict(la=(60, 10, 100)))
    case = PR.hand_prop("case", "case")
    return {"cam": move([(0, p0, (-58, -1, 1.3), 35), (3, (-45.6, 1.6, 1.6), (-49, -1, 1.3), 35)], hh=0.9, ease="lin"), "actors": [him],
            "callbacks": [PR.attach(case, him, joint=LHA, elbow=LEL)], "cues": [[0, 3, "A POT BANGS ON A RAILING, A WHISTLE"]]}

def S05_SH020(nf):
    p = (-14, 1.0, 1.6); street(p)
    him = Actor("him", COST["him"], nf); him.path(0, 3, [(-42, -1), (-33.5, -1)], "run", speed="lin", base=dict(la=(60, 10, 100)))
    fa = Actor("fat", COST["fat"], nf); fa.path(0, 3, [(-56, 0.8), (-48.5, 0.8)], "run", speed="lin")
    fr = Actor("friend", COST["friend"], nf); fr.path(0, 3, [(-57, -1.2), (-47.5, -1.2)], "run", speed="lin")
    doors = [(-52, -5.3), (-47, 5.3), (-44, -5.3), (-40, 5.3), (-37, -5.3), (-50, 5.3), (-45.5, -5.3), (-42, 5.3)]
    starts = np.array([0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6])
    P0 = np.array(doors, float)
    cr = Crowd(P0, np.full(len(P0), 3.6), walls=ST_WALLS, space_k=0.0, seed=3)
    def brain(t, P, V):
        T_ = np.stack([P[:, 0] + 20, np.clip(P[:, 1] * 0.2, -2, 2)], 1); Vd = seek(P, T_, cr.v0, 2.0); Vd[starts > t] = 0; return Vd, T_
    sim = cr.run(3.0, brain)
    acts = [him, fa, fr] + people("door", sim, nf, 5, hide_before=starts)
    return {"cam": cam(p, (-45, -0.5, 1.2), 85, hh=0.4), "actors": acts}

def S05_SH030(nf):
    p0 = (-19.5, 2.8, 1.8); street(p0)
    him = Actor("him", COST["him"], nf); him.path(0, 2, [(-26, -1), (-20, -1)], "run", speed="lin", base=dict(la=(60, 10, 100)))
    sim = runners_sim(30, -42, -32, -3.0, 3.0, 2.0, (4.0, 4.6), lambda t, P: np.stack([P[:, 0] + 20, P[:, 1]], 1), 7)
    return {"cam": move([(0, p0, (-28, -0.5, 1.2), 28), (2, (-13.5, 2.8, 1.8), (-22, -0.5, 1.2), 28)], hh=1.0, ease="lin"),
            "actors": [him] + people("c", sim, nf, 8)}

_TRIP = {}
def trip():
    if "J" in _TRIP: return _TRIP["J"]
    p = dict(BASE); p.update(gait("run", 0.3, 1.0)); p.update(x=-18.4, y=-1.0, yaw=-90.0)
    J0 = fk(p); V0 = np.zeros_like(J0); V0[:, 0] = 3.4; V0[:, 2] = 0.4
    rd = Ragdoll(J0, V0); lt = J0[LTO].copy(); la = J0[LAN].copy()
    rd.pins[LTO] = lambda t: lt if t < 0.12 else None; rd.pins[LAN] = lambda t: la if t < 0.12 else None
    rd.muscles.append(toward([LHA, RHA], lambda t, x: x[HEAD] + np.array((0.5, 0, -0.4)) if t > 0.3 else None, 8))
    _TRIP["J"] = rd.run(2.0); return _TRIP["J"]

def S05_SH040(nf):
    p = (-16.6, 2.4, 1.0); street(p)
    him = Actor("him", COST["him"], nf); him.path(0, 0.7, [(-20.6, -1.0), (-18.4, -1.0)], "run", speed="lin")
    JA = trip(); him.joints(0.7, JA)
    case = PR.hand_prop("case", "case")
    att = PR.attach(case, him, joint=LHA, elbow=LEL)
    def case_cb(f):
        t = f / core.FPS
        if t < 0.75: att(f); return
        u = min(1, (t - 0.75) / 0.45); case.hide_render = False
        x = -18.0 + 2.6 * u; z = 0.9 * (1 - u) + 1.2 * u * (1 - u) + 0.1
        PR.place(case, (x, -0.7, z), 20 + 200 * u)
    paper = PR.papers("bond", 30, (-15.4, -0.7), 0.5, 1.2, 2.0, rise=1.2, seed=3, drift=(1.0, 0.3))
    def paper_vis(f):
        paper(f)
    return {"cam": cam(p, (-17.5, -1, 0.6), 30, hh=0.8), "actors": [him], "callbacks": [case_cb, paper_vis], "cues": [[1.1, 1.5, "THE CASE BURSTS OPEN"]]}

def S05_SH060(nf):
    p = (-12.5, 2.6, 1.6); street(p)
    end = trip()[-1]
    him = Actor("him", COST["him"], nf)
    him.joints(0, [end] * F(0.3))
    stand = dict(x=-16.0, y=-0.8, yaw=90)
    him.seq([(0.3, pose("hands_knees", x=-16.0, y=-0.9, yaw=90)), (0.9, pose("stand", **stand)), (1.3, pose("throw_back", **stand)),
             (1.75, pose("throw_fwd", **stand)), (2.3, pose("stand", **stand, la=(10, 10, 20)))], blend=0.3)
    case = PR.briefcase("case_open", opened=True)
    def case_cb(f):
        t = f / core.FPS
        if t < 1.3:
            PR.place(case, (-15.2, -0.6, 0.0), 0); return
        J = him.J[min(f, him.nf - 1)]
        if t < 1.75:
            PR.place(case, tuple(J[RHA]), 90); return
        u = min(1, (t - 1.75) / 0.55); x = -16.3 - 6.0 * u; z = 1.6 * (1 - u) + 1.8 * u * (1 - u) + 0.05
        PR.place(case, (x, -0.5, z), 90 + 300 * u)
    paper = PR.papers("bond", 45, (-21.5, -0.5), 1.2, 1.8, 3.0, rise=2.6, seed=5, drift=(-1.5, 0))
    sim = runners_sim(14, -38, -30, -2.8, 2.8, 3.0, (3.6, 4.2), lambda t, P: np.stack([np.full(len(P), -21.5), P[:, 1] * 0.6], 1), 9)
    acts = people("c", sim, nf, 10)
    for a in acts[:8]:
        a.over(2.4, 3.0, **{k: v for k, v in POSES["crouch"].items()})
    return {"cam": cam(p, (-21, -0.8, 0.9), 28, hh=0.6), "actors": [him] + acts, "callbacks": [case_cb, paper]}

def square_set(eye, sky="day"):
    reset(sky); return sets.square(eye)

def S05_SH070(nf):
    p0 = (-78.5, 1.4, 1.6); square_set(p0)
    him = Actor("him", COST["him"], nf); him.path(0, 3, [(-80, -2.0), (-71.5, -2.0)], "run", speed="lin")
    him.over(1.6, 3.0, ra=(35, 25, 150), hyaw=0)
    phone = PR.hand_prop("phone", "phone")
    return {"cam": move([(0, p0, (-80, -2, 1.5), 35), (3, (-70, 1.4, 1.6), (-71.5, -2, 1.5), 35)], hh=0.9, ease="lin"), "actors": [him],
            "callbacks": [PR.attach(phone, him, visible=lambda f: f >= F(1.6))], "speakers": {}}

def S05_SH090(nf):
    p0 = (-68.8, 0.2, 1.65); square_set(p0)
    him = Actor("him", COST["him"], nf); him.path(0, 6, [(-71, -2.0), (-55, -2.5)], "run", speed="lin")
    him.over(0, 6, ra=(35, 25, 150)); him.talk(0.3, 5.7)
    sim = runners_sim(18, -112, -98, -5, 5, 6.0, (3.4, 4.0), lambda t, P: np.stack([P[:, 0] + 30, P[:, 1]], 1), 11, walls=SQ_WALLS)
    phone = PR.hand_prop("phone", "phone")
    return {"cam": move([(0, p0, (-71, -2, 1.55), 40), (6, (-52.8, -0.3, 1.65), (-55, -2.5, 1.55), 40)], hh=0.9, ease="lin"),
            "actors": [him] + people("c", sim, nf, 12), "speakers": {"OLD MAN": him}, "say": [[0.3, 5.7, "OLD MAN"]], "callbacks": [PR.attach(phone, him)]}

def S05_SH100(nf):
    p = (-51.0, -0.3, 1.6); square_set(p)
    him = Actor("him", COST["him"], nf); him.path(0, 2, [(-54.5, -2.6), (-51.8, -2.9)], "run", speed="out")
    him.over(0, 1.0, ra=(35, 25, 150)); him.over(1.0, 2.0, hroll=25, hyaw=30, spine=15, ra=(80, 30, 120))
    rock = PR._obj("rock", PR._mesh_sphere("rock", 0.07, seg=8, rings=5), "#7A6A58")
    def rock_cb(f):
        t = f / core.FPS; J = him.J[min(f, him.nf - 1)]
        if t <= 1.0:
            u = t / 1.0; s = np.array((-62.0, 0.5, 2.2)); e = J[HEAD] + np.array((-0.05, 0.05, 0.0))
            rock.location = tuple(s + (e - s) * u + np.array((0, 0, 0.8 * u * (1 - u))))
        else:
            u = min(1, (t - 1.0) / 0.5); rock.location = (J[HEAD][0] - 0.4 - 0.6 * u, J[HEAD][1] + 0.3, max(0.07, J[HEAD][2] * (1 - u)))
    phone = PR.hand_prop("phone", "phone")
    return {"cam": cam(p, (-53.2, -2.7, 1.55), 40, hh=0.8), "actors": [him], "callbacks": [rock_cb, PR.attach(phone, him, visible=lambda f: f < F(1.05))],
            "cues": [[1.0, 1.3, "CRACK OF STONE ON BONE"]]}

_FALLSQ = {}
def fall_square():
    if "J" in _FALLSQ: return _FALLSQ["J"]
    p = dict(BASE); p.update(gait("run", 2.0, 1.0)); p.update(x=-43.6, y=-6.0, yaw=fdir((-43.6, -6.0), FALL))
    J0 = fk(p); d = np.array(FALL) - np.array((-43.6, -6.0)); d /= np.linalg.norm(d)
    V0 = np.zeros_like(J0); V0[:, 0] = d[0] * 3.0; V0[:, 1] = d[1] * 3.0
    V0[HEAD] += (d[0] * 1.5, d[1] * 1.5, -0.5)
    rd = Ragdoll(J0, V0)
    rd.walls.append((-43.5, -40.0, -10.5, -7.0, 0.15))
    rd.muscles.append(toward([LHA, RHA], lambda t, x: x[HEAD] if t > 0.5 else None, 10))
    rd.muscles.append(impulse([LSH, LHIP, LEL], 0.45, (0.0, -1.2, 0.6)))
    JA = rd.run(2.5)
    end = fk(pose("lie_curl", x=FALL[0], y=FALL[1], yaw=90))
    n = len(JA); k0 = int(n * 0.55)
    for i in range(k0, n):
        u = (i - k0) / max(1, n - 1 - k0); u = u * u * (3 - 2 * u); JA[i] = JA[i] * (1 - u) + end * u
    _FALLSQ["J"] = JA; return JA

def gather_sim(n, T, seed, start_box=(-100, -70, -6, 6), arc=(-110, 190), r0=1.4, dr=0.8, speed=(3.4, 4.4), center=FALL):
    rng = np.random.default_rng(seed)
    P0 = np.stack([rng.uniform(start_box[0], start_box[1], n), rng.uniform(start_box[2], start_box[3], n)], 1)
    S = slots(center, n, r0=r0, dr=dr, arc=arc, seed=seed, spacing=0.9)
    T_ = assign(P0, S, center)
    cr = Crowd(P0, rng.uniform(*speed, n), focus=center, space_k=0.03, walls=SQ_WALLS, bubble=lambda t: (center, 1.0), seed=seed)
    look = np.repeat(np.array(center)[None], n, 0)
    def brain(t, P, V):
        return seek(P, T_, cr.v0, arrive=2.5), look
    return cr.run(T, brain)

def S05_SH110(nf):
    p = (-31.0, 9.0, 2.3); square_set(p)
    him = Actor("him", COST["him"], nf)
    him.path(0, 1.0, [(-50.5, -2.9), (-43.6, -6.0)], "run", speed="lin")
    him.joints(1.0, fall_square())
    sim = gather_sim(45, nf / core.FPS, 21, start_box=(-72, -54, -6, 6))
    acts = people("c", sim, nf, 22)
    return {"cam": cam(p, (-43, -6, 1.0), 30), "actors": [him] + acts, "cues": [[1.2, 7, "THE YELLING CLOSES IN"], [8.5, 9, "GUNSHOT"]]}
