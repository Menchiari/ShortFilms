# Politician: every asset, in the order to make them

Status 2026-11-17, checked against screenplay draft 10 (98 shots) and the live Higgsfield element list.
Images: made inside the Higgsfield project "Talent Contest - Politician" (anything made outside it is void for the
contest). Elements: Leonard creates them inside the project. Claude never creates elements: its tool makes
workspace elements outside the project, which are void (Leonard, 2026-11-17).
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

## Street rules (Leonard, 2026-11-17: "people know street rules more than their mothers")

Every location is a real modern street that a local would find nothing wrong with. Put in every location prompt:

- Curbs and raised sidewalks on both sides of every road.
- Lamp posts on the sidewalk edge, one identical model, evenly spaced (about 30 m), arms over the road. Never
  placed for the composition. In narrow streets: lamps on wall brackets.
- Road markings: lane lines, stop lines, zebra crossings at every junction. Worn and half buried in dust, still there.
- Every junction: traffic lights on poles at the corners, facing each approach; crossings on every arm; curb ramps.
- Traffic signs on poles: shapes and colors only, no readable text.
- [PROPOSED] Dusty cars parked along the curbs, away from the junctions. The town is not abandoned: people hide indoors.

## Prompts (draft 10: dusty asphalt, towers, no laundry, street rules)

### M1. Main street (master) v2

```
The main street of a dry, dusty modern town where the outskirts of a city meet the desert, eye level from the middle of the road: four lanes with worn white lane lines half buried in dust and drifted sand, raised sidewalks and curbs on both sides, identical street lamps on the sidewalk edges evenly spaced about thirty meters apart with their arms over the road, a junction ahead with traffic lights on poles at its corners and a faded zebra crossing, traffic signs on poles with no readable text, a few dusty cars parked along the curbs. Tall plain concrete apartment towers on both sides, balconies closed in with corrugated plastic, satellite dishes, air-conditioner units, rolled-down metal shutters, faded and stained plaster. Unplaceable. The sun from the left of frame, mid-afternoon. A real street a local would find nothing wrong with. No laundry, no trees, no palms, no greenery, no people. Hazy afternoon, warm ochre and brown palette, dust in the air, deep brown shadows, 35mm film photograph, anamorphic framing. Documentary realism, not CGI.
```

### M2. Town edge v2 (image refs: `look/mood/mood_4_town-edge.webp` for composition, #1 for architecture)

```
Extreme wide shot from a road across flat desert toward the edge of a dry, dusty modern town. Tall plain concrete apartment towers stand shoulder to shoulder like a wall, running to the horizon on both sides. One single gap between two towers: the road runs straight into it and becomes the main street. The road is two-lane asphalt with a worn center line and edge lines half buried in dust and drifted sand; a row of identical street lamps evenly spaced along one side starts a few hundred meters before the towers; road signs on poles with no readable text. On both sides of the road, broken ground, a deep dry ditch and rubble that no car could cross. In the near foreground, an abandoned building with a crumbled concrete wall. Heat shimmer over the road, the sun on the rooftops. No laundry, no trees, no palms, no greenery, no people, no moving cars, no animals. Hazy afternoon, warm ochre and brown palette, dust in the air, deep brown shadows, 35mm film photograph, anamorphic framing.
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

### M6. Side streets v2

```
A narrow one-way side street in the same dry, dusty town, eye level. Raised sidewalks with curbs on both sides, dusty cars parked half on the sidewalk, street lamps on wall brackets at regular intervals, a no-entry sign on a pole with no readable text. Doorways, one with a bead curtain; a ground-floor window with a television glowing inside; a small bar with an awning and plastic chairs on the sidewalk; balconies and windows above; tangled cables overhead; shutters down; a junction ahead with a faded zebra crossing where the street meets another. Asphalt buried in dust. Unwelcoming and anonymous. A real street a local would find nothing wrong with. No laundry, no trees, no plants, no people. Hazy afternoon, warm ochre and brown palette, deep brown shadows, dust in the air, 35mm film photograph, anamorphic framing.
```

### M7. The square v2

```
A wide square in the same dry, dusty town, seen from one corner at eye level. A paved open space in the middle, big enough to land a helicopter, ringed by a road with worn lane markings, curbs and raised sidewalks. Identical street lamps evenly spaced along the sidewalk edge all around the square, arms over the road. In the near corner, where a narrow street enters the square, traffic lights on poles, a faded zebra crossing, and one of those street lamps standing on the curb beside the sidewalk, its long arm over the road, a concrete wall a few steps behind it. Tall plain concrete apartment towers on all sides, shutters down, faded shop fronts, power cables, traffic signs on poles with no readable text, a few dusty cars parked along the curbs. Rubble at the edges. A real square a local would find nothing wrong with. No laundry, no trees, no palms, no greenery, no people. Hazy afternoon, warm ochre and brown palette, dust in the air, deep brown shadows, 35mm film photograph, anamorphic framing.
```

### M10. Crossroads v2 (image ref: `crossroads/setup_01_est_high.jpg` for the camera and the street layout only, not its lamp posts)

```
A high view from a fourth-floor balcony over a large four-way crossroads in a dry, dusty modern town: two four-lane streets crossing, worn lane lines, stop lines and zebra crossings on all four arms, half buried in dust and drifted sand; traffic lights on poles at all four corners facing each approach; raised sidewalks with curbs and ramps; identical street lamps evenly spaced along every sidewalk edge, arms over the road; traffic signs on poles with no readable text; a few dusty cars parked along the curbs away from the junction. One black luxury sedan stands alone in the middle of the junction, facing away from the camera. Tall plain concrete apartment towers on all corners, balconies closed in with corrugated plastic, satellite dishes, shutters down, power cables. A real junction a local would find nothing wrong with. No laundry, no people, no trees, no greenery. Hazy afternoon, warm ochre and brown palette, long soft shadows, dust in the air, 35mm film photograph, anamorphic framing.
```

### M8. Helicopter, outside

```
A glossy white Airbus ACH160 private helicopter, no logos or markings, its right sliding cabin door open, in flight above a dusty town of tall concrete towers, seen from the side and slightly below with a long lens. Orange sunset haze, smoke on the horizon, 35mm film photograph.
```

### M9. Helicopter cabin

```
The cabin of a white Airbus ACH160 VIP helicopter, seen from the rear of the cabin looking forward: cream leather seats, the right sliding door open with sunset light pouring in, the cockpit beyond with two front seats, the town far below through the open door. No people. Sunset, 35mm film photograph.
```
