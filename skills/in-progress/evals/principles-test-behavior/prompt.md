---
name: principles-test-behavior
runs: 3
max_turns: 30
timeout_seconds: 600
allowed_tools: [Skill, Read, Glob, Grep, Bash, Edit, Write]
append_system_prompt: "Non-interactive run: nobody answers questions. Finish the task, then end with a short report as your final message."
---

Next week I move the tax maths in checkout.py into a TaxPolicy class. Are the tests in test_checkout.py good enough to protect that refactor? Fix the ones that are not.
