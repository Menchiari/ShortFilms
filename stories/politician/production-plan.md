# Politician: production plan

Final script: 10 scenes, 100 shots, 5:34 of screen time. Seedance 2.5 on Higgsfield, 24 fps, following PIPELINE.md.

## 1. Your decisions first (about 10 minutes)

| # | Decision | My pick |
|---|---|---|
| 1 | Lock the story and the script, and start the film | You say "lock". I run `filmtool new "Politician"` (film 001) and copy the script into the film. |
| 2 | Aspect ratio | 21:9. It suits the Clancy register, and Seedance supports it at the same price. |
| 3 | Resolution of the takes you keep | 720p. Tests at 480p. A take can't be re-rendered later at a higher resolution as the same performance. |
| 4 | Voices and accents | Generated audio with a written accent for each character. A line gets replaced with an ElevenLabs voice only if an accent drifts. |
| 5 | Music | Your two "I Was There" references stay a temp track until the rights are clear (I don't know who holds them). The final cue gets made in stage 11. |
| 6 | Piazzale Loreto echo of the hanging | Your call: keep it or avoid it. |

## 2. Stages and who does what

| Stage | Claude | You | Your time |
|---|---|---|---|
| 0. Film created | Runs `filmtool new`, copies the script into `01-story/source/` | Say "lock" | 1 min |
| 1 to 5. Analysis, bible, shot list, shot plan, sound list | One pass: style, characters, locations, props, `shotlist.json`, budget, SFX list with ElevenLabs prompts | Read a one-page PDF summary, answer the few questions | 30 min |
| 6. References | Prepares and registers your images as Higgsfield Elements in the film's project, folder REFS | Make the photographic references in your own pipeline (Midjourney) | Your biggest block |
| 6b. Graphic props | Designs every on-screen text as an image: gas board, bearer bond, news package, scope boxes, phone screens, the Agreement (rebuilt to look like a real contract) | Approve | 15 min |
| 7a. Tests at 480p | 4 risk tests (section 5) | Approve the spend | 15 min |
| 7b. Generation | Prompts, free cost preflight, generates the list you approve, scene by scene, downloads, names, logs, commits every take | Approve each list, react to the takes | Your second biggest block |
| 8. Frame rate | Fixes every take to constant 24 fps | Nothing | 0 |
| 9 to 11. Edit, sound, music | Conform list, SFX prompts, music analysis and prompts | Edit in Resolve, sound design, music choices | Yours |
| 12. Release | Updates the site page, writes the Discord post | Final export, the YouTube or Vimeo link | 15 min |

## 3. Elements to make (Higgsfield project "SF 001 Politician")

- **Characters (7 sheets):** the old man clean; the old man beaten (blood and dirt, not exaggerated: he still has to look cool at the end); the fat person; the friend; the business lady; Roger; the reporter. The crowd, the police, the old woman and the pipe man don't need sheets.
- **Locations (5):** the dirt road and the edge of town; the main street with the apartment blocks; the side streets; the crossroads (the street light at the corner, room for a helicopter to land); the helicopter cabin (cream leather).
- **Vehicles (2):** his car (defined in the bible); the Airbus ACH160, white, Lounge cabin with sliding doors.
- **Props:** the bobblehead (painted, giving the finger), the briefcase with a pocket in the lid, the nickel Walther PPK/S, the rope, the metal pipe, his phone.
- **Graphic props, made by me as images, no credits:** the gas price board, the bearer bond certificate, the TV news package (logo, BREAKING bar, ticker, his portrait), the scope's face boxes, the phone's lock and call screens, the Agreement page.

## 4. Budget

Your Higgsfield balance on 2026-11-11: 32,871 credits.

| Plan | Generation seconds | 480p (3 per s) | 720p (7 per s) |
|---|---|---|---|
| One take of every shot, each shot generated alone (4 s minimum) | 437 | 1,311 | 3,059 |
| One take, short shots grouped into multi-shot generations | about 352 | about 1,056 | about 2,464 |
| Realistic: about two takes per generation on average (estimate) | about 700 | about 2,100 | about 4,900 |
| Risk tests before the main spend | about 60 | about 180 | |

Music runs at 480p: 90 credits per 30 s. Nothing is spent without a free preflight and your approval of that exact list.

## 5. The hard shots and how we lower the risk

| Risk | Where | Plan |
|---|---|---|
| Content filters on guns and the lynching. I don't know Seedance's limits. | S06, S07, S08 | Test first, at 480p: a man falling from a gunshot at a distance; the mob seen from above; the man hanging by one foot; the massacre in a wide. If a shot is refused, imply it: cut on the crack, the fall out of frame, the sound. |
| Crowd choreography (advancing, sprinting, scattering under fire) | S05, S06, S07 SH080, S08 SH040 | AI crowd first. If it fails, a Blender previs with grey figures as a video reference (a method in PROMPTING.md). Real riot footage only as a private motion reference, never in the cut. |
| The old man stays the same person across about 45 shots, clean then beaten | S02 to S09 | Two locked character sheets, and wardrobe locks per scene in the bible. |
| Readable text | All inserts with text | Never generated. My graphics, composited in Resolve or used as start frames. |
| Hanging upside down by one foot, and the rope over the light | S07 | A start frame from your image pipeline. |
| A specific helicopter model | S08, S09, S10 | ACH160 reference stills registered as an element. |
| The crowd slowing down in his head | S06 SH070 | Generate at normal speed and retime in the edit. If the retime isn't clean, ask Seedance for slow motion directly. |
| Accents drifting between takes | All dialogue | The accent is written for each character. A line is replaced with an ElevenLabs voice only when needed. |

## 6. Order of work

1. You decide section 1. I create the film and run stages 1 to 5 in one pass.
2. You make the references while I build the graphic props.
3. Tests at 480p (about 180 credits). They answer the filter and crowd questions before any big spend.
4. Generation, easiest first to lock the look: the road and the town (S02, S03), then the dialogue (S04), then the action (S05 to S07), the helicopter and the ending (S08 to S10), and the riots (S01) last, since they only need his face on the signs.
5. Frame-rate fix, then your edit, sound design and music, then release.
