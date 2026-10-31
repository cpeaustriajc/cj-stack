#!/usr/bin/env bash
# Usage (from the repo root): plugins/engineering/skills/drive/evals/handback/run.sh [results dir]
# Copies, not symlinks: the eval sandbox can't read a reference file through a link.
set -euo pipefail
root="$(pwd)"; here="$root/plugins/engineering/skills/drive/evals/handback"
out="${1:-$root/.claude/work/drive-handback-eval}"; mkdir -p "$out"
p="$(mktemp -d)"; mkdir -p "$p/.claude-plugin" "$p/skills" "$p/evals"
for d in "$root"/plugins/*/skills/*/; do cp -RL "${d%/}" "$p/skills/$(basename "$d")"; done
cp -RL "$root/plugins/engineering/skills/drive" "$p/skills/drive"
echo '{"name":"dotfiles","version":"0.0.0-eval"}' > "$p/.claude-plugin/plugin.json"
cp -R "$here/drive-audit-unrun-step" "$here/drive-audit-clean" "$p/evals/"
cd "$p" && claude plugin eval . --eval-dir evals --ablation none --scaffold --allow-tools Bash \
  --trust-plugin --no-publish --max-cost-usd 5 -j 2 \
  --output-dir "$out/results" --report "$out/report.html" --json "$out/result.json"
