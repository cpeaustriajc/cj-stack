---
name: playbooks-design-two-sketches
runs: 2
max_turns: 6
allowed_tools: [Skill, Read, Glob, Grep]
---

we need to add Adyen as a second payment provider next to Stripe. today the Stripe SDK is called directly from checkout/submit.ts, billing/refund.ts and admin/reconcile.ts. the repo isn't here, so don't write code yet. how would you approach the design before building it? give me the steps.
