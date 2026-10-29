# test-guard

A mod (a plugin that adds a hook to Claude Code) that stops Claude from making a failing test pass by changing the test. Claude can add tests, but it cannot change or remove a line that a test file has at `HEAD`.

## Why

An agent with a red test sometimes changes the test instead of the code. It turns `toHaveBeenCalledTimes(1)` into `toHaveBeenCalled()`, and the test goes green while the bug stays.

test-guard denies that edit and tells Claude to add a test or to explain the change to you. Only you can let one test file change.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install test-guard@cj-stack
```

To see that it is on, run `claude plugin list` and look for `test-guard`. The mod is optional: `cj-stack` does not install it.

## Example

1. A test fails, and Claude edits `tests/notify.test.ts` to change `toHaveBeenCalledTimes(1)` to `toHaveBeenCalled()`.
2. The hook reads the file at `HEAD` with `git show` and finds that the old line is gone.
3. The hook denies the edit. Claude reads: "test-guard: this changes or removes a line that tests/notify.test.ts has at HEAD".
4. Claude fixes the code, or tells you which test is wrong and why.
5. If you agree, run `/test-guard allow tests/notify.test.ts`. Claude can then change that file for the rest of the session.

## What it does

The hook checks every Edit, MultiEdit and Write to a test file. A test file is a name like `*.test.*`, `*.spec.*`, `test_*.py`, `*_test.py` or `*_test.go`. A file in a `test`, `tests`, `__tests__`, `e2e` or `__snapshots__` folder inside the repository is also a test file. The hook asks git for the path from the repository root, so a project in `~/e2e/demo/` does not make every file a test file.

| Case | Decision |
|---|---|
| The file is not a test file | Pass. |
| The test file is new or not in `HEAD` | Pass. |
| The folder is not in a git repository, or the repository has no commit | Pass. |
| Every non-blank `HEAD` line stays, in the same order | Pass: only additions. |
| A `HEAD` line changes or goes away | Deny. The text names the first such line and `/test-guard allow`. |
| You ran `/test-guard allow <path>` for this file in this session | Pass. |
| `git show` fails for another reason, or the hook fails | Deny with "could not check". |

A line that Claude added in this session is not in `HEAD`, so Claude can change it.

`/test-guard allow <path>` allows one file until the session ends. `/test-guard` alone lists the allowed files. Claude has no tool to allow a file.

## Settings

No settings and no allow list file.

To turn the mod off, run `claude plugin disable test-guard@cj-stack`.

## Limits

- It checks only Edit, MultiEdit and Write. A Bash command such as `sed -i` or `jest -u` passes, because Claude Code decides Bash.
- A moved line or a changed indent counts as a change and gets a deny.
- It compares with `HEAD`, not with the base branch. A weaker test that is already committed passes; the self-verify PR verdict checks that.
- The mod is always on. It is not the "careful mode" that `SCOPE.md` rejects, which runs hooks only while a skill runs.
- If the hook fails, it denies. Retry, or allow the file.

## More

- [hooks/register.ts](hooks/register.ts): the hook source.
- [hooks/register.test.ts](hooks/register.test.ts): the tests.
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json): the manifest.
- [nizos/tdd-guard](https://github.com/nizos/tdd-guard): the prior art. It blocks code without a failing test and asks a model; test-guard protects old test lines with a fixed check.
