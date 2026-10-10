---
name: feature-files
description: Keep one short file per user-facing feature that says what exists, how a user reaches it, how to drive and check it, and what tends to break, so end-to-end checks read only the file for the area being changed. Use when verifying a change in the running app, when writing or running an E2E check, when break-it needs a starting point, and when a UI change makes an existing feature file wrong.
---

# Feature files

An agent verifying a change shouldn't have to rediscover the app each time, and it shouldn't
read a whole test corpus either. Each feature gets one small file. A check opens the file for
the area it touches and nothing else.

## Where they live

Use the folder the project already has. If it has none, propose `docs/features/` in one line
and wait for a yes. There is one file per feature, named after what a user calls it, such as
`checkout.md` or `domain-search.md`, not after the code. An `index.md` lists them in a
one-line-each table.

## What one file holds

```markdown
# Checkout

**What exists**: cart, guest and signed-in checkout, test-mode card payment, receipt page.
**How a user gets there**: search → domain card → "Buy" → /cart → "Checkout".
**How to drive it**: test account from the project's test setup; test card 4242…; start URL.
**Check**: the exact command or steps that prove it works, and what to capture as evidence.
**Paths to cover**: success, cancel, payment declined, empty cart, reload mid-payment, back
after paying.
**What tends to break**: cart lost after login redirect; double charge on double click.
```

Keep it under about 40 lines. Describe behaviour a user can see, not implementation. Put no
dates, statuses, ticket numbers or "fixed in…" notes in it: those go stale. They belong in the
tracker and git history.

Feature files say *what* to check. Launching the app stays with the built-in `run` skill or the
project's launch skill. Don't copy launch steps into them.

## Using them

1. Find the files for the areas the change touches, usually 1-2. Read only those.
2. Run the **Check** in the real app and the **Paths to cover** that the change could affect.
   Save the evidence (screenshots, trace or video) and say where it is, plus the command to run
   it again.
3. If the app no longer matches the file, fix the file in the same change. A wrong feature
   file is worse than none.
4. When a bug turns up that the file didn't predict, add one line to **What tends to break**.

To start the set, don't document the whole app. Write a file for each feature the next change
touches, and let the set grow from there.
