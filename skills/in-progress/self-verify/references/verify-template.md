---
name: verify
description: >
  Verify the current change by driving the real app. Use before commit and before a PR. Prints
  one result line per feature: VERIFIED, NOT VERIFIED or BLOCKED.
---

# Verify

## Launch

Use the project's run skill `<run skill name>`. Do not copy its launch command here.
Wait until `<ready URL or log line>` appears. Time out after `<seconds>` seconds. A timeout is BLOCKED.
Record the PID or container name the launch created, for Cleanup.

## Doctor

Check each prerequisite before any test runs. Command: `<doctor command>`.
A missing prerequisite is BLOCKED. Print its name and the fix.

## Select

Map the diff to features. Read `references/features/README.md`. Take each changed path, find
the feature file whose **Code** line matches it, and run that file's **Tests** and **Check**.
Command: `<diff-to-features command>`.
A docs-only or test-only diff skips this run.

## Drive

For each selected feature, run its check. Run this block under bash: `PIPESTATUS` is a bash array
(zsh names it `pipestatus`).

```
set -o pipefail
<check command for feature> 2>&1 | tee <log dir>/<feature>.log
status=${PIPESTATUS[0]}
echo "exit=$status"
```

Read the exit code. Zero tests run in the log is NOT VERIFIED.

## Evidence

Save the report to `<report dir>/<feature>/`. Include the screenshot or trace.
Print the path. The reviewer re-runs the command shown on the result line.

## Cleanup

Stop only what this run started. Stop it by the PID or container name recorded at Launch. Never
stop by process name. Command: `<cleanup command>`. Run cleanup even when a check failed.
Keep the evidence.

## Full suite

Where and when the full suite runs: `<the project's answer from setup: where and when the full suite runs>`.
Use the same exit-code rule as Drive.

## Result line format

Print one line per feature, in this form:

```
<feature>: VERIFIED | NOT VERIFIED | BLOCKED  cmd: <re-run command>  evidence: <path>
```

Print the overall result last. Overall is VERIFIED only when every selected feature is VERIFIED.
