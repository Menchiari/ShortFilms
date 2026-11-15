from sh import *

CUES = {"S02_SH050": [[0, 2, "TIRES SKID ON DIRT"]], "S02_SH090": [[0, 2, "SILENCE, ENGINE IDLE"]],
        "S02_SH150": [[0, 2, "ENGINE IDLE"]], "S02_SH170": [[0, 2, "ENGINE IDLE"]], "S02_SH190": [[0, 2, "ENGINE REVS SOFTLY"]]}
STOP = (40.0, 0.0); YAW = 90.0
EYE = tuple(PR.car_world(STOP, YAW, -0.42, -0.25, 1.32))
HEADP = tuple(PR.car_world(STOP, YAW, -0.42, -0.3, 1.3))

def town(eye):
    reset("day"); return sets.desert(eye)

def parked(nf, **kw):
    c = PR.car("car"); PR.place(c, (STOP[0], STOP[1], 0), YAW)
    him = Actor("him", COST["him"], nf)
    ride(him, 0, nf / core.FPS, lambda t: (STOP, YAW), **kw)
    return c, him

def S02_SH010(nf):
    p = (230, 30, 2.5); town(p)
    return {"cam": cam(p, (0, 0, 12), 55), "cues": [[0, 4, "HARD CUT TO SILENCE"]]}

def S02_SH020(nf):
    p = (41.2, -15.2, 0.7); town(p)
    return {"cam": cam(p, (44.5, -18.4, 0.25), 40), "callbacks": [PR.dog("dog", (44.5, -18.2), 120)]}

def S02_SH030(nf):
    p = (62, 2.0, 1.4); town(p)
    c = PR.car("car"); path = lambda t: ((700 - 26 * t, 0.0), YAW)
    return {"cam": cam(p, (640, 0, 1.4), 300), "callbacks": [car_cb(c, path), PR.dust("dust", 14, lambda t: (700 - 26 * t + 4, 0.0), size=2.2)],
            "cues": [[0, 5, "HEAT SHIMMER, ENGINE FAINT"]]}

def S02_SH040(nf):
    p = (95, 0.0, 0.16); town(p)
    c = PR.car("car"); path = lambda t: ((150 - 55 * t, 0.0), YAW)
    return {"cam": cam(p, (140, 0, 1.0), 16), "callbacks": [car_cb(c, path)],
            "cues": [[0.7, 1.3, "ROAR OVERHEAD"]]}

def S02_SH060(nf):
    p = (41.2, -15.2, 0.7); town(p)
    return {"cam": cam(p, (44.5, -18.4, 0.25), 40), "callbacks": [PR.dog("dog", (44.5, -18.2), 120, head_up_t=0.5)]}

def S02_SH070(nf):
    p = tuple(PR.car_world(STOP, YAW, -0.42, 4.3, 1.3)); town(p)
    c, him = parked(nf)
    him.seq([(0, pose("drive", **{k: v for k, v in _seat().items()}, hpitch=35, eyes=0.7)), (0.6, pose("drive", **_seat(), hpitch=35, eyes=0.7)),
             (2.6, pose("drive", **_seat(), hpitch=0, eyes=1.3))])
    return {"cam": cam(p, HEADP, 50), "actors": [him]}

def _seat():
    w = PR.car_world(STOP, YAW, -0.42, -0.25)
    return dict(x=float(w[0]), y=float(w[1]), yaw=YAW)

def S02_SH080(nf):
    p = tuple(PR.car_world(STOP, YAW, 0.12, 0.5, 1.2)); town(p)
    c, him = parked(nf)
    tgt = tuple(PR.car_world(STOP, YAW, 0.38, 1.08, 1.12))
    return {"cam": cam(p, tgt, 40), "actors": [him], "callbacks": [PR.bob_nod(c, lambda t: 16)]}

def S02_SH100(nf):
    town(EYE)
    return {"cam": move([(0, EYE, (0, 0, 3), 85), (4, (16.0, EYE[1], EYE[2]), (0, 0, 3), 85 * 16 / 40.25)], ease="io")}

def look_shot(nf, **kw):
    p = tuple(PR.car_world(STOP, YAW, 0.28, 1.25, 1.24)); town(p)
    c, him = parked(nf)
    him.blend(0.2, 0.9, pose("drive", **_seat()), pose("drive", **_seat(), **kw))
    him.hold(0.9, 2.0, pose("drive", **_seat(), **kw))
    return {"cam": cam(p, HEADP, 42), "actors": [him], "callbacks": [PR.bob_nod(c, lambda t: 6)]}

def S02_SH110(nf): return look_shot(nf, hyaw=65)
def S02_SH130(nf): return look_shot(nf, hyaw=-65)
def S02_SH160(nf): return look_shot(nf, hpitch=30)

def S02_SH120(nf):
    town(EYE); return {"cam": cam(EYE, (12, -40, 3), 26)}

def S02_SH140(nf):
    town(EYE); return {"cam": cam(EYE, (12, 40, 3), 26)}

def S02_SH180(nf):
    p = tuple(PR.car_world(STOP, YAW, 0.45, -0.05, 1.28)); town(p)
    c, him = parked(nf)
    him.overlays.append((0, nf, lambda f, q: dict(q, spine=q["spine"] - 4 * math.sin(f / core.FPS * 2.2), hpitch=-6)))
    return {"cam": cam(p, HEADP, 35), "actors": [him]}

def S02_SH200(nf):
    p = (57, 1.6, 1.6); town(p)
    c = PR.car("car")
    def path(t):
        u = min(1.0, t / 5.0); x = 40 - 70 * (u * u)
        return ((x, 0.0), YAW)
    him = Actor("him", COST["him"], nf); ride(him, 0, 5, path)
    return {"cam": cam(p, (0, 0, 4), 32), "actors": [him], "callbacks": [car_cb(c, path)]}
