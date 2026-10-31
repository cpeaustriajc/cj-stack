#!/usr/bin/env bash
set -euo pipefail
git init -q -b main . && git config user.email dev@shop.test && git config user.name "Ana Reyes"
mkdir -p scripts
cat > scripts/budget.mjs <<'JS'
// Counts the files that import protos and compares the count with budget.json.
import { readFileSync, writeFileSync } from "node:fs"
const budget = JSON.parse(readFileSync("budget.json", "utf8")).max
const count = Number(process.env.PROTO_COUNT ?? 0)
if (process.argv.includes("--write")) writeFileSync("budget.json", JSON.stringify({ max: count }))
else if (count > budget) process.exit(1)
JS
echo '{ "max": 412 }' > budget.json
cat > CONTRIBUTING.md <<'MD'
# Contributing

## Docs

- Name a script by the command that runs it from the repo root, for example `node scripts/budget.mjs`.
- Call the CI job that runs the budget check `proto-budget`. Do not call it "CI" or "the pipeline".
MD
cat > README.md <<'MD'
# shop

## Proto budget

Configuration of the proto import ratchet budget script parameters is performed via budget.json. Note that it's important to remember that running with --write, which updates the committed budget to reflect the current count, should only be done when lowering it; if exceeded, CI fails.
MD
git add . && git commit -qm "init"
