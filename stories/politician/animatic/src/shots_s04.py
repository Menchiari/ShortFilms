from sh import *
from puppet import _obj, _mesh_sphere

CUES = {"S04_SH020": [[0, 2, "BEADS CLICK"]], "S04_SH030": [[0, 2, "TV MURMUR"]]}
Y = -4.5                      # his sidewalk (south side of the street)
F_POS = (-65.6, -4.95)        # the fat man after stepping out of the side street
O_DOWN = (-63.7, -4.75)       # where the old man lands (head east)
BARMEN = [(-31.4, 4.7, 200), (-28.6, 4.7, 160), (-30.0, 5.3, 180)]

def streets(eye, **kw):
    """The streets set without laundry on the balconies (draft 10: no laundry anywhere)."""
    core.LAUNDRY = False
    try:
        return sets.streets(eye, **kw)
    finally:
        core.LAUNDRY = False

def street(eye):
    reset("day"); return streets(eye)

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
    """Long lens from his sidewalk, a little behind him: the three men at the bar, every head in frame with air above.
    The nearest one is talking, stops and turns his head to look at him (toward the lens); the others fall silent."""
    p = (-40.0, -4.0, 1.5); street(p)
    him = Actor("him", COST["him"], nf); him.path(0, 2, [(-32.5, Y), (-36.0, Y)], "walk", speed="lin", base=dict(hpitch=20))
    bm = barmen(nf)
    T = nf / core.FPS
    bm[1].overlays.clear(); bm[1].talk(0, 0.7); bm[1].look(0.9, T + 0.5, (-34.0, Y, 1.5), strength=0.5)
    bm[0].talk(0, 0.45); bm[0].look(0.45, T + 0.5, (-34.5, Y, 1.5))
    bm[2].look(1.1, T + 0.5, (-34.0, Y, 1.5), strength=0.35)
    case = PR.hand_prop("case", "case")
    return {"cam": cam(p, (-29.9, 4.9, 1.02), 100), "actors": [him] + bm, "callbacks": [PR.chest(case, him)], "cues": [[0.4, 2, "THE TALK STOPS"]]}

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

SH070_CAM = (-70.0, -3.6, 3.2); SH070_TGT = (-63.6, -4.6, 1.0); SH070_LENS = 60     # higher, further back: his head stays in frame
def S04_SH070(nf):
    """Over the fat man's shoulder, long lens, looking down: he lands flat on his back (a shape: no body through the ground)."""
    p = SH070_CAM; street(p)
    him = Actor("him", COST["him"], nf)
    him.seq([(0.0, pose("stand", x=HIT[0] + 0.45, y=HIT[1] - 0.05, yaw=90, spine=-22, hpitch=-25)), (0.3, pose("stand", x=HIT[0] + 0.8, y=-4.7, yaw=90, spine=-35, hpitch=-30)),
             (0.75, down_pose()), (3.0, down_pose())])
    fa = Actor("fat", COST["fat"], nf); fa.hold(0, 3, pose("stand", x=F_POS[0] + 0.1, y=F_POS[1], yaw=-90, spine=-6, hpitch=25))
    case = PR.briefcase("case")
    def ccb(f):                      # the case flies out of his arms, tips over and lands flat
        t = f / core.FPS; u = min(1, t / 0.6); k = u * u * (3 - 2 * u)
        x, y = -63.9 + 1.0 * u, -4.25 + 0.2 * u            # it lands on the sidewalk (0.15 high)
        PR.place(case, (x, y, 0.6 * (1 - u) ** 2 + (0.06 + core.ground_z(x, y)) * k), 30 + 60 * u, extra=Matrix.Rotation(math.radians(90 * k), 4, "X"))
    return {"cam": cam(p, SH070_TGT, SH070_LENS), "actors": [him, fa], "callbacks": [ccb], "cues": [[0.6, 1.0, "THUD ON THE ASPHALT"]]}

def S04_SH080(nf):
    p = (O_DOWN[0] - 0.3, O_DOWN[1] + 0.55, 0.32); street(p)
    fa = Actor("fat", COST["fat"], nf); yw = fdir(F_POS, O_DOWN)
    st = lambda **kw: pose("stand", x=F_POS[0], y=F_POS[1], yaw=yw, **kw)
    # one track for the whole shot: he looks down, can't place him (a slow tilt of the head), then his eyes widen
    fa.seq([(0, st(hpitch=35)), (1.0, st(hpitch=36, hroll=7)), (1.7, st(hpitch=36, hroll=8)), (2.05, st(hpitch=38, spine=10, eyes=1.5)),
            (nf / core.FPS, st(hpitch=38, spine=11, eyes=1.5))])
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
    fp = (-67.3, -5.7)                      # the friend out of the side street, visible past the fat man
    fr = Actor("friend", COST["friend"], nf); fr.hold(0, nf / core.FPS, pose("stand", x=fp[0], y=fp[1], yaw=fdir(fp, O_DOWN), hpitch=15))
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
            "callbacks": [PR.chest(case, him, low=0.3)]}

def grip_arm(fa, him, release=None):
    """The fat person's right arm, the fist closed on the old man's collar (the shapes have no arms of their own).
    release (t0, t1): from t0 the collar slides out of the fist; the hand stays in the air and slowly opens and sinks.
    Returns (sticks, callback); call after the set is built."""
    if fa.J is None: fa.compute()
    if him.J is None: him.compute()
    def collar(f):
        J = him.J[min(f, him.nf - 1)]; up = J[NECK] - J[PELVIS]; up = up / np.linalg.norm(up)
        fwd = J[NOSE] - J[HEAD]; fwd = fwd - up * np.dot(fwd, up); fwd = fwd / np.linalg.norm(fwd)
        return J[NECK] + fwd * 0.14 - up * 0.08
    def fist(f):
        t = f / core.FPS
        if release is None or t <= release[0]: return collar(f)
        c0 = collar(F(release[0])); u = min(1.0, (t - release[0]) / (release[1] - release[0])); k = u * u * (3 - 2 * u)
        return c0 + np.array((-0.08 * k, -0.03 * k, -0.18 * k))
    def joints(f):
        J = fa.J[min(f, fa.nf - 1)]; up = J[NECK] - J[PELVIS]; up = up / np.linalg.norm(up)
        out = J[RSH] - J[LSH]; out = out / np.linalg.norm(out)
        sh = J[RSH] + out * 0.05; h = fist(f); el = (sh + h) / 2 - up * 0.17 + out * 0.1
        return sh, el, h
    col = COST["fat"]["skin"]
    ua = Stick("fat_ua", 0.07, col, lambda f: joints(f)[:2]); fo = Stick("fat_fa", 0.058, col, lambda f: joints(f)[1:])
    ball = _obj("fat_fist", _mesh_sphere("fat_fist", 0.065, 1.0, 1.15, 0.95, seg=10, rings=7), col)
    def cb(f):
        sh, el, h = joints(f); ball.location = tuple(h)
    return [ua, fo], cb

def S04_SH120(nf):
    """Close on the old man: the reverse of SH110 on the same side of the line (from the north, past the fat person's
    left shoulder, which stays out of frame). Same lens and feel as the d9 SH120. He says nothing; the fat person's line
    comes from off screen, camera side. The fat person's fist holds his collar."""
    T = nf / core.FPS
    street((GRIP_HIM[0] - 1.2, GRIP_HIM[1] + 0.75, 1.75))       # the set first: the sidewalk lifts the figures
    him, fa = grip_pair(nf, haul=False); fa.talk(0.3, 5.7)
    him.overlays.append((0, nf, lambda f, q: dict(q, hpitch=-9, hyaw=4)))
    him.face(2.6, 2.75, eyes=0.1); him.face(4.9, 5.05, eyes=0.1)
    him.compute(); fa.compute()
    h = him.J[0, HEAD]; a = math.radians(36)
    p = (h[0] - 1.6 * math.cos(a), h[1] + 1.6 * math.sin(a), h[2] + 0.1)
    sticks, arm = grip_arm(fa, him)
    case = PR.hand_prop("case", "case")
    return {"cam": cam(p, tuple(h + np.array((0, 0, -0.065))), 70, hh=0.5, focus=(him, HEAD), fstop=1.8), "actors": [him, fa],
            "speakers": {"FAT PERSON": fa}, "say": [[0.3, 5.7, "FAT PERSON"]], "sticks": sticks, "callbacks": [arm, PR.chest(case, him, low=0.3)]}

def S04_SH130(nf):
    """Low, looking up at the facade above them (north side of the street, same side of the line): the watchers are
    already at their windows and on their balconies in the first frame; nobody appears. A few turn their heads a little.
    The windows are the set's own (columns x -63.86, -60.86, -57.86, -52.75; floors 3.2, 6.2, 9.2, 12.2); three get a
    balcony."""
    p = (-60.0, -3.0, 0.45); street(p)
    acts = []; mb = core.MB(None, detail=False); T = nf / core.FPS; k = 0
    def person(x, y, fz, out):
        nonlocal k
        a = Actor(f"w{k}", crowd_costume(random.Random(70 + k)), nf, lod="high"); k += 1
        if out:      # standing on a balcony, leaning on the railing
            a.hold(0, T + 1, pose("stand", x=x, y=y, yaw=180, z=fz + 0.14 + 0.93, spine=16, hpitch=40, la=(50, 8, 30), ra=(50, 8, 30)))
        else:        # leaning out of the window
            a.hold(0, T + 1, pose("stand", x=x, y=y, yaw=180, z=fz + 0.95, spine=32, hpitch=32, la=(40, 10, 40), ra=(40, 10, 40)))
        acts.append(a)
    for (x, fz, n) in ((-63.86, 6.2, 2), (-57.86, 6.2, 1), (-60.86, 12.2, 1)):
        mb.box(x - 1.25, x + 1.25, 4.5, 5.5, fz, fz + 0.14, PAL["balcony"]); mb.box(x - 1.25, x + 1.25, 4.5, 4.56, fz + 0.14, fz + 1.0, PAL["balcony"])
        for j in range(n):
            person(x + (0.0 if n == 1 else -0.45 + 0.9 * j), 4.95, fz, True)
    for (x, fz) in ((-60.86, 6.2), (-57.86, 9.2), (-63.86, 9.2), (-52.75, 6.2), (-52.75, 12.2)):
        person(x, 5.75, fz, False)
    person(-68.4, 4.95, 9.2, True)                                          # on an existing balcony, left
    mb.build("balconies")
    for i, t0 in ((0, 0.4), (3, 0.9), (5, 0.6), (7, 1.1)):
        acts[i].look(t0, T + 1, (-65.0, -4.8, -8.0), strength=0.6)
    h, f2 = grip_pair(nf, haul=False); acts += [h, f2]
    return {"cam": cam(p, (-60.6, 5.5, 8.4), 34), "actors": acts, "cues": [[0, 2, "SILENCE ABOVE. A SHUTTER CREAKS"]]}

def S04_SH135(nf):
    """Over the fat person's left shoulder onto the old man (same side of the line as SH110 and SH120). Cordial, almost
    apologetic, slowly, gently, he slides himself out of the grip: a small bow, he lowers himself and eases back and to
    his left; the collar slides out of the fist, which stays in the air and sinks. Coverage of the slide in SH140."""
    T = nf / core.FPS; g = GRIP_HIM
    p = (GRIP_FAT[0] - 0.9, GRIP_FAT[1] + 0.65, 1.95); street(p)
    def st(dx=0.0, dy=0.0, yaw=90, **kw):
        return pose("stand", x=g[0] + dx, y=g[1] + dy, yaw=yaw, **kw)
    bend = dict(ll=(24, 4, 40), rl=(24, 4, 40))
    him = Actor("him", COST["him"], nf)
    him.seq([(0, st(spine=-8, hpitch=-9)), (0.5, st(spine=-7, hpitch=-9)), (1.4, st(0.07, -0.03, spine=9, hpitch=7, **bend)),
             (2.4, st(0.36, -0.15, yaw=82, spine=11, hpitch=-1, **bend)), (T + 0.5, st(0.46, -0.2, yaw=80, spine=10, hpitch=-4, **bend))])
    fa = Actor("fat", COST["fat"], nf)
    fb = dict(x=GRIP_FAT[0], y=GRIP_FAT[1], yaw=-90)
    fa.seq([(0, pose("stand", **fb, spine=8, hpitch=18)), (1.5, pose("stand", **fb, spine=8, hpitch=18)), (T + 0.5, pose("stand", **fb, spine=5, hpitch=11, hyaw=-7))])
    him.compute(); fa.compute()
    sticks, arm = grip_arm(fa, him, release=(1.3, 3.0))
    case = PR.hand_prop("case", "case")
    return {"cam": cam(p, (-64.8, -4.7, 1.77), 45, hh=0.6, focus=(him, HEAD), fstop=2.0), "actors": [him, fa],
            "sticks": sticks, "callbacks": [arm, PR.chest(case, him, low=0.3)]}

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
            "callbacks": [PR.chest(case, him, low=0.3)]}
