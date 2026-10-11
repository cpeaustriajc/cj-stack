#!/usr/bin/env bash
# Drives the cj-stack marketplace the way a user's Claude Code sees it.
# Usage (from the repo root): .claude/skills/run-cj-stack/smoke.sh [validate|tests|doctor|details|all]
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

case "$step" in
  validate|tests|doctor|details) "$step" ;;
  all) validate; tests; details; doctor ;;
  *) echo "usage: $0 [validate|tests|doctor|details|all]" >&2; exit 2 ;;
esac
find skills -name __pycache__ -prune -exec rm -rf {} +
exit $failed
