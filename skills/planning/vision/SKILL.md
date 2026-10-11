---
name: vision
description: >
  This skill should be used when the user brings a product idea or vision, asks "is this worth
  building", says "grill me on this idea", "plan the product", "set up the initiative" or "what
  are the features", wants a plan from product down to tickets, wonders whether a personal tool
  could sell, or asks for a product-level update. It grills the idea, worth-it first, then writes
  the top level of the plan and hands each feature to shape.
---

# Vision

The product level of a top-down plan, and the vaguest one, so this skill grills it itself. Read
`../shape/references/top-down.md` first: the five rules, finding the tracker (use its adapter's
Product row), and how writes are made and checked.

## 1. Grill me

Run the interview from `../triage/SKILL.md`, from **Grilling** to **Ending**: the ledger, rounds
of questions with recommended answers, lookups before asking. Skip its sizing; a product idea is
always grilled. An idea handed over from `scout` arrives with its filter scores, which answer
section 2's Real, Reach and copies rows; start the ledger from them and ask only what scored
unknown. What changes at this level:

- **Breadth first.** Round 1 asks one question per branch before going deep on any: who it is
  for, their problem today, whether it is worth it (section 2), the destination, how we'll know it
  worked, the first version's cut, and the riskiest unknown. Going deep early spends the
  interview on a branch that the worth-it answer may cut.
- **The ledger grows the product.** Each settled branch becomes a line of section 3. Show the
  Features list growing each round, numbered F1…Fn.
- **Vague may stay vague.** When I can't answer sharply and no lookup or prototype would settle
  it, put it under Not yet specified and move on. Pressing a vague answer into a feature invents
  one.
- **Make it concrete.** Ask through one person in one moment ("Ana's domain lapses on Friday
  night. What does she do first?"). When words aren't landing, offer a rough sketch, a mock
  headline or a one-screen flow as an option.
- **The riskiest unknown gets a test, not an opinion.** If a lookup, a prototype or a talk with a
  user can settle it, make that the first item of the first project instead of deciding it here.

The interview ends when every branch is settled, out of scope or not yet specified. Post the
ledger as the draft product and ask whether it is right before writing anything.

## 2. Is it worth building, and worth my time?

Settle this first; every later answer depends on it. Look up what you can before asking. Ask who
it is for if that isn't plain, because the questions differ:

| Question | For others | For me alone |
|---|---|---|
| **Real** | Who has the problem, how often, and what they do now. A workaround people pay for or put up with is evidence; "it would be nice" is not. | How often I hit it and the minutes it costs. Five minutes a day is about 30 hours a year: the budget to beat, if time saved is the point. |
| **Already solved** | Existing products, tools or a spreadsheet. Say what this does that they don't, or recommend one. | A tool 80% there with some setup, a script, a spreadsheet: an option to price, not a reason to stop. |
| **Cost** | My weeks to a first usable version, plus running and upkeep. Estimates are mine; label yours as guesses. | Evenings and weekends, plus upkeep when an API or the OS changes. |
| **Reach and copies** | How I reach the people who pay, and what a weekend copy built with an agent can't take: distribution I own, data that accrues per customer, a workflow it sits in, trust, compliance. If a copy with an audience would win, say so. | Not asked. |
| **Displaces** | What else that time would go to; I decide which matters more. | The same. |
| **Returns** | Money, time saved, learning or joy; say which. | Time saved, learning or joy. For learning or joy the time math doesn't apply, but the build gets a timebox ("two weekends") that ends in a keep-going or stop decision. |

Then recommend one verdict, with its reason in a line: **build**; **shrink** (a smaller first
version is worth it, the whole isn't yet); **test first** (one cheap check decides it: a landing
page, five conversations, a prototype); or **don't build**, which ends the interview. Test first
and don't build are good outcomes; say them plainly when the evidence points there.

## 3. Write the product

In the tracker object the adapter names for the Product level:

```markdown
Status: Draft | Confirmed (<date>, <approver>)

## Destination
<Who it is for, the problem it solves, what the product is once it exists, in neutral present
tense: "Buyers find and buy a domain in one visit".>

## Worth it
<The verdict and why, from section 2.>

## Success
<One or two observations or measures that say it worked.>

## Features
F1. <Outcome in one line.> → <project, or "not yet shaped">

## Sequence
<The order features are shaped and built, and what each waits on. Start with the thinnest
version of the whole product that works end to end and answers the riskiest unknown.>

## Not yet specified
- <What is surely coming but can't yet be stated sharply.>

## Out of scope
- <What this product deliberately is not.>
```

- **Features are outcomes**, one line each, not screens or components. Numbers never change; a
  dropped feature is struck through, so projects citing it still resolve.
- **Feature or not yet specified?** The test is whether it can be stated sharply now, not
  whether it is next. A not-yet-specified item is coarser than a feature, and one later answer
  may turn it into several features or none.
- **Confirmed means complete**: Worth it and Out of scope are filled. A test-first verdict makes
  the test the first item of the first project, and the product stays Draft until its result is
  in.

## 4. Hand down, in stages

1. Once the product is Confirmed, create one project per feature in the Sequence's first step,
   linked to the product and holding only the feature's line. Later features wait their turn.
2. Hand the first project to `shape`. The next feature is shaped when the project before it
   reaches Launch, or sooner if I say so, so later features benefit from what the launch taught.
3. **At each Launch, check Worth it again** against what the launch showed and the time it really
   took; for personal software, whether I used it this week. Say in a line whether the verdict
   holds; if not, recommend shrinking or stopping rather than carrying on by momentum.
4. A change to a feature after its project exists returns that project's spec to Draft; say so
   and what it touches.

## 5. From personal to sellable

When something I built for myself might sell, run section 2 again for others. Two things differ
from a fresh idea:

- **I am user one, which is evidence and bias at once.** My weekly use proves it works for one
  person; my liking it proves nothing about anyone else. Ask for evidence from others: who has
  asked for it or a copy, who I could show it to this week, how I would reach more of them.
- **Selling costs what the personal version never paid.** Price it in weeks before the verdict:
  accounts for more than one person, billing, onboarding that works without me, support, privacy
  and security, reliability.

The usual verdict is test first: put it in front of five people with the problem, or offer it
before building the selling parts, and decide on what they do, not what they say. On build,
write a new Draft product for others with product phases; the personal one stays as it is until
the new one replaces it.

## 6. Updates and audits

- **A product update** is one line per project with its own health and phase, then the
  product's health as my call, proposed if the facts don't settle it.
- **An audit** checks Worth it against the latest launch, then the five rules: every feature has
  a project or waits its turn, every project serves a feature, nothing is built under a Draft
  level, and Not yet specified holds nothing that has since sharpened.
