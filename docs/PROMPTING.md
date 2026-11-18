# Prompting

How every Seedance 2.5 prompt in this repo is built. Facts behind it:
`docs/reference/seedance-2-5-official-digest.md`.

Three principles:
- **Fixed skeleton, film-specific voice.** The skeleton below never changes. The voice (look,
  camera grammar, density, rhythm, sound, acting register) comes from the film's
  `03-bible/style.md`, so no two films read alike.
- **Cheapest method that gives the same or a similar result wins.**
- **Acting is the core.** Lines can overlap, characters can say things without words. The prompt
  makes room for that.

## Shot prompt

Plain English prose. Settings (duration, resolution, aspect, audio flag) never go in the prompt.

1. **Audio policy, first line:**
   `Audio: only [the dialogue / room tone / named sounds]. No music, BGM, score, instrumental,
   melody, soundtrack, synth, ambient pad, drone, swelling tone, crescendo, musical build or
   stinger at any moment. No subtitles.`
2. **Elements,** in the order they first appear on screen. Each element's image job id goes in
   `medias` as an image reference (no `<<<element_id>>>` placeholders: Seedance 2.5 ignores them).
   - Reference media are named by upload order: `@Image1`, `@Image2` ..., `@Video1` ...,
     `@Audio1` ... Never "Image 1" or "VIDEO 1".
   - Characters are always `@char_<name>`, in the element version that matches the scene in the
     script (film 001: `stories/politician/elements.md`). Props `@prop_<name>`, locations
     `@loc_<name>` when used.
   - One line per element: what it gives, and what not to take from it.
     `@char_marta (@Image1): face, hair and coat only, not pose or background.`
     `@loc_corridor (@Image2): space and light only, empty of people.`
   - In the body use only the `@char_` / `@prop_` / `@loc_` names. Name the character before
     each action. Say who holds each prop.
   - Template: `films/001-politician/05-generation/prompts/001_S05_SH120_T01_v5.txt`. Older
     prompts (for example `001_S03_SH010_T01.txt`) may use the old naming: never copy them.
3. **One sentence:** who, where, what happens, in the film's style, with which camera.
4. **Timeline in whole seconds, no gaps:**
   `0-3s: medium shot, eye level. Camera: dolly slowly in, stop on a medium close-up.
   @char_marta ...` Each segment starts where the last ended. One main change per segment. The
   last segment states the final frame: where people, objects and camera are.
5. **Dialogue,** language and accent once, then each line with its time and a playable verb:
   `2-4s, Marta's line (testing him): {I thought you weren't coming.}`
   `3-5s, Luca's line (cutting her off): {Don't.}`
   Overlapping times mean overlapping lines. Never repeat a line's words anywhere else in the
   prompt. Characters without a line in that moment: "keeps their mouth closed".
6. **Acting task** (when anyone speaks, listens, reacts, or holds something back): the director's
   ACTING TASK block (seedance-master skill): scene direction, motive, goal, obstacle, tactic,
   eye work as action. Silent beats get a tactic too: what they say without saying it. Refer to
   lines by order ("during her first line"), never by quoting them.
7. **Voice and continuity:** the look line from `style.md`, word for word in every shot, plus
   what must stay fixed. Positive wording. Counts only for things that could duplicate
   (`Count of lamps: one`).
8. **Audio policy again, last line.**

Camera: plain terms (shot sizes, push in, pull out, pan, tilt, track, orbit, handheld,
locked-off, dolly zoom). Every move has a pace, what stays steady and where it stops. A rare term
gets a short description of what happens on screen.

Words to avoid unless the scene needs them: water, waves, echo (audio artifacts); strong emotion
labels such as "fanatical" or "extremely shocked" (glowing eyes).

## Methods (cheapest first)

| Method | Higgsfield | Use when |
|---|---|---|
| Text + elements | mode `omni_reference` | Most shots |
| Start frame | `start_image` | Composition or light must be exact. Make the frame at the film's aspect: the video takes it |
| Start and end frame | `start_image` + `end_image` | The shot must land on an exact frame. Same aspect for both |
| Keyframes | references + "Use images 1 to N in order as keyframes" | Several exact compositions in one shot |
| Storyboard | one line-art image, up to 15 panels | Loose guide for a sequence |
| Blender previs | `video_references`, simple grey shapes | Camera path or blocking words cannot hold. Still describe everything |
| Edit | mode `video_edit` | Most of a take works: change only what fails (A to B, with times) |
| Extension | mode `video_extension` | Longer continuous takes. Extend our own Seedance 2.5 takes |

Complex requests become several simple passes. One video model per film.

## Saving credits

- Fix the cause before paying for a retake (see "After every take").
- Edit or extend a take that mostly works instead of generating a new one.
- Shots last as long as the edit needs, never padded. Minimum 4 s.
- Test at 480p only when a shot is risky and the test answers a structural question. Without a
  seed a test is never the keeper.
- Music runs: picture is discarded, so the lowest resolution that keeps the audio.

## Preparing references

- Images come from the director's own pipeline. Claude resizes them so they do not exceed the
  output resolution, saves them as standard JPEG (`ffmpeg -i in.jpg -pix_fmt yuvj420p out.jpg`)
  or PNG, and registers them as Elements (naming in `docs/HIGGSFIELD.md`).
- Reference videos: 5 to 10 s, no subtitles.
- Exact on-screen text: supplied as an image, or spelled letter by letter.

## After every take

Watch at normal speed with sound, then pick one:
1. **Fix the reference** when the error is already in the image.
2. **Fix the prompt** when the wrong person acts, a prop is misplaced or lines contradict.
3. **Another take** only when inputs are right and the defect does not repeat.

The next take changes one thing.
