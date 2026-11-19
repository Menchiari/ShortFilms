# Mistakes log

Read before any generation, any plan, any list. One entry per mistake: what happened, the cause,
the rule that prevents it. Newest first.

## 2026-11-19, Politician S04 SH080 T01 and T02 (27 credits)

- **What:** both prompts named the reference as "@Image1" and the fat man as "the fat man from @Image1" instead of
  the element `@char_big-guy (@Image1)` and `@char_big-guy` in the body (docs/PROMPTING.md step 2). The T03 draft
  repeated it.
- **Cause:** the session brief named an old prompt (001_S03_SH010_T01.txt) as house template. I read PROMPTING.md
  once at session start; the naming rule changed in it at 17:36 UTC the same day, and every later prompt was a copy
  of my own first one, so the old naming carried forward. The pulls brought the new rule; I never re-read it.
- **Rule:** before writing or copying any prompt, re-read docs/PROMPTING.md step 2 from freshly pulled main and
  start from the template it names, never from a brief's template or an older prompt. Before every cost preflight,
  check: every reference line reads `@char_/@prop_/@loc_<name> (@ImageN)`, and the body uses only those names.

## 2026-11-18, Politician S02 SH050 T03 and T04 (24 credits)

- **What:** in both takes the car reaches the foot of the towers in two seconds: the town reads as a toy model (Leonard).
- **Cause:** my prompt ended on "the car small, racing toward the gap". For the car to look small next to a skyline about
  1.5 km away it has to cover about 200 m in 2 s (about 340 km/h). The town's distance came from the loc_town-edge image
  (a far skyline), not from the d11 clip (towers close, filling the frame); the end state was never checked against speed.
- **Rule:** every end position of a moving object gets a distance that its speed can reach in the time ("about 60 m
  away after 2 s"), and its size in frame against a fixed object ("as tall as half a tower").

## 2026-11-18, Politician S02 SH110 T02 (96 credits, approved)

- **What:** asked for a 720p final of a Seedance 2.5 draft; Higgsfield rendered it at 1080p and charged the 1080p price.
- **Cause:** a draft final (`draft_job_id`) ignores `resolution`. The preflight showed it: 96 credits at 720p and at 1080p
  alike, while a fresh 720p generation quoted 42. I flagged the gap as unknown instead of reading it as the answer.
- **Rule:** a draft final costs the 1080p rate (16 credits per second) and comes out at 1080p. Present it that way. When two
  quotes that should differ come back equal, the parameter that differs is being ignored.

## 2026-11-18, Politician S02 SH100 T02 and T03 (24 credits)

- **What:** Leonard: "the city doesn't look realistic, street signs everything is wrong". No lamp posts, lane lines,
  traffic lights, signs, sidewalks or parked cars; storefronts sit on a dirt road; identical towers repeat to infinity.
- **Cause:** the prompt carried none of the street rules ("Nobody in the street", furniture only named as "only" for
  image 2), and the guide clip is the d11 animatic street, which has no furniture: the model took the layout from it.
- **Rule:** a guide clip of a street that lacks the street rules is not used. Start from the location image that
  carries them (start frame) and describe the camera in words.

## 2026-11-18, Politician S02 SH080 T03 (12 credits)

- **What:** the car skidded straight, but in a city street with towers and palms; the shot happens outside the city, desert only.
- **Cause:** the "palette_afternoon" image (3bf30eee) is a city street. I passed it as "color and light only" without looking at it;
  once the T01 video stopped carrying the place, the model copied the street.
- **Rule:** look at every reference image before a preflight, palette images included. A "color only" image still gives its place.

## 2026-11-17, Politician S01 SH020 T03 to T06 (70.75 credits for one 2 s shot)

- **What:** four takes. T03 edited the old take into an LED sign Leonard never asked for; T04 held still; T05 put the
  panel in the wrong row; T06 worked.
- **Cause:** T03: I chose an edit of a take Leonard had rejected instead of starting from the reference he named.
  T05: Seedance moved the empty slot to the Plus row on frame zero; I proposed re-rolling the same inputs with
  firmer words. Leonard's fix was to rebuild the start picture around what the model did.
- **Rule:** when a take drifts the same way twice, rebuild the inputs around the drift instead of re-rolling them.
  When Leonard names a source, start from that source.

## 2026-11-17, Politician S01 SH020 T04 (29.5 credits with the stills)

- **What:** the sign was right, but after the panel went in the take held still for three seconds: nothing happened.
- **Cause:** I wrote the second half as a hold ("keeps his hand on it, looks at the sign") to land on the end still.
- **Rule (Leonard):** "beautiful, interesting, or both" does not cover a shot where nothing happens and the frame is
  not breathtaking. Every second of a shot carries an action, unless the image itself is breathtaking.
## 2026-11-17/18, "a branch for each shot" (no credits)

- **What:** Leonard asked for a conversation branch per shot. I first queued suggestion cards for separate sessions, then
  told him twice that I cannot create conversation branches, while his sidebar showed other sessions doing exactly that.
- **Cause:** I read "branch" as a git branch or an app feature for forking a chat, and never connected it to
  `create_session`, which opens a child conversation nested under the current one. I answered from an assumption instead
  of checking what he could see.
- **Rule:** a conversation branch is a child session made with `create_session` from the current session (titled
  "Scene N - SHxxx", with a self-contained brief). When a word has two readings, check the user's evidence before acting.

## 2026-11-17, Politician S02 prompt files emptied (no credits)

- **What:** my script emptied 001_S02_SH120_T01.txt and 001_S02_SH200_T01.txt in commit 7e1d0d8, and the REQUEST 018 table
  offered them as ready. Caught before any submission.
- **Cause:** `open(f, "w").write(f(open(f).read()))` truncates the file before reading it; my check only looked for banned
  words, which an empty file passes.
- **Rule:** read into a variable first, write after. Every prompt check asserts a minimum length and the audio line at the
  start.

## 2026-11-17, Politician S02 REQUEST 016 (63 credits)

- **What:** SH030 T01 (35) and SH100 T01 (28) copied the d11 animatic's grey geometry as untextured CG: the road and a
  foreground block in SH030, the whole street in SH100.
- **Cause:** both prompts gave the clip with no real image of that place (SH030: car and palette only; SH100: the town
  edge seen from outside). The S05 SH020 test had already shown the same failure with a palette-only prompt, and I had
  read it. I flagged the risk as unknown instead of applying it.
- **Rule:** a reference clip goes in only when every place in its frame also has a real image in the references.
  Otherwise drop the clip and describe the place in words.

## 2026-11-17, Politician S02 REQUEST 015a (84 credits)

- **What:** SH010 T01 was static and the town small; SH090 T01 was framed wide with a town behind him and flat acting;
  the briefcase in SH060 T01 bounced like it was on a horse. No S02 prompt used the d11 animatic clips, which exist for
  every 3D shot and carry Leonard's framing.
- **Cause:** my material check covered elements and images, not the animatic clip in each shot's `animatic` field, so
  prompts written without the clips passed. Motion was described without a size ("bounces with the road" in a car
  "racing over a rough road"). The acting task played calculation; his inner state was in no document.
- **Rule:** the material check lists each shot's animatic clip, and every 3D shot uses it as a video reference with the
  motion diagram line (no extra cost). Every motion gets a size ("slides a few centimeters"). His inner state is in the
  bible (Leonard, 2026-11-17) and goes into every acting task.

## 2026-11-17, Politician S02 request 013 (no credits spent)

- **What:** S02 prompts used the request 011 images for the town edge and the car. Leonard had already registered
  different images as the elements loc_town-edge and prop_car. Two of four references were wrong.
- **Cause:** I took image ids from the repo docs and local files, not from the live element list in Higgsfield.
- **Rule:** before any preflight, list the live elements (manage_reference_elements, action list) and take every
  image id from there. The ids in `films/<film>/film.json` under `higgsfield.elements` are refreshed from that list.

## 2026-11-17, Politician elements and locations (request 011)

- **What:** I created 9 elements with the Higgsfield tool: they landed in the workspace, outside the project, so
  they are void for the contest. The locations broke street rules: the crossroads had no traffic lights, no
  markings, four lamp posts at the four corners pointing in like stage lights; the other streets had no
  markings, no signs, lamps placed for the picture.
- **Cause:** the element tool has no project field; I created the elements after saying I could not confirm
  where they would live. The crossroads copied my own 3D blockout, which placed lamps for the composition, and
  the prompt said "keep the street lights". No prompt named any street furniture rule.
- **Rule:** Claude never creates elements; images go to the project folder, Leonard makes the elements. Every
  location prompt carries the street rules in `politician/assets.md`. A blockout gives camera and layout, never
  street furniture. When I cannot confirm an action meets a hard constraint, I do not take it: I say so.

## 2026-11-16, Politician S01 SH020 T01 (12 credits)

- **What:** the price board came out building-sized, each digit taller than the worker.
- **Cause:** a real object (a gas price sign) was described without a photo and without a scale
  anchor; "tall price board with large number panels" gave the model no size.
- **Rule:** a real object gets a real photo as reference (see the PPK/S entry), and every object
  that can be any size gets a size tied to a body: "each tile the size of the worker's head".

## 2026-11-16, Politician S01 REQUEST 005 (SH030, SH070, SH100)

- **What:** SH070 had cars facing both ways; SH100 showed a delivery van alone on an empty plain;
  SH030 answered the shot with gunfire at once and hid the action behind the crowd.
- **Cause:** SH070's prompt named two directions (outbound toward camera, inbound empty) and too
  many lanes. SH100 followed the screenplay line literally and named "police truck" without the
  features that make one. SH030 packed cause and answer into one second each.
- **Rule:** traffic: one direction, said once, a few lanes, no moving traffic. A vehicle type
  needs its identifying features or an element. Check that the image delivers the shot's reason
  in its world. Violence has beats: the act, the reaction, a pause, the answer.

## 2026-11-16, Politician S01 SH010 T02 (12 credits, refunded)

- **What:** the take was blocked by the output filter. The request did not say the shot carried a
  filter risk.
- **Cause:** the production plan lists hanging as a filter risk with a written fallback. The
  request was checked against reason and material, not against that list. T02 made the noose
  explicit and put his real face on it.
- **Rule:** before any request, check the shot against the plan's filter list. A listed risk goes
  in the request with its fallback.

## 2026-11-16, Politician screenplay edited in two sessions at once

- **What:** I edited `screenplay.fountain` (S02 towers and asphalt, S06 SH120 PPK/S slide) and
  `animatic/src/sets.py` on my branch; they auto-merged to main. Another session was writing drafts
  9 and 10 on its own branch. Every push of that branch now conflicts with main: the stories-sync job
  fails and GitHub emails Leonard each time (11 failures since 21:56 UTC).
- **Cause:** I did not check other branches for a newer draft before editing a shared story file.
- **Rule:** before editing the screenplay, the animatic source or any shared story file, fetch all
  branches and check who else changed it. If another session holds a newer draft, do not edit:
  hand the change to that session (or to Leonard) as a note.

## 2026-11-16, Politician props (request 002b, 4 credits)

- **What:** the PPK/S came out as a Beretta 92 with a misspelled engraving; the bobblehead does not
  have his face.
- **Cause:** a specific real object was asked for by name only, with no photo. The bobblehead relied
  on the element placeholder alone.
- **Rule:** a real, specific object (gun, vehicle model, product) needs a real photo as reference,
  or the photo itself becomes the element. A face that must be recognized gets the element image as
  a direct reference too.

## 2026-11-16, Politician S01 SH010 T01 (28 credits)

- **What:** generated the riot signs with a generic face. The face exists so the audience
  recognizes him later; without old man A the shot cannot do its job.
- **Cause:** checked settings and cost, not the reason of the shot. The missing element was written
  as warning 2 of 3 instead of a stop. The plan said "S01, no elements needed", which was false for
  4 of 12 shots.
- **Rule:** before any preflight, one line per shot: its reason, the material that reason needs,
  whether the material exists. Missing material: stop, one line, first thing in the message.

## 2026-11-16, Politician asset list

- **What:** the Monday reference list missed the square (33 shots in S06, S07, S09, plus views from S05 and S08; the main location since
  draft 8), the man with the pipe and the reporter.
- **Cause:** the list was written before draft 8 (2026-11-15 06:15) and edited after it (21:17)
  without being checked against it. Draft 8 moved the chase to a square.
- **Rule:** after every new draft, recheck the asset list against the screenplay, scene by scene.

## 2026-11-18 001 S02 SH010 T06: angle not changed, tripod in frame (28 credits)

- **What:** asked for eye height with start frame v1 as an image reference. The take kept the reference's
  camera height exactly, and a camera tripod stands on the road for the whole shot.
- **Cause:** a Seedance image reference of a whole scene locks its composition like a start frame; the
  prompt text cannot move the camera against it. "Locked-off on a tripod" was drawn as an object.
- **Rule:** a new angle needs a new image at that angle (from Leonard's pipeline). Never write "tripod" in a
  prompt: write "static camera".
