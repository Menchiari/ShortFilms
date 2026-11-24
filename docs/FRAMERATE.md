# Framerate fixes

Status: first version. Your existing tools get merged in once you send them, this file and
`tools/media/fps.py` get refined around them.

## What goes wrong with AI clips

| Problem | What you see | How `fps.py` detects it |
|---|---|---|
| Duplicate frames | Micro freezes, stutter in otherwise smooth motion | `mpdecimate` counts frames identical to the previous one |
| Variable frame rate | Drift, audio sync slips in the edit | real frame rate differs from average frame rate |
| Wrong base rate | Judder on a 24 fps timeline (a 30 or 16 fps clip) | frame rate in the container |
| Generated at a lower internal rate and padded | Regular pattern of duplicates (every 2nd or 3rd frame) | duplicate ratio and spacing |

Seedance 2.5 outputs 24 fps. The first real take gets probed and its numbers go here.

## Commands

```
python tools/media/fps.py probe take.mp4
python tools/media/fps.py fix take.mp4 --method interp
python tools/media/fps.py fit take.mov --max-mb 95
```

- `probe` prints codec, size, duration, container rate, average rate, frame count, duplicate
  frames (a frame held at the very end is reported apart, it is not stutter), the spacing pattern
  of unique frames, and a verdict with the command to run.
- `fix` always keeps the original duration, outputs `<name>_fx.mp4` under 95 MB. Methods:
  - `cfr` (default): forces constant 24 fps. For variable frame rate or a wrong base rate.
    Invents no frames.
  - `interp`: removes duplicate frames and rebuilds them with motion compensated interpolation
    (ffmpeg `minterpolate`). For stutter and half-rate padded clips. Slow (about 3 s of processing
    per second of 720p on this test machine) and can warp fine edges on fast motion.
  - `blend`: same, with frame blending. Faster, ghosts on fast motion.
  For heavy cases a dedicated interpolator (RIFE, Topaz, Resolve Speed Warp in Studio) does
  better than ffmpeg. Your own tools plug in here.
- Dropped frames (motion jumps double every few frames, no duplicates): `python tools/media/dejudder.py in.mp4 out.mp4 --metric pan` for camera moves, `--metric flow` for locked-off shots, run twice (needs `pip install opencv-python-headless numpy`). Writes `<take>_dj.mp4`, same frames and duration.
- `fit` encodes H.264 high profile at CRF 16 (visually near lossless). If that is still over the
  cap, it re-encodes in two passes at the bitrate that lands under it. Files already under the cap
  are left alone (no needless quality loss) unless `--force`.

Tested on synthetic clips: half-rate padded, irregular stutter, variable frame rate (24 and 30
mixed), 30 fps, and a 140 MB ProRes file fitted to 19 MB with `--max-mb 20`.
H.264 is used because the free Resolve decodes it on every platform.

Intermediate files go to the film's `_local/` folder. Only the final fixed file replaces the take
in git, with the suffix `_fx` (`001_S01_SH010_T03_fx.mp4`), the original stays in Higgsfield.

## Size reality

A 95 MB cap is roughly 76 Mbit/s for a 10 s clip and 25 Mbit/s for a 30 s clip. I have not
measured a Seedance file yet. Web delivery video at 1080p usually sits well below those numbers,
so the cap most likely bites only when a tool writes ProRes or another near uncompressed
intermediate. `fit` handles exactly that case. The first real take confirms or corrects this.
