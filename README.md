# cj-stack

CJ's skills and mods for Claude Code.

## Install

```
/plugin marketplace add cpeaustriajc/cj-stack
/plugin install cj-stack@cj-stack
/plugin install work-pane@cj-stack
```

While editing a mod, add the local clone instead (`/plugin marketplace add ~/Projects/cj-stack`):
a directory marketplace hot-reloads.

Other agents (Codex and anything that reads `~/.agents/skills`): `scripts/link-skills.sh`.

## Plugins

| Plugin | Contents | Install |
|---|---|---|
| `cj-stack` | the shipped skills below | by default |
| `work-pane` | a mod: holds Linear writes until you allow them; task progress and subagents in a pane | by default |
| `cj-paint` | painting-craft | where you paint in code |
| `cj-jira` | archived Jira-era skills | only for a Jira client |

## Skills

All skills are model-invoked: Claude picks them from their description.

| Skill | Bucket | What it is for |
|---|---|---|
| [linear-planning](skills/planning/linear-planning/SKILL.md) | planning | where a spec, story, AC, dependency or risk lands in Linear |
| [linear-project](skills/planning/linear-project/SKILL.md) | planning | drafting, auditing and updating Linear projects |
| [project-knowledge](skills/knowledge/project-knowledge/SKILL.md) | knowledge | a decision log and research pages in the team's wiki, Notion, Linear, Obsidian or Confluence |
| [painting-craft](skills/craft/painting-craft/SKILL.md) | craft | drawing and painting in code to a gallery standard, with a screenshot review loop |
| [jira-ticket](skills/archived/jira-ticket/SKILL.md) | archived | Jira tickets and acceptance criteria |
| [draft-ticket](skills/archived/draft-ticket/SKILL.md) | archived | end-to-end Jira ticket drafting |
| [github-issue](skills/archived/github-issue/SKILL.md) | archived | GitHub issues holding a Jira ticket's engineering detail |
| [project-wiki](skills/archived/project-wiki/SKILL.md) | archived | GitHub-wiki-only predecessor of project-knowledge |

The archived skills and painting-craft's `worlds.md` were written for one project and still name its files.
