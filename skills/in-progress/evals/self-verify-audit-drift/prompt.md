---
name: self-verify-audit-drift
runs: 2
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Glob, Grep, Bash, Agent, Edit, Write]
---

audit the verify skill. there's no remote, so don't open a PR: tell me the outcome and what the PR would change. if `git` fails in this sandbox, use /Library/Developer/CommandLineTools/usr/bin/git
