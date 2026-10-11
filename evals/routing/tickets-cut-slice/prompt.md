---
name: tickets-cut-slice
runs: 2
max_turns: 3
allowed_tools: [Skill, Read, Glob, Grep]
---

break the confirmed alerts spec into tickets. requirements: R1 an alert fires on an exact name match, R2 a daily digest email, R3 every alert has an unsubscribe link.
