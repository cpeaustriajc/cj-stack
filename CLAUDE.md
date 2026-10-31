# dotfiles

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
- Prove a skill fires and helps, scored against a run without the plugin
  (`.claude/rules/claude-code-authoring.md`).
- Check a plugin's components and projected token cost.
- Run a mod's hook tests after you change the mod.
- Audit the instruction files when a new frontier model ships, and audit a skill or rule after
  you edit it.
- From any of these audits, cut duplicate, dead or stale lines and rules whose failure no
  longer occurs without them; a rule that still prevents a failure moves to its right file,
  never drops.
- Draft skills and plugin parts with the harness's own authoring helpers.

## Buckets

- `.claude-plugin/marketplace.json` is the only manifest. Each plugin has one entry there with its
  version, description and author.
- Each mod has a `.claude-plugin/plugin.json` with only its `name`, `types` and `userConfig`;
  display fields and `version` stay in the marketplace entry. Without it, `claude plugin validate`
  finds no manifest in the mod's folder and does not check its `$.state` keys against `types`, and
  `claude plugin test` reads no `userConfig` defaults (linear-gate failed 86 of 105 tests). With it,
  the entry's `userConfig` does not apply.
- `plugins/<plugin>/skills/<skill>/`: the shipped skill plugins `design`, `engineering`,
  `planning`, `knowledge`, `writing` and `principles`. A plugin's own evals go in `plugins/<plugin>/evals/`.
- `mods/<mod>/`: one plugin for each mod.
- To retire a skill or a mod, delete its folder in one commit. Write its name in the commit
  message, so that `git log --diff-filter=D` finds it.
- `evals/routing/` and `evals/behaviour/`: eval cases across all shipped skills.
- Every skill and mod folder has a `README.md` for people: `.claude/rules/wiki.md` says how to
  write it, and `python3 -I scripts/check_readmes.py` checks it.

## Moving a skill

Move a skill to a different plugin in one commit:

1. Move the folder with `git mv`.
2. Update its row in the README Skills table, and its install lines in its own README.
3. In `marketplace.json`, increase the `version` of each plugin that gets or loses the skill
   (minor for an added or moved skill, patch for an edit).

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

`home/` is the chezmoi source (`.chezmoiroot`); `home/dot_claude/` is the `~/.claude` config.
Never share machine state (`projects/`, memory, transcripts, `.claude.json`).

- Edit here, then `chezmoi diff` and `chezmoi apply`.
- `settings.json` syncs only the keys in `home/dot_claude/.settings.json`; every other key stays
  on the machine. To keep a live edit of a synced key, run `home/dot_claude/.settings-capture.sh`.
- This repo is public: no sensitive information.
