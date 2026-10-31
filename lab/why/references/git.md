# Git and GitHub

Run these from the repo root. Replace `<file>`, `<a>,<b>` and `<text>` with the target.

## Seed anchor

```bash
git blame -L <a>,<b> -w -C -- <file>            # last touch per line, ignoring moves and whitespace
git log --oneline --follow -20 -- <file>        # recent history through renames, PR numbers visible
git log -S '<text>' --oneline -- <file>         # commits that added or removed this exact text
git log -1 --format='%H %an %ad%n%B' <sha>      # one commit's full message
```

The commit that added the line is the oldest hit of `git log -S`, not the newest blame line.
A blame hit that only reformats or moves code is not the origin; run `git blame <sha>^` on it.

## Deeper sweep

```bash
git log -G '<regex>' -p --follow -- <file>      # commits whose diff matches a pattern
git log --all --oneline --grep='<text>' -i      # messages that name an incident, issue or revert
git log --oneline --grep='^Revert' -- <file>    # revert chains: find the revert, then the reapply
git show <sha> --stat                           # files changed together (co-change)
git grep -n '<symbol>' -- '*test*' '*spec*'     # tests that pin the behaviour
git grep -n -E 'TODO|FIXME|HACK|XXX' -- <file>  # notes near the target
```

A test named for a case ("retries after 429", "rejects an empty cart") is evidence of the edge
case, not of who wanted it. A CHANGELOG or `docs/adr/` entry counts as an author's own words.

## Pull requests (GitHub)

```bash
gh pr view <n> --json title,body,author,mergedAt,closingIssuesReferences,comments,reviews
gh api repos/{owner}/{repo}/pulls/<n>/comments --jq '.[] | {path, line, user: .user.login, body}'
gh pr list --state merged --search '<sha>' --json number,title   # PR for a squash-merged commit
gh issue view <n> --json title,body,comments,labels
gh search issues --repo {owner}/{repo} '<text>' --json number,title,state
```

`gh pr view` leaves out inline review comments; the `pulls/<n>/comments` call has them. They
often hold the only "why" ("this guards against the null from the old API").

With no remote or no `gh` sign-in, PR and issue text is unavailable: say so in Sources.
