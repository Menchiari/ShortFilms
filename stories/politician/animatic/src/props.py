"""Props: the car, the helicopter, the dog, the briefcase, small hand props, bills, dust. Per-frame callbacks."""
import math, random
import numpy as np
import bpy
from mathutils import Matrix
import core
from core import MB, PAL
from puppet import Puppet, NJ, HEAD, NECK, PELVIS, LHA, RHA, LEL, REL, LSH, RSH, NOSE, _mesh_cyl, _mesh_box, _mesh_sphere, _obj

def mesh_obj(name, mb):
    mb.d = None
    return mb.build(name)

def place(o, pos, yaw_deg=0.0, extra=None):
    R = Puppet.frame(np.array((0, 0, 1.0)), np.array((math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg)), 0)))
    m = Puppet.M(R, np.array(pos, float))
    if extra is not None:
        m = m @ extra
    o.matrix_world = m

# ------------------------------------------------------------------ car (local: +y forward, driver on the left, x right)
def car(name="car", door_open=0.0, glass=True):
    mb = MB(None, detail=False); k = PAL["car"]; g = PAL["carglass"]
    mb.box(-0.93, 0.93, -2.45, 2.45, 0.32, 0.82, k)                    # body
    mb.box(-0.9, 0.9, 1.3, 2.5, 0.82, 0.9, k)                          # hood slope (flat)
    mb.box(-0.9, 0.9, -2.5, -1.6, 0.82, 0.92, k)                       # trunk
    mb.box(-0.86, 0.86, -1.25, 0.95, 1.5, 1.56, k)                     # roof
    for x in (-0.86, 0.78):
        mb.box(x, x + 0.08, 0.95, 1.05, 0.82, 1.5, k); mb.box(x, x + 0.08, -1.3, -1.2, 0.82, 1.5, k); mb.box(x, x + 0.08, -0.2, -0.12, 0.82, 1.5, k)
    mb.box(-0.86, 0.86, 1.25, 1.33, 0.82, 0.88, k)
    mb.box(-0.88, 0.88, 0.95, 1.3, 0.82, 1.05, "#2A2622")              # dashboard
    for x in (-0.42, 0.42):
        mb.box(x - 0.26, x + 0.26, -0.45, 0.1, 0.38, 0.6, PAL["seat"]); mb.box(x - 0.26, x + 0.26, -0.55, -0.42, 0.6, 1.22, PAL["seat"])
    mb.box(-0.85, 0.85, -1.2, -0.85, 0.38, 1.1, PAL["seat"])
    mb.box(-0.95, 0.95, 2.42, 2.5, 0.45, 0.6, "#8C8C88")                # bumper
    o = mesh_obj(name, mb)
    wheel = _obj(name + "_wheel", _mesh_cyl(name + "_wheel", 0.19, 0.19, 0.03, n=16), "#202020", o)
    wheel.location = (-0.42, 0.75, 1.02); wheel.rotation_euler = (math.radians(-62), 0, 0)
    door = _obj(name + "_door", _mesh_box(name + "_door", 0.03, 0.55, 0.32, 0.82), k, None)
    door.parent = o
    bob = bpy.data.objects.new(name + "_bob", None); bpy.context.scene.collection.objects.link(bob); bob.parent = o
    bob.location = (0.38, 1.08, 1.05)
    _obj(name + "_bob_base", _mesh_cyl(name + "_bob_base", 0.03, 0.03, 0.015), "#3A3A3A", bob)
    bb = _obj(name + "_bob_body", _mesh_cyl(name + "_bob_body", 0.022, 0.018, 0.06), "#9DB8D6", bob); bb.location = (0, 0, 0.015)
    hd = bpy.data.objects.new(name + "_bob_neck", None); bpy.context.scene.collection.objects.link(hd); hd.parent = bob; hd.location = (0, 0, 0.08)
    h = _obj(name + "_bob_head", _mesh_sphere(name + "_bob_head", 0.035, 0.95, 1.0, 1.1, seg=10, rings=7), "#C9A085", hd); h.location = (0, 0, 0.035)
    hr = _obj(name + "_bob_hair", _mesh_sphere(name + "_bob_hair", 0.036, 0.95, 1.0, 0.75, seg=8, rings=5), "#5A3A22", hd); hr.location = (0, -0.006, 0.048)
    fi = _obj(name + "_bob_finger", _mesh_box(name + "_bob_finger", 0.005, 0.005, 0.0, 0.035), "#C9A085", bob); fi.location = (0.026, 0.01, 0.06)
    ar = _obj(name + "_bob_arm", _mesh_box(name + "_bob_arm", 0.007, 0.007, 0.0, 0.04), "#9DB8D6", bob); ar.location = (0.026, 0.005, 0.03)
    for side, e in (("l", -0.012), ("r", 0.012)):
        ey = _obj(name + "_bob_eye" + side, _mesh_sphere(name + "_bob_eye" + side, 0.005, seg=6, rings=4), "#151515", hd); ey.location = (e, 0.032, 0.04)
    mo = _obj(name + "_bob_mouth", _mesh_box(name + "_bob_mouth", 0.012, 0.003, -0.002, 0.003), "#7A2A22", hd); mo.location = (0, 0.033, 0.02)
    for i, (x, y) in enumerate(((-0.82, 1.55), (0.82, 1.55), (-0.82, -1.55), (0.82, -1.55))):
        wh = _obj(name + f"_tire{i}", _mesh_cyl(name + f"_tire{i}", 0.36, 0.36, 0.25, n=14), "#141414", o)
        wh.location = (x - 0.125 if x < 0 else x + 0.125, y, 0.36); wh.rotation_euler = (0, math.radians(90 if x < 0 else -90), 0)
        hub = _obj(name + f"_hub{i}", _mesh_cyl(name + f"_hub{i}", 0.2, 0.2, 0.27, n=10), "#7A7A78", o)
        hub.location = wh.location; hub.rotation_euler = wh.rotation_euler
    o["door"] = door.name; o["bobneck"] = hd.name
    set_door(o, door_open)
    return o

def set_door(o, amount):
    d = bpy.data.objects[o["door"]]
    a = math.radians(-65 * amount)
    hinge = np.array((-0.93, 0.95, 0.0))
    R = np.array(((math.cos(a), -math.sin(a), 0), (math.sin(a), math.cos(a), 0), (0, 0, 1)))
    off = hinge + R @ np.array((0.0, -0.55, 0.0))
    d.matrix_parent_inverse = Matrix.Identity(4)
    d.location = tuple(off); d.rotation_euler = (0, 0, a)

def car_world(pos, yaw, lx, ly, lz=0.0):
    """Car-local point to world."""
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    return np.array((pos[0] + c * lx - s * ly, pos[1] + s * lx + c * ly, lz))

def bob_nod(o, amp_fn):
    hd = bpy.data.objects[o["bobneck"]]
    def cb(f):
        t = f / core.FPS; a = amp_fn(t)
        hd.rotation_euler = (math.radians(a * math.sin(t * 11.0)), 0, 0)
    return cb

# ------------------------------------------------------------------ helicopter (local: +y nose, door on +x)
def heli(name="heli", door=True):
    mb = MB(None, detail=False); w = PAL["heli"]; dk = PAL["heli_dark"]
    mb.box(-1.05, 1.05, -1.9, 1.7, 0.55, 2.35, w)
    mb.box(-0.95, 0.95, 1.7, 2.9, 0.65, 2.05, w); mb.box(-0.7, 0.7, 2.9, 3.6, 0.8, 1.7, w)
    mb.box(-0.85, 0.85, 1.85, 2.95, 1.55, 2.06, dk)               # windshield band
    mb.box(-0.9, 0.9, -2.5, -1.9, 0.9, 2.2, w)
    mb.box(-0.32, 0.32, -7.8, -2.5, 1.45, 2.05, w)                # tail boom
    mb.box(-0.12, 0.12, -8.6, -7.6, 1.3, 3.2, w)                  # fin (fenestron)
    mb.box(-1.4, 1.4, -7.2, -6.8, 1.6, 1.7, w)                    # stabilizer
    mb.box(-0.5, 0.5, -1.0, 0.8, 2.35, 2.75, w)                   # engine cowling
    for x in (-1.06, 1.02):
        mb.box(x, x + 0.04, 0.9, 1.6, 1.35, 1.95, dk)             # cabin windows
        mb.box(x, x + 0.04, -1.6, -0.9, 1.35, 1.95, dk)
    if door:
        mb.box(1.04, 1.07, -1.5, 0.5, 0.75, 2.15, "#151515")      # open sliding door
        mb.box(1.08, 1.13, -3.4, -1.5, 0.75, 2.15, w)              # the door slid back
    for x in (-1.15, 1.15):
        mb.box(x - 0.05, x + 0.05, -1.9, 2.0, 0.0, 0.08, "#9A9A9A")
        mb.box(x - 0.04, x + 0.04, 1.2, 1.3, 0.08, 0.55, "#9A9A9A"); mb.box(x - 0.04, x + 0.04, -1.2, -1.1, 0.08, 0.55, "#9A9A9A")
    mb.cyl(0, 0, 2.75, 3.1, 0.12, "#3A3A3A", n=8)
    o = mesh_obj(name, mb)
    rot = bpy.data.objects.new(name + "_rotor", None); bpy.context.scene.collection.objects.link(rot); rot.parent = o; rot.location = (0, 0, 3.1)
    for i in range(5):
        b = _obj(name + f"_blade{i}", _mesh_box(name + f"_blade{i}", 0.16, 0.02, 0.0, 6.6), "#2E2E2E", rot)
        b.rotation_euler = (0, math.radians(90), math.radians(72 * i))
    o["rotor"] = rot.name
    return o

def heli_cb(o, path_fn, spin=True):
    """path_fn(t) -> (pos (3,), yaw_deg, bank_deg)."""
    rot = bpy.data.objects[o["rotor"]]
    def cb(f):
        t = f / core.FPS; pos, yaw, bank = path_fn(t)
        Ryaw = Puppet.frame(np.array((0, 0, 1.0)), np.array((math.cos(math.radians(yaw)), math.sin(math.radians(yaw)), 0)))
        bk = math.radians(bank)
        Rroll = np.array(((math.cos(bk), 0, math.sin(bk)), (0, 1, 0), (-math.sin(bk), 0, math.cos(bk))))
        o.matrix_world = Puppet.M(Ryaw @ Rroll, np.array(pos, float))
        if spin:
            rot.rotation_euler = (0, 0, t * 26.0)
    return cb

# ------------------------------------------------------------------ dog
def dog(name, pos, yaw, head_up_t=None):
    root = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(root)
    col = "#8A6A48"
    b = _obj(name + "_body", _mesh_box(name + "_body", 0.13, 0.36, 0.0, 0.2), col, root); b.location = (0, 0, 0.12)
    for (x, y) in ((-0.09, 0.25), (0.09, 0.25), (-0.09, -0.25), (0.09, -0.25)):
        lg = _obj(name + "_leg", _mesh_box(name + "_leg", 0.03, 0.03, 0.0, 0.14), col, root); lg.location = (x, y, 0.0)
        lg.rotation_euler = (math.radians(90), 0, 0) if y > 0 else (math.radians(-90), 0, 0)
    hd = bpy.data.objects.new(name + "_neck", None); bpy.context.scene.collection.objects.link(hd); hd.parent = root; hd.location = (0, 0.36, 0.18)
    h = _obj(name + "_head", _mesh_box(name + "_head", 0.08, 0.09, -0.06, 0.08), col, hd); h.location = (0, 0.05, 0)
    sn = _obj(name + "_snout", _mesh_box(name + "_snout", 0.045, 0.06, -0.04, 0.02), "#6A5038", hd); sn.location = (0, 0.15, -0.02)
    for x in (-0.05, 0.05):
        ear = _obj(name + "_ear", _mesh_box(name + "_ear", 0.02, 0.01, 0.0, 0.07), "#5A4030", hd); ear.location = (x, 0.02, 0.07)
    tl = _obj(name + "_tail", _mesh_box(name + "_tail", 0.015, 0.015, 0.0, 0.25), col, root); tl.location = (0, -0.36, 0.25); tl.rotation_euler = (math.radians(-120), 0, 0)
    root.location = (pos[0], pos[1], 0.0); root.rotation_euler = (0, 0, math.radians(yaw))
    def cb(f):
        t = f / core.FPS
        if head_up_t is None:
            hd.rotation_euler = (math.radians(-35), 0, 0); hd.location = (0, 0.36, 0.1)
        else:
            u = min(1, max(0, (t - head_up_t) / 0.4)); u = u * u * (3 - 2 * u)
            hd.rotation_euler = (math.radians(-35 + 50 * u), 0, 0); hd.location = (0, 0.36, 0.1 + 0.12 * u)
    return cb

# ------------------------------------------------------------------ small props
def briefcase(name, opened=False):
    mb = MB(None, detail=False)
    if opened:
        mb.box(-0.23, 0.23, -0.17, 0.17, 0.0, 0.08, "#8A5A30"); mb.box(-0.23, 0.23, 0.17, 0.21, 0.0, 0.34, "#8A5A30")
        mb.box(-0.2, 0.2, -0.14, 0.14, 0.02, 0.06, "#3A2A1C")
    else:
        mb.box(-0.23, 0.23, -0.06, 0.06, 0.0, 0.34, "#8A5A30"); mb.box(-0.08, 0.08, -0.015, 0.015, 0.34, 0.4, "#5A3A20")
    return mesh_obj(name, mb)

def hand_prop(name, kind):
    if kind == "gun":
        mb = MB(None, detail=False); mb.box(-0.015, 0.015, -0.02, 0.13, -0.02, 0.02, "#C8C8C8"); mb.box(-0.014, 0.014, -0.02, 0.02, -0.09, 0.0, "#5A5A5A")
    elif kind == "phone":
        mb = MB(None, detail=False); mb.box(-0.035, 0.035, -0.005, 0.005, -0.07, 0.07, "#1A1A1A")
    elif kind == "folder":
        mb = MB(None, detail=False); mb.box(-0.15, 0.15, -0.01, 0.01, -0.11, 0.11, "#3A4A6A")
    elif kind == "case":
        mb = MB(None, detail=False); mb.box(-0.23, 0.23, -0.06, 0.06, -0.34, 0.0, "#8A5A30")
    return mesh_obj(name, mb)

def attach(o, actor, joint=RHA, elbow=REL, offset=(0, 0, 0), visible=None):
    """Keep a prop in an actor's hand: oriented along the forearm."""
    def cb(f):
        if visible is not None and not visible(f):
            o.hide_render = True; return
        o.hide_render = False
        J = actor.J[min(f, actor.nf - 1)]
        z = J[joint] - J[elbow]
        R = Puppet.frame(-z, J[NECK] - J[PELVIS])
        R2 = np.stack([R[:, 0], R[:, 2], -R[:, 1]], 1)
        o.matrix_world = Puppet.M(R2, J[joint] + R2 @ np.array(offset))
    return cb

def chest(o, actor, visible=None, out=0.2):
    """The briefcase hugged flat against his chest, both arms around it (the shape has no arms)."""
    def cb(f):
        if visible is not None and not visible(f):
            o.hide_render = True; return
        o.hide_render = False
        J = actor.J[min(f, actor.nf - 1)]; up = J[NECK] - J[PELVIS]; up = up / (np.linalg.norm(up) + 1e-9)
        right = J[RSH] - J[LSH]; right = right - up * np.dot(right, up); right = right / (np.linalg.norm(right) + 1e-9)
        fwd = np.cross(up, right)
        c = J[PELVIS] + up * 0.47 + fwd * out
        R = np.stack([right, fwd, up], 1)              # case: wide along right, thin along fwd, tall along up (handle up)
        o.matrix_world = Puppet.M(R, c + up * 0.17)
    return cb

def at_ear(o, actor, side=1.0, visible=None):
    """The phone pressed to his ear: upright along the jaw, screen to the cheek."""
    def cb(f):
        if visible is not None and not visible(f):
            o.hide_render = True; return
        o.hide_render = False
        J = actor.J[min(f, actor.nf - 1)]; up = J[HEAD] - J[NECK]; up = up / (np.linalg.norm(up) + 1e-9)
        fwd = J[NOSE] - J[HEAD]; fwd = fwd - up * np.dot(fwd, up); fwd = fwd / (np.linalg.norm(fwd) + 1e-9)
        right = np.cross(fwd, up)
        tilt = up * 0.94 + fwd * 0.34; tilt /= np.linalg.norm(tilt)
        R = np.stack([fwd, right, tilt], 1)
        o.matrix_world = Puppet.M(R, J[HEAD] + right * side * 0.125 - up * 0.01)
    return cb

def papers(prefix, n, center, spread, t0, t1, rise=3.0, seed=4, drift=(0, 0), lift_from=None, hidden_before=False):
    """Bills: white flats lying, then blown around between t0 and t1. Returns a callback."""
    rnd = np.random.default_rng(seed); objs = []
    base = np.stack([center[0] + rnd.uniform(-spread, spread, n), center[1] + rnd.uniform(-spread, spread, n)], 1)
    ph = rnd.uniform(0, 6.28, (n, 4)); amp = rnd.uniform(0.5, 1.0, n); hmax = rnd.uniform(0.6, rise, n)
    for i in range(n):
        mb = MB(None, detail=False); mb.box(-0.1, 0.1, -0.045, 0.045, 0, 0.004, "#EDE6D2"); objs.append(mesh_obj(f"{prefix}{i}", mb))
    def cb(f):
        t = f / core.FPS
        for i, o in enumerate(objs):
            o.hide_render = bool(hidden_before and t < t0)
            u = 0.0 if t < t0 else min(1.0, (t - t0) / max(0.01, (t1 - t0)))
            k = u * u * (3 - 2 * u)
            x = base[i, 0] + (drift[0] * k + 2.5 * amp[i] * math.sin(ph[i, 0] + t * 1.7) * k)
            y = base[i, 1] + (drift[1] * k + 2.5 * amp[i] * math.sin(ph[i, 1] + t * 1.3) * k)
            z = 0.01 + hmax[i] * k * (0.6 + 0.4 * math.sin(ph[i, 2] + t * 2.1))
            o.location = (x, y, z)
            o.rotation_euler = (k * (ph[i, 3] + t * 4), k * (ph[i, 0] + t * 3), ph[i, 1] + k * t * 2)
    return cb

def dust(prefix, n, src_fn, t0=0.0, life=1.6, size=1.2, col="#CDB590"):
    """Dust puffs trailing a moving point: spheres that grow and drift."""
    objs = [_obj(f"{prefix}{i}", _mesh_sphere(f"{prefix}{i}", 1.0, seg=8, rings=5), col) for i in range(n)]
    def cb(f):
        t = f / core.FPS
        for i, o in enumerate(objs):
            birth = t0 + i * life / n
            age = (t - birth) % life
            p = src_fn(t - age)
            if p is None:
                o.hide_render = True; continue
            o.hide_render = False
            s = size * (0.3 + age / life)
            o.location = (p[0], p[1] + 0.3 * math.sin(i), max(0.2, s * 0.5))
            o.scale = (s, s, s * 0.6)
    return cb
