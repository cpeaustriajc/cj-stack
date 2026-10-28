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

# header names the session: s= plus the first 8 chars of the transcript file name
rm -rf "$tmp/root"; mkdir -p "$tmp/root/-proj"
printf '%s\n%s\n' '{"type":"assistant","message":{"content":[{"type":"text","text":"Should I add a retry?"}]}}' "$(U 'no, I already said we fix the source')" > "$tmp/root/-proj/abcdef12-3456.jsonl"
python3 -I "$dir/corrections.py" --root "$tmp/root" --out "$tmp/out.md" >/dev/null
[[ "$(head -1 "$tmp/out.md")" == "### REPLY s=abcdef12 -proj" ]] \
  && { pass=$((pass+1)); echo "ok   header carries s= and 8 chars of the session id"; } || { fail=$((fail+1)); echo "FAIL header carries s= and 8 chars of the session id: $(head -1 "$tmp/out.md")"; }

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

Q='{"type":"assistant","message":{"content":[{"type":"tool_use","id":"q1","name":"AskUserQuestion","input":{"questions":[]}}]}}'
QA() { printf '{"type":"user","message":{"content":[{"type":"tool_result","tool_use_id":"q1","content":"Your questions have been answered: \\"Which?\\"=\\"%s\\". You can now continue."}]}}' "$1"; }

run ask-default "$Q${NL}$(QA 'Ship it (Recommended)')"
check "a form answered with every recommended option is not a correction" 0

run ask-multi "$Q${NL}$(QA 'break-it (Recommended), grill-me upgrades')"
check "a multi-select that adds a non-recommended option is kept" 1 "grill-me upgrades"

run ask-own "$Q${NL}$(QA 'keep it in notion')"
check "a non-recommended or typed answer is kept" 1 "keep it in notion"

AQ='{"type":"assistant","message":{"content":[{"type":"text","text":"Should I continue?"}]}}'
run peer "$AQ${NL}$(U 'Another Claude session sent a message:\n<cross-session-message from=\"x\">no, stop that</cross-session-message>')"
check "a message from another Claude session is not the user's correction" 0

run stophook "$A${NL}$(U 'Stop hook feedback:\n[Run ui-polish]: the goal is not satisfied')"
check "stop hook feedback is kept, labelled as a hook" 1 "### HOOK" "goal is not satisfied"

run resumed "$A${NL}$(U 'no, I already said we fix the source')"
cp "$tmp/root/-proj/s.jsonl" "$tmp/root/-proj/resumed.jsonl"
summary="$(python3 -I "$dir/corrections.py" --root "$tmp/root" --out "$tmp/out.md" | tail -1)"; out="$(cat "$tmp/out.md")"
check "a resumed session repeating the same exchange is written once" 1 "fix the source"

# --turns: every turn, corrected or not, with its tool calls, for the lens pass
BASH() { printf '{"type":"assistant","message":{"content":[{"type":"tool_use","id":"b1","name":"Bash","input":{"command":"%s"}}]}}' "$1"; }
DONE='{"type":"assistant","message":{"content":[{"type":"text","text":"Done, the tests pass."}]}}'
SIDE='{"type":"assistant","isSidechain":true,"message":{"content":[{"type":"tool_use","id":"s1","name":"Bash","input":{"command":"sidechain-only"}}]}}'
run turns "$(U 'add the export button')${NL}$(BASH 'npm run lint')${NL}$(SK release-notes)${NL}$SIDE${NL}$DONE${NL}$(U 'great, thanks')${NL}$A" --turns
check "every turn is written, uncorrected ones too" 2 "### TURN" "USER: add the export button" "USER: great, thanks"
[[ "$out" == *"TOOLS: Bash npm run lint; Skill release-notes"* ]] && { pass=$((pass+1)); echo "ok   tool calls listed in order"; } || { fail=$((fail+1)); echo "FAIL tool calls listed in order"; }
[[ "$out" == *"CLAUDE: Done, the tests pass."* ]] && { pass=$((pass+1)); echo "ok   claude's last words kept"; } || { fail=$((fail+1)); echo "FAIL claude's last words kept"; }
[[ "$out" != *"sidechain-only"* ]] && { pass=$((pass+1)); echo "ok   subagent calls left out"; } || { fail=$((fail+1)); echo "FAIL subagent calls left out"; }

run plain "$(U 'add the export button')${NL}$DONE${NL}$(U 'great, thanks')"
check "without --turns an uncorrected turn is not written" 0

python3 -I "$dir/corrections.py" --root "$tmp/root" --out "$tmp/out.md" --turns --skill x >/dev/null 2>&1
[[ $? -ne 0 ]] && { pass=$((pass+1)); echo "ok   --turns with --skill is refused"; } || { fail=$((fail+1)); echo "FAIL --turns with --skill is refused"; }

# --chunk-lines: chunk files for the miners, cut only where the session changes
shopt -s nullglob
rm -rf "$tmp/root"; mkdir -p "$tmp/root/-proj"
for s in aaaa1111 bbbb2222 cccc3333; do printf '%s\n%s\n%s\n%s\n' "$(U "first in $s")" "$DONE" "$(U "second in $s")" "$DONE" > "$tmp/root/-proj/$s.jsonl"; done
rm -f "$tmp"/out.*.md
python3 -I "$dir/corrections.py" --root "$tmp/root" --out "$tmp/out.md" --turns --chunk-lines 6 >/dev/null
chunks=("$tmp"/out.*.md)
(( ${#chunks[@]} == 3 )) && { pass=$((pass+1)); echo "ok   one chunk per session once a chunk reaches the limit"; } || { fail=$((fail+1)); echo "FAIL chunk count ${#chunks[@]}, want 3"; }
[[ "$(cat ${chunks[@]+"${chunks[@]}"} /dev/null)" == "$(cat "$tmp/out.md")" ]] && { pass=$((pass+1)); echo "ok   chunks add up to the whole file"; } || { fail=$((fail+1)); echo "FAIL chunks add up to the whole file"; }
cut=0; for c in ${chunks[@]+"${chunks[@]}"}; do [[ "$(grep -o 's=[a-z0-9]*' "$c" | sort -u | wc -l | tr -d ' ')" == 1 ]] || cut=1; done
(( cut == 0 )) && { pass=$((pass+1)); echo "ok   no session is cut across two chunks"; } || { fail=$((fail+1)); echo "FAIL a session spans two chunks"; }

rm -f "$tmp"/out.*.md
python3 -I "$dir/corrections.py" --root "$tmp/root" --out "$tmp/out.md" --turns --chunk-lines 1000 >/dev/null
chunks=("$tmp"/out.*.md)
(( ${#chunks[@]} == 1 )) && { pass=$((pass+1)); echo "ok   a file under the limit is one chunk"; } || { fail=$((fail+1)); echo "FAIL small file gave ${#chunks[@]} chunks"; }

rm -f "$tmp"/out.*.md
python3 -I "$dir/corrections.py" --root "$tmp/root" --out "$tmp/out.md" --turns >/dev/null
compgen -G "$tmp/out.*.md" >/dev/null && { fail=$((fail+1)); echo "FAIL chunk files written without --chunk-lines"; } || { pass=$((pass+1)); echo "ok   no chunk files without --chunk-lines"; }

python3 -I "$dir/corrections.py" --root "$tmp/root" --out "$tmp/out.md" --chunk-lines 0 >/dev/null 2>&1
[[ $? -ne 0 ]] && { pass=$((pass+1)); echo "ok   --chunk-lines below 1 is refused"; } || { fail=$((fail+1)); echo "FAIL --chunk-lines 0 is refused"; }

echo "$pass passed, $fail failed"; (( fail == 0 ))
