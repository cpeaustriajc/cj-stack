#!/bin/sh
# usage: build_formats.sh MASTER_PROJECT_DIR
# Generates MASTER-1x1 and MASTER-16x9 beside the master: copies the project (without renders,
# snapshots, capture), then rewrites the root size, data-format, body size and viewport in index.html.
# The master's root must carry: data-width="1080" data-height="1920" data-format="9x16", and its CSS
# "html, body { margin: 0; width: 1080px; height: 1920px;". See references/hyperframes.md.
set -e
[ -n "$1" ] || { sed -n 2,6p "$0"; exit 1; }
M="$(cd "$1" && pwd)"
for spec in 1x1:1080:1080 16x9:1920:1080; do
  f=${spec%%:*}; rest=${spec#*:}; w=${rest%%:*}; h=${rest#*:}
  D="$M-$f"; mkdir -p "$D"
  rsync -a --delete --exclude renders --exclude snapshots --exclude capture --exclude index.html "$M/" "$D/"
  sed -e "s/data-width=\"1080\" data-height=\"1920\" data-format=\"9x16\"/data-width=\"$w\" data-height=\"$h\" data-format=\"$f\"/" \
      -e "s/html, body { margin: 0; width: 1080px; height: 1920px;/html, body { margin: 0; width: ${w}px; height: ${h}px;/" \
      -e "s/content=\"width=1080, height=1920\"/content=\"width=$w, height=$h\"/" "$M/index.html" > "$D/index.html"
  grep -q "data-format=\"$f\"" "$D/index.html" && grep -q "width: ${w}px; height: ${h}px" "$D/index.html" || { echo "[$f] master is missing the expected markers"; exit 1; }
  echo "[$f] ✔ $D"
done
