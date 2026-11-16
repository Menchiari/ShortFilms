from sh import *

CUES = {"S04_SH020": [[0, 2, "BEADS CLICK"]], "S04_SH030": [[0, 2, "TV MURMUR"]]}
Y = -4.5                      # his sidewalk (south side of the street)
F_POS = (-65.6, -4.95)        # the fat man after stepping out of the side street
O_DOWN = (-63.7, -4.75)       # where the old man lands (head east)
BARMEN = [(-31.4, 4.7, 200), (-28.6, 4.7, 160), (-30.0, 5.3, 180)]

def street(eye):
    reset("day"); return sets.streets(eye)

def barmen(nf, look_from=None, target=None):
    out = []
    for i, (x, y, yaw) in enumerate(BARMEN):
        c = dict(crowd_costume(random.Random(40 + i)))
        a = Actor(f"bar{i}", c, nf, lod="high" if i == 0 else "low")
        a.hold(0, nf / core.FPS, pose("seat", x=x, y=y, yaw=yaw, z=0.5))
        a.talk(0, nf / core.FPS) if i == 1 else None
        out.append(a)
    if look_from is not None:
        out[0].look(look_from, nf / core.FPS, target)
    return out

def fat(nf, pos=F_POS, yaw=None):
    a = Actor("fat", COST["fat"], nf); a.hold(0, nf / core.FPS, pose("stand", x=pos[0], y=pos[1], yaw=yaw if yaw is not None else fdir(pos, O_DOWN)))
    return a

def friend(nf):
    a = Actor("friend", COST["friend"], nf); a.hold(0, nf / core.FPS, pose("stand", x=-67.6, y=-7.6, yaw=fdir((-67.6, -7.6), O_DOWN), ra=(80, 10, 100), la=(70, 10, 110)))
    return a

def down_pose(**kw):
    return pose("lie_back", x=O_DOWN[0], y=O_DOWN[1], yaw=90, **kw)

def S04_SH010(nf):
    p0 = (-1.0, -1.4, 1.5); street(p0)
    him = Actor("him", COST["him"], nf); him.path(0, 4, [(-2, Y), (-9, Y)], "walk", speed="lin")
    case = PR.hand_prop("case", "case")
    return {"cam": move([(0, p0, (-2.6, Y, 1.4), 35), (4, (-8.0, -1.4, 1.5), (-9.6, Y, 1.4), 35)], hh=0.6, ease="lin"), "actors": [him],
            "callbacks": [PR.chest(case, him)], "cues": [[0, 4, "FOOTSTEPS, HEAVY BREATH, NOTHING ELSE"]]}

def S04_SH040(nf):
    p = (-72.0, 2.2, 2.0); street(p)
    him = Actor("him", COST["him"], nf); him.path(0, 4, [(-24, Y), (-31, Y)], "walk", speed="lin", base=dict(hpitch=20))
    case = PR.hand_prop("case", "case")
    return {"cam": cam(p, (-28, 0.2, 1.2), 100), "actors": [him] + barmen(nf), "callbacks": [PR.chest(case, him)], "cues": [[0, 4, "THE MEN TALK LOW"]]}

def S04_SH050(nf):
    p = (-34.0, 3.6, 1.25); street(p)
    him = Actor("him", COST["him"], nf); him.path(0, 2, [(-32.5, Y), (-36.0, Y)], "walk", speed="lin", base=dict(hpitch=20))
    bm = barmen(nf, look_from=0.5, target=(-35, Y, 1.6))
    case = PR.hand_prop("case", "case")
    return {"cam": cam(p, (-31.4, 4.7, 1.2), 70), "actors": [him] + bm, "callbacks": [PR.chest(case, him)], "cues": [[0.4, 2, "THE TALK STOPS"]]}

HIT = (-64.9, -4.6)               # where he walks into the fat man
def S04_SH060(nf):
    """Tracking beside him, he looks back, faster and faster; the fat man steps into frame from nowhere: impact."""
    street((-55.3, -2.6, 1.6))
    him = Actor("him", COST["him"], nf)
    him.path(0, 4.4, [(-56.5, Y), HIT], "walk", speed="in")
    him.over(0.6, 4.3, hyaw=-75, twist=-15)
    him.blend(4.4, 4.9, pose("stand", x=HIT[0], y=HIT[1], yaw=90), pose("stand", x=HIT[0] + 0.45, y=HIT[1] - 0.05, yaw=90, spine=-22, hpitch=-25))
    fa = Actor("fat", COST["fat"], nf)
    fa.path(0, 4.35, [(-66.4, -9.5), (F_POS[0] + 0.25, F_POS[1])], "walk", speed="lin")
    fa.blend(4.35, 4.8, pose("stand", x=F_POS[0] + 0.25, y=F_POS[1], yaw=-90), pose("stand", x=F_POS[0] + 0.1, y=F_POS[1], yaw=-90, spine=-6))
    case = PR.hand_prop("case", "case")
    him.compute()
    def pos(t):
        f = min(nf - 1, int(round(t * core.FPS))); x = him.J[f, PELVIS, 0]; return np.array((x + 1.3, -2.6, 1.6))
    return {"cam": follow(him, pos, lens=40, offset=(-0.6, 0, 0.6), lag=0.3, hh=0.7), "actors": [him, fa],
            "callbacks": [PR.chest(case, him, visible=lambda f: f < F(4.5))], "cues": [[4.3, 4.7, "IMPACT"]]}

def S04_SH070(nf):
    """Over the fat man's shoulder, long lens, looking down: he lands flat on his back (a shape: no body through the ground)."""
    p = (-67.3, -4.3, 2.05); street(p)
    him = Actor("him", COST["him"], nf)
    him.seq([(0.0, pose("stand", x=HIT[0] + 0.45, y=HIT[1] - 0.05, yaw=90, spine=-22, hpitch=-25)), (0.3, pose("stand", x=HIT[0] + 0.8, y=-4.7, yaw=90, spine=-35, hpitch=-30)),
             (0.75, down_pose()), (3.0, down_pose())])
    fa = Actor("fat", COST["fat"], nf); fa.hold(0, 3, pose("stand", x=F_POS[0] + 0.1, y=F_POS[1], yaw=-90, spine=-6, hpitch=25))
    case = PR.briefcase("case")
    def ccb(f):
        t = f / core.FPS; u = min(1, t / 0.6); PR.place(case, (-63.9 + 1.0 * u, -4.25 + 0.2 * u, 0.6 * (1 - u) ** 2), 30 + 60 * u)
    return {"cam": cam(p, (-63.9, -4.75, 0.3), 85), "actors": [him, fa], "callbacks": [ccb], "cues": [[0.6, 1.0, "THUD ON THE ASPHALT"]]}

def S04_SH080(nf):
    p = (O_DOWN[0] - 0.3, O_DOWN[1] + 0.55, 0.32); street(p)
    fa = fat(nf); fa.seq([(0, pose("stand", x=F_POS[0], y=F_POS[1], yaw=fdir(F_POS, O_DOWN), hpitch=35)),
                          (2.0, pose("stand", x=F_POS[0], y=F_POS[1], yaw=fdir(F_POS, O_DOWN), hpitch=38, spine=10, eyes=1.5))])
    fa.talk(2.2, 3.9)
    him = Actor("him", COST["him"], nf); him.hold(0, 4, down_pose())
    return {"cam": cam(p, (F_POS[0], F_POS[1], 1.85), 24, hh=0.4), "actors": [fa, him], "speakers": {"FAT PERSON": fa}, "say": [[2.2, 3.9, "FAT PERSON"]]}

def S04_SH090(nf):
    p = (-65.1, -3.9, 2.35); street(p)
    him = Actor("him", COST["him"], nf)
    him.seq([(0, down_pose()), (0.6, pose("lie_cover", x=O_DOWN[0], y=O_DOWN[1], yaw=90))])
    him.talk(1.0, 4.6)
    fa = fat(nf)
    return {"cam": cam(p, (O_DOWN[0] + 0.5, O_DOWN[1], 0.15), 28, hh=0.4), "actors": [him, fa], "speakers": {"OLD MAN": him}, "say": [[1.0, 4.6, "OLD MAN"]]}

def S04_SH100(nf):
    """Low, from his eyes on the ground: the fat man above him; behind, the friend films, then types on his phone."""
    p = (O_DOWN[0] + 0.75, O_DOWN[1] + 0.1, 0.35); street(p)
    fa = fat(nf); fa.over(0, 7, hpitch=30, spine=8); fa.talk(0.4, 6.4)
    fr = friend(nf)
    him = Actor("him", COST["him"], nf); him.hold(0, 7, pose("lie_cover", x=O_DOWN[0], y=O_DOWN[1], yaw=90)); him.hide(0, 7)   # his eyes: he is the camera
    phone = PR.hand_prop("phone", "phone")
    fr.compute()
    def texting(f):
        t = f / core.FPS; J = fr.J[min(f, nf - 1)]
        up = J[NECK] - J[PELVIS]; up /= np.linalg.norm(up); fwd = J[NOSE] - J[HEAD]; fwd -= up * np.dot(fwd, up); fwd /= np.linalg.norm(fwd)
        right = np.cross(fwd, up)
        if t < 3.5:      # filming: phone up in front of his face, screen to him
            c = J[HEAD] + fwd * 0.32 - up * 0.05; R = np.stack([right, fwd, up], 1)
        else:            # typing: phone low at the chest, screen up
            c = J[NECK] + fwd * 0.3 - up * 0.28; tl = up * 0.5 + fwd * 0.87; R = np.stack([right, np.cross(tl, right), tl], 1)
        phone.matrix_world = Puppet.M(R, c)
    return {"cam": cam(p, (-66.3, -5.9, 1.75), 32, hh=0.5), "actors": [fa, fr, him], "speakers": {"FAT PERSON": fa}, "say": [[0.4, 6.4, "FAT PERSON"]],
            "callbacks": [texting]}

GRIP_HIM = (-64.85, -4.75); GRIP_FAT = (-65.45, -4.8)
def grip_pair(nf, haul=True):
    him = Actor("him", COST["him"], nf)
    if haul:
        him.seq([(0, down_pose()), (0.5, pose("sit_ground", x=-64.2, y=-4.75, yaw=90)), (1.2, pose("stand", x=GRIP_HIM[0], y=GRIP_HIM[1], yaw=90, spine=-8))])
    else:
        him.hold(0, nf / core.FPS, pose("stand", x=GRIP_HIM[0], y=GRIP_HIM[1], yaw=90, spine=-8))
    fa = Actor("fat", COST["fat"], nf)
    fa.hold(0, nf / core.FPS, pose("stand", x=GRIP_FAT[0], y=GRIP_FAT[1], yaw=-90, spine=8, hpitch=18))
    return him, fa

def S04_SH110(nf):
    """Tight, over his right shoulder: the two face to face; the long street behind the fat man, soft."""
    p = (-64.15, -3.75, 1.72); street(p)
    him, fa = grip_pair(nf); fa.talk(1.6, 4.8); fa.compute()
    case = PR.hand_prop("case", "case")
    tgt = fa.J[0, HEAD] + np.array((0, 0, -0.05))
    return {"cam": cam(p, tuple(tgt), 50, hh=0.5, focus=(fa, HEAD), fstop=1.8), "actors": [him, fa], "speakers": {"FAT PERSON": fa}, "say": [[1.6, 4.8, "FAT PERSON"]],
            "callbacks": [PR.chest(case, him)]}

def S04_SH120(nf):
    p = (-64.3, -5.1, 1.7); street(p)
    him, fa = grip_pair(nf, haul=False); fa.talk(0.3, 5.7); fa.compute()
    tgt = fa.J[0, HEAD] + np.array((0, 0, -0.04))
    return {"cam": cam(p, tuple(tgt), 70, hh=0.5, focus=(fa, HEAD), fstop=1.8), "actors": [him, fa], "speakers": {"FAT PERSON": fa}, "say": [[0.3, 5.7, "FAT PERSON"]]}

def S04_SH130(nf):
    p = (-59.0, -2.8, 0.5); reset("day"); sets.streets(p, clear=[(-58.0, 5.5, 8.0, 9.0)])
    acts = []
    mb = core.MB(None, detail=False)
    spots = [(-61.0, 4.6, 0.3), (-57.5, 7.6, 0.6), (-54.0, 4.6, 0.9), (-62.5, 10.6, 0.2), (-56.0, 10.6, 1.1)]
    for i, (x, z, t0) in enumerate(spots):
        mb.box(x - 0.6, x + 0.6, 5.5, 5.52, z - 0.9, z + 0.7, PAL["window"])
        a = Actor(f"win{i}", crowd_costume(random.Random(70 + i)), nf, lod="high")
        a.hold(0, 2, pose("stand", x=x, y=5.62, yaw=180, z=z - 1.62, spine=30, hpitch=30))
        a.hide(0, t0); acts.append(a)
    mb.build("windows")
    h, f2 = grip_pair(nf, haul=False); acts += [h, f2]
    return {"cam": cam(p, (-58.5, 5.5, 7.0), 45), "actors": acts, "cues": [[0, 2, "SHUTTERS OPEN ABOVE"]]}

def S04_SH140(nf):
    """Same angle as SH110: no violence, he shrinks and slides out of the grip, then runs back the way he came (frame left)."""
    p = (-64.2, -4.0, 1.74); street(p)
    him = Actor("him", COST["him"], nf)
    him.seq([(0, pose("stand", x=GRIP_HIM[0], y=GRIP_HIM[1], yaw=90, spine=-8)), (1.0, pose("crouch", x=GRIP_HIM[0] + 0.15, y=GRIP_HIM[1] - 0.2, yaw=60)),
             (1.6, pose("crouch", x=GRIP_HIM[0] + 0.5, y=GRIP_HIM[1] - 0.55, yaw=-30))], blend=0.4)
    him.path(1.6, 4.0, [(GRIP_HIM[0] + 0.5, GRIP_HIM[1] - 0.55), (-63.0, -5.4), (-57.0, -5.0)], "run", speed="in")
    fa = Actor("fat", COST["fat"], nf)
    fa.seq([(0, pose("stand", x=GRIP_FAT[0], y=GRIP_FAT[1], yaw=-90, spine=8, hpitch=18)), (1.2, pose("stand", x=GRIP_FAT[0], y=GRIP_FAT[1], yaw=-90, hpitch=5))])
    fa.look(1.6, 4.0, (-57, -5, 1.6))
    fr = Actor("friend", COST["friend"], nf); fr.path(0, 3.5, [(-67.6, -7.6), (-66.6, -5.8)], "walk", speed="io"); fr.talk(2.6, 4.0)
    case = PR.hand_prop("case", "case"); fa.compute()
    tgt = fa.J[0, HEAD] + np.array((0, 0, -0.05))
    return {"cam": cam(p, tuple(tgt), 50, hh=0.6, focus=(fa, HEAD), fstop=2.2), "actors": [him, fa, fr], "speakers": {"FRIEND": fr}, "say": [[2.6, 4.0, "FRIEND"]],
            "callbacks": [PR.chest(case, him)]}
