# Website: menchiari.net/filmai/

The public face of this repository. The repository stays private; the site publishes only what
each film allows.

## How it works

```
private repo (films/*)  ->  GitHub Action builds dist/ (small)  ->  Cloudflare serves dist/
```

- `python3 tools/site/build.py` reads every `films/*/film.json` and `shotlist.json`, copies only
  public material into `dist/`, and writes `dist/data/*.json`. No dependencies beyond Python 3.
- All links are relative, so the same build works at `/filmai/`, at the root of a subdomain, or
  opened from disk.
- Cloudflare never clones the repository. The Action uploads only `dist/`: documents, JSON,
  posters and short muted previews of loved takes. Every file stays far below Cloudflare's 25 MiB
  per-file limit, and the free plan allows 20,000 files per deployment.
- `private/` folders are never read. Each film controls the rest with its `publish` flags in
  `film.json`:

| Flag | Default | Publishes |
|---|---|---|
| `story` | true | `01-story/story.md` |
| `analysis` | false | `02-analysis/analysis.md` |
| `bible` | true | `03-bible/**/*.md` and reference stills |
| `shotlist` | true | the shotlist with status per shot |
| `prompts` | true | prompts of loved takes |
| `costs` | true | credits spent |
| `sound` | true | `06-sound/SFX.md` |
| `music` | true | `07-music/*.md` |

Preview locally:

```
python3 tools/site/build.py && python3 -m http.server -d dist 8000
```

## Pages

- **Index**: every public film as a reel card: poster, title, logline, status stamp, progress
  strip (approved shots out of planned), takes, credits, Discord link.
- **Film**: tabs for Overview (stages, numbers, log), Story, Bible, Shotlist (click a shot to see
  the loved take, its prompt and its references), Sound, Music.

## Deploy setup (one time, needs your Cloudflare and GitHub logins)

1. Cloudflare dashboard: create an API token with the permission "Cloudflare Pages: Edit". Copy
   your Account ID from the dashboard sidebar.
2. GitHub, repository Settings > Secrets and variables > Actions: add `CLOUDFLARE_API_TOKEN` and
   `CLOUDFLARE_ACCOUNT_ID`.
3. Merge to `main`. The Action `.github/workflows/site.yml` builds and deploys to a Pages project
   called `filmai` (created on the first run), reachable at `filmai.pages.dev`.
4. Put it under `menchiari.net/filmai/`. How depends on how menchiari.net is hosted today:
   - menchiari.net on Cloudflare (Pages, Workers, or any host with DNS proxied by Cloudflare): a
     small Worker on the route `menchiari.net/filmai*` forwards requests to `filmai.pages.dev`.
     The Worker is in `tools/site/worker-proxy.js`.
   - menchiari.net not on Cloudflare: use a subdomain (`filmai.menchiari.net`) as a Pages custom
     domain, or move DNS to Cloudflare first.

Until the two secrets exist, the Action builds and skips the deploy, so nothing fails.

## Discord

Set the invite link once in `site.json` at the repository root. It appears on every page.
