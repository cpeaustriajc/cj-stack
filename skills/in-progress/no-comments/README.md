# no-comments

A typed `/no-comments` command that sweeps a folder of old code for comment slop. It deletes the comments, flags the code they excused, and proves that the tests did not change.

> In progress: only in the opt-in `cj-lab` plugin.

## When to use it

Use it on code written before current models: narrating comments, workaround notes and lint suppressions that new prompts copy. Current models rarely write these, so the value is in old folders, not in each diff.

- For how the code works, use `how`.
- For why code has its shape, use `why`.
- For a review of a finished diff, use `interrogate`.

## Example

You type: `/no-comments src/legacy`

1. Claude runs the typecheck, lint and tests, and saves the results.
2. A read-only Sonnet sweeper lists every comment in the folder that is not on its keep list.
3. Claude checks that list, then deletes the comments in one commit.
4. Claude makes the small fixes that the flags ask for in a second commit. It removes the suppressions in a third.
5. After each commit, the checks give the same result as before.
6. Claude checks each `do not remove` comment against the history or the code, and offers a type, test or lint.

You get the deletion count, one line for each `MUST KILL` flag, and the comments it kept and why. Each `MUST KILL` shows the deleted comment beside its code, with a button that sends it to `/architect`. Without an inline view, the same items print as text, with the `/architect` prompt to paste. An empty sweep says `0 deletions` and names the folder.

## Install

The opt-in `cj-lab` plugin ships it:

```
/plugin install cj-lab@cj-stack
```

It starts only when you type `/no-comments`. Claude does not pick it on its own.

## What it does

- Keeps license headers, `prettier-ignore`, public API doc comments, issue links, and notes about a vendor or protocol we cannot change.
- Marks code that a comment excused as `MUST KILL`, with the rename, extract or type that would make the comment unneeded.
- Writes only on a branch. It stops if you have uncommitted work outside the project's work folder.
- Undoes any change that alters a check result, and reports that change as open.

## Limits

- It encodes a constraint only after you say yes. A run with nobody to answer only makes the offer.
- A `MUST KILL` that needs a new design is reported, not built. `/architect` stops at two sketches.
- It does not change behaviour on purpose. A fix that changes a test result is undone.

## More

- [SKILL.md](SKILL.md): the method.
- [references/sweeper-prompt.md](references/sweeper-prompt.md): the brief the sweeper gets, with its keep list.
- [references/constraints.md](references/constraints.md): how a constraint comment is checked, encoded or deleted.
- [references/claude-code.md](references/claude-code.md): the spawn call and the commit rules.
- [../evals/no-comments-folder-sweep](../evals/no-comments-folder-sweep): the folder-sweep eval case.
- [LICENSE](LICENSE): adapted from pstack by Lauren Tan, under the MIT licence.
