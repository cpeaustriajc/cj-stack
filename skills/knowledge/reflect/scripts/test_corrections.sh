#!/usr/bin/env bash
# Re-runnable check: a correction and an interrupt are found, and a half-written line is skipped.
set -euo pipefail
dir="$(cd "$(dirname "$0")" && pwd)"; tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/root/-proj"
cat > "$tmp/root/-proj/s.jsonl" <<'J'
{"type":"assistant","message":{"content":[{"type":"text","text":"Should I add a retry?"}]}}
{"type":"user","message":{"content":"no, I already said we fix the source"}}
{"type":"assistant","message":{"content":[{"type":"text","text":"Running it"}]}}
{"type":"user","message":{"content":"[Request interrupted by user]"}}
{"type":"user","message":{"content":"half writ
J
summary="$(python3 -I "$dir/corrections.py" --root "$tmp/root" --out "$tmp/out.md" | tail -1)"
grep -q '^### REPLY' "$tmp/out.md" && grep -q '^### INTERRUPT' "$tmp/out.md" && [[ "$summary" == *"1 unreadable lines skipped"* ]] \
  && echo "PASS" || { echo "FAIL: $summary"; cat "$tmp/out.md"; exit 1; }
