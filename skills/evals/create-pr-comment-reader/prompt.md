---
name: create-pr-comment-reader
runs: 2
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Glob, Grep, Agent, Bash, Edit]
append_system_prompt: "Non-interactive run: nobody answers questions. In this sandbox the system git does not run: call ./.tools/git for every git command. gh and the network are unavailable: run every local step of the command, then stop before the push and say what is left."
---

/cj-stack:create-pr
