#!/usr/bin/env bash
# Copies the live ~/.claude/settings.json values of the synced keys into
# ~/Projects/dotfiles/home/dot_claude/.settings.json. The synced keys are the keys of that file:
# to sync a new key, add it there by hand first. Every other live key stays on this machine.
set -euo pipefail

public=~/Projects/dotfiles/home/dot_claude/.settings.json
tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

jq --slurpfile l ~/.claude/settings.json \
  'with_entries(.key as $k | .value = (if $l[0] | has($k) then $l[0][$k] else .value end))' \
  "$public" > "$tmp"

cp "$tmp" "$public"
git -C "$(dirname "$public")" --no-pager diff --stat -- .settings.json
