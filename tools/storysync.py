#!/usr/bin/env python3
"""Keep each film in step with its story folder. Run by .github/workflows/film-sync.yml after
every push, by hand with:  python3 tools/storysync.py

For every film whose film.json has "story_sync":
  "screenplay": shots follow the screenplay's [[SH### | seconds | size | move | note | change]]
      notes under "#S###" scene headings. New shots are added, changed ones updated (description,
      framing, movement, seconds, note), shots gone from the screenplay are marked "cut", never
      removed, takes always kept. A parse that finds no shots, or would cut more than half, changes
      nothing.
  "takes_log": takes logged in the story's takes/log.md and missing from shotlist.json (same job id)
      are added, their video and prompt copied (never moved) into the film. A take already in
      shotlist.json only gets a rating, love or notes it does not have yet.
Python 3 standard library only.
"""

import re
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from filmlib import ROOT, film_dirs, load_film, save_json, update_index  # noqa: E402


def parse_screenplay(path):
    text = re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"), flags=re.S)
    scenes = []
    for chunk in re.split(r"\n(?=\.[A-Z])", "\n" + text):
        chunk = chunk.strip()
        m = re.match(r"\.(.*?)\s*#(S\d+)#", chunk)
        if not m:
            continue
        sc = {"id": m.group(2), "title": m.group(1).strip(), "shots": []}
        parts = re.split(r"\[\[(.*?)\]\]", chunk)
        for i in range(1, len(parts), 2):
            f = [x.strip() for x in parts[i].split("|")]
            if not re.fullmatch(r"SH\d+", f[0]) or len(f) < 4:
                continue
            try:
                sec = float(f[1])
            except ValueError:
                sec = 0
            action = ""
            for block in re.split(r"\n\s*\n", parts[i + 1]):
                rows = [r.strip() for r in block.strip().split("\n") if r.strip()]
                if not rows or (rows[0].isupper() and len(rows) > 1) or rows[0].startswith(">") \
                        or rows[0].endswith("TO:"):
                    continue
                action = " ".join(rows)
                break
            sc["shots"].append({"id": f[0], "duration_s": int(sec) if sec == int(sec) else sec,
                                "framing": f[2], "movement": f[3],
                                "note": f[4] if len(f) > 4 else "", "description": action[:400]})
        if sc["shots"]:
            scenes.append(sc)
    return scenes


def sync_shots(shotlist, scenes, label):
    new_ids = {(sc["id"], s["id"]) for sc in scenes for s in sc["shots"]}
    old = {(sc["id"], sh["id"]): sh for sc in shotlist.get("scenes", []) for sh in sc.get("shots", [])}
    live_old = [k for k, sh in old.items() if sh.get("status") != "cut"]
    gone = [k for k in live_old if k not in new_ids]
    if not new_ids or (live_old and len(gone) > len(live_old) / 2):
        print(f"{label}: screenplay parse looks wrong ({len(new_ids)} shots, {len(gone)} would be cut), shots left as they are")
        return []
    changes = []
    old_scenes = {sc["id"]: sc for sc in shotlist.get("scenes", [])}
    out = []
    for sc in scenes:
        base = {k: v for k, v in old_scenes.get(sc["id"], {}).items() if k != "shots"}
        if base.get("title") != sc["title"]:
            base["title"] = sc["title"]
        base["id"] = sc["id"]
        shots = []
        for s in sc["shots"]:
            sh = old.pop((sc["id"], s["id"]), None)
            if sh is None:
                sh = {"id": s["id"], "status": "planned", "takes": []}
                changes.append(f"+{sc['id']} {s['id']}")
            else:
                if any(sh.get(k) != s[k] for k in ["description", "framing", "movement", "duration_s", "note"]):
                    changes.append(f"~{sc['id']} {s['id']}")
                if sh.get("status") == "cut":
                    sh["status"] = "planned"
                    changes.append(f"back {sc['id']} {s['id']}")
            for k in ["description", "framing", "movement", "duration_s", "note"]:
                sh[k] = s[k]
            shots.append(sh)
        out.append(dict(base, shots=shots))
    for (scid, shid), sh in old.items():          # gone from the screenplay: kept, marked cut
        if sh.get("status") != "cut":
            sh["status"] = "cut"
            changes.append(f"cut {scid} {shid}")
        target = next((x for x in out if x["id"] == scid), None)
        if target is None:
            target = dict({k: v for k, v in old_scenes[scid].items() if k != "shots"}, shots=[])
            out.append(target)
        target["shots"].append(sh)
    shotlist["scenes"] = out
    return changes


def parse_log(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        c = [x.strip() for x in line.strip().strip("|").split(" | ")]
        m = re.match(r"(\d{3})_(S\d+)_(SH\d+)_(T\d+)", c[0]) if len(c) >= 7 else None
        if not m:
            continue
        _, scene, shot, tid = m.groups()
        job, settings, credits, prompt, rating, notes = c[1:7]
        cm = re.match(r"[\d.]+", credits)
        if not cm or "refunded: 0" in credits:    # blocked by a filter: no file, no cost
            continue
        mode = re.match(r"\w+, (\w+)", settings)
        dur = re.search(r"(\d+) s\b", settings)
        res = re.search(r"\b(480p|720p|1080p)\b", settings)
        asp = re.search(r"\b(\d+:\d+)\b", settings)
        r = re.match(r"(\d)", rating)
        rows.append({
            "name": m.group(0), "scene": scene, "shot": shot, "id": tid, "job": job,
            "mode": mode.group(1) if mode else "", "duration_s": int(dur.group(1)) if dur else None,
            "resolution": res.group(1) if res else "", "aspect": asp.group(1) if asp else "",
            "credits": float(cm.group(0)), "prompt_src": prompt,
            "rating": int(r.group(1)) if r else None,
            "rating_source": ("inferred" if "inferred" in rating else "user") if r else None,
            "love": "love" in rating and "unlove" not in rating, "notes": notes,
        })
    return rows


def sync_takes(film_dir, film, shotlist, log_path, label):
    story_dir = log_path.parent.parent
    index = {(sc["id"], sh["id"]): sh for sc in shotlist.get("scenes", []) for sh in sc.get("shots", [])}
    changes = []
    for t in parse_log(log_path):
        shot = index.get((t["scene"], t["shot"]))
        if shot is None:
            print(f"{label}: {t['name']} has no shot {t['scene']} {t['shot']} in shotlist.json, skipped")
            continue
        takes = shot.setdefault("takes", [])
        mine = next((x for x in takes if x.get("job_id") == t["job"]), None)
        if mine:
            if mine.get("rating") is None and t["rating"] is not None:
                mine["rating"], mine["rating_source"] = t["rating"], t["rating_source"]
                changes.append(f"rated {t['name']}")
            if t["love"] and not mine.get("love"):
                mine["love"] = True
                changes.append(f"love {t['name']}")
            if t["notes"] and not mine.get("notes"):
                mine["notes"] = t["notes"]
            continue
        if any(x.get("id") == t["id"] for x in takes):
            print(f"{label}: {t['name']} job {t['job']} clashes with another {t['id']} in shotlist.json, skipped")
            continue
        base = f"{film['id']}_{t['scene']}_{t['shot']}_{t['id']}"
        take = {
            "id": t["id"], "date": date.today().isoformat(), "model": "seedance_2_5", "mode": t["mode"],
            "duration_s": t["duration_s"], "resolution": t["resolution"], "aspect": t["aspect"],
            "audio": True, "credits": t["credits"], "job_id": t["job"],
            "prompt": f"05-generation/prompts/{base}.txt",
            "file": f"05-generation/takes/{t['scene']}/{t['shot']}/{base}.mp4",
            "preview": "", "poster": "", "references": [],
            "love": t["love"], "rating": t["rating"], "rating_source": t["rating_source"],
            "notes": t["notes"],
        }
        for src, key in [(story_dir / t["prompt_src"], "prompt"),
                         (story_dir / "takes" / t["scene"] / t["shot"] / f"{t['name']}.mp4", "file")]:
            dest = film_dir / take[key]
            if src.is_file() and not dest.exists():
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
            if not dest.exists():
                take[key] = ""
        takes.append(take)
        takes.sort(key=lambda x: x.get("id", ""))
        changes.append(f"+{t['name']}")
    return changes


def refresh_status(shotlist):
    for sc in shotlist.get("scenes", []):
        for sh in sc.get("shots", []):
            if sh.get("status") == "cut":
                continue
            if any(t.get("love") for t in sh.get("takes", [])):
                sh["status"] = "approved"
            elif sh.get("takes") and sh.get("status") in ("planned", "ready"):
                sh["status"] = "review"


def main():
    total = 0
    for d in film_dirs():
        film, shotlist = load_film(d)
        cfg = film.get("story_sync") or {}
        if not cfg:
            continue
        before = repr(shotlist)
        changes = []
        sp = ROOT / cfg.get("screenplay", "")
        if cfg.get("screenplay") and sp.is_file():
            changes += sync_shots(shotlist, parse_screenplay(sp), d.name)
        log = ROOT / cfg.get("takes_log", "")
        if cfg.get("takes_log") and log.is_file():
            changes += sync_takes(d, film, shotlist, log, d.name)
        refresh_status(shotlist)
        if repr(shotlist) != before:
            save_json(d / "shotlist.json", shotlist)
            total += 1
            print(f"{d.name}: {len(changes)} changes: {' '.join(changes[:60])}{' ...' if len(changes) > 60 else ''}")
        else:
            print(f"{d.name}: in step")
    if total:
        update_index()


if __name__ == "__main__":
    main()
