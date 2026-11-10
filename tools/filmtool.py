#!/usr/bin/env python3
"""Film project tool. On Windows use `python`, on Mac and Linux `python3`.

  python tools/filmtool.py new "Title" [--id 007]
  python tools/filmtool.py status [film]
  python tools/filmtool.py render <film>
  python tools/filmtool.py add-take <film> S01 SH010 --credits 35 --duration 5 --resolution 720p
        [--mode t2v] [--aspect 21:9] [--job JOB_ID] [--no-audio] [--file PATH]
  python tools/filmtool.py rate <film> S01 SH010 T02 --rating 4 [--love] [--inferred] [--notes "..."]
  python tools/filmtool.py log <film> "What happened"
  python tools/filmtool.py check
  python tools/filmtool.py get 001        add one film to a sparse clone
  python tools/filmtool.py hooks          install the 95 MB commit guard (once per computer)
"""

import argparse
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from filmlib import (  # noqa: E402
    FILMS, MAX_FILE_MB, ROOT, SHOT_STATUSES, STAGES, TEMPLATE, film_dirs, find_film, iter_shots,
    load_film, load_json, loved_take, save_json, slugify, stats,
)

TODAY = dt.date.today().isoformat()
WARN_TOTAL_GB = 4.0


def disk_mb(path):
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file() and "_local" not in f.parts) / 1e6


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def cmd_new(args):
    FILMS.mkdir(exist_ok=True)
    used = [int(d.name[:3]) for d in film_dirs() if d.name[:3].isdigit()]
    fid = args.id.zfill(3) if args.id else str((max(used) + 1) if used else 1).zfill(3)
    if any(d.name.startswith(fid + "-") for d in film_dirs()):
        raise SystemExit(f"Film id {fid} already exists.")
    slug = f"{fid}-{slugify(args.title)[:40].rstrip('-')}"
    dest = FILMS / slug
    if dest.exists():
        raise SystemExit(f"{dest} already exists, nothing done.")
    shutil.copytree(TEMPLATE, dest)
    for path in dest.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json", ".txt"}:
            text = path.read_text(encoding="utf-8")
            text = (text.replace("{{ID}}", fid).replace("{{SLUG}}", slug)
                    .replace("{{TITLE}}", args.title).replace("{{DATE}}", TODAY))
            path.write_text(text, encoding="utf-8")
    (dest / "_local").mkdir(exist_ok=True)
    print(f"Created films/{slug}")
    print("Next: put the story in 01-story/source/ or paste it to Claude.")


def cmd_status(args):
    dirs = [find_film(args.film)] if args.film else film_dirs()
    if not dirs:
        print("No films yet. Start one with: python tools/filmtool.py new \"Title\"")
        return
    total = 0.0
    for d in dirs:
        film, shotlist = load_film(d)
        s = stats(film, shotlist)
        print(f"{d.name}  [{film.get('status')}]  {film.get('title')}")
        print(f"  stages {s['stages_done']}/{s['stages_total']}   shots {s['shots_done']}/{s['shots_total']}"
              f" ({s['shot_progress'] * 100:.0f}%)   takes {s['takes']}   loved {s['loved']}"
              f"   credits {s['credits']:g} (estimate {s['estimated_credits']:g})")
        stages = film.get("stages", {})
        line = "  " + "  ".join(f"{k}:{stages.get(k, 'todo')}" for k in STAGES)
        print(line)
        mb = disk_mb(d)
        total += mb
        print(f"  size on disk {mb:.1f} MB")
    if not args.film:
        print(f"All films on disk: {total / 1000:.2f} GB (GitHub guidance: under 5 GB; warning at {WARN_TOTAL_GB:g} GB)")


def cmd_render(args):
    d = find_film(args.film)
    film, shotlist = load_film(d)
    s = stats(film, shotlist)
    out = [f"# Shotlist: {film.get('title')}", "",
           "Rendered from `shotlist.json` by `tools/filmtool.py render`. Do not edit by hand.", "",
           f"Shots approved {s['shots_done']}/{s['shots_total']}, takes {s['takes']}, "
           f"planned runtime {s['planned_seconds']} s, credits spent {s['credits']:g}, "
           f"estimate {s['estimated_credits']:g}.", ""]
    for scene in shotlist.get("scenes", []):
        out += [f"## {scene.get('id')} {scene.get('title', '')}".rstrip(), ""]
        meta = ", ".join(x for x in [scene.get("location", ""), scene.get("time", "")] if x)
        if meta:
            out += [f"*{meta}*", ""]
        if scene.get("summary"):
            out += [scene["summary"], ""]
        out += ["| Shot | Status | Framing | Angle | Lens | Move | Sec | In | Method | Takes | Loved | What |",
                "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for shot in scene.get("shots", []):
            ap = shot.get("approach") or {}
            lt = loved_take(shot)
            cells = [shot.get("id", ""), shot.get("status", ""), shot.get("framing", ""),
                     shot.get("angle", ""), shot.get("lens", ""), shot.get("movement", ""),
                     str(shot.get("duration_s", "")), shot.get("transition_in", ""),
                     ap.get("method", ""), str(len(shot.get("takes", []))),
                     lt.get("id") if lt else "", shot.get("description", "")]
            out.append("| " + " | ".join(c.replace("|", "/").replace("\n", " ") for c in cells) + " |")
        out.append("")
    target = d / "04-shotlist" / "SHOTLIST.md"
    target.parent.mkdir(exist_ok=True)
    target.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {target.relative_to(ROOT)}")


def _get_shot(shotlist, scene_id, shot_id):
    for scene, shot in iter_shots(shotlist):
        if scene.get("id") == scene_id and shot.get("id") == shot_id:
            return shot
    raise SystemExit(f"Shot {scene_id} {shot_id} not found in shotlist.json")


def cmd_add_take(args):
    d = find_film(args.film)
    film, shotlist = load_film(d)
    shot = _get_shot(shotlist, args.scene, args.shot)
    takes = shot.setdefault("takes", [])
    n = max([int(t["id"][1:]) for t in takes if t.get("id", "T").lstrip("T").isdigit()] or [0]) + 1
    tid = f"T{n:02d}"
    base = f"{film['id']}_{args.scene}_{args.shot}_{tid}"
    take = {
        "id": tid, "date": TODAY, "model": args.model, "mode": args.mode,
        "duration_s": args.duration, "resolution": args.resolution, "aspect": args.aspect,
        "audio": not args.no_audio, "credits": args.credits, "job_id": args.job or "",
        "prompt": f"05-generation/prompts/{base}.txt",
        "file": args.file or "", "preview": "", "poster": "", "references": [],
        "love": False, "rating": None, "rating_source": None, "notes": "",
    }
    if not (d / take["prompt"]).exists():
        print(f"Warning: prompt file {take['prompt']} does not exist yet. Write it before committing.")
    takes.append(take)
    shot["status"] = "review"
    save_json(d / "shotlist.json", shotlist)
    print(f"Added {args.scene} {args.shot} {tid}  ({base})")


def cmd_rate(args):
    d = find_film(args.film)
    film, shotlist = load_film(d)
    shot = _get_shot(shotlist, args.scene, args.shot)
    for t in shot.get("takes", []):
        if t.get("id") == args.take:
            if args.rating is not None:
                t["rating"] = args.rating
                t["rating_source"] = "inferred" if args.inferred else "user"
            if args.love is not None:
                t["love"] = args.love
            if args.notes:
                t["notes"] = args.notes
            if t.get("love"):
                shot["status"] = "approved"
            save_json(d / "shotlist.json", shotlist)
            print(f"{args.scene} {args.shot} {args.take}: rating {t.get('rating')} love {t.get('love')}")
            return
    raise SystemExit(f"Take {args.take} not found.")


def cmd_log(args):
    d = find_film(args.film)
    film = load_json(d / "film.json")
    film.setdefault("log", []).append({"date": TODAY, "text": args.text})
    save_json(d / "film.json", film)
    print("Logged.")


def cmd_check(args):
    problems = []
    for d in film_dirs():
        try:
            film, shotlist = load_film(d)
        except Exception as e:  # malformed JSON
            problems.append(f"{d.name}: cannot read JSON ({e})")
            continue
        for key in ["id", "slug", "title", "status", "stages", "publish"]:
            if key not in film:
                problems.append(f"{d.name}/film.json: missing '{key}'")
        if film.get("slug") and film["slug"] != d.name:
            problems.append(f"{d.name}/film.json: slug '{film['slug']}' does not match folder")
        for k in film.get("stages", {}):
            if k not in STAGES:
                problems.append(f"{d.name}/film.json: unknown stage '{k}'")
        for scene, shot in iter_shots(shotlist):
            sid = f"{d.name} {scene.get('id')} {shot.get('id')}"
            if shot.get("status") not in SHOT_STATUSES:
                problems.append(f"{sid}: bad status '{shot.get('status')}'")
            for t in shot.get("takes", []):
                for key in ["file", "preview", "poster", "prompt"]:
                    rel = t.get(key)
                    if rel and not (d / rel).exists():
                        problems.append(f"{sid} {t.get('id')}: {key} missing on disk ({rel})")
                if t.get("love") and not t.get("file"):
                    problems.append(f"{sid} {t.get('id')}: loved take has no file in git")
        for path in d.rglob("*"):
            if "_local" in path.parts or not path.is_file():
                continue
            mb = path.stat().st_size / 1_000_000
            if mb > MAX_FILE_MB:
                problems.append(f"{path.relative_to(ROOT)}: {mb:.1f} MB is over {MAX_FILE_MB} MB")
    total_gb = sum(disk_mb(d) for d in film_dirs()) / 1000
    if total_gb > WARN_TOTAL_GB:
        print(f"WARNING: films take {total_gb:.2f} GB on disk, nearing GitHub's 5 GB guidance. Tell the user.")
    if problems:
        print("\n".join(problems))
        raise SystemExit(1)
    print(f"OK ({len(film_dirs())} films, {total_gb:.2f} GB)")


def cmd_get(args):
    fid = args.film.zfill(3) if args.film.isdigit() else args.film
    r = git("ls-tree", "-d", "--name-only", "HEAD", "films/")
    names = [n.split("/", 1)[1] for n in r.stdout.split() if n.startswith("films/")]
    match = [n for n in names if n == fid or n.startswith(fid + "-")]
    if not match:
        raise SystemExit(f"No film starting with {fid}- on this branch.")
    if git("config", "core.sparseCheckout").stdout.strip() != "true":
        print(f"This clone is complete, films/{match[0]} is already here.")
        return
    r = git("sparse-checkout", "add", f"films/{match[0]}")
    if r.returncode:
        raise SystemExit(r.stderr)
    print(f"Ready: films/{match[0]}")


def cmd_hooks(args):
    r = git("config", "core.hooksPath", "tools/hooks")
    if r.returncode:
        raise SystemExit(r.stderr)
    print("Commit guard installed: commits with a file over 95 MB will be refused.")


def main():
    p = argparse.ArgumentParser(description="ShortFilms film tool")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("new"); a.add_argument("title"); a.add_argument("--id")
    a.set_defaults(func=cmd_new)
    a = sub.add_parser("status"); a.add_argument("film", nargs="?"); a.set_defaults(func=cmd_status)
    a = sub.add_parser("render"); a.add_argument("film"); a.set_defaults(func=cmd_render)

    a = sub.add_parser("add-take")
    for name in ["film", "scene", "shot"]:
        a.add_argument(name)
    a.add_argument("--credits", type=float, required=True)
    a.add_argument("--duration", type=int, required=True)
    a.add_argument("--resolution", required=True)
    a.add_argument("--aspect", default="")
    a.add_argument("--mode", default="t2v")
    a.add_argument("--model", default="seedance_2_5")
    a.add_argument("--job")
    a.add_argument("--file")
    a.add_argument("--no-audio", action="store_true")
    a.set_defaults(func=cmd_add_take)

    a = sub.add_parser("rate")
    for name in ["film", "scene", "shot", "take"]:
        a.add_argument(name)
    a.add_argument("--rating", type=int, choices=range(1, 6))
    a.add_argument("--love", dest="love", action="store_true", default=None)
    a.add_argument("--unlove", dest="love", action="store_false")
    a.add_argument("--inferred", action="store_true")
    a.add_argument("--notes")
    a.set_defaults(func=cmd_rate)

    a = sub.add_parser("log"); a.add_argument("film"); a.add_argument("text"); a.set_defaults(func=cmd_log)
    a = sub.add_parser("check"); a.set_defaults(func=cmd_check)
    a = sub.add_parser("get"); a.add_argument("film"); a.set_defaults(func=cmd_get)
    a = sub.add_parser("hooks"); a.set_defaults(func=cmd_hooks)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
