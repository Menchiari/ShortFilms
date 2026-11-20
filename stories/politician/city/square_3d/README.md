# The square: 3D blockout (from Leonard's frame, 2026-11-20)

Master frame: `../square_leonard_v1.webp` (Leonard). JPEG copy uploaded to Higgsfield: media 058651a0-6ac5-4a47-9612-b6db37c03d18.
3D scene (hosted, free): https://higgsfield.ai/3d-jutsu/67aff3d7-7e28-46e8-ac18-0ce2bd807485 (revision 5).

## Layout (metres, +x east, +y north, same axes as `animatic/src/sets.py`)

- Paved plaza x -36..36, y -24..24; ring road to x +-43.5, y +-31.5; sidewalks 4 m; blocks of 6 to 10 floors.
- West street: middle of the west side (|y| < 7), toward the sun. He comes out of it (sets.py).
- North-east street: continues the north side of the square (y 17.5..31.5), toward the crossroads and the car
  [ASSUMPTION: read from Leonard's frame, the road on the right runs straight along the north row].
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

Files: `cam00..07.jpg`, `contact_sheet.jpg`, `square_blockout_tour_v1.mp4` (free blockout tour, 8 s, cuts every second).
Seedance tour prompt: `prompt_square_tour_v1.txt` (start frame = Leonard's frame). Not generated: waiting for approval.

## Conflict found

The S09 prompts (for example `05-generation/prompts/001_S09_SH050_T06_v2.txt`) describe the square as three to five
floors, close and low, never a wide avenue, no parked cars, no traffic lights. Leonard's frame: six to ten floors,
wide, parked cars. One of them changes.
