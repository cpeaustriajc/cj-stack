# home

The user-level Claude Code config of the cj-stack author: the files that go in `~/.claude`. It
came from the private dotfiles repo, without that repo's history. The folder is `claude/`, not
`.claude/`, so that Claude Code does not load it as project config in this repo.

Nothing installs these files yet. `~/.claude` still comes from chezmoi.

## Not in this folder

- `settings.json` entries that name third-party domains, a client's MCP server or private key
  files. They stay on the author's machine and merge into the live settings there.
- The `autoMode` and `feedbackDrafts` settings keys. They name hosts and clients and stay on the
  machine.
- Machine state: transcripts, history, caches, backups.
