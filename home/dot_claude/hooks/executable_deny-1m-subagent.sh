#!/usr/bin/env bash
# PreToolUse hook: deny an Agent/Task dispatch pinned to a 1M-context model.
# A subagent inherits the parent model unless one is set, so the default is
# governed by CLAUDE_CODE_SUBAGENT_MODEL in settings.json, not by this hook.
# This hook only refuses an EXPLICIT [1m] override on the call.

set -u

input="$(cat)"

model="$(printf '%s' "$input" | jq -r '.tool_input.model // empty')"

case "$model" in
  *'[1m]'*)
    cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"A 1M-context subagent is blocked by ~/.claude/hooks/deny-1m-subagent.sh. Re-dispatch without the [1m] suffix (e.g. model: \"opus\") and vary effort instead. Remove that hook to override."}}
JSON
    exit 0
    ;;
esac

exit 0
