#!/usr/bin/env python3
"""Poster still for the site (the site shows no video, to stay light).

  python tools/media/preview.py <film> S01 SH010 T03     one take, updates shotlist.json
  python tools/media/preview.py <film> --loved             every loved take without a poster
  python tools/media/preview.py --file clip.mp4 --out DIR  any clip

Poster: JPEG frame at 40% of the clip, 1280 px wide at most (about 100 to 250 KB).
"""

import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from filmlib import find_film, iter_shots, load_film, save_json  # noqa: E402


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                        "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True)
    return float(r.stdout.strip() or 0)


def make(src, out_dir):
    src, out_dir = Path(src), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    jpg = out_dir / f"{src.stem}.jpg"
    t = duration(src) * 0.4
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i",
                    str(src), "-frames:v", "1", "-vf", "scale='min(1280,iw)':-2", "-q:v", "4", str(jpg)],
                   check=True)
    print(f"{jpg.name} {jpg.stat().st_size / 1e3:.0f} KB")
    return jpg


def for_take(film_dir, take):
    src = film_dir / take["file"]
    if not take.get("file") or not src.exists():
        print(f"{take.get('id')}: no file on disk, skipped")
        return False
    jpg = make(src, film_dir / "05-generation" / "web")
    take["poster"] = jpg.relative_to(film_dir).as_posix()
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("film", nargs="?")
    p.add_argument("scene", nargs="?")
    p.add_argument("shot", nargs="?")
    p.add_argument("take", nargs="?")
    p.add_argument("--loved", action="store_true")
    p.add_argument("--file")
    p.add_argument("--out", default=".")
    a = p.parse_args()

    if a.file:
        make(a.file, a.out)
        return
    if not a.film:
        p.error("give a film, or --file")
    d = find_film(a.film)
    film, shotlist = load_film(d)
    changed = False
    for scene, shot in iter_shots(shotlist):
        for t in shot.get("takes", []):
            if a.loved and t.get("love") and not t.get("poster"):
                changed |= for_take(d, t)
            elif (scene.get("id"), shot.get("id"), t.get("id")) == (a.scene, a.shot, a.take):
                changed |= for_take(d, t)
    if changed:
        save_json(d / "shotlist.json", shotlist)


if __name__ == "__main__":
    main()
