# home

The chezmoi source for the author's home folder: Claude Code config, zsh, nvim and tmux.
`.chezmoiroot` at the repo root names this folder, so chezmoi reads only `home/` and never the
marketplace folders. The Claude Code folder is `dot_claude/`, not `.claude/`, so that Claude Code
does not load it as project config in this repo.

## Install on a new machine

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply cpeaustriajc
```

This installs [chezmoi](https://www.chezmoi.io), clones `cpeaustriajc/dotfiles` and applies the
files to `~`. It works on macOS and Linux.

## What is in this folder

| Live file | Source |
|-----------|--------|
| `~/.claude/CLAUDE.md`, `statusline-command.sh`, `hooks/*`, `agents/*`, `skills/workflow-models/` | `dot_claude/` |
| `~/.claude/settings.json` | only the keys in `dot_claude/.settings.json`, merged by `dot_claude/modify_private_settings.json`; every other live key keeps its live text |
| `~/.config/nvim/` | `dot_config/nvim/` |
| `~/.config/tmux/` | `dot_config/tmux/`; `tmux.conf.tmpl` renders per OS |
| `~/.zshrc` | `dot_zshrc` |

tmux is deprecated: it is no longer maintained. Use `claude agents` for parallel sessions. The
status bar uses Catppuccin Mocha (dark) or Latte (light), chosen from the system appearance when
the config loads. After you change the appearance, press `prefix r` to reload.

## Change a file

- Edit the file here, then run `chezmoi diff` and `chezmoi apply`.
- `settings.json` syncs only the keys in `dot_claude/.settings.json`. To keep an app change to
  one of those keys, run `dot_claude/.settings-capture.sh`: it copies their live values here.
- The `settings-drift.sh` hook reports at session start when the live files differ from this
  folder.

## Not in this folder

- Every other `settings.json` key: hooks, plugins, permissions, `autoMode` and the UI choices.
  Each machine sets them itself; run `/auto-mode-setup` to teach auto mode about the machine.
- The playwright-cli skill: `playwright-cli install --skills -g` installs it.
- Machine state: transcripts, history, caches, backups.
