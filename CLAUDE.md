# Rules for Claude in this repository

This repo is the production server for the Menchiari AI short films. Every session that works here
follows these rules. They override habits and defaults.

## Hard rules (never break)

1. **Credits.** Never spend Higgsfield credits (or any paid generation) without explicit approval
   in chat for that exact request. Before asking, run a cost preflight (`get_cost: true`, free) and
   present: what will be generated, model, mode, duration, resolution, count, credits each, total,
   and balance after. An approval covers exactly that list. Anything else is a new request.
2. **Never delete the user's files.** Not in git, not in Higgsfield, not on disk. Replacing a file
   means a new version next to it (`_v2`, `T02`), never an overwrite or removal. If something truly
   must go, ask first and name the exact path.
3. **Higgsfield folder discipline.** Every generation goes into the film's own Higgsfield project,
   into the folder of its scene and shot (`S01/SH010`), reference stills into `REFS`, music into
   `MUSIC`. IDs live in `films/<film>/film.json` under `higgsfield`. Nothing bleeds into another
   project. If a folder does not exist yet, create it in the right project first.
4. **No music in shot generations, ever.** Every shot prompt carries "No background music." Sound
   in generations stays flat and diegetic: dialogue, room tone, contact sounds. The user does the
   sound design.
5. **No file over 95 MB in git.** GitHub rejects 100 MiB. The pre-commit hook in `tools/hooks`
   enforces it. Big masters and intermediates live in the film's `_local/` folder (gitignored).
6. **No Git LFS.** By the user's decision.
7. **Never use the em dash character** in any file or message. Use a hyphen, a colon or a period.

## How to work

- Follow `PIPELINE.md` stage by stage. Each stage writes its output into the film folder.
- When something is unclear: write the question into `02-analysis/questions.md`, send it to the
  user, then **keep going** on the best-reasoned assumption, marked `[ASSUMPTION]` in the docs so it
  can be challenged. Never block the pipeline waiting for an answer unless credits are involved.
- Separate what is known from what is inferred. If you do not know, write "I don't know".
- Prompts for Seedance follow the `seedance-master` skill (formula, timed beats, reference roles,
  ACTING TASK block, constraint tail). Load it before writing any generation prompt.
- After every generation: download the file, name it `<filmid>_<S##>_<SH###>_<T##>.mp4`, record the
  take in `shotlist.json` (job id, settings, credits, prompt file), and commit. Rejected takes stay
  in Higgsfield and are only referenced by job id; loved takes are committed to git.
- Ratings: the user's word wins. If the user only reacts, infer the rating and mark
  `"rating_source": "inferred"`: "love it" = 5 + love, "good/works" = 4, "usable" = 3,
  "meh" = 2, "no/bad" = 1.
- Keep `film.json` stages and log current. The website reads them.
- Before committing, run `python3 tools/filmtool.py check` (schema and size sanity).
- Commit messages: short, factual, film id first, for example `001: S01 SH010 T03 loved`.

## Defaults (until the user changes them)

- Video model: `seedance_2_5` on Higgsfield. 24 fps output.
- Shot generation: one shot per generation. Multi-shot generations only for rapid sequences of very
  short shots.
- `generate_audio: true` (costs the same, gives a guide track and lip sync), always with
  "No background music. No subtitles."
- Resolution: decided per shot in the shot plan. Cost per second (checked 2026-11-09):
  480p = 3, 720p = 7, 1080p = 16 credits. Audio and bitrate mode do not change the price.

## Where things are

- `PIPELINE.md`: the process, stage by stage.
- `docs/`: storage and editing, Higgsfield, framerate, website, music.
- `templates/film/`: skeleton copied by `python3 tools/filmtool.py new "Title"`.
- `films/<id>-<slug>/`: one folder per film.
- `tools/`: film tool, media tools, site builder, git hooks.
