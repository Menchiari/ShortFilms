# ShortFilms

Production server for AI short films: story, analysis, bible, shotlist, prompts, takes, sound,
music, edit and the public site at menchiari.net/filmai/. One folder per film.

## Start a film

```
python3 tools/filmtool.py new "Title of the film"
```

Creates `films/001-title-of-the-film/` from `templates/film/`. Drop the story in
`01-story/source/` (or paste it to Claude) and the pipeline starts. See `PIPELINE.md`.

## Map

```
PIPELINE.md              the process, stage by stage
CLAUDE.md                standing rules for Claude (credits, folders, no music, no deletions)
site.json                site settings (title, Discord link)
docs/
  STORAGE-AND-EDIT.md    git without LFS, sparse clone per film, DaVinci Resolve routine
  HIGGSFIELD.md          cost table, project and folder layout, approval protocol
  FRAMERATE.md           framerate problems and the fix tool
  WEBSITE.md             how the site is built and deployed
templates/film/          skeleton of a film folder
films/                   one folder per film
tools/
  filmtool.py            new film, render shotlist, status, checks
  media/fps.py           probe, fix and fit clips (framerate, size under 95 MB)
  media/preview.py       muted web preview and poster for the site
  site/build.py          static site generator
  get-film.sh            download one film only (partial clone + sparse checkout)
  install-hooks.sh       blocks commits of files over 95 MB
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

## First time on a new computer

Only the films you need (light):

```
git clone --filter=blob:none --sparse https://github.com/Menchiari/ShortFilms.git ~/ShortFilms
cd ~/ShortFilms
git sparse-checkout set tools templates docs
sh tools/get-film.sh 001
sh tools/install-hooks.sh
```

Everything: `git clone https://github.com/Menchiari/ShortFilms.git ~/ShortFilms`, then the hook.
Keep the same path on every computer and Resolve never loses media.

Requirements: git, Python 3.9+, ffmpeg (for the media tools).
