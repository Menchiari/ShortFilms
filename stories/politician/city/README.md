# City building (film 001)

Goal: one consistent town that every scene's shots draw from. No credits spent. Waiting for Leonard to say
what this branch builds.

## What exists

- Location elements (`elements.md`): loc_town-edge, loc_main-street, loc_crossroads, loc_side-street, loc_square.
  Local copies read: `refs/locations/*_v2|v3.jpg` [ASSUMPTION: the newest local versions are the element images].
- `animatic/src/sets.py`: four separate sets with exact coordinates (+x east, sun in the west). Each set has its
  own origin: they are not joined into one map.
- `crossroads/`: Higgsfield 3D blockout, 12 setups, predates draft 8 (9 of the 12 setups were for the chase,
  now in the square).

## Contradictions found

1. **Car heading.** Crossroads README: car faces north. sets.py: the car dies facing west. One must go.
2. **No town map.** Distance and direction from the crossroads to the square are undefined; S10 SH010 T03 had to
   assume the square lies ahead of the car, toward the sun.
3. **Scale.** Town edge: a wall of 20 to 30 storey towers. Main street, crossroads, side streets, square: 5 to 8
   storey blocks. Workable (the towers are the rim, the inside is lower) but no document says so.
4. **Square.** loc_square v3 is a road junction with traffic lights, not a paved open space big enough for a
   helicopter (the M7 prompt and sets.py). v2 is the open space. Takes drift (S09 SH050 T06: wide ruined plaza).
5. **Side street.** Older plaster and a bar with an awning: reads more Mediterranean old town than the
   concrete blocks of the other four.
6. **Sun.** Town edge and square: backlit, sun straight ahead. Crossroads: sun behind and right of camera.
   With one map, the sun side follows from each camera heading.

## Open question for Leonard

What should "city building" produce? Recommendation below.
