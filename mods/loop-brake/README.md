# loop-brake

A mod (a plugin that adds a hook to Claude Code) that ends a turn after a set number of forced continuations. A looping goal hook then cannot burn your usage.

## Why

A Stop hook runs when Claude ends its turn. The hook can block the stop and force Claude to continue. A goal hook that never gets satisfied blocks every time, and Claude keeps working.

loop-brake counts these forced continuations. At the cap, it lets the stop through and shows a toast (a short message in the interface).

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install loop-brake@cj-stack
```

To see that it is on, run `claude plugin list` and look for `loop-brake`. The mod is optional: `cj-stack` does not install it.

## Example

1. A Stop hook blocks the stop with "Not satisfied: keep going". Claude continues.
2. The hook blocks twice more. That is three forced continuations, the default cap.
3. The hook blocks a fourth time. The mod lets this stop through, and Claude stops.

You see this toast: "loop-brake: stopped after 3 forced continuations — reply to keep going". Send a message to start a new turn.

## What it does

| Event | Decision |
|---|---|
| A Stop hook blocks the stop | Count it and show the count. |
| The count is at the cap and the hook blocks again | Remove the block, show the toast, reset the count. |
| A Stop hook does not block | Reset the count. |
| A Stop hook ends the session outright | Reset the count and leave the result as it is. |
| You send a prompt from the composer or from your phone | Reset the count. |
| A machine-injected prompt arrives | Keep the count. |
| A session starts | Delete this mod's state files older than seven days. |

When a desktop or phone surface is attached, the status row shows "1 of 3 forced continuations". A terminal-only session shows no status row.

The mod also writes `{ "v": 1, "streak": 1, "cap": 3 }` to `~/.claude/mod-state/<session id>.loop-brake.json` for a custom status line to read. If `CLAUDE_CONFIG_DIR` is set, the file goes to `$CLAUDE_CONFIG_DIR/mod-state`.

## Settings

| Option | Default | Meaning |
|---|---|---|
| `maxContinuations` | 3 | Forced continuations allowed per turn, 1 to 20. |

A value that is not a whole number from 1 to 20 falls back to 3. Run `claude plugin configure loop-brake@cj-stack` to show the options and which are unset.

To turn the mod off, run `claude plugin disable loop-brake@cj-stack`.

## Limits

- It counts only blocks from Stop hooks. It does not limit tool calls or token use.
- A reset writes a zero count to the state file. It does not delete the file.
- If the mod cannot find a home directory, it writes and prunes no state file. The brake still counts.
- If the prune fails, the brake still counts. If the state file write fails, the hook throws "loop-brake: could not publish state for the status line".

## More

- [hooks/register.ts](hooks/register.ts): the hook source.
- [hooks/register.test.ts](hooks/register.test.ts): the tests.
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json): the manifest and the option default.
