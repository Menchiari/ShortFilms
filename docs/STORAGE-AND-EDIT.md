# Storage (git without LFS) and editing (DaVinci Resolve)

## What GitHub allows

- A single file over 100 MiB is rejected on push. Git warns above 50 MiB.
- GitHub's guidance is to keep a repository ideally under 1 GB and strongly under 5 GB. This is a
  soft limit: nothing breaks at 5 GB, but GitHub can ask the owner to reduce it.
- Git keeps every committed version forever. Deleting a file later does not shrink the repository.

So the rule is about **what** we commit, not only how big each file is.

## What goes in git

| In git | Not in git (stays in Higgsfield or `_local/`) |
|---|---|
| All documents, `film.json`, `shotlist.json`, prompts | Rejected takes (tracked by Higgsfield job id, re-downloadable) |
| Loved takes, original Seedance file | ProRes or other intermediates from the framerate fix (only the final fixed file, under 95 MB, replaces the original) |
| Reference stills, start and end frames | Resolve cache, proxies, optimized media, render cache |
| Muted web previews and posters for the site | Final masters over 95 MB (export a second, compressed version for git) |
| SFX files, music takes, the Resolve `.drp` | |

Every film has a `_local/` folder that git ignores. Anything big or temporary goes there.

A pre-commit hook refuses any file over 95 MB. Install it once per computer:

```
sh tools/install-hooks.sh
```

### Size math

Repository growth per film is about `loved takes x average take size + previews + stills`. I don't
know the real size of a Seedance 2.5 1080p file yet. The first generated take gets measured and the
number goes here, so we can see how many films fit under the 5 GB guidance before planning a split
(for example one archive repository per year). We act on the measurement, not on a guess.

## Working on one film from any computer

You do not need a branch per film. Git can download only one film folder:

```
git clone --filter=blob:none --sparse https://github.com/Menchiari/ShortFilms.git ~/ShortFilms
cd ~/ShortFilms
git sparse-checkout set tools templates docs
sh tools/get-film.sh 001
```

The partial clone (`--filter=blob:none`) downloads file contents only for what you check out; the
sparse checkout limits that to the shared tools plus `films/001-*`. Another film later:

```
sh tools/get-film.sh 002
```

Then the normal loop: `git pull` before you start, `git add`, `git commit`, `git push` when you
stop.

## DaVinci Resolve

### Facts that shape the setup

- Resolve does not keep a project as a folder. Projects live in Resolve's database. A project
  travels as one `.drp` file (Project Manager: right click, Export Project / Import Project). This
  works in the free version.
- Media links inside a project are absolute paths. If the repository sits at the same path on
  every computer, media never goes offline. If not, one relink fixes it (select all clips, Relink
  Selected Clips, choose the film folder) or a Mapped Mount in Preferences > System > Media Storage
  translates paths between Mac and Windows.
- Automation: Blackmagic's 21.1 release notes say Python scripting moved to the Studio version.
  Community tests report that Lua scripts in the Workspace > Scripts menu still run in the free
  21.1, but Blackmagic does not document that, so it can disappear in an update. With Studio we can
  automate bins, timelines and relinking. Without it, the routine below is manual and short.

### The routine

Clone at the same path on every machine (recommended: `~/ShortFilms` on Mac).

First time for a film:

1. New project in Resolve named like the film folder (`001-title`), timeline 24 fps.
2. Drag `05-generation/takes`, `06-sound/sfx` and `07-music/takes` into the Media Pool.
   The bins mirror the folders: scene, then shot.
3. Edit.
4. End of session: Project Manager, right click the project, Export Project, save as
   `08-edit/001-title.drp` (overwrite the previous one, git keeps the history).
5. Commit and push.

On another computer:

1. `git pull` (or `tools/get-film.sh` the first time).
2. Project Manager, Import Project, pick `08-edit/001-title.drp`.
3. If any clip shows offline: select all, Relink Selected Clips, pick the film folder.

Rule that prevents lost work: export the `.drp` at the end of every session, import it at the
start of a session on a different computer. Resolve's own database is local; the `.drp` in git is
the shared truth.

### Exports

Final masters go to `08-edit/exports/_local/` (ignored). A compressed copy under 95 MB can be
committed if you want one in the repository; the public version goes to YouTube or Vimeo and its
link into `film.json`.
