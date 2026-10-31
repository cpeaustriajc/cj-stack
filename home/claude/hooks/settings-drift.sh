#!/usr/bin/env bash
# SessionStart: one line per kind of drift from the sources (settings.json keys, other ~/.claude
# files), silent otherwise. Sources: this repo's home/claude/ and, for private permission entries, the
# private chezmoi repo's dot_claude/.settings-private.json.
set -euo pipefail

src="$(chezmoi source-path)/dot_claude"
public=~/Projects/dotfiles/home/claude/settings.json
live=~/.claude/settings.json
[ -s "$live" ] || live=/dev/null

# Permission lists compare as sorted lists: the merge appends private entries, and order has no effect.
keys="$(jq -rn \
  --slurpfile l "$live" \
  --slurpfile s "$public" \
  --slurpfile p "$src/.settings-private.json" \
  --slurpfile d "$src/.settings-deny.json" '
  def norm: if has("permissions") then .permissions.allow |= sort | .permissions.deny |= sort else . end;
  ($l[0] // {} | norm) as $l | $d[0] as $d
  | ($s[0] | .permissions.allow += $p[0].permissions.allow | .permissions.deny += $p[0].permissions.deny | norm) as $s
  | [ ($l | keys) + ($s | keys) | unique[]
      | . as $k | select(($d | index($k)) == null)
      | select(($l | has($k)) != ($s | has($k)) or $l[$k] != $s[$k]) ]
  | join(", ")')"

[ -z "$keys" ] || echo "settings.json: $keys differ from the sources; capture a live edit with .settings-capture.sh"

# Claude Code rewrites settings.json itself, so chezmoi always lists it; the key check above judges it.
files="$(chezmoi status ~/.claude | awk '{ p = substr($0, 4) } p != ".claude/settings.json" { printf "%s%s", (n++ ? ", " : ""), p }')"

[ -z "$files" ] || echo "chezmoi: $files differ from the source; copy a live edit into ~/Projects/dotfiles/home/claude/, or diff before apply"
