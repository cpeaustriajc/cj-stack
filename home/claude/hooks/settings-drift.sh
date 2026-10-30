#!/usr/bin/env bash
# SessionStart: one line per kind of drift from chezmoi (settings.json keys, other ~/.claude files),
# silent otherwise.
set -euo pipefail

src="$(chezmoi source-path)/dot_claude"
live=~/.claude/settings.json
[ -s "$live" ] || live=/dev/null

keys="$(jq -rn \
  --slurpfile l "$live" \
  --slurpfile s "$src/.settings-shared.json" \
  --slurpfile d "$src/.settings-deny.json" '
  ($l[0] // {}) as $l | $s[0] as $s | $d[0] as $d
  | [ ($l | keys) + ($s | keys) | unique[]
      | . as $k | select(($d | index($k)) == null)
      | select(($l | has($k)) != ($s | has($k)) or $l[$k] != $s[$k]) ]
  | join(", ")')"

[ -z "$keys" ] || echo "settings.json: $keys differ from chezmoi"

# Claude Code rewrites settings.json itself, so chezmoi always lists it; the key check above judges it.
files="$(chezmoi status ~/.claude | awk '{ p = substr($0, 4) } p != ".claude/settings.json" { printf "%s%s", (n++ ? ", " : ""), p }')"

[ -z "$files" ] || echo "chezmoi: $files differ from the source; re-add a live edit, or diff before apply"
