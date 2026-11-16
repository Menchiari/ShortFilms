"""Empty location plates for the Seedream remap. Usage: python plates.py <out_dir>
Same sets as the animatic, no figures, 1680x720 (21:9). Square lowered to Leonard's mood image."""
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
import core, inspect
from sets import avenue, square

PLATES = {
    # name: (set builder, kwargs, camera position, target, lens mm)
    "main-street": (avenue, {"hr": (16, 26)}, (90, -6, 1.7), (-300, 1, 6), 40),
    "square": (square, {"hr": (9, 15)}, (-8, -24, 1.7), (-41.6, -6.0, 4.0), 32),
}

def render(out_dir, name):
    fn, kw, pos, tgt, lens = PLATES[name]
    sc = core.reset(sky="day")
    sc.render.resolution_x, sc.render.resolution_y = 1680, 720
    fn(pos, **{k: v for k, v in kw.items() if k in inspect.signature(fn).parameters})
    cd = bpy.data.cameras.new("CAM"); cd.sensor_width = 36; cd.clip_start = 0.05; cd.clip_end = 6000; cd.lens = lens
    cam = bpy.data.objects.new("CAM", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = pos
    cam.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(out_dir, f"plate_{name}.png")
    bpy.ops.render.render(write_still=True)
    print("DONE", name, flush=True)

if __name__ == "__main__":
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    for n in (sys.argv[2:] or PLATES):
        render(out, n)
