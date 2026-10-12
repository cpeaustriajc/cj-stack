---
name: run-cj-stack
description: >
  This skill should be used to run, test, validate or inspect the cj-stack marketplace as Claude
  Code loads it: plugin validation, every mod's tests, the skill script tests, plugin token costs,
  /skill-doctor with the plugin installed, and the trigger and routing evals. Use it before
  committing a change to a skill, mod or manifest, or to see what a skill costs per turn.
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
.claude/skills/run-cj-stack/smoke.sh routing   # claude plugin eval on evals/routing, about $2; RUNS=1 halves it
```

`routing` checks that each request loads its own skill and not its nearest neighbour, with every
shipped skill installed together, plus `drive` and `scout` from `in-progress` (linked into the
eval plugin only), and that the typed-only `commit` and `create-pr` never load on their own. Each case in `evals/routing/<case>/` is a `prompt.md` plus
`tool_used` graders on the Skill call. Add a case when a new skill's triggers could collide with
an old one's.

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
- **`claude plugin eval .` resolves no plugin** ("none resolved — cases run against baseline"):
  the repo root has no `plugin.json`. The driver builds a throwaway plugin of symlinks instead.
  The routing cases cap `max_turns` at 3, so "Reached maximum number of turns" in the notes is
  expected; the Skill call comes on turn 1.
- **`claude plugin validate skills/<bucket>/<skill>` always fails** with "No manifest found": a
  skill folder is not a plugin. Validate the repo root.
- **Python scripts leave `__pycache__`** in the skill folder; the driver deletes it, and
  `.gitignore` covers it.

## Not in the driver

- **secret-guard's suite** (`python3 mods/secret-guard/tests/secret_hooks_test.py --hooks-dir
  mods/secret-guard/hooks`) is left out of `all`: some cases need macOS `sandbox-exec`, and those
  haven't been separated from real failures on Linux.
- **`claude plugin eval <plugin>`** reads cases from `evals/` at the plugin root, not from a
  skill's `evals/`; in the driver only `routing` runs it, and `all` leaves it out.
- **Trigger checks.** Each skill's `evals/triggers.json` holds should-trigger and near-miss prompts
  for skill-creator's `run_eval`. `run_eval` ignores
  `disable-model-invocation`, so for the typed-only `commit` and `create-pr` it measures only the
  description; the routing suite checks that they never load on their own. Run `run_eval` from an
  empty folder that has a `.claude/` directory, with `--num-workers 1`: parallel workers each write a
  copy of the skill into the same `.claude/commands/`, Claude invokes another worker's copy, and
  the run scores as a miss. A prompt that points at content it doesn't include ("file these
  bugs") makes Claude look for the content first, which also scores as a miss.
- **Descriptions** follow plugin-dev's rules (`tests` checks them): third person ("This skill
  should be used when…"), at most 500 characters, and a `>` block scalar, since an unquoted
  description containing `": "` is invalid YAML that `claude plugin validate` doesn't catch.
