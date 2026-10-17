# bash-trim

A mod (a plugin that adds a hook to Claude Code) that cuts a long successful Bash output to its start and its end. Long sessions then carry less dead context.

## Why

Claude Code keeps a successful Bash output in context whole, up to about 30,000 characters. Each later call sends that output again. A test run, a build log or a long `grep` usually matters only at its start and its end.

bash-trim keeps the first 2,000 and the last 3,000 characters of such an output, and says how much it cut.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install bash-trim@cj-stack
```

To see that it is on, run `claude plugin list` and look for `bash-trim`. The mod is optional: `cj-stack` does not install it.

## Example

1. Claude runs `npm test`. The command passes and prints 18,000 characters.
2. The hook keeps the first 2,000 characters and the last 3,000 characters.
3. Claude reads the start, the line `[… 217 lines, 13,000 characters cut …]`, and the end with "26 passed, 0 failed".

## What it does

| Bash result | Decision |
|---|---|
| Successful, over 10,000 characters | Keep the first 2,000 and last 3,000 characters, with a line that counts the cut lines and characters. |
| 10,000 characters or less | Pass whole. |
| Failed or interrupted | Pass whole. Claude Code already shows a part of a failed output. |
| Saved to a file by Claude Code, an image, or a background task | Pass whole. |
| A read-like command: `cat`, `sed -n`, `head`, `tail`, `jq`, `git diff`, `git show`, `git log -p`, `gh pr`, `gh api`, `gh issue` | Pass whole, also after a leading `cd … &&`. |

The mod cuts only the standard output. The error output passes whole.

## Settings

No settings. The limits are constants in [hooks/register.ts](hooks/register.ts).

To turn the mod off, run `claude plugin disable bash-trim@cj-stack`.

## Limits

- The mod keeps no copy of the cut text. To see the middle, run a narrower command, such as `sed -n` or `grep`.
- It checks only the first command of a line. `npm test && cat log` is trimmed.
- It reads only the Bash tool. Read, Grep and MCP outputs pass whole.
- If the hook fails, the output passes whole and a toast names the error.

## More

- [hooks/register.ts](hooks/register.ts): the hook source.
- [hooks/register.test.ts](hooks/register.test.ts): the tests.
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json): the manifest.
