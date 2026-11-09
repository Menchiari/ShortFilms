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

## One project per film

```
Higgsfield project: "SF 001 Title"
  REFS/            character, location, prop stills
  S01/
    SH010/         every take of shot 1 of scene 1
    SH020/
  S02/ ...
  MUSIC/
  TESTS/           calibration and structure tests
```

Folders are created when first needed. Project and folder ids are stored in
`films/<film>/film.json` under `higgsfield`, so generations always land in the right place.

## Approval protocol

Before any credit spend, Claude posts:

```
REQUEST 001 / S01 SH010 T03
Model: seedance_2_5, mode omni_reference, 8 s, 1080p, 21:9, audio on (no music)
Credits: 128 (preflight)   Balance after: ~3,505
Why this take: T02 rushed the turn, this one adds timed beats 0-3 / 3-6 / 6-8
```

Nothing is generated until you answer with an approval. An approval covers exactly that request.

## Download and naming

Each finished take is downloaded to `05-generation/takes/S01/SH010/` as
`001_S01_SH010_T03.mp4`, with the prompt in `05-generation/prompts/001_S01_SH010_T03.txt`.
Rejected takes are not downloaded into git; the job id in `shotlist.json` is enough to fetch them.
