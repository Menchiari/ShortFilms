# Take review v2, film 001, 2026-11-20

v1 was too simple and wrong in two places: S05 SH140 T03 (5) used `loc_square`, and S08 SH010 T03
(5) is "exactly the animatic composition, but realistic" (Leonard's note on T02). Neither the element
nor the animatic layout is bad in itself. This version looks at what changed between takes of the
same shot, at every note Leonard wrote, and at full frames.

Source: `shotlist.json` (297 takes, 205 rated), Leonard's notes, prompt files, frames.

## 1. The first take is a guess, Leonard's note is the fix

| Take | Rated | Average |
|---|---|---|
| T01 | 67 | 2.54 |
| T02 | 50 | 3.42 |
| T03 to T06 | 79 | 3.3 to 4.1 |

43 times a shot jumped two or more points from one take to the next. What changed:

| Change | Jumps |
|---|---|
| Prompt only, same references, after Leonard's note | 17 |
| A reference removed (element, guide clip, animatic, cabin, `loc_square`) | 10 |
| A start frame added | 6 |
| Footage Leonard approved reused (extension, a frame of an approved take) | 4 |
| Guide clip changed or other | 6 |

A reference was added and helped only when it showed exactly the target frame (start frame,
approved footage). A reference was removed and helped ten times. A reference image is copied, not
read: when it shows another angle, another place or another moment, that is what comes back
(the cabin back in S08 SH060 T01, the street-light corner in S09 SH040, SH050 and SH110 T01, the
previz boxes from every place-filling guide clip).

Most of the gain comes from Leonard's direction, not from the method. My first takes are mostly
wrong about what he sees, not about how Seedance works.

## 2. What Leonard's notes are about

Every note on a rated take, sorted by what it complains about (keyword sort, rough, one note can
count twice):

| Problem | Notes | On takes rated 1-2 |
|---|---|---|
| Blocking, geography, angle, distance, height | 73 | 37 |
| Fake, AI, previz, toy, game look | 46 | 22 |
| Crowd and casting (all men, all one origin, clones, all acting the same) | 38 | 20 |
| Background or location wrong | 30 | 13 |
| Prop scale or detail (gigantic pipe, numbers, shells, folder) | 26 | 10 |
| Acting, expression | 21 | 8 |
| Physics, timing, slow motion | 18 | 11 |
| Film look (lens, grain, cinematic) | 18 | 7 |
| Light, color (too orange) | 17 | 5 |
| Quantity (too many sheets, people) | 11 | 5 |

The biggest single cause is not the look: it is that I put people and camera in the wrong place.
Where he stands, which way the camera faces, how far, how high. The film has no map. Every S09
session rebuilt the square from the screenplay and an element image, and each got it differently.
The street-light corner problem was found in S09 SH050 T01 and then repeated in S09 SH040 T02 and
T03 and S09 SH110 T01, because the sessions run in parallel and the lesson lives only in one take note.

## 3. Behavior: people doing something, or props standing around

The 5s that are not about the look are about behavior: S04 SH070 T02 (he goes for the briefcase at
once, real time), S04 SH090 T02 (a fox planning his escape), S05 SH030 T02, S08 SH050 T02. The 1s
in the same category: "no human acts like this" (S05 SH140 T01), "the acting is flat" (S02 SH090
T01), "mannequins" (S06 SH060 T01, S07 SH030 T01), "they all act the same" (S07 SH080 T01),
"muppets" (S06 SH010 T03), "the movement is static and robotic, taken from the animatic" (S09 SH010 T01).

Pattern: a person with a concrete goal in the moment reads alive. Extras listed as a crowd
("about fifty people") come out as copies doing one thing. `style.md` already says "a task for every
person in frame, extras included"; where the prompt gave each group a different task and pace, the
crowd worked (S06 SH010 T04, S07 SH080 T03, S05 SH020 T10).

## 4. The look: what full frames show

Compared at full size: S06 SH030 T04 (5), S07 SH080 T03 (4), S05 SH140 T03 (5) against S09 SH110 T03.

The good frames:
- **Something is happening.** Men walking at him, a riot in motion, a gun on the crowd. The frame has
  an event and the event has a direction.
- **The world is cluttered.** Parked cars, a pipe, rubble at the wall foot, smoke, debris, shoes,
  people of every size at every distance. Nothing is cleaned for the shot.
- **Neutral, washed light.** Warm but grey, the sky blown out, shadows soft. It looks exposed by a
  camera, not graded.
- **A real camera position and foreground** (his back, the railing, the backs of men).

S09 SH110 T03:
- **Nothing happens.** The paper, the subject of the shot, is a few small sheets that run out by 2 s.
  The frame has no event, so the model makes a beauty shot.
- **Clean street.** No rubble, no shoes, no rocks, no sticks, no trash after a riot of sixty people.
  Only bodies placed along the curb. Clean reads as staged.
- **The car is posed like an ad:** centered in its space, facing camera, headlights on.
- **Monochrome orange with a lens streak laid on top:** a graded sunset, the "filter" look.

Same pattern in the other bad wides (S09 SH040 T01, S06 SH060 T01, S07 SH080 T01, S09 SH110 T02):
clean ground, frontal planes, evenly spread people or bodies, nothing in the foreground.

## 5. Light at sunset

S08 and S09 average 2.43 and 2.62, the lowest scenes; S04 (afternoon, side street) is 3.70. S08 and
S09 prompts with the `palette_sunset` image average 2.33 (30 takes) against 3.00 without (8 takes).
The 5 at sunset (S08 SH010 T03) is hazy and pink-grey, not orange; Leonard on S09 SH050 T04: "light
too orange, too fake, more like 35mm film". [Inference] sunset words plus the palette image push
Seedance to its graded golden-hour default. Sample too small to prove.

## 6. Why this shot (S09 SH110) failed three times

1. **Wrong place, then no map.** T01 took the element's corner. I did not look at the image or at the
   S09 takes already made. T02 and T03 invented a place that matches no other S09 shot.
2. **No event.** The screenplay line is "the certificates flutter among the bodies in the rotor wash".
   I made the paper a detail and the street the subject. The money among the dead is the shot; it
   was never more than a few sheets.
3. **A clean, staged aftermath.** No debris, bodies laid out, an advertised car.
4. **Orange grade.** Palette image and "orange" in every light paragraph.
5. **Composition copied from the animatic as words** (T01, T02), then corrected only by layout tricks
   (T03): the frame changed, the emptiness stayed.
6. **Review against my checklist,** not against Leonard's eye and the approved shots.

## 7. Rules I propose (Leonard decides; nothing changed in the bible yet)

1. **One map of each location**, shared by every shot session: a top view with the camera positions
   of approved takes and which direction each faces, plus one approved frame per direction.
   For the square: the street-light corner, where the helicopter sits, where the bodies lie, the
   street to the crossroads. No shot of that place is prompted before it exists.
2. **A reference image only when it shows the target view.** Element images go in only after looking
   at them and checking that the angle and place match.
3. **Before the first paid take of a wide: a free check with Leonard.** The planned frame in two lines
   (where the camera stands, what faces it, what moves) plus the nearest approved frame.
   T01 averages 2.54 because it is my guess.
4. **Every shot has an event, and its subject is big enough to read.** If the subject is paper, the
   paper fills the frame.
5. **Aftermath has debris.** Rocks, shoes, sticks, a lost bag, trash, dust on everything. Bodies where
   they fell, not placed.
6. **Every person has a task; groups get different tasks and paces.**
7. **Sunset light in words,** hazy and grey-warm, sky blown, no palette image, no laid-on streaks;
   test on one take before it becomes a rule.
8. **Review in this order:** does it look like a still from a real film, does it match the approved
   shots around it, then the checklist.

## 8. S09 SH110 next

Map of the square first (free). Then a start frame from Leonard's pipeline or a frame of an approved
S09 take facing that direction, with the paper as the subject and riot debris on the ground, and
Seedance only moving the paper. Cost to be quoted on request.
