import json, re, sys


def scrub(o):
    if isinstance(o, str):
        return re.sub(r"FAKESECRET_\w+", "[REDACTED]", o)
    if isinstance(o, list):
        return [scrub(x) for x in o]
    if isinstance(o, dict):
        return {k: scrub(v) for k, v in o.items()}
    return o


ev = json.load(sys.stdin)
print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedToolOutput": scrub(ev["tool_response"])}}))
