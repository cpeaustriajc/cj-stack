import json, sys

ev = json.load(sys.stdin)
tr = ev["tool_response"]
if isinstance(tr, dict) and isinstance(tr.get("stdout"), str):
    tr = {**tr, "stdout": tr["stdout"].replace("FAKESECRET_toy1", "[REDACTED]")}
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedToolOutput": tr}}))
