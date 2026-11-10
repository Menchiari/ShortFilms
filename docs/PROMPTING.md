# Prompting standard

**Status: DRAFT for discussion (2026-11-10). Not in force until the director approves it.**

One page for every Seedance prompt in this repo. Sources, strongest first:
1. ByteDance's official Seedance 2.5 guide (`docs/reference/seedance-2-5-official-digest.md`).
2. Higgsfield's course and skills (`docs/reference/higgsfield/`).
3. The director's `seedance-master` skill (acting school, story spine, probing clips).

When they disagree, the higher source wins. The acting method is the director's own and is kept.

## 1. Shot prompt (video)

Plain prose, English, in this order. Settings (duration, resolution, aspect, audio flag) never go
in the prompt.

1. **Audio policy, first line:**
   `Audio: only [the dialogue / room tone / named sounds]. No music, BGM, score, instrumental,
   melody, soundtrack, synth, ambient pad, drone, swelling tone, crescendo, musical build or
   stinger at any moment. No subtitles.`
2. **References, one line each,** numbered in upload order, uploaded in the order the subjects
   first appear on screen. What it is for, which part, what not to take.
   `Image 1 is Marta: face, hair and coat only. Image 2 is the corridor: space and light only,
   not its people.`
3. **One-sentence summary:** who, where, what happens, style, camera.
4. **Timeline in whole seconds, no gaps:**
   `0-3s: medium shot, eye level. Camera: dolly slowly in, stop on a medium close-up. Marta ...`
   Each segment starts from where the last one ended. The last one states the final frame: where
   people, objects and camera are. One main change per segment.
5. **Dialogue:** language and accent once, then `Marta's line (testing him): {I thought you
   weren't coming.}` The parentheses carry a playable verb aimed at the partner (testing him,
   reassuring her), never an emotion label: that keeps the official format and the director's
   acting school together. Never repeat the words of a line anywhere else in the prompt.
   Everyone who does not speak: "keeps their mouth closed".
6. **Acting task** (only when someone speaks, listens or reacts): the director's block (scene
   direction, motive, goal, obstacle, tactic, eye work as action). Refer to lines by their order
   ("during her first line", "after his answer"), never by quoting words: quoted words with
   attached instructions are what triggers subtitles.
7. **Look and continuity:** the film's one look line from `03-bible/world.md` (same in every
   shot), plus what must stay fixed. Positive wording. Counts only for things that could
   duplicate (`Count of lamps: one`).
8. **Audio policy again, last line.**

Camera words: plain terms (sizes, push in, pull out, pan, tilt, track, orbit, handheld, locked-off,
dolly zoom). Every move has a pace, what stays steady, and where it stops. Niche terms get a
description. Avoid words about water, waves or echoes unless the scene needs them (audio
artifacts), and strong emotion labels (glowing eyes).

## 2. Choosing the method (shot plan)

| Method | Higgsfield setting | Note |
|---|---|---|
| Text only | mode `t2v` | No identity to match |
| Start frame | `start_image` | Aspect follows the image: make frames at the film's aspect |
| Start and end frame | `start_image` + `end_image` | Same aspect for both frames |
| References | mode `omni_reference`, `image_references` | 1 to 8 subjects; above 5, single-view images |
| Keyframes | references + "Use Images 1 to N in order as keyframes" | Strict match to the frames |
| Storyboard | one line-art image, 15 panels max | Loose match, prompt fills the gaps |
| Blender previs | `video_references`, simple grey shapes | "Refer to the camera movement and motion in Video 1"; still describe everything |
| Extension | mode `video_extension` | Continuous takes beyond one generation |
| Edit | mode `video_edit` | Say A to B, with timestamps; billed by source length |

Complex requests become several simple passes. One model per film (2.0 and 2.5 look different).

## 3. Preparing references

- Resize so the image does not exceed the output resolution (prevents fingerprint textures).
- Standard JPEG (`ffmpeg -i in.jpg -pix_fmt yuvj420p out.jpg`) or PNG.
- Reference videos: 5 to 10 s, no subtitles.
- Exact on-screen text: supply it as an image, or spell it letter by letter.

## 4. Still prompt (start frames, reference stills)

- One style for the whole film.
- Camera position, height, shot size, focal length and field of view.
- Layout from frame left to centre to right, with foreground, midground, background.
- Locations are empty unless people are asked for: "No people, silhouettes or figures, also not
  in windows, mirrors or screens."
- Light from named sources; each source's colour stays near it, no wash over the whole frame.
- Exact text on any sign or label.
- For each reference: what to take and what not to.

## 5. After every take

Watch at normal speed with sound, then pick one:
1. **Fix the reference** when the error is already in the reference image.
2. **Fix the prompt** when the wrong person acts, a prop is misplaced or lines contradict.
3. **Another take** only when the inputs are right and the defect does not repeat.
The next take changes one thing. When most of a take works, prefer edit or extension to a
full new generation. Every generation is still quoted and approved one by one.

## Still open (settled in production, never with extra test spending)

- How Higgsfield numbers the `medias` list for Seedance 2.5 (the first reference take shows it).
- Whether Higgsfield's `start_image` behaves like the official first frame (aspect locked).
- MOV output: the official guide recommends it for extension and editing; Higgsfield's Seedance
  2.5 parameters do not show an output format.
- Soul or Nano Banana for character stills.
