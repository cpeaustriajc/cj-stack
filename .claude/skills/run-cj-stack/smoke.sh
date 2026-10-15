#!/usr/bin/env bash
# Drives the cj-stack marketplace the way a user's Claude Code sees it.
# Usage (from the repo root): .claude/skills/run-cj-stack/smoke.sh [validate|tests|doctor|details|routing|all]
# `all` skips routing: it costs about $2 of model calls per run.
set -uo pipefail
root="$(cd "$(dirname "$0")/../../.." && pwd)"; cd "$root"
step="${1:-all}"; failed=0; blocked=0
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
    say "mod tests: $mod"; run bash -c "set -o pipefail; claude plugin test '$mod' 2>&1 | tail -3"
  done
  say "claude-owned: no mod denies or approves what Claude Code decides"
  run python3 tests/claude-owned/run.py
  say "READMEs"
  run python3 -I scripts/check_readmes.py
  say "skill descriptions: valid YAML, at most 500 characters, third person (plugin-dev's rules)"
  local py=(python3 -)
  python3 -c 'import yaml' 2>/dev/null || py=(uv run --quiet --no-project --with pyyaml python3 -)
  run "${py[@]}" <<'PY'
import glob, sys, yaml
bad = 0
for f in sorted(glob.glob("skills/*/*/SKILL.md") + glob.glob(".claude/skills/*/SKILL.md")):
    if "/archived/" in f:
        continue
    try:
        d = str(yaml.safe_load(open(f).read().split("\n---\n")[0][4:])["description"]).strip()
    except Exception as e:
        print(f"{f}: frontmatter does not parse: {e}"); bad = 1; continue
    if len(d) > 500: print(f"{f}: description is {len(d)} characters"); bad = 1
    if not d.startswith("This skill should be used"): print(f"{f}: description is not third person"); bad = 1
print("descriptions ok" if not bad else "descriptions FAILED")
sys.exit(bad)
PY
  say "script tests"
  run python3 -I skills/planning/shape/scripts/test_check_tree.py
  run bash skills/knowledge/hone/scripts/test_corrections.sh
}

doctor() {
  say "/skill-doctor with cj-stack installed"; installed
  local out; out="$(CLAUDE_CONFIG_DIR="$cfg" claude -p '/skill-doctor' --max-budget-usd 1 2>&1)"; local st=$?
  if grep -q 'Not logged in' <<<"$out"; then echo "BLOCKED: the throwaway config is not signed in"; blocked=1; return; fi
  grep -v anthropic-skills <<<"$out"; [[ $st -eq 0 ]] || { failed=1; echo "FAILED: /skill-doctor exit $st"; }
}

details() { say "plugin details"; installed; run env CLAUDE_CONFIG_DIR="$cfg" claude plugin details cj-stack; }

# The marketplace entry has no plugin.json, so `claude plugin eval .` resolves no plugin. Build a
# throwaway plugin of symlinks to the shipped skills, named cj-stack, and evaluate that.
routing() {
  say "routing evals: each request loads its own skill and no neighbour"
  local p; p="$(mktemp -d)"; mkdir -p "$p/.claude-plugin" "$p/skills" "$p/evals"
  local list; list="$(python3 -c "import json;print('\n'.join(json.load(open('skills/.claude-plugin/plugin.json'))['skills']))")" || { failed=1; echo "FAILED: read skills/.claude-plugin/plugin.json"; return; }
  while read -r s; do ln -s "$root/skills/${s#./}" "$p/skills/$(basename "$s")"; done <<<"$list"
  [[ -n "$(ls "$p/skills")" ]] || { failed=1; echo "FAILED: no skills linked into the eval plugin"; return; }
  # In-progress skills with routing cases join the eval plugin only; they still don't ship.
  for s in drive scout; do ln -s "$root/skills/in-progress/$s" "$p/skills/$s"; done
  echo '{"name":"cj-stack","version":"0.0.0-eval"}' > "$p/.claude-plugin/plugin.json"
  cp -r skills/evals/. "$p/evals/"
  (cd "$p" && claude plugin eval . --eval-dir evals --runs "${RUNS:-2}" --ablation none \
    --trust-plugin --no-publish --max-cost-usd 10 -j 4) || { failed=1; echo "FAILED: routing evals"; }
  rm -rf "$p"
}

case "$step" in
  validate|tests|doctor|details|routing) "$step" ;;
  all) validate; tests; details; doctor ;;
  *) echo "usage: $0 [validate|tests|doctor|details|routing|all]" >&2; exit 64 ;;
esac
find skills -name __pycache__ -prune -exec rm -rf {} +
(( failed )) && exit 1
(( blocked )) && exit 2
exit 0
