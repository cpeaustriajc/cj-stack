---
name: vision
description: >
  Turn a product idea into the top level of the plan in the team's tracker: the destination, the
  features that become projects, what is not yet specified and what is out of scope, ordered so
  the riskiest unknown is built first. Then hand each feature to `shape`, one at a time. Use when I
  bring a product idea or a vision, say "plan the product", "set up the initiative", "what are the
  features", or ask for a product plan from features down to tickets; and for a product-level
  status update or audit.
---

# Vision

The top of three levels: `vision` for the product, `shape` for each project, `tickets` for each
slice. Read the five top-down rules in `../shape/SKILL.md` first; they hold here too. The tracker
adapters live there as well: find the tracker as its section 1 says, and use the adapter's
**Product** row and its status-update row for a product update.

## 1. Settle it first

Run `triage` on the idea until the destination, the people it is for, the first version's cut and
the features are settled. This skill records those decisions; it makes none.

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
