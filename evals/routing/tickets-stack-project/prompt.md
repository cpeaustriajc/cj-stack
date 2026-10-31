---
name: tickets-stack-project
runs: 2
max_turns: 4
allowed_tools: [Skill, Read, Glob, Grep]
append_system_prompt: "Non-interactive run: nobody answers questions and no tracker is connected. Write nothing to a tracker. End with the full proposed list of items as your final message."
---

the order status spec in our Linear project is confirmed, break it into tickets. one ticket per status: R1 the order page shows "Placed" right after checkout, R2 it shows "Paid" once the payment clears, R3 it shows "Packed" when the warehouse scans the box, R4 it shows "Shipped" with a tracking link, R5 it shows "Delivered" with the delivery date. each status sits on the timeline the one before it adds. agents will build these as separate PRs.
