---
name: verify
description: >
  This skill should be used before a commit or a push in cj-stack, and when the user says "verify
  this" or "prove it works". It maps the diff to features, runs each feature's checks with their
  real exit codes, saves the logs and prints one result line per feature: VERIFIED, NOT VERIFIED
  or BLOCKED.
---

# Verify

## Launch

cj-stack has no app to launch. The project's run skill is `run-cj-stack`; its driver
`.claude/skills/run-cj-stack/smoke.sh` is the only launch interface. Do not copy its steps here.

## Doctor

`command -v claude python3 bash git` must print four paths, and `python3 -c 'import yaml'` or
`command -v uv` must succeed. A missing one is BLOCKED: name it.

## Select

Map the diff to features with `.claude/skills/verify/select.sh [base]` (default base
`origin/main`). It prints `feature<TAB>command` lines from the **Code** lines in
`references/features/`. In this repo Markdown is the product, so a docs-only diff is not skipped.

## Drive

For each selected feature, run its command under bash and read the runner's own exit code:

```
set -o pipefail
mkdir -p .claude/work/verify/<short sha>
<command> 2>&1 | tee .claude/work/verify/<short sha>/<feature>.log
status=${PIPESTATUS[0]}
echo "exit=$status"
```

- A mod's log must show `N pass` with N > 0 and `0 fail`; zero tests is NOT VERIFIED.
- `routing` costs about $2; run it with `RUNS=1` unless a routing case changed. Over budget or
  unauthenticated is BLOCKED.
- Then do the feature file's **Check** line by hand and note it in the log.

## Evidence

Logs go to `.claude/work/verify/<short sha>/`, which git ignores. Print that path.

## Cleanup

`smoke.sh` removes its own throwaway config directory. This run starts nothing else.

## Full suite

`.claude/skills/run-cj-stack/smoke.sh all` (about 20 s) before every push to `main`; `routing`
only when the Routing feature is selected. Exit 2 is BLOCKED (the line says what is missing), not a pass.

## Result line format

```
<feature>: VERIFIED | NOT VERIFIED | BLOCKED  cmd: <re-run command>  evidence: <path>
```

Print the overall result last. Overall is VERIFIED only when every selected feature is VERIFIED.
