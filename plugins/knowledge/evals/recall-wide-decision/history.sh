#!/usr/bin/env bash
set -euo pipefail
git init -q -b main . && git config user.email e@x && git config user.name e
echo app > app.txt && git add . && git commit -qm "init"
git branch feat/checkout-drawer-12
dir="$HOME/.claude/projects/$(pwd | sed 's#[/.]#-#g')"
mkdir -p "$dir"
topics=(
  "checkout drawer: we decided the drawer opens from the right"
  "login test flake, branch fix/login-7, fixed and committed"
  "checkout drawer: we decided it closes on Escape and on an overlay click"
  "checkout drawer: we decided totals are rounded to cents on the server"
  "search index rebuild, PR #9 merged"
  "checkout drawer: we decided promo codes are applied in the drawer, not on the cart page"
  "dark mode tokens, branch feat/dark-3, uncommitted"
  "checkout drawer: we decided the drawer is 420px wide on desktop and full width on mobile"
  "checkout drawer: we decided the drawer state is kept in the URL hash"
  "cart totals rounding bug, planned, not started"
  "checkout drawer: we decided there is no upsell carousel in the drawer"
  "release notes for 1.4"
)
for i in "${!topics[@]}"; do
  n=$((i + 1))
  id=$(printf '0000000-0000-4000-8000-%012d' "$n")
  t="${topics[$i]}"
  f="$dir/$id.jsonl"
  {
    printf '{"type":"user","sessionId":"%s","entrypoint":"cli","message":{"role":"user","content":"work on %s"}}\n' "$id" "$t"
    printf '{"type":"assistant","sessionId":"%s","message":{"role":"assistant","content":[{"type":"text","text":"Done: %s."}]}}\n' "$id" "$t"
  } > "$f"
  python3 -I -c 'import os,sys,time; t=time.time()-int(sys.argv[2])*86400; os.utime(sys.argv[1],(t,t))' "$f" $((3 + n * 2))
done
