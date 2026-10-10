import json, os, shlex, sys

ev = json.load(sys.stdin)
cmd = (ev.get("tool_input") or {}).get("command", "")
if ev.get("tool_name") == "Bash":
    if "base64" in cmd and ".env" in cmd:
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                 "permissionDecisionReason": "toy: transform of a secret source"}}))
        sys.exit(0)
    filt = f"{shlex.quote(sys.executable)} {shlex.quote(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secret_filter.py'))}"
    new = f"exec > >({filt}) 2> >({filt} >&2)\n{cmd}"
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow",
                                             "updatedInput": {**ev["tool_input"], "command": new}}}))
