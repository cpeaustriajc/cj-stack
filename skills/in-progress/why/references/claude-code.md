# Claude Code

- An investigator is an `Agent` call with `subagent_type: "general-purpose"`: it needs Bash for
  git and the MCP tools of its source. `Explore` has neither.
- Send every investigator `Agent` call in one message, so they run in parallel.
- Source control: `model: "haiku"`. It runs commands and quotes their output.
- Tracker, docs or wiki: `model: "sonnet"`, `effort: "medium"`. It must judge stale, boilerplate
  and superseded text.
- Never `model: "opus"` for an investigator. The main session synthesizes.
- An MCP that needs sign-in (it says so at session start) is unavailable. Do not start an
  investigator for it; list it as a gap.
- For the decision log, use the project-knowledge adapters, not your own queries.
