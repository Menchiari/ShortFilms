# Storage (git without LFS) and editing (DaVinci Resolve Free, Mac and PC)

## What GitHub allows

- A single file over 100 MiB is rejected on push. Git warns above 50 MiB.
- GitHub's guidance is to keep a repository ideally under 1 GB and strongly under 5 GB. This is a
  soft limit: nothing breaks at 5 GB, but GitHub can ask the owner to reduce it.
- Git keeps every committed version forever. Deleting a file later does not shrink the repository.

## What goes in git

Everything that belongs to the film, including every take, loved or not (decision of 2026-11-10:
scraps can be reused).

| In git | Never in git |
|---|---|
| All documents, `film.json`, `shotlist.json`, prompts | Files over 95 MB (the hook refuses them) |
| Every take, original Seedance file | ProRes and other big intermediates (film's `_local/` folder) |
| Framerate-fixed versions (`_fx`, under 95 MB) | Resolve cache, proxies, optimized media, render cache |
| Reference stills, start and end frames, previews, posters | Final masters over 95 MB (`08-edit/exports/_local/`) |
| SFX files, music takes, the Resolve `.drp` | |

### Watching the size

Keeping every take makes the repository grow faster. `python tools/filmtool.py status` prints the
size of each film on disk and the total, and `check` warns above 4 GB. I don't know the real size
of a Seedance 2.5 file yet: the first take gets measured and the number goes here. When the total
nears the 5 GB guidance, the clean way out is a second repository for finished films (for example
`ShortFilms-Archive`), decided with you before it is needed, never done silently.

## Each computer keeps its own copy

GitHub holds everything. Each computer (Mac or PC) keeps its own copy on whichever of **its own**
drives has room, and only the film you are working on. Computers never share a drive: they meet
on GitHub through `git pull` and `git push`.

**How much room.** A film needs about twice its size on a computer (the files, plus git's own
copy of them in the hidden `.git` folder). Before downloading a film, run:

```
python tools/filmtool.py space        (Mac: python3)
```

It lists every drive of that computer with its free space, and every film with its size and the
space it needs. Pick any drive with more free space than that. The sizes come from
`films-index.json`, which Claude keeps current at every commit.

**Setup, once per computer.** Install Git, Python 3 and ffmpeg
(Windows: Git for Windows, python.org with "Add python.exe to PATH" ticked, and
`winget install --id Gyan.FFmpeg -e`; Mac: `xcode-select --install` for Git, python.org for
Python, ffmpeg from ffmpeg.org or Homebrew). Then, with `<drive>` being the drive you picked
(your PC uses `D:\ShortFilms`; on the Mac for example `~/ShortFilms`):

```
git clone --filter=blob:none --sparse https://github.com/Menchiari/ShortFilms.git <drive>
cd <drive>
git sparse-checkout set tools templates docs
python tools/filmtool.py space
python tools/filmtool.py get 001
python tools/filmtool.py hooks
```

This light clone downloads the tools (a few MB), then only film 001. `get 002` adds another film.
`hooks` installs the guard that refuses commits with a file over 95 MB.

**Freeing space after a film is finished.** Everything is on GitHub once pushed. When a computer
runs short, the clean way is a fresh light clone with only the current film, on any drive; what
happens to the old folder is your call (after `git status` says nothing to commit and `git push`
is done, nothing in it is lost).

Daily loop: `git pull` before you start, `git add -A`, `git commit -m "..."`, `git push` when you
stop.

## DaVinci Resolve

### Facts that shape the setup

- Resolve does not keep a project as a folder. Projects live in Resolve's database. A project
  travels as one `.drp` file (Project Manager: right click, Export Project / Import Project). This
  works in the free version.
- Media links inside a project are absolute paths, and your Mac and your PC have different paths.
  Two ways to bridge them:
  - **Mapped Mount (set once per computer, automatic after that).** Preferences > System >
    Media Storage. Add the local ShortFilms folder, and in its "Mapped Mount" column put the path
    of the same folder on the other computer. PC: mount `D:\ShortFilms`, mapped mount
    `/Users/<you>/ShortFilms`. Mac: the reverse. If the Windows field only offers Browse, use
    Relink.
  - **Relink (always works).** Select all clips in the Media Pool, right click, Relink Selected
    Clips, pick the film folder. Every file name in this repo is unique
    (`001_S01_SH010_T03.mp4`), so Resolve cannot link the wrong take.
- Automation: Blackmagic's 21.1 release notes say Python scripting moved to the Studio version.
  You use Free, so the routine below is manual. It is short.

### The routine

First time for a film:

1. New project in Resolve named like the film folder (`001-title`), timeline 24 fps, resolution
   and aspect from `film.json`.
2. Drag `05-generation\takes`, `06-sound\sfx` and `07-music\takes` into the Media Pool.
   The bins mirror the folders: scene, then shot.
3. Edit.
4. End of session: Project Manager, right click the project, Export Project, save as
   `08-edit\001-title.drp` (overwrite the previous one, git keeps the history).
5. Commit and push.

On the other computer:

1. `git pull`. Keep the same Resolve version on both computers: a project from a newer Resolve
   does not open in an older one.
2. Project Manager, Import Project, pick `08-edit\001-title.drp`. If a project with that name is
   already in Resolve on this computer, rename the local one first (right click, Rename, add
   `_old-<date>`), then import. Never delete it: it may hold work that was not exported.
3. Edit, then export over the `.drp` again before you stop.

The rule that prevents lost work: export the `.drp` at the end of every session, import it at
the start of a session on the other computer.

### Exports

Final masters go to `08-edit\exports\_local\` (ignored). A compressed copy under 95 MB can be
committed if you want one in the repository; the public version goes to YouTube or Vimeo and its
link into `film.json`.
