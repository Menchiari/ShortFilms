from sh import *
from puppet import _obj, _mesh_cyl, _mesh_sphere, _mesh_box
from shots_s05 import SQ_WALLS, CASE_AT
from shots_s07 import ARM, TOP, PIPE_AT, fat_death, bodies_s07
import phys

CUES = {"S09_SH030": [[0, 3, "ROTORS WINDING DOWN"]], "S09_SH070": [[0, 2, "ROTORS"]]}
SEAT = (-39.6, -6.66)            # his pelvis on the road, his back against the corner curb (y = -7)
CASE = CASE_AT                   # the case lies where it fell when the rock hit him
HIMC = (CASE[0] + 0.6, CASE[1] - 0.3)
PAD = (-24.0, 0.5)               # helicopter in the square; door faces west
DOOR = (-25.6, 1.0)
DOORP = (-25.95, 0.55)           # where he stops at the door (the south half of the opening), then climbs in
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

def open_case(name):
    """d10: the briefcase lying flat and open on the asphalt: the body and the lid side by side, lining up, the lid's
    inside pocket (where the folder is) on the lid. Origin at the hinge, on the ground; the body on -y, the lid on +y."""
    mb = core.MB(None, detail=False); k = "#8A5A30"; ln = "#3A2A1C"
    mb.box(-0.23, 0.23, -0.34, 0.0, 0.0, 0.085, k)                 # the body, open side up
    mb.box(-0.205, 0.205, -0.32, -0.02, 0.085, 0.087, ln)           # its lining (seemingly empty)
    mb.box(-0.23, 0.23, 0.0, 0.34, 0.0, 0.035, k)                   # the lid, flat open, inside up
    mb.box(-0.205, 0.205, 0.02, 0.32, 0.035, 0.037, ln)
    mb.box(-0.17, 0.17, 0.05, 0.24, 0.037, 0.045, "#4A3826")        # the pocket inside the lid
    mb.box(-0.13, 0.13, 0.07, 0.2, 0.045, 0.049, "#3A4A6A")         # the folder in it
    mb.box(-0.08, 0.08, -0.375, -0.34, 0.03, 0.06, "#5A3A20")       # the handle
    return PR.mesh_obj(name, mb)

def scenery(nf, case=True):
    acts = bodies_s07(nf) + sniper_bodies(nf)
    if case:
        c = open_case("case"); PR.place(c, (CASE[0], CASE[1], 0.0), 80)
    return acts

def still_papers(n, center, spread, seed):
    """The certificates lying still on the street (the animatic leaves the paper still: Seedance moves it)."""
    return PR.papers("bond", n, center, spread, 999.0, 1000.0, seed=seed)

def wash_drift(n, center, spread, seed, src, t_on=0.0):
    """d10: a gentle, plausible drift of the lying certificates away from the rotor wash: they slide along the street
    radially away from the helicopter, faster when it is low and close (outwash ~ 1/r), with a small hop now and then.
    src(t) -> (x, y, height) of the rotor hub. No paper climbs into the air."""
    rnd = np.random.default_rng(seed); objs = []
    P = np.stack([center[0] + rnd.uniform(-spread, spread, n), center[1] + rnd.uniform(-spread, spread, n)], 1)
    k = rnd.uniform(0.03, 0.09, n); ph = rnd.uniform(0, 6.28, (n, 3)); yaw = rnd.uniform(0, 6.28, n)
    for i in range(n):
        mb = core.MB(None, detail=False); mb.box(-0.1, 0.1, -0.045, 0.045, 0, 0.004, "#EDE6D2"); objs.append(PR.mesh_obj(f"bond{i}", mb))
    nfr = int(30 * core.FPS); pos = np.zeros((nfr, n, 2)); vel = np.zeros((nfr, n)); p = P.copy()
    for f in range(nfr):
        t = f / core.FPS; hx, hy, hz = src(t)
        r = p - np.array((hx, hy))[None]; d = np.linalg.norm(r, axis=1) + 1e-6
        w = 0.0 if t < t_on else max(0.0, min(1.0, (26.0 - hz) / 20.0))           # the wash reaches the ground under ~2 rotor diameters
        U = 12.0 * np.minimum(1.0, 13.0 / d) * w                                  # outwash speed at the street
        gust = 0.6 + 0.4 * np.sin(ph[:, 0] + t * 2.3)
        v = k * U * gust; p = p + r / d[:, None] * v[:, None] / core.FPS
        pos[f] = p; vel[f] = v
    def cb(f):
        f = min(f, nfr - 1)
        for i, o in enumerate(objs):
            v = vel[f, i]; hop = 0.18 * max(0.0, math.sin(ph[i, 1] + f / core.FPS * 3.1)) ** 6 * min(1.0, v / 0.6)
            o.location = (pos[f, i, 0], pos[f, i, 1], 0.01 + hop)
            o.rotation_euler = (hop * 3.0, hop * 2.0 * math.sin(ph[i, 2]), yaw[i] + 0.8 * float(np.sum(vel[:f + 1, i])) / core.FPS)
    return cb

def heli_landed(yaw=180.0):
    h = PR.heli("heli"); return h, PR.heli_cb(h, lambda t: (np.array((PAD[0], PAD[1], 0.0)), yaw, 0.0))

# ------------------------------------------------------------------ SH010: limbs for the shape lying on the street
def shape_limbs(a, t0=0.0):
    """d10, for the reclining shape in SH010: two legs (thigh, knee, shin, shoe) and two arms (upper arm, elbow,
    forearm, hand) in the costume's colours instead of the single legs pill, so the knees read and the elbows rest on
    the sidewalk. Same height smoothing and lift as the shape; hidden on physics frames and before t0."""
    c = a.c; s = c.get("scale", 1.0); wide = min(1.4, c.get("wide", 1.0)); n = a.name + "_limb"
    rt, rl, rh = 0.17 * s * wide, 0.13 * s * wide, 0.112 * s
    sleeve = c.get("sleeve", "long"); fa_col = c["shirt"] if sleeve == "long" else c["skin"]
    P = {}
    for sd in ("l", "r"):
        P[sd + "th"] = _obj(n + sd + "th", _mesh_cyl(n + sd + "th", 0.085 * s, 0.07 * s, 1.0, n=12), c["pants"])
        P[sd + "kn"] = _obj(n + sd + "kn", _mesh_sphere(n + sd + "kn", 0.07 * s, seg=10, rings=6), c["pants"])
        P[sd + "sh"] = _obj(n + sd + "sh", _mesh_cyl(n + sd + "sh", 0.065 * s, 0.052 * s, 1.0, n=12), c["pants"])
        P[sd + "ft"] = _obj(n + sd + "ft", _mesh_box(n + sd + "ft", 0.052 * s, 0.045 * s, -0.05 * s, 0.2 * s), c.get("shoes", "#2A2622"))
        P[sd + "ua"] = _obj(n + sd + "ua", _mesh_cyl(n + sd + "ua", 0.06 * s, 0.05 * s, 1.0, n=10), c["shirt"])
        P[sd + "el"] = _obj(n + sd + "el", _mesh_sphere(n + sd + "el", 0.05 * s, seg=8, rings=5), c["shirt"])
        P[sd + "fa"] = _obj(n + sd + "fa", _mesh_cyl(n + sd + "fa", 0.045 * s, 0.038 * s, 1.0, n=10), fa_col)
        P[sd + "ha"] = _obj(n + sd + "ha", _mesh_sphere(n + sd + "ha", 0.045 * s, 1, 0.8, 1.2, seg=8, rings=5), c["skin"])
    st = {}
    def smooth():
        if "Jg" not in st:
            J = a.J; k = 3; Jg = J.copy()
            pad = np.concatenate([J[:1].repeat(k, 0), J, J[-1:].repeat(k, 0)])
            z = np.mean([pad[i:i + len(J), :, 2] for i in range(2 * k + 1)], axis=0)
            moving = np.abs(J[:, PELVIS, 2] - z[:, PELVIS]) < 0.12
            Jg[moving, :, 2] = z[moving]; st["Jg"] = Jg
        return st["Jg"]
    def seg(o, A, B, xr):
        d = B - A; L = np.linalg.norm(d) + 1e-6
        o.matrix_world = Puppet.M(Puppet.frame(d, xr), A) @ Matrix.Diagonal((1, 1, L, 1))
    def cb(f):
        ff = min(f, a.nf - 1); show = bool(a.visible[ff]) and not a.K[ff] and f >= F(t0)
        for o in P.values(): o.hide_render = not show
        if not show: return
        for nm in ("_shape_legs", "_shape_foot"):
            o = bpy.data.objects.get(a.name + nm)
            if o is not None: o.hide_render = True
        J = smooth()[ff].copy()
        up = J[NECK] - J[PELVIS]; u = up / (np.linalg.norm(up) + 1e-9)
        pel = J[PELVIS] + u * 0.02; top = J[NECK] - u * 0.065 * s
        feet = (J[LAN] + J[RAN]) / 2 + np.array((0, 0, 0.1 * s)); hipc = (J[LHIP] + J[RHIP]) / 2
        gz = core.ground_z(J[PELVIS, 0], J[PELVIS, 1])
        low = min(pel[2] - rt, top[2] - rt, hipc[2] - rl, feet[2] - rl * 0.85, J[HEAD, 2] - rh)
        J[:, 2] += max(0.0, gz + 0.005 - low)
        xr = J[RSH] - J[LSH]
        for sd, (hp, kn, an, to, sh, el, ha) in (("l", (LHIP, LKN, LAN, LTO, LSH, LEL, LHA)), ("r", (RHIP, RKN, RAN, RTO, RSH, REL, RHA))):
            seg(P[sd + "th"], J[hp], J[kn], xr); seg(P[sd + "sh"], J[kn], J[an], xr)
            P[sd + "kn"].matrix_world = Puppet.M(np.eye(3), J[kn])
            P[sd + "ft"].matrix_world = Puppet.M(Puppet.frame(J[to] - J[an], xr), J[an] + np.array((0, 0, -0.01)))
            seg(P[sd + "ua"], J[sh], J[el], xr); seg(P[sd + "fa"], J[el], J[ha], xr)
            P[sd + "el"].matrix_world = Puppet.M(np.eye(3), J[el])
            dd = J[ha] - J[el]; P[sd + "ha"].matrix_world = Puppet.M(Puppet.frame(dd, xr), J[ha] + dd / (np.linalg.norm(dd) + 1e-9) * 0.03)
    return cb

# his poses by the curb (pelvis 0.18 up: the shape's hips rest on the asphalt)
CURL = dict(x=-39.95, y=-6.62, z=None, yaw=0, roll=86, spine=32, ll=(95, 6, 112), rl=(84, 6, 118), la=(70, 12, 105), ra=(82, 10, 92),
            hpitch=-15, ground="all")                                   # on his right side, curled up, facing the camera
LEAN = dict(x=SEAT[0], y=SEAT[1], z=0.18, yaw=0, tilt=70, spine=4, ra=(-118, -10, 142), la=(-118, -6, 148), ll=(26, 10, 22), rl=(14, 3, 2))
PROP = dict(LEAN, tilt=55, spine=8, roll=33, twist=-22, ra=(-102, 54, 147), la=(11, 14, 32), ll=(41, 10, 22), rl=(29, 3, 2),
            hyaw=-58, hpitch=2)                                         # up on his right elbow, turned to the body beside him

def S09_SH010(nf):
    """The rope goes: he drops beside the curb, curls up facing the camera, shaking; turns over and leans back against
    the curb, elbows on the sidewalk behind him, legs out on the street; props up on his right elbow and spits on the fat man."""
    p = (-39.4, 8.4, 0.3); sq(p)
    JA = phys.drop(1.6)
    him = Actor("him", COST["him"], nf); him.joints(0, JA)
    curl = pose("stand", **CURL); lean = pose("stand", **LEAN); prop = pose("stand", **PROP)
    # turning over at ground level: a tilt about his long axis rolls him from his side onto his back (head still east),
    # then he swivels on his back, sliding up against the curb, and leans back on his elbows
    back = pose("stand", x=-39.85, y=-6.65, z=0.18, yaw=0, tilt=88, roll=88, spine=14, la=(20, 25, 50), ra=(30, 20, 40), ll=(75, 8, 105),
                rl=(65, 8, 95), hpitch=10)
    swivel = pose("stand", x=-39.72, y=-6.62, z=0.18, yaw=0, tilt=82, roll=42, spine=10, la=(-40, 20, 90), ra=(-50, 15, 100), ll=(55, 8, 70),
                  rl=(45, 8, 50), hpitch=5)
    spit = dict(prop, spine=prop["spine"] + 7, hpitch=prop["hpitch"] + 14)
    him.seq([(1.6, curl), (7.3, curl), (8.3, back), (9.2, swivel), (10.0, lean), (13.4, lean), (14.6, prop), (14.9, spit), (15.25, dict(prop, hpitch=prop["hpitch"] + 4)),
             (18.0, prop)], blend=0.6)
    him.overlays.append((F(4.4), F(7.3), lambda f, q: dict(q, spine=q["spine"] + 4 * math.sin(f * 2.3))))
    him.overlays.append((F(10.0), F(13.4), lambda f, q: dict(q, spine=q["spine"] - 3 * math.sin(f / core.FPS * 3.0))))
    him.talk(0.6, 4.2); him.face(12.2, 13.2, mouth=0.12); him.face(13.6, 14.4, mouth=0.15); him.face(14.9, 15.2, mouth=0.9)
    rope = Stick("rope", 0.018, PAL["rope"], lambda f: (tuple(ARM), tuple(TOP)) if f < F(0.3) else (tuple(ARM), tuple(ARM - np.array((0, 0, 1.0)))))
    return {"cam": cam(p, (SEAT[0] + 0.4, SEAT[1], 0.42), 135), "actors": [him] + scenery(nf, case=False), "sticks": [rope],
            "callbacks": [shape_limbs(him, 1.6)], "speakers": {"OLD MAN": him},
            "say": [[0.6, 4.2, "OLD MAN"]], "cues": [[0.3, 0.9, "THE ROPE GOES, HE HITS THE ASPHALT"], [4.4, 7.3, "THE STAIN SPREADS"],
                                                    [10.0, 13.4, "HE BREATHES. LOOKS AT THE SKY"], [14.9, 15.4, "SPIT"]]}

def hpath_landing(t):
    u = min(1.0, max(0.0, (t - 0.5) / 9.0)); u = 1 - (1 - u) ** 2.2
    return np.array((PAD[0] + 8 * (1 - u), PAD[1], 32 * (1 - u))), 180.0 + 10 * (1 - u), 4 * (1 - u)

def S09_SH020(nf):
    """Low, the open case lying flat in the foreground; far back he gets up and limps to it; the helicopter comes down;
    the certificates drift away from the wash along the street (Seedance does the wind and the paper)."""
    p = (CASE[0] - 1.8, CASE[1] + 0.45, 0.35); sq(p)
    him = Actor("him", COST["him"], nf)
    prop = pose("stand", **PROP)
    him.seq([(0, prop), (1.0, prop), (2.0, pose("hands_knees", x=SEAT[0], y=SEAT[1] + 0.3, yaw=fdir(SEAT, HIMC))),
             (3.0, pose("kneel", x=SEAT[0] - 0.1, y=SEAT[1] + 0.4, yaw=fdir(SEAT, HIMC))), (3.8, pose("stand", x=SEAT[0] - 0.2, y=SEAT[1] + 0.45, yaw=fdir(SEAT, HIMC)))])
    him.path(3.8, 12.4, [(SEAT[0] - 0.2, SEAT[1] + 0.45), (-45.0, -4.2), HIMC], "limp", speed="io")
    him.blend(12.4, 13.0, pose("stand", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, CASE)), pose("crouch", x=HIMC[0], y=HIMC[1], yaw=fdir(HIMC, CASE)))
    h = PR.heli("heli")
    def src(t):
        pos = hpath_landing(t)[0]; return pos[0], pos[1], pos[2] + 3.1
    paper = wash_drift(70, (-44.0, -3.0), 7, 7, src)
    return {"cam": cam(p, (-36.0, -4.5, 1.6), 24), "actors": [him] + scenery(nf), "callbacks": [PR.heli_cb(h, hpath_landing), paper],
            "cues": [[0, 13, "ROTOR WASH GROWS"]]}

def S09_SH040(nf):
    """Wide: she steps out low under the rotors and stops a few steps from the helicopter. He limps toward her."""
    p = (-27.0, 24.0, 2.6); sq(p)
    h, hcb = heli_landed()
    him = Actor("him", COST["him"], nf); him.path(0, 4, [(-41.0, -1.4), (-38.6, -1.1)], "limp", speed="lin")
    la = Actor("lady", COST["lady"], nf)
    la.seq([(0, pose("crouch", x=DOOR[0], y=DOOR[1], yaw=fdir(DOOR, (-40, -1)))), (0.6, pose("crouch", x=DOOR[0] - 0.6, y=DOOR[1], yaw=fdir(DOOR, (-40, -1))))])
    la.path(0.6, 2.6, [(DOOR[0] - 0.6, DOOR[1]), LADYC], "walk", speed="io", base=dict(spine=14))
    la.hold(2.6, 4.0, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, (-38.6, -1.1))))
    folder = PR.hand_prop("folder", "folder")
    paper = still_papers(50, (-40.0, -1.0), 8, 9)
    return {"cam": cam(p, (-33.0, -0.5, 1.2), 24), "actors": [him, la] + scenery(nf), "callbacks": [hcb, paper, PR.chest(folder, him, out=0.16, low=0.3)],
            "cues": [[0, 4, "ROTORS"]]}

def lady(nf, **kw):
    a = Actor("lady", COST["lady"], nf); a.hold(0, nf / core.FPS, pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, MEET), **kw)); return a

def S09_SH050(nf):
    """Medium on him over her shoulders (her back to us): a slow limp up to her, the folder low at his chest; he holds it out."""
    p = (LADYC[0] + 1.25, LADYC[1] + 0.55, 1.62); sq(p)
    h, hcb = heli_landed()
    him = Actor("him", COST["him"], nf)
    start = (MEET[0] - 2.2, MEET[1] - 0.15)
    him.path(0, 4.0, [start, MEET], "limp", speed="lin", blend=0.0)
    him.blend(4.0, 4.6, pose("stand", x=MEET[0], y=MEET[1], yaw=fdir(MEET, LADYC)), pose("stand", x=MEET[0], y=MEET[1], yaw=fdir(MEET, LADYC), ra=(62, 5, 25)))
    him.hold(4.6, 6.0, pose("stand", x=MEET[0], y=MEET[1], yaw=fdir(MEET, LADYC), ra=(62, 5, 25))); him.talk(3.4, 5.2)
    folder = PR.hand_prop("folder", "folder")
    held = PR.chest(folder, him, out=0.16, low=0.3); out = folder_hold_out(folder, him, LADYC)
    def fcb(f):
        held(f) if f < F(4.1) else out(f)
    him.compute()
    return {"cam": cam(p, (MEET[0] - 0.4, MEET[1], 1.45), 40, focus=(him, HEAD), fstop=2.4), "actors": [him, lady(nf)] + scenery(nf), "callbacks": [hcb, fcb],
            "speakers": {"OLD MAN": him}, "say": [[3.4, 5.2, "OLD MAN"]]}

def folder_hold_out(o, actor, toward, t0=4.1, t1=4.6):
    """He moves the folder from his chest out toward her, at chest height (the shape has no arms)."""
    def cb(f):
        J = actor.J[min(f, actor.nf - 1)]; up = J[NECK] - J[PELVIS]; up /= np.linalg.norm(up) + 1e-9
        d = np.array((toward[0], toward[1], 0.0)) - J[PELVIS]; d[2] = 0; fwd = d / (np.linalg.norm(d) + 1e-9)
        right = np.cross(fwd, up); u = min(1.0, max(0.0, (f / core.FPS - t0) / (t1 - t0))); u = u * u * (3 - 2 * u)
        c = J[PELVIS] + up * (0.34 + 0.04 * u) + fwd * (0.16 + 0.3 * u)
        o.matrix_world = Puppet.M(np.stack([right, fwd, up], 1), c)
    return cb

# ------------------------------------------------------------------ her close-ups (SH060, SH080, SH100, SH120): one frame
FRAME_A = ((LADYC[0] - 1.38, LADYC[1] + 0.6, 1.62), 40)     # close on her from his side, the helicopter door behind her to the left
AIM_LEFT = 4.0                                              # degrees: her face a little right of centre, the door well inside the frame

def folder_low(o_closed, o_open, actor, phases, h=0.45, out=0.3, tilt=38.0):
    """The folder held low at her chest (the shape has no arms), tipped toward her face like a book being read.
    phases(t) -> (state, u): ("offered", u) held out by him toward her; ("take", u) moving to her chest; ("held", 0);
    open/closed is chosen by phases(t)[2]."""
    def cb(f):
        t = f / core.FPS; J = actor.J[min(f, actor.nf - 1)]
        up = J[NECK] - J[PELVIS]; up /= np.linalg.norm(up) + 1e-9
        fw = J[NOSE] - J[HEAD]; fw = fw - up * np.dot(fw, up); fw /= np.linalg.norm(fw) + 1e-9
        right = np.cross(fw, up)
        a = fw * math.cos(math.radians(tilt)) + up * math.sin(math.radians(tilt)); nrm = np.cross(a, right)
        c_read = J[PELVIS] + up * h * actor.c.get("scale", 1.0) + fw * out
        st, u, opened = phases(t)
        if st == "held":
            c, R = c_read, np.stack([right, nrm, a], 1)
        else:
            c_off = J[PELVIS] + up * 0.36 + fw * 0.62; R_off = np.stack([right, -fw, up], 1)       # upright, held out by him
            if st == "offered":
                c, R = c_off, R_off
            else:
                c = c_off * (1 - u) + c_read * u; M = R_off * (1 - u) + np.stack([right, nrm, a], 1) * u
                q, _ = np.linalg.qr(M); R = q * np.sign(np.diag(_))[None]
        o_closed.hide_render = opened; o_open.hide_render = not opened
        for o in (o_closed, o_open):
            o.matrix_world = Puppet.M(R, c)
    return cb

def folders():
    mb = core.MB(None, detail=False); mb.box(-0.11, 0.11, -0.008, 0.008, -0.155, 0.155, "#3A4A6A"); closed = PR.mesh_obj("folder", mb)
    mb = core.MB(None, detail=False); mb.box(-0.22, 0.22, -0.006, 0.006, -0.155, 0.155, "#3A4A6A")
    mb.box(-0.205, -0.01, -0.0075, -0.0065, -0.14, 0.14, "#EDE6D2"); mb.box(0.01, 0.205, -0.0075, -0.0065, -0.14, 0.14, "#EDE6D2")
    mb.box(-0.205, -0.01, 0.0065, 0.0075, -0.14, 0.14, "#EDE6D2"); mb.box(0.01, 0.205, 0.0065, 0.0075, -0.14, 0.14, "#EDE6D2")
    opened = PR.mesh_obj("folder_open", mb)
    return closed, opened

def her_cam(la, focus=None):
    """One fixed frame for SH060, SH080, SH100, SH120 (generation pairs): aimed from her standing head, a little low
    (her face in the upper half, the folder at the bottom of frame) and a little left (the door well inside the frame)."""
    pos = np.array(FRAME_A[0]); la.compute()
    hd = fk(pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, MEET)))[HEAD] + np.array((0.0, 0.0, -0.12))
    d = hd - pos; a = math.radians(AIM_LEFT); c, s = math.cos(a), math.sin(a)
    tgt = pos + np.array((c * d[0] - s * d[1], s * d[0] + c * d[1], d[2]))
    return cam(tuple(pos), tuple(tgt), FRAME_A[1], focus=focus or (la, HEAD), fstop=2.0)

def her_close(nf, la, extra=(), focus=None, cbs=()):
    return {"cam": her_cam(la, focus), "actors": [la] + list(extra) + scenery(nf), "callbacks": list(cbs)}

def S09_SH060(nf):
    """Close on her, the helicopter behind: she takes the folder he holds out, brings it low to her chest and opens it
    to the last page. Her face stays clear. Silence. (One generation with SH080.)"""
    sq(FRAME_A[0]); h, hcb = heli_landed()
    la = Actor("lady", COST["lady"], nf); Y = fdir(LADYC, MEET)
    la.seq([(0, pose("stand", x=LADYC[0], y=LADYC[1], yaw=Y)), (0.7, pose("stand", x=LADYC[0], y=LADYC[1], yaw=Y, hpitch=8)),
            (1.6, pose("stand", x=LADYC[0], y=LADYC[1], yaw=Y, hpitch=24, spine=5)), (4.0, pose("stand", x=LADYC[0], y=LADYC[1], yaw=Y, hpitch=27, spine=5))])
    cl, op = folders()
    def ph(t):
        if t < 0.7: return ("offered", 0.0, False)
        if t < 1.6: u = (t - 0.7) / 0.9; return ("take", u * u * (3 - 2 * u), False)
        return ("held", 0.0, t >= 2.3)
    return her_close(nf, la, cbs=[hcb, folder_low(cl, op, la, ph)])

def S09_SH080(nf):
    """Close on her: it starts as she looks up from the folder at him. She closes it. About to say something. She waits."""
    sq(FRAME_A[0]); h, hcb = heli_landed()
    la = Actor("lady", COST["lady"], nf); Y = fdir(LADYC, MEET)
    la.seq([(0, pose("stand", x=LADYC[0], y=LADYC[1], yaw=Y, hpitch=27, spine=5)), (0.7, pose("stand", x=LADYC[0], y=LADYC[1], yaw=Y, hpitch=-2, spine=2)),
            (4.0, pose("stand", x=LADYC[0], y=LADYC[1], yaw=Y, hpitch=-3, spine=2))])
    la.face(1.9, 2.4, mouth=0.3)
    cl, op = folders()
    return her_close(nf, la, cbs=[hcb, folder_low(cl, op, la, lambda t: ("held", 0.0, t < 1.3))])

def S09_SH090(nf):
    """Close on him from her side: chin up, a challenge. Then he limps off toward the helicopter."""
    p = (MEET[0] + 1.35, MEET[1] + 0.65, 1.62); sq(p)
    h, hcb = heli_landed()
    him = Actor("him", COST["him"], nf); him.hold(0, 3.0, pose("stand", x=MEET[0], y=MEET[1], yaw=fdir(MEET, LADYC), hpitch=-12))
    him.path(3.0, 4.0, [MEET, (MEET[0] + 0.7, MEET[1] - 0.6)], "limp", speed="in")
    him.compute()
    cl, op = folders()
    la = lady(nf)
    return {"cam": cam(p, tuple(him.J[0, HEAD] + np.array((0, 0, -0.05))), 50, focus=(him, HEAD), fstop=2.0), "actors": [him, la] + scenery(nf),
            "callbacks": [hcb, folder_low(cl, op, la, lambda t: ("held", 0.0, False))]}

def S09_SH100(nf):
    """Same frame as her close-up: he limps past her to the door, half turns, says it in focus; the focus pulls to her;
    behind her, out of focus, he climbs in, still in frame at the end. (One generation with SH120.)"""
    sq(FRAME_A[0]); h, hcb = heli_landed()
    la = lady(nf)
    him = Actor("him", COST["him"], nf)
    him.path(0, 3.8, [(MEET[0] + 0.7, MEET[1] - 0.6), (LADYC[0] + 0.8, LADYC[1] - 0.45), DOORP], "limp", speed="io")
    yd = fdir(DOORP, LADYC) + 40
    him.blend(3.8, 4.4, pose("stand", x=DOORP[0], y=DOORP[1], yaw=-90), pose("point_chin", x=DOORP[0], y=DOORP[1], yaw=yd))
    him.hold(4.4, 5.9, pose("point_chin", x=DOORP[0], y=DOORP[1], yaw=yd)); him.talk(4.4, 5.8)
    # he climbs in: a foot up onto the cabin floor, leaning into the doorway (the body is solid: he stays outside its skin)
    him.seq([(5.9, pose("stand", x=DOORP[0], y=DOORP[1], yaw=-90)), (6.5, pose("stand", x=DOORP[0] + 0.25, y=DOORP[1], yaw=-90, spine=14, ll=(75, 6, 85))),
             (7.0, pose("stand", x=DOORP[0] + 0.4, y=DOORP[1], yaw=-90, z=1.25, spine=22, ll=(80, 6, 95), rl=(-5, 4, 10)))])
    cl, op = folders()
    d = her_close(nf, la, extra=[him], focus=[(0, (la, HEAD)), (1.2, (him, HEAD)), (5.7, (him, HEAD)), (6.4, (la, HEAD))],
                  cbs=[hcb, folder_low(cl, op, la, lambda t: ("held", 0.0, False))])
    d["speakers"] = {"OLD MAN": him}; d["say"] = [[4.4, 5.8, "OLD MAN"]]
    return d

def S09_SH110(nf):
    """Her point of view: the certificates among the bodies, lying still (Seedance moves the paper in the wash)."""
    p = (LADYC[0] - 0.3, LADYC[1], 1.62); sq(p)
    h, hcb = heli_landed()
    paper = still_papers(70, (-46.0, -2.5), 8, 11)
    return {"cam": cam(p, (-50.0, -3.5, 0.4), 28), "actors": scenery(nf), "callbacks": [hcb, paper], "cues": [[0, 3, "ROTOR WASH, PAPER FLUTTERING"]]}

def S09_SH120(nf):
    """Close on her face, same frame: Not anymore. She turns and walks to the helicopter, slowly."""
    sq(FRAME_A[0]); h, hcb = heli_landed()
    la = Actor("lady", COST["lady"], nf); Y0 = fdir(LADYC, FRAME_A[0][:2]) + 25
    la.hold(0, 3.2, pose("stand", x=LADYC[0], y=LADYC[1], yaw=Y0)); la.look(0.3, 3.2, (-50.0, -2.0, 0.3)); la.talk(1.4, 2.8)
    la.blend(3.2, 3.8, pose("stand", x=LADYC[0], y=LADYC[1], yaw=Y0), pose("stand", x=LADYC[0], y=LADYC[1], yaw=fdir(LADYC, DOOR)))
    la.path(3.8, 6.0, [LADYC, (DOOR[0] - 0.5, DOOR[1])], "walk", speed="in")
    cl, op = folders()
    d = her_close(nf, la, cbs=[hcb, folder_low(cl, op, la, lambda t: ("held", 0.0, False))])
    d["speakers"] = {"BUSINESS LADY": la}; d["say"] = [[1.4, 2.8, "BUSINESS LADY"]]
    return d
