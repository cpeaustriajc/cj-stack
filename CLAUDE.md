# cj-stack

Write every rule, skill line and mod on the assumption that a later model makes it obsolete:
name the failure it prevents, so a run without it can show when that failure stops. When a
frontier model ships from any vendor the stack runs on, or a vendor engineering blog or a
prior-art author below publishes a best-practice article on coding agents, audit the stack with
the instruction-file tools below and trim before you add: cut any rule whose failure a model no
longer makes without it.

## Build only what the tools lack

- Before you add or change a skill, mod, hook, script or rule, find the nearest native feature
  in each tool in use: the agent harness, the code host, CI and the tracker. Read that tool's
  current docs and changelog.
- If a tool does the job, use its feature. If it does part of the job, build only the missing
  part. A skill holds the method; its per-tool adapter points to the native feature, and
  rebuilds it only for a tool that has none.
- Failure: `hone` re-read transcripts that Claude Code's `/insights` and auto memory already
  mine.

## Prior art

Before adding or changing a skill or mod, research how public AI-coding practitioners solve it:
their GitHub repos, blog posts and talks, such as `garrytan/gstack`, Lauren Tan's pstack
(`cursor/plugins`), `mattpocock/skills` and `emilkowalski/skills`. Copy a fan-out only when its
agents work in parallel or need a fresh context; otherwise fold it into the main loop. Put each
agent on the cheapest model that can do its job (see `models/README.md`). Skip only what needs
another vendor's models or a fleet of agents. Check `SCOPE.md` before adding a skill or mod.
`docs/sources.md` lists the blogs and authors to watch and how far to trust each.

## Authoring tools

Use what Claude Code ships before writing your own checks:

- `claude plugin validate .` after any manifest, skill or frontmatter change.
- `claude plugin eval <plugin>` to prove a skill fires and helps, scored against a no-plugin
  baseline. It reads cases from `evals/` at the plugin root (`skills/` for cj-stack,
  `skills/<bucket>/` for the opt-in plugins); a skill's own `evals/evals.json` is skill-creator's
  format, which it doesn't read.
  - While you iterate, run one case with `--case <name> --runs 1 --max-cost-usd 3`. Run the
    full suite at the default runs once, at the end.
  - After a grader fix, rerun only the cases that grader scores (`--case`).
  - If the no-plugin baseline passes a case, the case cannot show a gain. Make it harder or
    drop it; do not rerun it.
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
- `skills/in-progress/`: not shipped in `cj-stack`. A skill starts here; the opt-in `cj-lab` plugin may list one to try it.
- `skills/archived/`: shipped only in the opt-in `cj-jira` plugin, or not at all. Never delete a skill; archive it.
- Every skill and mod folder has a `README.md` for people: `.claude/rules/readme.md` says how to
  write it, and `python3 -I scripts/check_readmes.py` checks it.

## Moving a skill

A skill changes bucket in one commit that also updates:

1. its path in the `skills` array of the right plugin's `plugin.json`: `skills/.claude-plugin/` for
   cj-stack, `skills/<bucket>/.claude-plugin/` for the opt-in plugins
2. its row in the README Skills table
3. the `version` in that `plugin.json` (minor for an added or moved skill, patch for an edit)

Then run `claude plugin validate .`.

## Tool-neutral

A shipped skill holds a method that works on any tool. Tool mechanics go in `references/<tool>.md`
adapters; a team's roles, rules and taste stay in that team's repo, which the skill reads first.

A mod never denies or overrides what Claude Code already decides: the permission mode, edits to
its settings and hooks, the auto-mode classifier. It adds only what the harness lacks.
`python3 tests/claude-owned/run.py` checks it.

## Copies

This repo is the only source. Never hand-copy a skill into `~/.claude/skills` or a project's
`.agents/skills`: a copy drifts, and a skill installed both ways is listed twice in every session.
