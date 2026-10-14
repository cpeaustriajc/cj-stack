"""Proves secret_redact.py emits a withheld result when the engine hangs in a way SIGALRM cannot stop.
Usage: python3 deadline_test.py [HOOKS_DIR]. Exit 0 = PASS."""
import json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "hooks")
tmp = Path(tempfile.mkdtemp(prefix="deadline-"))
hooks = tmp / "hooks"
shutil.copytree(src, hooks, ignore=shutil.ignore_patterns("__pycache__"))
with open(hooks / "secret_engine.py", "a") as f:
    # sum(range(..)) is one C loop that holds the GIL and never checks signals, so only a process kill stops it.
    f.write("\n\ndef _stall(*a, **k):\n    sum(range(10 ** 13))\n\n\nEngine.redact_obj = _stall\n")
home = tmp / "home"
(home / "Projects").mkdir(parents=True)
env = dict(os.environ, SECRET_HOOK_HOME=str(home), SECRET_HOOK_ROOTS=str(home / "Projects"))
event = {"hook_event_name": "PostToolUse", "tool_name": "Read", "tool_input": {"file_path": "notes.txt"}, "cwd": str(tmp),
         "tool_response": {"stdout": "line one", "stderr": "", "nested": ["a", {"b": "c"}], "n": 3}}
t0 = time.monotonic()
try:
    p = subprocess.run([sys.executable, str(hooks / "secret_redact.py")], input=json.dumps(event).encode(),
                       capture_output=True, env=env, timeout=40)
except subprocess.TimeoutExpired:
    print("FAIL: still running after 40 s; Claude Code would time the hook out and pass raw output")
    sys.exit(1)
elapsed = time.monotonic() - t0
got = json.loads(p.stdout.decode() or "null")
out = (got or {}).get("hookSpecificOutput", {}).get("updatedToolOutput", {})
held = lambda v: isinstance(v, str) and v.startswith("[REDACTED: output withheld (")
ok = (p.returncode == 0 and elapsed < 20 and all(held(v) for v in (out.get("stdout"), out.get("stderr")))
      and isinstance(out.get("nested"), list) and held(out["nested"][0]) and held(out["nested"][1].get("b")) and out.get("n") == 3)
print("%s elapsed=%.1fs rc=%d out=%s" % ("PASS" if ok else "FAIL", elapsed, p.returncode, p.stdout.decode()[:200]))
sys.exit(0 if ok else 1)
