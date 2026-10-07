"""Cut a one-take narration into one WAV per line, using Whisper word timestamps.

usage: split_take.py TAKE.wav LINES.json OUT_DIR [--model small.en]

LINES.json: ["line 1 text", "line 2 text", ...] (the script as generated).
Writes OUT_DIR/line<N>.wav and OUT_DIR/timing.json with each line's duration, its start in the take,
and the onset of every word (seconds from the line's start). Needs openai-whisper and soundfile.
"""
import argparse, json, os, re, numpy as np, soundfile as sf, whisper

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("take"); ap.add_argument("lines"); ap.add_argument("out_dir")
ap.add_argument("--model", default="small.en"); ap.add_argument("--pre", type=float, default=0.05)
ap.add_argument("--post", type=float, default=0.18)
a = ap.parse_args()
lines = json.load(open(a.lines))
audio, sr = sf.read(a.take, dtype="float32")
r = whisper.load_model(a.model).transcribe(a.take, word_timestamps=True, language="en", fp16=False)
words = [(w["word"].strip(), w["start"], w["end"]) for s in r["segments"] for w in s["words"]]
norm = lambda w: re.sub(r"[^a-z0-9]", "", w.lower())
# Assign recognised words to lines in order by matching each line's last word.
spans, wi = [], 0
for li, line in enumerate(lines):
    toks = [norm(t) for t in line.split() if norm(t)]
    start = words[wi][1] if wi < len(words) else len(audio) / sr
    last = toks[-1] if toks else ""
    end_i = wi
    while end_i < len(words) and norm(words[end_i][0]) != last and not norm(words[end_i][0]).endswith(last):
        end_i += 1
    if end_i >= len(words):
        end_i = min(wi + len(toks), len(words)) - 1
    spans.append((start, words[end_i][2], [w for w in words[wi:end_i + 1]]))
    wi = end_i + 1
os.makedirs(a.out_dir, exist_ok=True)
timing = {}
for n, (s, e, ws) in enumerate(spans, 1):
    s0, e0 = max(0, s - a.pre), min(len(audio) / sr, e + a.post)
    sf.write(os.path.join(a.out_dir, f"line{n}.wav"), audio[int(s0 * sr):int(e0 * sr)], sr)
    timing[n] = {"duration": round(e0 - s0, 3), "start_in_take": round(s0, 3),
                 "words": [[w, round(ws_s - s0, 3)] for w, ws_s, _ in ws]}
    print(f"[{n}/{len(spans)}] {e0 - s0:.2f}s  {' '.join(w for w, _, _ in ws)}", flush=True)
json.dump(timing, open(os.path.join(a.out_dir, "timing.json"), "w"), indent=1)
print("Check each line by ear: Whisper can drop a word, so a cut may need nudging.")
