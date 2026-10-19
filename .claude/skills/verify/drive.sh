#!/usr/bin/env bash
# Runs feature<TAB>command lines from stdin, one log each, and prints `[i/n] ✔|✘ feature (Ns)`.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
dir=".claude/work/verify/$(git rev-parse --short HEAD)"
mkdir -p "$dir"
rows=()
while IFS= read -r row; do [[ "$row" == *$'\t'* ]] && rows+=("$row"); done
total=${#rows[@]}
(( total )) || { echo "no features selected"; exit 0; }
failed=0 i=0
for row in "${rows[@]}"; do
  i=$((i + 1)) feature="${row%%$'\t'*}" cmd="${row#*$'\t'}"
  log="$dir/${feature// /-}.log" start=$SECONDS
  bash -c "$cmd" < /dev/null 2>&1 | tee "$log"
  status=${PIPESTATUS[0]}
  if (( status == 0 )); then line="[$i/$total] ✔ $feature ($((SECONDS - start))s)"
  else line="[$i/$total] ✘ $feature ($((SECONDS - start))s, exit $status)"; failed=1; fi
  echo "$line" | tee -a "$log"
done
echo "evidence: $dir"
exit $failed
