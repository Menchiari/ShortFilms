from sh import *

CAR = (0.0, 1.0); YAW = 90.0
G = 9.81

# ------------------------------------------------------------------ helicopter flight (d10)
# A light twin of about 4 t (Airbus ACH160 class) flown by a reckless, precise pilot. Point mass with the rotor
# thrust along the disk normal (the whole helicopter tilts with the disk), drag on a flat-plate area, attitude that
# lags the cyclic commands with rate limits, a collective that lags too (so a hard bank costs a little height), and
# coordinated flight once moving (no sideslip: the turn rate comes out as g * tan(bank) / airspeed).
# World: +x east, +y north, z up. Heading psi: nose toward (-sin psi, cos psi). Pitch: nose up positive. Bank: right down positive.

def _rot(psi, th, ph):
    cz, sz = math.cos(psi), math.sin(psi); cx, sx = math.cos(th), math.sin(th); cy, sy = math.cos(ph), math.sin(ph)
    return (np.array(((cz, -sz, 0), (sz, cz, 0), (0, 0, 1))) @ np.array(((1, 0, 0), (0, cx, -sx), (0, sx, cx)))
            @ np.array(((cy, 0, sy), (0, 1, 0), (-sy, 0, cy))))

def _wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi

_FLY = {}
def flight(T=15.0, p0=(-52.0, -6.8, 1.8), m=4000.0, f_drag=2.4, tau_att=0.28, roll_rate=75.0, pitch_rate=28.0, tau_T=0.32,
           t_lift=0.5, t_nose=1.3, nose=17.0, v_turn=9.5, bank=60.0, z_turn=7.6, aim=(-1000.0, -0.5)):
    """Hover low in the avenue, nose toward the car (the centre of mass at p0, skids 0.4 m off the street); lift,
    nose down and run at the car, a hard coordinated left turn at 60 degrees of bank, roll out on the avenue,
    nose down and away west, climbing slightly. Returns per frame (cg position, heading, pitch, bank) in radians."""
    key = (T, p0, v_turn, bank, z_turn)
    if key in _FLY: return _FLY[key]
    dt = 1.0 / 240; n = int(round(T * 240)) + 1; every = int(round(240 / core.FPS))
    p = np.array(p0, float); v = np.zeros(3); psi = math.radians(-90.0)
    th = ph = 0.0; Tn = m * G; phase = "hover"; out = []; psi_rate = 0.0
    def follow(a, c, rate):
        d = (c - a) / tau_att * dt; lim = math.radians(rate) * dt
        return a + max(-lim, min(lim, d))
    for i in range(n):
        t = i * dt; Vh = math.hypot(v[0], v[1])
        # the pilot
        vz_c = 0.0; th_c = 0.0; ph_c = 0.0
        if phase == "hover" and t >= t_lift: phase = "climb"
        if phase in ("climb", "accel"):
            vz_c = min(4.0, 1.3 * (z_turn - p[2]))
            if t >= t_nose: phase = "accel"; th_c = -math.radians(nose)
            if phase == "accel" and Vh >= v_turn: phase = "turn"
        if phase == "turn":
            ph_c = -math.radians(bank)                                                   # hard left
            th_c = max(-math.radians(10), min(math.radians(14), 0.05 * (Vh - v_turn)))   # hold the speed
            vz_c = 1.2 * (z_turn - p[2])                                                 # hold the height (the collective lags)
            if abs(_wrap(math.radians(90.0) - psi)) < math.radians(50): phase = "out"
        if phase == "out":
            want = math.atan2(-(aim[0] - p[0]), aim[1] - p[1]); err = _wrap(want - psi)
            ph_c = max(-math.radians(40), min(math.radians(40), -(1.3 * err - 0.45 * psi_rate)))
            th_c = -math.radians(19.0) if Vh < 32 else -math.radians(19.0 - 7.0 * min(1.0, (Vh - 32) / 15))
            vz_c = 2.0
        th = follow(th, th_c, pitch_rate); ph = follow(ph, ph_c, roll_rate)
        az_c = 2.5 * (vz_c - v[2])
        T_c = min(2.3 * m * G, m * (G + az_c) / max(0.35, math.cos(th) * math.cos(ph)))
        Tn += (T_c - Tn) / tau_T * dt
        if Vh > 3.0:
            course = math.atan2(-v[0], v[1]); psi_f = psi + min(1.0, (Vh - 3.0) / 3.0) * _wrap(course - psi)
        else:
            psi_f = psi
        nrm = _rot(psi_f, th, ph) @ np.array((0.0, 0.0, 1.0))
        a = (Tn * nrm - 0.5 * 1.2 * f_drag * np.linalg.norm(v) * v) / m - np.array((0, 0, G))
        v = v + a * dt; p = p + v * dt
        if p[2] < p0[2] and v[2] < 0: p[2] = p0[2]; v[2] = 0.0
        Vh = math.hypot(v[0], v[1]); prev = psi
        if Vh > 3.0:
            course = math.atan2(-v[0], v[1]); psi = _wrap(psi + min(1.0, (Vh - 3.0) / 3.0) * 7.0 * _wrap(course - psi) * dt)
        psi_rate = _wrap(psi - prev) / dt
        if i % every == 0:
            out.append((p.copy(), psi, th, ph))
    _FLY[key] = out
    return out

def heli_fly_cb(o, traj, cg=(0.0, 0.0, 1.4)):
    """Full attitude (heading, pitch, bank) about the centre of mass, rotor spinning."""
    rot = bpy.data.objects[o["rotor"]]
    def cb(f):
        p, psi, th, ph = traj[min(f, len(traj) - 1)]
        R = _rot(psi, th, ph)
        o.matrix_world = Puppet.M(R, np.array(p, float) - R @ np.array(cg))
        rot.rotation_euler = (0, 0, f / core.FPS * 26.0)
    return cb

# ------------------------------------------------------------------ rotor wash and paper
def wash_front(traj, c0=10.0, tau=2.5, z_max=15.0, v_max=18.0):
    """How far east the rotor wash has rolled at each frame. While the helicopter is low and slow its downwash hits the
    street and spreads as a wall jet; each puff runs on toward the car, slowing down: x = x_heli + c0 * tau * ln(1 + age / tau).
    Returns (front x per frame, the helicopter's footprint per frame)."""
    n = len(traj); fps = core.FPS; front = np.full(n, -1e9); foot = np.array([tr[0][:2] for tr in traj])
    emit = [f for f in range(n) if traj[f][0][2] < z_max and (f == 0 or np.linalg.norm(traj[f][0][:2] - traj[f - 1][0][:2]) * fps < v_max)]
    for f in range(n):
        best = -1e9
        for e in emit:
            if e > f: break
            best = max(best, foot[e][0] + c0 * tau * math.log(1 + (f - e) / fps / tau))
        front[f] = best
    return front, foot

def wash_papers(traj, n=34, seed=21):
    """Certificates lying on the avenue. Each is lifted when the wash reaches it, blown away from the helicopter (and
    down the street, toward the car), up and tumbling, then it sinks and settles. Sheets in the car's lane go over it."""
    front, foot = wash_front(traj)
    rnd = np.random.default_rng(seed); objs = []
    X = np.concatenate([rnd.uniform(-46.0, -14.0, n - 12), rnd.uniform(-13.0, -3.5, 12)]); Y = rnd.uniform(-7.5, 8.5, n)
    H = rnd.uniform(1.6, 4.5, n); D = rnd.uniform(2.0, 3.6, n); L = rnd.uniform(4.0, 10.0, n)
    ph = rnd.uniform(0, 6.28, (n, 3)); yaw0 = rnd.uniform(0, 6.28, n)
    F0 = np.array([int(np.argmax(front >= x)) if np.any(front >= x) else 10 ** 6 for x in X])
    DIR = []
    for i in range(n):
        f = min(F0[i], len(traj) - 1); r = np.array((X[i], Y[i])) - foot[f]
        r = r / (np.linalg.norm(r) + 1e-6) + np.array((0.8, 0.0)); DIR.append(r / np.linalg.norm(r))
        if abs(Y[i] + L[i] * DIR[i][1] - CAR[1]) < 1.6 and X[i] + L[i] * DIR[i][0] > -3.0:
            H[i] = max(H[i], 2.8)                                   # in the car's lane: it goes over the car
        mb = core.MB(None, detail=False); mb.box(-0.1, 0.1, -0.045, 0.045, 0, 0.004, "#EDE6D2"); objs.append(PR.mesh_obj(f"cert{i}", mb))
    def cb(f):
        for i, o in enumerate(objs):
            s = (f - F0[i]) / core.FPS / D[i]
            if s <= 0:
                o.location = (X[i], Y[i], 0.01); o.rotation_euler = (0, 0, yaw0[i]); continue
            u = min(1.0, s); k = 1 - (1 - u) ** 2
            d = L[i] * k + (0.5 * min(1.0, s - 1) if s > 1 else 0.0)
            side = 0.6 * math.sin(ph[i, 0] + 2.4 * s) * min(1.0, s)
            x = X[i] + DIR[i][0] * d - DIR[i][1] * side; y = Y[i] + DIR[i][1] * d + DIR[i][0] * side
            z = 0.01 + (H[i] * math.sin(math.pi * u ** 0.75) if s < 1 else 0.0)
            spin = 1 - min(1.0, max(0.0, s - 0.85) / 0.3)
            o.location = (x, y, z)
            o.rotation_euler = (spin * (ph[i, 1] + 8 * s), spin * (ph[i, 2] + 5 * s), yaw0[i] + 2.5 * s)
    return cb, front

def bob_wobble(o, t_hit, amp=22.0, tau=1.15, w=11.0):
    """The bobblehead hit by the gust: a damped oscillation (mostly fore and aft, a little sideways) to a stop."""
    hd = bpy.data.objects[o["bobneck"]]
    def cb(f):
        t = f / core.FPS - t_hit
        if t <= 0:
            hd.rotation_euler = (0, 0, 0); return
        e = amp * math.exp(-t / tau) * min(1.0, t / 0.12)
        hd.rotation_euler = (math.radians(e * math.sin(w * t)), math.radians(0.35 * e * math.sin(1.31 * w * t + 1.0)), 0)
    return cb

def S10_SH010(nf):
    """Inside the empty car, through the windshield: the helicopter lifts out of a low hover down the avenue into frame,
    noses down at the car, banks hard and swings around, rolls out and goes away west, climbing, into open sky. As it
    turns we sink: the bobblehead (facing into the car, giving the finger) rises into the bottom of the frame. The wash
    rolls down the street lifting certificates and reaches the car: the head wobbles to a stop."""
    eye0 = np.array(PR.car_world(CAR, YAW, 0.2, 0.3, 1.25)); eye1 = np.array(PR.car_world(CAR, YAW, 0.2, 0.3, 1.08))
    reset("sunset"); sets.avenue(tuple(eye0), towers=False)
    c = PR.car("car", door_open=1.0); PR.place(c, (CAR[0], CAR[1], 0), YAW)
    d = (-0.42 - 0.38, -0.25 - 1.08)                                               # the bobblehead faces into the car, turned to
    bpy.data.objects[c.name + "_bob"].rotation_euler = (0, 0, math.atan2(-d[0], d[1]))   # the driver's seat as in S02
    h = PR.heli("heli"); traj = flight()
    def look(el_deg):
        e = math.radians(el_deg); return np.array((-math.cos(e), 0.0, math.sin(e)))
    def camfn(t):
        u = min(1.0, max(0.0, (t - 5.4) / 3.8)); u = u * u * (3 - 2 * u)            # the pedestal as it turns
        pos = eye0 * (1 - u) + eye1 * u
        el = 14.4 - 1.8 * u
        return pos, pos + look(el) * 10.0, 40, 0
    paper, front = wash_papers(traj)
    bob = PR.car_world(CAR, YAW, 0.38, 1.08); t_hit = float(np.argmax(front >= bob[0])) / core.FPS     # the wash reaches the car
    return {"cam": {"fn": camfn}, "callbacks": [heli_fly_cb(h, traj), paper, bob_wobble(c, t_hit)],
            "cues": [[0, 1.4, "ROTOR, CLOSE, LOW"], [1.4, 5.4, "IT LIFTS, NOSE DOWN AT US"], [5.4, 8.2, "HARD BANK, IT SWINGS AROUND"],
                     [8.2, 10.8, "THE WASH ROLLS DOWN THE STREET"], [10.8, 15, "THE HEAD WOBBLES TO A STOP. THE ROTOR FADES"]]}
