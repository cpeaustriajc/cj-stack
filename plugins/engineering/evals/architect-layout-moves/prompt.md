---
name: architect-layout-moves
runs: 2
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Skill, Read, Glob, Grep, Agent, Write, Edit, Bash]
append_system_prompt: "Non-interactive run: nobody answers questions. The owner said beforehand: after you show the two candidates, take the one you recommend as their pick, and go on."
---

/engineering:architect make the routes thin
