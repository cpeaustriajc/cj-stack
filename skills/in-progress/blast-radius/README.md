# blast-radius

A typed `/blast-radius` command that finds what a change can break outside its diff. It proves the one fact the change is safe because of, or says that fact is unproven.

> In progress: not shipped in any plugin.

## When to use it

Use it before you merge a change that you do not trust yet, even a small one. A list of callers is not enough: it looks for the breakage that a search does not show.

- For how the code works today, use `how`.
- For why code has its shape, use `why`.
- For a full review of a risky diff, use `interrogate`.

## Example

You type: `/blast-radius the cache expiry change on this branch`

1. Claude reads the diff, its commits and its pull request.
2. Claude names the one fact that makes the change safe.
3. Claude reads past the diff: library source, data formats, flags and callers three steps away.
4. Claude writes a small script that runs the real code, runs it, and pastes the result.
5. You get the writeup and a risk map, with the change in the middle.

The writeup has five parts: What it does, the one fact it's safe because of, Risks, Cleared, and Before you merge. Each risk has a file and line, and a proof level from 1 (Claude said so) to 5 (reproduced in the running app).

## Install

The opt-in `cj-lab` plugin ships it:

```
/plugin install cj-lab@cj-stack
```

It starts only when you type `/blast-radius`. Claude does not pick it on its own.

## What it does

- Reads the change: a pull request, a branch, a commit or a diff. With no argument, it reads the current branch and your uncommitted edits.
- Writes proof scripts in `.claude/work/blast-radius/` and runs them. It does not edit the change's own files.
- Marks the safety fact unproven when no proof holds.
- Shows the risk map in the desktop app. A click on a risk asks how to check it. In a terminal, it prints the map as a mermaid flowchart.

## Limits

- It does not fix the risks it finds.
- It proves only the one or two facts that the change depends on, not every risk.
- A wide change goes to `interrogate` for more reviewers.

## More

- [SKILL.md](SKILL.md): the method and the five parts of the writeup.
- [references/claude-code.md](references/claude-code.md): proof scripts and the risk map.
- [LICENSE](LICENSE): adapted from pstack by Lauren Tan, under the MIT licence.
