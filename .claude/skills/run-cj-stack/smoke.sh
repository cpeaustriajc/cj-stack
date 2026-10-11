#!/usr/bin/env bash
# Drives the cj-stack marketplace the way a user's Claude Code sees it.
# Usage (from the repo root): .claude/skills/run-cj-stack/smoke.sh [validate|tests|doctor|details|routing|all]
# `all` skips routing: it costs about $1 of model calls per run.
set -uo pipefail
root="$(cd "$(dirname "$0")/../../.." && pwd)"; cd "$root"
step="${1:-all}"; failed=0
say() { printf '\n== %s\n' "$*"; }
run() { "$@" || { failed=1; echo "FAILED: $*"; }; }

# A throwaway config dir with the local marketplace installed, so the real ~/.claude is untouched.
installed() {
  [[ -n "${cfg:-}" ]] && return
  cfg="$(mktemp -d)"; trap 'rm -rf "$cfg"' EXIT
  CLAUDE_CONFIG_DIR="$cfg" claude plugin marketplace add "$root" >/dev/null
  CLAUDE_CONFIG_DIR="$cfg" claude plugin install cj-stack@cj-stack >/dev/null
}

validate() { say "validate"; run claude plugin validate .; }

tests() {
  for mod in mods/*/; do
    compgen -G "$mod/hooks/*.test.ts*" >/dev/null || continue
    say "mod tests: $mod"; run bash -c "claude plugin test '$mod' 2>&1 | tail -3"
  done
  say "script tests"
  run python3 -I skills/planning/shape/scripts/test_check_tree.py
  run bash skills/knowledge/hone/scripts/test_corrections.sh
}

doctor() {
  say "/skill-doctor with cj-stack installed"; installed
  run bash -c "CLAUDE_CONFIG_DIR='$cfg' claude -p '/skill-doctor' --max-budget-usd 1 | grep -v anthropic-skills"
}

details() { say "plugin details"; installed; run env CLAUDE_CONFIG_DIR="$cfg" claude plugin details cj-stack; }

# The marketplace entry has no plugin.json, so `claude plugin eval .` resolves no plugin. Build a
# throwaway plugin of symlinks to the shipped skills, named cj-stack, and evaluate that.
routing() {
  say "routing evals: each request loads its own skill and no sibling"
  local p; p="$(mktemp -d)"; mkdir -p "$p/.claude-plugin" "$p/skills" "$p/evals"
  python3 -c "import json;m=json.load(open('.claude-plugin/marketplace.json'));print('\n'.join(next(x for x in m['plugins'] if x['name']=='cj-stack')['skills']))" |
    while read -r s; do ln -s "$root/${s#./}" "$p/skills/$(basename "$s")"; done
  echo '{"name":"cj-stack","version":"0.0.0-eval"}' > "$p/.claude-plugin/plugin.json"
  cp -r evals/routing "$p/evals/"
  (cd "$p" && claude plugin eval . --eval-dir evals/routing --runs "${RUNS:-2}" --ablation none \
    --trust-plugin --no-publish --max-cost-usd 10 -j 4) || { failed=1; echo "FAILED: routing evals"; }
  rm -rf "$p"
}

case "$step" in
  validate|tests|doctor|details|routing) "$step" ;;
  all) validate; tests; details; doctor ;;
  *) echo "usage: $0 [validate|tests|doctor|details|routing|all]" >&2; exit 2 ;;
esac
find skills -name __pycache__ -prune -exec rm -rf {} +
exit $failed
