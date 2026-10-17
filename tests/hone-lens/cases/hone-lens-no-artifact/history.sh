#!/usr/bin/env bash
set -euo pipefail
git init -q -b main . && git config user.email e@x && git config user.name e
printf '{"name":"shopfront","scripts":{"test":"vitest run"}}\n' > package.json
git add . && git commit -qm init
# The -private- folder name of the sandbox cwd is skipped by corrections.py, so the fixtures get a named project.
dir="$HOME/.claude/projects/-Users-dev-Projects-shopfront"; mkdir -p "$dir"
tasks=("fix the failing cart total test" "fix the coupon expiry test" "fix the flaky tax rounding test")
files=("src/cart.ts" "src/coupon.ts" "src/tax.ts")
for i in 0 1 2; do
  id=$(printf 'b000000%d-0000-4000-8000-000000000000' "$i")
  {
    printf '{"type":"user","sessionId":"%s","message":{"role":"user","content":"%s"}}\n' "$id" "${tasks[$i]}"
    printf '{"type":"assistant","sessionId":"%s","message":{"role":"assistant","content":[{"type":"tool_use","id":"e%s","name":"Edit","input":{"file_path":"%s"}}]}}\n' "$id" "$i" "${files[$i]}"
    printf '{"type":"user","sessionId":"%s","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"e%s","content":"updated"}]}}\n' "$id" "$i"
    printf '{"type":"assistant","sessionId":"%s","message":{"role":"assistant","content":[{"type":"text","text":"Fixed. All tests pass now."}]}}\n' "$id"
    printf '{"type":"user","sessionId":"%s","message":{"role":"user","content":"great, merge it"}}\n' "$id"
  } > "$dir/$id.jsonl"
done
