from sh import *

CUES = {"S03_SH040": [[0, 1, "BEEP"], [2, 3, "LAST CLAP"]]}
CAR = (0.0, 1.0); YAW = 90.0

def town(eye, sky="day"):
    reset(sky); return sets.avenue(eye)

def S03_SH010(nf):
    p0 = (121.5, 13.2, 1.45); town(p0)
    c = PR.car("car"); path = lambda t: ((120 - 2.0 * t, 3.0), YAW)
    him = Actor("him", COST["him"], nf); ride(him, 0, 6, path)
    return {"cam": move([(0, p0, (120, 3.0, 1.1), 45), (6, (109.5, 13.2, 1.45), (108, 3.0, 1.1), 45)], ease="lin"),
            "actors": [him], "callbacks": [car_cb(c, path)], "cues": [[0, 6, "THE SAME NEWS FROM WINDOW TO WINDOW"]]}

def S03_SH020(nf):
    pos = (60.0, 3.0); p = tuple(PR.car_world(pos, YAW, 1.45, 0.62, 1.25)); town(p)
    c = PR.car("car"); PR.place(c, (pos[0], pos[1], 0), YAW)
    case = PR.briefcase("case"); w = PR.car_world(pos, YAW, 0.42, -0.2, 0.6); PR.place(case, (w[0], w[1], 0.6), YAW + 90)
    him = Actor("him", COST["him"], nf)
    base = PR.car_world(pos, YAW, -0.42, -0.25)
    seat = dict(x=float(base[0]), y=float(base[1]), yaw=YAW)
    him.seq([(0, pose("drive", **seat)), (0.5, pose("drive", **seat, hyaw=-55, hpitch=20)), (2.2, pose("drive", **seat, hyaw=-55, hpitch=20)),
             (2.8, pose("drive", **seat)), (6.8, pose("drive", **seat)), (7.4, pose("drive", **seat, hpitch=-8, eyes=1.4))])
    him.talk(0.4, 7.6)
    head = PR.car_world(pos, YAW, -0.42, -0.3, 1.3)
    return {"cam": cam(p, tuple(head), 32), "actors": [him], "speakers": {"OLD MAN": him}, "say": [[0.4, 7.6, "OLD MAN"]], "cues": [[7, 8, "ENGINE POPS"]]}

def S03_SH030(nf):
    p = (-3.3, -0.65, 0.25); town(p)
    c = PR.car("car")
    def path(t):
        u = min(1.0, t / 1.6); u = 1 - (1 - u) ** 2
        return ((7.0 - 7.0 * u, 1.0), YAW)
    return {"cam": cam(p, (-1.55, 0.15, 0.36), 28), "callbacks": [car_cb(c, path)], "cues": [[1.5, 2, "THE CAR STOPS"]]}

def S03_SH050(nf):
    p = (24.0, -14.2, 16.6); reset("day"); sets.avenue(p, clear=[(24.0, -14.5, 16.0, 14.0)])
    # balcony: floor under the camera, railing square to the view, low enough to stay a thin band at the bottom edge
    tgt = np.array((-4.0, 1.0, 0.5)); d = (tgt[:2] - np.array(p[:2])); d /= np.linalg.norm(d); perp = np.array((-d[1], d[0]))
    pitch = math.degrees(math.atan2(p[2] - tgt[2], np.linalg.norm(tgt[:2] - np.array(p[:2]))))
    half_v = math.degrees(math.atan(36 / (1120 / 480) / 2 / 28)); edge = pitch + half_v - 1.8
    top = p[2] - 0.65 * math.tan(math.radians(edge)); c = np.array(p[:2]) + d * 0.65
    R = np.stack([np.append(perp, 0), np.append(d, 0), np.array((0, 0, 1.0))], axis=1)
    mb = core.MB(None, detail=False)
    mb.box(21.5, 26.5, -14.5, -13.3, 14.85, 15.0, PAL["balcony"])
    mb.obox((c[0], c[1], (15.0 + top) / 2), (3.0, 0.07, top - 15.0), R, PAL["balcony"])
    mb.build("own_balcony")
    c = PR.car("car"); PR.place(c, (CAR[0], CAR[1], 0), YAW)
    def door(f):
        t = f / core.FPS; u = min(1, max(0, (t - 5.0) / 0.6)); PR.set_door(c, u * u * (3 - 2 * u))
    him = Actor("him", COST["him"], nf)
    seatw = PR.car_world(CAR, YAW, -0.42, -0.25)
    him.hold(0, 5.4, pose("drive", x=float(seatw[0]), y=float(seatw[1]), yaw=YAW))
    out = PR.car_world(CAR, YAW, -1.35, 0.35)
    him.seq([(5.4, pose("stand", x=float(out[0]), y=float(out[1]), yaw=180)), (6.2, pose("stand", x=float(out[0]), y=float(out[1]), yaw=230)),
             (7.2, pose("stand", x=float(out[0]), y=float(out[1]), yaw=130)), (8.4, pose("stand", x=float(out[0]), y=float(out[1]), yaw=150)),
             (9.0, pose("stand", x=float(out[0]) - 0.3, y=float(out[1]), yaw=90))], blend=0.3)
    him.path(9.0, 14.0, [(out[0] - 0.3, out[1]), (-6.0, -0.8), (-9.8, -1.4)], "walk", speed="in")
    him.talk(7.0, 8.6)
    case = PR.hand_prop("case", "case")
    return {"cam": cam(p, tuple(tgt), 28, hh=0.25), "actors": [him], "speakers": {"OLD MAN": him}, "say": [[7.0, 8.6, "OLD MAN"]],
            "callbacks": [door, PR.attach(case, him, offset=(0, 0, 0.02), visible=lambda f: f >= F(8.6))],
            "cues": [[0, 3, "CLAP ECHOES OFF THE BUILDINGS, FADES"], [3, 5, "SILENCE"], [0, 14, "cigarette smoke drifts across the foreground"]]}
