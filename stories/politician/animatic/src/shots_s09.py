from sh import *
from shots_s05 import SQ_WALLS, people
from shots_s07 import ARM, TOP, hanging, pipe_fall, _H, haul

CUES = {"S09_SH030": [[0, 3, "ROTORS WINDING DOWN"]], "S09_SH080": [[0, 2, "ROTORS"]]}
SEAT = (-39.6, -6.55)            # sitting on the street, back against the curb (the sidewalk edge at y = -7)
BODY = (-38.1, -5.9)             # the man with the pipe, next to him
CASE = (-47.0, -2.0)
HIMC = (-46.4, -2.3)             # him at the case
LADYC = (-45.0, -1.9)
PAD = (-24.0, 0.5)               # helicopter in the square; door faces west
DOOR = (-25.6, 1.0)
BODIES = [(-46.0, 2.5), (-52.0, -4.0), (-35.0, 3.0), (-50.0, 4.0), (-30.0, -5.0), (-56.0, 1.0), (-43.0, 5.5)]

def sq(eye, sky="sunset"):
    reset(sky); return sets.square(eye)

def scenery(nf, case=True, case_open=True):
    acts = []
    for i, (x, y) in enumerate(BODIES):
        a = Actor(f"body{i}", crowd_costume(random.Random(300 + i)), nf); a.hold(0, nf / core.FPS, pose("lie_front" if i % 2 else "lie_back", x=x, y=y, yaw=37 * i)); acts.append(a)
    b = Actor("pipe", crowd_costume(random.Random(141)), nf, lod="high"); b.hold(0, nf / core.FPS, pose("lie_back", x=BODY[0], y=BODY[1], yaw=0)); acts.append(b)
    mb = core.MB(None, detail=False); mb.box(BODY[0] + 0.3, BODY[0] + 1.3, BODY[1] + 0.6, BODY[1] + 0.66, 0.0, 0.05, "#8A8A8E"); mb.build("pipe_on_ground")
    if case:
        c = PR.briefcase("case", opened=case_open); PR.place(c, (CASE[0], CASE[1], 0.0), 60)
    return acts

def heli_landed(yaw=180.0):
    h = PR.heli("heli"); return h, PR.heli_cb(h, lambda t: (np.array((PAD[0], PAD[1], 0.0)), yaw, 0.0))

def S09_SH010(nf):
    p = (-39.4, 8.4, 0.22); sq(p)
    haul(); x, xp = _H["state"]
    rd = Ragdoll(x); rd.xp = xp.copy(); rd.pins[RAN] = lambda t: TOP if t < 0.3 else None
    rd.muscles.append(toward([LHA, RHA], lambda t, x_: x_[HEAD] if t > 0.6 else None, 12))
    JA = rd.run(1.6)
    him = Actor("him", COST["him"], nf); him.joints(0, JA)
    curl = pose("lie_curl", x=SEAT[0], y=SEAT[1] + 0.45, yaw=90)
    lean = pose("lean_curb", x=SEAT[0], y=SEAT[1], yaw=0)
    him.seq([(1.6, curl), (4.4, curl), (7.3, curl), (10.0, lean), (13.4, dict(lean, hpitch=-30)), (14.6, dict(lean, roll=-14, hyaw=-70, hpitch=12, spine=16, la=(-40, 30, 80))),
             (15.0, dict(lean, roll=-14, hyaw=-70, hpitch=22, spine=24, la=(-40, 30, 80))), (15.4, dict(lean, roll=-14, hyaw=-70, hpitch=8, spine=14, la=(-40, 30, 80))),
             (18.0, dict(lean, roll=-14, hyaw=-70, hpitch=10, spine=14, la=(-40, 30, 80)))], blend=0.6)
    him.overlays.append((F(4.4), F(7.3), lambda f, q: dict(q, spine=q["spine"] + 4 * math.sin(f * 2.3))))
    him.overlays.append((F(10.0), F(13.4), lambda f, q: dict(q, spine=q["spine"] - 5 * math.sin(f / core.FPS * 3.0))))
    him.talk(0.6, 4.2); him.face(13.6, 14.4, mouth=0.15); him.face(14.9, 15.2, mouth=0.9)
    rope = Stick("rope", 0.018, PAL["rope"], lambda f: (tuple(ARM), tuple(TOP)) if f < F(0.3) else (tuple(ARM), tuple(ARM - np.array((0, 0, 1.0)))))
    return {"cam": cam(p, (SEAT[0], SEAT[1], 0.45), 135), "actors": [him] + scenery(nf, case=False), "sticks": [rope], "speakers": {"OLD MAN": him},
            "say": [[0.6, 4.2, "OLD MAN"]], "cues": [[0.3, 0.9, "THE ROPE GOES, HE HITS THE ASPHALT"], [4.4, 7.3, "THE STAIN SPREADS"],
                                                    [10.0, 13.4, "HE BREATHES. LOOKS AT THE SKY"], [14.9, 15.4, "SPIT"]]}

def S09_SH020(nf):
    p = (-48.7, -1.5, 0.35); sq(p)
    him = Actor("him", COST["him"], nf)
    lean = pose("lean_curb", x=SEAT[0], y=SEAT[1], yaw=0)
    him.seq([(0, lean), (1.0, lean), (2.0, pose("hands_knees", x=SEAT[0], y=SEAT[1] + 0.3, yaw=fdir(SEAT, HIMC))),
             (3.0, pose("kneel", x=SEAT[0] - 0.1, y=SEAT[1] + 0.4, yaw=fdir(SEAT, HIMC))), (3.8, pose("stand", x=SEAT[0] - 0.2, y=SEAT[1] + 0.45, yaw=fdir(SEAT, HIMC)))])
    him.path(3.8, 12.4, [(SEAT[0] - 0.2, SEAT[1] + 0.45), (-43.0, -4.4), (HIMC[0], HIMC[1])], "limp", speed="io")
    him.blend(12.4, 13.0, pose("stand", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, CASE)), pose("crouch", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, CASE), la=(80, 5, 10), ra=(80, 5, 10)))
    h = PR.heli("heli")
    def hpath(t):
        u = min(1.0, max(0.0, (t - 0.5) / 9.0)); u = 1 - (1 - u) ** 2.2
        return np.array((PAD[0] + 8 * (1 - u), PAD[1], 32 * (1 - u))), 180.0 + 10 * (1 - u), 4 * (1 - u)
    paper = PR.papers("bond", 70, (-42.0, -3.0), 7, 4.0, 13.0, rise=4.0, seed=7, drift=(-6, 0))
    return {"cam": cam(p, (-36.0, -4.5, 1.6), 24), "actors": [him] + scenery(nf), "callbacks": [PR.heli_cb(h, hpath), paper], "cues": [[0, 13, "ROTOR WASH GROWS"]]}

def standing_pair(nf, him_kw=None, lady_kw=None, lady_turn=None):
    him = Actor("him", COST["him"], nf); him.hold(0, nf / core.FPS, pose("stand", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, LADYC), **(him_kw or {})))
    la = Actor("lady", COST["lady"], nf); la.hold(0, nf / core.FPS, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, HIMC), **(lady_kw or {})))
    return him, la

def S09_SH040(nf):
    p = (-27.0, 24.0, 2.6); sq(p)
    h, hcb = heli_landed()
    him = Actor("him", COST["him"], nf); him.hold(0, 4, pose("stand", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, DOOR), ra=(40, 10, 60)))
    la = Actor("lady", COST["lady"], nf)
    la.seq([(0, pose("crouch", x=DOOR[0], y=DOOR[1], yaw=fdir(DOOR, HIMC))), (0.5, pose("crouch", x=DOOR[0] - 0.5, y=DOOR[1], yaw=fdir(DOOR, HIMC)))])
    la.path(0.5, 4.0, [(DOOR[0] - 0.5, DOOR[1]), (-31.0, -0.2)], "walk", speed="in", base=dict(spine=18))
    folder = PR.hand_prop("folder", "folder")
    paper = PR.papers("bond", 50, (-40.0, -1.0), 8, 0.0, 4.0, rise=2.5, seed=9, drift=(-3, 0))
    return {"cam": cam(p, (-35.0, -1.0, 1.2), 24), "actors": [him, la] + scenery(nf), "callbacks": [hcb, paper, PR.attach(folder, him)], "cues": [[0, 4, "ROTORS"]]}

def S09_SH050(nf):
    p = (-45.6, 0.7, 1.6); sq(p)
    h, hcb = heli_landed(); him, la = standing_pair(nf); him.talk(1.4, 3.6)
    folder = PR.hand_prop("folder", "folder")
    return {"cam": cam(p, (HIMC[0], HIMC[1], 1.5), 40), "actors": [him, la] + scenery(nf), "callbacks": [hcb, PR.attach(folder, him)],
            "speakers": {"OLD MAN": him}, "say": [[1.4, 3.6, "OLD MAN"]]}

def S09_SH060(nf):
    p = (-46.2, -1.35, 1.68); sq(p)
    h, hcb = heli_landed(); him, la = standing_pair(nf)
    return {"cam": cam(p, (LADYC[0], LADYC[1], 1.58), 50), "actors": [him, la] + scenery(nf), "callbacks": [hcb]}

def S09_SH070(nf):
    p = (-45.7, 1.6, 1.55); sq(p)
    h, hcb = heli_landed(); him, la = standing_pair(nf)
    him.blend(0.4, 1.2, pose("stand", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, LADYC)), pose("stand", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, LADYC), ra=(60, 5, 30)))
    him.blend(1.6, 2.2, pose("stand", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, LADYC), ra=(60, 5, 30)), pose("stand", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, LADYC)))
    la.seq([(0, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, HIMC))), (0.6, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, HIMC), ra=(55, 5, 30))),
            (2.4, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, HIMC), ra=(55, 5, 70), la=(55, 5, 70), hpitch=30))])
    for a in (him, la): a.compute()
    folder = PR.hand_prop("folder", "folder")
    a1 = PR.attach(folder, him); a2 = PR.attach(folder, la)
    def fcb(f):
        (a1 if f < F(1.5) else a2)(f)
    return {"cam": cam(p, (-45.7, -2.1, 1.3), 32), "actors": [him, la] + scenery(nf), "callbacks": [hcb, fcb]}

def S09_SH090(nf):
    p = (-46.2, -1.35, 1.68); sq(p)
    h, hcb = heli_landed(); him, la = standing_pair(nf, lady_kw=dict(ra=(50, 5, 70), la=(50, 5, 70)))
    la.face(1.4, 2.0, mouth=0.3)
    folder = PR.hand_prop("folder", "folder")
    return {"cam": cam(p, (LADYC[0], LADYC[1], 1.58), 50), "actors": [him, la] + scenery(nf), "callbacks": [hcb, PR.attach(folder, la)]}

def S09_SH100(nf):
    p = (-45.25, -1.3, 1.7); sq(p)
    h, hcb = heli_landed(); him, la = standing_pair(nf, him_kw=dict(hpitch=-12))
    return {"cam": cam(p, (HIMC[0], HIMC[1], 1.6), 50), "actors": [him, la] + scenery(nf), "callbacks": [hcb]}

def S09_SH110(nf):
    p = (-34.0, 9.0, 1.7); sq(p)
    h, hcb = heli_landed()
    him = Actor("him", COST["him"], nf)
    him.path(0, 4.4, [(-35.5, -0.9), (DOOR[0] - 0.4, DOOR[1])], "walk", speed="io")
    him.blend(4.4, 5.0, pose("stand", x=DOOR[0] - 0.4, y=DOOR[1], yaw=-90), pose("stand", x=DOOR[0] + 0.3, y=DOOR[1], yaw=-90, z=0.6))
    him.blend(5.0, 5.4, pose("stand", x=DOOR[0] + 0.3, y=DOOR[1], yaw=-90, z=0.6), pose("point_chin", x=DOOR[0] + 0.3, y=DOOR[1], yaw=90, z=0.6))
    him.hold(5.4, 7.0, pose("point_chin", x=DOOR[0] + 0.3, y=DOOR[1], yaw=90, z=0.6)); him.talk(5.4, 6.9)
    la = Actor("lady", COST["lady"], nf); la.hold(0, 7, pose("stand", x=-38.6, y=-1.4, yaw=fdir((-38.6, -1.4), DOOR), ra=(50, 5, 70), la=(50, 5, 70)))
    la.look(0, 7, (DOOR[0], DOOR[1], 1.6))
    return {"cam": cam(p, (-30.0, 0.0, 1.4), 32), "actors": [him, la] + scenery(nf), "callbacks": [hcb], "speakers": {"OLD MAN": him}, "say": [[5.4, 6.9, "OLD MAN"]]}

def S09_SH120(nf):
    p = (-37.0, -0.7, 1.62); sq(p)
    h, hcb = heli_landed()
    paper = PR.papers("bond", 60, (-49.0, -2.0), 7, 0.0, 3.0, rise=1.5, seed=11, drift=(-2, 0))
    return {"cam": cam(p, (-56.0, -2.5, 0.3), 28), "actors": scenery(nf), "callbacks": [hcb, paper], "cues": [[0, 3, "ROTOR WASH, PAPER FLUTTERING"]]}

def S09_SH130(nf):
    p = (-35.4, -0.9, 1.6); sq(p)
    h, hcb = heli_landed()
    him = Actor("him", COST["him"], nf); him.hold(0, 5, pose("stand", x=DOOR[0] + 0.3, y=DOOR[1], yaw=90, z=0.6))
    pos = (-32.4, -0.2)
    la = Actor("lady", COST["lady"], nf)
    la.hold(0, 3.4, pose("stand", x=pos[0], y=pos[1], yaw=fdir(pos, (-35.4, -0.9)), ra=(50, 5, 70), la=(50, 5, 70)))
    la.look(0.4, 3.4, (-50.0, -2.0, 0.3)); la.talk(1.6, 3.0)
    la.blend(3.4, 3.9, pose("stand", x=pos[0], y=pos[1], yaw=fdir(pos, (-35.4, -0.9))), pose("stand", x=pos[0], y=pos[1], yaw=fdir(pos, DOOR)))
    la.path(3.9, 5.0, [pos, (DOOR[0] - 0.4, DOOR[1])], "walk", speed="in")
    return {"cam": cam(p, (pos[0], pos[1], 1.58), 50), "actors": [him, la], "callbacks": [hcb], "speakers": {"BUSINESS LADY": la}, "say": [[1.6, 3.0, "BUSINESS LADY"]]}
