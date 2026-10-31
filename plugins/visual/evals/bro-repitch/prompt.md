---
name: bro-repitch
runs: 2
max_turns: 15
timeout_seconds: 300
allowed_tools: [Skill, Read, Glob, Grep]
append_system_prompt: "Non-interactive run: nobody answers questions."
---

/visual:bro Fixed. Root cause was chain lapses: `passToNext` stamps `ready_at` while the copy is still in transit, so by the time the van lands the window's already burned and the sweep lapses it, re-passes, repeat down the queue. Added a transit skip in `sweep()` (`copy.state === 'transit'` → continue). Caveat: `ready_at` is still stale on arrival, so the first post-arrival sweep can still lapse it. Want me to re-stamp in `arrive()` too, or leave it for the window-from-arrival ticket?
