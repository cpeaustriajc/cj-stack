# home

The user-level Claude Code config of the cj-stack author: the files that go in `~/.claude`. It
came from the private dotfiles repo, without that repo's history. The folder is `claude/`, not
`.claude/`, so that Claude Code does not load it as project config in this repo.

## How the files are installed

[chezmoi](https://www.chezmoi.io) installs them from the author's private dotfiles repo, on macOS
and in Git Bash on Windows. Each managed file there is a template that includes its file from
this folder, so this folder is the only source for them:

1. Clone this repo to `~/Projects/cj-stack`. The templates include files from that path.
2. Run `chezmoi diff`, then `chezmoi apply`.

To change a file, edit it here, then run step 2. `chezmoi re-add` does not work for these
templates. To keep a `settings.json` change made in the app, run `.settings-capture.sh` in the
dotfiles repo: it writes the public part to `claude/settings.json` and the private part to the
dotfiles repo.

## Not in this folder

- `settings.json` entries that name third-party domains, a client's MCP server or private key
  files. They stay in the dotfiles repo, and chezmoi appends them to the permission lists of
  `claude/settings.json`.
- The `autoMode` and `feedbackDrafts` settings keys. They name hosts and clients and stay on the
  machine.
- The playwright-cli skill: its own installer puts it in `~/.claude/skills/`.
- Machine state: transcripts, history, caches, backups.
