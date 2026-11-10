# Prompting Handbook: AI film generation

Portable and self-contained. Give this whole file to any film project, short or feature. Written
2026-11-10 for Seedance 2.5 on Higgsfield; section 21 covers other models. The film's own style
sheet supplies the voice; this file supplies the method.

Status of the rules:
- Unmarked: from ByteDance's official Seedance 2.5 prompt guide, Higgsfield's documentation,
  model spec and price checks, the director's acting method and Seedance prompting skill, or
  standard film craft (screen direction, continuity, coverage).
- `[UNTESTED]`: reasoned from documented behavior, not yet proven on a take. Test it once on one
  shot before building a sequence on it.

---

## 1. Ground rules

1. One video model for the whole film. Model versions render differently and the cut shows it.
2. Prompts are plain English prose. Settings (mode, duration, resolution, aspect, audio flag)
   never go inside the prompt: they go in a settings line next to it.
3. Default: one shot per generation. Multi-shot generations only for rapid sequences of very
   short shots.
4. The cheapest method that gives the same or a similar result wins.
5. Acting is the core. Everyone on screen has a task, speaking or not.
6. Fixed skeleton, film-specific voice. The skeleton (section 6) never changes. Look, camera
   grammar, density, rhythm, sound and acting register come from the film's style sheet, so no two
   films read alike.
7. Each take changes one thing from the last, or the result cannot be read.
8. No music in shot generations. Score is a separate job (section 17).
9. No credit spend without a cost preflight and an explicit approval of that exact request.

## 2. Model facts (Seedance 2.5 on Higgsfield, November 2026)

- Duration 4 to 30 s, whole seconds, default 5, one continuous single-pass generation.
- Frame rate is not a setting. Expected 24 fps: probe the first take to confirm (appendix).
- Modes: `t2v`, `omni_reference` (image, video and audio references), `video_edit` (billed by
  the source video's duration; duration and aspect settings are ignored), `video_extension`
  (direction `forward` or `backward`; aspect setting ignored, the output follows the source).
- Settings: resolution 480p, 720p or 1080p; `generate_audio` on or off; `bitrate_mode` standard
  or high.
- Media roles: `start_image`, `end_image`, `image_references`, `video_references`,
  `audio_references`.
- Aspect: auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16.
- References: the model takes up to 50 (30 images, 10 videos, 10 audio; about 30 s total per
  video and audio), per ByteDance. Higgsfield does not publish its own per-request limit: I don't
  know it. Recommended: 8 or fewer image subjects, 5 or fewer video or audio subjects, clips 5 to
  10 s. More than 5 subjects: single-view images only.
- Native audio with lip sync: dialogue, ambience, effects. 11+ languages.
- No seed parameter. A take cannot be reproduced, and a loved 720p take cannot be re-rendered at
  1080p: a new generation is a new performance. Choose the delivery resolution before generating
  the takes you hope to keep.
- Locked tasks (the input fixes the output): edit (aspect and duration follow the source; output
  can be about 0.33 s shorter unless the source has 8n+1 frames), first frame or first and last
  frame (aspect follows the first frame; give both frames the same aspect or the last one is
  stretched), extension (aspect follows the source).
- Unlocked tasks (references are semantic only): reference, storyboard, keyframes. Aspect and
  duration are free.
- Editing works best on sources up to 20 s with 1 to 5 reference images.
- Edit and extension keep colour, brightness and audio continuity best with MOV in and out
  (ByteDance guide). Whether Higgsfield accepts and returns MOV: I don't know.
- Seedance 2.0 ignores timestamps; 2.5 follows them.
- Price (Higgsfield preflight, 2026-11-09): 480p 3, 720p 7, 1080p 16 credits per second. Audio on
  or off and bitrate mode do not change it. Prices change: run the free preflight every time.

## 3. Feature-length arithmetic

A 90-minute film is 5,400 screen seconds. At an average shot length of 4 s that is about 1,350
shots; at 8 s, about 675.

Generated seconds always exceed screen seconds: the 4 s minimum, trims, retakes. Call the ratio G
(generated seconds per screen second). Credits = 5,400 x G x price per second.

| G | 480p | 720p | 1080p |
|---|---|---|---|
| 1 | 16,200 | 37,800 | 86,400 |
| 3 | 48,600 | 113,400 | 259,200 |
| 5 | 81,000 | 189,000 | 432,000 |

G is the lever. In order of effect: fix the cause before a retake (section 18), edit or extend a
take that mostly works, let one take carry several beats, generate shots at their real length
(never padded), lock the look with a still before spending on motion.

## 4. Before the first prompt: the bible

Prompts copy from these files. They never re-invent.

- **Style sheet:** look line (word for word in every prompt), camera grammar, rhythm, prompt
  density (sparse, medium or dense, per scene if it changes), sound grammar, acting register,
  what the film never does.
- **World:** year, place, season, class, technology of the period, money, brands policy (generic
  objects, no logos), the sound of the world.
- **Characters:** locked identity (face, build, hair, hands, voice and accent), wardrobe per scene
  with condition (new, worn, stained, pressed), acting notes, continuity locks, element id.
- **Locations:** layout with screen-left and screen-right for each camera setup, light sources and
  their direction, time of day per scene, wear and dirt, sound of the place, element id.
- **Props and vehicles:** material, era, condition, owner, how it is held or used.
- **Continuity ledger** (one row per scene): day and time, weather, light direction, each
  character's wardrobe and physical state (wet, bandaged, stained), what each one holds, where the
  props are. A state that starts in a scene (a cut on the hand) stays in every later row until the
  story ends it. Every prompt's continuity line is copied from its row.
- **Snippet library:** the exact wording that repeats across hundreds of prompts: audio policy,
  look line, each element line per costume, each location's light sentence. Paste, never retype:
  changed words change the picture.

## 5. References (Elements)

- Use every element exactly as it is named in the film's element sheet. Higgsfield proposes a
  name automatically (like `char_example`) and the name can be changed; the sheet is the record.
- New elements only: `char_<name>`, `loc_<name>`, `prop_<name>`, lowercase, hyphens. Higgsfield
  caps names at 32 characters and turns spaces into hyphens. Higgsfield categories: character,
  environment, prop.
- In the Higgsfield prompt the element is `@element_name`. Through the API (or any tool call),
  only `<<<element_id>>>` works; Higgsfield injects the image and rewrites it to `@element_name`.
  A name that matches no element (a template placeholder such as `@character_1`) attaches
  nothing.
- Higgsfield's element documentation (November 2026) lists Seedance 2.0 among element-capable
  video models and does not list 2.5. Confirm elements work in 2.5 with one test before a
  sequence depends on them.
- One line per reference: what it provides and what must not transfer. Narrow wins:
  `@char_marta is Marta: face and hair only.` `@loc_corridor: space and light only, empty of people.`
- Bind every asset in the text; a name written inside the image does nothing. When the asset is
  accurate, say to follow it instead of describing it again.
- Mention references (and upload plain ones) in the order the subjects first appear on screen.
  A wrong order can give the wrong person the face or the voice.
- Image = look. Video = motion, camera path, timing. Audio = voice, ambience or a melody. An image
  and a video never do the same job.
- Several angles of one object: separate images, never a grid, then: `@image1, @image2 and
  @image3 show one single lamp. There is only ever one lamp.`
- Fewer is stronger. Over budget, cut style first, then setting, then props. Characters last.
- Resize images so they do not exceed the output resolution (oversized references cause
  fingerprint-like texture on grass and foliage). Save as standard JPEG
  (`ffmpeg -i in.jpg -pix_fmt yuvj420p out.jpg`) or PNG; some JPEGs return HTTP 400.
- Reference videos: 5 to 10 s, no subtitles.
- Exact on-screen text: supplied as an image, or spelled letter by letter.
- The image beats the words. Wording cannot be relied on to erase an unwanted detail that is in
  a reference (a coat, a scar, a wall). Fix the image.

Feature scale:
- **Costumes:** one reference per costume, same face (`char_marta-uniform`, `char_marta-coat`).
  One element wearing the coat can carry the coat into scenes where it does not belong.
- **Age, injury, haircut:** a new reference each, same rules.
- **Locations:** one reference per camera direction you will shoot (toward the door, toward the
  window). Whatever no reference shows, the model invents, and invents differently every take.
  Reverse angles need their own image.
- **Voices** `[UNTESTED]`: one clean 5 to 10 s voice sample per character, no music, attached to
  every shot where that character speaks: `@audio1 provides Marta's voice.` Same file every time.
  The guide track can also be replaced in post with a consistent voice.

## 6. The shot prompt skeleton

In this order, every time. Delete nothing but the parts the shot does not have (no dialogue, no
acting task in an empty landscape).

```
Audio: only [the dialogue / room tone / named sounds]. No music, BGM, score, instrumental,
melody, soundtrack, synth, ambient pad, drone, swelling tone, crescendo, musical build or
stinger at any moment. No subtitles.

@char_a is A: [what to take]. @loc_x: [what to take], empty of other people. @prop_y: [what it
is], held by A.

[One sentence: who, where, what happens, in the film's style, with which camera.]

0-3s: [shot size, angle]. Camera: [move, pace, what stays steady, where it stops]. [A does ...]
3-6s: [the next change, starting from the state 0-3s left behind]
6-8s: [the last change]. Final frame: [where people, objects and camera are].

Language: [language and accent].
[t-t]s, A's line ([playable verb]): {line}
[t-t]s, B's line ([playable verb]): {line}
Whoever is not speaking keeps their mouth closed.

ACTING TASK blocks (section 10).

Look: [look line from the style sheet, verbatim]. Light: [key direction]. Continuity: [from the
ledger]. Count of [anything that could duplicate]: [n].

Audio: [the same policy line again].
```

Settings line, separate from the prompt:
`Settings: mode omni_reference, aspect 21:9, duration 8 s, resolution 720p, audio on.`
`References: @char_a, @loc_x, @prop_y (Elements, in this order).`

Timeline rules:
- Whole seconds, no gaps (`0-3s ... 5-6s` is wrong). The last end time equals the duration.
- One main change per segment, plus a visible end state.
- Each segment inherits the physical state of the one before. The helmet stays in the left hand:
  say it.
- Too little in a segment and the model improvises; too much and it adds cuts or drops events.
- Do not time rapid repeated actions (hammering, running steps). Describe them once.
- The last segment states the final frame. Without it the model stops on its most dramatic frame
  or invents an action to fill the tail.
- Timestamps allocate pacing; they are not frame-accurate edit points.
- Also understood: time points ("at the 5-second mark") and relative time ("after 3 seconds").
- A long duration adds time, not events. A 20 s shot with one small movement becomes waiting or
  repetition: route the whole shot (entrance, middle, exit, settle).

## 7. Writing the action

- Order: subject, action, setting, style, camera, sound. Summarize first, then detail only the
  moments that matter.
- Clear nouns and physical verbs beat stacked adjectives.
- Describe each action once. Said twice in different words, it can happen twice.
- Name the person before every action. Every prop has an owner and a hand.
- Positive wording. Negatives only for audio, subtitles, and counts of things that could
  duplicate (`Count of lamps: one`).
- **Cause before reaction.** Contact, resulting movement, sound, then reaction, as separate
  actions. "She looks surprised" invites the reaction before its cause.
- **Contacts, not results.** Not "he jumps the fence": the hands on the top rail, the weight
  shifting forward, the left foot finding the crossbar, the landing on both feet, the knees
  absorbing it.
- **Occlusion.** An object behind a pillar still exists. Say how long it is hidden and relist the
  few details that must return (identity, clothing, direction, speed).
- **Cloth, hair, smoke, liquids:** direction of force, where the motion stops, what settles where.
  "Realistic physics" says none of that.
- Words that cause artifacts, unless the scene needs them: water, waves, echo (bubbling, whistling
  in the audio); strong emotion labels such as "fanatical" or "extremely shocked" (glowing eyes).
  Use plain words: "surprised", not "shocked to the core".
- Rare terms (a camera move, a period object): the term plus a short description of what happens
  on screen.

## 8. Camera

Size, angle and movement are three separate choices. Size is not lens: "close-up" is a frame
boundary; focal length and distance are separate decisions.

| Size | Clause | Use |
|---|---|---|
| Extreme wide | Extreme wide shot; keep the subject small within the surrounding environment. | Geography, isolation |
| Wide | Wide shot; full figure with open space around them. | Entrances, relationships across a space |
| Full | Full-body shot; keep the head and feet inside the frame. | Stance, walk, a full action |
| Medium long | Medium long shot; frame the person from head to knees. | Standing dialogue, hands and legs |
| Cowboy | Cowboy shot; head to mid-thigh, hands visible. | A reach, a standoff |
| Medium | Medium shot; waist-up, camera at eye level. | Dialogue with hands |
| Medium close-up | Medium close-up; head and shoulders, chest at the lower edge. | Dialogue, intimate reactions |
| Close-up | Close-up of the face; blurred background. | The reaction that carries the scene |
| Extreme close-up | Extreme close-up of the key detail; exclude the surrounding context. | A clue, a finger on a button |

Angles: eye level (`lens at the subject's eye height`), high (`camera above the subject, looking
down`), low (`low camera position, looking upward`), overhead (`directly overhead; camera looking
straight down`), Dutch (`a clearly diagonal horizon`).

| Move | Clause |
|---|---|
| Static | Locked-off camera; keep the composition fixed while the action unfolds. |
| Pan | Pan right at an even pace from a fixed position; keep the horizon level and settle on the new view. |
| Tilt | Tilt smoothly upward from a fixed position; keep the camera at the same height and stop on the upper subject. |
| Pedestal or boom | Raise the camera vertically at an even pace; keep the lens level and finish on a higher view. |
| Dolly | Dolly slowly forward to a closer view; keep focal length and camera height fixed, subject near centre. |
| Truck | Truck sideways past the foreground at an even pace to reveal the subject. |
| Track | Track parallel to the moving subject at a matching pace; keep a steady distance and consistent framing. |
| Arc | Arc from a side view to a frontal view at a steady distance; the subject stays still. |
| Zoom | Increase focal length smoothly from a fixed camera position; finish on a tighter frame. |
| Dolly zoom | Move the camera backwards while zooming in; keep the subject the same size in frame. |
| Handheld | Restrained handheld drift; keep the subject clearly framed. |
| Roll | Slow clockwise camera roll from a level frame. |
| Whip pan | Whip pan right with brief motion blur; settle on a sharp, readable final frame. |

Rules:
- Every move has a pace, what stays steady, and where it stops.
- Tie each move to a visible event or a time: "as she sits, the camera begins to push in".
- Give the subject a screen position (left third, centre) and say whether it holds.
- Interactions: keep hands and objects inside the frame. Move closer only when the reaction is
  the information. A close-up hits harder after a wider view showed what is being reacted to.
- Three depth layers (foreground, subject, background) give the frame depth.
- When testing, change one camera choice at a time.

Screen grammar across a scene (the model has no memory between generations, so each prompt
restates it):
- Each character's screen side and gaze direction in every shot of the scene: "Ines screen-left,
  looking screen-right". The model keeps nothing between generations, so the 180-degree line
  holds only if every prompt restates it.
- Travel keeps one screen direction across a journey unless a shot shows the turn.
- Key light direction per location setup in every prompt: "key from screen-right, the window".

## 9. Dialogue and sound

- Language and accent once, in words, before the lines: `Language: English, both with a light
  Neapolitan accent.` Naming the language is the fix for lines delivered in the wrong one.
- Each line with its time and a playable verb (what the speaker does to the other), never an
  emotion: `2-4s, Marta's line (testing him): {I thought you weren't coming.}`
- Overlapping times mean overlapping lines. Silence is allowed; so are lines cut off mid-word.
- Never repeat a line's wording anywhere else in the prompt, and never attach tone notes to single
  words inside it. The official guide names both as causes of unwanted subtitles. Refer to lines
  by order ("during her first line").
- Non-speakers: "keeps their mouth closed" for the moments they do not speak.
- Syntax: `{ }` speech, `【 】` on-screen text that is meant to be there. Parentheses only for the
  delivery verb after the speaker's name. Sound effects in plain words ("the metal taps on the
  steel"): the official examples use angle brackets `< >` for asset and character names, so they
  are not used for sound.
- The audio policy goes first and last in every prompt, listing every music word (section 6).
  If music still appears, strip non-vocal audio in post.
- Generated audio is a guide track: dialogue, room tone, contact sounds. It is not
  frame-accurate and gives no stems. Real sound design happens in post.
- To sync a camera move to a line, anchor it twice: `On the line "<exact words>", the camera
  begins a slow push-in` and `At about 4 seconds, the camera ...`. Leave 2 to 3 s of tail after it.

## 10. Acting: the ACTING TASK

Use it whenever anyone speaks, listens, reacts or holds something back. These definitions are the
director's own method and override textbook versions.

**An acting task is the character being invested in their tactic for reaching the goal.** It is
not external behavior ("eyes flick", "brows lift"): that plays the result and produces dead faces.
The tactic can live entirely in the eyes: someone arguing from conviction checks both of the
partner's eyes, hunting for a spark of trust, registering whether the partner is with them or
drifting, adjusting to what they find. The eye movement is the doing. Dead eyes are never fixed
with catchlights. They are fixed with a task.

Build it in this order:

0. **Read the whole dialogue first.** The task lives across the exchange: where it holds, where
   it breaks. Never build from one line.
1. **Scene direction:** one shared, unspoken direction all characters play toward, a silent
   agreement about how this time will be lived (a mother packing her son's army suitcase: make it
   painless, hide the feeling, stay positive). Read it backward from how the scene ends. It
   includes every character, silent ones too. It is never the film's theme: characters never play
   the film's purposes.
2. **Physical action as the channel:** the surface activity (packing, cooking, routine rounds)
   stays; each character pursues the direction through it.
3. **Motive:** same direction, different fuel per character (the son keeps it painless for his
   mother; the mother, out of superstition: no tears before a journey). Given circumstances
   constrain it: a man who took a compromised job cannot play moral innocence.
4. **Goal:** what this person fights for in the scene. Ordinary, personal, playable, never the
   same words as the scene direction.
5. **Obstacle:** what presses against the line. One crack and the shared direction collapses. The
   audience feels it because nobody plays it.
6. **Tactic:** the moment-to-moment pursuit, written as what they do to the partner, with the eye
   work named as purposeful action.

Block format inside the prompt:

```
ACTING TASK, [NAME] (fully invested in the tactic; the work happens in the eyes):
SCENE DIRECTION (shared, unspoken): [one line]
MOTIVE: [what makes this person push that direction]
GOAL: [their personal fight]
OBSTACLE: [what presses against the line, what one crack costs]
TACTIC: [what they do to the partner, with eye work as action]
Moment to moment:
- during [their first line / the partner's line / the silence]: [verb at the partner + what the eyes check]
- [where the line breaks, if it breaks]
(Safety: gaze always engaged in the task, never a frozen glassy unfocused stare; natural blink cadence.)
```

Rules:
- Verbs aimed at the partner. No emotion adverbs as instruction ("sadly", "nervously"). No facial
  choreography beyond the safety line, which exists only because the model needs it.
- Silent listeners get a real task ("decide if he is serious", "protect the mood").
- Nobody plays the emotion. Everyone plays the direction.
- **Contrast pairing** for duos: each carries one plus and one minus, mirrored against the
  partner; one axis is the one the audience reads. The surface trait is usually scar tissue over
  its opposite: "careless" means hope lost, not care absent. Direct the history, not the surface.

## 11. Story check before a narrative shot

Name these, or the shot reads flat however good the render:
- **Goal:** what the hero fights for. It never changes; tactics can be wrong, the goal cannot.
- **Obstacle:** a circumstance that puts the goal at risk, and at what scale.
- **Tactic:** the move the threat forces. Its failure returns information that shapes the next
  move.
- **Reversal:** a turn against expectation, at least one per sequence.
- **Value shift:** the before-verdict and after-verdict the audience holds on the character. A
  reversal with no value shift is inert.

Also: every shot has a purpose (the reason it exists). If the purpose is "coverage", it is a candidate
for the cut before it costs credits.

## 12. Methods, cheapest first

| Method | Higgsfield | Use when |
|---|---|---|
| Text + elements | `omni_reference` | Most shots |
| Start frame | `start_image` | Composition or light must be exact. Made at the film's aspect |
| Start and end frame | `start_image` + `end_image` | The shot must land on an exact frame. Same aspect for both |
| Keyframes | references + "Use images 1 to N in order as keyframes" | Several exact compositions in one shot |
| Storyboard | one line-art image, 15 panels or fewer, no text on the panels | Loose guide for a sequence |
| Previs | `video_references`: simple grey primitives (Blender) | Camera path or blocking words cannot hold. Still describe everything in the prompt |
| Edit | `video_edit` | Most of a take works: change only what fails |
| Extension | `video_extension` | Longer continuous takes, or the moment before or after a take |

Complex requests become several simple passes (reference first, then edit). Rapid sequences of
very short shots may share one generation: `Shot 1, 0-2s: ... Hard cut. Shot 2, 2-4s: ...`.

## 13. Coverage and continuity between generations

1. Each generation is a new performance. Separate generations of the same scene differ in timing,
   gesture and line reading.
2. So stage scenes for few generations. Let one take carry the performance: a master, a moving
   shot, a oner up to 30 s, longer by extension.
3. Cut on the listener. A reaction shot needs no lip sync, so the speaker's audio from the master
   plays over it. No lip sync to match makes it the cheapest coverage.
4. A matching single of the speaker `[UNTESTED]`: attach the master's dialogue audio as `@audio1`
   ("@audio1 provides the exact dialogue, voices and timing; lips match it").
5. Cut on action: the receiving shot starts with the action already underway at 0 s, in the exact
   state the previous shot ended in. Copy the previous final frame into the next prompt's first
   segment.
6. Continuing from the same angle: extension, or the last frame as start image (`ffmpeg -sseof
   -0.1 -i in.mp4 -frames:v 1 -q:v 2 last.jpg`), then: `Use @image1 as the exact first frame and
   continue forward from that moment. Preserve composition, lens, light, props and framing. Do not
   replay <what happened before this frame>.`
7. Never retell the previous clip. Say only what has finished, what stays fixed, and the first new
   action.
8. A shot that plays 2 s in the edit is generated at 4 s and trimmed, or grouped with neighbours
   in a rapid multi-shot generation.

## 14. Start frames and stills

A still is cheaper than a video take and locks composition and light before motion credits are
spent. The image model is the director's choice; the grammar below works across models.

- Make it at the film's aspect: the video takes the first frame's aspect.
- Generation order: subject, style, light, composition, lens. Editing: the delta only, what
  changes and what stays identical.
- Lens: camera position, height, viewing direction, shot size, full-frame-equivalent focal length.
  Default to clean rectilinear rendering unless the style sheet says otherwise.
- Location references are empty: "No people, silhouettes, faces, human figures, mannequins or
  reflections of people; no figures through windows, doors, mirrors or screens." Life shows
  through objects and wear.
- Map the frame left to right, each zone foreground to background, matching the location sheet.
- Colour, unless the style sheet chooses a stylized palette: a neutral photographic foundation
  where each material keeps its own colour (concrete grey, steel neutral, off-white stays
  off-white); warm and cool light stays near its source; contrast comes from light direction,
  depth and falloff, not a full-frame tint.
- Text only on natural carriers (signs, plates, screens), with the exact words.
- Refine by editing the chosen image. Never restart when 80% is right.
- Every sentence either changes the image or prevents a likely failure. Cut the rest.

## 15. Edit and extend

- Choose the mode explicitly: `video_edit`, or `video_extension` with its direction. The source
  clip must be 4 to 30 s.
- Trigger words. Edit: edit video, add, insert, remove, delete, modify, replace, change to.
  Extend: extend forward, extend backward, continue, continue from.
- Edit prompt: verb first, time window, current state, target state, then the lock:
  `Edit 6 to 9 s. Davide's right hand goes from flat on the counter to resting beside the keys.
  Keep both faces, the lines, the lighting, the camera and everything else exactly the same.`
- Heavier edits: state the lock before the change.
- Extend: the direction, the new action, and "lighting, mood, characters and camera rhythm carry
  over".
- A missed take: rewrite only the physical state where the bad action begins and where it should
  end.

## 16. Transforming footage you shot

- Probe it first (appendix). Build the prompt from what the footage shows.
- Lock, then change: `@video1 is the original take: <who, wardrobe, setting, action>. Preserve
  identity, face, wardrobe, performance, framing, lens and camera motion exactly; change only
  <the element>.` End with: `Face and identity unchanged; everything else identical to the
  source.`
- An added element gets its behavior over time (where it starts, how it spreads, what light it
  throws), its interaction with the plate (light on faces, contact shadows, refraction) and an
  explicit scale ("enormous, dwarfing the tower").
- Lighting fork, chosen first: keep the subject's light and grade the new element to it (lowest
  identity risk), or relight the whole frame with identity explicitly locked (higher risk).
- Integration is more than colour: same key direction and softness, environmental bounce, a touch
  of the scene's haze over the subject, matched lens character, depth of field and grain, no halos
  or cut-out edges.
- Designs (creatures, vehicles, armor): "generic, not based on any brand or character".
  Photoreal creatures: "fully photoreal, true anatomy, never CG", plus a real photo declared as
  texture reference only.
- Prepending an intro shortens the window for the source: total runtime minus intro length =
  seconds left for the source performance. Do the subtraction before promising lip sync.

## 17. Music

- Never in shot generations. Every shot prompt carries the audio policy.
- Music is its own generation, only when the director asks: a static locked-off shot of musicians
  playing the piece, instruments named, tempo and key stated, the director's melody (hummed,
  played or MIDI-rendered) attached as `@audio1`. Up to 30 s; longer cues by extension forward or
  backward. The picture is discarded, so the lowest resolution that keeps the audio.

## 18. Review and repair

Watch at normal speed with sound, then pick one:
1. **Fix the reference** when the error is already in the image.
2. **Fix the prompt** when the wrong person acts, a prop is misplaced or lines contradict.
3. **Another take** only when the inputs are right and the defect does not repeat.

| Symptom | Fix |
|---|---|
| Music appears | Audio policy first and last with every music word; or strip non-vocal audio in post |
| Subtitles appear | `Name's line (verb): {text}`; line words never repeated; "No subtitles"; references without subtitles |
| Wrong person gets a face or voice | References in order of first appearance; name the person before each action |
| Glowing eyes | Neutral emotion words; "normal human eyes, no glowing eyes" first among constraints |
| Dead, glassy eyes | ACTING TASK with eye work as action, plus the safety line |
| Bubbling, echo, whistling audio | Remove water, waves, echo words |
| Rushed, repeated, slow motion | Timed segments, one change each, a settling tail |
| Extra cuts, dropped events | Fewer events per segment, more seconds |
| Reaction before its cause | Contact, movement, sound, reaction as separate actions |
| Object teleports after occlusion | How long it is hidden; relist what returns unchanged |
| Duplicated objects | "One single ..., there is only ever one"; `Count of X: one` |
| Reference background bleeds in | "space and light only" or "do not use its background"; crop the image |
| Camera wanders | Screen position; each move tied to an event or a time, with a stop |
| Identity drifts in a long take | 8 or fewer image subjects, 5 to 10 s clips, single-view; cut style first |
| Wrong language or accent | Language and accent named before the lines |
| Edit came back as a new clip | Mode `video_edit`; verb-first edit with a time window, then the lock |
| Fingerprint texture on foliage | Resize references to the output resolution |
| Misspelled text | Spell it letter by letter, or supply it as an image |
| Looks pasted in (plates) | Key direction, bounce, haze, grain, depth of field, edges |
| Style differs between clips | One model per film |
| Re-roll came back worse | Return to the last good prompt; change one axis |

Repair request to any LLM:

```
Revise the tested prompt below. What went wrong: [the errors, in plain words]. What I want
instead: [the intended result]. Keep the parts that already work. Update every affected line so
the instructions agree. Return the full revised prompt, then list exactly what you changed and the reason for each change.
Tested prompt: [paste it].
```

## 19. Preflight checklist

1. Duration equals the last timecode. Start and end frames share the video's aspect.
2. Resolution is the delivery resolution if this take could be a keeper.
3. Audio policy first and last.
4. Every element named exactly as in the element sheet (`<<<element_id>>>` through the API), in
   order of first appearance, each with a role and what not to take.
5. Every action has a named person; every prop has an owner.
6. Timeline: whole seconds, no gaps, one change per segment, each inheriting the last state, the
   last one stating the final frame.
7. Every camera move: pace, what stays steady, where it stops. Screen sides and gaze stated.
8. Dialogue: language once, each line timed with a verb, wording never repeated, non-speakers
   with mouths closed.
9. An ACTING TASK for everyone who speaks, listens or reacts.
10. Look line verbatim; continuity from the ledger; counts only for what could duplicate.
11. No water, waves, echo or extreme emotion words unless the scene needs them.
12. One written sentence: what this take changes from the last.
13. Cost preflight run; approval given for exactly this request.

## 20. Worked examples

Fictional scene, for form only.

**A. Dialogue shot (omni_reference)**

```
Label: S12 SH040 T01

Audio: only the two voices, the low fan of the ovens and the small contact sounds of hands and
metal. No music, BGM, score, instrumental, melody, soundtrack, synth, ambient pad, drone, swelling
tone, crescendo, musical build or stinger at any moment. No subtitles.

@char_ines is Ines: face, hair and grey wool coat. @char_davide is Davide: face, hair and white
work shirt. @loc_bakery: space and light only, empty of other people. @prop_keys: one ring of
three brass keys, held by Ines.

Before dawn in a small bakery, Ines returns the shop keys to her brother Davide across the steel
counter, in one locked-off medium two-shot at counter height.

0-3s: medium two-shot, eye level, locked-off camera. Ines stands screen-left at the near end of
the counter, facing screen-right, the keys in her right hand at her side. Davide stands
screen-right behind the counter, flour on his forearms, facing her.
3-6s: Ines sets the keys on the counter between them. The metal taps on the steel. Her hand stays
on the keys.
6-9s: Davide looks down at the keys, then back at Ines. His hands stay flat on the counter.
9-10s: final frame: Ines's hand on the keys, Davide's hands flat on the counter, the two of them
looking at each other, the camera unmoved.

Language: English, both with a light Neapolitan accent.
1-3s, Ines's line (closing the matter): {I won't need these anymore.}
7-9s, Davide's line (leaving the door open): {Take them with you. In case.}
Whoever is not speaking keeps their mouth closed.

ACTING TASK, INES (fully invested in the tactic; the work happens in the eyes):
SCENE DIRECTION (shared, unspoken): a normal morning; nobody turns this into a goodbye.
MOTIVE: if it becomes a scene, he will talk her out of leaving.
GOAL: walk out with the keys left behind.
OBSTACLE: one long look at him and she stays.
TACTIC: keeps it practical; checks his eyes once to see if he will make it hard, then gives her
attention to the counter.
Moment to moment:
- during her line: closes the matter, eyes check that he heard the finality.
- as the metal touches the steel: her hand stays, a last hold she does not admit to.
(Safety: gaze always engaged in the task, never a frozen glassy unfocused stare; natural blink
cadence.)

ACTING TASK, DAVIDE (fully invested in the tactic; the work happens in the eyes):
SCENE DIRECTION (shared, unspoken): a normal morning; nobody turns this into a goodbye.
MOTIVE: if he begs, she leaves faster and thinks less of him.
GOAL: leave her a way back without asking for it.
OBSTACLE: one plea and the morning breaks.
TACTIC: refuses to make it final; searches her eyes for an opening.
Moment to moment:
- during her line: weighs whether she means it, eyes on hers.
- looking down: decides not to reach for them.
- during his line: holds the door open, eyes stay on hers longer than the words need.
(Safety: gaze always engaged in the task, never a frozen glassy unfocused stare; natural blink
cadence.)

Look: 35mm photochemical film, neutral midtones, fine grain, natural skin texture, shallow depth
of field. Light: cold pre-dawn daylight from the shop window screen-left, one warm bulb above the
counter. Continuity: Ines holds the keys until they rest on the counter, then her hand stays on
them. Davide's hands stay empty. Count of key rings: one.

Audio: only the two voices, the oven fan and the contact sounds. No music, BGM, score,
instrumental, melody, soundtrack, synth, ambient pad, drone, swelling tone, crescendo, musical
build or stinger at any moment. No subtitles.

Settings: mode omni_reference, aspect 21:9, duration 10 s, resolution 720p, audio on.
References: @char_ines, @char_davide, @loc_bakery, @prop_keys (Elements, in this order).
```

**B. Edit of the same take**

```
Label: S12 SH040 T02 (edit of T01)

Edit 6 to 9 s. Davide's right hand goes from flat on the counter to resting beside the keys,
not touching them. Keep both faces, both lines, the lighting, the locked-off camera and
everything else exactly the same. No music. No subtitles.

Settings: mode video_edit, source T01, audio on.
This take changes: Davide's hand only.
```

**C. Extension forward**

```
Label: S12 SH050 T01 (extends S12 SH040 T01)

Audio: [policy line].
Extend forward from the last frame of @video1. Lighting, mood, both characters and the
locked-off camera carry over.
0-3s: Ines lifts her hand off the keys, turns and walks out of frame screen-left.
3-5s: Davide stays, hands flat on the counter, eyes on the keys. Final frame: the keys alone on
the counter, Davide's hands either side of them, the camera unmoved.
Audio: [policy line].

Settings: mode video_extension, forward, duration 5 s, resolution 720p, audio on.
```

**D. Location still for the reference**

```
The interior of a small neighbourhood bakery before dawn, seen from the street door at eye
level, 35mm full-frame-equivalent lens, clean rectilinear rendering, no distortion, 21:9 frame.
Frame left: the shop window, a wooden bread rack with empty baskets in the foreground, the dark
street beyond the glass. Frame centre: a brushed-steel counter running away from camera, an old
till at its far end. Frame right: a white tiled wall and a half-open wooden door to the oven
room, warm light inside. Cold blue pre-dawn light through the window from frame left; one warm
bulb above the counter, its light staying in a pool on the steel. The steel reads neutral grey,
the tiles off-white, the wood its own brown. Flour dust along the counter edge, worn floor tiles
at the door. 35mm photochemical film look, fine grain. No people, silhouettes, faces, human
figures or reflections of people; no figures through the window or the door.
```

## 21. Other models (Kling, Veo, Sora, Wan, Hailuo and others)

Transfers: the skeleton order, timed segments, reference roles with what-not-to-take, the
continuity ledger, the ACTING TASK, the audio policy wording, the repair loop.

Does not transfer without checking that model's documentation: the `@image1` and
`<<<element_id>>>` syntax, the `{ }` `< >` `【 】` audio syntax, the 30 s ceiling, the
reference counts, obedience to timestamps (Seedance 2.0 ignores them; other models: I don't know
until tested).

## 22. Records

- Take file name: `<filmid>_<S##>_<SH###>_<T##>.mp4`; the prompt beside it as `.txt` with the
  settings line. Scenes `S01`, shots `SH010`, `SH020` (gaps leave room for inserts like `SH015`).
- Each take records: job id, settings, credits, prompt file, rating, what this take changed.
- Keep working wording verbatim between takes. Number the versions so every result traces back to
  its prompt.
- Approval request before any spend:

```
REQUEST 001 / S01 SH010 T03
Model: seedance_2_5, mode omni_reference, 8 s, 720p, 21:9, audio on (never music)
Credits: 56 (preflight)   Balance after: [n]
This take changes: T02 rushed the turn; this one adds timed segments 0-3 / 3-6 / 6-8
```

## Appendix: probing a clip

```
# duration, resolution, fps
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -show_entries format=duration -of default=nw=1 in.mp4
# one frame per second, for reading wardrobe, framing, key direction
ffmpeg -i in.mp4 -vf fps=1 -q:v 2 frame_%03d.jpg
# exact last frame, to seed the next clip
ffmpeg -sseof -0.1 -i in.mp4 -frames:v 1 -q:v 2 last.jpg
# where speech starts and stops, for timing anchors
ffmpeg -i in.mp4 -af silencedetect=n=-30dB:d=0.25 -f null - 2>&1 | grep silence_
```

Timecode to seconds at 24 fps: `mm:ss:ff` = mm x 60 + ss + ff / 24.
