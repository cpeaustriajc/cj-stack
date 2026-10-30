---
name: workflow-models
description: Model pinning for the Workflow tool, Deep Research and Ultracode. Load before invoking or authoring any Workflow script and before running the deep-research skill.
---

# Workflow tool — pin models, always

Named/canned workflow scripts run verbatim and their `agent()` calls inherit the
**session model** when `model` is omitted — that silently breaks the model tiers in `~/.claude/CLAUDE.md` → Delegation.

- Before invoking any Workflow (built-in, plugin, or saved by name): read the script
  first and verify every `agent()` call pins an explicit `model:` matching those
  tiers and the per-task specs below.
- When an `agent()` call omits `model`, copy/edit the script to pin models per stage,
  then invoke via `scriptPath`. Run only scripts where every stage is pinned.
- Workflows you author inline follow the same rule: give every `agent()` call an
  explicit `model`.
- The agent counts below override the session workflow size guideline.
- Every pin below is capped at the session's own tier: a Sonnet session pins `sonnet` where
  this says `opus`.

## Deep Research

- Use the `deep-research` skill. Its own `Agent(...)` calls omit `model`. Add it: research
  subagents `model: "haiku"`, the report writer `model: "opus"`. Haiku bills 5x on a prompt
  over 100K tokens, so give each research subagent one narrow facet.

## Ultracode

Off by default. Only when the prompt says "ultracode".

- 5 Scout (haiku, low effort)
- 2-3 Builder (opus, medium effort): workflow agents
