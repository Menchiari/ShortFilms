# Politician: Higgsfield elements

Elements by Leonard, created inside the project. The rows marked "Claude, 2026-11-17" are workspace elements made with Claude's tool, outside the project: void for the contest (Leonard, 2026-11-17), never used in prompts. Leonard is redoing them in the project; their new ids replace these rows. Written into prompts as `<<<id>>>`.

| Element | Id | Use |
|---|---|---|
| char_politician | 1d544095-f1c6-4865-8e97-e09dbadcabc7 | Old man. State: I don't know which (A or the dusty one) |
| char_politician_dusty | 1ecc0e0b-5c3c-4826-b0fd-361861a4b87b | Old man, dusty, no blood. State: I don't know which |
| char_politician_blood | b3b677ef-3cd5-48d1-abe8-39552e40b573 | Old man B: the cut at the hairline. [ASSUMPTION] |
| char_politician_final | f4279c8f-0cbb-407d-98b6-7c774a5f7603 | Old man C: most beaten, jacket torn. D = this plus the stain, written in the prompt. [ASSUMPTION] |
| char_big-guy | f5cc12be-ecbd-4a93-bf39-76debb61c908 | The fat person (S04, the pipe in S07, S09) |
| char_boss | 69d22ecb-f04a-419e-95bf-f50071d2fa89 | The business lady (S08, S09) |
| char_sniper | 5f97e15f-91bf-446c-b457-aaf95231f22f | Roger (S08) |
| prop_briefcase | 1f5eb35a-c180-4c28-a0ca-3b4ac49ec939 | The briefcase |
| prop_gun | 8c5ae0e6-7b29-4e4d-acd3-f3bf423254a0 | The gun (in prompts: a toy gun) |
| prop_wobblehead | 79dc8b10-0969-4c09-b152-f1bfd0a92490 | The bobblehead |
| prop_rifle | 1ba45df5-3781-4aa4-a647-2fa4a63af43c | Roger's rifle (S08). Leonard, 2026-11-17 |
| prop_car | 4fb2b9be-e3bf-4122-be00-0c098818122e | His car, outside (S02, S03, S10). Leonard's edit of prop_car_v1, 2026-11-17 |
| loc_main-street | a85235c7-5f3d-4552-8e77-2045cc719e91 | The main street (S03), master look of the town. Claude, 2026-11-17 |
| loc_town-edge | 86326c41-a762-42a4-8059-8d1b3a7dd88f | Town edge, towers like a wall, one gap (S02). Claude, 2026-11-17 |
| loc_side-streets | 4cca367a-be65-4e17-892e-9e828e8b9741 | Side streets (S04, S05). Claude, 2026-11-17 |
| loc_square | 628fa32c-ba3c-4159-b4d7-d14cde18e151 | The square, street light corner (S05 SH140 to S09). Claude, 2026-11-17 |
| loc_crossroads | 2ed7ddd7-b755-4062-ab3f-5aead6e34a2a | The crossroads (S03 SH050, S10). Claude, 2026-11-17 |
| loc_car-interior | 61e6cb72-0285-4965-ab03-78c7d6de3a39 | His car, inside (S02, S03, S10). Palms through the windshield: name the towers in the prompt. Claude, 2026-11-17 |
| prop_instrument-cluster | b5c349f4-d0e1-4b0b-9973-e840e486d97e | Fuel needle on E (S02 SH170, S03 SH040). Claude, 2026-11-17 |
| prop_helicopter | 72463ac3-1c0e-4e49-b5c3-b39fbfd7e7d3 | Matte black Black Hawk, unmarked (S08, S09, S10). A gunner sits in the door: say the door is empty or Roger's. Claude, 2026-11-17 |
| loc_heli-cabin | b10298b3-ada9-4bfb-8d93-edde78d3aaa5 | Black Hawk cabin, bare military (S08). Claude, 2026-11-17 |

Higgsfield project: "Talent Contest - Politician" (37733499-03c4-4405-8dee-fea3a2d3b96e).

Seedance 2.5 does not resolve `<<<id>>>` placeholders. Pass the element's image instead, in `medias` as
`image_references`:

| Element | Image job id |
|---|---|
| char_politician | a7601ce4-95ee-410c-b6f1-2887359c73a9 |
| char_politician_dusty | 98e1e69e-c6a2-42c5-acbe-92a3607d484a |
| char_politician_blood | 73236f58-4093-48bf-a4fc-88f05e189556 |
| char_politician_final | 547bbfa3-b1b2-441e-b704-ae87c835eaec |
| char_big-guy | 6228445b-458a-498a-b4aa-88ba8d8ca3d5 |
| char_boss | 7ef41962-b628-4da9-b376-d0ca1975659b |
| char_sniper | 8716ad9f-ce08-4d86-8aa3-b6dbf0e0c2e3 |
| prop_briefcase | 4bf36cb5-5acb-401b-bfd0-8dee52e64d25 |
| prop_gun | 24875e9a-80ba-4b38-b970-3aede1a48c1b |
| prop_wobblehead | fa19c43f-6118-4229-b27e-9094c0351770 |
| prop_rifle | bb9db39b-9cde-4f92-af18-92d3c3dd74c3 |
| prop_car | 42787b78-4682-4c84-953a-f89d853f105d |
| loc_main-street | c758e4e6-4cc6-4871-af3e-83c39a46940c |
| loc_town-edge | b73a0ba3-7e16-4543-acb1-af56f2de2d16 |
| loc_side-streets | 06709193-ec74-4f64-83b3-e65b715ad8a5 |
| loc_square | ad9c994a-8fb1-4a4c-a67d-6453e164eb64 |
| loc_crossroads | 94ac5651-d88d-460b-b8d8-ca4a6b2ce1e4 |
| loc_car-interior | 60a2aec8-3fc7-49b7-b030-3eacbe274b77 |
| prop_instrument-cluster | 4025ee1a-fb17-4220-9842-2967dc102054 |
| prop_helicopter | 6c8efe25-fd49-4797-a086-047c9c7ca372 |
| loc_heli-cabin | 75f579e3-8496-4bdf-aaf4-82329a0b01eb |
