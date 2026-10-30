#!/usr/bin/env python3
"""PreToolUse hook: deny git branch/worktree creation unless the new name starts with claude/,
and deny a worktree path outside <main repo>/.claude/."""
import json, shlex, sys, os, re, subprocess

PREFIX = "claude/"

def new_branch_names(argv):
    if not argv or os.path.basename(argv[0]) != "git":
        return []
    # skip global git options like -C <path>, -c k=v, --git-dir=...
    i = 1
    while i < len(argv) and argv[i].startswith("-"):
        i += 2 if argv[i] in ("-C", "-c", "--git-dir", "--work-tree") else 1
    if i >= len(argv):
        return []
    sub, args = argv[i], argv[i + 1:]
    names = []
    if sub in ("checkout", "switch"):
        for k, a in enumerate(args):
            if a in ("-b", "-B", "-c", "-C", "--orphan") and k + 1 < len(args):
                names.append(args[k + 1])
    elif sub == "branch":
        flags = {a for a in args if a.startswith("-")}
        if flags & {"-d", "-D", "--delete", "-m", "-M", "--move", "-c", "-C", "--copy",
                    "-l", "--list", "-a", "-r", "--all", "--remotes", "-u", "--set-upstream-to",
                    "--unset-upstream", "--edit-description", "--show-current", "--merged",
                    "--no-merged", "--contains", "--no-contains", "--points-at", "-v", "-vv"}:
            return []
        pos = [a for a in args if not a.startswith("-")]
        if pos:
            names.append(pos[0])
    elif sub == "worktree" and args and args[0] == "add":
        wa = args[1:]
        explicit = None
        pos = []
        k = 0
        while k < len(wa):
            a = wa[k]
            if a in ("-b", "-B") and k + 1 < len(wa):
                explicit = wa[k + 1]; k += 2; continue
            if a in ("--reason",) and k + 1 < len(wa):
                k += 2; continue
            if not a.startswith("-"):
                pos.append(a)
            k += 1
        if explicit is not None:
            names.append(explicit)
        elif len(pos) == 1:
            # no commit-ish given: git derives a NEW branch from the path basename
            names.append(os.path.basename(pos[0].rstrip("/")))
        if pos:
            WORKTREE_PATHS.append(pos[0])
    return names

WORKTREE_PATHS = []

def main_repo_root(cwd):
    try:
        common = subprocess.run(["git", "-C", cwd, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None
    return os.path.realpath(os.path.dirname(common))

def main():
    data = json.load(sys.stdin)
    cmd = (data.get("tool_input") or {}).get("command") or ""
    bad = []
    for segment in re.split(r"\s*(?:&&|\|\||;|\|)\s*", cmd):
        try:
            argv = shlex.split(segment)
        except ValueError:
            continue
        bad += [n for n in new_branch_names(argv) if not n.startswith(PREFIX)]
    reasons = []
    if bad:
        reasons.append(f"Branch/worktree name(s) {bad} lack the claude/ prefix; use claude/<topic>.")
    if WORKTREE_PATHS:
        cwd = data.get("cwd") or os.getcwd()
        root = main_repo_root(cwd)
        allowed = os.path.join(root, ".claude") + os.sep if root else None
        for p in WORKTREE_PATHS:
            full = os.path.realpath(os.path.join(cwd, os.path.expanduser(p)))
            if not allowed or not full.startswith(allowed):
                reasons.append(f"Worktree path {p!r} resolves outside {allowed or '<repo>/.claude/'}; "
                               "create worktrees under <repo>/.claude/worktrees/ only.")
    if reasons:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": " ".join(reasons) + " (~/.claude/hooks/deny-unprefixed-branch.py)"}}))
    sys.exit(0)

main()
