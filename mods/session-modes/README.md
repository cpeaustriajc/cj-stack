# session-modes

A mod (a plugin that adds hooks to Claude Code) that adds the `/mode` command. A mode sets a working rule for the whole session, and the mod blocks any tool call that breaks the rule.

## Why

An instruction in a prompt can fade in a long session. With `/mode readonly`, Claude cannot edit a file, even if you forget to repeat the rule. With `/mode edit`, Claude cannot push or open a pull request.

Each mode also adds one sentence to the system prompt (the instructions Claude reads each turn). Claude knows the rule before the hook has to block anything.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install session-modes@cj-stack
```

To see that it is on, run `claude plugin list` and look for `session-modes`. The mod is optional: `cj-stack` does not install it.

## Example

1. You type `/mode readonly`. The mod answers "Mode readonly on."
2. Claude tries to edit `src/app.ts`. The mod blocks the call.
3. Claude reads the reason: "readonly mode is on: report the change instead of making it; /mode off to leave."
4. Claude lists the change in its reply. You type `/mode off` to leave.

## What it does

The modes form a ladder, from the strictest to the loosest: `readonly`, `research`, `edit`, `off`. Each tool call needs one level. A mode blocks a call that needs a higher level than the mode.

| Mode | Allows | Blocks |
|---|---|---|
| `readonly` | Reading, `git status`, `git log`, redirects to `/dev/null` | Everything in the rows below |
| `research` | Edits to `.md` and `.markdown` files, a redirect to such a file, `git commit`, tracker writes | Edits to any other file, a redirect to any other file, `git push`, pull requests |
| `edit` | Edits to any file, redirects to any file | `git push`, `gh pr create`, `gh pr merge`, pull request writes through `gh api` or an MCP tool |

A tracker write is an MCP tool with a write word in its name, such as `save_issue` or `createJiraIssue`. It is also `gh issue create`, a `gh api` call with `-X POST`, or `acli jira workitem create`. A pull request write is an MCP tool such as `create_pull_request`, or a `gh api` call on a `/pulls` path with `-X POST` or a field flag. An MCP tool with `push` in its name needs `/mode off`.

A Bash command with several parts, such as `git commit -m x && git push`, needs the highest level of its parts.

Other commands:

- `/mode` alone shows "Current mode: off. Modes: readonly, research, edit, off. Also: clear, agents on, agents off."
- `/mode off` removes the mode and shows "Mode off."
- `/mode clear` clears the modes Claude set.
- `/mode agents off` and `/mode agents on` block and allow the `agent_mode` tool. See "Your overrides".
- An unknown name shows `Unknown mode "<name>"` and changes nothing.
- A name in capital letters or with spaces around it still works.
- Typing `/mode ` lists the four names, `clear` and `agents` in the prompt suggestions. Typing `/mode agents ` lists `on` and `off`.

While a mode is on, a band above the prompt shows it in the terminal and in the desktop app. The band has the mode name in bold and in the mode's colour, the rule in one line and a "Turn off" button. For `readonly` it reads "Read only Read and report only. Edits, commits, pushes, PRs and tracker writes are blocked." The "Turn off" button does what `/mode off` does. In a band narrower than 60 columns, the band shows the first sentence only. The band hides while a survey is on screen and when no mode is set.

When the mode changes, also by "Turn off", the mod adds a hidden note to your next message. The note says the current mode, for example "Session mode: off. Read only mode has ended; its rules no longer apply". The mod also puts the mode in the system prompt each turn, but the desktop app does not pass that text to the model. A subagent started while a mode is on gets the rule at the top of its task. The mod blocks its tool calls like the main thread's. Workflow agents do not get the note, because their prompt cannot be changed.

### Modes the model sets

The mod adds a tool, `agent_mode`. Claude can call it to set a mode for itself (scope `self`) or for its subagents (scope `subagents`). The mode also reaches subagents that are already running. Example: with your mode off, Claude sets `readonly` for subagents and starts three Explore subagents. Each one gets the Read only rule at the top of its task, and any `Edit` it makes is denied. The main thread can still edit.

A call is denied when any rule that applies to the caller denies it, so the stricter rule always wins. Claude cannot loosen your `/mode`: its `off` clears only the modes it set itself. A subagent can set modes for itself and for its own subagents in the same way. `/mode off` and the band's "Turn off" clear every mode Claude set. `/mode readonly` does not.

Claude also picks its own mode for each message you send. The mod adds a hidden note that asks for the pick and names Claude's current mode. Claude calls `agent_mode` with scope `self` when the pick differs. The note goes on messages you type in the terminal, in the desktop app or through Remote Control. It does not go on task notifications, scheduled prompts or messages from other sessions. The mod skips the note while your own mode is `readonly`.

Example: you type "why does the band hide at 50 columns? do not change anything". Claude sets `readonly` for itself, and a later `Edit` is denied. You type "ok, fix it". Claude sets `edit`. You type "fix it and open a PR". Claude sets `off`.

The band shows the modes Claude set on a second row, for example "Set by Claude: Read only for itself and Edit for subagents". With your mode off, that row is all the band shows. `/mode` alone adds the same text to its report.

### Your overrides

You can always take control back from a mode Claude set.

- The "Clear" button on the "Set by Claude" row clears every mode Claude set. Your own mode stays.
- `/mode clear` does the same. It shows "Cleared Claude's modes." or, with nothing set, "Claude has no modes set."
- `/mode agents off` clears the modes Claude set and blocks the `agent_mode` tool. It also stops the hidden note that asks for Claude's pick. While it is off, the mod denies a call with any mode except `off`. The reason is "The user turned off agent modes with /mode agents off." `/mode` alone then ends with "Agent modes: off."
- `/mode agents on` turns the tool back on.
- Any other value after `agents` shows "Use /mode agents off or /mode agents on." and changes nothing.

Claude is told on your next message. For example, after "Clear" it reads "Session mode: the user cleared the modes you set (Read only for itself). They no longer apply." `/mode off` and the band's "Turn off" send the same note when Claude had set a mode. Each note is sent once.

The mod writes `{ "v": 1, "mode": "readonly" }` to `~/.claude/mod-state/<session id>.session-modes.json` for a custom status line to read. With no mode, `mode` is `null`. If `CLAUDE_CONFIG_DIR` is set, the file goes to `$CLAUDE_CONFIG_DIR/mod-state`. At session start, the mod deletes its state files older than seven days.

## Settings

No settings. To turn the mod off, run `claude plugin disable session-modes@cj-stack`.

## Limits

- Claude picks the mode, and the mod does not check the pick. The "Set by Claude" row in the band shows it.
- `readonly` does not block a Bash command that writes without a redirect, such as `sed -i`.
- The mod judges an MCP tool by its name only. A tool with no write word in the name passes in every mode.
- The mod finds a Bash redirect and the commands above by their text. A command inside a script or an alias passes.
- A subagent that is already running gets no new task note when a mode above it changes. The new rule applies to its tool calls at once, and only the deny message tells it.
- If the mod cannot find a home directory, it writes and prunes no state file. If a write fails, the hook throws "session-modes: could not publish state for the status line". If a prune fails, it throws "session-modes: could not prune old state files".

## More

- [hooks/modes.ts](hooks/modes.ts): the modes, the prompt text and the block rules.
- [hooks/register.tsx](hooks/register.tsx): the hook source, the band and the state file.
- [hooks/suggest.ts](hooks/suggest.ts): the prompt suggestions.
- [hooks/register.test.ts](hooks/register.test.ts) and [hooks/suggest.test.ts](hooks/suggest.test.ts): the tests.
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json): the manifest.
