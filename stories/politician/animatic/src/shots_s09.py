from sh import *
from shots_s05 import SQ_WALLS, CASE_AT
from shots_s07 import ARM, TOP, PIPE_AT, fat_death, bodies_s07
import phys

CUES = {"S09_SH030": [[0, 3, "ROTORS WINDING DOWN"]], "S09_SH070": [[0, 2, "ROTORS"]]}
SEAT = (-39.6, -6.55)            # on the road, back against the corner curb (y = -7)
CASE = CASE_AT                   # the case lies where it fell when the rock hit him
HIMC = (CASE[0] + 0.6, CASE[1] - 0.3)
PAD = (-24.0, 0.5)               # helicopter in the square; door faces west
DOOR = (-25.6, 1.0)
LADYC = (-28.0, 0.6)             # she stays a few steps from the helicopter
MEET = (LADYC[0] - 0.95, LADYC[1] - 0.05)   # where he stops in front of her

def sq(eye, sky="sunset"):
    reset(sky); return sets.square(eye)

def sniper_bodies(nf):
    try:
        from shots_s08 import sniper_dead
        return sniper_dead(nf)
    except Exception:
        return []

def scenery(nf, case=True, case_open=True):
    acts = bodies_s07(nf) + sniper_bodies(nf)
    if case:
        c = PR.briefcase("case", opened=case_open); PR.place(c, (CASE[0], CASE[1], 0.0), 80)
    return acts

def heli_landed(yaw=180.0):
    h = PR.heli("heli"); return h, PR.heli_cb(h, lambda t: (np.array((PAD[0], PAD[1], 0.0)), yaw, 0.0))

def S09_SH010(nf):
    """The rope goes: he drops beside the curb, curls up facing the camera, shaking; leans back on his elbows; spits on the fat man."""
    p = (-39.4, 8.4, 0.22); sq(p)
    JA = phys.drop(1.6)
    him = Actor("him", COST["him"], nf); him.joints(0, JA)
    curl = pose("lie_curl", x=SEAT[0], y=SEAT[1] + 0.45, yaw=-90)
    lean = pose("lean_curb", x=SEAT[0], y=SEAT[1], yaw=0)
    side = dict(lean, roll=-14, hyaw=-70, spine=14, la=(-40, 30, 80))
    him.seq([(1.6, curl), (4.4, curl), (7.3, curl), (10.0, lean), (13.4, dict(lean, hpitch=-30)), (14.6, dict(side, hpitch=12, spine=16)),
             (15.0, dict(side, hpitch=22, spine=24)), (15.4, dict(side, hpitch=8)), (18.0, dict(side, hpitch=10))], blend=0.6)
    him.overlays.append((F(4.4), F(7.3), lambda f, q: dict(q, spine=q["spine"] + 4 * math.sin(f * 2.3))))
    him.overlays.append((F(10.0), F(13.4), lambda f, q: dict(q, spine=q["spine"] - 5 * math.sin(f / core.FPS * 3.0))))
    him.talk(0.6, 4.2); him.face(13.6, 14.4, mouth=0.15); him.face(14.9, 15.2, mouth=0.9)
    rope = Stick("rope", 0.018, PAL["rope"], lambda f: (tuple(ARM), tuple(TOP)) if f < F(0.3) else (tuple(ARM), tuple(ARM - np.array((0, 0, 1.0)))))
    return {"cam": cam(p, (SEAT[0] + 0.4, SEAT[1], 0.45), 135), "actors": [him] + scenery(nf, case=False), "sticks": [rope], "speakers": {"OLD MAN": him},
            "say": [[0.6, 4.2, "OLD MAN"]], "cues": [[0.3, 0.9, "THE ROPE GOES, HE HITS THE ASPHALT"], [4.4, 7.3, "THE STAIN SPREADS"],
                                                    [10.0, 13.4, "HE BREATHES. LOOKS AT THE SKY"], [14.9, 15.4, "SPIT"]]}

def S09_SH020(nf):
    """Low, the open case in the foreground; far back he gets up and limps to it; the helicopter comes down; the paper flies."""
    p = (CASE[0] - 1.8, CASE[1] + 0.45, 0.35); sq(p)
    him = Actor("him", COST["him"], nf)
    lean = pose("lean_curb", x=SEAT[0], y=SEAT[1], yaw=0)
    him.seq([(0, lean), (1.0, lean), (2.0, pose("hands_knees", x=SEAT[0], y=SEAT[1] + 0.3, yaw=fdir(SEAT, HIMC))),
             (3.0, pose("kneel", x=SEAT[0] - 0.1, y=SEAT[1] + 0.4, yaw=fdir(SEAT, HIMC))), (3.8, pose("stand", x=SEAT[0] - 0.2, y=SEAT[1] + 0.45, yaw=fdir(SEAT, HIMC)))])
    him.path(3.8, 12.4, [(SEAT[0] - 0.2, SEAT[1] + 0.45), (-45.0, -4.2), HIMC], "limp", speed="io")
    him.blend(12.4, 13.0, pose("stand", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, CASE)), pose("crouch", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, CASE)))
    h = PR.heli("heli")
    def hpath(t):
        u = min(1.0, max(0.0, (t - 0.5) / 9.0)); u = 1 - (1 - u) ** 2.2
        return np.array((PAD[0] + 8 * (1 - u), PAD[1], 32 * (1 - u))), 180.0 + 10 * (1 - u), 4 * (1 - u)
    paper = PR.papers("bond", 70, (-44.0, -3.0), 7, 4.0, 13.0, rise=4.0, seed=7, drift=(-6, 0))
    return {"cam": cam(p, (-36.0, -4.5, 1.6), 24), "actors": [him] + scenery(nf), "callbacks": [PR.heli_cb(h, hpath), paper], "cues": [[0, 13, "ROTOR WASH GROWS"]]}

def S09_SH040(nf):
    """Wide: she steps out low under the rotors and stops a few steps from the helicopter. He limps toward her."""
    p = (-27.0, 24.0, 2.6); sq(p)
    h, hcb = heli_landed()
    him = Actor("him", COST["him"], nf); him.path(0, 4, [(-41.0, -1.4), (-37.0, -0.9)], "limp", speed="lin")
    la = Actor("lady", COST["lady"], nf)
    la.seq([(0, pose("crouch", x=DOOR[0], y=DOOR[1], yaw=fdir(DOOR, (-40, -1)))), (0.6, pose("crouch", x=DOOR[0] - 0.6, y=DOOR[1], yaw=fdir(DOOR, (-40, -1))))])
    la.path(0.6, 2.6, [(DOOR[0] - 0.6, DOOR[1]), LADYC], "walk", speed="io", base=dict(spine=14))
    la.hold(2.6, 4.0, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, (-37, -0.9))))
    folder = PR.hand_prop("folder", "folder")
    paper = PR.papers("bond", 50, (-40.0, -1.0), 8, 0.0, 4.0, rise=2.5, seed=9, drift=(-3, 0))
    return {"cam": cam(p, (-33.0, -0.5, 1.2), 24), "actors": [him, la] + scenery(nf), "callbacks": [hcb, paper, PR.chest(folder, him, out=0.18)], "cues": [[0, 4, "ROTORS"]]}

def lady(nf, **kw):
    a = Actor("lady", COST["lady"], nf); a.hold(0, nf / core.FPS, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, MEET), **kw)); return a

def S09_SH050(nf):
    """Medium on him over her shoulders (her back to us): he limps up to her and holds out the folder."""
    p = (LADYC[0] + 1.25, LADYC[1] + 0.55, 1.62); sq(p)
    h, hcb = heli_landed()
    him = Actor("him", COST["him"], nf)
    him.path(0, 3.6, [(MEET[0] - 4.2, MEET[1] - 0.3), MEET], "limp", speed="out")
    him.blend(3.6, 4.4, pose("stand", x=MEET[0], y=MEET[1], yaw=fdir(MEET, LADYC)), pose("stand", x=MEET[0], y=MEET[1], yaw=fdir(MEET, LADYC), ra=(75, 5, 15)))
    him.hold(4.4, 6.0, pose("stand", x=MEET[0], y=MEET[1], yaw=fdir(MEET, LADYC), ra=(75, 5, 15))); him.talk(3.2, 5.0)
    folder = PR.hand_prop("folder", "folder")
    def fcb(f):
        PR.chest(folder, him, out=0.18)(f) if f < F(3.8) else PR.attach(folder, him)(f)
    him.compute()
    return {"cam": cam(p, (MEET[0] - 0.4, MEET[1], 1.5), 40, focus=(him, HEAD), fstop=2.4), "actors": [him, lady(nf)] + scenery(nf), "callbacks": [hcb, fcb],
            "speakers": {"OLD MAN": him}, "say": [[3.2, 5.0, "OLD MAN"]]}

FRAME_A = ((LADYC[0] - 1.7, LADYC[1] + 0.75, 1.62), 50)     # close on her from his side; the helicopter behind her
def her_close(nf, la, extra=(), focus=None, cbs=()):
    la.compute(); h = la.J[0, HEAD]
    return {"cam": cam(FRAME_A[0], tuple(h + np.array((0.0, 0.0, -0.05))), FRAME_A[1], focus=focus or (la, HEAD), fstop=2.0),
            "actors": [la] + list(extra) + scenery(nf), "callbacks": list(cbs)}

def S09_SH060(nf):
    """Close on her, the helicopter behind: she takes the folder and opens it to the last page. Silence."""
    sq(FRAME_A[0]); h, hcb = heli_landed()
    la = Actor("lady", COST["lady"], nf)
    la.seq([(0, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, MEET))), (1.0, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, MEET), ra=(60, 5, 60))),
            (2.0, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, MEET), ra=(55, 5, 70), la=(55, 5, 70), hpitch=30))])
    folder = PR.hand_prop("folder", "folder")
    return her_close(nf, la, cbs=[hcb, PR.attach(folder, la)])

def S09_SH080(nf):
    sq(FRAME_A[0]); h, hcb = heli_landed()
    la = lady(nf, ra=(50, 5, 70), la=(50, 5, 70)); la.face(1.4, 2.0, mouth=0.3)
    folder = PR.hand_prop("folder", "folder")
    return her_close(nf, la, cbs=[hcb, PR.attach(folder, la)])

def S09_SH090(nf):
    """Close on him from her side: chin up, a challenge. Then he limps off toward the helicopter."""
    p = (MEET[0] + 1.35, MEET[1] + 0.65, 1.62); sq(p)
    h, hcb = heli_landed()
    him = Actor("him", COST["him"], nf); him.hold(0, 3.0, pose("stand", x=MEET[0], y=MEET[1], yaw=fdir(MEET, LADYC), hpitch=-12))
    him.path(3.0, 4.0, [MEET, (MEET[0] + 0.7, MEET[1] - 0.6)], "limp", speed="in")
    him.compute()
    return {"cam": cam(p, tuple(him.J[0, HEAD] + np.array((0, 0, -0.05))), 50, focus=(him, HEAD), fstop=2.0), "actors": [him, lady(nf)] + scenery(nf), "callbacks": [hcb]}

def S09_SH100(nf):
    """Same frame as her close-up: he limps past her to the door, half turns, says it out of focus; the focus pulls to her."""
    sq(FRAME_A[0]); h, hcb = heli_landed()
    la = lady(nf)
    him = Actor("him", COST["him"], nf)
    him.path(0, 3.8, [(MEET[0] + 0.7, MEET[1] - 0.6), (LADYC[0] + 0.8, LADYC[1] - 0.5), (DOOR[0] - 0.4, DOOR[1])], "limp", speed="io")
    him.blend(3.8, 4.4, pose("stand", x=DOOR[0] - 0.4, y=DOOR[1], yaw=-90), pose("point_chin", x=DOOR[0] - 0.4, y=DOOR[1], yaw=fdir(DOOR, LADYC) + 40))
    him.hold(4.4, 5.9, pose("point_chin", x=DOOR[0] - 0.4, y=DOOR[1], yaw=fdir(DOOR, LADYC) + 40)); him.talk(4.4, 5.8)
    him.blend(5.9, 6.8, pose("stand", x=DOOR[0] - 0.4, y=DOOR[1], yaw=-90), pose("stand", x=DOOR[0] + 0.3, y=DOOR[1], yaw=-90, z=0.6))
    d = her_close(nf, la, extra=[him], focus=[(0, (la, HEAD)), (1.2, (him, HEAD)), (5.7, (him, HEAD)), (6.4, (la, HEAD))], cbs=[hcb])
    d["speakers"] = {"OLD MAN": him}; d["say"] = [[4.4, 5.8, "OLD MAN"]]
    return d

def S09_SH110(nf):
    """Her point of view: the certificates flutter among the bodies in the rotor wash."""
    p = (LADYC[0] - 0.3, LADYC[1], 1.62); sq(p)
    h, hcb = heli_landed()
    paper = PR.papers("bond", 70, (-46.0, -2.5), 8, 0.0, 3.0, rise=1.5, seed=11, drift=(-2, 0))
    return {"cam": cam(p, (-50.0, -3.5, 0.4), 28), "actors": scenery(nf), "callbacks": [hcb, paper], "cues": [[0, 3, "ROTOR WASH, PAPER FLUTTERING"]]}

def S09_SH120(nf):
    """Close on her face, same frame: Not anymore. She turns and walks to the helicopter, slowly."""
    sq(FRAME_A[0]); h, hcb = heli_landed()
    la = Actor("lady", COST["lady"], nf)
    la.hold(0, 3.2, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, FRAME_A[0][:2]) + 25)); la.look(0.3, 3.2, (-50.0, -2.0, 0.3)); la.talk(1.4, 2.8)
    la.blend(3.2, 3.8, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, FRAME_A[0][:2]) + 25), pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, DOOR)))
    la.path(3.8, 6.0, [LADYC, (DOOR[0] - 0.5, DOOR[1])], "walk", speed="in")
    d = her_close(nf, la, cbs=[hcb]); d["speakers"] = {"BUSINESS LADY": la}; d["say"] = [[1.4, 2.8, "BUSINESS LADY"]]
    return d
