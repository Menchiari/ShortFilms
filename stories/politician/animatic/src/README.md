# Animatic builder (draft 8)

Grey blockout of the shooting script: Cairo-style town, jointed figures, crowd simulation, ragdoll.
Local Blender (bpy) with the Workbench engine, no Higgsfield credits.

- Render: `python run2.py <out_dir> <shot ids>` (PREVIEW=1 renders 3 frames per shot). Shot ids come from
  `shots_sXX.py`; any shot without a function becomes a text card.
- Composite: `python3 comp.py <out_dir> <file.mp4>` (labels, subtitles above speakers, sound cues).
- PDF: `python3 pdf_build.py screenplay.fountain out.html`, then `node pdf_render.js out.html out.pdf`.
- Needs: `pip install bpy==5.3.0` (Python 3.13), libegl1 + mesa, ffmpeg, Pillow, Playwright for the PDF.
