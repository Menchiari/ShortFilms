# Reference clips, draft 11

One clean clip per 3D shot of animatic d11 (`<SCENE>_<SHOT>.mp4`, 24 fps, 1120x480): no labels, no subtitles, no faces
(close shots rendered with `SHAPE_SLITS=0`). Text-card shots have no clip. Shot ids follow draft 11 (no renumbering:
S04 SH135 and S06 SH025 (renumbered SH026 on 2026-11-22) are new; S05 SH040 to SH060 and SH100 are cut; S08 SH030 is now a 3D shot).

Use: the prompt names each clip and its one job ("a motion diagram only: the camera angle and the timing and paths of
the people"). Test S05 SH020 showed that a clip with the grey set gets copied as a fake 3D model: for crowd and fall
shots use the motion-only clip in `../refs_d11_motion/` (people on plain ground, no set), and describe the place in words.

S02 at 720p (REQUEST 016, 2026-11-17), corrected after a full-resolution check: every shot where the clip carried
architecture or ground came out as 3D previz, even with a real image of the place attached (SH010 towers and boxy rubble,
SH030 road and block, SH100 street, the towers in SH090's rear window). Shots where the clip carried only a subject held
photoreal (SH020 dog, SH070 briefcase, SH080 car). Rule: never give a set clip for a shot whose frame is filled by place;
the composition comes from a photoreal start frame made over the animatic frame (production plan, Keeping the vision 1-2),
or from words.

Method from REQUEST 018a (2026-11-17): the clip goes in as a line drawing, never as the render:
`ffmpeg -i in.mp4 -vf "format=gray,edgedetect=low=0.08:high=0.25,negate,format=yuv420p" out_lines.mp4`, with the prompt's
strict guide paragraph (take only camera position, movement, framing, rough positions, paths and timing). Both line and
blurred versions came out photographic on S02 SH100; the line version kept real detail, the blurred one turned edges into slabs.

Superseded 2026-11-19 (S05 SH110 T01 and T08 copied the box figures and the paper even as line drawings): no d11 clip goes
in as a video reference. Use: one frame of the clip, turned into a photoreal still with gpt_image_2_6 (every shape named
as a real thing), as the start frame (S05 SH110 T09, `05-generation/frames/001_S05_SH110_T09_start_gpt.txt`).
