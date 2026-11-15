"""Render animatic v2 shots. Usage: python run2.py <out_dir> <shot ids...>  (PREVIEW=1 renders 3 frames per shot)"""
import sys, os, json, math, time, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))
import numpy as np
import bpy
from mathutils import Vector, Quaternion, Euler
from bpy_extras.object_utils import world_to_camera_view
import core
from puppet import Puppet, MixedPuppet, HEAD, NECK, PELVIS, R_J
from parse import parse

SCRIPT = os.path.join(HERE, "..", "..", "screenplay.fountain")

def catmull(P, u):
    """Catmull-Rom through points P (k,3) at global parameter u in [0,1]."""
    P = np.asarray(P, float); k = len(P)
    if k == 1: return P[0]
    if k == 2: return P[0] + (P[1] - P[0]) * u
    s = u * (k - 1); i = min(int(s), k - 2); t = s - i
    p0 = P[max(0, i - 1)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(k - 1, i + 2)]
    return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)

def ease(u, kind):
    u = max(0.0, min(1.0, u))
    if kind == "io": return u * u * (3 - 2 * u)
    if kind == "io2": return u * u * u * (u * (6 * u - 15) + 10)
    if kind == "in": return u * u
    if kind == "out": return 1 - (1 - u) ** 2
    return u

def cam_at(spec, t, T, actors):
    if "fn" in spec:
        return spec["fn"](t)
    if "follow" in spec:
        a = spec["follow"]; j = spec.get("joint", PELVIS); lag = spec.get("lag", 0.25)
        f = int(round(t * core.FPS)); n = max(1, int(round(lag * core.FPS)))
        pts = [a.J[min(a.nf - 1, max(0, f - k)), j] for k in range(n)]
        tgt = np.mean(pts, axis=0) + np.array(spec.get("offset", (0, 0, 0)))
        pos = spec["pos"](t) if callable(spec["pos"]) else np.array(spec["pos"], float)
        return pos, tgt, spec.get("lens", 50), spec.get("roll", 0)
    keys = spec["keys"]
    if len(keys) == 1:
        k = keys[0]; return np.array(k[1], float), np.array(k[2], float), k[3], spec.get("roll", 0)
    ts = [k[0] for k in keys]
    if spec.get("spline"):
        u = ease((t - ts[0]) / max(1e-6, ts[-1] - ts[0]), spec.get("ease", "io"))
        pos = catmull([k[1] for k in keys], u); tgt = catmull([k[2] for k in keys], u)
        lens = float(np.interp(u, np.linspace(0, 1, len(keys)), [k[3] for k in keys]))
        return pos, tgt, lens, spec.get("roll", 0)
    if t <= ts[0]:
        k = keys[0]; return np.array(k[1], float), np.array(k[2], float), k[3], spec.get("roll", 0)
    if t >= ts[-1]:
        k = keys[-1]; return np.array(k[1], float), np.array(k[2], float), k[3], spec.get("roll", 0)
    for a, b in zip(keys, keys[1:]):
        if a[0] <= t <= b[0]:
            u = ease((t - a[0]) / max(1e-6, b[0] - a[0]), spec.get("ease", "io"))
            pos = np.array(a[1]) + (np.array(b[1]) - np.array(a[1])) * u
            tgt = np.array(a[2]) + (np.array(b[2]) - np.array(a[2])) * u
            return pos, tgt, a[3] + (b[3] - a[3]) * u, spec.get("roll", 0)

def main():
    out_dir = sys.argv[1]; want = sys.argv[2:]
    meta, scenes = parse(SCRIPT)
    order = [(sc["id"], sh) for sc in scenes for sh in sc["shots"] if f"{sc['id']}_{sh['id']}" in want]
    preview = bool(os.environ.get("PREVIEW"))
    for scid, sh in order:
        sid = f"{scid}_{sh['id']}"; d = os.path.join(out_dir, sid); os.makedirs(d, exist_ok=True)
        modname = "shots_" + scid.lower()
        mod = importlib.import_module(modname) if os.path.exists(os.path.join(HERE, modname + ".py")) else None
        fn = getattr(mod, sid, None) if mod else None
        info = {"id": sid, "sec": sh["sec"], "size": sh["size"], "move": sh["move"], "card": fn is None}
        if fn is None:
            if mod and sid in getattr(mod, "CUES", {}):
                info["cues"] = mod.CUES[sid]
            json.dump(info, open(os.path.join(d, "meta.json"), "w")); print("DONE", sid, "card", flush=True); continue
        t_start = time.time()
        nf = int(round(sh["sec"] * core.FPS))
        spec = fn(nf)
        actors = spec.get("actors", [])
        for a in actors:
            if a.J is None: a.compute()
        # floor check: how far any joint's mesh dips below the ground or a sidewalk under it
        worst = [0.0, ""]
        for a in actors:
            rj = R_J * a.c.get("scale", 1.0)
            for f in range(0, nf, 2):
                if not a.visible[f]: continue
                J = a.J[f]; gz = np.array([core.ground_z(x, y) for x, y in J[:, :2]])
                dz = float(np.min(J[:, 2] - rj - gz))
                if dz < worst[0]: worst = [round(dz, 3), f"{a.name}@{f}"]
        info["below"] = worst
        pups = [MixedPuppet(a) if a.style == "shape" else Puppet(a) for a in actors]
        sticks = spec.get("sticks", [])
        sc = bpy.context.scene
        cd = bpy.data.cameras.new("CAM"); cd.sensor_width = 36; cd.clip_start = 0.05; cd.clip_end = 6000
        cam = bpy.data.objects.new("CAM", cd); sc.collection.objects.link(cam); sc.camera = cam
        cs = spec["cam"]; hh = math.radians(cs.get("hh", 0.0)); ph = np.random.default_rng(abs(hash(sid)) % 999).uniform(0, 6.28, 6)
        frames = sorted({0, nf // 2, nf - 1}) if preview else list(range(nf))
        anchors = [dict() for _ in range(nf)]
        spk = spec.get("speakers", {})
        for f in range(nf):
            t = f / core.FPS
            sc.frame_set(f + 1)
            pos, tgt, lens, roll = cam_at(cs, t, sh["sec"], actors)
            for p in pups:
                p.apply(f, (pos, lens)) if isinstance(p, MixedPuppet) else p.apply(f)
            for s in sticks: s.apply(f)
            for cb in spec.get("callbacks", []): cb(f)
            if "euler" in cs:
                e = Euler(tuple(math.radians(v) for v in cs["euler"]))
            else:
                q = (Vector(tuple(tgt)) - Vector(tuple(pos))).to_track_quat("-Z", "Y")
                if roll: q = q @ Quaternion((0, 0, 1), math.radians(roll))
                e = q.to_euler()
            if hh:
                e.x += hh * (0.6 * math.sin(t * 1.3 + ph[0]) + 0.4 * math.sin(t * 3.1 + ph[1]))
                e.z += hh * (0.6 * math.sin(t * 1.1 + ph[2]) + 0.4 * math.sin(t * 2.7 + ph[3]))
            cam.location = tuple(pos); cam.rotation_euler = e; cd.lens = lens
            bpy.context.view_layer.update()
            for name, a in spk.items():
                hp = a.J[f, HEAD] + np.array((0, 0, 0.22))
                v = world_to_camera_view(sc, cam, Vector(tuple(hp)))
                anchors[f][name] = [round(v.x, 4), round(1 - v.y, 4), round(v.z, 2)]
            if f in frames:
                sc.render.filepath = os.path.join(d, f"{'p' if preview else 'f'}_{f + 1:04d}.png")
                bpy.ops.render.render(write_still=True)
        info["anchors"] = anchors
        for k in ("say", "cues"):
            if k in spec: info[k] = spec[k]
        info["render_s"] = round(time.time() - t_start, 1)
        json.dump(info, open(os.path.join(d, "meta.json"), "w"))
        print("DONE", sid, info["render_s"], "below", info["below"], flush=True)

main()
