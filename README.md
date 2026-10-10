| `session-modes` | a mod: `/mode audit`, `no-pr` or `chat`, enforced for the session | optional |
| `denial-explainer` | a mod: names the rule behind an auto-mode denial and the allow rule that would cover it | optional |
| `loop-brake` | a mod: ends a turn after N forced Stop-hook continuations | optional |
# cj-stack

CJ's skills and mods for Claude Code.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-stack@cj-stack
/plugin install work-pane@cj-stack
/plugin install usage-pace@cj-stack
/plugin install session-modes@cj-stack
/plugin install denial-explainer@cj-stack
/plugin install loop-brake@cj-stack
```

While editing a mod, add the local clone instead (`/plugin marketplace add ~/Projects/cj-stack`):
a directory marketplace hot-reloads.

Other agents (Codex and anything that reads `~/.agents/skills`): `scripts/link-skills.sh`.

## Plugins

| Plugin | Contents | Install |
|---|---|---|
| `cj-stack` | the shipped skills below | by default |
| `work-pane` | a mod: holds Linear writes until you allow them; test runs in a pane | by default |
| `usage-pace` | a mod: weekly usage in the status line, and whether it lasts until your reset | optional |
| `cj-paint` | painting-craft | where you paint in code |
| `cj-jira` | archived Jira-era skills | only for a Jira client |

## Skills

All skills are model-invoked: Claude picks them from their description.

| Skill | Bucket | What it is for |
|---|---|---|
| [work-planning](skills/planning/work-planning/SKILL.md) | planning | shaping work in any tracker (Linear, Jira, GitHub, others): specs, work items, phases, projects, updates |
| [project-knowledge](skills/knowledge/project-knowledge/SKILL.md) | knowledge | a decision log and research pages in the team's wiki, Notion, Linear, Obsidian or Confluence |
| [painting-craft](skills/craft/painting-craft/SKILL.md) | craft | drawing and painting in code to a gallery standard, with a screenshot review loop |
| [jira-ticket](skills/archived/jira-ticket/SKILL.md) | archived | Jira tickets and acceptance criteria |
| [draft-ticket](skills/archived/draft-ticket/SKILL.md) | archived | end-to-end Jira ticket drafting |
| [github-issue](skills/archived/github-issue/SKILL.md) | archived | GitHub issues holding a Jira ticket's engineering detail |
| [linear-planning](skills/archived/linear-planning/SKILL.md) | archived | Linear-only predecessor of work-planning (not shipped) |
| [linear-project](skills/archived/linear-project/SKILL.md) | archived | Linear-only predecessor of work-planning (not shipped) |
| [project-wiki](skills/archived/project-wiki/SKILL.md) | archived | GitHub-wiki-only predecessor of project-knowledge |

The archived skills were written for one project and still name its files. Shipped skills stay tool-neutral: tool specifics go in a skill's adapters, and a project's own facts stay in that project.

## painting-craft: before and after

The same two prompts, each run once in a fresh session: the original skill on the left, the current
painting-craft on the right. Nothing was touched up by hand.

**"Paint a 1600x1000 SVG of a knight asleep against an oak tree at dusk, in a Romantic oil-painting look."**

![Knight at dusk, full picture: before and after](docs/images/knight-full.jpg)

At 2× zoom, where the viewer looks. The knight is a 3D figure lit by the low sun, with separate
plates, mail in rows and a visor, instead of a mannequin of tubes:

![Knight at dusk, 2x crop: before and after](docs/images/knight-zoom.jpg)

**"Draw a night city street as a 1600x1000 SVG: a car passes behind a row of trees on the near verge.
Flat vector style, but it must not look cheap."**

![Night street, full picture: before and after](docs/images/street-full.jpg)

At 2× zoom, a crown is clumps hung on a branch skeleton, in three values with broken edges, instead
of a pile of round blobs:

![Night street, 2x crop of a tree: before and after](docs/images/street-zoom.jpg)

What changed: build recipes for the parts that fail up close (`references/recipes.md`), studies of
each hero element against fetched public-domain references before composing (`scripts/refs.py`,
`scripts/compare.py`), the bundled 3D figure renderer, a paint pass that unifies painted styles
(`scripts/paintpass.py`), and delivery at twice the display size.
