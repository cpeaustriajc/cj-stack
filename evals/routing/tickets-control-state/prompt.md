---
name: tickets-control-state
runs: 2
max_turns: 4
allowed_tools: [Skill, Read, Glob, Grep]
append_system_prompt: "Non-interactive run: nobody answers questions and no tracker is connected. Write nothing to a tracker. End with the full proposed item as your final message."
---

write the issue for this: the devtools QA panel gets a "Reset my trial" button that puts the signed-in tester's test account back to day 1 of its trial. it only acts on test accounts. signed in with a real customer account the panel offers nothing, same as the other QA buttons already do. straight into the backlog, an agent builds it in its own PR.
