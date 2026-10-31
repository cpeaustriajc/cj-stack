---
paths:
  - "plugins/**"
  - "lab/**"
  - "evals/**"
  - "mods/**"
  - "**/.claude-plugin/*.json"
  - "CLAUDE.md"
---

# Claude Code commands for the authoring steps

The section "Authoring" in `CLAUDE.md` names each step. This file gives the Claude Code command
for it. Use what Claude Code ships before writing your own checks.

## Validate the manifests

- `claude plugin validate .` after any manifest, skill or frontmatter change.

## Prove a skill fires and helps

- `claude plugin eval <plugin>` to prove a skill fires and helps, scored against a no-plugin
  baseline. It reads cases from `evals/` at the plugin root (`plugins/<plugin>/`), or from the
  folder that `--eval-dir` names (`evals/routing/`, `evals/behaviour/`, `lab/evals/`). A skill's
  own `evals/evals.json` is skill-creator's format, which it doesn't read.
  - While you iterate, run one case with `--case <name> --runs 1 --max-cost-usd 3`. Run the
    full suite at the default runs once, at the end.
  - After a grader fix, rerun only the cases that grader scores (`--case`).
  - If the no-plugin baseline passes a case, the case cannot show a gain. Make it harder or
    drop it; do not rerun it.

## Check a plugin's components and token cost

- `claude plugin details <plugin>` for a plugin's components and projected token cost.

## Run a mod's hook tests

- `claude plugin test mods/<mod>` for a mod's hook tests.

## Audit the instruction files

- `/doctor prompt-audit` when a new frontier model ships, and `/doctor prompt-audit <path>` after
  editing a skill or rule: flags dated instructions, conflicts and missing files. Headless runs
  skip `~/.claude` unless given `--add-dir ~/.claude`.
- `claude-md-improver` (claude-md-management) when CLAUDE.md drifts from the code;
  `/revise-claude-md` at the end of a session that exposed missing context.

## Draft skills and plugin parts

- `skill-creator` and `plugin-dev` (claude-plugins-official) for drafting skills and plugin parts.
