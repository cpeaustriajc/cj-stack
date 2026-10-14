# secret-guard

> Archived: not maintained.

Its pattern-based deny rules blocked normal work, such as edits under `.claude/` and reads of `settings.json`. Auto mode's built-in credential rules cover the same risks by intent.

A mod (a plugin that adds hooks to Claude Code) that keeps secret values out of Claude's context. It hides values in tool output and denies commands that would encode, test or send a secret.

## Why

Claude reads files and runs commands. A `.env` file, a `docker inspect` dump or an error message can hold a password or a token. Whatever Claude reads goes to the model.

secret-guard has two parts. A hook (a script that runs on a Claude Code event) checks each call before it runs. A second hook cleans each result before Claude sees it. Claude can still read the file and see its structure, but not the secret value.

## Install

It is not installable from the marketplace. No plugin in `.claude-plugin/marketplace.json` lists it, so no cj-stack plugin ships it.

## Example

Your project has a `.env` file with a secret in `API_KEY`.

1. You ask Claude to print the value of `API_KEY` in `.env`.
2. Claude reads the file. The result hook replaces the value with `[REDACTED]`.
3. Claude sees the line with `[REDACTED]` in place of the value.

Claude then tries a workaround, such as piping `printenv API_KEY` into `base64`. The call hook denies it. The reason starts with "Blocked:" and ends with a "Safe alternative:" that Claude can use.

## What it does

| Event | Decision |
|---|---|
| PreToolUse, a Bash call | Filter. Wrap the command so stdout and stderr pass through the redactor. |
| PreToolUse, a call that joins a secret source with an encoder, slicer or test | Deny, with a reason and a safe alternative. |
| PreToolUse, a write or message that holds a secret value | Deny. |
| PreToolUse, a change to the hooks, to settings, or to the mod itself | Deny. |
| PreToolUse, any other call | Allow. The mod gives no verdict, so Claude Code's own permission rules apply. |
| PostToolUse, any tool | Redact. Replace each secret value in the output with `[REDACTED]`. |
| PostToolUse, redaction fails or runs too long | Withhold the whole output and show `[REDACTED: output withheld (<reason>)]`. |

PreToolUse runs before a tool call. PostToolUse runs after it. Both hooks match every tool, as `hooks/hooks.json` shows.

## Settings

The mod has no `userConfig` option. To turn it off, run `claude plugin disable secret-guard@cj-stack` in your own terminal.

If Claude runs that command, the mod denies it.

## Limits

- Redaction has false positives. In use it replaced harmless lines, such as a code fence, `esac` and some file names, with `[REDACTED]`. The line is not missing from your file.
- If a line shows `[REDACTED]` and you need it, read the file yourself.
- Detection works on patterns. A secret in a form the patterns do not know can reach Claude.
- The hook fails closed. On an error, a timeout or output over its size limit, Claude gets the withheld notice, not the raw output.
- If the call hook cannot analyse a call, it denies the call: "Blocked: the secret guard could not analyse this call".
- The Bash filter needs `mkfifo`. Without it, the output is withheld: "filter unavailable".
- Some tests need macOS `sandbox-exec`. Without it, the runner reports those cases as failed-unsafe.

## More

- [hooks/hooks.json](hooks/hooks.json): the events and timeouts.
- [hooks/secret_guard.py](hooks/secret_guard.py): the call hook, with the deny rules.
- [hooks/secret_redact.py](hooks/secret_redact.py): the result hook.
- [hooks/secret_filter.py](hooks/secret_filter.py): the Bash stream filter.
- [hooks/secret_engine.py](hooks/secret_engine.py): the shared detection and redaction code.
- [tests/README.md](tests/README.md): how to run and read the tests.
- [redteam/README.md](redteam/README.md): attack runs against real Claude sessions.
- [docs/](docs/): design specs and handoff notes.
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json): the manifest.

To run the tests from the repo root, run `python3 mods/archived/secret-guard/tests/secret_hooks_test.py --hooks-dir mods/archived/secret-guard/hooks`.
