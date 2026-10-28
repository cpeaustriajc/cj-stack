# create-pr

A skill that commits your work, runs the fast checks, pushes, and opens a GitHub pull request that links the issue and the evidence. It is the terminal version of the desktop Create PR button.

## When to use it

Type `/create-pr`, or ask Claude to open a PR, when a branch is ready for review. Claude also loads it on a request such as "push it and open the PR".

Do not use it for commits alone: use `commit`. Do not use it to review the diff: use `interrogate`.

## Example

You type: `/create-pr draft develop`

1. Claude commits any loose changes and runs the checks that your `CLAUDE.md` names.
2. Claude pushes the branch.
3. Claude opens a draft PR against `develop`.

You get the PR URL on its own line, plus one line on anything skipped, such as "no issue found". The word `draft` makes a draft. Any other word is the base branch.

## Install

The `cj-stack` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-stack@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-stack@cj-stack`. This also turns off every other skill in `cj-stack`.

## What it does

- It needs `gh` signed in. If `gh auth status` fails, it stops.
- If there is no GitHub remote, it asks whether to link a matching repo, create a private repo, or create a public one.
- If you are on the default branch, it creates a `claude/<short-topic>` branch first, because a hook requires the prefix.
- It keeps your existing commits and never squashes them.
- It commits loose changes in small slices, in the repo's message style.
- Before the checks, a separate reader reads the diff for comments only. It keeps a comment only if the comment warns about a trap: something that breaks if the next person edits the code blindly.
- Claude removes or shortens each comment that the reader lists, and commits that change as its own slice.
- It runs the fast checks that the repo's `CLAUDE.md` names. If one fails, it stops and opens no PR.
- If a PR is already open for the branch, it pushes and reports the URL. It does not open a duplicate.
- The PR body follows the repo's template. Otherwise it holds a short summary, a `Related` line, an `Evidence` line and a `Merge danger` line.
- Evidence videos and screenshots show each click and key press, play at a person's pace, and leave out sign-in and cleanup. They are attached to the PR with `gh --attach`.
- It links the issue as related and never writes `Closes`, `Fixes` or `Resolves`.
- Before it opens the PR, Claude reads the title and body for AI-sounding prose, such as arrows and metaphor nouns, and rewrites it.

## Limits

- It leaves out the `Evidence` line when no end-to-end run happened. It does not invent one.
- It leaves out the `Related` line when it finds no issue.
- It adds no AI attribution and no co-author trailer.
- It does not change the draft or ready state of an existing PR.
- It has no settings. The arguments are `draft` and a base branch.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [references/claude-code.md](references/claude-code.md): how the comment reader runs in Claude Code.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not match the skill.
