from sh import *

CAR = (0.0, 1.0); YAW = 90.0
G = 9.81

# ------------------------------------------------------------------ helicopter flight (d11: heavy)
# Flown like a heavy machine of about 10 t (UH-60 class weight; the model stays the white helicopter). Point mass with the
# rotor thrust along the disk normal (the whole helicopter tilts with the disk), drag on a flat-plate area, a second-order
# attitude response with rate limits (slow, smooth, no snap), a lagging collective, and a limited yaw rate. The pilot flies
# a planned ground track with a speed plan (feed-forward plus a soft correction), so the motion is what the physics
# allows: east along the south side of the avenue, a slow swing to the left across the street whose apex is the point
# closest to the car, west along the north side, then nose down and away down the centre line, climbing gently.
# World: +x east, +y north, z up. Heading psi: nose toward (-sin psi, cos psi). Pitch: nose up positive. Bank: right down positive.

def _rot(psi, th, ph):
    cz, sz = math.cos(psi), math.sin(psi); cx, sx = math.cos(th), math.sin(th); cy, sy = math.cos(ph), math.sin(ph)
    return (np.array(((cz, -sz, 0), (sz, cz, 0), (0, 0, 1))) @ np.array(((1, 0, 0), (0, cx, -sx), (0, sx, cx)))
            @ np.array(((cy, 0, sy), (0, 1, 0), (-sy, 0, cy))))

def _wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi

def _smooth(u):
    u = min(1.0, max(0.0, u)); return u * u * u * (u * (6 * u - 15) + 10)

HEAVY = dict(p0=(-38.0, -6.0, 1.8), y_in=-6.0, x_turn=-26.0, R=6.5, ease_len=140.0, y_line=1.0, m=10000.0, f_drag=3.0,
             wn=1.9, zeta=0.9, rate_r=22.0, rate_p=13.0, tau_T=0.5, tilt_max=20.0, kp=0.35, kd=0.9, yaw_rate=45.0,
             t_lift=0.4, t_climb=3.6, z_turn=5.6, t_go=1.3, v_in=7.0, v_turn=4.0, v_max=42.0, a_acc=3.0, vz_out=1.5)

def _track(P):
    x0, ys, xc, R = P["p0"][0], P["y_in"], P["x_turn"], P["R"]
    pts = [np.array((x, ys)) for x in np.arange(x0, xc, 0.1)]
    cy = ys + R
    for a in np.arange(-math.pi / 2, math.pi / 2, 0.1 / R):
        pts.append(np.array((xc + R * math.cos(a), cy + R * math.sin(a))))
    yn = cy + R
    for x in np.arange(xc, -2500.0, -0.1):
        pts.append(np.array((x, yn + (P["y_line"] - yn) * _smooth((xc - x) / P["ease_len"]))))
    pts = np.array(pts)
    return pts, np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]), (xc - x0, xc - x0 + math.pi * R)

_FLY = {}
def flight(T=20.0, **kw):
    """Per frame (cg position, heading, pitch, bank), radians. The centre of mass starts 1.8 m up (skids 0.4 m off the street)."""
    P = dict(HEAVY); P.update(kw); key = (T, tuple(sorted((k, str(v)) for k, v in P.items())))
    if key in _FLY: return _FLY[key]
    pts, sl, (s_in, s_out) = _track(P)
    def v_of_s(s):
        if s < s_in - 12: return P["v_in"]
        if s < s_in: return P["v_in"] + (P["v_turn"] - P["v_in"]) * _smooth((s - (s_in - 12)) / 12)
        if s < s_out: return P["v_turn"]
        return 1e9
    dt = 1.0 / 240; n = int(round(T * 240)) + 1; every = int(round(240 / core.FPS))
    S = np.zeros(n); V = np.zeros(n); s = 0.0; v = 0.0; t_exit = None
    for i in range(n):                                   # the plan in time: slow start, slow swing, then away
        t = i * dt
        if s < s_out:
            v = min(P["v_in"] * _smooth((t - P["t_go"]) / 3.2), v_of_s(s))
        else:
            if t_exit is None: t_exit = t
            v = min(P["v_max"], v + P["a_acc"] * _smooth((t - t_exit) / 3.0) * dt * (1 - (v / P["v_max"]) ** 2))
        s += v * dt; S[i] = s; V[i] = v
    def at(sv):
        k = max(1, min(len(sl) - 2, int(np.searchsorted(sl, sv))))
        u = (sv - sl[k - 1]) / max(1e-9, sl[k] - sl[k - 1]); return pts[k - 1] + (pts[k] - pts[k - 1]) * u, pts[k] - pts[k - 1]
    def z_plan(t):
        z = P["p0"][2] + (P["z_turn"] - P["p0"][2]) * _smooth((t - P["t_lift"]) / P["t_climb"])
        if t_exit is not None and t > t_exit:
            w = t - t_exit; z += P["vz_out"] * (w - 1.5 * (1 - math.exp(-w / 1.5)))
        return z
    m = P["m"]; p = np.array(P["p0"], float); vel = np.zeros(3); psi = math.radians(-90.0); r = 0.0
    th = ph = thd = phd = 0.0; Tn = m * G; out = []; prev = np.zeros(2); wn, zt_ = P["wn"], P["zeta"]
    lim = G * math.tan(math.radians(P["tilt_max"]))
    for i in range(n):
        t = i * dt
        pp, tan = at(S[i]); tan = tan / (np.linalg.norm(tan) + 1e-9); vp = tan * V[i]
        ap = (vp - prev) / dt if i else np.zeros(2); prev = vp
        ah = ap + P["kp"] * (pp - p[:2]) + P["kd"] * (vp - vel[:2])          # what the pilot asks of the disk
        if np.linalg.norm(ah) > lim: ah = ah / np.linalg.norm(ah) * lim
        psi_c = math.atan2(-tan[0], tan[1]) if V[i] > 0.8 else math.radians(-90.0)
        r_c = max(-math.radians(P["yaw_rate"]), min(math.radians(P["yaw_rate"]), 1.8 * _wrap(psi_c - psi)))
        r += (r_c - r) / 0.45 * dt; psi = _wrap(psi + r * dt)
        fwd = np.array((-math.sin(psi), math.cos(psi))); right = np.array((math.cos(psi), math.sin(psi)))
        th_c = -math.atan2(np.dot(ah, fwd), G); ph_c = math.atan2(np.dot(ah, right), G)
        thd += (wn * wn * (th_c - th) - 2 * zt_ * wn * thd) * dt; thd = max(-math.radians(P["rate_p"]), min(math.radians(P["rate_p"]), thd))
        phd += (wn * wn * (ph_c - ph) - 2 * zt_ * wn * phd) * dt; phd = max(-math.radians(P["rate_r"]), min(math.radians(P["rate_r"]), phd))
        th += thd * dt; ph += phd * dt
        zt = z_plan(t); vzt = (z_plan(t + 0.05) - zt) / 0.05
        az_c = 1.5 * (vzt + 0.6 * (zt - p[2]) - vel[2])
        T_c = min(1.6 * m * G, m * (G + az_c) / max(0.5, math.cos(th) * math.cos(ph)))
        Tn += (T_c - Tn) / P["tau_T"] * dt
        nrm = _rot(psi, th, ph) @ np.array((0.0, 0.0, 1.0))
        acc = (Tn * nrm - 0.5 * 1.2 * P["f_drag"] * np.linalg.norm(vel) * vel) / m - np.array((0, 0, G))
        vel = vel + acc * dt; p = p + vel * dt
        if p[2] < P["p0"][2] and vel[2] < 0: p[2] = P["p0"][2]; vel[2] = 0.0
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

def heli_haze(o, traj, cam_xy, d0=80.0, d1=175.0):
    """The sunset haze swallows the helicopter as it goes: its own colours blend into the sky with distance."""
    objs = [o] + list(o.children_recursive); mats = {}
    for ob in objs:
        if ob.type != "MESH": continue
        for k, sl in enumerate(ob.material_slots):
            m = sl.material
            if m is None: continue
            if m.name not in mats:
                mats[m.name] = (m.copy(), tuple(m.diffuse_color[:3]))
            ob.material_slots[k].material = mats[m.name][0]
    sky = core.MATS.sky
    def cb(f):
        p = traj[min(f, len(traj) - 1)][0]; d = math.hypot(p[0] - cam_xy[0], p[1] - cam_xy[1])
        k = _smooth((d - d0) / (d1 - d0)) ** 0.8; o.hide_render = k >= 0.995
        for ob in o.children_recursive: ob.hide_render = k >= 0.999
        for mc, c0 in mats.values():
            mc.diffuse_color = (*[c0[i] * (1 - k) + sky[i] * k for i in range(3)], 1)
    return cb

def S10_SH010(nf):
    """Inside the empty car, through the windshield: the helicopter lifts out of a low hover down the avenue into frame,
    noses down at the car and swings around in a heavy, slow bank across the street, closest to the car at its apex,
    then goes away west and vanishes in the sunset haze. As it turns we sink: the bobblehead (facing into the car, giving
    the finger) rises into the bottom of the frame. The wash rolls down the street lifting certificates and reaches the
    car: the head wobbles to a stop. At the end we sink a little more: the whole bobblehead, the street, the sky."""
    eye0 = np.array(PR.car_world(CAR, YAW, 0.2, 0.38, 1.25)); eye1 = np.array(PR.car_world(CAR, YAW, 0.2, 0.38, 1.11))
    eye2 = np.array(PR.car_world(CAR, YAW, 0.2, 0.38, 1.03))
    reset("sunset"); sets.avenue(tuple(eye0), towers=False)
    c = PR.car("car", door_open=1.0); PR.place(c, (CAR[0], CAR[1], 0), YAW)
    d = (-0.42 - 0.38, -0.25 - 1.08)                                               # the bobblehead faces into the car, turned to
    bpy.data.objects[c.name + "_bob"].rotation_euler = (0, 0, math.atan2(-d[0], d[1]))   # the driver's seat as in S02
    h = PR.heli("heli"); traj = flight(nf / core.FPS)
    def look(el_deg):
        e = math.radians(el_deg); return np.array((-math.cos(e), 0.0, math.sin(e)))
    def camfn(t):
        u1 = _smooth((t - 7.5) / 3.6); u2 = _smooth((t - 14.0) / 3.6)       # sink as it turns; a little more at the end
        pos = eye0 + (eye1 - eye0) * u1 + (eye2 - eye1) * u2
        el = 16.5 - 1.8 * u1 - 5.6 * u2
        return pos, pos + look(el) * 10.0, 32, 0
    paper, front = wash_papers(traj)
    bob = PR.car_world(CAR, YAW, 0.38, 1.08); t_hit = float(np.argmax(front >= bob[0])) / core.FPS     # the wash reaches the car
    return {"cam": {"fn": camfn}, "callbacks": [heli_fly_cb(h, traj), heli_haze(h, traj, eye0[:2]), paper, bob_wobble(c, t_hit)],
            "cues": [[0, 2.0, "ROTOR, CLOSE, LOW"], [2.0, 6.0, "IT LIFTS, NOSE DOWN AT US"], [6.0, 12.0, "A SLOW HEAVY SWING, CLOSE"],
                     [12.0, t_hit, "THE WASH ROLLS DOWN THE STREET"], [t_hit, 15.0, "THE HEAD WOBBLES TO A STOP"],
                     [15.0, 20.0, "THE ROTOR FADES. IT VANISHES IN THE SUNSET"]]}
