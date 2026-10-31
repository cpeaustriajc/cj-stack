#!/usr/bin/env bash
# SessionStart: one line per kind of drift from the sources (synced settings.json keys, other
# ~/.claude files), silent otherwise. Source: this repo's home/claude/. Only the keys of
# home/claude/settings.json are synced; other live keys belong to the machine.
set -euo pipefail

public=~/Projects/dotfiles/home/claude/settings.json
live=~/.claude/settings.json
[ -s "$live" ] || live=/dev/null

keys="$(jq -rn --slurpfile l "$live" --slurpfile s "$public" '
  ($l[0] // {}) as $l | $s[0] as $s
  | [ $s | keys[] | . as $k | select(($l | has($k) | not) or $l[$k] != $s[$k]) ]
  | join(", ")')"

[ -z "$keys" ] || echo "settings.json: $keys differ from the sources; capture a live edit with .settings-capture.sh"

# Claude Code rewrites settings.json itself, so chezmoi always lists it; the key check above judges it.
files="$(chezmoi status ~/.claude | awk '{ p = substr($0, 4) } p != ".claude/settings.json" { printf "%s%s", (n++ ? ", " : ""), p }')"

[ -z "$files" ] || echo "chezmoi: $files differ from the source; copy a live edit into ~/Projects/dotfiles/home/claude/, or diff before apply"
