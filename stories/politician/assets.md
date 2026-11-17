# Politician: every asset, in the order to make them

Status 2026-11-17 (all elements made), checked against screenplay draft 10 (98 shots) and the live Higgsfield element list.
Leonard makes the images inside the Higgsfield project "Talent Contest - Politician" (anything made outside
it is void for the contest). Claude registers each one as an element after Leonard's OK.
Locations: 21:9, empty, the afternoon palette image (`look/palette_ref_1_afternoon.jpg`) for color and light
only; helicopter: the sunset one. Props: plain light grey background. One view per image.

## Done (elements live, ids in `elements.md`)

Old man A, dusty, blood, final (D = final plus the stain, written in the prompt), the fat person (also the
man with the pipe since draft 9), the business lady, Roger, the briefcase, the gun, the bobblehead. The bond
(`props/bond/`, a file, composited).

## Missing: you make (shooting order; the main street first, as the master every location takes as reference)

| # | Asset | Shots it unlocks | Prompt | Status |
|---|---|---|---|---|
| 1 | Main street (master frame) | S03 SH010 to SH030, the look of every town shot | M1 | done: loc_main-street `a85235c7` |
| 2 | Town edge: towers like a wall, one gap | S02, 10 shots | M2 | done: loc_town-edge `86326c41` |
| 3 | His car, outside | S02, S03, S10 | M3 | done: prop_car `4fb2b9be-e3bf-4122-be00-0c098818122e` (Leonard's edit) |
| 4 | His car, inside | S02 inserts and POVs, S03 SH020, S10 | M4 | done: loc_car-interior `61e6cb72` (palms through the windshield) |
| 5 | Instrument cluster (one still) | S02 SH170, S03 SH040 (the same fuel symbol) | M5 | done: prop_instrument-cluster `b5c349f4` |
| 6 | Crossroads | S03 SH050, S10 | paint over `crossroads/setup_01_est_high.jpg` with #1 as reference | done: loc_crossroads `2ed7ddd7` |
| 7 | Side streets | S04 (15 shots), S05 SH010 to SH130 (9) | M6 | done: loc_side-streets `4cca367a` |
| 8 | The square, street light corner | S05 SH140, S06, S07, S08 POVs, S09: 32 shots | M7 | done: loc_square `628fa32c` |
| 9 | Helicopter, outside | S08 SH010, S09, S10 | M8 | done: prop_helicopter `72463ac3` (black Black Hawk) |
| 10 | Helicopter cabin | S08 SH020, SH050, SH060 | M9 | done: loc_heli-cabin `b10298b3` (bare military) |

Optional:

| Asset | Shots | Note |
|---|---|---|
| Rifle | S08 SH020, SH050 | done: prop_rifle `1ba45df5-3781-4aa4-a647-2fa4a63af43c` |
| The friend | S04 SH100 (seen), SH140 (voice) | one visible shot: text is enough. Prompt in `references-monday.md` section 6 |

Not needed any more: the man with the pipe (he is the fat person), the reporter (S01 SH120 T01 exists from
text). From text, no element: the dog, the policeman, the child, the old woman, the three men at the bar, the
pilot, the crowds, the rope, the pipe.

Open: the screenplay says the gun is nickel (S06 SH010); the prop_gun element is black and worn. One of the
two changes. I don't know which you want.

## I make (no credits)

| Asset | Status |
|---|---|
| S01 signs, billboard, TV news | made from char_politician in the prompts; composites only if a take fails |
| Phone screen, scope overlay, the Agreement | can start |

## Prompts (draft 10: dusty asphalt, towers, no laundry)

### M1. Main street (master)

```
The main street of a dry, dusty modern town where the outskirts of a city meet the desert: tall plain concrete apartment towers on both sides, balconies closed in with corrugated plastic, satellite dishes, air-conditioner units, rolled-down metal shutters, faded and stained plaster, power cables across the street, asphalt buried in dust and drifted sand. The part of a city people are afraid of. Unplaceable. The sun from the left of frame, mid-afternoon, shadows falling across the street to the right. No laundry, no trees, no palms, no greenery, no people, no cars, no readable signs. Hazy afternoon, warm ochre and brown palette, dust in the air, deep brown shadows, 35mm film photograph, anamorphic framing. Documentary realism, not CGI.
```

### M2. Town edge (image refs: `look/mood/mood_4_town-edge.webp` for composition, #1 for architecture)

```
Extreme wide shot from a road across flat desert toward the edge of a dry, dusty modern town. Tall plain concrete apartment towers stand shoulder to shoulder like a wall, running to the horizon on both sides. One single gap between two towers: the road runs straight into it and becomes a long street that runs deep into the town. The road is asphalt buried in dust and drifted sand. On both sides of the road, broken ground, a deep dry ditch and rubble that no car could cross. In the near foreground, an abandoned building with a crumbled concrete wall. Heat shimmer over the road, the sun on the rooftops. No laundry, no trees, no palms, no greenery, no people, no cars, no animals, no readable signs. Hazy afternoon, warm ochre and brown palette, dust in the air, deep brown shadows, 35mm film photograph, anamorphic framing.
```

### M3. His car, outside

```
A black full-size luxury sedan, modern, no badges or logos, covered in desert dust, three-quarter front view, standing on a road of asphalt buried in dust and drifted sand, flat hazy desert behind it. No people. Hazy afternoon light, 35mm film photograph.
```

### M4. His car, inside

```
The interior of the same black luxury sedan seen from the back seat: dusty leather seats, a dusty dashboard, the windshield showing a road of dusty asphalt running toward a wall of tall concrete towers. No people, no objects on the dashboard or the seats. Hazy afternoon light, 35mm film photograph.
```

### M5. Instrument cluster

```
Close-up of the instrument cluster of the same black luxury sedan, straight on: the fuel gauge needle resting on the edge of E, beside a fuel pump symbol, the low fuel warning light off, the speedometer at zero. A thin layer of dust on the glass. Soft daylight through the windshield, 35mm film photograph.
```

### M6. Side streets

```
A narrow side street in the same dry, dusty town, eye level. Doorways, one with a bead curtain; a ground-floor window with a television glowing inside; a small bar with an awning and plastic chairs against the wall; balconies and windows above; tangled cables overhead; shutters down; a corner ahead where the street turns. Asphalt buried in dust. Unwelcoming and anonymous. No laundry, no trees, no plants, no people, no readable signs. Hazy afternoon, warm ochre and brown palette, deep brown shadows, dust in the air, 35mm film photograph, anamorphic framing.
```

### M7. The square

```
A wide, empty square in the same dry, dusty town, seen from one corner at eye level. Tall plain concrete apartment towers on all sides, shutters down, faded shop fronts, power cables. Several streets open into it. In the near corner, where a narrow street meets the square, one tall old street light on a steel pole with a long horizontal arm, beside a sidewalk with a high curb, and a concrete wall a few steps behind it. Asphalt buried in dust and sand, rubble at the edges, open space in the middle big enough to land a helicopter. No laundry, no trees, no palms, no greenery, no people, no cars, no readable signs. Hazy afternoon, warm ochre and brown palette, dust in the air, deep brown shadows, 35mm film photograph, anamorphic framing.
```

### M8. Helicopter, outside

```
A glossy white Airbus ACH160 private helicopter, no logos or markings, its right sliding cabin door open, in flight above a dusty town of tall concrete towers, seen from the side and slightly below with a long lens. Orange sunset haze, smoke on the horizon, 35mm film photograph.
```

### M9. Helicopter cabin

```
The cabin of a white Airbus ACH160 VIP helicopter, seen from the rear of the cabin looking forward: cream leather seats, the right sliding door open with sunset light pouring in, the cockpit beyond with two front seats, the town far below through the open door. No people. Sunset, 35mm film photograph.
```
