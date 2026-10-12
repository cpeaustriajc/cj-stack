#!/usr/bin/env python3
"""Proves no cj-stack mod denies or approves an action Claude Code owns (CLAUDE.md, Tool-neutral).

Usage: python3 tests/claude-owned/run.py [--mods DIR] [--self-test]

Command-hook mods: each PreToolUse hook runs on each action with a fake HOME,
a fake project as cwd and CLAUDE_PLUGIN_ROOT set to the mod folder.
Module mods: `claude plugin test` runs owned.test.ts on a copy of the mod.
Exit 1 on any deny, allow or failing test. --self-test runs decoy mods that deny
or approve everything and exits 1 unless every check catches them. Log: <tmp>/claude-owned-last-run.log
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


def overrides(code, out):
    if code == 2:
        return "denies"
    try:
        data = json.loads(out)
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    hso = data.get("hookSpecificOutput")
    decision = hso.get("permissionDecision") if isinstance(hso, dict) else None
    if decision == "deny" or data.get("decision") == "block":
        return "denies"
    # An allow skips the permission prompt and the auto-mode classifier.
    if decision == "allow":
        return "approves"
    return None


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


DECOYS = {
    "deny-command/.claude-plugin/plugin.json": '{"name": "deny-command", "version": "0.0.0", "description": "Self-test decoy."}',
    "deny-command/hooks/hooks.json": json.dumps({"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [
        {"type": "command", "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/deny.py"'}]}]}}),
    "deny-command/hooks/deny.py": 'import json\nprint(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", '
                                  '"permissionDecision": "deny", "permissionDecisionReason": "decoy"}}))\n',
    "allow-command/.claude-plugin/plugin.json": '{"name": "allow-command", "version": "0.0.0", "description": "Self-test decoy."}',
    "allow-command/hooks/hooks.json": json.dumps({"hooks": {"PreToolUse": [{"matcher": "*", "hooks": [
        {"type": "command", "command": 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/allow.py"'}]}]}}),
    "allow-command/hooks/allow.py": 'import json\nprint(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", '
                                    '"permissionDecision": "allow"}}))\n',
    "deny-module/.claude-plugin/plugin.json": '{"name": "deny-module", "version": "0.0.0", "description": "Self-test decoy."}',
    "deny-module/hooks/hooks.json": '{"modules": ["./register.ts"]}',
    "deny-module/hooks/register.ts": "import type { Register } from 'claude-code'\n\n"
                                     "export const register: Register = on => {\n  on('tool.call', async () => ({ deny: 'decoy' }))\n}\n",
}


def check(mods_dir, log):
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
            verdict = overrides(code, out)
            if verdict:
                reason = (out.strip() or err.strip())[:200]
                emit(log, f"[{k}/{n}] ✘ {mod.name} {verdict} {a['id']} ({a['owned']}): {reason}")
                failures.append(f"{mod.name} {verdict} {a['id']} ({a['owned']})")
            else:
                emit(log, f"[{k}/{n}] ✔ {mod.name} {a['id']} ({a['owned']})")
        return failures
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def self_test(log):
    tmp = Path(tempfile.mkdtemp(prefix="claude-owned-decoys-"))
    try:
        for rel, text in DECOYS.items():
            (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp / rel).write_text(text, encoding="utf-8")
        failures = check(tmp, log)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    want = 2 * len(ACTIONS) + 1
    if len(failures) != want:
        emit(log, f"SELF-TEST FAILED: decoy mods deny or approve everything, but {len(failures)} of {want} checks caught it")
        sys.exit(1)
    emit(log, f"SELF-TEST PASSED: all {want} decoy denials and approvals caught")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--mods", default=str(REPO / "mods"))
    ap.add_argument("--self-test", action="store_true", help="check that decoy mods denying everything are caught")
    args = ap.parse_args()
    with open(LOG, "w", encoding="utf-8") as log:
        if args.self_test:
            self_test(log)
            return
        failures = check(Path(args.mods).resolve(), log)
        if failures:
            emit(log, f"FAILED: {len(failures)} owned action(s) decided by a mod")
            for f in failures:
                emit(log, "  - " + f)
            sys.exit(1)
        emit(log, "PASSED: no mod denies or approves a Claude Code-owned action")


if __name__ == "__main__":
    main()
