from sh import *

CUES = {"S02_SH080": [[0, 2, "TIRES SKID ON DIRT"]], "S02_SH150": [[0, 2, "ENGINE IDLE"]], "S02_SH170": [[0, 2, "ENGINE IDLE"]],
        "S02_SH190": [[0, 2, "ENGINE REVS SOFTLY"]]}
STOP = (7.0, 0.0); YAW = 90.0                       # the car stops a few meters from the wall, facing the gap (west)
EYE = tuple(PR.car_world(STOP, YAW, -0.42, -0.25, 1.32))
HEADP = tuple(PR.car_world(STOP, YAW, -0.42, -0.3, 1.3))
DOG = (44.5, -18.2)

def town(eye):
    reset("day"); return sets.desert(eye)

def parked(nf, **kw):
    c = PR.car("car"); PR.place(c, (STOP[0], STOP[1], 0), YAW)
    him = Actor("him", COST["him"], nf)
    ride(him, 0, nf / core.FPS, lambda t: (STOP, YAW), **kw)
    return c, him

def _seat():
    w = PR.car_world(STOP, YAW, -0.42, -0.25)
    return dict(x=float(w[0]), y=float(w[1]), yaw=YAW)

def driving(x0, speed):
    """The car on the dirt road toward the town, with a little road bounce."""
    def path(t):
        return ((x0 - speed * t, 0.0), YAW)
    return path

def onboard(path, local_pos, local_tgt, lens, shake=0.012):
    """A camera fixed inside the moving car (road vibration)."""
    def fn(t):
        (pos, yaw) = path(t)
        jig = np.array((math.sin(t * 31) * shake, math.sin(t * 23 + 1) * shake, math.sin(t * 37 + 2) * shake * 1.5))
        p = PR.car_world(pos, yaw, *local_pos) + jig; q = PR.car_world(pos, yaw, *local_tgt)
        return p, q, lens, 0
    return {"fn": fn}

def S02_SH010(nf):
    p = (230, 30, 2.5); town(p)
    return {"cam": cam(p, (0, 0, 12), 55), "cues": [[0, 4, "HARD CUT TO SILENCE"]]}

def S02_SH020(nf):
    p = (41.2, -15.2, 0.7); town(p)
    return {"cam": cam(p, (44.5, -18.4, 0.25), 40), "callbacks": [PR.dog("dog", DOG, 120)], "cues": [[0, 3, "HEAT, FLIES"]]}

def S02_SH030(nf):
    p = (62, 2.0, 1.4); town(p)
    c = PR.car("car"); path = lambda t: ((700 - 26 * t, 0.0), YAW)
    return {"cam": cam(p, (640, 0, 1.4), 300), "callbacks": [car_cb(c, path), PR.dust("dust", 14, lambda t: (700 - 26 * t + 4, 0.0), size=2.2)],
            "cues": [[0, 5, "HEAT SHIMMER, ENGINE FAINT"]]}

def S02_SH040(nf):
    """Close on the dog: it lifts its head toward the engine (the end of the SH020 take)."""
    head = (44.5 - 0.866 * 0.4, -18.2 - 0.5 * 0.4, 0.3)
    p = (head[0] - 0.55, head[1] + 1.05, 0.34); town(p)
    return {"cam": cam(p, head, 55), "callbacks": [PR.dog("dog", DOG, 120, head_up_t=0.4)], "cues": [[0, 2, "THE ENGINE, CLOSER"]]}

def S02_SH050(nf):
    """Low on the road, the town on the horizon; the car comes from behind, hits a bump and flies over the lens."""
    p = (95, 0.0, 0.18); town(p)
    c = PR.car("car")
    x_at = lambda t: 140 - 30 * t
    def cb(f):
        t = f / core.FPS; x = x_at(t)
        u = (x - 97.5) / 7.0; z = max(0.0, 0.55 * (1 - u * u))                 # airborne for ~7 m around the bump
        pitch = math.radians(-6 * u) if z > 0 else 0.0
        PR.place(c, (x, 0.0, z), YAW, extra=Matrix.Rotation(pitch, 4, "X"))
    return {"cam": cam(p, (0, 0, 2.5), 24), "callbacks": [cb],
            "cues": [[0.6, 1.4, "ROAR OVERHEAD"]]}

def S02_SH060(nf):
    """Driving: the bobblehead nods hard with every bump."""
    path = driving(160, 20); p0 = PR.car_world((160, 0), YAW, -0.42, -0.25, 1.3); town(tuple(p0))
    c = PR.car("car")
    return {"cam": onboard(path, (-0.05, 0.55, 1.22), (0.38, 1.08, 1.12), 42), "callbacks": [car_cb(c, path), PR.bob_nod(c, lambda t: 28)],
            "cues": [[0, 2, "ENGINE STRAINING, GRAVEL"]]}

def S02_SH070(nf):
    """Driving: the briefcase bounces on the passenger seat."""
    path = driving(140, 20); p0 = PR.car_world((140, 0), YAW, -0.42, -0.25, 1.3); town(tuple(p0))
    c = PR.car("car"); case = PR.briefcase("case")
    def cb(f):
        t = f / core.FPS; (pos, yaw) = path(t)
        w = PR.car_world(pos, yaw, 0.42, -0.2, 0.6 + 0.035 * abs(math.sin(t * 13)))
        PR.place(case, (w[0], w[1], w[2]), yaw + 90 + 4 * math.sin(t * 9))
    return {"cam": onboard(path, (-0.3, 0.1, 1.25), (0.42, -0.2, 0.75), 30), "callbacks": [car_cb(c, path), cb]}

def S02_SH080(nf):
    """Ground level: the front wheel locks and slides to a stop a few meters from the wall."""
    p = (2.4, -2.3, 0.22); town(p)
    c = PR.car("car")
    def path(t):
        u = min(1.0, t / 1.6); return ((STOP[0] + 9.6 * (1 - u) ** 2, STOP[1]), YAW)
    return {"cam": cam(p, (5.45, -0.95, 0.4), 32), "callbacks": [car_cb(c, path)]}

def S02_SH090(nf):
    p = tuple(PR.car_world(STOP, YAW, -0.42, 4.3, 1.3)); town(p)
    c, him = parked(nf)
    him.seq([(0, pose("drive", **_seat(), hpitch=35, eyes=0.7)), (0.6, pose("drive", **_seat(), hpitch=35, eyes=0.7)),
             (2.6, pose("drive", **_seat(), hpitch=0, eyes=1.3))])
    return {"cam": cam(p, HEADP, 50), "actors": [him], "callbacks": [PR.bob_nod(c, lambda t: 4)]}

def S02_SH100(nf):
    """POV dolly zoom: the gap keeps its size while the main road beyond it stretches away."""
    town(EYE)
    d0 = EYE[0] + 17.0
    return {"cam": move([(0, (d0, EYE[1], EYE[2]), (-200, 0, 3), 85), (4, EYE, (-200, 0, 3), 85 * EYE[0] / d0)], ease="io")}

def lean_look(nf, first, second=None, t_switch=None):
    """From the passenger seat, low: he leans over the wheel and looks out one side (then the other: one take)."""
    p = tuple(PR.car_world(STOP, YAW, 0.35, 0.05, 1.02)); town(p)
    c, him = parked(nf)
    lean = dict(spine=18)
    keys = [(0.0, pose("drive", **_seat())), (0.6, pose("drive", **_seat(), **lean, **first))]
    if second:
        keys += [(t_switch, pose("drive", **_seat(), **lean, **first)), (t_switch + 0.6, pose("drive", **_seat(), **lean, **second))]
    him.seq(keys); him.compute()
    tgt = him.J[min(nf - 1, F(0.8)), HEAD] + np.array((0, 0, -0.05))
    p = tuple(PR.car_world(STOP, YAW, 0.38, 0.38, 1.02))
    return {"cam": cam(p, tuple(tgt), 28), "actors": [him], "callbacks": [PR.bob_nod(c, lambda t: 3)]}

def S02_SH110(nf): return lean_look(nf, dict(hyaw=70))
def S02_SH130(nf): return lean_look(nf, dict(hyaw=70), dict(hyaw=-70), 0.0)
def S02_SH160(nf): return lean_look(nf, dict(hpitch=32, hyaw=0))

def S02_SH120(nf):
    """His POV through the driver window: the wall a few meters off, running away to the left."""
    town(EYE); c = PR.car("car"); PR.place(c, (STOP[0], STOP[1], 0), YAW)
    return {"cam": cam(EYE, (-6.0, -14.0, 2.4), 30)}

def S02_SH140(nf):
    """His POV through the passenger window, past the briefcase: the wall running to the horizon."""
    town(EYE); c = PR.car("car"); PR.place(c, (STOP[0], STOP[1], 0), YAW)
    case = PR.briefcase("case"); w = PR.car_world(STOP, YAW, 0.42, -0.2, 0.6); PR.place(case, (w[0], w[1], 0.6), YAW + 90)
    return {"cam": cam(EYE, (-6.0, 14.0, 2.2), 30)}

def S02_SH180(nf):
    p = tuple(PR.car_world(STOP, YAW, 0.45, -0.05, 1.28)); town(p)
    c, him = parked(nf)
    him.overlays.append((0, nf, lambda f, q: dict(q, spine=q["spine"] - 4 * math.sin(f / core.FPS * 2.2), hpitch=-6)))
    return {"cam": cam(p, HEADP, 35), "actors": [him]}

def S02_SH200(nf):
    p = (STOP[0] + 17, 1.6, 1.6); town(p)
    c = PR.car("car")
    def path(t):
        u = min(1.0, t / 5.0); x = STOP[0] - 70 * (u * u)
        return ((x, 0.0), YAW)
    him = Actor("him", COST["him"], nf); ride(him, 0, 5, path)
    return {"cam": cam(p, (0, 0, 4), 32), "actors": [him], "callbacks": [car_cb(c, path)]}
