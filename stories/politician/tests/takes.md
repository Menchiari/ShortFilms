# Politician: test takes

Model seedance_2_5, mode omni_reference, 480p, 21:9, audio on, draft on. Project "Talent Contest - Politician".
Approved in chat 2026-11-16 (78 credits).

| Take | Job id | Duration | Credits | Refs | Prompt | Folder | Rating |
|---|---|---|---|---|---|---|---|
| S09 SH010 T01 | d46b01e3-c244-4f50-9504-3c2123cacadf | 18 s | 54 | char_big-guy, char_politician_final, sunset palette | S09_SH010_T01_prompt.txt | Scenes/S09/SH010 (ce52aac5-c927-4805-a7e5-d5eb78bb051f) | Blocked: nsfw, "Output may contain sensitive content". 54 refunded 22:28 |
| S05 SH020 T01 | 50fb4003-105a-480b-b0f7-56dfdc8585ec | 4 s | 12 | animatic d9 clip (video ref), afternoon palette | S05_SH020_T01_prompt.txt | Scenes/S05/SH020 (d4ab191c-4c76-427f-a8b6-2c47f8f6ba04, moved 2026-11-19 from duplicate 4cc020fe) | Completed: politician_S05_SH020_T01.mp4, 992x432, 24 fps |
| S06 SH060 T01 | 8e7f71fb-db97-4884-9388-a7261c267338 | 4 s | 12 | char_politician_blood, afternoon palette | S06_SH060_T01_prompt.txt | Scenes/S06/SH060 (3bb5a842-039d-44ad-b40c-73d57cf69bc2, moved 2026-11-19 from duplicate 32439b6b) | Blocked: nsfw, "Something went wrong". 12 refunded 22:46 |

Uploaded refs: sunset palette 1f563179-51a7-4e02-bcac-0affdd52a903, afternoon palette 3bf30eee-4c0b-4823-bb61-73c8015ce55a,
S09 SH010 animatic f831ff0a-c0a5-45b4-991d-7eae53293cca (not used), S05 SH020 animatic 449a7c8b-aac7-452f-b62a-72517f06eeb7.

Net spend: 12 credits (S09 and S06 blocked and refunded). Both blocked takes carry an old man element with blood on the face; the passed take has no element.

## Round 2 (approved 2026-11-16, 24 credits at most)

| Take | Job id | Duration | Credits | Refs | Prompt | Folder | Result |
|---|---|---|---|---|---|---|---|
| FILTER blood element | dcee6e93-f991-42d2-a49d-a71415236e6f | 4 s | 12 | char_politician_blood image (73236f58) as image_references | FILTER_blood_element_prompt.txt | TESTS (8ccc6c44-5206-40c6-bff5-c6b00a33ede4) | Completed after 66 min in the queue: politician_FILTER_blood_T01.mp4. Passed the filter, identity holds, but the blood is almost gone (a faint mark at the right temple). The blood image is not what blocked S09 and S06: their text was |
| S05 SH020 T02 | 0b6ce512-f385-4397-9d14-3ec7ae117e80 | 4 s | 12 | motion-only clip (d0c8119e), afternoon palette | S05_SH020_T02_prompt.txt | Scenes/S05/SH020 | Completed: politician_S05_SH020_T02.mp4. Reads as real drone footage: the motion-only clip carries the crowd's motion without the set |

Finding: with seedance_2_5 the `<<<element_id>>>` placeholder is NOT injected (the backend received the raw text and no
image; first FILTER submission rejected with "omni_reference requires at least one reference media item", no charge).
S09 SH010 T01 and S06 SH060 T01 therefore ran with no character images. For seedance_2_5 the element's image job id goes
in `medias` as `image_references` (ids in ../elements.md), and the prompt names it as "the reference image of ...".
