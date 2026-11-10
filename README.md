# ShortFilms

Production server for AI short films: story, analysis, bible, shotlist, prompts, takes, sound,
music, edit and the public site at menchiari.net/filmai/. One folder per film.

## Start a film

```
python tools/filmtool.py new "Title of the film"
```

(Windows: `python`. Mac and Linux: `python3`.)

Creates `films/001-title-of-the-film/` from `templates/film/`. Drop the story in
`01-story/source/` (or paste it to Claude) and the pipeline starts. See `PIPELINE.md`.

## Map

```
PIPELINE.md              the process, stage by stage
CLAUDE.md                standing rules for Claude (credits, folders, no music, no deletions)
site.json                site settings (title, Discord link)
docs/
  PROMPTING.md           how every Seedance prompt is built (one page)
  STORAGE-AND-EDIT.md    git without LFS, sparse clone per film, DaVinci Resolve routine
  HIGGSFIELD.md          cost table, project and folder layout, approval protocol
  FRAMERATE.md           framerate problems and the fix tool
  WEBSITE.md             how the site is built and deployed
  reference/             official Seedance 2.5 digest, Higgsfield originals
templates/film/          skeleton of a film folder
films/                   one folder per film
tools/
  filmtool.py            new film, status and sizes, render shotlist, takes, ratings, checks,
                         get (one film into a sparse clone), hooks (install the commit guard),
                         space (free space per drive, size of every film)
  media/fps.py           probe, fix and fit clips (framerate, size under 95 MB)
  media/preview.py       muted web preview and poster for the site
  site/build.py          static site generator
  get-film.sh            same as `filmtool.py get` (Git Bash, Mac, Linux)
  install-hooks.sh       same as `filmtool.py hooks` (Git Bash, Mac, Linux)
  hooks/pre-commit       refuses commits with a file over 95 MB
```

## Film folder

```
films/001-title/
  film.json              metadata, stages, publish flags, Higgsfield ids, costs, log
  shotlist.json          scenes, shots, approach, takes, love and ratings
  01-story/              source/ untouched, story.md clean transcription
  02-analysis/           analysis.md, questions.md
  03-bible/              world.md, characters/, locations/, props/, vehicles/
  04-shotlist/           SHOTLIST.md (rendered), BUDGET.md
  05-generation/         prompts/, frames/, takes/S01/SH010/, web/ (site previews)
  06-sound/              SFX.md (ElevenLabs list), sfx/
  07-music/              input/, analysis.md, prompts/, takes/
  08-edit/               EDIT.md, <film>.drp, exports/
  private/               never published
  _local/                never committed (big intermediates, masters)
```

## First time on a computer (Mac or PC)

Each computer keeps its own copy, on any of its own drives, with only the film in progress.
`python tools/filmtool.py space` shows which drive has room. Steps in
`docs/STORAGE-AND-EDIT.md` ("Each computer keeps its own copy").

Requirements: Git, Python 3.9+, ffmpeg.
