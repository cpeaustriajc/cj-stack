#!/usr/bin/env bash
set -euo pipefail
git init -q -b main . && git config user.email e@x && git config user.name e
mkdir -p .claude/skills/release-notes
printf -- '---\nname: release-notes\ndescription: >\n  This skill should be used when the user asks to write release notes or a changelog entry for a\n  version. It groups merged PRs by area and links each one.\n---\n\nGroup the merged PRs by area; link each PR; lead with breaking changes.\n' > .claude/skills/release-notes/SKILL.md
git add . && git commit -qm init
# The -private- folder name of the sandbox cwd is skipped by corrections.py, so the fixtures get a named project.
dir="$HOME/.claude/projects/-Users-dev-Projects-shopfront"; mkdir -p "$dir"
for i in 1 2 3; do
  id=$(printf 'a000000%d-0000-4000-8000-000000000000' "$i")
  {
    printf '{"type":"user","sessionId":"%s","message":{"role":"user","content":"write the release notes for v1.%s from the PRs merged since the last tag"}}\n' "$id" "$i"
    printf '{"type":"assistant","sessionId":"%s","message":{"role":"assistant","content":[{"type":"tool_use","id":"b%s","name":"Bash","input":{"command":"git log v1.%s..HEAD --oneline --merges"}}]}}\n' "$id" "$i" "$((i-1))"
    printf '{"type":"user","sessionId":"%s","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"b%s","content":"a1 Merge PR #4%s checkout fix"}]}}\n' "$id" "$i" "$i"
    printf '{"type":"assistant","sessionId":"%s","message":{"role":"assistant","content":[{"type":"text","text":"Release notes for v1.%s: checkout fix (#4%s)."}]}}\n' "$id" "$i" "$i"
    printf '{"type":"user","sessionId":"%s","message":{"role":"user","content":"thanks, posting them now"}}\n' "$id"
  } > "$dir/$id.jsonl"
done
