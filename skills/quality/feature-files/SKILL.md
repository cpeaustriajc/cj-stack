---
name: feature-files
description: >
  This skill should be used when writing or updating a feature file, when an E2E check needs to
  know how to reach and drive an area of the app, when verifying a change in the running app, when
  break-it needs a starting point, and when a UI change makes a feature file wrong. It keeps one
  short file per feature: what exists, how to reach it, how to drive and check it. Not for writing
  the test code itself.
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
**Code**: `src/checkout/`, `api/orders.ts`, `components/Cart*`.
**Tests**: `e2e/checkout.spec.ts`, `src/checkout/*.test.ts`.
**Check**: the exact command or steps that prove it works, and what to capture as evidence.
**Paths to cover**: success, cancel, payment declined, empty cart, reload mid-payment, back
after paying.
**What tends to break**: cart lost after login redirect; double charge on double click.
```

**Code** and **Tests** let a diff find its feature: a changed path maps to the file, which lists
its Tests and Check. Keep it under about 40 lines. Describe behaviour a user can see, not
implementation. Each step pairs an action with a user-visible end state, such as reopening the
saved item; a toast alone is not proof. Put no
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
