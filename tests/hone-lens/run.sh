#!/usr/bin/env bash
# Runs the lens cases with `claude plugin eval` against a no-plugin baseline; about $0.50 per run.
# Usage from the repo root: tests/hone-lens/run.sh [git-ref]
# A git-ref evaluates hone as it was at that ref, for a before/after comparison.
set -euo pipefail
root="$(git rev-parse --show-toplevel)"; p="$(mktemp -d)"; trap 'rm -rf "$p"' EXIT
mkdir -p "$p/.claude-plugin" "$p/skills" "$p/evals"
# Copies, not symlinks: the eval sandbox refuses reads through a link to the repo.
while read -r s; do cp -R "$root/skills/${s#./}" "$p/skills/"; done \
  < <(python3 -I -c "import json,sys;print('\n'.join(json.load(open(sys.argv[1]))['skills']))" "$root/skills/.claude-plugin/plugin.json")
if [[ -n "${1:-}" ]]; then
  rm -rf "$p/skills/hone"; mkdir -p "$p/old"
  git -C "$root" archive "$1" skills/knowledge/hone | tar -x -C "$p/old"
  mv "$p/old/skills/knowledge/hone" "$p/skills/hone"
fi
echo '{"name":"cj-stack","version":"0.0.0-eval"}' > "$p/.claude-plugin/plugin.json"
cp -R "$root/tests/hone-lens/cases/." "$p/evals/"
out="$root/.claude/work/hone-lens"; label="$(tr '/' '-' <<<"${1:-current}")"; mkdir -p "$out"
(cd "$p" && claude plugin eval . --eval-dir evals --runs "${RUNS:-2}" --scaffold --allow-tools Bash \
  --judge-model sonnet --trust-plugin --no-publish --max-cost-usd 15 -j 4 --threshold 0 ${CASE:+--case "$CASE"} \
  --json "$out/lens-$label.json" --report "$out/lens-$label.html") 2>&1 | tee "$out/lens-$label.log"
