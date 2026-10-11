#!/usr/bin/env python3
"""Proves no cj-stack mod denies an action Claude Code owns (CLAUDE.md, Tool-neutral).

Usage: python3 tests/claude-owned/run.py [--mods DIR]

Command-hook mods: each PreToolUse hook runs on each action with a fake HOME,
a fake project as cwd and CLAUDE_PLUGIN_ROOT set to the mod folder.
Module mods: `claude plugin test` runs owned.test.ts on a copy of the mod.
Exit 1 on any deny or failing test. Log: <tmp>/claude-owned-last-run.log
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
LOG = Path(tempfile.gettempdir()) / "claude-owned-last-run.log"
SHAPE = json.loads((HERE / "actions.json").read_text(encoding="utf-8"))
ACTIONS = SHAPE["actions"]


def emit(log, line):
    print(line, flush=True)
    log.write(line + "\n")
    log.flush()


def place(value, home, project):
    if isinstance(value, str):
        return re.sub(r"^~(?=/)", lambda _: home, value).replace("<project>", project)
    return value


def write_seed(seed, home, project):
    for rel, text in seed.items():
        path = Path(place(rel, home, project))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def tool_matches(matcher, tool):
    if matcher in ("", "*"):
        return True
    try:
        return any(re.fullmatch(p, tool) for p in matcher.split("|"))
    except re.error:
        return False


def is_deny(code, out):
    if code == 2:
        return True
    try:
        data = json.loads(out)
    except ValueError:
        return False
    if not isinstance(data, dict):
        return False
    hso = data.get("hookSpecificOutput")
    return (isinstance(hso, dict) and hso.get("permissionDecision") == "deny") or data.get("decision") == "block"


def command_hooks(mod):
    path = mod / "hooks" / "hooks.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for group in (data.get("hooks") or {}).get("PreToolUse", []):
        for hook in group.get("hooks", []):
            if hook.get("type") == "command":
                out.append((group.get("matcher", "*"), hook["command"], int(hook.get("timeout", 30))))
    return out


def has_modules(mod):
    path = mod / "hooks" / "hooks.json"
    return path.is_file() and "modules" in json.loads(path.read_text(encoding="utf-8"))


def run_hook(mod, command, timeout, event, home, project):
    bash = shutil.which("bash")
    if not bash:
        raise SystemExit("bash not found on PATH")
    env = dict(os.environ, HOME=home, USERPROFILE=home, CLAUDE_PLUGIN_ROOT=str(mod), CLAUDE_PROJECT_DIR=project)
    proc = subprocess.run([bash, "-c", command], input=json.dumps(event).encode("utf-8"),
                          capture_output=True, env=env, cwd=project, timeout=timeout + 30)
    return proc.returncode, proc.stdout.decode("utf-8", "replace"), proc.stderr.decode("utf-8", "replace")


def run_module_mod(mod, tmp, log, k, n):
    dest = Path(tmp) / mod.name
    shutil.copytree(mod, dest, ignore=shutil.ignore_patterns("*.test.ts", "*.test.tsx", "node_modules"))
    shutil.copy(HERE / "owned.test.ts", dest / "owned.test.ts")
    # The plugin test runtime imports only code files, so the JSON becomes a TS module.
    (dest / "actions.ts").write_text("export default " + (HERE / "actions.json").read_text(encoding="utf-8"), encoding="utf-8")
    claude = shutil.which("claude")
    if not claude:
        raise SystemExit("claude not found on PATH")
    emit(log, f"[{k}/{n}] {mod.name}: claude plugin test ({len(ACTIONS)} actions)")
    proc = subprocess.run([claude, "plugin", "test", str(dest)], capture_output=True, timeout=900)
    text = (proc.stdout + proc.stderr).decode("utf-8", "replace")
    for line in text.splitlines():
        log.write("    " + line + "\n")
    log.flush()
    return proc.returncode == 0, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mods", default=str(REPO / "mods"))
    args = ap.parse_args()
    mods_dir = Path(args.mods).resolve()
    mods = sorted(p for p in mods_dir.iterdir()
                  if p.name != "archived" and (p / ".claude-plugin" / "plugin.json").is_file())
    tmp = tempfile.mkdtemp(prefix="claude-owned-")
    home, project = str(Path(tmp, "home")), str(Path(tmp, "project"))
    os.makedirs(home)
    os.makedirs(project)

    jobs = []
    for mod in mods:
        if has_modules(mod):
            jobs.append(("module", mod))
        for matcher, command, timeout in command_hooks(mod):
            for a in ACTIONS:
                if tool_matches(matcher, a["tool"]):
                    jobs.append(("command", mod, command, timeout, a))
    n = len(jobs)
    failures = []
    try:
        write_seed(SHAPE["seed"], home, project)
        with open(LOG, "w", encoding="utf-8") as log:
            emit(log, f"claude-owned: {len(mods)} mods, {len(ACTIONS)} actions, {n} checks, log {LOG}")
            for k, job in enumerate(jobs, 1):
                if job[0] == "module":
                    ok, _ = run_module_mod(job[1], tmp, log, k, n)
                    emit(log, f"[{k}/{n}] {'✔' if ok else '✘'} {job[1].name} module tests")
                    if not ok:
                        failures.append(f"{job[1].name}: module tests failed (see log)")
                    continue
                _, mod, command, timeout, a = job
                event = {"session_id": "claude-owned", "hook_event_name": "PreToolUse", "transcript_path": "",
                         "cwd": project, "tool_name": a["tool"],
                         "tool_input": {key: place(v, home, project) for key, v in a["input"].items()}}
                code, out, err = run_hook(mod, command, timeout, event, home, project)
                if is_deny(code, out):
                    reason = (out.strip() or err.strip())[:200]
                    emit(log, f"[{k}/{n}] ✘ {mod.name} denies {a['id']} ({a['owned']}): {reason}")
                    failures.append(f"{mod.name} denies {a['id']} ({a['owned']})")
                else:
                    emit(log, f"[{k}/{n}] ✔ {mod.name} {a['id']} ({a['owned']})")
            if failures:
                emit(log, f"FAILED: {len(failures)} owned action(s) blocked by a mod")
                for f in failures:
                    emit(log, "  - " + f)
                sys.exit(1)
            emit(log, "PASSED: no mod denies a Claude Code-owned action")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
