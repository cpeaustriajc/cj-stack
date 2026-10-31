# cj-stack

Write every rule, skill line and mod on the assumption that a later model makes it obsolete:
name the failure it prevents, so a run without it can show when that failure stops. When a
frontier model ships from any vendor the stack runs on, or a vendor engineering blog publishes
a best-practice article on coding agents, audit the stack with the instruction-file tools below
and trim before you add: cut any rule whose failure a model no longer makes without it.

## Build only what the tools lack

- Before you add or change a skill, mod, hook, script or rule, find the nearest native feature
  in each tool in use: the agent harness, the code host, CI and the tracker. Read that tool's
  current docs and changelog.
- If a tool does the job, use its feature. If it does part of the job, build only the missing
  part. A skill holds the method; its per-tool adapter points to the native feature, and
  rebuilds it only for a tool that has none.
- Hand off only to a stable feature. A preview can go away, so for a preview the skill keeps its
  method and the adapter only points to the feature.
- A guard hands off only to a feature with the same guarantee: one that holds every time. A
  model's judgment or a mode the user switches can fail, so it never replaces a guard.
- Failure: `hone` re-read transcripts that Claude Code's `/insights` and auto memory already
  mine.

## Prior art

After the native-feature check above, look for others who solved the same problem before you
add or change a skill or mod. Prior art is a hypothesis, not an authority: a known name does
not make a claim true, and a source that was right before can be wrong now.

- Weigh each claim by what it shows, not by who wrote it: code you can read or run, a measured
  result, a failure it names. A claim with no evidence is only a lead.
- Adopt an idea or another stack's skill only when the skill eval shows a gain over what it
  replaces: our skill, or a run without the plugin. A tie keeps ours. Until then, mark it
  untested.
- In the skill's or mod's README, name the source and the evidence you used, so an audit can
  remove the idea when that evidence no longer holds.

## Authoring

- Check `SCOPE.md` before adding a skill or mod.
- Copy a fan-out only when its agents work in parallel or need a fresh context; otherwise fold
  it into the main loop.
- Put each agent on the cheapest model that can do its job (see `models/README.md`).
- `SOURCES.md` lists where to look for new articles and leads; being on it is no reason to
  trust a claim.
- Validate the manifests after any manifest, skill or frontmatter change.
- Prove a skill fires and helps, scored against a run without the plugin. While you iterate,
  run one case once at a capped cost; run the full suite once, at the end. After a grader fix,
  rerun only the cases that grader scores. A case the no-plugin run already passes cannot show
  a gain: make it harder or drop it.
- Check a plugin's components and projected token cost.
- Run a mod's hook tests after you change the mod.
- Audit the instruction files when a new frontier model ships, and audit a skill or rule after
  you edit it.
- From any of these audits, cut duplicate, dead or stale lines and rules whose failure no
  longer occurs without them; a rule that still prevents a failure moves to its right file,
  never drops.
- Draft skills and plugin parts with the harness's own authoring helpers.

## Buckets

- `skills/planning/`, `skills/knowledge/`, `skills/quality/`, `skills/shipping/`: shipped in the `cj-stack` plugin.
- `skills/craft/`: shipped in the opt-in `cj-paint` plugin.
- `skills/in-progress/`: not shipped in `cj-stack`. A skill starts here; the opt-in `cj-lab` plugin may list one to try it.
- `skills/archived/`: shipped only in the opt-in `cj-jira` plugin, or not at all. Never delete a skill; archive it.
- Every skill and mod folder has a `README.md` for people: `.claude/rules/wiki.md` says how to
  write it, and `python3 -I scripts/check_readmes.py` checks it.

## Moving a skill

A skill changes bucket in one commit that also updates:

1. its path in the `skills` array of the right plugin's `plugin.json`: `skills/.claude-plugin/` for
   cj-stack, `skills/<bucket>/.claude-plugin/` for the opt-in plugins
2. its row in the README Skills table
3. the `version` in that `plugin.json` (minor for an added or moved skill, patch for an edit)

Then validate the manifests.

## Tool-neutral

A shipped skill holds a method that works on any tool. Tool mechanics go in `references/<tool>.md`
adapters; a team's roles, rules and taste stay in that team's repo, which the skill reads first.

A mod never denies or overrides what Claude Code already decides: the permission mode, edits to
its settings and hooks, the auto-mode classifier. It adds only what the harness lacks.
`python3 tests/claude-owned/run.py` checks it.

## Copies

This repo is the only source. Never hand-copy a skill into `~/.claude/skills` or a project's
`.agents/skills`: a copy drifts, and a skill installed both ways is listed twice in every session.

## Claude config is shared through chezmoi

`home/claude/` is the source of the `~/.claude` files shared with a Windows machine (Git Bash, so
paths start with `~`). The dotfiles repo (`$(chezmoi source-path)`) holds templates that include
them, and the private parts.

- Edit here, then `chezmoi diff` and `chezmoi apply`: an apply silently reverts what Claude Code
  wrote to `settings.json`. `chezmoi re-add` does not work on the templates.
- For `settings.json`, run `dot_claude/.settings-capture.sh` in dotfiles: public part here,
  private permissions to `.settings-private.json` there; commit both. `.settings-deny.json` stays
  on this machine.
- This repo is public: no sensitive information.
