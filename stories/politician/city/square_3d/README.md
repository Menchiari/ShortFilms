# The square: 3D blockout (from Leonard's frame, 2026-11-20)

Master frame: `../square_leonard_v1.webp` (Leonard). JPEG copy uploaded to Higgsfield: media 058651a0-6ac5-4a47-9612-b6db37c03d18.
3D scene (hosted, free): https://higgsfield.ai/3d-jutsu/67aff3d7-7e28-46e8-ac18-0ce2bd807485 (revision 5).

## Layout (metres, +x east, +y north, same axes as `animatic/src/sets.py`)

- Paved plaza x -36..36, y -24..24; ring road to x +-43.5, y +-31.5; sidewalks 4 m; blocks of 6 to 10 floors.
- West street: middle of the west side (|y| < 7), toward the sun. He comes out of it (sets.py).
- North-east street: continues the north side of the square (y 17.5..31.5) [read from Leonard's frame].
- The crossroads with his car: down the west street, x -215..-200 (d11 `shots_s09.far_city`, seen in S09 SH110).
  The street runs to x -436 and ends at a row of blocks. Conflict: S10 SH010 T03 assumed the square lies toward the
  sun from the car; d11 puts it east of the car (away from the sun).
- Hero street lamp: south-west corner, (-44, -8.5), as sets.py.
- Lamps: one model, every 12 m along the outer sidewalks (Leonard's frame is denser than the 30 m street rule).
- Sun: low in the west, a little north (Leonard's frame: sun ahead, right of centre, camera looking west).
- CAM_00_source: Leonard's frame, from the north-east street mouth (60, 26, 1.6 m), 22 mm, looking 8 degrees south
  of west. Approximate fit: the corner lamp sits a little right of where it is in his frame.

## Tour cameras (one second each in the tour)

| s | Camera | What it shows |
|---|---|---|
| 0 | CAM_00_source | Leonard's frame |
| 1 | CAM_01_reverse_from_west_street | the reverse, sun behind, toward the car's street |
| 2 | CAM_02_hero_lamp_low | the hero lamp from the ground (S07 hanging) |
| 3 | CAM_03_high_balcony_north | 4th floor, north side, down on the square (S07 SH010) |
| 4 | CAM_04_plaza_center_south | centre of the square, looking south (landing area) |
| 5 | CAM_05_south_side_long_lens | south sidewalk, long lens, north side flat (S06 profile shots) |
| 6 | CAM_06_hero_corner_to_west_street | toward the west street mouth (S05 SH140 entrance). Framing blocked by a block: to fix |
| 7 | CAM_07_top_down | straight down, north up (S08 aerial) |

Files: `cam00..07.jpg`, `contact_sheet.jpg`, `square_blockout_tour_v1.mp4` (cuts every second), `square_blockout_tour_v2_continuous.mp4` (Leonard 2026-11-20: no cuts. One continuous camera, one second per move, linear, no easing; camera CAM_TOUR_continuous, 3D revision 6).
Seedance tour prompt: `prompt_square_tour_v2_continuous.txt` (v1 with cuts replaced). Not generated: waiting for approval.

## Conflict found

The S09 prompts (for example `05-generation/prompts/001_S09_SH050_T06_v2.txt`) describe the square as three to five
floors, close and low, never a wide avenue, no parked cars, no traffic lights. Leonard's frame: six to ten floors,
wide, parked cars. One of them changes.

## S09 tour, after SH020 (Leonard 2026-11-20: only the shots needed after S09 SH020, a 1 s pause between moves)

Camera `CAM_TOUR_S09_holds` (3D revision 10): hold 1 s, move 1 s, linear. Positions from d11 `animatic/src/shots_s09.py`.
Blocking proxies (helicopter at PAD, her, him, the case) in collection `BLOCKING_S09`, hidden in the tour render.

| s | Hold on | Shots |
|---|---|---|
| 0-1 | Leonard's frame | start |
| 2-3 | wide from the north side, looking south over the west half | SH040 |
| 4-5 | eye level looking west, the west street behind him | SH050 |
| 6-7 | tighter, same axis | SH090 |
| 8-9 | her POV down the west street | SH110 |
| 10-11 | reverse, looking east, the helicopter's place behind her | SH060, SH080, SH100, SH120 |

Inserts SH030 and SH070 need no place. Blockout: `square_blockout_tour_v5_s09_holds.mp4` (v3 and v4: the west street
was blocked by a background tower and by the proxies). Prompt: `prompt_square_tour_v3_s09.txt`, 11 s.

## S09 tour, no repeats (Leonard 2026-11-20: start with the reference frame, do not repeat shots)

Camera `CAM_TOUR_S09_v2` (3D revision 12). One hold per distinct view: SH050, SH090 and SH110 all look west at the
same street mouth, so they share one wide hold (SH050 and SH090 are crops of it). The first second of the blockout is
Leonard's reference frame itself.

| s | Hold on | Shots |
|---|---|---|
| 0-1 | Leonard's reference frame | start |
| 2-3 | wide from the north side, looking south over the west half | SH040 |
| 4-5 | eye level, wide, looking west down the west street | SH050, SH090, SH110 |
| 6-7 | reverse, looking east, the helicopter's place behind her | SH060, SH080, SH100, SH120 |

Blockout: `square_blockout_tour_v7_s09_norepeat.mp4` (v6: 9 s, still had two west views). Prompt:
`prompt_square_tour_v5_s09_norepeat.txt`, 7 s.

## Take T01 (2026-11-20)

`takes/001_city_square_tour_T01.mp4`: job 4043c429-d77b-4542-a77b-fc3cd5bd7acc, seedance_2_5 omni_reference, 7 s, 720p
(1470x630), 21:9, audio on, 49 credits, prompt `prompt_square_tour_v5_s09_norepeat.txt`, folder REFS/LOC_square. Unrated.
Claude's read: it opens on Leonard's frame, then the camera only drifts a few meters toward the corner building and
back. No new angle is reached: none of the SH040, west street or reverse holds happen. Words alone did not move the
camera across the square. Stills: `takes/001_city_square_tour_T01_*.jpg`.
