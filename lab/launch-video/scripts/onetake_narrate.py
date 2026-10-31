"""Generate a whole narration script in one Qwen3-TTS VoiceDesign call, so it is one voice.

usage: onetake_narrate.py SPEC.json MODEL_DIR OUT_DIR --seeds 77,78,79

SPEC.json: {"voice": "<who is speaking: accent, age, timbre, register, what to avoid>",
            "lines": ["line 1 text", "line 2 text", ...],
            "directions": ["delivery for line 1", "delivery for line 2", ...]}
Writes OUT_DIR/take-<seed>.wav per seed. Run in an env with mlx-audio and soundfile.
"""
import argparse, json, os, numpy as np, soundfile as sf, mlx.core as mx
from mlx_audio.tts.utils import load_model

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("spec"); ap.add_argument("model_dir"); ap.add_argument("out_dir")
ap.add_argument("--seeds", default="11,42,77")
a = ap.parse_args()
spec = json.load(open(a.spec))
text = "\n\n".join(spec["lines"])
direction = spec["voice"] + " Read this as one continuous voiceover by the same person, leaving a clear pause between paragraphs. " + " ".join(
    f"Paragraph {i}: {d}" for i, d in enumerate(spec.get("directions", []), 1))
os.makedirs(a.out_dir, exist_ok=True)
m = load_model(a.model_dir); sr = m.sample_rate
seeds = [int(s) for s in a.seeds.split(",")]
for n, seed in enumerate(seeds, 1):
    mx.random.seed(seed)
    r = list(m.generate_voice_design(text=text, language="English", instruct=direction))
    audio = np.concatenate([np.array(x.audio, dtype=np.float32) for x in r])
    path = os.path.join(a.out_dir, f"take-{seed}.wav")
    sf.write(path, audio, sr)
    print(f"[{n}/{len(seeds)}] seed {seed}: {len(audio)/sr:.1f}s -> {path}", flush=True)
