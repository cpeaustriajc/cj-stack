#!/usr/bin/env bash
# Symlinks the shipped skills for agents that read a skills folder (default ~/.agents/skills).
# Never point it at ~/.claude/skills: the plugin already lists them there, and a link lists each twice.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
target="${1:-$HOME/.agents/skills}"
mkdir -p "$target"
for dir in "$root"/skills/planning/*/ "$root"/skills/knowledge/*/ "$root"/skills/quality/*/ "$root"/skills/shipping/*/; do
  name="$(basename "$dir")"
  ln -sfn "${dir%/}" "$target/$name"
  echo "linked $name -> $target/$name"
done
