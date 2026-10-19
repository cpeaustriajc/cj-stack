# commit

A skill that commits your uncommitted changes in small logical commits, in the repo's message style, then pushes the branch. It is the terminal version of the desktop Commit and push button.

## When to use it

Type `/commit` when you want your work saved as clean commits. The skill sets `disable-model-invocation`, so it runs only when you type the command. Claude never starts it alone.

Do not use it to open a pull request: use `create-pr`. Do not use it to review changes: use `interrogate`.

## Example

You type: `/commit`

1. Claude reads `git status`, `git diff HEAD` and the last 10 commit messages.
2. Claude splits the changes into one commit for each concern.
3. Claude pushes the current branch.

You get one `<sha> <subject>` line for each commit, the branch name, and whether Claude pushed. Type `/commit local` to skip the push.

## Install

The `cj-stack` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-stack@cj-stack
```

To turn the plugin off, run `claude plugin disable cj-stack@cj-stack`. This also turns off every other skill in `cj-stack`.

## What it does

- It stages files by path and never stages everything blindly.
- It never commits `.env`, credentials or ignored files.
- It adds no AI attribution and no co-author trailer.
- If you are on the default branch, it creates a `claude/<short-topic>` branch first, because a hook requires the prefix.
- It pushes with `-u`, unless you pass `local`.
- If the remote moved and the push fails, it pulls with rebase only when the rebase applies cleanly.

## Limits

- On any rebase conflict, it stops and tells you. It does not resolve the conflict.
- It does not open a pull request or write a PR body.
- It does not review the code it commits.
- It has no settings. The only argument is `local`.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not match the skill.
