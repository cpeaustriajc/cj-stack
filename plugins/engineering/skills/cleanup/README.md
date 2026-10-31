# cleanup

A skill that removes what a Claude session left behind, keeps anything that still holds work, and then archives the session.

## When to use it

Use it at the end of a session, after its pull request merges. Archiving a session removes only its worktree. Dev servers, Docker containers, branches, stashes and evidence files stay behind.

- Use `/cleanup repo` for stale branches and worktrees from many sessions.
- For code that needs a tidy-up, use `simplify` instead.

## Example

You say: "Merged, clean up after yourself and archive this session."

1. Claude lists the servers, containers, branches, stashes and evidence that this session made.
2. Claude checks each item, such as the pull request state for a branch.
3. Claude removes the safe items without a question.
4. Claude reports what it removed and kept, then archives the session.

You get three lists in the chat: Removed, Kept with a reason, and commands to run yourself.

## Install

The `engineering` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install engineering@dotfiles
```

The skill then loads as `/engineering:cleanup`.

## What it does

- Stops a process by its PID, never by name or port.
- Deletes a branch only when its pull request is merged or closed and the tip matches.
- Deletes a remote branch only when you opened its pull request.
- Keeps unpushed commits, uncommitted edits and things another session made, and says why.
- Archives the session only when you say "archive" or "close".
- In `/cleanup repo`, saves every branch to a bundle in `.claude/work/cleanup/` and asks once.

## Limits

- It never force-deletes a branch. If git refuses, it gives you the command.
- After a context summary, it can miss items that it no longer remembers.
- In the terminal there is no archive. You get the command to remove the worktree.

## More

- [SKILL.md](SKILL.md): the method.
- [references/claude-desktop.md](references/claude-desktop.md): archive and worktree tools in the desktop app.
- [references/claude-code.md](references/claude-code.md): the terminal.
- [evals/triggers.json](evals/triggers.json): the trigger cases.
