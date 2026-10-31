# Features

One file per feature. **Code** lists the paths it owns; `select.sh` maps a diff to features
by these paths. **Tests** and **Check** are the commands that prove it.

| Feature | File | Code |
|---|---|---|
| Skills | [skills.md](skills.md) | `plugins/**`, `lab/**`, `evals/**`, `.claude/skills/**` |
| Mods | [mods.md](mods.md) | `mods/<mod>/**`, `tests/claude-owned/**` |
| Manifests and READMEs | [manifests.md](manifests.md) | `**/.claude-plugin/**`, `README.md`, `**/README.md`, `scripts/check_readmes.py` |
| Routing | [routing.md](routing.md) | `evals/routing/**`, any `SKILL.md` frontmatter |
