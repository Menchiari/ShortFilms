# Take review, film 001, 2026-11-20

Source: every take in `shotlist.json` (297 takes, 205 rated), Leonard's notes in them, the prompt files,
and a frame from the 8 best and 8 worst wides. Facts are marked as counts; inferences say so.

## The numbers

| Rating | Takes |
|---|---|
| 5 | 23 |
| 4 | 80 |
| 3 | 29 |
| 2 | 38 |
| 1 | 35 |

By shot size (average rating): close 3.50, insert 3.42, POV 2.92, wide 2.73, medium 2.73.
The failures are concentrated in wides and crowds: the frames filled by place and people.

By method:
- Start frame (a still sets the first frame): 68% of takes rated 4 or 5. Without: 48%.
- Extensions of an approved take: average 3.70. Plain text plus elements (`omni_reference`): 3.02.
- Guide clip or location element present: no measurable difference on their own.
- S08 and S09 prompts with the `palette_sunset` image: average 2.33 (30 takes). Without it: 3.00
  (8 takes). Small sample, so this is a signal, not proof.

## What the 5s have in common (wides)

Frames read: S08 SH010 T03, S06 SH030 T04, S04 SH130 T03, S05 SH140 T03, S01 SH110 T02,
S04 SH030 T01, S07 SH080 T03, S02 SH030 T03.

1. **A real operator's position.** On a balcony, a rooftop, behind a man's back, through a window,
   low on a roadside. The camera is somewhere a person could stand with a camera, for a reason.
2. **Something in the foreground cuts the frame.** A building edge, a balcony, a shoulder, the backs
   of men, a window frame, a broken block. The subject sits behind it, in depth.
3. **Asymmetry.** Nothing important on the center line. Weight on one side, air on the other.
4. **Plain light.** Hazy, washed, the sky blown to cream. Warm, but not orange. Color comes from the
   place, not from a filter.
5. **The composition came from something already approved.** A start frame Leonard accepted
   (S08 SH010 T03, S07 SH080 T03, S03 SH050), or an extension of an approved take (S06 SH030 T04),
   or a frame from a take he liked used as the start (S04 SH090 T02).
6. **Few things, unevenly placed.** S05 SH110 T12 (4) won with scattered sheets, a few heads; T04 and
   T05 (1) failed with many sheets and gusts.

## What the 1s have in common (wides)

Frames read: S09 SH040 T01, S08 SH040 T01, S06 SH060 T01, S07 SH080 T01, S05 SH110 T05,
S08 SH010 T02, S09 SH050 T04, S09 SH110 T02.

1. **The camera stands square to the space.** Facades parallel to the frame, eye level, a centered
   vanishing point. It looks like a stage or a game level. Leonard's words: "toy render",
   "looks like an animatic", "videogame", "AI composition".
2. **People and objects spread evenly.** Rows, grids, clones, everyone doing the same thing.
   Leonard's words: "mannequins", "muppets", "like boxes", "they all act the same", "posing".
3. **Saturated orange.** Sunset turned up to a filter. Leonard on S09 SH050 T04: "light too orange,
   too fake, must feel more organic, more like 35mm film".
4. **The place copied from the wrong source.** `loc_square` (62815a4f) is the street-light corner with
   traffic lights and towers; every take that used it got that corner, whatever the prompt said
   (S09 SH040 T02 and T03, S09 SH050 T01, S09 SH110 T01). Guide clips of a place come out as 3D
   previz (S02 SH100 T01, S02 SH200 T01, S09 SH040 T01, S05 SH110 T01, S08 SH040 T01).
5. **Too many counted things.** "Thirteen bodies", "thirty sheets", "about fifty people":
   [inference] the model lays exact counts out evenly to satisfy them, which makes the grid.

## What I did wrong on S09 SH110

- **T01:** used `loc_square` without looking at the image, and did not check the S09 takes already on
  main. The take got the street-light corner, the opposite angle. Both mistakes are in the record
  (S09 SH050 T01 had the same cause one day earlier).
- **T01 and T02:** wrote the animatic composition literally ("the street runs straight away to a
  vanishing point"). The animatic is a blocking diagram: centered, square, one-point. Written as
  cinematography, it gives the AI composition of T02.
- **T01 and T02:** normal lens. `style.md` says wides here are long lens. I broke the bible.
- **Every take:** `palette_sunset` as an image, plus "warm orange and amber haze", "orange sunset sky".
  That is the orange filter look.
- **Every take:** thirteen bodies and thirty sheets, counted. Grid bodies in T02, paper that runs out
  in T03.
- **Method:** text-only for a frame filled by place, chosen as "cheapest". The README and `style.md`
  say such frames come from a photoreal start frame. Three text takes cost 36 credits; a start
  frame route costs about 15 and is the one that has produced the 5s.
- **Review:** I checked takes against my prompt's checklist (angle, car, people, signs) and called T02's
  angle a success. I never asked first whether the frame looks like a film still. T03 I rated
  "3 to 4" for the same reason.

## Rules I propose (Leonard decides; nothing changed in the bible yet)

1. **Wides and place-filled frames start from a still**: Leonard's pipeline (Midjourney) or a frame of
   an approved take. Text-only only for closes and inserts. Extensions of approved takes stay allowed.
2. **Before any wide:** pull the frames of every approved take of that place and direction, and pick the
   reference from those. Never send an element image without looking at what it shows.
3. **Composition in every wide prompt:** where the operator stands and why, one foreground element
   cutting the frame, the subject off center, long lens per `style.md`. Never "straight down the
   middle", never a centered vanishing point.
4. **No palette image for sunset.** Light in words: low hazy sun, washed sky, warm but not orange,
   color from the place.
5. **No counts above five for scattered things.** Name the two or three nearest ones in detail,
   then "others further off, unevenly". Few sheets of paper, not thirty.
6. **Review order:** first "would a DP have framed it this way?", then the checklist. If the first
   answer is no, it is a 1 or 2, whatever the checklist says.

## S09 SH110 next

The T03 frame (corner, flare, long lens) is the closest to a film frame. The route most likely to
work, by the numbers above: a start still (Leonard's pipeline over the T03 composition, or T03's
first frame as is), then a Seedance take that only adds the paper: a few sheets, skidding, uneven.
Cost to be quoted on request.
