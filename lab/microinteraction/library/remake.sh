#!/usr/bin/env bash
# Re-makes every example GIF and frame sheet from its demo page.
# Needs node, the playwright npm package (global or local) with Chromium, and ffmpeg.
# Usage: bash remake.sh [effect ...]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
export NODE_PATH="${NODE_PATH:-}:$(npm root -g)"
max_kb=150
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

effects=("$@")
if [ ${#effects[@]} -eq 0 ]; then
  for d in "$here"/*/; do [ -f "$d/good.html" ] && effects+=("$(basename "$d")"); done
fi

status=0
for effect in "${effects[@]}"; do
  for version in good bad; do
    demo="$here/$effect/$version.html"
    work="$tmp/$effect-$version"
    node "$here/record.cjs" "$demo" "$work"
    ffmpeg -loglevel error -y -framerate 50 -i "$work/frames/%04d.png" \
      -vf "split[a][b];[a]palettegen=max_colors=64:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle" \
      -loop 0 "$here/$effect/$version.gif"
    ffmpeg -loglevel error -y -i "$work/sheet/%02d.png" -i "$work/plot.png" \
      -filter_complex "[0]scale=240:-1,tile=4x3:padding=4:color=white,scale=480:-1[t];[t][1]vstack" \
      -frames:v 1 -update 1 "$here/$effect/$version-frames.png"
    cp "$work/samples.json" "$here/$effect/$version-samples.json"
    kb=$(( $(wc -c < "$here/$effect/$version.gif") / 1024 ))
    width=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$here/$effect/$version.gif")
    if [ "$kb" -gt "$max_kb" ] || [ "$width" -gt 480 ]; then
      echo "FAIL $effect/$version.gif: ${width}px, ${kb} KB (limit 480px, ${max_kb} KB)"; status=1
    else
      echo "ok   $effect/$version.gif: ${width}px, ${kb} KB"
    fi
  done
done
exit $status
