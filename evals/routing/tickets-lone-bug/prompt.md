---
name: tickets-lone-bug
runs: 2
max_turns: 4
allowed_tools: [Skill, Read, Glob, Grep]
append_system_prompt: "Non-interactive run: nobody answers questions and no tracker is connected. Write nothing to a tracker. End with the full proposed item as your final message."
---

write the issue for this one, it goes straight into the team backlog, not into any project: the footer "Contact us" link points to /contakt and 404s. an agent will fix it in its own PR. we're also in the middle of building the order status project, five stacked PRs, but this has nothing to do with that.
