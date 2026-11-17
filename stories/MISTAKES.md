# Mistakes log

Read before any generation, any plan, any list. One entry per mistake: what happened, the cause,
the rule that prevents it. Newest first.

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
