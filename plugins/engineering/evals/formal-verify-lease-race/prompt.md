---
name: formal-verify-lease-race
runs: 2
max_turns: 60
timeout_seconds: 1500
allowed_tools: [Skill, Read, Glob, Grep, Bash, Agent, Edit, Write]
---

the job runner's tests all pass, but I don't trust the lease logic. formally verify it and leave a check the next agent can run when they touch it. don't change the product code. if `git` fails in this sandbox, use /Library/Developer/CommandLineTools/usr/bin/git
