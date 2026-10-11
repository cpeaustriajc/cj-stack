# cj-stack

When a new frontier model ships (Fable or Opus tier), audit the stack with the instruction-file
tools below and trim before you add: cut any rule you would follow without being told.

## Authoring tools

Use what Claude Code ships before writing your own checks:

- `claude plugin validate .` after any manifest, skill or frontmatter change.
- `claude plugin eval <plugin>` to prove a skill fires and helps, scored against a no-plugin
  baseline. It reads cases from `evals/` at the plugin root; a skill's own `evals/evals.json` is
  skill-creator's format, which it doesn't read.
- `claude plugin details <plugin>` for a plugin's components and projected token cost.
- `claude plugin test mods/<mod>` for a mod's hook tests.
- `/doctor prompt-audit` when a new frontier model ships, and `/doctor prompt-audit <path>` after
  editing a skill or rule: flags dated instructions, conflicts and missing files. Headless runs
  skip `~/.claude` unless given `--add-dir ~/.claude`.
- `claude-md-improver` (claude-md-management) when CLAUDE.md drifts from the code;
  `/revise-claude-md` at the end of a session that exposed missing context.
- From any of these audits, cut only duplicate, dead or stale lines; a real rule moves to its
  right file, never drops.
- `skill-creator` and `plugin-dev` (claude-plugins-official) for drafting skills and plugin parts.

## Buckets

- `skills/planning/`, `skills/knowledge/`, `skills/quality/`, `skills/shipping/`: shipped in the `cj-stack` plugin.
- `skills/craft/`: shipped in the opt-in `cj-paint` plugin.
- `skills/in-progress/`: not shipped. A skill starts here.
- `skills/archived/`: shipped only in the opt-in `cj-jira` plugin, or not at all. Never delete a skill; archive it.

## Moving a skill

A skill changes bucket in one commit that also updates:

1. its path in the `skills` array of the right plugin in `.claude-plugin/marketplace.json`
2. its row in the README Skills table
3. the plugin's `version` (minor for an added or moved skill, patch for an edit)

Then run `claude plugin validate .`.

## Tool-neutral

A shipped skill holds a method that works on any tool. Tool mechanics go in `references/<tool>.md`
adapters; a team's roles, rules and taste stay in that team's repo, which the skill reads first.

## Copies

This repo is the only source. Never hand-copy a skill into `~/.claude/skills` or a project's
`.agents/skills`: a copy drifts, and a skill installed both ways is listed twice in every session.
