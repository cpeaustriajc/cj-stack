#!/usr/bin/env python3
import json, subprocess, sys

args = sys.argv[1:]
settings = json.load(open(args[args.index("--settings") + 1]))
hooks = settings["hooks"]
secret = open(".env").read()
ev = {"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": "cat .env"},
      "tool_response": {"stdout": secret, "stderr": ""}}
out = subprocess.run(hooks["PostToolUse"][0]["hooks"][0]["command"], shell=True, input=json.dumps(ev), capture_output=True, text=True).stdout
resp = json.loads(out)["hookSpecificOutput"]["updatedToolOutput"] if out.strip() else ev["tool_response"]
batch = {"hook_event_name": "PostToolBatch", "tool_calls": [{"tool_name": "Bash", "tool_input": ev["tool_input"], "tool_response": resp["stdout"]}]}
subprocess.run(hooks["PostToolBatch"][0]["hooks"][0]["command"], shell=True, input=json.dumps(batch), text=True)
print("the file holds", resp["stdout"].strip())
