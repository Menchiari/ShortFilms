# Website: menchiari.net/filmai/

The public face of this repository. The repository stays private; the site publishes only what
each film allows.

## How it works

```
private repo (films/*)  ->  GitHub Action builds dist/ (small)  ->  Cloudflare serves dist/
```

- `python tools/site/build.py` reads every `films/*/film.json` and `shotlist.json`, copies only
  public material into `dist/`, and writes `dist/data/*.json`. No dependencies beyond Python 3.
- All links are relative, so the same build works at `/filmai/`, at the root of a subdomain, or
  opened from disk.
- Cloudflare never clones the repository. The Action uploads only `dist/`: documents, JSON,
  a still of every take, and every take video (copied from `05-generation/takes/`, no extra
  copy in git). A take over Cloudflare's 25 MiB per-file limit is left out of the site. The free
  plan allows 20,000 files per deployment; uploads send only files that changed.
- `tools/site/functions/films/[[path]].js` (a Pages Function) answers byte-range requests for the
  videos: Pages static files do not, and Safari (Mac, iPhone) plays video only with them.
- `private/` folders are never read. Each film controls the rest with its `publish` flags in
  `film.json`:

| Flag | Default | Publishes |
|---|---|---|
| `story` | true | `01-story/story.md` |
| `analysis` | true | `02-analysis/analysis.md` and `questions.md` (open questions, answers) |
| `bible` | true | `03-bible/**/*.md` and reference stills |
| `shotlist` | true | the shotlist with status per shot, notes of every take |
| `takes` | true | the video of every take, played in the Shotlist tab |
| `prompts` | true | the prompt of every take, shown beside its video |
| `costs` | true | credits spent and `04-shotlist/BUDGET.md` |
| `sound` | true | `06-sound/SFX.md` |
| `music` | true | `07-music/analysis.md` |
| `edit` | true | `08-edit/EDIT.md` (cut notes) |

A document appears only once its stage has started in `film.json` and differs from its template,
so empty templates never show up. The site is your tracking board as much as the community's window: anything you want
kept off it goes in the film's `private/` folder or gets its flag set to `false`.

Preview locally:

```
python tools/site/build.py
python -m http.server -d dist 8000      (then open http://localhost:8000)
```

## Pages

- **Index**: every public film as a reel card: poster, title, logline, status stamp, progress
  strip (one cell per shot, colored by its best rating), takes, credits, Discord link.
- **Film, Production tab** (the default): the production board.
  - Approved share, shots left, runtime approved, days to the deadline, credits spent.
  - One bar: approved (a loved take), in review (takes, no select), not shot.
  - Plan check: shots the schedule wanted approved by today against the real count, and the pace
    (shots a day) needed to approve every shot by `shots_due` (the last day before the edit;
    without it, the last day that has scenes).
  - Schedule: one row per day from `film.json` `schedule`, its scenes with approved/total, a flag
    when a past day is behind. "Today" is the viewer's local date.
  - Shots by scene: one tile per shot. Fill = best rating (red 1 to 2, gray 3, blue 4 to 5, the
    number printed), dashed = not shot, ring and heart = approved. A tile opens the shot.
  - Quality: rating spread, strong shots with no select yet, weak shots, takes waiting for a
    rating. Then stages and the production log.
- **Shotlist tab**: every shot with its takes, rating and cost. The shot's animatic clip, when
  there is one, is the first row. Each shot shows and opens on its face take: the approved one,
  else the best rated (3 or more, newest on a tie), else the newest; without takes, the animatic.
  The prompt and notes sit beside the video; clicking a row switches to it.
- **Characters tab**: one card per character element (`03-bible/characters/`), whole sheet
  image, use, Higgsfield ids.
- Other tabs: Story, Analysis, Questions, Bible, Budget, Sound, Music, Edit. Tabs appear as their
  stage starts.

Shot state on the site: a loved take (or status `approved`) = approved; takes without a select =
in review; no takes = its status (`planned`, `ready`); `cut` shots are left out of every count.

### Schedule (in `film.json`)

```json
"schedule": {
  "source": "production plan v4",
  "deadline": "2026-11-25",
  "shots_due": "2026-11-22",
  "days": [ { "date": "2026-11-17", "scenes": ["S02", "S03"], "task": "Crossroads start frames." } ]
}
```

### Live updates

1. Every push to a working branch starts `.github/workflows/film-sync.yml` (through
   `stories-sync.yml`; also on pushes to main touching `stories/`). It runs main's copy, so old
   branches cannot block it. `tools/mergebranches.sh` merges every branch pushed in the last 48
   hours that is ahead of main and changes only `stories/`, `films/` and `films-index.json`:
   `film.json` and `shotlist.json` by structure (`tools/jsonmerge.py`: shots and takes by id,
   both sides' log entries kept), `MISTAKES.md` and `takes/log.md` keeping both sides,
   `films-index.json` regenerated. A real conflict or a failed `filmtool check` leaves that branch
   out and is named in the run log.
2. Then it runs `tools/storysync.py`: a film with `story_sync` in `film.json` gets its shots from the screenplay,
   the takes logged in the story's `takes/log.md`, the animatic clip of each shot and its
   character elements (details in the script). It commits the
   result to main and starts the site deploy whenever the live build is behind main. It always
   runs main's copy, so a session on an old branch still reaches the site. Push to live: about
   2 minutes.
3. An open page checks `data/site.json` every minute and redraws when a new build is there (never
   while a video plays: it waits until it stops). The board shows when the data was built and from
   which commit.

## Deploy setup (one time, needs your Cloudflare and GitHub logins)

1. Cloudflare dashboard: create an API token with the permission "Cloudflare Pages: Edit". Copy
   your Account ID from the dashboard sidebar.
2. GitHub, repository Settings > Secrets and variables > Actions: add `CLOUDFLARE_API_TOKEN` and
   `CLOUDFLARE_ACCOUNT_ID`.
3. Push to `main` (any change under `films/`), or a content-only branch (Live updates above). The
   Action `.github/workflows/site.yml` builds and deploys to the Pages project `filmai`, reachable
   at `filmai-6sp.pages.dev`.
4. Put it under `menchiari.net/filmai/` (menchiari.net is on Cloudflare): a small Worker on the
   route `menchiari.net/filmai*` forwards requests to `filmai-6sp.pages.dev`. The code is in
   `tools/site/worker-proxy.js`. Known facts: the most specific route pattern wins, and a Worker
   cannot fetch its own zone, which is why it fetches the `pages.dev` address.
   Checked 2026-11-17: `www.menchiari.net/filmai/` serves the site; `menchiari.net/filmai/` (no
   www) returns 404. Fix: the same Worker on a second route `menchiari.net/filmai*` (Cloudflare
   dashboard, Workers Routes).

Until the two secrets exist, the Action builds and skips the deploy, so nothing fails.

## Discord

Set the invite link once in `site.json` at the repository root. It appears on every page.
