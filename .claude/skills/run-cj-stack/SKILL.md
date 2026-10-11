---
name: run-cj-stack
description: Run, test, validate and inspect the cj-stack marketplace as a user's Claude Code loads it - plugin validation, every mod's hook tests, the skill script tests, `claude plugin details` token costs and `/skill-doctor` with the plugin installed. Use to check a change to a skill, mod or manifest before committing, to see what a skill costs per turn, or to run skill-doctor on cj-stack.
---

# Run cj-stack

cj-stack has no app to launch: the "running" product is the marketplace as Claude Code installs
it. The driver is `.claude/skills/run-cj-stack/smoke.sh`, which validates it, runs every test
suite, installs the plugin into a throwaway config directory and asks Claude Code what it loaded.
Paths here are relative to the repo root.

## Prerequisites

`claude`, `python3` and `bash`. Nothing to install or build.

## Run (agent path)

```bash
.claude/skills/run-cj-stack/smoke.sh all       # everything, about 20 s; exit 0 when all pass
.claude/skills/run-cj-stack/smoke.sh validate  # claude plugin validate .
.claude/skills/run-cj-stack/smoke.sh tests     # each mod's hook tests + skill script tests
.claude/skills/run-cj-stack/smoke.sh details   # skills and per-skill token cost, always-on and on-invoke
.claude/skills/run-cj-stack/smoke.sh doctor    # /skill-doctor with cj-stack installed
```

`doctor` and `details` install the local working tree (not the pushed one) into a `mktemp -d`
config directory, so your real `~/.claude` never changes and the temp directory is removed on
exit.

One mod or script at a time:

```bash
claude plugin test mods/session-modes
python3 -I skills/planning/shape/scripts/test_check_tree.py
bash skills/knowledge/hone/scripts/test_corrections.sh
```

## Gotchas

- **`/skill-doctor` runs headless**: `claude -p "/skill-doctor"` prints its table and exits.
- **`--plugin-dir .` loads none of cj-stack's skills.** The repo root is a marketplace
  (`.claude-plugin/marketplace.json` with `"source": "./"`, `"strict": false`), not a plugin, so
  skill-doctor shows only claude.ai and user skills. Install from the local marketplace instead,
  as the driver does.
- **A fresh `CLAUDE_CONFIG_DIR` still authenticates** in this container, so the throwaway install
  works for `claude -p` too.
- **The 7-day token and use columns are always empty** in the driver's throwaway config: they come
  from this machine's past sessions. For real usage, run `claude -p "/skill-doctor"` with your own
  config after installing the plugin there.
- **Skills in `skills/in-progress/` never appear**: they are not in the marketplace's skills
  array, by design.
- **`claude plugin validate skills/<bucket>/<skill>` always fails** with "No manifest found": a
  skill folder is not a plugin. Validate the repo root.
- **Python scripts leave `__pycache__`** in the skill folder; the driver deletes it, and
  `.gitignore` covers it.

## Not in the driver

- **secret-guard's suite** (`python3 mods/secret-guard/tests/secret_hooks_test.py --hooks-dir
  mods/secret-guard/hooks`) is left out of `all`: some cases need macOS `sandbox-exec`, and those
  haven't been separated from real failures on Linux.
- **`claude plugin eval <plugin>`** runs the cases under each skill's `evals/`; the driver
  doesn't.
