#!/usr/bin/env bash
total=${1:-12}
pass=0; fail=0
for i in $(seq 1 "$total"); do
  sleep 2
  if (( i % 5 == 0 )); then fail=$((fail+1)); mark="✘"; else pass=$((pass+1)); mark="✔"; fi
  echo "[$i/$total] $mark Suite $i (2s) pass $pass fail $fail"
done
