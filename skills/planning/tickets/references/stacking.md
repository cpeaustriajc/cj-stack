# Stack tools

The method is in `SKILL.md`: one bottom-to-top chain, each item's Stack line names its branch
and its base. This file maps that onto each tool. Use the tool the project already uses; with
none, use plain git and the PR base.

The PR's base branch is the record every tool shares: each PR targets the branch of the item
below it, the bottom PR targets the trunk. Land the chain bottom first.

| Step | Plain git + `gh` | `gh stack` | Graphite (`gt`) | git-town |
|---|---|---|---|---|
| Start the bottom item | `git switch -c <branch> <trunk>` | `gh stack init <branch>` | `gt create <branch>` on the trunk | `git town hack <branch>` |
| Start the next item on the one below | `git switch -c <branch> <base>` | `gh stack add <branch>` from the top branch | `gt create <branch>` from the top branch | `git town append <branch>` from the top branch |
| Open the PRs | `gh pr create --base <base>` per item | `gh stack submit` | `gt submit --stack` | `git town propose --stack` |
| After the bottom PR merges | `git rebase --onto <trunk> <old base> <branch>`, then `gh pr edit <pr> --base <trunk>`; repeat up the chain | `gh stack sync` | `gt sync` | `git town sync --stack` |
| Fix a wrong parent | `gh pr edit <pr> --base <base>` | see `gh stack --help` | see `gt --help` | `git town set-parent` |

- Where each tool stores the parent: `gh stack` in `.git/gh-stack`, git-town in git config,
  Graphite in its own metadata. None of them is in the ticket, so the Stack line stays the
  source a fresh thread reads.
- A thread that builds an item never rebases onto another item's branch on its own; the
  coordinator restacks after a merge, bottom up.
- Check each command with `--help` before the first use in a project: these tools change often.

Sources: `github/gh-stack` README; graphite.com/docs/cheatsheet; git-town.com/stacked-changes
and its command pages; the autopilot-stack playbook in `cursor/plugins` (pstack), which keeps one
linear stack and records the parent only as the PR base.
