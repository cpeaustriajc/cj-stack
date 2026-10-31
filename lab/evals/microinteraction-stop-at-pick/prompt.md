---
name: microinteraction-stop-at-pick
runs: 2
max_turns: 30
timeout_seconds: 900
allowed_tools: [Skill, Read, Glob, Grep, Write, Edit]
append_system_prompt: "Non-interactive run: nobody answers questions."
---

/lab:microinteraction the goals page
