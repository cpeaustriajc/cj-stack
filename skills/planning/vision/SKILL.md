---
name: vision
description: >
  Grill me on a vague product idea until it is sharp, then write it as the top level of the plan
  in the team's tracker: the destination, the features that become projects, what is not yet
  specified and what is out of scope, ordered so the riskiest unknown is built first. Then hand
  each feature to `shape`, one at a time. Use when I bring a product idea or a vision, say "grill
  me on this idea", "plan the product", "set up the initiative" or "what are the features", or ask
  for a product plan from features down to tickets; and for a product-level status update or
  audit.
---

# Vision

The top of three levels: `vision` for the product, `shape` for each project, `tickets` for each
slice. Read the five top-down rules in `../shape/SKILL.md` first; they hold here too. The tracker
adapters live there as well: find the tracker as its section 1 says, and use the adapter's
**Product** row and its status-update row for a product update.

## 1. Grill me

A product idea is the vaguest thing in the plan, so this skill does the grilling itself. Run the
interview from `../triage/SKILL.md`, from **Grilling** to **Ending**: the ledger, the rounds, the
recommended answers, the lookups. Skip its sizing: a product idea is always grilled. What changes
at this level:

- **Breadth first.** Round 1 fans out across the whole idea, one question per branch, before going
  deep on any: who it is for, their problem today, the destination, how we will know it worked,
  the first version's cut, and the riskiest unknown. Deep questions wait until every branch has a
  first answer.
- **The tree is the product.** Every settled branch becomes a line in section 2: a feature, a
  Success measure, an Out of scope item or the Sequence. Show the Features list growing in the
  ledger each round, numbered F1…Fn.
- **Vague is allowed to stay vague.** When I can't answer sharply and no lookup or prototype
  would settle it, don't press: put it under Not yet specified, say so in the ledger, and move on.
  Pressing a vague answer into a feature invents one.
- **Make it concrete to sharpen it.** Ask through one specific person in one specific moment ("Ana
  runs a small shop and her domain lapses on Friday night. What does she do first?"). Offer a
  rough sketch, a mock landing page headline or a one-screen flow, as an option when words are
  not landing.
- **Kill early.** If the answers show the problem is not real, already solved, or not worth the
  build, say so with the evidence and recommend stopping. That is a good outcome.
- **The riskiest unknown gets a test, not an opinion.** If it can be settled by a lookup, a
  prototype or talking to a user, name that as the first item of the first project rather than
  deciding it in the interview.

The interview ends when the frontier is empty: every branch is settled, out of scope, or under
Not yet specified. Then post the ledger as the draft product and ask whether it is right before
writing anything.

## 2. Write the product

The product's description, in the tracker object the adapter names for the Product level:

```markdown
Status: Draft | Confirmed (<date>, <approver>)

## Destination

<Who it is for, the problem it solves for them, and what the product is once it exists. Neutral
present tense: "Buyers find and buy a domain in one visit".>

## Success

<One or two observations or measures that say it worked.>

## Features

F1. <Outcome in one line.> → <project, or "not yet shaped">
F2. ...

## Sequence

<The order the features are shaped and built, and what each waits on. Start with the thinnest
version of the whole product that works end to end and answers the riskiest unknown.>

## Not yet specified

- <What is surely coming but cannot yet be stated as a feature. Coarser than a feature; no
  project until it sharpens.>

## Out of scope

- <What this product deliberately is not.>
```

- **Features are outcomes**, one line each, never a list of screens or components. Number them
  once; a dropped feature is struck through, so projects that cite it still resolve.
- **Fog or feature?** A feature you can state sharply now gets an F number, even if it waits. One
  you cannot yet phrase sharply goes under Not yet specified, and one later answer may turn it into
  several features or none.
- **An unknown that a prototype can settle** becomes a prototype item in the first project's Demo
  phase, not a question for me.
- **Out of scope is never empty** on a Confirmed product.

## 3. Hand down, in stages

1. Once the product is Confirmed, create one project per feature in the Sequence's first step,
   linked to the product, holding only the feature's line. Later features stay in the Features
   list until their turn.
2. Hand the first project to `shape`. The next feature is shaped when the project before it
   reaches Launch, or sooner if I say so.
3. A change to a feature after its project exists returns that project's spec to Draft; say so in
   one line and tell me what it touches.

## 4. Product updates and audits

- **A product update** is one line per project, with the project's own health and its phase,
  then the product's health as my judgement, proposed if the facts don't settle it. Read each
  project's latest update; never retype a project's progress by hand.
- **An audit** checks the product against the five rules: every feature has a project or is
  deferred, every project serves a feature, nothing is built under a Draft level, and Not yet
  specified holds nothing that has since sharpened.

## 5. Writing to the tracker and checking the tree

Writing follows section 7 of `../shape/SKILL.md`: state each write before making it, show the
first one, read it back. Then read the tree back into the outline in
`../shape/references/tree-outline.md` and run `python3 ../shape/scripts/check_tree.py
<outline.json>` from this skill's folder. Fix every line it prints before handing back.
