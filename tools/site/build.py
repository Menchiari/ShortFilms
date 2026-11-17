#!/usr/bin/env python3
"""Build the public site into dist/ from the films in this repository.

  python3 tools/site/build.py [--out dist] [--films-dir films]

Only public material is copied: films with "public": true, and inside them only what their
"publish" flags allow. private/ and _local/ folders are never read. Python 3 standard library only.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from filmlib import ROOT, iter_shots, load_json, loved_take, stats  # noqa: E402

BIBLE_GROUPS = ["characters", "locations", "props", "vehicles"]
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_PUBLISH = {"story": True, "analysis": True, "bible": True, "shotlist": True, "takes": True,
                   "prompts": True, "costs": True, "sound": True, "music": True, "edit": True}
MAX_SITE_FILE = 25 * 1024 * 1024  # Cloudflare Pages limit per file


def shot_state(shot, lt):
    """Status the site shows: a loved take approves the shot, takes without a select mean review."""
    status = shot.get("status") or "planned"
    if status == "cut":
        return "cut"
    if lt or status == "approved":
        return "approved"
    if shot.get("takes"):
        return status if status == "generating" else "review"
    return status


def shot_quality(shot, lt):
    """Rating of the loved take, else the best rating among the takes, else None."""
    if lt and lt.get("rating"):
        return lt["rating"]
    return max((t.get("rating") or 0 for t in shot.get("takes", [])), default=0) or None


def is_template(rel, text):
    """True when a film document is still its unfilled copy from templates/film/."""
    tpl = ROOT / "templates" / "film" / rel
    if not tpl.is_file():
        return False
    t = re.sub(r"<!--.*?-->", "", tpl.read_text(encoding="utf-8"), flags=re.S).strip()
    pattern = re.escape(t).replace(r"\{\{", "{{").replace(r"\}\}", "}}")
    pattern = re.sub(r"\{\{[A-Z]+\}\}", ".*", pattern)
    return re.fullmatch(pattern, text, flags=re.S) is not None


def commit_id():
    sha = os.environ.get("GITHUB_SHA", "")
    if not sha:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
        sha = r.stdout.strip()
    return sha[:7]


class Builder:
    def __init__(self, out, films_dir):
        self.out = out
        self.films_dir = films_dir

    def copy(self, film_dir, rel):
        """Copy one file of a film into dist and return its site-relative path."""
        src = film_dir / rel
        if not rel or not src.is_file():
            return ""
        parts = Path(rel).parts
        if "private" in parts or "_local" in parts:
            return ""
        dest = self.out / "films" / film_dir.name / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return f"films/{film_dir.name}/{Path(rel).as_posix()}"

    def doc(self, film_dir, rel):
        path = film_dir / rel
        if not path.is_file():
            return None
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S).strip()
        if len(text.splitlines()) <= 1 or is_template(rel, text):  # template left empty
            return None
        title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), path.stem)
        body = "\n".join(ln for ln in text.splitlines() if not ln.startswith("# ")).strip()
        summary = next((ln.strip() for ln in body.splitlines()
                        if ln.strip() and not ln.startswith(("#", "|", "-", "*", ">"))), "")
        self.copy(film_dir, rel)
        return {"title": title, "summary": summary[:240], "path": f"films/{film_dir.name}/{rel}",
                "base": f"films/{film_dir.name}/{Path(rel).parent.as_posix()}/"}

    def bible(self, film_dir):
        groups = []
        for name in ["style", "world"]:
            item = self.doc(film_dir, f"03-bible/{name}.md")
            if item:
                groups.append({"name": name, "items": [item]})
        for g in BIBLE_GROUPS:
            gdir = film_dir / "03-bible" / g
            if not gdir.is_dir():
                continue
            items = []
            def order(md):
                m = re.search(r"<!--[^>]*?order:\s*(\d+)", md.read_text(encoding="utf-8")[:400])
                return (int(m.group(1)) if m else 10_000, md.name)
            for md in sorted(gdir.glob("*.md"), key=order):
                if md.name.startswith("_"):
                    continue
                item = self.doc(film_dir, f"03-bible/{g}/{md.name}")
                if not item:
                    continue
                refs = sorted(p for p in (gdir / "refs").glob(f"{md.stem}*")
                              if p.suffix.lower() in IMAGE_EXT) if (gdir / "refs").is_dir() else []
                item["images"] = [self.copy(film_dir, f"03-bible/{g}/refs/{p.name}") for p in refs]
                items.append(item)
            if items:
                groups.append({"name": g, "items": items})
        return groups

    def shotlist(self, film_dir, shotlist, publish):
        scenes = []
        for scene in shotlist.get("scenes", []):
            shots = []
            for shot in scene.get("shots", []):
                lt = loved_take(shot)
                takes = []
                for t in shot.get("takes", []):
                    entry = {k: t.get(k) for k in ["id", "date", "mode", "duration_s", "resolution",
                                                    "aspect", "love", "rating", "rating_source"]}
                    if publish["costs"]:
                        entry["credits"] = t.get("credits")
                    video = film_dir / (t.get("file") or "_none_")
                    if publish["takes"] and video.is_file() and video.stat().st_size <= MAX_SITE_FILE:
                        entry["video"] = self.copy(film_dir, t["file"])
                    if publish["prompts"] and t.get("prompt") and (film_dir / t["prompt"]).is_file():
                        entry["prompt"] = (film_dir / t["prompt"]).read_text(encoding="utf-8").strip()
                    entry["notes"] = t.get("notes", "")
                    entry["poster"] = self.copy(film_dir, t.get("poster", ""))
                    if t is lt or t.get("love"):
                        entry["references"] = [self.copy(film_dir, r) for r in t.get("references", [])]
                    takes.append(entry)
                keep = ["id", "status", "description", "purpose", "framing", "angle", "lens", "movement",
                        "duration_s", "transition_in", "characters", "props", "dialogue", "note"]
                s = {k: shot.get(k) for k in keep}
                s["status"] = shot_state(shot, lt)
                s["quality"] = shot_quality(shot, lt)
                ap = shot.get("approach") or {}
                s["method"] = ap.get("method", "")
                s["takes"] = takes
                s["loved"] = lt.get("id") if lt else None
                anim = shot.get("animatic") or {}
                clip = film_dir / (anim.get("file") or "_none_")
                if publish["takes"] and clip.is_file() and clip.stat().st_size <= MAX_SITE_FILE:
                    s["animatic"] = {"video": self.copy(film_dir, anim["file"]), "draft": anim.get("draft", "")}
                shots.append(s)
            scenes.append({k: scene.get(k) for k in ["id", "title", "location", "time", "summary"]}
                          | {"shots": shots})
        return scenes

    def film(self, film_dir):
        film = load_json(film_dir / "film.json")
        if not film.get("public", False):
            return None
        sl_path = film_dir / "shotlist.json"
        shotlist = load_json(sl_path) if sl_path.exists() else {"scenes": []}
        publish = DEFAULT_PUBLISH | (film.get("publish") or {})
        st = stats(film, shotlist)
        if not publish["costs"]:
            st.pop("credits", None)
            st.pop("estimated_credits", None)

        poster = self.copy(film_dir, film.get("poster", ""))
        if not poster:
            for _, shot in iter_shots(shotlist):
                lt = loved_take(shot)
                if lt and lt.get("poster"):
                    poster = self.copy(film_dir, lt["poster"])
                    break

        data = {
            "slug": film_dir.name, "id": film.get("id"), "title": film.get("title"),
            "project": film.get("project", ""),
            "logline": film.get("logline", ""), "status": film.get("status", ""),
            "created": film.get("created", ""), "format": film.get("format", {}),
            "stages": film.get("stages", {}), "links": film.get("links", {}),
            "log": film.get("log", []), "poster": poster, "stats": st,
            "schedule": film.get("schedule") or {},
            "docs": {}, "bible": [], "scenes": [],
        }
        # a document is published only when its flag allows it and its stage has started,
        # so empty templates never reach the site
        started = {k for k, v in (film.get("stages") or {}).items() if v in ("in-progress", "done")}
        docs = [("story", "story", "story", "01-story/story.md"),
                ("analysis", "analysis", "analysis", "02-analysis/analysis.md"),
                ("questions", "analysis", "analysis", "02-analysis/questions.md"),
                ("budget", "costs", "shot_plan", "04-shotlist/BUDGET.md"),
                ("sound", "sound", "sound_list", "06-sound/SFX.md"),
                ("music", "music", "music", "07-music/analysis.md"),
                ("edit", "edit", "edit", "08-edit/EDIT.md")]
        for key, flag, stage, rel in docs:
            if publish.get(flag) and stage in started:
                data["docs"][key] = self.doc(film_dir, rel)
        data["docs"] = {k: v for k, v in data["docs"].items() if v}
        if publish["bible"] and "bible" in started:
            data["bible"] = self.bible(film_dir)
        if publish["shotlist"]:
            data["scenes"] = self.shotlist(film_dir, shotlist, publish)
        return data

    def run(self):
        if self.out.exists():
            shutil.rmtree(self.out)
        (self.out / "data" / "films").mkdir(parents=True)
        shutil.copytree(HERE / "static", self.out, dirs_exist_ok=True)

        site_cfg = ROOT / "site.json"
        site = load_json(site_cfg) if site_cfg.exists() else {}
        summaries = []
        film_dirs = sorted(p for p in self.films_dir.iterdir()
                           if p.is_dir() and (p / "film.json").exists()) if self.films_dir.exists() else []
        for d in film_dirs:
            data = self.film(d)
            if not data:
                continue
            (self.out / "data" / "films" / f"{d.name}.json").write_text(
                json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
            summary = {k: data[k] for k in ["slug", "id", "title", "project", "logline", "status", "created",
                                             "poster", "stats", "format", "links"]}
            summary["strip"] = [
                {"id": f"{sc['id']} {sh['id']}", "status": sh["status"], "loved": bool(sh["loved"]),
                 "quality": sh["quality"]}
                for sc in data["scenes"] for sh in sc["shots"] if sh["status"] != "cut"
            ]
            summary["deadline"] = (data["schedule"] or {}).get("deadline", "")
            summaries.append(summary)
        site["films"] = sorted(summaries, key=lambda f: f["id"] or "", reverse=True)
        site["built"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        site["commit"] = commit_id()
        (self.out / "data" / "site.json").write_text(json.dumps(site, ensure_ascii=False, indent=1),
                                                     encoding="utf-8")
        size = sum(p.stat().st_size for p in self.out.rglob("*") if p.is_file())
        biggest = max((p for p in self.out.rglob("*") if p.is_file()), key=lambda p: p.stat().st_size)
        print(f"Built {self.out} : {len(summaries)} public films, "
              f"{sum(1 for p in self.out.rglob('*') if p.is_file())} files, {size / 1e6:.1f} MB "
              f"(largest {biggest.name} {biggest.stat().st_size / 1e6:.1f} MB)")
        if biggest.stat().st_size > MAX_SITE_FILE:
            raise SystemExit(f"{biggest} is over Cloudflare's 25 MiB per-file limit.")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=str(ROOT / "dist"))
    p.add_argument("--films-dir", default=str(ROOT / "films"))
    a = p.parse_args()
    Builder(Path(a.out).resolve(), Path(a.films_dir).resolve()).run()


if __name__ == "__main__":
    main()
