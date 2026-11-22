# Politician: Higgsfield elements

All made by Leonard inside the project "Talent Contest - Politician" (37733499-03c4-4405-8dee-fea3a2d3b96e).
Checked against the live element list 2026-11-22: 25 elements (prop_bar-weapon added 2026-11-19, char_bigger-guy, char_citizen1 and char_citizen2 2026-11-22); prop_helicopter's image is a64e5f09 (was 6c8efe25). Claude never creates elements.

Prompts use the element itself: `<<<element id>>>` in the prompt text, never its image job in `medias`
(Leonard, 2026-11-20). The backend attaches it as a reference element and names it `@<element name>`
(seen on seedance_2_5, job 28fc84db). Images that are not elements (`palette_*`) go in `medias` as
`image_references` and are named in words, never with an element name.

| Element | Element id | Image job id | Use |
|---|---|---|---|
| char_politician | 1d544095-f1c6-4865-8e97-e09dbadcabc7 | a7601ce4-95ee-410c-b6f1-2887359c73a9 | Old man A: S02 to S04, until he bounces off the fat person |
| char_politician_dusty | 1ecc0e0b-5c3c-4826-b0fd-361861a4b87b | 98e1e69e-c6a2-42c5-acbe-92a3607d484a | S04 after the fall, S05 until the rock |
| char_politician_blood | b3b677ef-3cd5-48d1-abe8-39552e40b573 | 0d0a5637-8109-4f72-b184-682b4a3bd534 | Old man B: S05 after the rock, S06, S07 until the pipe. Image replaced by Leonard 2026-11-18 13:30 (was 73236f58) |
| char_politician_final | f4279c8f-0cbb-407d-98b6-7c774a5f7603 | 547bbfa3-b1b2-441e-b704-ae87c835eaec | Old man C: S07 after the pipe, S09, S10. D = this plus the stain, in the prompt |
| char_big-guy | f5cc12be-ecbd-4a93-bf39-76debb61c908 | 6228445b-458a-498a-b4aa-88ba8d8ca3d5 | The fat person (S04, the pipe in S07, S09). To be replaced by char_bigger-guy (Leonard, 2026-11-22) |
| char_bigger-guy | 4017a781-5a07-4f87-929d-578380c83bbd | 1d925d6b-c418-4dc3-ba34-dc35200d5863 | The fat person from now on (Leonard, 2026-11-22): heavy-set, long dark curly hair, full beard, sweat-stained tan t-shirt with a chest pocket, brown work trousers, boots. Replaces char_big-guy in S04, S07 and S09 for new takes. Registered 2026-11-22 |
| char_citizen1 | 6f316a04-6a34-4945-a238-13c5c0c5cb8a | e782c45a-c53e-4809-9a44-7f97cee673db | A townsman: heavy-set, dark curly hair, full beard, beige linen shirt, jeans. Use not set yet. Registered 2026-11-22 |
| char_citizen2 | ee520fc8-19c1-43f2-8520-c9aa86acfec7 | daa5d6b7-164a-428e-a20c-d358f0b46067 | A townsman: heavy-set, balding, thick moustache, beige shirt, dark trousers. Use not set yet. Registered 2026-11-22 |
| char_boss | 69d22ecb-f04a-419e-95bf-f50071d2fa89 | 7ef41962-b628-4da9-b376-d0ca1975659b | The business lady (S08 to S10) |
| char_sniper | 5f97e15f-91bf-446c-b457-aaf95231f22f | 8716ad9f-ce08-4d86-8aa3-b6dbf0e0c2e3 | Roger (S08) |
| prop_briefcase | 1f5eb35a-c180-4c28-a0ca-3b4ac49ec939 | 4bf36cb5-5acb-401b-bfd0-8dee52e64d25 | The briefcase, dark leather |
| prop_gun | 8c5ae0e6-7b29-4e4d-acd3-f3bf423254a0 | 24875e9a-80ba-4b38-b970-3aede1a48c1b | The PPK/S, black and worn (in prompts: a toy gun) |
| prop_bar-weapon | 37fe2cf2-2fec-431c-8a44-4a370e26e42b | 8d69a591-a811-4b07-9ef9-586a70f736ae | The fat person's pipe (S07 SH050 to SH080, S09): a rusty iron pipe with a raised collar at each end, the size of a baseball bat (about 80 cm long, as thick as a wrist), swung with both hands. Added by Leonard, registered 2026-11-19 |
| prop_wobblehead | 79dc8b10-0969-4c09-b152-f1bfd0a92490 | fa19c43f-6118-4229-b27e-9094c0351770 | The bobblehead (S02, S10) |
| prop_rifle | 1ba45df5-3781-4aa4-a647-2fa4a63af43c | bb9db39b-9cde-4f92-af18-92d3c3dd74c3 | Roger's rifle (S08) |
| prop_car | 4fb2b9be-e3bf-4122-be00-0c098818122e | 42787b78-4682-4c84-953a-f89d853f105d | His car, outside (S02, S03, S10) |
| prop_instrument-cluster | 3befe9ae-a3a2-4a51-be69-06976021afa8 | 4025ee1a-fb17-4220-9842-2967dc102054 | Fuel needle on E (S02 SH170, S03 SH040) |
| prop_helicopter | 7a86dade-e435-46ab-95bd-80a76b1e0900 | a64e5f09-22a5-499f-9aa1-1420d05761c9 | Matte black Black Hawk (S08 to S10). A gunner sits in the door: the prompt says the door is empty or Roger's |
| loc_car-interior | efd956ba-f03a-4095-afc7-f2ce3aa2d086 | 60a2aec8-3fc7-49b7-b030-3eacbe274b77 | His car, inside (S02, S03, S10). Palms through the windshield: the prompt names the towers |
| loc_heli-cabin | 50fe3f54-266f-45e8-87c0-fe2907640931 | 75f579e3-8496-4bdf-aaf4-82329a0b01eb | Black Hawk cabin, bare military (S08) |
| loc_town-edge | 3ecccf45-3aa3-4ac3-82fe-81297889d6fa | 146470dd-64ff-4cd6-b7b6-235135167b1f | Town edge (S02). Leonard's image |
| loc_main-street | 99fe3ded-411a-4a82-bdb3-92d799254b00 | c30451ef-fa25-4482-9271-98223db4b72e | Main street (S03), street rules |
| loc_crossroads | 3b11ad9c-3f1b-4c72-aabe-50bb764e8032 | a5b52222-2225-4a38-8faa-9946e3115f5a | Crossroads (S03 SH050, S10), street rules |
| loc_side-street | 8787643a-a3b4-479e-854b-9a2f8808c092 | e728a9ae-4623-423a-b70a-2537058db407 | Side streets (S04, S05). Leonard's image |
| loc_square | 4eff3268-fe4a-489e-bc82-23fc6969f9a3 | 62815a4f-296f-4467-8d4a-62d56c348066 | The square, the hanging lamp at the corner (S05 SH140 to S09), street rules |
