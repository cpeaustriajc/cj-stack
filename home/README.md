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
templates. `settings.json` syncs only the keys in `claude/settings.json`. To keep an app change
to one of those keys, run `.settings-capture.sh` in the chezmoi repo: it copies their live values
to `claude/settings.json`.

## Not in this folder

- Every other `settings.json` key: hooks, plugins, permissions, `autoMode` and the UI choices.
  Each machine sets them itself; run `/auto-mode-setup` to teach auto mode about the machine.
- The playwright-cli skill: its own installer puts it in `~/.claude/skills/`.
- Machine state: transcripts, history, caches, backups.
