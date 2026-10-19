"""Join audio clips into one file with gaps, for review by ear, and print where each starts.

usage: audition.py OUT.wav CLIP.wav [CLIP.wav ...] [--gap 1.2]
"""
import argparse, numpy as np, soundfile as sf
ap = argparse.ArgumentParser(description=__doc__); ap.add_argument("out"); ap.add_argument("clips", nargs="+")
ap.add_argument("--gap", type=float, default=1.2); a = ap.parse_args()
parts, t, sr = [], 0.0, None
for i, c in enumerate(a.clips, 1):
    x, sr = sf.read(c, dtype="float32")
    if x.ndim > 1: x = x.mean(axis=1)
    print(f"{i}. {int(t // 60)}:{t % 60:04.1f}  {c}")
    parts += [x, np.zeros(int(a.gap * sr), np.float32)]; t += len(x) / sr + a.gap
sf.write(a.out, np.concatenate(parts), sr); print(f"-> {a.out} ({t:.1f}s)")
