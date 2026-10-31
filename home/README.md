# home

The user-level Claude Code config of this repo's author: the files that go in `~/.claude`. It
came from the private chezmoi repo, without that repo's history. The folder is `claude/`, not
`.claude/`, so that Claude Code does not load it as project config in this repo.

## How the files are installed

[chezmoi](https://www.chezmoi.io) installs them from the author's private chezmoi repo, on macOS
and in Git Bash on Windows. Each managed file there is a template that includes its file from
this folder, so this folder is the only source for them:

1. Clone this repo to `~/Projects/dotfiles`. The templates include files from that path.
2. Run `chezmoi diff`, then `chezmoi apply`.

To change a file, edit it here, then run step 2. `chezmoi re-add` does not work for these
templates. To keep a `settings.json` change made in the app, run `.settings-capture.sh` in the
chezmoi repo: it writes the public part to `claude/settings.json` and the private part to the
chezmoi repo.

## Not in this folder

- `settings.json` entries that name third-party domains, a client's MCP server or private key
  files. They stay in the chezmoi repo, and chezmoi appends them to the permission lists of
  `claude/settings.json`.
- The `autoMode` and `feedbackDrafts` settings keys. They name hosts and clients and stay on the
  machine.
- The playwright-cli skill: its own installer puts it in `~/.claude/skills/`.
- Machine state: transcripts, history, caches, backups.
