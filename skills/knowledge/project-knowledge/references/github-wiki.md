# GitHub wiki adapter

A GitHub wiki is a git repository at `https://github.com/<owner>/<repo>.wiki.git`. Page `Foo Bar`
is the file `Foo-Bar.md`, and `[[Foo Bar]]` links to it. A private repo has a private wiki, and an
unauthenticated fetch of a page URL answers 404 even when the page exists. So check a page with
`git ls-remote` or the clone, never with `curl`.

## Use the script

`scripts/ghwiki.sh` keeps one managed clone per wiki under
`${XDG_CACHE_HOME:-~/.cache}/project-knowledge/github/<owner>/<repo>`. Every session and every
agent then edits the same copy, and nothing is left uncommitted in a scratch folder that someone
re-clones. The script uses `gh auth` for credentials.

```bash
S=<this skill's base directory>/scripts/ghwiki.sh
$S detect [owner/repo]     # "exists" | "missing" (wiki enabled but no first page) | "disabled"
$S path   [owner/repo]     # print the managed clone's path, cloning or pulling it first
$S list   [owner/repo]     # page names, one per line
$S save   [owner/repo] -m "message"   # commit every local change (no push)
$S push   [owner/repo] -m "message"   # commit, pull --rebase, push
$S status [owner/repo]     # uncommitted files and ahead/behind counts
```

If `owner/repo` is left out, it comes from the current directory's `origin` remote. Read and edit
the files under `$($S path)` with the normal file tools, then `save` straight away. `push` runs
only once the user has seen the change (see SKILL.md §5).

## Quirks

- **A wiki that was never initialised has no repo.** `detect` reports `missing`, and the user
  must create any first page in the web UI before a clone can work.
- **Keep dots, slashes and `#` out of page names.** GitHub maps a page's title to its file name
  loosely, and a dotted name breaks `[[links]]`.
- **The web editor commits too.** `push` rebases onto it. On a conflict, stop and show the user
  both versions. Never force-push a wiki.
- **Wiki pages bypass pull requests.** Nothing reviews them, which is why they are shown to the
  user before a push.
- **Link from the repo with the full URL**, `https://github.com/<owner>/<repo>/wiki/<Page-Name>`.
