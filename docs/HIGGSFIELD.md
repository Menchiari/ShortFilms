# Higgsfield

## Cost table (Seedance 2.5, checked with free preflights on 2026-11-09)

| Resolution | Credits per second | 5 s | 10 s | 15 s | 30 s |
|---|---|---|---|---|---|
| 480p | 3 | 15 | 30 | 45 | 90 |
| 720p | 7 | 35 | 70 | 105 | 210 |
| 1080p | 16 | 80 | 160 | 240 | 480 |

- `generate_audio` on or off: same price. `bitrate_mode` standard or high: same price.
- Aspect ratio did not change the price in the checks (16:9 and 21:9).
- Prices change. Claude re-runs the preflight before every approval request, the table is a guide.

## Model facts used by the pipeline

- Seedance 2.5 modes: `t2v`, `omni_reference` (image, video, audio references), `video_edit`,
  `video_extension` (forward or backward).
- Media roles: `start_image`, `end_image`, `image_references`, `video_references`,
  `audio_references`.
- Duration 4 to 30 s, whole seconds. Aspect: auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16.
- No seed parameter is exposed, so a take cannot be reproduced exactly. A loved 720p take cannot
  be "re-rendered" at 1080p: a new generation is a new performance. Choose the final resolution
  before generating the take you hope to keep.

## Drafts and finalizing

- A 480p seedance_2_5 take is sent with `draft: true` only when the job allows it. Same price
  as a plain 480p render.
- Only a draft job can be finalized: a new job with `draft_job_id`, within seven days of the
  draft. The final renders the draft's full duration at the final resolution's price.
- A take sent without the flag can never be finalized.
- A `video_edit` at a higher resolution is not a substitute for finalizing: it keeps the
  performance but adds no detail (001 S04 SH070 T03: SSIM 0.972 against a bicubic upscale of
  the 480p take, edge energy slightly lower, 31 credits).
- Not allowed: image inputs with no video reference (001: 3 of 3 failed, refunded). Those takes
  go out without the flag, and the approval request says they cannot be finalized.

## Elements (characters, locations, props)

References are Higgsfield Elements, named like the existing ones:
`char_<name>`, `loc_<name>`, `prop_<name>` (lowercase, hyphens, 32 characters max).
With seedance_2_5 an element is passed by its image job id in `medias` (`image_references`);
the prompt names it `@char_<name> (@Image1)`, in `medias` order (rules in `docs/PROMPTING.md`).
Each element's id goes in its bible document
(`03-bible/characters/<name>.md` and so on). The images come from the director's own pipeline.

## One project per film

```
Higgsfield project: "SF 001 Title"
  Scenes/
    S01/
      SH010/       every take of shot 1 of scene 1
      SH020/
    S02/ ...
  REFS/            uploaded stills: references, start and end frames
  Elements/        element images
  Documents/
  TESTS/           structure tests
  MUSIC/           only when the film has music
```

Folders are created when first needed. Project and folder ids are stored in
`films/<film>/film.json` under `higgsfield.folders` (keys `Scenes`, `S01`, `S01/SH010`, `REFS`),
so generations always land in the right place.

- A new scene folder is created with `parent_folder_id` = `higgsfield.folders.Scenes`, a new shot
  folder with its scene folder's id. Nothing scene-related goes at the project root.
- Before creating any folder, list the parent's children (every page) and reuse the folder with
  the same name. Never create a second folder with the same name.

## Approval protocol

Before any credit spend, Claude posts:

```
REQUEST 001 / S01 SH010 T03
Model: seedance_2_5, mode omni_reference, 8 s, 720p, 21:9, audio on (never music)
Credits: 56 (preflight)   Balance after: ~3,577
This take changes: T02 rushed the turn, this one adds timed beats 0-3 / 3-6 / 6-8
```

Nothing is generated until you answer with an approval. An approval covers exactly that request.
Credit spending is never automated: no budgets, no automatic retries, no batches you did not
approve one by one.

## Download and naming

Every finished take, loved or not, is downloaded to `05-generation/takes/S01/SH010/` as
`001_S01_SH010_T03.mp4` and committed, with the prompt in
`05-generation/prompts/001_S01_SH010_T03.txt`. The job id in `shotlist.json` links back to
Higgsfield.
