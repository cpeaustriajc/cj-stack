# work-pane

> Archived: not maintained.

A mod (a plugin that adds hooks to Claude Code) that shows test runs in a pane. It reads the progress of a test run from the log file the run writes.

## Why

A long test run in the background gives no sign of progress. work-pane shows each run with a progress bar and the pass and fail counts.

## Install

It is not installable from the marketplace. No plugin in `.claude-plugin/marketplace.json` lists it, so no cj-stack plugin ships it.

## Example

1. Claude runs `pnpm test 2>&1 | tee /tmp/e2e.log`.
2. The mod adds a row and opens the Tests pane.
3. You see a bar, a count such as `12/146`, and `pass 11 fail 1`.

The log must print lines like `[12/146] ✔ Suite test (19s) pass 11 fail 1`. The script `demo/fake-suite.sh` prints such lines.

## What it does

| Event | Decision |
|---|---|
| A Bash command pipes to `tee` on its first line | Add a row, keep the last 10, and open the pane. |
| One second passes | Read the last 40 log lines of each running row and update the counts. |
| The count reaches the total | Mark the row finished: `✓`, or `✗` if any test failed. |
| A foreground run ends | Read the log once and mark the row finished. |
| You run `/tests` | Open the pane. It lists the newest three rows, or "No test runs yet". |

## Settings

No settings. If you loaded a local copy, run `claude plugin disable work-pane` to turn it off.

## Limits

- It finds a run only by `| tee <file>` or `| tee -a <file>` on the first line of the command.
- If the log cannot be read, the row stays "running" with no counts.

## More

- [hooks/register.tsx](hooks/register.tsx): the hook source.
- [hooks/tests.test.ts](hooks/tests.test.ts): the tests.
