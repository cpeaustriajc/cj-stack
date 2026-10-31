---
name: no-comments-folder-sweep
runs: 2
max_turns: 80
timeout_seconds: 1500
allowed_tools: [Skill, Read, Glob, Grep, Agent, Write, Edit, Bash]
append_system_prompt: "Non-interactive run: nobody answers questions."
---

/lab:no-comments src/legacy
