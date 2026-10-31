# git-guard

A mod (a plugin that adds a hook to Claude Code) that denies a git command which loses work. Each deny message names the safe command to run instead.

## Why

Claude sometimes cleans up with a git command that cannot be undone. `git branch -D` deletes unmerged commits. A force push to `main` rewrites history that other people pulled. `git checkout -- .` throws away every uncommitted edit.

git-guard denies these commands and tells Claude the safe way to do the same job.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install git-guard@cj-stack
```

To see that it is on, run `claude plugin list` and look for `git-guard`. The mod is optional: `cj-stack` does not install it.

## Example

1. Claude has edited three files and runs `git checkout -- .` to start again.
2. The hook runs `git status --porcelain --untracked-files=no` and finds changed files.
3. The hook denies the command. Claude reads: "git-guard: this discards the uncommitted changes in every tracked file."
4. Claude runs `git stash push -u -m retry`, then starts again with the edits saved.

## What it does

The hook checks every Bash command. It ignores text inside quotes and comments, so `git commit -m "git push -f origin main"` passes.

| Command | Decision | Safe way out in the deny text |
|---|---|---|
| `git branch -D`, or `-d` with `-f` or `--force` | Deny. | `git branch -d <branch>`, which deletes only a merged branch |
| `git push` with `--force`, `-f`, `--force-with-lease` or a `+` refspec, to `main` or `master` | Deny. | Push to your own branch and open a pull request, or `git revert <sha>` |
| A force push that names no branch, while the current branch is `main` or `master` | Deny. | The same as above |
| `git checkout -- .`, `git checkout .`, `git restore .` when a tracked file has changes | Deny. | `git stash push -u -m <tag>`, a WIP commit, or name only the files |
| `git branch -d`, `git push` without force, a force push to a feature branch | Pass. | |
| `git restore --staged .`, `git checkout -- src/app.ts`, `git reset --soft` | Pass. | |
| `git reset --hard`, `git clean -fd` | Pass: Claude Code decides these itself. | |
| The hook fails, or `git status` exits with an error | Deny with "could not check". | Name the branch and the files |

The hook follows `git -C <dir>` and a plain `cd <dir>` earlier in the same command when it reads the branch or the status.

## Settings

No settings and no allow list.

To turn the mod off, run `claude plugin disable git-guard@cj-stack`.

## Limits

- It does not deny `git reset --hard` or `git clean`. Claude Code and its auto mode decide those, and a mod never overrides them.
- It checks only the Bash tool. Git called from a script file, `bash -c "..."` or `eval` passes.
- A quoted branch name or path is not read: `git push -f origin "main"` passes.
- If a `cd` target is quoted or starts with `~`, the hook treats the tree as dirty and denies.
- It does not check `git push --mirror`, `git push --all` or a deleted remote branch.
- If the hook fails, it denies. Retry, or run a command that names the branch and the files.

## More

- [hooks/register.ts](hooks/register.ts): the hook source.
- [hooks/register.test.ts](hooks/register.test.ts): the tests.
- [marketplace.json](../../.claude-plugin/marketplace.json): the manifest, in this mod's entry.
- [mattpocock/skills git-guardrails-claude-code](https://github.com/mattpocock/skills/tree/main/skills/misc/git-guardrails-claude-code): the prior art. It blocks every `git push` by text match; git-guard blocks only the force push to `main`.
