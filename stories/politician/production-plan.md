# Politician: 10-day production plan

Script draft 6: 10 scenes, 100 shots, 5:34. Seedance 2.5 on Higgsfield, 24 fps, PIPELINE.md. Balance on 2026-11-11: 31,721 credits. Shot by shot: "Locations and angles" (PDF).

Day 1 is the day you say "lock". The dates assume Thursday 12 November [ASSUMPTION].

Method: an assembly line by scene. While scene N generates, you cut scene N-1 and lay sound on N-2. Nothing waits for "all shots done".

## 1. Decisions on Day 1 (10 minutes)

| # | Decision | My pick |
|---|---|---|
| 1 | Lock the script, start film 001 | Say "lock" |
| 2 | Aspect ratio | 21:9 |
| 3 | Resolution | 720p. 1080p for 9 establishing shots and big moments (40 s) |
| 4 | The gun | Original Ruger LCP: no last-round hold-open (LCP II added it in 2016), so the empty click is real and lives in the sound. 6+1 = 7 rounds: the count drops from 8 to 7, black instead of nickel. Alternative: keep the PPK/S; its slide locks open, there is no click, and the open slide has to read on screen |
| 5 | Voices | Generated with the takes (lip sync), then each character unified with one speech-to-speech voice |
| 6 | Risky shots | Two takes each in the first pass (an exact list, about 25 shots, about 800 credits more): saves a review-and-retake day |
| 7 | Music | The "I Was There" temp tracks can't go online without rights. An original cue on Day 8 if you ask, or no score |
| 8 | Piazzale Loreto echo of the hanging | Your call, no effect on time |
| 9 | Your hours | Planned: about 5 h a day, more on Days 7 to 10. If that's wrong, the plan moves |

## 2. The 10 days

| Day | You | Claude |
|---|---|---|
| 1 Thu 12 | Decisions. Approve the test list. References: the town style frame, then the old man A. About 3 h | Film 001, stages 1 to 5 in one pass, Higgsfield project and folders. Filter and technique tests. Riot shots S01 SH030 to SH080 at 720p. Crossroads blockout and its 12 setup renders. A prompt sheet for every reference |
| 2 Fri 13 | References: B, C, D as edits of A; lady, fat person, friend, Roger, bobblehead; the 12 crossroads setups over my renders. React to the tests and S01. About 5 h | Elements registered as they arrive. Every prompt for S02 to S10. All graphics. S01 SH010, SH020 (his face on the signs). S02 landscape shots (no elements needed) |
| 3 Sat 14 | References: car outside and inside, helicopter outside and cabin, streets, props. Review S02, S03. About 4 h | S02, S03. Each scene delivered as a Resolve timeline |
| 4 Sun 15 | Review S04, S05. Cut S01 to S03. Start making SFX from the list. About 5 h | S04 (dialogue), S05 |
| 5 Mon 16 | Review S06, S07. Cut S04, S05. SFX. About 5 h | S06, S07 |
| 6 Tue 17 | Review S08 to S10. Cut S06, S07. Sound on S01 to S03. About 5 h | S08, S09, S10 |
| 7 Wed 18 | One retake list for the whole film. Cut S08 to S10: full rough cut. About 6 h | Retakes. Composites finished (TV, phone, scope, bond, Agreement). Voices unified. 24 fps check on every keeper |
| 8 Thu 19 | Picture lock. About 6 h | Last retakes, only for holes found in the cut. Music cue if you ask |
| 9 Fri 20 | Sound design and mix. About 8 h | Extra SFX on request. Poster stills, film.json |
| 10 Sat 21 | Grade, export, upload. Half a day of buffer. About 5 h | Site, upload checklist |

## 3. Challenges and solutions

Certainty: High = works unless something outside our control breaks. Medium = depends on a test or on your time.

### A. Time and people

| # | Challenge | Solution | Certainty |
|---|---|---|---|
| A1 | Your time is the bottleneck: references, reviews, cut, sound, grade | I take everything that is not taste: prompt sheets for your references, all composites, a Resolve timeline per scene, the SFX list with prompts, voice unification, 24 fps fixes | High |
| A2 | About 100 shots to approve | One approval per scene: the exact list of takes, credits each, total. About 12 approvals for the film | High |
| A3 | Reviewing about 200 takes | One video per scene, takes in script order, shot and take burned in. You answer in one line | High |
| A4 | I only work while a session runs | Before you sleep, give me the long jobs that cost no credits (prompts, graphics, composites, timelines). Credits never move without you | High |
| A5 | Script changes after the lock cost days | After Day 1, changes only as cuts and trims. A new shot only for a hole in the cut, Day 8 at the latest | High, if held |

### B. References

| # | Challenge | Solution | Certainty |
|---|---|---|---|
| B1 | References gate about 90 of 100 shots | Made in the order that unlocks the most shots (section 4). Shots without elements (riots, landscapes) generate meanwhile | High |
| B2 | The same old man in about 60 shots, in 4 states | B, C and D are edits of the same A image, not new images: same face by construction. Bobblehead, protest signs and TV portrait all come from A | High |
| B3 | Your Midjourney time | I write the prompt for each reference (framing, light, background, lens). The crossroads needs 12 images, one per camera setup, not 43 | Medium-high |

### C. Content filters

| # | Challenge | Solution | Certainty |
|---|---|---|---|
| C1 | Seedance limits on guns, a gun at the temple, a hanging, a lynching, firebombs at police, the stain: unknown | Day 1, before anything else: about 13 text-only tests at 480p (12 credits each). Riot shots go straight at 720p, so the ones that pass are keepers | High that we know on Day 1. The result: I don't know |
| C2 | A refusal on a core beat | Every risky shot gets a written fallback: cut on the action, the hit out of frame, the sound carries it. Gun at the temple: close on his eyes, the muzzle at the frame edge. Hanging: rope and foot from below, his face upside down in close | Medium-high |

### D. Continuity

| # | Challenge | Solution | Certainty |
|---|---|---|---|
| D1 | 43 shots (2:32) at the crossroads: car, street light, landing area and sun must stay put | A grey blockout built in code here, no credits (Blender if it installs in this container, a browser 3D engine otherwise: checked Day 1). Shots grouped into about 12 camera setups, like a real shoot. One start frame per setup, reused by all its shots | High |
| D2 | Same dog, car, bodies and certificates shot to shot | Frame chaining: a frame of the approved take seeds the next shot of the same setup. No credits | High |
| D3 | Every generation invents a new voice | Generated audio kept for lip sync and timing, then each character's lines pass through one speech-to-speech voice. A voice isolator cleans whatever sits under the dialogue | High |
| D4 | 69 of 100 shots are shorter than Seedance's 4 s minimum | Runs of short shots in one place become one multi-shot generation (look left and right, the inserts, the hanging beats). The rest at 4 s, trimmed | High |

### E. Text on screen (video models garble text)

| # | Challenge | Solution | Certainty |
|---|---|---|---|
| E1 | Signs, gas board, bond, Agreement | Nothing readable is generated. Start and end frame lock: the take starts or ends on my exact image, so the text is clean when the eye reads it. Bond spill ends on clean bonds on asphalt; the gas board starts on 1.94 and ends on 5.89 | Medium-high (start, end and element references in one call: checked in the tests) |
| E2 | TV news (S01 SH090) | Locked-off TV with a blank screen. The reporter generated full frame with lip sync, my news package on top, a fixed corner pin. I render it | High |
| E3 | Phone insert (S05 SH080) | Hand and phone generated with a green screen. I find the green corners in every frame and map my animated screen onto them: no manual tracking | Medium-high |
| E4 | Scope boxes (S08 SH030, SH070) | A face detector runs on the generated clip and draws the boxes: the detector is the effect. The upside-down man gets his green box from a tracker | Medium-high |
| E5 | The signature (S09 SH110) | A still of the Agreement page, push-in in the edit. No credits | High |

### F. Hard shots

| # | Challenge | Solution | Certainty |
|---|---|---|---|
| F1 | Car over the low camera; landing behind him with the case in front; takeoff through the windshield | Tested Day 1. Where the path must be exact, a grey render of the blockout guides the motion as a video reference | Medium |
| F2 | Dolly zoom (S02 SH100) | Prompted first. Fallback: a plain push-in at 1080p, widened in Resolve while the camera moves in. Same stretch, no model needed | High (fallback) |
| F3 | The crowd slowing in his head (S06 SH070) | Slow motion in the take. Fallback: a short optical flow ramp in Resolve | Medium-high |
| F4 | Crowd moves: the tough ones walking in, the sprint, the scatter | Seedance first, tested Day 1. Crowd simulation only if those tests fail | Medium |
| F5 | The gun's click | Decision 4 | High once decided |

### G. Post and release

| # | Challenge | Solution | Certainty |
|---|---|---|---|
| G1 | Cutting 100 shots | Each scene arrives as a Resolve timeline (FCPXML, paths on D:\ShortFilms) in script order, takes trimmed to script length. You start from a cut, not from a bin | High |
| G2 | Sound design in little time | The guide audio already carries crowd, contact sounds and dialogue. The SFX list with ready prompts per shot is done on Day 2. You make SFX between reviews and sound each scene as it locks | Medium (your time) |
| G3 | 720p and 1080p mixed, looks that drift between takes | One 1080p 24 fps timeline. Start frames from your pipeline keep the palette close. One base grade, then per scene | Medium-high |
| G4 | Jitter | fps.py probe and fix on every keeper before it reaches you | High |
| G5 | Music rights | Temp tracks stay offline. Original cue on Day 8 if you ask, or no score | High |
| G6 | Release | YouTube asks for the "altered or synthetic content" disclosure on realistic AI video: tick it. The violence may bring an age restriction: less reach, the film still goes out | High |

### H. Infrastructure

| # | Challenge | Solution | Certainty |
|---|---|---|---|
| H1 | Generation time and parallel limits | Measured on the Day 1 tests. Each scene goes as one batch | I don't know the numbers yet |
| H2 | Repository size (every take goes into git) | File size per take measured on Day 1. I warn you before 4 GB | Medium |
| H3 | Credits | Not a constraint: about 6,000 to 7,000 of 31,721. Here credits buy days (decision 6) | High |

## 4. References, in the order they unlock shots

1. Town style frame: the look of every town shot.
2. Old man A: about 30 shots, and the source of B, C, D, the bobblehead, the signs and the TV portrait.
3. Crossroads: 12 setups over my renders (43 shots).
4. Old man B, C, D (edits of A): about 30 shots.
5. Car, outside and inside: S02, S03.
6. Lady, fat person: S04, S08, S09.
7. Helicopter outside and cabin, Roger, friend.
8. Props: briefcase, pistol, pipe, rope, phone. The reporter needs no sheet (one shot).

## 5. Credits (estimate)

| Item | Credits |
|---|---|
| Day 1 tests, 480p | about 160 |
| First pass, one take per generation, short shots grouped | about 2,900 |
| Second take of about 25 risky shots (decision 6) | about 800 |
| Retakes, Days 7 and 8 | about 2,000 to 3,000 |
| Total | about 6,000 to 7,000 |

Every list gets a free preflight and your approval of that exact list.

## 6. What can break the 10 days

1. References after Day 3: each late day moves the end by about a day.
2. A filter refuses a core beat (the gun at the temple, the hanging, the massacre): the fallback changes the film, and you decide the same day.
3. Sound design squeezed into Day 9: it starts per scene on Day 6.
4. Generation time and parallel limits: unknown until Day 1.
