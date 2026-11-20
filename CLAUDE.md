# Rules for Claude in this repository

This repo is the production server for the Menchiari AI short films. Every session that works here
follows these rules. They override habits and defaults.

## Hard rules (never break)

1. **Credits.** Never spend Higgsfield credits (or any paid generation) without explicit approval
   in chat for that exact request. Before asking, run a cost preflight (`get_cost: true`, free) and
   present: what will be generated, model, mode, duration, resolution, count, credits each, total,
   and balance after. An approval covers exactly that list. Anything else is a new request.
   Credit spending is never automated: no standing budgets, no "up to N takes", no retries, no
   scheduled or batch spending. The user decides every spend, every time.
2. **Never delete the user's files.** Not in git, not in Higgsfield, not on disk. Replacing a file
   means a new version next to it (`_v2`, `T02`), never an overwrite or removal. If something truly
   must go, ask first and name the exact path. Exception: story drafts in `stories/` are versioned
   by git: edited in place, committed and pushed after every change.
3. **Higgsfield folder discipline.** Every generation goes into the film's own Higgsfield project,
   into the folder of its scene and shot (`S01/SH010`), reference stills into `REFS`, music into
   `MUSIC`. IDs live in `films/<film>/film.json` under `higgsfield`. Nothing bleeds into another
   project. If a folder does not exist yet, create it in the right project first.
4. **Never music in shot generations.** Every shot prompt starts and ends with the audio policy
   in `docs/PROMPTING.md`. Sound in generations stays flat and diegetic: dialogue, room tone,
   contact sounds. The user does the sound design. Music is generated only in the music stage
   (PIPELINE.md stage 11), only when the user asks for it.
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
- Prompts follow `docs/PROMPTING.md` and the film's `03-bible/style.md`. For the ACTING TASK
  block, load the `seedance-master` skill (the director's acting method).
- The cheapest method that gives the same or a similar result is always the right choice.
- References are Higgsfield Elements (`docs/HIGGSFIELD.md`). Images come from the user's own
  pipeline (the user picks the image model, Midjourney for style); Claude does not pick image
  models.
- When Leonard changes a rule, the doc that teaches it changes on main in the same session. Film-sync
  never merges `docs/`, `tools/` or `CLAUDE.md`: a branch with those is not done until main has it.
- Docs state rules only: no comparisons of sources, no debates. Keep every document as short as
  it can be.
- After every generation: download the file, name it `<filmid>_<S##>_<SH###>_<T##>.mp4`, record the
  take in `shotlist.json` (job id, settings, credits, prompt file), and commit. **Every take goes
  into git, loved or not** (user decision 2026-11-10: scraps can be reused). Watch the repository
  size with `filmtool.py status` and tell the user before it nears GitHub's 5 GB guidance.
- Ratings: the user's word wins. If the user only reacts, infer the rating and mark
  `"rating_source": "inferred"`: "love it" = 5 + love, "good/works" = 4, "usable" = 3,
  "meh" = 2, "no/bad" = 1.
- Keep `film.json` stages and log current. The website reads them. The site plays every take
  with its prompt and notes (user decision 2026-11-17) and a still of every take (made
  automatically by film-sync), the finished film is linked (YouTube or Vimeo).
- Before committing, run `python3 tools/filmtool.py check` (schema and size sanity).
- Commit messages: short, factual, film id first, for example `001: S01 SH010 T03 loved`.

## Story development

- For any film idea, story development, outline, treatment or screenplay, use the `writers-room`
  skill. Review every stage with the `braintrust` subagent.
- Stories live in `stories/<slug>/`, one file per stage, versions in git. The site never reads
  `stories/`.
- A pushed branch that changes only `stories/`, `films/` and `films-index.json` is merged into
  main automatically by `.github/workflows/film-sync.yml` (`tools/mergebranches.sh`: film JSON
  merged by structure, append-only logs keep both sides), and the site redeploys: no pull request
  needed. Keep story and production work on their own branch, without tool or doc changes. The
  run log names any branch it could not merge (a real conflict, or `filmtool check`): tell the
  user and fix it.
- A story becomes a film only when the user says so: `python3 tools/filmtool.py new "Title"`, then
  the locked screenplay is copied (never moved) into the film's `01-story/source/` and PIPELINE.md
  stage 0 starts.
- Developing an existing film: story work goes in `stories/<film-slug>/`; the film folder is read,
  and edited only on explicit instruction. One automatic exception: a film with `story_sync` in
  `film.json` takes its shots, logged takes, per-shot animatic clips and character elements from
  the story (`tools/storysync.py`, run by `.github/workflows/film-sync.yml` after every push).
  When a character element is registered, save its image as
  `films/<film>/03-bible/characters/refs/<element name>.<ext>` (GitHub cannot reach Higgsfield).
- Pipeline export: the story bible's "Pipeline export" table maps story outputs to the film's
  files: `01-story/story.md`, `02-analysis/analysis.md`, `03-bible/world.md`, `03-bible/style.md`
  and `style-refs/`, `03-bible/characters|locations|props|vehicles/<slug>.md` (elements; Higgsfield
  ids there and in `film.json` under `higgsfield`), `shotlist.json`, `docs/PROMPTING.md`.

## Defaults (until the user changes them)

- Video model: `seedance_2_5` on Higgsfield. 24 fps output.
- Shot generation: one shot per generation. Multi-shot generations only for rapid sequences of very
  short shots.
- `generate_audio: true` (costs the same, gives a guide track and lip sync), always with the
  no-music line from rule 4.
- Resolution and aspect ratio: decided per film with the user, usually 480p or 720p. 1080p only
  when the user asks. Cost per second (checked 2026-11-09): 480p = 3, 720p = 7, 1080p = 16
  credits. Audio and bitrate mode do not change the price.
- The user works on a PC (Windows) and a Mac, DaVinci Resolve Free. Each computer has its own
  light clone on whichever of its own drives has room, with only the film in progress; paths
  differ per computer (Resolve Mapped Mount or relink). PC clone: `D:\ShortFilms`. Mac: not set up yet. User-facing commands: `python` on
  Windows (PowerShell), `python3` on Mac.
- `films-index.json` (film sizes for `filmtool space`) is refreshed by `filmtool check`: commit it.

## Where things are

- `PIPELINE.md`: the process, stage by stage.
- `docs/PROMPTING.md`: how every prompt is built. `docs/`: storage and editing, Higgsfield,
  framerate, website. `docs/reference/`: source material.
- `templates/film/`: skeleton copied by `python3 tools/filmtool.py new "Title"`.
- `films/<id>-<slug>/`: one folder per film.
- `stories/<slug>/`: story development, one folder per idea.
- `.claude/skills/writers-room/`: writers' room skill and research. `.claude/agents/braintrust.md`:
  story reviewer.
- `tools/`: film tool, media tools, site builder, git hooks.
