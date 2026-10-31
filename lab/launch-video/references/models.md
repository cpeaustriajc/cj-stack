# Models: getting weights, and the environments

## When a hub is slow, measure before waiting

A download that "is running" can be stalled. Check the cache size twice, a few seconds apart, and
compare hosts:

```sh
curl -s -o /dev/null -r 0-20000000 -w "%{speed_download} B/s\n" -L <hub file URL>
curl -s -o /dev/null -w "%{speed_download} B/s\n" "https://speed.cloudflare.com/__down?bytes=25000000"
```

At the October 2026 launch Hugging Face served about 200 KB/s per connection while Cloudflare served
24 MB/s: a 4.5 GB model would have taken six hours. Parallel ranges helped about 5×, but the fix was
another source.

**ModelScope** (`modelscope.cn`, Alibaba) hosts Qwen's official weights and mirrors many popular models
under the same repo name (`facebook/musicgen-medium`, `AI-ModelScope/…`). It served 10–15 MB/s.
`scripts/modelscope_download.py <repo> <dest> [skip,files]` lists a repo through its API and downloads
it in parallel 64 MB ranges with retries, verifying sizes. Load the local folder directly
(`load_model("<dest>")`) and set `HF_HUB_OFFLINE=1` so nothing reaches back to the slow hub.

Check a mirror's file list before downloading; it may hold several weight formats and you need one.

## Environments

Keep each heavy stack in its own environment so they do not fight over versions:
- `tts-venv`: `uv venv --python 3.12 tts-venv && uv pip install --python tts-venv/bin/python --prerelease=allow mlx-audio soundfile`
- `music-venv`: `transformers torch soundfile numpy`, plus `openai-whisper` for word timings.

Tell the person the size of each download before starting it, run long downloads in the background
with progress in the log, and remove models and environments only after they approve the output.
