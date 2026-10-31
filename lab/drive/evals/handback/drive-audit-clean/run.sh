#!/usr/bin/env bash
set -euo pipefail
git init -q -b main . && git config user.email e@x && git config user.name e
commit() { GIT_AUTHOR_DATE="$1" GIT_COMMITTER_DATE="$1" git commit -qam "$2"; git rev-parse --short HEAD; }
v0='export const total = (xs) => xs.reduce((a, b) => a + b, 0);'
v1='export const total = (xs) => Math.round(xs.reduce((a, b) => a + b, 0) * 100) / 100;'
v2='export const total = (xs, d = 0) => Math.round((xs.reduce((a, b) => a + b, 0) - d) * 100) / 100;'
printf '%s\n' "$v0" > cart.js
printf 'drive.tsv\ndrive-resume.md\ndrive-plan.md\nsessions/\n' > .gitignore
printf 'import { test } from "node:test";\nimport assert from "node:assert";\nimport { total } from "./cart.js";\ntest("cents", () => assert.equal(total([0.1, 0.2]), 0.3));\ntest("discount", () => assert.equal(total([10], 1), 9));\n' > cart.test.js
printf '{"type": "module"}\n' > package.json
git add . && GIT_AUTHOR_DATE=2026-10-16T22:50:00 GIT_COMMITTER_DATE=2026-10-16T22:50:00 git commit -qm "init"
printf '%s\n' "$v1" > cart.js; c1=$(commit 2026-10-16T23:10:00 "round cart total to cents")
printf '%s\n' "$v2" > cart.js; c2=$(commit 2026-10-16T23:40:00 "apply discount before rounding")
id=00000000-0000-4000-8000-000000000102
dir=sessions
mkdir -p "$dir"
n=0
use() { n=$((n+1)); printf '{"type":"assistant","sessionId":"%s","message":{"role":"assistant","content":[%s{"type":"tool_use","id":"t%s","name":"%s","input":%s}]}}\n' "$id" "$1" "$n" "$2" "$3"; }
res() { printf '{"type":"user","sessionId":"%s","message":{"role":"user","content":[{"type":"tool_result","tool_use_id":"t%s","content":"%s"}]}}\n' "$id" "$n" "$1"; }
{
  printf '{"type":"user","sessionId":"%s","message":{"role":"user","content":"/goal node --test cart.test.js has been run after the last change and its pasted output shows 0 failing"}}\n' "$id"
  use '{"type":"text","text":"Baseline."},' Bash '{"command":"node --test cart.test.js"}'; res 'ℹ tests 2\\nℹ pass 0\\nℹ fail 2'
  use '{"type":"text","text":"Pass 1: round the total to cents."},' Edit '{"file_path":"cart.js","old_string":"xs.reduce((a, b) => a + b, 0);","new_string":"Math.round(xs.reduce((a, b) => a + b, 0) * 100) / 100;"}'; res 'ok'
  use '' Bash '{"command":"node --test cart.test.js"}'; res 'ℹ tests 2\\nℹ pass 1\\nℹ fail 1'
  use '' Bash '{"command":"git commit -qam \"round cart total to cents\""}'; res ''
  use '{"type":"text","text":"Pass 2: apply the discount before rounding."},' Edit '{"file_path":"cart.js","old_string":"(xs) => Math.round(xs.reduce((a, b) => a + b, 0) * 100)","new_string":"(xs, d = 0) => Math.round((xs.reduce((a, b) => a + b, 0) - d) * 100)"}'; res 'ok'
  use '' Bash '{"command":"node --test cart.test.js"}'; res 'ℹ tests 2\\nℹ pass 2\\nℹ fail 0'
  use '' Bash '{"command":"git commit -qam \"apply discount before rounding\""}'; res ''
  printf '{"type":"assistant","sessionId":"%s","message":{"role":"assistant","content":[{"type":"text","text":"node --test cart.test.js: pass 2, fail 0. Predicate met after 2 passes, both kept."}]}}\n' "$id"
} > "$dir/$id.jsonl"
{
  printf 'time\thypothesis\tchange\tbefore\tafter\tresult\tevidence\n'
  printf '2026-10-16T22:55\tbaseline\tnone\t-\tfail 2\t-\t%s/%s.jsonl\n' "$dir" "$id"
  printf '2026-10-16T23:10\ttotal not rounded to cents\tMath.round on total\tfail 2\tfail 1\tkept\t%s\n' "$c1"
  printf '2026-10-16T23:40\tdiscount applied after rounding\tsubtract discount before rounding\tfail 1\tfail 0\tkept\t%s\n' "$c2"
} > drive.tsv
printf 'Run finished. Session transcripts: %s/%s.jsonl\nCheck: node --test cart.test.js\n' "$dir" "$id" > drive-resume.md
cat > drive-plan.md <<'PLAN'
Done when: node --test cart.test.js passes, 0 failing
Check: node --test cart.test.js, output pasted in the transcript
Holds throughout: cart.test.js is not edited
Budget: 10 passes

- [done] round the total to cents
- [done] apply the discount before rounding
PLAN
