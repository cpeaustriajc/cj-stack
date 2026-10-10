#!/usr/bin/env bash
# Re-runnable check of corrections.py: every case writes a transcript, runs the script, asserts on the output.
set -uo pipefail
dir="$(cd "$(dirname "$0")" && pwd)"; tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
pass=0; fail=0

# run <name> <transcript-lines> [extra args]: sets $out (markdown) and $summary (last line)
run() {
  local name="$1" lines="$2"; shift 2
  rm -rf "$tmp/root"; mkdir -p "$tmp/root/-proj"; printf '%s\n' "$lines" > "$tmp/root/-proj/s.jsonl"
  summary="$(python3 -I "$dir/corrections.py" --root "$tmp/root" --out "$tmp/out.md" "$@" | tail -1)"
  out="$(cat "$tmp/out.md")"
}
# check <case> <expected hits> [needle...]: hits must match the count and every needle must appear
check() {
  local case="$1" want="$2"; shift 2
  local got; got="$(grep -c '^### ' "$tmp/out.md")"; local ok=1
  [[ "$got" == "$want" ]] || ok=0
  for n in "$@"; do [[ "$out" == *"$n"* ]] || ok=0; done
  if (( ok )); then pass=$((pass+1)); echo "ok   $case"; else fail=$((fail+1)); echo "FAIL $case (hits $got, want $want): $summary"; fi
}

A='{"type":"assistant","message":{"content":[{"type":"text","text":"Running it"}]}}'
U() { printf '{"type":"user","message":{"content":"%s"}}' "$1"; }
SK() { printf '{"type":"assistant","message":{"content":[{"type":"tool_use","id":"t1","name":"Skill","input":{"skill":"%s"}}]}}' "$1"; }
CMD() { printf '{"type":"user","message":{"content":"<command-name>%s</command-name>"}}' "$1"; }
NL=$'\n'

# without --skill: unchanged behaviour, half-written last line skipped
run base "$(printf '%s\n%s\n%s\n%s\n%s' \
 '{"type":"assistant","message":{"content":[{"type":"text","text":"Should I add a retry?"}]}}' \
 "$(U 'no, I already said we fix the source')" "$A" "$(U '[Request interrupted by user]')" '{"type":"user","message":{"content":"half writ')"
[[ "$out" == *"### REPLY"* && "$out" == *"### INTERRUPT"* && "$summary" == *"1 unreadable lines skipped"* ]] \
  && { pass=$((pass+1)); echo "ok   base"; } || { fail=$((fail+1)); echo "FAIL base: $summary"; }

for form in "cj-stack:ui-polish" "ui-polish"; do
  run "tool $form" "$(SK "$form")${NL}$A${NL}$(U 'no, wrong easing')" --skill ui-polish
  check "tool_use $form matches ui-polish" 1 "wrong easing"
done
run "flag prefixed" "$(SK ui-polish)${NL}$A${NL}$(U 'no, wrong easing')" --skill cj-stack:ui-polish
check "prefixed --skill value matches" 1 "wrong easing"

for form in "/ui-polish" "/cj-stack:ui-polish"; do
  run "cmd $form" "$(CMD "$form")${NL}$A${NL}$(U 'no, wrong easing')" --skill ui-polish
  check "slash command $form starts the skill" 1 "wrong easing"
done

run before "$A${NL}$(U 'no, before the skill')${NL}$(SK ui-polish)" --skill ui-polish
check "correction before the skill started is excluded" 0

run switched "$(SK ui-polish)${NL}$A${NL}$(U 'no, mid skill')${NL}$(SK cj-stack:break-it)${NL}$A${NL}$(U 'no, after the switch')" --skill ui-polish
check "only the span before another skill took over" 1 "mid skill"
[[ "$out" != *"after the switch"* ]] || { fail=$((fail+1)); echo "FAIL switched leaked"; }

run switched-cmd "$(SK ui-polish)${NL}$(CMD /break-it)${NL}$A${NL}$(U 'no, after the switch')" --skill ui-polish
check "a slash command for another skill ends the span" 0

run never "$A${NL}$(U 'no, nothing ran')" --skill ui-polish
check "session that never used the skill yields nothing" 0

run other "$(SK break-it)${NL}$A${NL}$(U 'no, other skill')" --skill ui-polish
check "a different skill alone yields nothing" 0

run kinds "$(SK ui-polish)${NL}$A${NL}$(U '[Request interrupted by user]')" --skill ui-polish
check "an interrupt inside the span is kept" 1 "### INTERRUPT"

run junk "$(SK ui-polish)${NL}not json at all${NL}$A${NL}$(U 'no, still found')${NL}"'{"type":"user","message":{"content":"trunc' --skill ui-polish
check "malformed and truncated lines are skipped, span survives" 1 "still found"
[[ "$summary" == *"2 unreadable lines skipped"* ]] || { fail=$((fail+1)); echo "FAIL junk count: $summary"; }

echo "$pass passed, $fail failed"; (( fail == 0 ))
