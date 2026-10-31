#!/usr/bin/env bash
# Drives the dotfiles marketplace the way a user's Claude Code sees it.
# Usage (from the repo root): .claude/skills/run-dotfiles/smoke.sh [validate|tests|doctor|details|routing|all]
# `all` skips routing: it costs about $2 of model calls per run.
set -uo pipefail
root="$(cd "$(dirname "$0")/../../.." && pwd)"; cd "$root"
step="${1:-all}"; failed=0; blocked=0
say() { printf '\n== %s\n' "$*"; }
run() { "$@" || { failed=1; echo "FAILED: $*"; }; }
# The skill plugins: one folder each under plugins/, with its skills in plugins/<plugin>/skills/.
plugins=(); for d in plugins/*/; do plugins+=("$(basename "$d")"); done

# A throwaway config dir with the local marketplace installed, so the real ~/.claude is untouched.
installed() {
  [[ -n "${cfg:-}" ]] && return
  cfg="$(mktemp -d)"; trap 'rm -rf "$cfg"' EXIT
  CLAUDE_CONFIG_DIR="$cfg" claude plugin marketplace add "$root" >/dev/null
  for p in "${plugins[@]}"; do CLAUDE_CONFIG_DIR="$cfg" claude plugin install "$p@dotfiles" >/dev/null; done
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
  run python3 -I scripts/test_check_readmes.py
  say "skill descriptions: valid YAML, at most 500 characters, third person (plugin-dev's rules)"
  local py=(python3 -)
  python3 -c 'import yaml' 2>/dev/null || py=(uv run --quiet --no-project --with pyyaml python3 -)
  run "${py[@]}" <<'PY'
import glob, sys, yaml
bad = 0
for f in sorted(glob.glob("plugins/*/skills/*/SKILL.md") + glob.glob(".claude/skills/*/SKILL.md")):
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
  run python3 -I plugins/planning/skills/shape/scripts/test_check_tree.py
  run bash plugins/knowledge/skills/hone/scripts/test_corrections.sh
  run python3 -I plugins/engineering/skills/architect/scripts/test_moves_only.py
}

doctor() {
  say "/skill-doctor with the skill plugins installed"; installed
  local ref='op://Personal/Claude Code OAuth token/credential' token="${CLAUDE_CODE_OAUTH_TOKEN:-}"
  if [[ -z "$token" ]] && ! token="$(op read "$ref" 2>&1)"; then
    echo "BLOCKED: CLAUDE_CODE_OAUTH_TOKEN is not set and \`op read '$ref'\` failed: $token"; blocked=1; return
  fi
  local out; out="$(CLAUDE_CODE_OAUTH_TOKEN="$token" CLAUDE_CONFIG_DIR="$cfg" claude -p '/skill-doctor' --max-budget-usd 1 2>&1)"; local st=$?
  if grep -qE 'Not logged in|Failed to authenticate' <<<"$out"; then echo "BLOCKED: the token was refused; run \`claude setup-token\` and save the new token at $ref"; blocked=1; return; fi
  grep -v anthropic-skills <<<"$out"; [[ $st -eq 0 ]] || { failed=1; echo "FAILED: /skill-doctor exit $st"; }
}

details() { say "plugin details"; installed; for p in "${plugins[@]}"; do run env CLAUDE_CONFIG_DIR="$cfg" claude plugin details "$p@dotfiles"; done; }

# The marketplace entry has no plugin.json, so `claude plugin eval .` resolves no plugin. Build a
# throwaway plugin of symlinks to the shipped skills, named dotfiles, and evaluate that.
routing() {
  say "routing evals: each request loads its own skill and no neighbour"
  local p; p="$(mktemp -d)"; mkdir -p "$p/.claude-plugin" "$p/skills" "$p/evals"
  # A skill with its own cases is copied, not linked: eval finds cases anywhere in the plugin, and
  # the filter below deletes some, which through a link would delete them from the repo.
  for d in "$root"/plugins/*/skills/*/; do
    if [[ -n "$(find "$d" -name case.yaml -print -quit)" ]]; then cp -R "${d%/}" "$p/skills/$(basename "$d")"
    else ln -s "${d%/}" "$p/skills/$(basename "$d")"; fi
  done
  [[ -n "$(ls "$p/skills")" ]] || { failed=1; echo "FAILED: no skills linked into the eval plugin"; return; }
  echo '{"name":"dotfiles","version":"0.0.0-eval"}' > "$p/.claude-plugin/plugin.json"
  cp -r evals/routing/. "$p/evals/"
  # Cases with a scaffold_script test behaviour, not routing, and fail without --scaffold.
  grep -rl --include=case.yaml scaffold_script "$p"/evals "$p"/skills 2>/dev/null |
    while read -r c; do rm -rf "$(dirname "$c")"; done
  (cd "$p" && claude plugin eval . --eval-dir evals --runs "${RUNS:-2}" --ablation none \
    --trust-plugin --no-publish --max-cost-usd 10 -j 4) || { failed=1; echo "FAILED: routing evals"; }
  rm -rf "$p"
}

case "$step" in
  validate|tests|doctor|details|routing) "$step" ;;
  all) validate; tests; details; doctor ;;
  *) echo "usage: $0 [validate|tests|doctor|details|routing|all]" >&2; exit 64 ;;
esac
find plugins -name __pycache__ -prune -exec rm -rf {} +
(( failed )) && exit 1
(( blocked )) && exit 2
exit 0
