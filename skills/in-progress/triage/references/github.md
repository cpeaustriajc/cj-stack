# GitHub adapter

Run `gh auth status` first. If it fails, ask the person to sign in.

## Read

```bash
gh label list --limit 100 --json name --jq '.[].name'
gh issue list --state open --limit 100 --json number,title,labels,createdAt,author
gh api 'repos/{owner}/{repo}/pulls?state=open&per_page=100' \
  --jq '.[] | "\(.number) \(.author_association) \(.user.login) \(.created_at) \(.title)"'
gh issue view <n> --comments
gh pr view <n> --comments
gh pr diff <n>
gh pr checkout <n>
gh search issues --repo <owner/repo> --state closed --label <wontfix label> "<concept>"
```

- An outside author: `author_association` is not `OWNER`, `MEMBER` or `COLLABORATOR`.
- A bare `#42` can be an issue or a PR: `gh issue view <n> --json url` also answers for a PR; the URL says `/pull/` or `/issues/`.
- "A reply after the last triage note": compare the dates of the last comment with the
  disclaimer and the reporter's last comment.

## Write

```bash
gh label create "<name>" --description "<state>"        # only after the person says yes
gh issue edit <n> --add-label "<state>,<category>" --remove-label "<old state>"
gh pr edit <n> --add-label "<state>,<category>" --remove-label "<old state>"
gh issue comment <n> --body-file brief.md
gh issue close <n> --reason "not planned" --comment "<reason>"
```

Every write notifies the watchers. Put the labels and the comment in one pass per item.
