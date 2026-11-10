# Seedance 2.5 official prompt guide: digest

Source: ByteDance / BytePlus "Dreamina Seedance 2.5 prompt guide" (received 2026-11-10).
The facts our pipeline uses, with the guide's section names.

## Capacity
- One generation up to 30 s. Up to 50 references: 30 images (up to 4K), 10 videos (30 s total),
  10 audio clips (30 s total).
- Recommended: image subjects 1 to 8 (9 to 12 less stable); audio or video subjects 1 to 5;
  audio or video reference length 5 to 10 s; for more than 5 subjects use single-view images,
  one view per image, never several views in one image.
- Storyboards: 15 panels or fewer, line art or stick figures, no text on the panels.
- 3D clay-model reference: simple, coarse geometric primitives work better than detailed models.
- Editing works best on videos up to 20 s; with 1 to 5 reference images (6 to 8 less stable).

## Locked and unlocked tasks
- **Locked** (the input fixes the output): editing (aspect and duration follow the source; edit
  output can be about 0.33 s shorter unless the source has 8n+1 frames), first frame or first and
  last frame (aspect follows the first-frame image; give both frames the same aspect, otherwise
  the last one is stretched), extension (aspect follows the source).
- **Unlocked** (references are only semantic): reference tasks, storyboards, keyframes. Aspect and
  duration are free.
- First and last frame can also be given as normal reference images with "Image 1 is the first
  frame": then the aspect is not locked and the match is looser.
- Edit trigger words: edit video, add, insert, remove, delete, modify, replace, change to.
  Extension trigger words: extend forward, extend backward, continue, continue from.
- Extension and editing keep colour, brightness and audio continuity best with MOV in and out.

## Prompt structure ("Basic prompting techniques")
1. **Asset referencing:** every image, video and audio named by its upload number (Image 1,
   Video 1, Audio 1) and its job (subject, voice, action, scene, lighting...). If only part of an
   asset matters, say which part. Bind every asset in the text: do not rely on a name written
   inside the image. When the asset is accurate, just say to follow it instead of re-describing it.
2. **One-sentence summary:** subject + location + event + genre/style + camera movement.
3. **Detailed plot:** split by timestamps or by "Shot N". Each segment: visuals, camera
   movement, action, dialogue, sound effects.
4. **Additional notes:** what stays the same throughout (camera angle, environment, sound,
   atmosphere).
- Positive descriptions whenever possible. Negatives are supported for subtitles and audio
  ("No subtitles", "No BGM; generate only environmental sounds and action sounds", "No audio").

## Timestamps
- Whole seconds as the unit. Seedance 2.0 ignores timestamps; 2.5 follows them.
- No gaps ("0-3s ... 5-6s" is wrong). Too little in a segment and the model improvises; too much
  and it adds cuts or drops plot. Do not time rapid repeated actions.
- Also supported: time points ("at the 5-second mark") and relative time ("after 3 seconds").

## Camera and acting language
- Plain terms work directly: shot sizes, push in, pull out, pan, track, follow, orbit, dive, tilt,
  handheld, low angle, overhead, first person, long take, dolly zoom, FPV, speed ramp.
- Niche terms: write the term plus a description of what happens.
- Transitions: say when and how.
- Actions: general description first, specific detail only for a few memorable actions, never
  repeat the same action. Expressions: descriptive sentences, few idioms.

## Known failures and the official fixes (FAQ)
| Problem | Fix |
|---|---|
| Music appears despite "no BGM" | Put an audio policy at the start, list every music word (music, BGM, score, instrumental, melody, soundtrack, synth, ambient pad, drone, swelling tone, crescendo, musical build, stinger), repeat it per shot and at the end. Or strip non-vocal audio in post |
| Subtitles appear despite "no subtitles" | Do not repeat dialogue words elsewhere in the prompt, do not attach tone or action notes to specific words. Use `Name's line (emotion): {text}`. Reference videos must have no subtitles |
| Wrong character takes a reference or voice | Upload references in the order the subjects first appear, number them to match |
| Glowing eyes | Neutral emotion words ("amazed", not "fanatical"); "normal human eyes, no glowing eyes" as top constraint |
| Fingerprint-like textures on grass and foliage | Resize reference images so they do not exceed the output resolution |
| HTTP 400 on some JPGs | `ffmpeg -i in.jpg -pix_fmt yuvj420p out.jpg`, or use PNG |
| Misspelled on-screen text | Spell it letter by letter in sequence, or supply the text as an image |
| Bubbling, echo, whistling in audio | Remove words about water, waves, echoes |
| Style differs between 2.0 and 2.5 | Do not mix models in one film (or extend 2.0 clips with 2.5 in MOV) |
| Unstable result on a complex task | Split into simpler passes (reference first, then edit) |
| Aspect change by editing fills badly | Use reference mode with a detailed timeline |

## Dialogue and syntax seen in the official examples
- Dialogue in braces: `Gao Yan says: {line}` or `Granny Zhou's line (voice trembling): {line}`.
- Language and accent stated in words before the line.
- On-screen text in 【 】.
- Angle brackets mark asset and character names (`<Image 2>`, `<Lina>`).
- Non-speakers: "keep their mouths naturally closed".
