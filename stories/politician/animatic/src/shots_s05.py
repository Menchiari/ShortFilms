from sh import *
import mjdoll as M

CUES = {"S05_SH070": [[0, 4, "HIS BREATH, FEET COMING"]]}
SQ_WALLS = [(-220, -43.5, -140, -10.5), (-220, -43.5, 10.5, 140), (-43.5, -11.5, -140, -31.5), (-43.5, -11.5, 31.5, 140),
            (11.5, 43.5, 31.5, 140), (11.5, 43.5, -140, -31.5), (43.5, 220, 10.5, 140), (43.5, 220, -140, -10.5)]
ST_WALLS = [(-220, 80, 5.5, 60), (-64.5, 80, -60, -5.5), (-220, -75.5, -60, -5.5)]
FALL = (-40.8, -8.1)
CASE_AT = (-51.2, -2.6)          # where the case falls and bursts open when the rock hits him (S09 finds it here)
V_RUN = 3.6                      # his running speed in S05 (m/s)

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
FAR = [(-57.0, -1.8), (-56.5, 2.2), (-27.0, 2.6), (-26.5, -1.4), (-58.5, 4.6), (-25.0, -4.6)]   # down the street, already out
def S05_SH020(nf):
    """Top view: him down the middle of the street. People step out of their doorways and move slowly around him and toward him,
    each at his own pace; he runs through them and they step aside. In the last second only the distant ones speed up, never the close ones."""
    p = (-41.0, -3.0, 30.0); street(p); T = nf / core.FPS
    hx = lambda t: -50.0 + 3.5 * min(max(t, 0.0), 4.0)
    him = Actor("him", COST["him"], nf); him.path(0, 4, [(-50, -0.6), (-36, -0.6)], "run", speed="lin")
    rng = np.random.default_rng(31); P0 = np.array(DOORS + FAR, float); n = len(P0)
    start = np.concatenate([rng.uniform(0.0, 1.8, len(DOORS)), rng.uniform(0.0, 0.5, len(FAR))])
    slow = rng.uniform(0.45, 0.9, n); fast = rng.uniform(2.2, 3.2, n)
    a = rng.uniform(0, 2 * math.pi, n); r = rng.uniform(2.6, 5.0, n); off = np.stack([np.cos(a) * r, np.sin(a) * r * 0.8], 1)
    cr = Crowd(P0, slow.copy(), walls=ST_WALLS, space_k=0.0, seed=31, start=start, life=0.1, bubble=lambda t: ((hx(t), -0.6), 1.3))
    sstep = lambda u: np.clip(u, 0, 1) ** 2 * (3 - 2 * np.clip(u, 0, 1))
    def brain(t, P, V):
        H = np.array((hx(t), -0.6)); T_ = H[None] + off
        d = np.linalg.norm(P - H[None], axis=1)
        cr.v0[:] = slow + (fast - slow) * sstep((t - (T - 1.3)) / 0.6) * sstep((d - 7.0) / 4.0)     # the far ones hurry at the end
        return seek(P, T_, cr.v0, 2.0), np.repeat(H[None], n, 0)
    acts = people("door", cr.run(T, brain), nf, 33)
    case = PR.hand_prop("case", "case")
    return {"cam": cam(p, (-41.0, -0.5, 0.0), 30), "actors": [him] + acts, "callbacks": [PR.chest(case, Glide(him))],
            "cues": [[0, 4, "DOORS, VOICES"]]}

def along_arm(a, f, fwd_off=0.02, kick=0.0):
    """World matrix for a pistol in his right hand (local: barrel +y, top +z, origin at the top of the grip):
    the barrel along his forearm, so it points where his arm points; kick (deg) flips the muzzle up (recoil)."""
    J = a.J[min(f, a.nf - 1)]
    y = J[RHA] - J[REL]; y = y / (np.linalg.norm(y) + 1e-9)
    up = J[NECK] - J[PELVIS]; up = up / (np.linalg.norm(up) + 1e-9)
    if abs(np.dot(y, up)) > 0.8:                                       # arm straight up: the top of the slide faces back
        fw = J[NOSE] - J[HEAD]; fw[2] = 0; up = -fw / (np.linalg.norm(fw) + 1e-9)
    z = up - y * np.dot(up, y); z = z / (np.linalg.norm(z) + 1e-9); x = np.cross(y, z)
    R = np.stack([x, y, z], 1)
    if kick: R = R @ core.rotx(math.radians(kick))
    return Puppet.M(R, J[RHA] + y * fwd_off)

def gun_along_arm(o, a, visible=None):
    """A hand prop gun (PR.hand_prop "gun") held along his arm, wherever the arm points."""
    def cb(f):
        if visible is not None and not visible(f): o.hide_render = True; return
        o.hide_render = False; o.matrix_world = along_arm(a, f)
    return cb

def arm_sticks(a, prefix="him"):
    """His arms for the shape (which has none): upper arm in the shirt, forearm and hand in skin, both sides (as S04 does for the fat man)."""
    c = a.c; out = []
    for side, (sh_, el_, ha_) in (("r", (RSH, REL, RHA)), ("l", (LSH, LEL, LHA))):
        J = lambda f: a.J[min(f, a.nf - 1)]
        out.append(Stick(f"{prefix}_{side}ua", 0.048, c["shirt"], lambda f, s_=sh_, e_=el_: (tuple(J(f)[s_]), tuple(J(f)[e_]))))
        out.append(Stick(f"{prefix}_{side}fa", 0.04, c["skin"], lambda f, e_=el_, h_=ha_: (tuple(J(f)[e_]), tuple(J(f)[h_]))))
        def hand(f, e_=el_, h_=ha_):
            j = J(f); d = j[h_] - j[e_]; d = d / (np.linalg.norm(d) + 1e-9); return tuple(j[h_] - d * 0.02), tuple(j[h_] + d * 0.07)
        out.append(Stick(f"{prefix}_{side}ha", 0.042, c["skin"], hand))
    return out

class Glide:
    """His joints as the shape draws them (gait bob smoothed out, as ShapePuppet.smooth): props and the camera ride on the shape, not on the bob."""
    def __init__(self, a):
        if a.J is None: a.compute()
        J = a.J; k = 3; Jg = J.copy()
        pad = np.concatenate([J[:1].repeat(k, 0), J, J[-1:].repeat(k, 0)])
        z = np.mean([pad[i:i + len(J), :, 2] for i in range(2 * k + 1)], axis=0)
        moving = (np.abs(J[:, PELVIS, 2] - z[:, PELVIS]) < 0.12) & ~a.K
        Jg[moving, :, 2] = z[moving]
        self.J = Jg; self.nf = a.nf; self.K = a.K

def phone_cb(phone, him, nf, t_out, t_ear, t_look):
    """The phone: out of his right pocket (t_out), pressed to his right ear (t_ear), brought in front of his eyes (t_look)."""
    ear = PR.at_ear(phone, him, side=1.0)
    def cb(f):
        t = f / core.FPS; J = him.J[min(f, him.nf - 1)]
        if t < t_out: phone.hide_render = True; return
        ear(f); m_ear = phone.matrix_world.copy()
        up = J[NECK] - J[PELVIS]; up /= np.linalg.norm(up); fwd = J[NOSE] - J[HEAD]; fwd -= up * np.dot(fwd, up); fwd /= np.linalg.norm(fwd)
        right = np.cross(fwd, up)
        if t < t_ear:
            u = (t - t_out) / (t_ear - t_out); u = u * u * (3 - 2 * u)
            pocket = Matrix.Translation(Vector(tuple(J[RHIP] + right * 0.12 + fwd * 0.05))) @ m_ear.to_3x3().to_4x4()
            phone.matrix_world = pocket.lerp(m_ear, u); return
        if t >= t_look:
            u = min(1.0, (t - t_look) / 0.4); u = u * u * (3 - 2 * u)
            tl = up * math.cos(0.5) - fwd * math.sin(0.5)                       # the screen turned to his eyes, tilted back
            screen = Puppet.M(np.stack([right, np.cross(tl, right), tl], 1), J[HEAD] + fwd * 0.3 + right * 0.04 - up * 0.07)
            phone.matrix_world = m_ear.lerp(screen, u)
    return cb

def S05_SH030(nf):
    """Close on him running at the lens; the street behind fills with people, soft, none in step. The phone: Hello? Hello?! He looks at the screen."""
    street((-17.0, -0.9, 1.7)); T = nf / core.FPS
    him = Actor("him", COST["him"], nf); him.path(0, T, [(-33.0, -0.9), (-33.0 + V_RUN * T, -0.9)], "run", speed="lin")
    him.talk(2.0, 2.6); him.talk(2.8, 3.4); him.over(3.8, T, hpitch=24, hyaw=6)
    rng = np.random.default_rng(41); n = 38
    P0 = band(-40.0, n, 3.2, -3.0, 3.0, seed=41, dirx=-1.0, walls=ST_WALLS)
    cr = Crowd(P0, rng.uniform(2.0, 4.3, n), walls=ST_WALLS, space_k=0.0, seed=41, start=rng.uniform(0, 2.6, n))
    def brain(t, P, V):
        T_ = np.stack([P[:, 0] + 25, P[:, 1]], 1); return seek(P, T_, cr.v0, 2.0), T_
    acts = people("c", cr.run(T, brain), nf, 42)
    case = PR.hand_prop("case", "case"); phone = PR.hand_prop("phone", "phone"); g = Glide(him)
    def pos(t):
        f = min(nf - 1, int(round(t * core.FPS))); return np.array((g.J[f, PELVIS, 0] + 3.2, -0.6, 1.65))
    return {"cam": dof(follow(g, pos, lens=55, offset=(0, 0, 0.62), lag=0.2, hh=1.0, joint=PELVIS), (g, HEAD), 1.6), "actors": [him] + acts,
            "speakers": {"OLD MAN": him}, "say": [[2.0, 2.6, "OLD MAN"], [2.8, 3.4, "OLD MAN"]],
            "callbacks": [PR.chest(case, g), phone_cb(phone, g, nf, 1.3, 1.8, 3.7)], "cues": [[3.4, 3.8, "NOTHING ON THE LINE"]]}

# S05 SH040, SH050, SH060 and SH100 are cut in draft 10 (the phone moved into SH030); their functions stay for reference.
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

# ---------------------------------------------------------------- the rock (SH080) and the case (SH090): one fall, two angles
HIT_T = 4.7                      # SH080: the rock hits (s into the shot); the physics starts here, the blow lands 0.04 s later
HIT_DT = 1 / 12                  # the blow lands one frame after the physics takes over: that frame shows the rock at his brow
_RF = {}

def case_rel(tau):
    """The case after the blow (tau s): centre offset from where it left his chest, tumble angle (rad), burst open.
    Flung forward with his speed, it slams on an edge, bounces, lands flat and bursts open, slides to a stop."""
    g = 9.81; z0 = 1.45; v0 = np.array((V_RUN + 1.8, -0.45, -1.2))   # flung forward, down and to his right by the blow
    t1 = (v0[2] + math.sqrt(v0[2] ** 2 + 2 * g * (z0 - 0.17))) / g
    p1 = np.array((v0[0] * t1, v0[1] * t1, 0.17 - z0)); v1 = np.array((v0[0] * 0.6, v0[1] * 0.6, -0.35 * (v0[2] - g * t1)))
    t2 = (v1[2] + math.sqrt(v1[2] ** 2 + 2 * g * 0.09)) / g
    p2 = p1 + np.array((v1[0] * t2, v1[1] * t2, -0.09 - 0.17 + 0.17)); v2 = v1[:2] * 0.5; slide = 0.3
    if tau < t1:
        return np.array((v0[0] * tau, v0[1] * tau, v0[2] * tau - g / 2 * tau * tau)), 12.0 * tau, False, (t1, t1 + t2)
    if tau < t1 + t2:
        s = tau - t1; return p1 + np.array((v1[0] * s, v1[1] * s, v1[2] * s - g / 2 * s * s)), 12.0 * t1 - 7.0 * s, False, (t1, t1 + t2)
    s = min(slide, tau - t1 - t2); d = v2 * (s - s * s / (2 * slide))
    return np.array((p2[0] + d[0], p2[1] + d[1], 0.0)), 0.0, True, (t1, t1 + t2)

def rock_fall():
    """MuJoCo: running at V_RUN, the rock hits his right eyebrow: the head snaps to his left, the knees go, he drops face down."""
    if "JA" in _RF: return _RF
    end = case_rel(5.0)[0]
    rel = np.array((CASE_AT[0] - end[0], CASE_AT[1] - end[1]))          # where the case leaves his chest
    x0 = rel - np.array((0.2 + V_RUN * HIT_DT, 0.0))                     # his pelvis when the physics starts (running east, yaw -90)
    d = M.Doll()
    q = {"lhip_x": 35, "rhip_x": -12, "lkn_x": -55, "rkn_x": -25, "waist_x": -8, "lsh_x": 45, "lel_x": 95, "lsh_y": 10,
         "rsh_x": 60, "rsh_y": -60, "rel_x": 140}
    d.place((float(x0[0]), float(x0[1]), 1.004 + 0.06), yaw=-90, q=q, vel=(V_RUN, 0, 0.3))
    dv = np.array((-0.5, 0.85, 0.2)); dv /= np.linalg.norm(dv)
    def ctrl(t, dd):
        if t < HIT_DT: return {k: (val, 60) for k, val in q.items()}
        if t < 0.7:
            u = min(1.0, (t - HIT_DT) / 0.3)
            return {"lkn_x": (-80 * u, 22), "rkn_x": (-60 * u, 22), "lhip_x": (40 * u, 12), "rhip_x": (30 * u, 12), "waist_x": (-10, 8)}
        return {"lkn_x": (-25, 4), "rkn_x": (-15, 4), "lhip_x": (15, 3), "rhip_x": (10, 3)}
    forces = lambda t, dd: [("head", dv * 700.0)] if HIT_DT <= t < HIT_DT + 0.04 else []
    JA = d.run(4.0, ctrl=ctrl, tone=1.5, forces=forces)
    _RF.update(JA=JA, x0=x0, rel=rel, land=JA[-1, PELVIS, :2].copy(), land_yaw=fdir(JA[-1, PELVIS], JA[-1, HEAD]))
    return _RF

def flying_case(tau_fn):
    """The thrown case: closed while it flies (centre at the computed point, tumbling forward), open once it bursts. tau_fn(f) -> tau or None."""
    shut = PR.briefcase("case_fly"); open_ = PR.briefcase("case_open", opened=True); rf = rock_fall()
    def cb(f):
        tau = tau_fn(f)
        if tau is None or tau < 0:
            shut.hide_render = True; open_.hide_render = True; return
        p, pitch, opened, _ = case_rel(tau)
        if opened:
            shut.hide_render = True; open_.hide_render = False; PR.place(open_, (CASE_AT[0], CASE_AT[1], 0.0) if tau > 3 else (rf["rel"][0] + p[0], rf["rel"][1] + p[1], 0.0), -80); return
        shut.hide_render = False; open_.hide_render = True
        R = Matrix.Rotation(math.radians(-90), 4, "Z") @ Matrix.Rotation(-pitch, 4, "X")
        shut.matrix_world = Matrix.Translation(Vector((rf["rel"][0] + p[0], rf["rel"][1] + p[1], 1.45 + p[2]))) @ R @ Matrix.Translation(Vector((0, 0, -0.17)))
    return cb

def S05_SH080(nf):
    """Same frame as SH030, closer and shakier: the call. A rock slams into his right eyebrow: the head snaps, he drops (MuJoCo)."""
    rf = rock_fall(); x0 = rf["x0"]; T = nf / core.FPS; xs = x0[0] - V_RUN * HIT_T
    square_set((x0[0] + 2.0, x0[1], 1.6))
    him = Actor("him", COST["him"], nf); him.path(0, HIT_T, [(xs, x0[1]), (x0[0], x0[1])], "run", speed="lin"); him.joints(HIT_T, rf["JA"])
    him.talk(0.3, 4.4)
    rng = np.random.default_rng(81); n = 34
    P0 = band(xs - 6.0, n, 3.5, -6.0, 6.0, seed=81, dirx=-1.0, walls=SQ_WALLS)
    cr = Crowd(P0, rng.uniform(2.3, 4.2, n), walls=SQ_WALLS, space_k=0.0, seed=81, start=rng.uniform(0, 2.0, n))
    gap = rng.uniform(2.5, 7.0, n)
    def brain(t, P, V):
        hx = xs + V_RUN * min(t, HIT_T) if t < HIT_T + 0.5 else rf["land"][0]
        T_ = np.stack([np.minimum(P[:, 0] + 25, hx - gap), P[:, 1]], 1); return seek(P, T_, cr.v0, 3.0), np.stack([np.full(n, hx), np.full(n, x0[1])], 1)
    acts = people("c", cr.run(T, brain), nf, 82)
    case = PR.hand_prop("case", "case"); phone = PR.hand_prop("phone", "phone"); g = Glide(him)
    t_imp = F(HIT_T) / core.FPS + HIT_DT
    # the rock: from his front right, a streak in the last frames, a hit on the right eyebrow, then it drops
    rock = PR._obj("rock", PR._mesh_sphere("rock", 0.045, seg=8, rings=5), "#6E5E4C")
    J0 = rf["JA"][1]; brow = J0[HEAD] + np.array((0.135, -0.05, 0.04))
    d_in = np.array((-0.45, 0.88, -0.05)); d_in /= np.linalg.norm(d_in); vr = 16.0
    def rock_cb(f):
        t = f / core.FPS
        if t < t_imp - 0.3: rock.hide_render = True; return
        rock.hide_render = False
        if t < t_imp - 0.01:
            rock.hide_render = True; return
        if t < t_imp + 0.01:
            p = brow - d_in * 0.1; rock.location = tuple(p)                  # the frame of the blow: at his brow, a streak behind it
            q = Vector(tuple(d_in)).to_track_quat("Z", "Y"); rock.rotation_mode = "QUATERNION"; rock.rotation_quaternion = q
            rock.scale = (1, 1, 3.0)
        else:
            s = t - t_imp; v = np.array((1.2, -1.6, 1.6)); p = brow + v * s + np.array((0, 0, -4.9 * s * s))
            rock.location = (p[0], p[1], max(0.045, p[2])); rock.scale = (1, 1, 1)
    # blood from the eyebrow: a few drops flung to his left at the blow
    drops = [PR._obj(f"drop{i}", PR._mesh_sphere(f"drop{i}", 0.012, seg=6, rings=4), "#7A1612") for i in range(8)]
    dvs = np.random.default_rng(5).normal((-0.6, 1.6, 0.9), 0.5, (8, 3))
    def blood_cb(f):
        s = f / core.FPS - t_imp
        for o, v in zip(drops, dvs):
            o.hide_render = not (0 <= s < 0.6)
            if 0 <= s: p = brow + v * s + np.array((0, 0, -4.9 * s * s)); o.location = (p[0], p[1], max(0.01, p[2]))
    # the phone flies off his ear
    ear = PR.at_ear(phone, g, side=1.0)
    def phone_fly(f):
        s = f / core.FPS - t_imp
        if s < 0: ear(f); return
        J = rf["JA"][1]; p0 = J[HEAD] + np.array((0, -0.12, 0)); v = np.array((1.8, -1.2, 2.2))
        p = p0 + v * s + np.array((0, 0, -4.9 * s * s)); phone.location = (p[0], p[1], max(0.006, p[2]))
        phone.rotation_euler = (s * 14, s * 9, s * 5)
    tau_fn = lambda f: (f / core.FPS - t_imp) if f / core.FPS >= t_imp - 0.01 else None
    # the camera: close in front of him, running backwards, shaking; it lurches at the blow, slows and tilts down to him on the ground
    ph = np.random.default_rng(8).uniform(0, 6.28, 6)
    def camfn(t):
        f = min(nf - 1, int(round(t * core.FPS))); fl = max(0, f - 1)
        w = 0.4 * min(1.0, max(0.0, t - t_imp - 0.2) / 0.3); head = (1 - w) * g.J[fl, HEAD] + w * g.J[fl, PELVIS]; xh = xs + V_RUN * min(t, HIT_T); cx = xh + 2.1
        s = t - HIT_T
        if s > 0:
            cx = xs + V_RUN * HIT_T + 2.1 + V_RUN * (min(s, 1.5) - min(s, 1.5) ** 2 / 3.0)
        cz = 1.66 - 0.36 * min(1.0, max(0.0, s) / 1.1)
        bob = np.array((0, 0.03 * math.sin(2 * math.pi * 1.4 * t + ph[0]), 0.04 * math.sin(2 * math.pi * 2.8 * t + ph[1])))
        pos = np.array((cx, x0[1] + 0.05, cz)) + bob
        tgt = head + np.array((0, 0, -0.02)) + np.array((0, 0.035 * math.sin(2 * math.pi * 0.9 * t + ph[2]), 0.025 * math.sin(2 * math.pi * 1.7 * t + ph[3])))
        k = t - t_imp
        if k > 0:
            j = math.exp(-k / 0.18) * math.sin(38 * k); tgt = tgt + np.array((0, 0.14 * j, 0.1 * j))
        return pos, tgt, 50, 0
    cam_spec = dof({"fn": camfn, "hh": 1.6}, (g, HEAD), 1.8)
    return {"cam": cam_spec, "actors": [him] + acts, "speakers": {"OLD MAN": him}, "say": [[0.3, 4.4, "OLD MAN"]],
            "callbacks": [PR.chest(case, g, visible=lambda f: f / core.FPS < t_imp - 0.01), flying_case(tau_fn), phone_fly, rock_cb, blood_cb],
            "cues": [[t_imp, t_imp + 0.3, "CRACK OF STONE ON BONE"], [t_imp + 0.6, t_imp + 0.9, "HE HITS THE ASPHALT"]]}

SH090_TAU = 0.15                 # SH090 starts this long after the blow
SH090_CAM = ((-52.0, -5.1, 0.12), (-52.0, -2.7, 0.33), 28)
def S05_SH090(nf):
    """Ground level: the case comes in at speed, slams on an edge, bounces and bursts open; he crashes down beside it. A gust takes the paper."""
    rf = rock_fall(); p = SH090_CAM[0]; square_set(p)
    him = Actor("him", COST["him"], nf); k = F(SH090_TAU + HIT_DT); him.joints(0, rf["JA"][k:])
    t_burst = case_rel(0)[3][1] - SH090_TAU
    burst = PR.papers("bond", 30, CASE_AT, 0.25, t_burst, t_burst + 1.1, rise=1.6, seed=8, drift=(1.4, 0.9), hidden_before=True)
    t_slam = case_rel(0)[3][0] - SH090_TAU
    return {"cam": cam(*SH090_CAM), "actors": [him], "callbacks": [flying_case(lambda f: f / core.FPS + SH090_TAU), burst],
            "cues": [[t_slam, t_slam + 0.25, "THE CASE SLAMS"], [0.5, 0.8, "HE CRASHES DOWN"], [t_burst, t_burst + 0.3, "IT BURSTS OPEN, A GUST"]]}

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
    return {"cam": cam(p, (-50.5, -1.0, 3.2), 24, hh=0.5), "actors": acts, "callbacks": [fly, bond_past_lens(p, (-50.5, -1.0, 3.2), *BOND_T)],
            "cues": [[BOND_T[0] + 0.35, BOND_T[1] - 0.25, "THE BOND TUMBLES PAST THE LENS"]]}

BOND_T = (0.9, 2.2)              # S05 SH110: the bond tumbles past the lens (readable around the middle of this window)
def bond_past_lens(campos, camtgt, t0, t1):
    """One certificate tumbles past the lens, its face turning to the camera mid-way: PUBLIC IMPROVEMENT BOND, $500,000."""
    import bpy
    mb = core.MB(None, detail=False); mb.box(-0.16, 0.16, -0.105, 0.105, 0, 0.003, "#EDE6D2"); mb.box(-0.15, 0.15, -0.095, -0.088, 0.003, 0.0035, "#6A5A3A")
    mb.box(-0.15, 0.15, 0.088, 0.095, 0.003, 0.0035, "#6A5A3A"); sheet = PR.mesh_obj("bond_lens", mb)
    cu = bpy.data.curves.new("bond_txt", "FONT"); cu.body = "PUBLIC IMPROVEMENT BOND\n$500,000"; cu.size = 0.024; cu.align_x = "CENTER"; cu.align_y = "CENTER"
    tx = bpy.data.objects.new("bond_txt", cu); bpy.context.scene.collection.objects.link(tx); tx.parent = sheet; tx.location = (0, 0, 0.004)
    cu.materials.append(core.MATS.get("#2A2620"))
    c = np.array(campos, float); f_ = np.array(camtgt, float) - c; f_ /= np.linalg.norm(f_)
    r_ = np.cross(f_, (0, 0, 1.0)); r_ /= np.linalg.norm(r_); u_ = np.cross(r_, f_)
    def cb(f):
        t = f / core.FPS; u = (t - t0) / (t1 - t0)
        if not 0 <= u <= 1: sheet.hide_render = True; tx.hide_render = True; return
        sheet.hide_render = False; tx.hide_render = False
        p = c + f_ * (1.05 - 0.3 * u) + r_ * (0.75 - 1.5 * u) + u_ * (0.42 - 0.75 * u + 0.08 * math.sin(7 * u))
        # face to the lens at mid-way, tumbling either side of it
        a = (u - 0.5) * 2.4; R = np.stack([r_, u_, -f_], 1) @ core.rotx(0.35 * math.sin(3 * u) + a * 0.6) @ core.roty(a)
        sheet.matrix_world = Puppet.M(R, p)
    return cb

def S05_SH120(nf):
    """Close: he gets up where he fell, looks at the open case, then at the people coming up the street, and backs away from it."""
    rf = rock_fall(); hp = rf["land"]; y0 = rf["land_yaw"]
    p = (hp[0] + 2.1, hp[1] - 0.8, 1.0); square_set(p)
    him = Actor("him", COST["him"], nf); X, Y = float(hp[0]), float(hp[1])
    him.seq([(0, pose("lie_front", x=X, y=Y, yaw=y0)), (0.7, pose("hands_knees", x=X, y=Y, yaw=y0)), (1.3, pose("kneel", x=X, y=Y, yaw=-100)),
             (1.85, pose("stand", x=X, y=Y, yaw=-115, spine=14, hpitch=26)), (2.35, pose("stand", x=X, y=Y, yaw=160, spine=6, hpitch=0))], blend=0.3)
    him.path(2.4, 3.3, [(X, Y), (X + 0.05, Y + 0.75)], "walk", speed="io", yaw_fixed=160)
    him.look(2.2, 3.0, (X - 9.0, Y + 1.0, 1.6))
    him.face(0, 1.8, eyes=0.55); him.face(1.8, 3.0, eyes=1.45)
    rest = PR.briefcase("case_open", opened=True); PR.place(rest, (CASE_AT[0], CASE_AT[1], 0.0), -80)
    paper = PR.papers("bond", 16, CASE_AT, 0.6, 0.0, 3.0, rise=1.2, seed=12, drift=(1.0, 0.8))
    # the people coming up the street behind him, each at his own pace, out of focus
    rng = np.random.default_rng(121); n = 16
    P0 = band(X - 9.0, n, 3.0, -6.0, 6.0, seed=121, dirx=-1.0, walls=SQ_WALLS)
    cr = Crowd(P0, rng.uniform(0.9, 1.7, n), walls=SQ_WALLS, space_k=0.0, seed=121, start=rng.uniform(0, 1.2, n))
    T_ = np.stack([np.full(n, X - 4.5), P0[:, 1] * 0.6], 1) + rng.normal(0, 0.8, (n, 2))
    acts = people("c", cr.run(nf / core.FPS, lambda t, P, V: (seek(P, T_, cr.v0, 2.0), np.repeat(np.array(hp)[None], n, 0))), nf, 122)
    him.compute()
    def camfn(t):                                    # the operator rises with him: always about at his eye level
        f = min(nf - 1, int(round(t * core.FPS))); hz = np.mean([him.J[max(0, f - k), HEAD] for k in range(5)], axis=0)
        return np.array((p[0], p[1], 0.75 + 0.5 * hz[2])), hz + np.array((0, 0, -0.08)), 40, 0
    return {"cam": dof({"fn": camfn, "hh": 0.6}, (him, HEAD), 2.8), "actors": [him] + acts, "callbacks": [paper],
            "cues": [[0, 3, "EARS RINGING, VOICES CLOSE"]]}

SH130_FROM = lambda: rock_fall()["land"] + np.array((0.05, 0.75))       # where he stands at the end of SH120
def S05_SH130(nf):
    """POV: faces close in around him, slowly, from every side, while he staggers toward the corner. Everyone keeps coming, facing him."""
    a0 = SH130_FROM(); a1 = np.array(FALL)
    eye = lambda t: a0 + (a1 - a0) * min(1.0, t / 4.0) * 0.45
    square_set((a0[0], a0[1], 1.6))
    rng = np.random.default_rng(71); n = 28
    P0 = falloff(tuple(a0), n, r_min=4.0, lam=2.5, seed=71, walls=SQ_WALLS, max_r=14)
    cr = Crowd(P0, rng.uniform(0.5, 1.2, n), walls=SQ_WALLS, space_k=0.0, seed=71, start=rng.uniform(0, 1.0, n), bubble=lambda t: (eye(t), 1.6))
    def brain(t, P, V):
        c = eye(t); d = P - c[None]; r = np.linalg.norm(d, axis=1)[:, None] + 1e-6
        T_ = c[None] + d / r * 1.9; Vd = seek(P, T_, cr.v0, 1.0)
        Vd[(r[:, 0] < 2.1)] = 0.0                                      # close enough: stop, never walk away
        return Vd, np.repeat(c[None], n, 0)
    X, Y, YW, SP = cr.run(nf / core.FPS, brain)
    for f in range(len(X)):                                            # everyone faces him, even when the crush pushes him a step back
        c = eye(f / core.FPS); YW[f] = np.degrees(np.arctan2(-(c[0] - X[f]), c[1] - Y[f]))
    acts = crowd_actors("c", (X, Y, YW, SP), 0, nf, rnd=random.Random(72), lod="high")     # faces: eyes, nose, mouth
    def camfn(t):
        c = eye(t); a = math.radians(-60 + 70 * t / 4.0)
        return np.array((c[0], c[1], 1.62)), np.array((c[0] + 6 * math.cos(a), c[1] + 6 * math.sin(a), 1.5)), 30, 0
    return {"cam": {"fn": camfn, "hh": 0.8}, "actors": acts, "cues": [[0, 4, "BREATHING, THE CROWD MUTTERS"]]}

def flinch(a, t0, dur, amt=1.0, crouch=False, hands=True):
    """A man who hears the shot: he ducks, shoulders up, hands to the head (crouch: knees bend too)."""
    f0, f1 = F(t0), F(t0 + dur)
    def fn(f, q):
        u = (f - f0) / max(1, f1 - f0); w = math.sin(math.pi / 2 * u / 0.2) if u < 0.2 else (1.0 if u < 0.55 else max(0.0, 1 - (u - 0.55) / 0.45))
        w *= amt; o = dict(q); o["spine"] = q["spine"] + 26 * w; o["hpitch"] = q["hpitch"] + 22 * w
        if hands: o["la"] = lerp_pose({"la": q["la"]}, {"la": (140, 30, 120)}, w)["la"]; o["ra"] = lerp_pose({"ra": q["ra"]}, {"ra": (140, 30, 120)}, w)["ra"]
        if crouch: o["ll"] = lerp_pose({"ll": q["ll"]}, {"ll": (70, 8, 100)}, w)["ll"]; o["rl"] = lerp_pose({"rl": q["rl"]}, {"rl": (70, 8, 100)}, w)["rl"]
        return o
    a.overlays.append((f0, f1, fn))

SHOT1 = 3.8                      # S05 SH140: the shot into the air
def S05_SH140(nf):
    """The corner of the square, under the street light: the crowd already closing in, slowly, each at his own pace.
    The shot into the air: everyone flinches; some run at once, others a moment later, the last ones later still."""
    p = (-31.0, 9.0, 2.3); square_set(p); T = nf / core.FPS; PRE = 2.0
    him = Actor("him", COST["him"], nf); him.hold(0, T, pose("stand", x=FALL[0], y=FALL[1], yaw=90, spine=10))
    him.over(SHOT1 - 0.3, T, ra=(170, 5, 5))
    n = 50; rng = np.random.default_rng(81)
    P0 = falloff(FALL, n, r_min=3.2, lam=2.4, arc=(-110, 200), seed=81, walls=SQ_WALLS, max_r=22)
    S = falloff(FALL, n, r_min=0.9, lam=1.3, arc=(-110, 200), seed=82, walls=SQ_WALLS, max_r=10); T_ = assign(P0, S, FALL)
    v_in = rng.uniform(0.3, 0.9, n)                                    # all slow, each his own pace
    cr = Crowd(P0, v_in.copy(), walls=SQ_WALLS, space_k=0.03, focus=FALL, seed=81, bubble=lambda t: (FALL, 0.8))
    grp = rng.choice(3, n, p=(0.35, 0.35, 0.3))
    react = np.where(grp == 0, rng.uniform(0.15, 0.45, n), np.where(grp == 1, rng.uniform(0.6, 1.1, n), rng.uniform(1.2, 1.9, n)))
    v_out = rng.uniform(3.0, 5.5, n); flee = rng.uniform(6, 12, n); shot = SHOT1 + PRE
    def brain(t, P, V):
        c = np.array(FALL)[None]
        if t < shot:
            return seek(P, T_, cr.v0, 2.0), np.repeat(c, n, 0)
        go = t >= shot + react; cr.v0[:] = np.where(go, v_out, v_in)
        d = P - c; r = np.linalg.norm(d, axis=1)[:, None] + 1e-6
        out = c + d / r * (r + flee[:, None]); Vd = seek(P, out, cr.v0, 1.0); Vd[~go] = 0.0
        return Vd, np.where(go[:, None], out, np.repeat(c, n, 0))
    X, Y, YW, SP = cr.run(T + PRE, brain); k = F(PRE)                   # already walking when the shot starts: the first 2 s are dropped
    acts = people("c", (X[k:], Y[k:], YW[k:], SP[k:]), nf, 83)
    for i, a in enumerate(acts):
        flinch(a, SHOT1 + rng.uniform(0.0, 0.12), min(react[i] + 0.35, 1.2), amt=rng.uniform(0.6, 1.0), crouch=rng.random() < 0.3)
    g = PR.hand_prop("gun", "gun")
    return {"cam": cam(p, (FALL[0], FALL[1], 1.0), 30), "actors": [him] + acts, "callbacks": [gun_along_arm(g, him, visible=lambda f: f >= F(SHOT1 - 0.3))], "sticks": arm_sticks(him),
            "cues": [[0, SHOT1, "THE YELLING CLOSES IN"], [SHOT1, SHOT1 + 0.3, "GUNSHOT, INTO THE AIR"], [SHOT1 + 0.3, T, "SCREAMS, FEET"]]}
