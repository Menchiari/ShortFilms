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
    him = Actor("him", COST["him"], nf); him.path(0, 4, [(-2, Y), (-9, Y)], "walk", speed="lin", base=dict(la=(55, 10, 110)))
    case = PR.hand_prop("case", "case")
    return {"cam": move([(0, p0, (-2.6, Y, 1.4), 35), (4, (-8.0, -1.4, 1.5), (-9.6, Y, 1.4), 35)], hh=0.6, ease="lin"), "actors": [him],
            "callbacks": [PR.attach(case, him, joint=LHA, elbow=LEL)], "cues": [[0, 4, "FOOTSTEPS, HEAVY BREATH, NOTHING ELSE"]]}

def S04_SH040(nf):
    p = (-72.0, 2.2, 2.0); street(p)
    him = Actor("him", COST["him"], nf); him.path(0, 4, [(-24, Y), (-31, Y)], "walk", speed="lin", base=dict(hpitch=20, la=(55, 10, 110)))
    return {"cam": cam(p, (-28, 0.2, 1.2), 100), "actors": [him] + barmen(nf), "cues": [[0, 4, "THE MEN TALK LOW"]]}

def S04_SH050(nf):
    p = (-34.0, 3.6, 1.25); street(p)
    him = Actor("him", COST["him"], nf); him.path(0, 2, [(-32.5, Y), (-36.0, Y)], "walk", speed="lin", base=dict(hpitch=20))
    bm = barmen(nf, look_from=0.5, target=(-35, Y, 1.6))
    return {"cam": cam(p, (-31.4, 4.7, 1.2), 70), "actors": [him] + bm, "cues": [[0.4, 2, "THE TALK STOPS"]]}

def S04_SH060(nf):
    p0 = (-35.8, -3.0, 1.6); street(p0)
    him = Actor("him", COST["him"], nf); him.path(0, 3, [(-34.5, Y), (-40.5, Y)], "walk", speed="in", base=dict(la=(55, 10, 110)))
    him.look(0.6, 1.5, (-31.4, 4.7, 1.2)); him.look(2.1, 2.9, (-31.4, 4.7, 1.2))
    case = PR.hand_prop("case", "case")
    return {"cam": move([(0, p0, (-34.5, Y, 1.55), 40), (3, (-41.8, -3.0, 1.6), (-40.5, Y, 1.55), 40)], hh=0.7, ease="in"),
            "actors": [him] + barmen(nf, look_from=0, target=(-38, Y, 1.6)), "callbacks": [PR.attach(case, him, joint=LHA, elbow=LEL)]}

_FALL = {}
def bump_fall():
    """Ragdoll: the old man bounces off the fat man and falls on his back. Shared by SH070 and SH080."""
    if "J" in _FALL:
        return _FALL["J"]
    p = dict(BASE); p.update(gait("walk", 1.0, 1.0)); p.update(x=-65.0, y=-4.6, yaw=90.0)
    J0 = fk(p)
    V0 = np.zeros_like(J0); V0[:, 0] = 2.6; V0[:, 2] = 0.6
    V0[HEAD] += (1.4, 0, 0.2); V0[NOSE] += (1.4, 0, 0.2); V0[LAN] = (-0.6, 0, 0); V0[RAN] = (-0.6, 0, 0)
    rd = Ragdoll(J0, V0)
    rd.muscles.append(toward([LHA, RHA], lambda t, x: x[HEAD] + np.array((0.0, 0, 0.1)) if t > 0.8 else None, 6))
    JA = rd.run(3.6)
    # settle into the FK lying pose
    end = fk(down_pose())
    n = len(JA); k0 = int(n * 0.6)
    for i in range(k0, n):
        u = (i - k0) / max(1, n - 1 - k0); u = u * u * (3 - 2 * u)
        JA[i] = JA[i] * (1 - u) + end * u
    _FALL["J"] = JA
    return JA

def S04_SH070(nf):
    p = (-57.0, 4.6, 1.6); street(p)
    him = Actor("him", COST["him"], nf)
    # cut half a second after the impact: SH080 picks the fall up from above
    him.path(0, 3.5, [(-56.5, Y), (-65.0, -4.6)], "jog", speed="lin", base=dict(la=(55, 10, 110)))
    him.over(0.3, 3.5, hyaw=-70, twist=-15)
    JA = bump_fall(); him.joints(3.5, JA[: F(0.5) + 1])
    fa = Actor("fat", COST["fat"], nf)
    fa.path(0, 3.5, [(-65.5, -10.5), (F_POS[0], F_POS[1])], "walk", speed="lin")
    fa.blend(3.5, 3.9, pose("stand", x=F_POS[0], y=F_POS[1], yaw=0), pose("stand", x=F_POS[0] - 0.15, y=F_POS[1], yaw=-30, spine=-6, la=(30, 20, 30), ra=(30, 20, 30)))
    fa.hold(3.9, 4.0, pose("stand", x=F_POS[0] - 0.15, y=F_POS[1], yaw=-30, spine=-6, la=(30, 20, 30), ra=(30, 20, 30)))
    case = PR.hand_prop("case", "case")
    return {"cam": follow(him, p, lens=85, offset=(0, 0, 0.5), lag=0.35, hh=0.4), "actors": [him, fa],
            "callbacks": [PR.attach(case, him, joint=LHA, elbow=LEL, visible=lambda f: f < F(3.6))], "cues": [[3.4, 3.8, "IMPACT"]]}

def S04_SH080(nf):
    p = (-63.2, -2.2, 5.2); street(p)
    him = Actor("him", COST["him"], nf); JA = bump_fall(); him.joints(0, JA[F(0.55):])
    fa = Actor("fat", COST["fat"], nf); fa.hold(0, 3, pose("stand", x=F_POS[0] - 0.15, y=F_POS[1], yaw=-60, spine=-4, hpitch=30))
    case = PR.briefcase("case"); PR.place(case, (-62.9, -4.2, 0.0), 30)
    return {"cam": cam(p, (-64.4, -4.7, 0.2), 30), "actors": [him, fa], "cues": [[0.3, 0.8, "THUD ON THE ASPHALT"]]}

def S04_SH090(nf):
    p = (O_DOWN[0] - 0.3, O_DOWN[1] + 0.55, 0.32); street(p)
    fa = fat(nf); fa.seq([(0, pose("stand", x=F_POS[0], y=F_POS[1], yaw=fdir(F_POS, O_DOWN), hpitch=35)),
                          (2.0, pose("stand", x=F_POS[0], y=F_POS[1], yaw=fdir(F_POS, O_DOWN), hpitch=38, spine=10, eyes=1.5))])
    fa.talk(2.2, 3.9)
    him = Actor("him", COST["him"], nf); him.hold(0, 4, down_pose())
    return {"cam": cam(p, (F_POS[0], F_POS[1], 1.85), 24, hh=0.4), "actors": [fa, him], "speakers": {"FAT PERSON": fa}, "say": [[2.2, 3.9, "FAT PERSON"]]}

def S04_SH100(nf):
    p = (-65.1, -3.9, 2.35); street(p)
    him = Actor("him", COST["him"], nf)
    him.seq([(0, down_pose()), (0.6, pose("lie_cover", x=O_DOWN[0], y=O_DOWN[1], yaw=90))])
    him.talk(1.0, 4.6)
    fa = fat(nf)
    return {"cam": cam(p, (O_DOWN[0] + 0.5, O_DOWN[1], 0.15), 28, hh=0.4), "actors": [him, fa], "speakers": {"OLD MAN": him}, "say": [[1.0, 4.6, "OLD MAN"]]}

def S04_SH110(nf):
    p = (-62.6, -3.2, 1.0); street(p)
    fa = fat(nf); fa.over(0, 7, hpitch=30, spine=8); fa.talk(0.4, 6.4)
    fr = friend(nf); fr.over(4.0, 7, ra=(60, 10, 120), la=(55, 10, 125), hpitch=30)
    him = Actor("him", COST["him"], nf); him.hold(0, 7, pose("lie_cover", x=O_DOWN[0], y=O_DOWN[1], yaw=90))
    phone = PR.hand_prop("phone", "phone")
    return {"cam": cam(p, (F_POS[0], F_POS[1], 1.75), 35, hh=0.5), "actors": [fa, fr, him], "speakers": {"FAT PERSON": fa}, "say": [[0.4, 6.4, "FAT PERSON"]],
            "callbacks": [PR.attach(phone, fr)]}

def S04_SH120(nf):
    p = (-64.3, -2.5, 1.6); street(p)
    him = Actor("him", COST["him"], nf)
    stand_at = (-64.55, -4.75)
    him.seq([(0, down_pose()), (0.5, pose("sit_ground", x=-64.2, y=-4.75, yaw=90)), (1.2, pose("stand", x=stand_at[0], y=stand_at[1], yaw=90, la=(60, 8, 100), ra=(55, 8, 100)))])
    fa = Actor("fat", COST["fat"], nf)
    fa.seq([(0, pose("stand", x=F_POS[0], y=F_POS[1], yaw=fdir(F_POS, O_DOWN), hpitch=30)), (0.4, pose("crouch", x=F_POS[0] + 0.1, y=F_POS[1], yaw=-90, la=(80, 5, 20), ra=(80, 5, 20))),
            (1.2, pose("stand", x=F_POS[0], y=F_POS[1], yaw=-90, la=(85, 5, 30), ra=(85, 5, 30))), (2.2, pose("stand", x=F_POS[0], y=F_POS[1], yaw=-90, la=(85, 5, 30), ra=(85, 5, 30), hpitch=35))])
    fa.talk(1.6, 4.8)
    case = PR.hand_prop("case", "case")
    return {"cam": cam(p, (-64.9, -4.8, 1.45), 32, hh=0.6), "actors": [him, fa], "speakers": {"FAT PERSON": fa}, "say": [[1.6, 4.8, "FAT PERSON"]],
            "callbacks": [PR.attach(case, him, joint=LHA, elbow=LEL)]}

def S04_SH130(nf):
    p = (-64.1, -4.25, 1.62); street(p)
    him = Actor("him", COST["him"], nf); him.hold(0, 6, pose("stand", x=-64.55, y=-4.75, yaw=90, la=(60, 8, 100), ra=(55, 8, 100)))
    fa = Actor("fat", COST["fat"], nf); fa.hold(0, 6, pose("stand", x=F_POS[0], y=F_POS[1], yaw=-90, la=(85, 5, 30), ra=(85, 5, 30), spine=10, hpitch=10)); fa.talk(0.3, 5.7)
    fa.compute(); hz = float(fa.J[0, HEAD, 2])
    return {"cam": cam(p, (F_POS[0], F_POS[1], hz - 0.1), 50, hh=0.5), "actors": [him, fa], "speakers": {"FAT PERSON": fa}, "say": [[0.3, 5.7, "FAT PERSON"]]}

def S04_SH140(nf):
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
    acts.append(fat(nf)); h = Actor("him", COST["him"], nf); h.hold(0, 2, pose("stand", x=-64.55, y=-4.75, yaw=90)); acts.append(h)
    return {"cam": cam(p, (-58.5, 5.5, 7.0), 45), "actors": acts, "cues": [[0, 2, "SHUTTERS OPEN ABOVE"]]}

def S04_SH150(nf):
    p = (-61.8, -2.0, 1.6); street(p)
    him = Actor("him", COST["him"], nf)
    him.seq([(0, pose("stand", x=-64.55, y=-4.75, yaw=90)), (0.5, pose("crouch", x=-64.4, y=-4.7, yaw=-60))])
    him.path(0.7, 4.0, [(-64.4, -4.7), (-62.5, -4.2), (-56.0, -4.0)], "run", speed="in")
    fa = Actor("fat", COST["fat"], nf)
    fa.seq([(0, pose("stand", x=F_POS[0], y=F_POS[1], yaw=-90, la=(85, 5, 30), ra=(85, 5, 30))), (0.8, pose("stand", x=F_POS[0], y=F_POS[1], yaw=-60))])
    fa.look(1.0, 4.0, (-56, -4, 1.6))
    fr = Actor("friend", COST["friend"], nf); fr.path(0, 3.5, [(-67.6, -7.6), (-66.4, -5.6)], "walk", speed="io")
    fr.talk(2.6, 4.0)
    return {"cam": cam(p, (-64.0, -4.6, 1.3), 30, hh=0.8), "actors": [him, fa, fr], "speakers": {"FRIEND": fr}, "say": [[2.6, 4.0, "FRIEND"]]}
