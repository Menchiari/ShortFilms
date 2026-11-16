"""Physics shared by the shots (MuJoCo, mjdoll.py): the haul, the hanging, the drop, and deaths.
Everything is cached per run so continuous shots start from the same state."""
import math
import numpy as np
import core
import mjdoll as M

ARM = np.array((-39.62, -6.62, 8.75))        # end of the street light arm, 0.4 m off the corner curb (y = -7)
TOP = np.array((ARM[0], ARM[1], 2.75))       # his right ankle when hung
LIE = (-39.9, -5.9)                          # where he lies before the haul
ROPE_FINAL = float(ARM[2] - TOP[2])
CORNER = [(-43.5, -35.5, -10.5, -7.0), (-43.5, -40.0, -31.5, -10.5)]   # the square's corner sidewalks, whatever set was built last
_C = {}


def _tone_live(t, d, crunch=(), kicks=(), protect=None, reach=(), hold_free_leg=True):
    """A conscious man hanging by the right ankle: body held straight, free leg bent forward, arms loose."""
    cr = max([M.pulse(t, t0, 1.6) for t0 in crunch] + [0.0])
    k = max([M.pulse(t, t0, 0.5) for t0 in kicks] + [0.0])
    re = max([M.pulse(t, t0, 1.2) for t0 in reach] + [0.0])
    g = {"waist_x": (-75 * cr, 150), "waist_y": (0, 150), "waist_z": (0, 100),
         "neck_x": (-15 - 30 * cr, 25), "neck_y": (0, 20), "neck_z": (0, 20),
         "rhip_x": (5 + 50 * cr, 120), "rhip_y": (0, 150), "rhip_z": (0, 80), "rkn_x": (-3, 120), "ran_x": (0, 20),
         "lhip_x": (30 + 40 * k + 30 * cr, 70), "lhip_y": (2, 120), "lhip_z": (0, 60), "lkn_x": (-80 + 60 * k, 35), "lan_x": (15, 5),
         "lsh_y": (10, 2), "rsh_y": (-10, 2)}
    arm = max(cr, re)
    g.update({"lsh_x": (150 * arm, 3 + 30 * arm), "rsh_x": (150 * arm, 3 + 30 * arm), "lel_x": (60 * arm, 2 + 10 * arm), "rel_x": (60 * arm, 2 + 10 * arm)})
    if protect is not None and t >= protect:
        # forearms over the head (toward the ground while he hangs)
        g.update({"lsh_x": (165, 60), "rsh_x": (165, 60), "lel_x": (110, 30), "rel_x": (110, 30), "lsh_y": (25, 20), "rsh_y": (-25, 20), "neck_x": (-35, 30)})
    return g


def haul(T=4.0):
    """Lying on his back by the curb, hauled up by the right ankle (rope shortened by the crowd), fighting."""
    if "haul" in _C:
        return _C["haul"]
    d = M.Doll(rope=tuple(ARM), sidewalks=CORNER); d.place((LIE[0], LIE[1], 0.13), yaw=0, lying="back")
    L0 = float(np.linalg.norm(d.joints()[15] - ARM)) + 0.05; d.set_rope(L0)
    keys = [(0.0, 0.0), (0.5, 0.0), (0.9, 0.25), (1.2, 0.3), (1.6, 0.55), (1.9, 0.6), (2.4, 0.85), (2.7, 0.92), (3.1, 1.0)]
    rf = lambda t: L0 + (ROPE_FINAL - L0) * float(np.interp(t, [k[0] for k in keys], [k[1] for k in keys]))
    ctrl = lambda t, dd: _tone_live(t, dd, crunch=(2.9,), kicks=(0.8, 1.5, 2.2), reach=(1.0, 2.0))
    JA = d.run(T, ctrl=ctrl, rope_fn=rf, tone=20, settle=0.3)
    _C["haul"] = JA; _C["haul_state"] = d.state()
    # settle into a calm hang for the shots that follow
    d.run(4.0, ctrl=lambda t, dd: _tone_live(t, dd), rope_fn=lambda t: ROPE_FINAL, tone=20)
    _C["settled"] = d.state()
    return JA


def hanging(T, struggle=0.0, seed=7, hits=(), protect=None, hit_body="lfarm", release=None):
    """Hanging from the settled state. hits: times of pipe blows (on the raised forearm). release: time the rope is cut."""
    haul()
    rng = np.random.default_rng(seed)
    crunch = tuple(sorted(rng.uniform(0.2, max(0.3, T - 1.0), int(round(2 * struggle))))) if struggle else ()
    kicks = tuple(sorted(rng.uniform(0.0, T, int(round(6 * struggle))))) if struggle else ()
    d = M.Doll(rope=tuple(ARM), sidewalks=CORNER); d.set_state(_C["settled"]); d.set_rope(ROPE_FINAL)
    def forces(t, dd):
        out = []
        for th in hits:
            if th <= t < th + 0.07:
                out.append((hit_body, np.array((0.0, -1.0, 0.25)) * 900.0))
                out.append(("torso", np.array((0.0, -1.0, 0.1)) * 400.0))
        return out
    ctrl = lambda t, dd: _tone_live(t, dd, crunch=crunch, kicks=kicks, protect=protect)
    rf = (lambda t: ROPE_FINAL if (release is None or t < release) else 100.0)
    return d.run(T, ctrl=ctrl, rope_fn=rf, tone=20, forces=forces)


def drop(T, release=0.3, seed=3):
    """The rope is shot: he falls beside the curb, shoulder first, then curls up (the acting after that is the shape)."""
    if ("drop", T) in _C:
        return _C[("drop", T)]
    haul()
    d = M.Doll(rope=tuple(ARM), sidewalks=CORNER); d.set_state(_C["settled"]); d.set_rope(ROPE_FINAL)
    def ctrl(t, dd):
        if t < release:
            return _tone_live(t, dd)
        # falling: arms come in, then he curls toward the camera side, knees up
        u = min(1.0, (t - release) / 0.8)
        return {"waist_x": (-40 * u, 60), "lhip_x": (70 * u, 40), "rhip_x": (70 * u, 40), "lkn_x": (-90 * u, 25), "rkn_x": (-90 * u, 25),
                "lsh_x": (60, 8), "rsh_x": (60, 8), "lel_x": (100, 6), "rel_x": (100, 6), "neck_x": (-30, 15)}
    JA = d.run(T, ctrl=ctrl, rope_fn=lambda t: ROPE_FINAL if t < release else 100.0, tone=10)
    _C[("drop", T)] = JA
    return JA


def death(pos, yaw, T, speed=0.0, hit=(0.0, 0.0, 0.0), hit_t=0.02, buckle=True, scale=1.0, wide=1.0, q=None, seed=0):
    """Shot: the body goes limp. buckle: knees give first, he drops where he stands (no movie flying back).
    pos: (x, y) of the pelvis on the ground; speed: forward speed when hit (runners); hit: impulse direction*size at the head."""
    key = ("death", round(pos[0], 2), round(pos[1], 2), round(yaw, 1), T, round(speed, 2), tuple(np.round(hit, 2)), buckle, scale, wide, seed)
    if key in _C:
        return _C[key]
    rng = np.random.default_rng(seed)
    fwd = np.array((-math.sin(math.radians(yaw)), math.cos(math.radians(yaw)), 0.0))
    d = M.Doll(scale=scale, wide=wide)
    q0 = dict(q or {}); q0.setdefault("lhip_x", rng.uniform(-10, 25)); q0.setdefault("rhip_x", rng.uniform(-10, 25))
    q0.setdefault("lkn_x", rng.uniform(-30, -5)); q0.setdefault("rkn_x", rng.uniform(-30, -5))
    gz = max(core.ground_z(pos[0] + dx, pos[1] + dy) for dx in (-0.3, 0, 0.3) for dy in (-0.3, 0, 0.3))   # on a sidewalk: start on top of it
    d.place((pos[0], pos[1], 1.004 * scale + 0.01 + gz), yaw=yaw, q=q0, vel=tuple(fwd * speed))
    side = rng.uniform(-1, 1)
    def ctrl(t, dd):
        if buckle and t < 0.45:
            u = min(1.0, t / 0.3)
            return {"lkn_x": (-120 * u, 60), "rkn_x": (-110 * u, 60), "lhip_x": (80 * u, 50), "rhip_x": (75 * u, 50),
                    "waist_x": (-30 * u, 30), "waist_y": (12 * side * u, 20), "neck_x": (-20 * u, 5)}
        if not buckle and hit_t + 0.1 < t < hit_t + 0.7:
            # a shot runner: the knees give as he goes down, nobody lands on straight locked legs
            u = min(1.0, (t - hit_t - 0.1) / 0.25)
            return {"lkn_x": (-75 * u, 35), "rkn_x": (-60 * u, 35), "lhip_x": (35 * u, 15), "rhip_x": (25 * u, 15)}
        if t > 0.7:
            # dead weight: the knees fold under it, so nobody stays bent over on locked legs
            return {"lkn_x": (-70, 14), "rkn_x": (-60, 14), "lhip_x": (45, 4), "rhip_x": (40, 4)}
        return {}
    tip = np.array((math.cos(rng.uniform(0, 6.28)), math.sin(rng.uniform(0, 6.28)), 0.0)) * 0.5 + fwd * 0.5
    def forces(t, dd):
        out = []
        if hit_t <= t < hit_t + 0.05:
            out.append(("head", np.array(hit, float) * 20.0))
        if buckle and 0.45 <= t < 0.75:
            out.append(("torso", tip * 160.0))
        if t > 0.9 and dd.d.xpos[dd.bid["pelvis"]][2] > 0.5:
            out.append(("pelvis", (tip * 0.6 + np.array((0.0, 0.0, -0.4))) * 300.0))   # hips left high: the dead weight goes over
        return out
    JA = d.run(T, ctrl=ctrl, tone=0.6, forces=forces)
    _C[key] = JA
    return JA
