---
name: ui-polish-toast-transition
runs: 2
max_turns: 12
allowed_tools: [Skill, Read, Glob, Grep]
append_system_prompt: "Non-interactive run: nobody answers questions and no browser is available; judge from the code."
---

/cj-stack:ui-polish review the motion on the new toasts in toast.css and toast.js before I sign off. Toasts get fired several at once when a sync finishes, so they often interrupt each other mid-animation. You can swipe one away.
