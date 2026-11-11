# Politician: production plan

Final script: 10 scenes, 100 shots, 5:34 of screen time. Seedance 2.5 on Higgsfield, 24 fps, following PIPELINE.md. The shot-by-shot list of locations and angles is in "Locations and angles" (separate PDF).

## 1. Your decisions first

| # | Decision | My pick |
|---|---|---|
| 1 | Lock the story and the script, and start the film | You say "lock". I run `filmtool new "Politician"` (film 001) and copy the script into the film. |
| 2 | Aspect ratio | 21:9 |
| 3 | Resolution | 720p for most shots. 1080p for 9 establishing shots and big moments (40 s, listed in "Locations and angles"). The resolution is chosen before a take: a take can't be re-rendered later as the same performance. |
| 4 | The gun (see section 8) | Keep the PPK/S and make it real: the slide locks open after his last shot, and at his temple the trigger does nothing. He opens his eyes and sees the open slide. |
| 5 | Voices and accents | Generated audio with a written accent for each character. A line gets replaced with an ElevenLabs voice only if an accent drifts. |
| 6 | Music | Your two "I Was There" references stay a temp track until the rights are clear (I don't know who holds them). |
| 7 | Piazzale Loreto echo of the hanging | Your call. |

## 2. Stages and who does what

| Stage | Claude | You |
|---|---|---|
| 0. Film created | `filmtool new`, script copied into `01-story/source/` | Say "lock" |
| 1 to 5. Analysis, bible, shot list, shot plan, sound list | One pass, summed up on one PDF page | Read it, answer the few questions (30 min) |
| 3D crossroads | Builds the blockout in Blender and renders every crossroads angle (section 4) | Approve the look of the layout |
| 6. References | Prepares and registers your images as Elements in the project "SF 001 Politician", folder REFS | Make the photographic references in your pipeline (Midjourney), on top of my 3D renders for the crossroads. Your biggest block of time. |
| 6b. Graphic props | Every on-screen text as an image: gas board, news package, scope boxes, phone screens, the Agreement (rebuilt to look like a real contract). The bond is your design. | Approve |
| 7a. Tests at 480p | The risk tests in section 7 | Approve the spend |
| 7b. Generation | Prompts, free preflight, generates the list you approve, scene by scene, downloads, logs, commits every take | Approve each list, react to the takes |
| 8. 24 fps | Probes and fixes every take (section 6) | Nothing |
| 9 to 12. Edit, sound, music, release | Conform list, SFX prompts, music prompts, site and Discord | Edit, sound design, music choices, final export |

## 3. Elements to make

- **The old man, 4 images for 3 states:**
  - A, clean: S02 to S05 (until the rock).
  - B, hit on the head, with dirt and a few rips from the fall: S05 SH100 to S06.
  - C, beaten, with more dirt and rips, trousers dry: S07 and S08.
  - D: C with the trousers pissed, S09 on. It's the same image as C, edited, so the two match. The stain spreads during S09 SH010.
- **Other characters, 1 sheet each:** the fat person, the friend, the business lady, Roger, the reporter. The crowd, the police, the old woman and the pipe man don't need sheets.
- **Locations:**
  - The crossroads (from the 3D blockout).
  - The dirt road and the edge of town.
  - The main street.
  - The side streets.
  - His car's interior.
  - The helicopter cabin (cream leather).
- **Vehicles:** his car (defined in the bible); the Airbus ACH160, white, Lounge cabin with sliding doors. No logos on either.
- **Props:** the bobblehead (painted, giving the finger), the briefcase with a pocket in the lid, the pistol, the rope, the metal pipe, his phone.
- **Graphic props (I make them, no credits):** the gas board, the news package, the scope's face boxes and crosshair, the phone screens, the Agreement. The bond is yours (Lincoln County Public Improvement Bond, $500,000).

## 4. 3D: the crossroads in Blender

The crossroads hosts 43 shots, about 2:30 of the film. It gets built once as a blockout: the building fronts around a large intersection, the street light at the corner, his car in the middle, a clear landing area, and a fixed sun for just after lunch.

- **What it gives:** the same geography, light direction and positions in every angle. Exact camera positions for all 43 shots. A ground plan for the crowd and the helicopter.
- **How I build it:** Higgsfield has a hosted Blender ("3D Jutsu"). I drive it with Python and render stills and grey videos. Nothing gets installed on your computer. I don't know yet whether building and rendering there costs credits. Turning a render into AI video does.
- **What happens to the renders:** they become the base for your start frames (your pipeline paints over them), and grey videos become motion references for Seedance.
- **Limit:** in this version, the hosted Blender only imports models from Higgsfield's own catalog, not files you download. A real ACH160 or a specific car model in 3D means your local Blender. For previs, a simple proxy shape is enough.

## 5. Crowds and vehicles

**Crowds, in this order (cheapest first):**
1. **Seedance alone** for most crowd shots. It handles dozens of people in a wide shot. Tested first at 480p.
2. **For the choreographed moments** (the tough ones advancing, the sprint, the scatter under fire, the mob from above, the crowd stepping back): I write a crowd simulation in Blender. That's your "each person is a ball" idea: agents that walk, sprint, keep their distance and flee from shots. It gets rendered as grey figures from the exact 3D camera, and Seedance turns the figures into people through a video reference.
3. **Not Unreal:** its crowd tools are powerful, but the setup is heavy and the result is a CG look that won't match the Seedance shots. That's not worth it for this film.
4. **Real riot footage:** at most as a private motion reference, never in the cut (rights, and real people).

**Vehicles:** the motion comes from Seedance, guided by the vehicle's element images. Blender only where the path has to be exact:
- the car passing over the low camera (S02 SH040),
- the helicopter landing behind him with the case in the foreground (S09 SH050),
- the takeoff seen through the windshield (S10).

You don't need to download 3D models of the vehicles for Seedance. A downloaded model is useful only to render clean reference angles for the elements, and its license has to allow that.

## 6. 24 fps without jitter

Seedance 2.5 outputs 24 fps. Jitter comes from four places, and each one has a fix:

| Cause | Fix |
|---|---|
| Duplicate frames or a variable frame rate inside a clip | `fps.py probe` on every take, then `fix` (conform to constant 24, or rebuild the duplicates). The first real take gets measured. |
| The timeline rate doesn't match the clips | The Resolve project and timeline set to the exact rate the probe reports (24 or 23.976, never mixed). |
| Speed changes | No frame blending. The slow crowd in S06 SH070 is generated slow, or retimed with optical flow and checked. |
| Fast pans at 24 fps strobe by nature | Pans in the prompts stay slow, and fast moves get motion blur. Your old-school static shots avoid this. |

## 7. Budget

Your Higgsfield balance on 2026-11-11: 32,871 credits.

| Plan | 720p part | 1080p part (9 shots) | Total |
|---|---|---|---|
| One take of every shot, each generated alone (4 s minimum) | 392 s = 2,744 | 45 s = 720 | 3,464 |
| One take, short shots grouped into multi-shot generations | about 307 s = 2,149 | 45 s = 720 | about 2,870 |
| Realistic, about two takes per generation (estimate) | | | about 6,000 to 7,000 |
| Risk tests at 480p before the main spend | | | about 180 |

Music runs at 480p: 90 credits per 30 s. Nothing is spent without a free preflight and your approval of that exact list.

## 8. Things to watch (realism and production)

| Item | What's wrong or risky | Plan |
|---|---|---|
| The gun's click | Checked: the Walther PPK/S locks its slide open after the last shot. An empty PPK/S doesn't click, and the open slide is visible. | Option A, my pick: the open slide is the reveal (decision 4). Option B: a small revolver, where the empty click is real, as in your first draft. Option C: a pocket pistol with no slide lock (the Seecamp .380 may be one, not verified). |
| Content filters | I don't know Seedance's limits on guns, shootings and a lynching. | 480p tests first: a fall from a gunshot at a distance, the mob from above, the hanging, the massacre wide. If refused: cut on the crack, the fall out of frame, the sound. |
| The rope shot from a hover | Hitting a rope from a hovering helicopter is close to impossible. | The helicopter is lower and closer by then. Optional: his first shot sparks off the light pole, the second cuts the rope. |
| The landing | A helicopter needs a large clear area away from poles and wires. | The 3D crossroads is built wide enough. Rotor size to check. |
| Readable text | Video models garble text. | Never generated. My graphics, composited or used as start frames. |
| No seed | A take can't be reproduced or re-rendered at another resolution. | Choose the resolution before each keeper take, and change one thing per retake. |
| Accents | AI voices drift toward a real nationality. | A written accent per character, checked on the first takes. |
| Brands | The ACH160, the PPK/S and the car are real products. | No logos anywhere (bible rule). |
| The bond | Your design: a 1948 county bond, payable to the bearer. US bearer bonds date from before 1982, so the period is right. It matured in 1968. | Keep it. Optional: a strip of interest coupons along the bottom edge, like real bearer bonds had. |
| Repository size | Every take goes into git, and 1080p takes are bigger. | `filmtool status` after each scene; I warn you well before 5 GB. |

## 9. Order of work

1. Your decisions. I create the film and run stages 1 to 5, and build the 3D crossroads.
2. You make the references (on my renders for the crossroads) while I build the graphic props.
3. Tests at 480p (about 180 credits).
4. Generation, easiest first to lock the look: the road and the town (S02, S03), the dialogue (S04), the action (S05 to S07), the helicopter and the ending (S08 to S10), and the riots (S01) last.
5. 24 fps fixes, then your edit, sound design and music, then release.
