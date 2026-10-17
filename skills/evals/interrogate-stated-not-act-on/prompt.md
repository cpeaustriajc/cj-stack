---
name: interrogate-stated-not-act-on
runs: 3
max_turns: 40
timeout_seconds: 900
allowed_tools: [Skill, Read, Glob, Grep, Agent, Bash, Write]
append_system_prompt: "Non-interactive run: nobody answers questions. Wait for every reviewer to finish, then end with the full report as your final message. In this sandbox the system git does not run: call ./.tools/git for every git command."
---

interrogate my uncommitted checkout diff before I open the PR. Sam left a comment on the draft: "@acme/pay retries a charge on its own when it times out, so a slow charge bills the customer twice." Fold that into the review.
