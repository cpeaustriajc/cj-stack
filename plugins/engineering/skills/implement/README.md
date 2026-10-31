# implement

A typed skill that builds a ready ticket without supervision. It ends with a pull request that closes the ticket and shows the proof for each check.

## When to use it

Use it when a ticket is planned and an agent can prove it done. It stops an agent from redesigning settled work, and from a "done" claim with no proof.

- You type `/implement owner/repo#42` for one `ready-for-agent` ticket.
- You type `/implement <spec link> orchestrate` to build all ready tickets of a spec.

Do not use it for an idea with open questions: use `grill`. Do not use it for an unchecked ticket: use `triage` first. For a change with no tickets that splits into independent parts, such as a migration across the codebase, run the built-in `/batch` command.

## Example

You type: `/implement acme/shop#42`.

1. Claude gets the ticket from GitHub and says its title.
2. Claude checks that the ticket is `ready-for-agent` and that its blockers are closed.
3. Claude builds it in slices and commits each slice with its check.
4. Fresh reviewers check the commits, and Claude fixes what they find.
5. Claude opens a pull request with `Closes #42`.

You get the pull request, with a verdict and evidence for each Done When line.

## Install

The `engineering` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install engineering@cj-stack
```

The skill then loads as `/engineering:implement`.

## What it does

- It reads the ticket from the tracker, never from a list in the conversation.
- It does not ask you design questions. An easy choice follows the closest pattern in the code and goes in the pull request.
- A costly question stops the run. The ticket moves to `needs-info` with a note.
- It reviews after the commit, with reviewers that did not write the code.
- In orchestrate mode, one session builds each ready ticket in its own worktree.
- In orchestrate mode, this session merges each verified branch into one integration branch, then opens one pull request.

## Limits

- It runs only when you type it. Claude does not start it alone.
- It does not merge to the main branch. You merge the pull request.
- It does not close a ticket by hand. The merge closes it.
- Orchestrate mode caps the sessions that run at one time. The cap is in `references/claude-code.md`.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [references/orchestrate.md](references/orchestrate.md): the coordinator steps for a spec or several tickets.
- [references/claude-code.md](references/claude-code.md): sessions, worktrees and the traps.
