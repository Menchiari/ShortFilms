"""Clean per-shot clips for Seedance references: python3 clips.py <out_dir> <faceless_dir> <dest_dir>
Every rendered shot becomes <dest>/<SHOT>.mp4 at 24 fps, no labels, no subtitles. Shots whose shapes showed eye and
mouth slits take their frames from <faceless_dir> (rendered with SHAPE_SLITS=0) when it has them."""
import sys, os, json, glob, subprocess
out, faceless, dest = sys.argv[1:4]; os.makedirs(dest, exist_ok=True); n = 0
for d in sorted(glob.glob(os.path.join(out, "S*_SH*"))):
    sid = os.path.basename(d); m = json.load(open(os.path.join(d, "meta.json")))
    if m.get("card"): continue
    src = os.path.join(faceless, sid) if m.get("slits") and glob.glob(os.path.join(faceless, sid, "f_*.png")) else d
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "12", "-i", os.path.join(src, "f_%04d.png"), "-r", "24", "-c:v", "libx264",
                    "-crf", "23", "-preset", "medium", "-pix_fmt", "yuv420p", os.path.join(dest, sid + ".mp4")], check=True); n += 1
print(n, "clips")
