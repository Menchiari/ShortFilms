# The Pipeline

From a document to a finished short film. Each stage has an owner, an output inside the film
folder, and a gate. Claude never waits on a question unless credits are involved: questions go to
the user, work continues on marked assumptions.

The aim of every film: art that stays with people and opens their mind. Not a dopamine clip.
Every decision below gets checked against that.

```
0 INTAKE > 1 ANALYSIS > 2 BIBLE > 3 SHOTLIST > 4 SHOT PLAN > 5 SOUND LIST
> 6 REFERENCES > 7 GENERATION > 8 FRAMERATE > 9 EDIT > 10 SOUND DESIGN > 11 MUSIC > 12 RELEASE
```

Stages 1 to 5 run back to back in one pass by Claude, with questions sent along the way.
Stages 6, 7 and 11 spend credits: every single generation is quoted and waits for your explicit
approval. Credit spending is never automated.

---

## 0. Intake

**You:** drop the document in chat or in `films/<film>/01-story/source/` (txt, md, pdf, docx,
Fountain, Final Draft, anything). Start a film with:

```
python tools/filmtool.py new "Title"
```

**Claude:** keeps the source untouched, writes `01-story/story.md` as a clean transcription that
preserves every blank line and indentation, because spacing is direction:

- One blank line = a cut, unless the text says continuous take.
- More space = more time between beats.
- Screenplay format: one page is about one minute. Prose: estimated per beat in the analysis.

## 1. Analysis

**Output:** `02-analysis/analysis.md`, `02-analysis/questions.md`

Claude reads the whole piece, then answers its own questions in writing:

- **Story spine:** goal, obstacle, tactic, reversal, value shift (before verdict, after verdict).
  A reversal with no value shift is flagged.
- **Scene by scene:** the shared unspoken scene direction, each character's motive, goal, obstacle,
  tactic (the ACTING TASK seeds from the seedance-master skill). Characters never play the theme.
- **Rhythm map:** estimated runtime per beat from page count and spacing, where time stretches,
  where it snaps. Total runtime estimate.
- **Tone and form:** what the film should feel like, the visual and sonic grammar, what it must
  never become. References only as language, never as imitation.
- **Motivation of every element:** why this shot, this object, this silence exists.
- **Questions:** anything that changes the film if guessed wrong goes to you. Everything else is
  decided and marked `[ASSUMPTION]`.

## 2. Bible (consistency documents)

**Output:** `03-bible/`

- `world.md`: year, place, season, weather, social context, technology of the period, money,
  brands policy (generic, no logos), palette, light, texture and wear level, lens philosophy.
- `characters/<slug>.md`: locked identity (face, body, hair, voice), background (origin, home, job,
  class, income, education, habits), what they drive, what they carry, wardrobe per scene with
  condition (new, worn, stained, pressed), acting notes, continuity locks, reference-still prompt.
- `locations/<slug>.md`: geography, architecture, era, time of day, light sources, set dressing,
  dirt and wear, sound of the place, continuity locks, reference prompt.
- `props/<slug>.md`, `vehicles/<slug>.md`: material, era, condition, how it is held or used,
  who owns it, continuity locks, reference prompt.

Everything must be believable for the time, place and class of the story. Claude decides by
reasoning from the text (a night-shift nurse in 1994 Turin does not drive a new car), and asks
only when the text leaves a real fork.

## 3. Shotlist

**Output:** `shotlist.json` (source of truth), rendered to `04-shotlist/SHOTLIST.md`

Per shot: id, what happens, purpose (why the shot exists), framing, angle, lens feel, camera
movement, duration, transition in (cut, continuous, match), characters, props, dialogue, sound.
Ids: scenes `S01`, shots `SH010` `SH020` (gaps leave room for inserts like `SH015`), takes `T01`.

Questions on angles or pacing go to you, Claude keeps going.

## 4. Shot plan (approach per shot)

**Output:** the `approach` block of each shot in `shotlist.json`, budget in `04-shotlist/BUDGET.md`

For each shot Claude picks the cheapest method that will hold:

| Method | When |
|---|---|
| Text to video | Simple shot, no identity that must match other shots |
| Start frame (image to video) | Composition, light or identity must be exact. Lock the look as a still first, it is far cheaper than re-rolling video |
| Start + end frame | The shot must land on an exact final composition (match cuts, reveals) |
| Omni reference (character, location, prop stills) | Recurring characters and places across many shots |
| Video reference | A camera path or motion rhythm that words cannot hold (from a phone video, a previs, another clip) |
| Blender previs | Complex geometry, spatial continuity across angles, precise camera moves. Render a grey previs, use it as video reference or clay control |
| Extension | Continuous takes longer than one generation, or a shot that must flow out of the previous one |
| Multi-shot in one generation | Only rapid sequences of very short shots |

Plus: resolution, duration, risk (low, medium, high), expected takes, estimated credits.
Total budget goes to you before any spend.

## 5. Sound list

**Output:** `06-sound/SFX.md`

Generation audio is a flat guide track: dialogue, room tone, contact sounds, never music. Claude
writes the full list of sound effects you need from ElevenLabs, per scene and shot: ambience beds,
foley, hard effects, designed sounds, each with a ready-to-paste ElevenLabs prompt, duration and
number of variations. You produce them, files go in `06-sound/sfx/`.

## 6. References (credits)

Character, location and prop stills generated from the bible prompts, into Higgsfield `REFS`
and `03-bible/*/refs/`. Each batch is quoted and approved before generating.

## 7. Generation (credits, one shot at a time)

For each shot, in order:

1. Claude writes the prompt (seedance-master format) into
   `05-generation/prompts/<film>_<S>_<SH>_<T>.txt` with the settings line.
2. Claude runs the free cost preflight and asks: shot, settings, credits, balance after.
3. You approve. Claude generates into the Higgsfield folder `S01/SH010` of this film.
4. Claude downloads, names the file, records the take and commits it.
5. You react. Claude records love and rating (inferred from your words when you do not give one)
   and makes a muted web preview and a poster for loved takes.
6. Next take changes one axis only, or we move to the next shot.

Every take goes into git, loved or not, so scraps stay reusable.

## 8. Framerate fix

AI clips can carry duplicate frames, stutter, or a frame rate that does not match the timeline.
`tools/media/fps.py probe` reports it, `fix` conforms to constant 24 fps, `fit` re-encodes under
95 MB. Details in `docs/FRAMERATE.md`. Your existing tools get merged in here.

## 9. Edit

DaVinci Resolve. The project travels as a `.drp` file in `08-edit/`, media links point into the
film folder. Details in `docs/STORAGE-AND-EDIT.md`.

## 10. Sound design

Yours. SFX from the list in stage 5, guide audio from the takes for timing and lip sync.

## 11. Music

1. You play a melody, hum it, or send a MIDI file into `07-music/input/`.
2. Claude analyzes it: key, tempo, meter, intervals, contour, phrase lengths (MIDI is exact, audio
   is analyzed by pitch tracking).
3. Together: genre, mood, instrumentation, and where it sits against the story. Subtle and serving
   the film, never decorating it.
4. Claude writes a Seedance prompt: a static locked-off shot of the musicians playing the piece,
   instruments named, tempo and key stated, your recording attached as `@audio1` reference
   (Seedance 2.5 accepts audio references). Max 30 s per generation.
5. Longer cues: extend forward (sequel) or backward (prequel) from the best take.
6. The audio is extracted, the picture discarded.

Cost note: the picture is thrown away, so music runs can be tested at 480p (3 credits per second,
90 for 30 s) if the audio quality holds at that resolution. I don't know yet whether it does: the
first music run will compare one 480p and one 720p take before we commit to a rule.

## 12. Release

Final export, the film page on the site switches to released, a Discord post with the link.

---

## Status values

- Film `status`: `development`, `pre-production`, `generation`, `post`, `released`
- Stage status in `film.json`: `todo`, `in-progress`, `done`
- Shot `status`: `planned`, `ready`, `generating`, `review`, `approved`, `cut`

## Progress shown on the site

- Shots approved (a loved take exists) out of shots planned, cut shots excluded.
- Takes per shot, credits spent (takes plus extra costs), stage checklist.
