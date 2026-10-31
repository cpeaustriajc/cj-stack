#!/usr/bin/env bash
# A thread started without a model inherits the settings default, which is opus[1m].

set -u

input="$(cat)"

prompt="$(printf '%s' "$input" | jq -r '.tool_input.prompt // empty')"
model="$(printf '%s' "$input" | jq -r '.tool_input.model // empty')"
effort="$(printf '%s' "$input" | jq -r '.tool_input.effort // empty')"

if [ -n "$prompt" ] && { [ -z "$model" ] || [ -z "$effort" ]; }; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"Thread start without model or effort, blocked by ~/.claude/hooks/require-thread-model.sh. Call start_session again with model: \"claude-opus-5-5\" and effort: \"medium\" (\"high\" only when the spec marks the thread hard)."}}
JSON
fi

exit 0
