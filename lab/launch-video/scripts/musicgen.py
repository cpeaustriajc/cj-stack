"""Generate music candidates with MusicGen from a local model folder.

usage: musicgen.py MODEL_DIR OUT_PREFIX SECONDS "prompt 1" ["prompt 2" ...]
Writes OUT_PREFIX-1.wav, OUT_PREFIX-2.wav, ... Needs transformers, torch, soundfile, numpy.
"""
import sys, time, torch, numpy as np, soundfile as sf
from transformers import AutoProcessor, MusicgenForConditionalGeneration
if len(sys.argv) < 5 or sys.argv[1] in ("-h", "--help"):
    print(__doc__); sys.exit(0)
model_dir, prefix, secs, prompts = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4:]
dev = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"[musicgen] loading {model_dir} on {dev}", flush=True)
proc = AutoProcessor.from_pretrained(model_dir)
model = MusicgenForConditionalGeneration.from_pretrained(model_dir).to(dev)
sr = model.config.audio_encoder.sampling_rate
for i, p in enumerate(prompts, 1):
    t0 = time.time(); torch.manual_seed(6 + i)
    inp = proc(text=[p], padding=True, return_tensors="pt").to(dev)
    out = model.generate(**inp, do_sample=True, guidance_scale=3.5, max_new_tokens=int(secs * 50))
    a = out[0, 0].float().cpu().numpy(); a = a / max(1e-6, np.abs(a).max()) * 0.89
    sf.write(f"{prefix}-{i}.wav", a, sr)
    print(f"[musicgen] [{i}/{len(prompts)}] {prefix}-{i}.wav ({len(a)/sr:.1f}s, {time.time()-t0:.0f}s)", flush=True)
