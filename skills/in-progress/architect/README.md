# architect

A typed `/architect` command that sketches two whole designs for a task before any code exists. You see both side by side and pick one.

> In progress: not shipped in any plugin.

## When to use it

Use it before non-trivial work where the first shape that compiles can be the wrong one. You judge the shape while it is still cheap to change.

- For how the code works today, use `how`.
- For why code has its shape, use `why`.
- For a review of a finished diff, use `interrogate`.

## Example

You type: `/architect add a weekly digest email to the notes app`

1. Claude reads the parts of the code that the task touches, with the method of `how`.
2. A Sonnet subagent writes one candidate. Claude, on Opus, writes the other without reading the first.
3. Claude checks both against a list of design red flags.
4. You see the two candidates side by side and click Pick or Push back.
5. After Pick, Claude writes the picked sketch as stub files and opens a pull request. Its body
   names the shape you picked, its tradeoffs and the shape you did not pick.
6. After Push back with a reason, Claude reads the code again and shows two new candidates. It
   writes no file in between.

Each candidate shows the caller's usage first, then the public surface, the internals, the red flags and one "we accept X for Y" line. Claude writes no code until you pick.

## Install

The opt-in `cj-lab` plugin ships it:

```
/plugin install cj-lab@cj-stack
```

It starts only when you type `/architect`. Claude does not pick it on its own.

## What it does

- Grounds the task in the code with the read-only method of `how` before it sketches.
- Gets two candidates from two models, and neither model sees the other candidate.
- Changes no file before your pick. The Sonnet runner has only read tools.
- Shows the candidates in two columns in the desktop app. In a terminal, it prints them as text blocks, one after the other.
- When the task changes code that exists, shows today's code with its red flags above the candidates.
- When the task only moves files, such as `/architect make the routes thin`, shows today's file
  tree and the moves and "rule after" line of each candidate. After your pick, it makes one
  commit of moves only and checks it with `scripts/moves_only.py`. Typecheck and tests must give
  the same result as before. Then it adds a check for the rule in a second commit and stops.
- When a move needs a logic edit to compile, undoes the moves and shows new candidates.
- While it fills in the stubs, tells you when the same workaround keeps coming back, and offers a smaller re-sketch.

## Limits

- It does not merge the two candidates. You pick one or push back.
- It does not use models from other vendors.

## More

- [SKILL.md](SKILL.md): the method.
- [references/runner-prompt.md](references/runner-prompt.md): the brief each runner gets.
- [references/design-red-flags.md](references/design-red-flags.md): the red flags each candidate is checked against.
- [references/rationale-template.md](references/rationale-template.md): the rationale that ships with the picked sketch.
- [references/claude-code.md](references/claude-code.md): models, spawn calls and the side-by-side view.
- [scripts/moves_only.py](scripts/moves_only.py): the check that a commit holds moves only, with its tests.
- [../evals/architect-layout-moves](../evals/architect-layout-moves): the eval case for a layout task, from the sketches to the two commits.
- [LICENSE](LICENSE): adapted from pstack by Lauren Tan, under the MIT licence.
