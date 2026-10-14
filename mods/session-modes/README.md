# session-modes

A mod (a plugin that adds hooks to Claude Code) that adds the `/mode` command. A mode sets a working rule for the whole session, and the mod blocks any tool call that breaks the rule.

## Why

An instruction in a prompt can fade in a long session. With `/mode audit`, Claude cannot edit a file, even if you forget to repeat the rule. With `/mode no-pr`, Claude cannot open a pull request.

Each mode also adds one sentence to the system prompt (the instructions Claude reads each turn). Claude knows the rule before the hook has to block anything.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install session-modes@cj-stack
```

To see that it is on, run `claude plugin list` and look for `session-modes`. The mod is optional: `cj-stack` does not install it.

## Example

1. You type `/mode audit`. The mod answers "Mode audit on."
2. Claude tries to edit `src/app.ts`. The mod blocks the call.
3. Claude reads the reason: "audit mode is on: report the change instead of making it; /mode off to leave."
4. Claude lists the change in its reply. You type `/mode off` to leave.

## What it does

| Mode | Allows | Blocks |
|---|---|---|
| `audit` | Reading, `git status`, `git log`, redirects to `/dev/null` | `Edit`, `Write`, `NotebookEdit`, `git commit`, `git push`, `gh pr create`, `gh pr merge`, a Bash redirect to a file |
| `no-pr` | Edits, commits, `git push` | `gh pr create`, an MCP tool named `create_pull_request` |
| `chat` | Edits, commits | `gh pr create`, `git push`, an MCP tool named `create_pull_request` |
| `product` | Edits to `.md` and `.markdown` files, `git commit` | Edits to any other file, `git push`, `gh pr create`, `create_pull_request`; tracker writes until a planning skill loads |

In `product` mode, a tracker write is an MCP tool with a write word in its name, such as `save_issue` or `createJiraIssue`. It is also `gh issue create`, a `gh api` call with `-X POST`, or `acli jira workitem create`. The mod holds these until you load the `vision`, `shape` or `tickets` skill. The `cj-stack:` prefix is also accepted. Other prefixes do not count.

Other commands:

- `/mode` alone shows "Current mode: off. Modes: audit, no-pr, chat, product, off."
- `/mode off` removes the mode and shows "Mode off."
- An unknown name shows `Unknown mode "<name>"` and changes nothing.
- A name in capital letters or with spaces around it still works.
- Typing `/mode ` lists the five names in the prompt suggestions.

While a mode is on, a band above the prompt shows it in the terminal and in the desktop app. The band has the mode name in bold and in the mode's colour, the rule in one line and a "Turn off" button. For `audit` it reads "Audit Read and report only. Edits, commits, pushes and PRs are blocked." The "Turn off" button does what `/mode off` does. In a band narrower than 60 columns, the band shows the first sentence only. The band hides while a survey is on screen and when no mode is set.

When the mode changes, also by "Turn off", the mod adds a hidden note to your next message that says the current mode, for example "Session mode: off. Audit mode has ended; its rules no longer apply". The mod also puts the mode in the system prompt each turn, but the desktop app does not pass that text to the model. A subagent started while a mode is on gets the rule at the top of its task, and its tool calls are blocked like the main thread's. Workflow agents do not get the note, because their prompt cannot be changed.

### Modes the model sets

The mod adds a tool, `agent_mode`, that Claude can call to set a mode for itself (scope `self`) or for its subagents (scope `subagents`), including subagents that are already running. Example: with your mode off, Claude sets `audit` for subagents and starts three Explore subagents. Each one gets the Audit rule at the top of its task, and any `Edit` it makes is denied. The main thread can still edit.

A call is denied when any rule that applies to the caller denies it, so the stricter rule always wins. Claude cannot loosen your `/mode`: its `off` clears only the modes it set itself. A subagent can set modes for itself and for its own subagents in the same way. `/mode off` and the band's "Turn off" clear every mode Claude set. `/mode audit` does not.

The band shows the modes Claude set on a second row, for example "Set by Claude: Audit for itself and Chat for subagents". With your mode off, that row is all the band shows. `/mode` alone adds the same text to its report.

The mod writes `{ "v": 1, "mode": "audit" }` to `~/.claude/mod-state/<session id>.session-modes.json` for a custom status line to read. With no mode, `mode` is `null`. If `CLAUDE_CONFIG_DIR` is set, the file goes to `$CLAUDE_CONFIG_DIR/mod-state`. At session start, the mod deletes its state files older than seven days.

## Settings

No settings. To turn the mod off, run `claude plugin disable session-modes@cj-stack`.

## Limits

- `audit` does not block a Bash command that writes without a redirect, such as `sed -i`. It does not block MCP tools.
- `no-pr` and `chat` check only the pull request and push commands above. They do not block edits.
- `product` mode judges an MCP tool by its name only. A tracker tool with no write word in the name passes.
- A subagent that is already running gets no new task note when a mode above it changes. The new rule applies to its tool calls at once, and only the deny message tells it.
- After you load a planning skill, tracker writes stay open for the rest of the session.
- If the mod cannot find a home directory, it writes and prunes no state file. If a write fails, the hook throws "session-modes: could not publish state for the status line". If a prune fails, it throws "session-modes: could not prune old state files".

## More

- [hooks/modes.ts](hooks/modes.ts): the modes, the prompt text and the block rules.
- [hooks/register.tsx](hooks/register.tsx): the hook source, the band and the state file.
- [hooks/suggest.ts](hooks/suggest.ts): the prompt suggestions.
- [hooks/register.test.ts](hooks/register.test.ts) and [hooks/suggest.test.ts](hooks/suggest.test.ts): the tests.
- [.claude-plugin/plugin.json](.claude-plugin/plugin.json): the manifest.
