# denial-explainer

> Archived: not maintained.

The newer Claude Code interface shows auto-mode denials well enough on its own, so the toast added little.

A mod (a plugin that adds a hook to Claude Code) that explains an auto-mode denial. It names the rule that blocked the action and shows the allow rule that would cover it.

## Why

In auto mode, a classifier (a model that judges each tool call) can deny an action. The denial tells you little. You must guess which rule fired and what to allow.

denial-explainer shows a toast (a short message in the interface) after each classifier denial. The toast names the rule and the narrowest `/permissions add` command for the call.

## Install

It is not installable from the marketplace. No plugin in `.claude-plugin/marketplace.json` lists it, so no cj-stack plugin ships it.

## Example

1. Claude runs `gh issue comment 12 --body hi` in auto mode.
2. The classifier denies it with the rule "Unreviewed External Writes".
3. The mod shows a toast and leaves the denial as it is.

You see this toast:

```
Blocked by Unreviewed External Writes: Bash gh issue comment 12 --body hi
Allow it: /permissions add "Bash(gh issue:*)"
```

To allow the call, run the command from the second line. The mod never adds a rule itself.

## What it does

| Event | Decision |
|---|---|
| The classifier denies a call | Show the toast. |
| A hook or you deny a call | Show nothing. |
| The denial is the second or later one | Add the count, for example "(2nd this session)". |

The toast shows the tool and its main argument. The argument is a Bash command, a WebFetch URL or a file path, cut to 60 characters.

The allow rule depends on the tool:

| Tool | Suggested rule |
|---|---|
| Bash | The first two words, for example `Bash(gh issue:*)`. |
| MCP tool | The tool name. |
| WebFetch | `WebFetch(domain:<host>)`. |
| Edit or Write | The exact file path. |
| Any other tool | None. The toast says "no allow rule suggested". |

## Settings

No settings.

## Limits

- Bash commands with `rm`, `sudo`, a force push or a pipe into a shell never get a rule.
- A Bash command whose first two words hold quotes or `$(` gets no rule.
- Any denial reason with text in square brackets counts as a classifier denial.
- The hook has no error handling of its own.

## More

- [hooks/register.ts](hooks/register.ts): the hook source.
- [hooks/explain.ts](hooks/explain.ts): the toast text and the allow rules.
- [hooks/register.test.ts](hooks/register.test.ts): the tests.
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json): the manifest.
