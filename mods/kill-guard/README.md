# kill-guard

A mod (a plugin that adds a hook to Claude Code) that denies a shell command which stops processes by name or by port. Claude then kills only a PID it can name.

## Why

Claude starts dev servers and test runners, and later stops them. A command such as `pkill -f "node \(vitest"` or `kill $(lsof -ti:3000)` stops every match on the machine. That includes the server of another checkout or another session.

kill-guard denies the command and tells Claude to kill a PID it saved, or a PID it checked.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install kill-guard@cj-stack
```

To see that it is on, run `claude plugin list` and look for `kill-guard`. The mod is optional: `cj-stack` does not install it.

## Example

1. Claude runs `pkill -f "wrangler dev" ; pkill -f workerd` to restart a server.
2. The hook finds `pkill` at the start of a command.
3. The hook denies the command. Claude reads: "kill-guard: a kill by name or port can stop another checkout's process."
4. Claude runs `lsof -a -p <pid> -d cwd`, sees that the PID belongs to this worktree, and runs `kill <pid>`.

## What it does

The hook checks every Bash command. It ignores text inside quotes and comments, so `echo "do not use pkill"` passes.

| Command | Decision |
|---|---|
| `pkill` or `killall` at the start of a command, or after `;`, `&&`, `\|`, `$(`, `sudo`, `xargs` | Deny. |
| `fuser -k` | Deny. |
| `kill` with an argument made by `lsof`, `pgrep`, `pidof`, `ps`, `ss`, `netstat` or `fuser`, such as `kill $(lsof -ti:3000)` | Deny. |
| `lsof`, `pgrep` or `ps` piped into `xargs kill` | Deny. |
| `kill 18427`, `kill $!`, `kill %1`, `kill $(cat app.pid)` | Pass. |
| `kill -0 <pid>`, `pgrep -fl vitest`, `grep pkill README.md` | Pass. |
| The hook fails on a command | Deny with "could not check". |

The deny text gives two ways out. Kill the PID you saved (`$!` or a pid file). Or check the PID's working directory with `lsof -a -p <pid> -d cwd` or `ps -o command= -p <pid>`, then kill it.

## Settings

No settings and no allow list.

To turn the mod off, run `claude plugin disable kill-guard@cj-stack`.

## Limits

- It checks only the Bash tool. Code that kills by name from a script file passes.
- It does not read the text of `bash -c "..."` or `eval`.
- A PID in a variable passes: `P=$(pgrep vite); kill $P`.
- It does not check that a named PID belongs to this worktree.
- If the hook fails, it denies. Retry, or kill a PID you saved.

## More

- [hooks/register.ts](hooks/register.ts): the hook source.
- [hooks/register.test.ts](hooks/register.test.ts): the tests.
- [marketplace.json](../../.claude-plugin/marketplace.json): the manifest, in this mod's entry.
