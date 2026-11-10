#!/usr/bin/env python3
"""Framerate and size tool for AI clips. Needs ffmpeg and ffprobe (ffmpeg 5.1 or newer).

  python tools/media/fps.py probe clip.mp4
  python tools/media/fps.py fix clip.mp4 [--fps 24] [--method cfr|interp|blend] [--max-mb 95] [-o out.mp4]
  python tools/media/fps.py fit clip.mp4 [--max-mb 95] [--force] [-o out.mp4]

fix methods (duration is always preserved):
  cfr     conform to constant frame rate only (VFR or wrong rate). Fast, no frames invented.
  interp  remove duplicate frames, rebuild them with motion compensated interpolation (stutter fix).
  blend   same as interp with frame blending. Cheaper, ghosts on fast motion.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path

MPDECIMATE = "mpdecimate=hi=64*12:lo=64*5:frac=0.33"


def run(cmd, capture=True):
    r = subprocess.run(cmd, capture_output=capture, text=True)
    if r.returncode != 0:
        sys.stderr.write((r.stderr or "")[-3000:])
        raise SystemExit(f"Command failed: {' '.join(cmd[:6])} ...")
    return r


def ffprobe_json(path):
    r = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    return json.loads(r.stdout)


def video_info(path):
    data = ffprobe_json(path)
    v = next((s for s in data["streams"] if s["codec_type"] == "video"), None)
    if v is None:
        raise SystemExit("No video stream.")
    a = next((s for s in data["streams"] if s["codec_type"] == "audio"), None)
    fmt = data["format"]
    duration = float(fmt.get("duration") or v.get("duration") or 0)
    return {
        "codec": v.get("codec_name"), "profile": v.get("profile"), "pix_fmt": v.get("pix_fmt"),
        "width": v.get("width"), "height": v.get("height"),
        "r_frame_rate": Fraction(v.get("r_frame_rate", "0/1")),
        "avg_frame_rate": Fraction(v.get("avg_frame_rate", "0/1") or "0/1"),
        "duration": duration, "size": int(fmt.get("size", 0)),
        "bit_rate": int(fmt.get("bit_rate", 0) or 0),
        "audio": a is not None, "audio_codec": a.get("codec_name") if a else None,
        "audio_bit_rate": int(a.get("bit_rate", 0) or 0) if a else 0,
    }


def packet_times(path):
    r = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time",
             "-of", "csv=p=0", str(path)])
    times = sorted(float(x) for x in r.stdout.split() if x and x != "N/A")
    return times


def kept_frame_times(path):
    """Timestamps of frames that survive duplicate removal."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-an", "-vf",
                        f"{MPDECIMATE},showinfo", "-fps_mode", "passthrough", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [float(m) for m in re.findall(r"pts_time:\s*([0-9.]+)", r.stderr)]


def cmd_probe(args):
    path = Path(args.file)
    info = video_info(path)
    times = packet_times(path)
    frames = len(times)
    deltas = [round(b - a, 4) for a, b in zip(times, times[1:])]
    vfr = len(set(deltas)) > 1 and (max(deltas) - min(deltas)) > 0.002 if deltas else False
    kept = kept_frame_times(path)
    dups = max(frames - len(kept), 0)
    # a held last frame (end of clip) is not stutter: count it apart
    tail = sum(1 for t in times if kept and t > kept[-1] + 1e-4)
    interior = max(dups - tail, 0)
    fps = float(info["avg_frame_rate"]) or float(info["r_frame_rate"]) or 24.0
    gaps = Counter(round((b - a) * fps) for a, b in zip(kept, kept[1:]))

    print(f"File        {path.name}")
    print(f"Video       {info['codec']} {info['profile']} {info['pix_fmt']} {info['width']}x{info['height']}")
    print(f"Rate        container {float(info['r_frame_rate']):.3f} fps, average {float(info['avg_frame_rate']):.3f} fps")
    print(f"Duration    {info['duration']:.3f} s, {frames} frames")
    print(f"Size        {info['size'] / 1e6:.2f} MB, {info['bit_rate'] / 1e6:.2f} Mbit/s")
    print(f"Audio       {info['audio_codec'] or 'none'}")
    print(f"Duplicates  {interior} of {frames} frames ({(interior / frames * 100 if frames else 0):.1f}%)"
          + (f", plus {tail} held at the end" if tail else ""))
    if gaps:
        common = ", ".join(f"{k}f x{v}" for k, v in sorted(gaps.items()))
        print(f"Unique-frame spacing  {common}")

    verdict = []
    if vfr:
        verdict.append("variable frame rate: run fix --method cfr")
    if abs(fps - args.target) > 0.01:
        verdict.append(f"rate {fps:.3f} differs from timeline {args.target}: run fix --method cfr "
                       "(or interp for smoother motion)")
    if frames and interior / frames > 0.02:
        spacing2 = gaps.get(2, 0) / max(sum(gaps.values()), 1)
        if spacing2 > 0.8:
            verdict.append("regular doubled frames: content is half rate padded, run fix --method interp")
        else:
            verdict.append("irregular duplicate frames (stutter): run fix --method interp")
    if info["size"] / 1e6 > args.max_mb:
        verdict.append(f"over {args.max_mb} MB: run fit")
    print("Verdict     " + ("; ".join(verdict) if verdict else "clean"))


def encode(src, dst, vf, audio, crf=16, bitrate=None, two_pass=False, duration=None):
    base = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src)]
    if duration:
        base += ["-t", f"{duration:.3f}"]
    vcodec = ["-c:v", "libx264", "-preset", "slow", "-profile:v", "high", "-pix_fmt", "yuv420p"]
    if vf:
        vcodec = ["-vf", vf] + vcodec
    tail = ["-movflags", "+faststart"]
    acodec = ["-c:a", "aac", "-b:a", "192k"] if audio else ["-an"]
    if not two_pass:
        run(base + vcodec + ["-crf", str(crf)] + acodec + tail + [str(dst)])
        return
    with tempfile.TemporaryDirectory() as tmp:
        log = os.path.join(tmp, "pass")
        rate = ["-b:v", f"{bitrate}k", "-maxrate", f"{int(bitrate * 1.2)}k", "-bufsize", f"{bitrate * 2}k"]
        run(base + vcodec + rate + ["-pass", "1", "-passlogfile", log, "-an", "-f", "mp4", os.devnull])
        run(base + vcodec + rate + ["-pass", "2", "-passlogfile", log] + acodec + tail + [str(dst)])


def fit_file(src, dst, max_mb, vf=None, force=False, keep_duration=False):
    info = video_info(src)
    duration = info["duration"] if keep_duration else None
    if not force and not vf and info["size"] / 1e6 <= max_mb:
        print(f"{Path(src).name} is {info['size'] / 1e6:.2f} MB, already under {max_mb} MB. Nothing done.")
        return None
    encode(src, dst, vf, info["audio"], duration=duration)
    size = Path(dst).stat().st_size / 1e6
    if size > max_mb:
        audio_k = 192 if info["audio"] else 0
        total_k = max_mb * 8000 * 0.96 / max(info["duration"], 0.1)
        video_k = int(total_k - audio_k)
        print(f"CRF 16 gave {size:.1f} MB, re-encoding two-pass at {video_k} kbit/s")
        encode(src, dst, vf, info["audio"], bitrate=video_k, two_pass=True, duration=duration)
        size = Path(dst).stat().st_size / 1e6
    print(f"Wrote {dst} ({size:.2f} MB)")
    return dst


def default_out(src, suffix):
    p = Path(src)
    return p.with_name(f"{p.stem}{suffix}.mp4")


def cmd_fix(args):
    fps = args.fps
    if args.method == "cfr":
        vf = f"fps={fps}"
    elif args.method == "interp":
        vf = f"{MPDECIMATE},minterpolate=fps={fps}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"
    else:
        vf = f"{MPDECIMATE},minterpolate=fps={fps}:mi_mode=blend"
    if args.method != "cfr":
        # duplicates removed at the tail shorten the clip: hold the last frame, trim to the source length.
        # The extra fps filter is needed: tpad does not fire directly after minterpolate (ffmpeg 6.1).
        vf += f",fps={fps},tpad=stop_mode=clone:stop_duration=1"
    out = args.output or default_out(args.file, "_fx")
    fit_file(args.file, out, args.max_mb, vf=vf, force=True, keep_duration=True)


def cmd_fit(args):
    out = args.output or default_out(args.file, "_fit")
    fit_file(args.file, out, args.max_mb, force=args.force)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("probe"); a.add_argument("file")
    a.add_argument("--target", type=float, default=24.0); a.add_argument("--max-mb", type=float, default=95)
    a.set_defaults(func=cmd_probe)
    a = sub.add_parser("fix"); a.add_argument("file"); a.add_argument("--fps", default="24")
    a.add_argument("--method", choices=["cfr", "interp", "blend"], default="cfr")
    a.add_argument("--max-mb", type=float, default=95); a.add_argument("-o", "--output")
    a.set_defaults(func=cmd_fix)
    a = sub.add_parser("fit"); a.add_argument("file"); a.add_argument("--max-mb", type=float, default=95)
    a.add_argument("--force", action="store_true"); a.add_argument("-o", "--output")
    a.set_defaults(func=cmd_fit)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
