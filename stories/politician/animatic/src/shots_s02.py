from sh import *
from puppet import _obj, _mesh_sphere

CUES = {"S02_SH080": [[0, 1.6, "TIRES SKID ON DUSTY ASPHALT"]], "S02_SH150": [[0, 2, "ENGINE IDLE"]], "S02_SH170": [[0, 2, "ENGINE IDLE"]],
        "S02_SH190": [[0, 2, "ENGINE REVS SOFTLY"]]}
STOP = (7.0, 0.0); YAW = 90.0                       # the car stops a few meters from the wall, facing the gap (west)
EYE = tuple(PR.car_world(STOP, YAW, -0.42, -0.25, 1.32))
HEADP = tuple(PR.car_world(STOP, YAW, -0.42, -0.3, 1.3))
DOG = (44.5, -18.2)

def town(eye):
    reset("day"); return sets.desert(eye, edge="towers")

def open_cabin(c):
    """Interior shots: take the lid off the car's solid body box so the seats show (the cabin becomes a tub)."""
    import bmesh
    me = c.data; bm = bmesh.new(); bm.from_mesh(me)
    lid = [f for f in bm.faces if all(abs(v.co.z - 0.82) < 1e-4 for v in f.verts) and abs(f.calc_area() - 1.86 * 4.9) < 1e-3]
    bmesh.ops.delete(bm, geom=lid, context="FACES_ONLY"); bm.to_mesh(me); bm.free(); me.update()
    return c

def face_in(c):
    """The bobblehead turned on its base to face the driver's seat: it looks into the car, not out."""
    bob = bpy.data.objects[c["bobneck"]].parent
    d = (-0.42 - 0.38, -0.25 - 1.08)                    # from the dashboard spot to the driver's head (car local)
    bob.rotation_euler = (0, 0, math.atan2(-d[0], d[1]))
    return c

def flat_case(name, papers=True):
    """The briefcase lying flat (origin at the bottom center): 0.46 x 0.34 x 0.12, handle on the front edge, papers
    sticking out of the seam at the end that faces the driver (shut in a hurry)."""
    mb = core.MB(None, detail=False)
    mb.box(-0.23, 0.23, -0.17, 0.17, 0.0, 0.12, "#8A5A30")
    mb.box(-0.234, 0.234, -0.174, 0.174, 0.056, 0.064, "#5A3A20")            # the seam
    mb.box(-0.08, 0.08, 0.17, 0.215, 0.045, 0.075, "#5A3A20")                # the handle
    if papers:
        mb.obox((-0.25, 0.04, 0.06), (0.09, 0.2, 0.005), core.rotz(0.18), "#EDE6D2")
        mb.obox((-0.245, -0.09, 0.061), (0.07, 0.13, 0.005), core.rotz(-0.25), "#E2DAC4")
    return PR.mesh_obj(name, mb)

CASE_SEAT = (0.42, -0.17)                            # the case on the passenger seat cushion (car local, top at z 0.6)
CASE_FRONT = (0.43, -0.06, 6.0)                     # after the skid it has slid to the front edge of the cushion (x, y, yaw)

def parked(nf, **kw):
    c = face_in(PR.car("car")); PR.place(c, (STOP[0], STOP[1], 0), YAW)
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
    """Driving: the bobblehead faces into the car, toward the driver's seat, and nods hard with every bump."""
    path = driving(160, 20); p0 = PR.car_world((160, 0), YAW, -0.42, -0.25, 1.3); town(tuple(p0))
    c = face_in(PR.car("car"))
    return {"cam": onboard(path, (-0.05, 0.55, 1.22), (0.38, 1.08, 1.12), 42), "callbacks": [car_cb(c, path), PR.bob_nod(c, lambda t: 28)],
            "cues": [[0, 2, "ENGINE STRAINING, GRAVEL"]]}

def case_hops(seed=3, T=3.0):
    """The case lying loose on a seat that shakes on a dirt road: short ballistic hops (h = 2 to 6 cm, t = 2 sqrt(2h/g)),
    each landing a little turned and shifted."""
    rnd = random.Random(seed); t = 0.04; out = []; ox = oy = oa = 0.0
    while t < T:
        h = rnd.uniform(0.02, 0.06); d = 2 * math.sqrt(2 * h / 9.81)
        nx, ny, na = ox + rnd.uniform(-0.012, 0.012), oy + rnd.uniform(-0.006, 0.014), oa + rnd.uniform(-3.0, 3.0)
        out.append((t, d, h, (ox, oy, oa), (nx, ny, na), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
        ox, oy, oa = nx, ny, na; t += d + rnd.uniform(0.1, 0.28)
    def at(tt):
        base = (0.0, 0.0, 0.0)
        for (t0, d, h, a, b, sp, sr) in out:
            if tt < t0: return base[0], base[1], base[2], 0.0, 0.0, 0.0
            if tt < t0 + d:
                u = (tt - t0) / d; z = 4 * h * u * (1 - u); k = u * u * (3 - 2 * u)
                tilt = 0.9 * z / 0.23                                   # tilt only as far as the hop height allows
                return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k, z, tilt * sp, tilt * sr
            base = b
        return base[0], base[1], base[2], 0.0, 0.0, 0.0
    return at

def S02_SH070(nf):
    """Driving: the briefcase lies flat on the passenger seat cushion and bounces with the road."""
    path = driving(140, 20); p0 = PR.car_world((140, 0), YAW, -0.42, -0.25, 1.3); town(tuple(p0))
    c = open_cabin(face_in(PR.car("car"))); case = flat_case("case"); hop = case_hops()
    def cb(f):
        t = f / core.FPS; (pos, yaw) = path(t); dx, dy, da, z, pt, rl = hop(t)
        w = PR.car_world(pos, yaw, CASE_SEAT[0] + dx, CASE_SEAT[1] + dy, 0.6 + z)
        PR.place(case, (w[0], w[1], w[2]), yaw + 8 + da, extra=Matrix.Rotation(pt, 4, "X") @ Matrix.Rotation(rl, 4, "Y"))
    return {"cam": onboard(path, (-0.3, 0.1, 1.25), (0.42, -0.2, 0.62), 30), "callbacks": [car_cb(c, path), cb]}

MU = 0.55                                            # locked tires on asphalt under dust and sand
def skid(v0=8.0, t_lock=0.05, drift=2.5):
    """Locked wheels: constant deceleration MU*g to a stop at STOP. The body pitches on its suspension (a damped spring,
    1.4 Hz, damping 0.35) toward a nose-down angle proportional to the deceleration; when the car stops the braking force
    vanishes and the body rocks back past level once, then settles. A slight yaw drift grows with the sliding distance."""
    a = MU * 9.81; ts = t_lock + v0 / a; D = v0 * t_lock + v0 * v0 / (2 * a)
    dt = 1 / 240.0; K = 3.2 / a; w = 2 * math.pi * 1.4; zt = 0.35; th = om = 0.0; tab = []
    for i in range(int(3.0 / dt) + 2):
        t = i * dt; tgt = -K * (a if t_lock <= t < ts else 0.0)
        om += (-w * w * (th - tgt) - 2 * zt * w * om) * dt; th += om * dt; tab.append(th)
    def state(t):
        u = min(max(t - t_lock, 0.0), ts - t_lock)
        s = v0 * min(t, t_lock) + v0 * u - a * u * u / 2
        v = v0 if t < t_lock else max(0.0, v0 - a * (t - t_lock))
        return STOP[0] + D - s, YAW + drift * (s / D) ** 2, tab[min(len(tab) - 1, int(round(t / dt)))], v
    return state, D, ts

def skid_dust(state, ts, n=24, seed=8):
    """Dust thrown up at the four locked tires while the car slides: each puff leaves with most of the car's speed, slows
    in the air (tau 1.1 s), grows and thins out; the cloud rolls on past the car after it stops. A light wind to the north."""
    rnd = np.random.default_rng(seed); objs = []
    c = core.srgb("#CDB590")
    for i in range(n):
        o = _obj(f"dust{i}", _mesh_sphere(f"dust{i}", 1.0, seg=10, rings=6), "#CDB590")
        m = bpy.data.materials.new(f"dust_m{i}"); m.diffuse_color = (*c, 0.5); o.data.materials[0] = m; objs.append((o, m))
    births = np.linspace(0.0, ts - 0.05, n); tires = [(-0.95, -1.55), (0.95, -1.55), (-0.95, 1.55), (0.95, 1.55)]
    side = rnd.uniform(-0.5, 0.5, n); up = rnd.uniform(0.15, 0.4, n); smax = rnd.uniform(0.35, 0.65, n)
    def cb(f):
        t = f / core.FPS
        for i, (o, m) in enumerate(objs):
            tb = births[i]; age = t - tb
            if age < 0 or age > 1.9:
                o.hide_render = True; continue
            x, yaw, th, v = state(tb); lx, ly = tires[i % 4]
            p0 = PR.car_world((x, 0.0), yaw, lx, ly, 0.15)
            tau = 1.1; dist = 0.85 * v * tau * (1 - math.exp(-age / tau))
            pos = p0 + np.array((-dist, side[i] * age + 0.35 * age, up[i] * age))
            s = 0.12 + (smax[i] - 0.12) * (1 - math.exp(-age / 0.5))
            o.hide_render = False; o.location = (pos[0], pos[1], max(pos[2], s * 0.45)); o.scale = (s, s, s * 0.6)
            m.diffuse_color = (*c, 0.4 * max(0.0, 1 - age / 1.9))
    return cb

def S02_SH080(nf):
    """Ground level: the wheels lock, the car slides on the dusty asphalt (constant deceleration, about 0.55 g), the nose dips,
    it stops a few meters from the wall and rocks back once. Skid marks, dust rolling past."""
    p = (2.4, -2.3, 0.22); town(p)
    c = PR.car("car"); state, D, ts = skid()
    piv = Matrix.Translation((0, 0.1, 0.55))
    wheels = [bpy.data.objects[f"{c.name}_{k}{i}"] for k in ("tire", "hub") for i in range(4)]
    base = {o.name: o.matrix_basis.copy() for o in wheels}
    mk = []
    for i, ly in enumerate((-0.945, 0.945)):
        for j in range(2):
            mb = core.MB(None, detail=False); mb.box(0.0, 1.0, -0.1, 0.1, 0.0125, 0.017, "#4E4234"); mk.append((PR.mesh_obj(f"mark{i}{j}", mb), ly, (1.55, -1.55)[j]))
    x0 = state(0.0)[0]
    def cb(f):
        t = f / core.FPS; x, yaw, th, v = state(t)
        E = piv @ Matrix.Rotation(math.radians(th), 4, "X") @ piv.inverted()
        PR.place(c, (x, 0.0, 0.0), yaw, extra=E)
        Ei = E.inverted()
        for o in wheels:                                  # the wheels stay on the ground: only the body pitches
            o.matrix_basis = Ei @ base[o.name]
        for (o, ly, lx_off) in mk:                        # each tire's mark runs from where it locked to where it is now
            xa = x - lx_off; xb = x0 - lx_off
            if xb - xa < 0.02: o.hide_render = True; continue
            o.hide_render = False; o.location = (xa, STOP[1] + ly, 0.0); o.scale = (xb - xa, 1, 1)
    return {"cam": cam(p, (5.45, -0.95, 0.4), 32), "callbacks": [cb, skid_dust(state, ts)], "cues": [[0, 1.6, "TIRES SKID ON DUSTY ASPHALT"]]}

def S02_SH090(nf):
    """MEDIUM CLOSE through the windshield (d11: closer): head and chest, the roof edge, the left pillar and the dashboard
    frame him."""
    p = tuple(PR.car_world(STOP, YAW, -0.42, 3.0, 1.34)); town(p)
    c, him = parked(nf)
    him.seq([(0, pose("drive", **_seat(), hpitch=35, eyes=0.7)), (0.6, pose("drive", **_seat(), hpitch=35, eyes=0.7)),
             (2.6, pose("drive", **_seat(), hpitch=0, eyes=1.3))])
    return {"cam": cam(p, (HEADP[0], HEADP[1], HEADP[2] - 0.1), 70), "actors": [him], "callbacks": [PR.bob_nod(c, lambda t: 4)]}

def S02_SH100(nf):
    """POV dolly zoom: the gap keeps its size while the main road beyond it stretches away."""
    town(EYE)
    d0 = EYE[0] + 17.0
    return {"cam": move([(0, (d0, EYE[1], EYE[2]), (-200, 0, 3), 85), (4, EYE, (-200, 0, 3), 85 * EYE[0] / d0)], ease="io")}

def lean_look(nf, keys):
    """From the passenger seat, low, below his shoulder: one fixed frame for SH110, SH130 and SH160 (one take).
    keys: [(t, overrides of the seated pose)], eased pose to pose, one track for the whole shot (no pops)."""
    p = tuple(PR.car_world(STOP, YAW, 0.38, 0.38, 1.02)); town(p)
    c, him = parked(nf); open_cabin(c)
    him.tracks.clear()
    him.seq([(t, pose("drive", **_seat(), **kw)) for (t, kw) in keys] + [(nf / core.FPS + 0.5, pose("drive", **_seat(), **keys[-1][1]))])
    ref = fk(pose("drive", **_seat(), spine=6)); tgt = ref[HEAD] + np.array((0, 0, -0.04))
    return {"cam": cam(p, tuple(tgt), 28), "actors": [him], "callbacks": [PR.bob_nod(c, lambda t: 3)]}

LEAN = dict(spine=17, hpitch=4)
def S02_SH110(nf):
    return lean_look(nf, [(0.0, dict(eyes=0.9)), (0.25, dict(hpitch=2)), (0.95, dict(LEAN, hyaw=66)), (1.5, dict(LEAN, hyaw=71)),
                          (2.0, dict(LEAN, hyaw=73))])
def S02_SH130(nf):
    return lean_look(nf, [(0.0, dict(LEAN, hyaw=73)), (0.3, dict(LEAN, hyaw=71)), (1.1, dict(LEAN, hyaw=-66, hpitch=2)),
                          (2.0, dict(LEAN, hyaw=-72, hpitch=2))])
def S02_SH160(nf):
    return lean_look(nf, [(0.0, dict(spine=8, hyaw=-22, hpitch=-12)), (0.45, dict(spine=8, hyaw=-20, hpitch=-11)),
                          (1.15, dict(spine=10, hyaw=-3, hpitch=30, eyes=0.7)), (2.0, dict(spine=11, hyaw=-2, hpitch=32, eyes=0.6))])

def pov(eye_local, turn, pitch, lens):
    """His point of view from inside the parked car: eye in car-local coordinates, turn > 0 = to his left (degrees)."""
    e = PR.car_world(STOP, YAW, *eye_local); h = math.radians(YAW + 90 + turn); pr = math.radians(pitch)
    tgt = e + 10 * np.array((math.cos(h) * math.cos(pr), math.sin(h) * math.cos(pr), math.sin(pr)))
    return tuple(e), tuple(tgt), lens

POV120 = ((-0.42, 0.45, 1.28), 58, -6, 16)          # leaning over the wheel, looking left
def S02_SH120(nf):
    """His POV, leaning over the wheel, looking left: the A-pillar, the roof edge and the dashboard edge frame the town's
    outer wall a few meters off, running away to the left to the horizon. No road."""
    e, tgt, lens = pov(*POV120); town(e)
    c = open_cabin(face_in(PR.car("car"))); PR.place(c, (STOP[0], STOP[1], 0), YAW)
    case = flat_case("case"); w = PR.car_world(STOP, YAW, CASE_FRONT[0], CASE_FRONT[1], 0.6); PR.place(case, (w[0], w[1], 0.6), YAW + CASE_FRONT[2])
    return {"cam": cam(e, tgt, lens)}

def S02_SH140(nf):
    """His POV looking right, past the briefcase on the passenger seat: through the windshield and the side window the
    wall runs away to the right, to the horizon. The only way is through."""
    e, tgt, lens = pov((-0.4, 0.15, 1.27), -68, -12, 16); town(e)
    c = open_cabin(face_in(PR.car("car"))); PR.place(c, (STOP[0], STOP[1], 0), YAW)
    case = flat_case("case"); w = PR.car_world(STOP, YAW, CASE_FRONT[0], CASE_FRONT[1], 0.6); PR.place(case, (w[0], w[1], 0.6), YAW + CASE_FRONT[2])
    return {"cam": cam(e, tgt, lens)}

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
