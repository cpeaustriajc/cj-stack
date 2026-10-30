#!/usr/bin/env bash

set -u

input="$(cat)"

text="$(printf '%s' "$input" | jq -r '[.tool_input | .. | strings] | join("\n")')"

match="$(printf '%s' "$text" | grep -o -E -i '/cj-(lab|stack):|self-verify|Before the PR|PASS verdict|re-run command' | head -n 1)"

if [ -n "$match" ]; then
  reason="Linear text contains \"$match\", blocked by ~/.claude/hooks/deny-linear-engineering-text.sh. PO and QA read Linear: drop engineering steps (verify, PR gates, skill commands) and keep only the template's sections."
  jq -cn --arg reason "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$reason}}'
fi

exit 0
