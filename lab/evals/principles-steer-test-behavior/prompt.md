---
name: principles-steer-test-behavior
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Glob, Grep, Bash, Edit, Write]
append_system_prompt: "Non-interactive run: nobody answers questions. Finish the task, then end with a short report as your final message."
---

Apply test behavior, not implementation to test_checkout.py.
