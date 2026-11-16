# Animatic builder (draft 9)

Grey blockout of the shooting script: Cairo-style town, jointed figures, crowd simulation, ragdoll.
Local Blender (bpy) with the Workbench engine, no Higgsfield credits.

- Render: `python run2.py <out_dir> <shot ids>` (PREVIEW=1 renders 3 frames per shot). Shot ids come from
  `shots_sXX.py`; any shot without a function becomes a text card.
- Composite: `python3 comp.py <out_dir> <file.mp4>` (labels, subtitles above speakers, sound cues).
- PDF: `python3 pdf_build.py screenplay.fountain out.html`, then `node pdf_render.js out.html out.pdf`.
- Clean clips per shot for Seedance references: `python3 clips.py <out_dir> <faceless_dir> <dest>` (no labels, no subtitles).
- Needs: `pip install bpy==5.3.0 mujoco` (Python 3.13), libegl1 + mesa, ffmpeg, Pillow, Playwright for the PDF.

## Figures (v5)

- Characters who act (costumes with `style="shape"`: him, the fat man, his friend, the lady, Roger, the pilot,
  the S07 thrower, pullers and pipe man) are plain shapes: body, neck, head ball, one legs pill, a wedge for
  where the face points. In close shots (head over 30% of the frame height) the wedge becomes eye and mouth
  slits that blink and talk (`SHAPE_SLITS=0` renders without them, for Seedance references). Seedance invents
  the bodies and faces; the shapes give position, timing and facing.
- Ragdoll frames (falls, the hanging) and crowds stay detailed figures.
- Nothing goes under the floor: every frame is lifted above the ground or the sidewalk (0.15 m) under it, shapes
  lift themselves, and ragdoll contacts with the ground and curbs stop a joint instead of bouncing it.
  The runner prints `below` for each shot: the deepest dip found (0.0 = clean).

## Draft 9 additions
- Physics: falls, the haul, the hanging, the drop and every death run in MuJoCo (`mjdoll.py`, `phys.py`): a humanoid with
  anatomical joint limits (a hip cannot open more than about 45 degrees sideways, knees bend one way), real mass, muscle
  tone for a conscious body, limp for a dead one. Men who are shot drop where they are hit.
- The dead: one body map (`shots_s06.kills()`, `shots_s07.bodies_s07()`, `shots_s08.sniper_dead()`) feeds every later shot,
  so each body stays where it fell.
- Crowds: every person sets off at his own time, at his own speed that breathes a little, with his own stride and gait
  phase, and faces where he goes from the first frame.
- Shapes glide: no gait bob. The prompt describes how he walks; the animatic gives position and timing.
- Props held right: the briefcase hugged to the chest (`PR.chest`), the phone at the ear (`PR.at_ear`), the gun at the
  temple, the pipe in both hands at the shoulder.
- Depth of field and rack focus: a camera spec takes `focus` (a distance, a point, (actor, joint) or timed keys) and `fstop`.
