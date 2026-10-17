---
name: interrogate-act-on-recall
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Glob, Grep, Agent, Bash, Write]
append_system_prompt: "Non-interactive run: nobody answers questions. Wait for every reviewer to finish, then end with the full report as your final message. In this sandbox the system git does not run: call ./.tools/git for every git command."
---

interrogate my uncommitted diff before I open the PR, it touches auth and payments
