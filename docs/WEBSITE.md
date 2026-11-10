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
  one small poster still per loved take, never video. Every file stays far below Cloudflare's 25 MiB
  per-file limit, and the free plan allows 20,000 files per deployment.
- `private/` folders are never read. Each film controls the rest with its `publish` flags in
  `film.json`:

| Flag | Default | Publishes |
|---|---|---|
| `story` | true | `01-story/story.md` |
| `analysis` | true | `02-analysis/analysis.md` and `questions.md` (open questions, answers) |
| `bible` | true | `03-bible/**/*.md` and reference stills |
| `shotlist` | true | the shotlist with status per shot |
| `prompts` | true | prompts of loved takes |
| `costs` | true | credits spent and `04-shotlist/BUDGET.md` |
| `sound` | true | `06-sound/SFX.md` |
| `music` | true | `07-music/analysis.md` |
| `edit` | true | `08-edit/EDIT.md` (cut notes) |

A document appears only once its stage has started in `film.json`, so empty templates never
show up. The site is your tracking board as much as the community's window: anything you want
kept off it goes in the film's `private/` folder or gets its flag set to `false`.

Preview locally:

```
python tools/site/build.py
python -m http.server -d dist 8000      (then open http://localhost:8000)
```

## Pages

- **Index**: every public film as a reel card: poster, title, logline, status stamp, progress
  strip (approved shots out of planned), takes, credits, Discord link.
- **Film**: tabs for Overview (stages, numbers, log), Story, Analysis, Questions, Bible,
  Shotlist (click a shot to see the loved take, its prompt and its references, plus every take
  with rating and cost), Budget, Sound, Music, Edit. Tabs appear as their stage starts.

## Deploy setup (one time, needs your Cloudflare and GitHub logins)

1. Cloudflare dashboard: create an API token with the permission "Cloudflare Pages: Edit". Copy
   your Account ID from the dashboard sidebar.
2. GitHub, repository Settings > Secrets and variables > Actions: add `CLOUDFLARE_API_TOKEN` and
   `CLOUDFLARE_ACCOUNT_ID`.
3. Push to `main` (any change under `films/`). The Action `.github/workflows/site.yml` builds and deploys to a Pages project
   called `filmai` (created on the first run), reachable at `filmai-6sp.pages.dev`.
4. Put it under `menchiari.net/filmai/` (menchiari.net is on Cloudflare): a small Worker on the
   route `menchiari.net/filmai*` forwards requests to `filmai-6sp.pages.dev`. The code is in
   `tools/site/worker-proxy.js`. Known facts: the most specific route pattern wins, and a Worker
   cannot fetch its own zone, which is why it fetches the `pages.dev` address. Not known: how
   Cloudflare orders a Worker route against a Pages custom domain on the same hostname (its docs
   are not consistent), so we test it on your account. Fallback if it misbehaves: the subdomain
   `filmai.menchiari.net` as a Pages custom domain, two clicks.

Until the two secrets exist, the Action builds and skips the deploy, so nothing fails.

## Discord

Set the invite link once in `site.json` at the repository root. It appears on every page.
