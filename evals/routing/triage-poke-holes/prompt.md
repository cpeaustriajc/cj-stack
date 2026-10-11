---
name: triage-poke-holes
runs: 2
max_turns: 3
allowed_tools: [Skill, Read, Glob, Grep]
---

here's my design for offline sync: writes go to IndexedDB first, a service worker replays the queue on reconnect, last write wins by server timestamp. poke holes in it with questions before we build.
