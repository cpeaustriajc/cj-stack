#!/usr/bin/env bash
set -euo pipefail
n=3
git init -q -b main . && git config user.email e@x && git config user.name e
echo app > app.txt && git add . && git commit -qm "init"
git branch feat/checkout-12 && git branch fix/login-7
dir="$HOME/.claude/projects/$(pwd | sed 's#[/.]#-#g')"
mkdir -p "$dir"
topics=("checkout drawer, branch feat/checkout-12, PR #12 opened" "login test flake, branch fix/login-7, fixed and committed" "cart totals rounding, planned, not started" "search index rebuild, PR #9 merged" "dark mode tokens, branch feat/dark-3, uncommitted, verified")
for i in $(seq 1 "$n"); do
  id=$(printf '0000000-0000-4000-8000-%012d' "$i")
  t="${topics[$(( (i-1) % ${#topics[@]} ))]}"
  {
    printf '{"type":"user","sessionId":"%s","message":{"role":"user","content":"day %s: work on %s"}}\n' "$id" "$i" "$t"
    printf '{"type":"assistant","sessionId":"%s","message":{"role":"assistant","content":[{"type":"text","text":"Done for today: %s."}]}}\n' "$id" "$t"
  } > "$dir/$id.jsonl"
done
