# Scope

cj-stack is a skill stack for one developer. Its skills hold methods that work on any tool. A
fan-out runs each agent on the cheapest model that can do its job: see
[models/README.md](models/README.md).

## Rejected

An idea goes on this list only with a reason. If you change your mind later, edit its line. Do
not add a new dated line.

- **Skill-fire log mod**: `/skill-doctor` already reports the uses, the last-used date and the
  7-day tokens of each skill.
- **Careful mode** (hooks that run only while a skill runs): a hook in skill frontmatter stays on
  for the rest of the session after the skill starts. See "Hooks in skills and agents" in the
  [hooks docs](https://code.claude.com/docs/en/hooks). Also, a deny would override the
  permission mode, and a mod never does that.
- **Multi-model panels** (arena, a model mix in interrogate, cross-family judges): they need
  models from another vendor.
- **Autopilot** and **orchestrate**: they need a fleet of agents.
- **Babysit's watcher**: it needs a fleet of agents that watch pull requests.
- **Cursor automations**, **Bugbot** and **Grok Bot UI**: they work only in Cursor.
- **Cloud agents** from pstack: they need Cursor's cloud agents.
- **setup-pstack's model map**: it maps models from other vendors.
