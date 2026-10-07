"""Download a ModelScope repo in parallel 64 MB ranges, with retries and size checks.

usage: modelscope_download.py REPO DEST [skip1,skip2]
example: modelscope_download.py Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign models/voicedesign
"""
import json, os, sys, urllib.request, concurrent.futures as cf, time
if len(sys.argv) < 3 or sys.argv[1] in ("-h", "--help"):
    print(__doc__); sys.exit(0)
repo, dest = sys.argv[1], sys.argv[2]
files = json.load(urllib.request.urlopen(f"https://modelscope.cn/api/v1/models/{repo}/repo/files?Recursive=true"))["Data"]["Files"]
files = [f for f in files if f["Type"] == "blob"]
skip = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else set()
files = [f for f in files if f["Path"] not in skip]
base = f"https://modelscope.cn/models/{repo}/resolve/master/"
CHUNK = 64 * 1024 * 1024
jobs = []
for f in files:
    p = os.path.join(dest, f["Path"]); os.makedirs(os.path.dirname(p), exist_ok=True)
    if os.path.exists(p) and os.path.getsize(p) == f["Size"]: continue
    with open(p, "wb") as h: h.truncate(f["Size"])
    for start in range(0, max(f["Size"], 1), CHUNK):
        jobs.append((p, f["Path"], start, min(start + CHUNK, f["Size"]) - 1))
total = sum(j[3] - j[2] + 1 for j in jobs); done = 0; t0 = time.time()
def get(job):
    p, path, a, b = job
    for attempt in range(5):
        try:
            req = urllib.request.Request(base + path, headers={"Range": f"bytes={a}-{b}"})
            data = urllib.request.urlopen(req, timeout=60).read()
            assert len(data) == b - a + 1, (len(data), b - a + 1)
            with open(p, "r+b") as h: h.seek(a); h.write(data)
            return len(data)
        except Exception as e:
            err = e; time.sleep(2)
    raise err
with cf.ThreadPoolExecutor(12) as ex:
    for i, n in enumerate(ex.map(get, jobs), 1):
        done += n
        if i % 4 == 0 or i == len(jobs):
            print(f"[{i}/{len(jobs)}] {done/1e9:.2f}/{total/1e9:.2f} GB  {done/1e6/(time.time()-t0):.1f} MB/s", flush=True)
for f in files:
    p = os.path.join(dest, f["Path"]); assert os.path.getsize(p) == f["Size"], p
print(f"[download] ✔ {repo} -> {dest} ({len(files)} files)", flush=True)
