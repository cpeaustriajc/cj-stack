---
name: architect-stop-at-pick
runs: 2
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Glob, Grep, Agent, Write, Edit]
append_system_prompt: "Non-interactive run: nobody answers questions."
---

/engineering:architect add a weekly digest email that lists each user's notes changed in the last 7 days. Users must be able to turn the digest off without turning off reminder emails, and the reminder worker should use the same preference rules.
