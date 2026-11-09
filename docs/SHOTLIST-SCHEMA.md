# shotlist.json

Source of truth for scenes, shots and takes. `04-shotlist/SHOTLIST.md` is rendered from it with
`python3 tools/filmtool.py render <film>`. Do not edit the rendered file.

```json
{
  "film": "001-example",
  "scenes": [
    {
      "id": "S01",
      "title": "Night shift",
      "location": "hospital-corridor",
      "time": "night",
      "summary": "She finishes the round and finds the bed empty.",
      "shots": [
        {
          "id": "SH010",
          "status": "planned",
          "description": "Wide of the corridor, she walks toward camera pushing the cart.",
          "purpose": "Establish the routine before it breaks.",
          "framing": "WS",
          "angle": "eye level",
          "lens": "35mm",
          "movement": "static",
          "duration_s": 6,
          "transition_in": "cut",
          "characters": ["marta"],
          "props": ["med-cart"],
          "dialogue": "",
          "sound": "fluorescent hum, cart wheel squeak",
          "approach": {
            "method": "start-frame",
            "why": "Corridor geometry and her identity must match S01 SH030.",
            "references": ["03-bible/characters/refs/marta_01.jpg"],
            "resolution": "1080p",
            "aspect": "21:9",
            "risk": "medium",
            "expected_takes": 3,
            "estimated_credits": 288
          },
          "takes": [
            {
              "id": "T01",
              "date": "2026-11-10",
              "model": "seedance_2_5",
              "mode": "omni_reference",
              "duration_s": 6,
              "resolution": "1080p",
              "aspect": "21:9",
              "audio": true,
              "credits": 96,
              "job_id": "",
              "prompt": "05-generation/prompts/001_S01_SH010_T01.txt",
              "file": "05-generation/takes/S01/SH010/001_S01_SH010_T01.mp4",
              "preview": "05-generation/web/001_S01_SH010_T01.mp4",
              "poster": "05-generation/web/001_S01_SH010_T01.jpg",
              "references": [],
              "love": false,
              "rating": null,
              "rating_source": null,
              "notes": ""
            }
          ]
        }
      ]
    }
  ]
}
```

## Fields

- Shot `status`: `planned`, `ready`, `generating`, `review`, `approved`, `cut`.
- `framing`: ECU, CU, MCU, MS, MWS, WS, EWS, OTS, POV, INSERT.
- `transition_in`: `cut`, `continuous`, `match`, `dissolve`, `smash`.
- `approach.method`: `t2v`, `start-frame`, `start-end-frame`, `omni-reference`, `video-reference`,
  `blender-previs`, `extension`, `multi-shot`.
- `approach.risk`: `low`, `medium`, `high`.
- Take `rating`: 1 to 5. `rating_source`: `user` or `inferred`. `love`: true marks the select.
- `file` is empty for rejected takes that were never downloaded. `job_id` always points to
  Higgsfield.
