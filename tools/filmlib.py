"""Shared helpers for the film tools and the site builder. Python 3 standard library only."""

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILMS = ROOT / "films"
TEMPLATE = ROOT / "templates" / "film"

STAGES = [
    "story", "analysis", "bible", "shotlist", "shot_plan", "sound_list", "references",
    "generation", "framerate", "edit", "sound_design", "music", "release",
]
SHOT_STATUSES = ["planned", "ready", "generating", "review", "approved", "cut"]
MAX_FILE_MB = 95


def slugify(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "untitled"


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def film_dirs():
    if not FILMS.exists():
        return []
    return sorted(p for p in FILMS.iterdir() if p.is_dir() and (p / "film.json").exists())


def find_film(ref):
    """Accept '001', '1', '001-slug' or a path."""
    p = Path(ref)
    if (p / "film.json").exists():
        return p.resolve()
    ref = str(ref)
    if ref.isdigit():
        ref = ref.zfill(3)
    for d in film_dirs():
        if d.name == ref or d.name.startswith(ref + "-"):
            return d
    raise SystemExit(f"Film not found: {ref}")


def load_film(path):
    film = load_json(path / "film.json")
    shotlist_path = path / "shotlist.json"
    shotlist = load_json(shotlist_path) if shotlist_path.exists() else {"scenes": []}
    return film, shotlist


def iter_shots(shotlist):
    for scene in shotlist.get("scenes", []):
        for shot in scene.get("shots", []):
            yield scene, shot


def loved_take(shot):
    loved = [t for t in shot.get("takes", []) if t.get("love")]
    if not loved:
        return None
    return max(loved, key=lambda t: (t.get("rating") or 0, t.get("id", "")))


def stats(film, shotlist):
    shots = [s for _, s in iter_shots(shotlist) if s.get("status") != "cut"]
    done = [s for s in shots if loved_take(s) or s.get("status") == "approved"]
    takes = [t for s in shots for t in s.get("takes", [])]
    take_credits = sum(t.get("credits") or 0 for _, s in iter_shots(shotlist) for t in s.get("takes", []))
    extra = sum(c.get("credits") or 0 for c in film.get("extra_costs", []))
    planned_seconds = sum(s.get("duration_s") or 0 for s in shots)
    stages = film.get("stages", {})
    stages_done = sum(1 for k in STAGES if stages.get(k) == "done")
    return {
        "scenes": len(shotlist.get("scenes", [])),
        "shots_total": len(shots),
        "shots_done": len(done),
        "takes": len(takes),
        "loved": sum(1 for t in takes if t.get("love")),
        "credits": round(take_credits + extra, 2),
        "planned_seconds": planned_seconds,
        "shot_progress": round(len(done) / len(shots), 4) if shots else 0,
        "stages_done": stages_done,
        "stages_total": len(STAGES),
        "estimated_credits": sum((s.get("approach") or {}).get("estimated_credits") or 0 for s in shots),
    }
