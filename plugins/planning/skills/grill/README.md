# grill

A skill that sizes a change, then interviews you in short rounds of questions. Each question has a recommended answer. It stops when no decision is open.

## When to use it

Use it before you build, when a design or change has decisions nobody made yet. Claude looks up facts itself and asks you only what is yours to decide.

- You say "grill me", "ask me questions first" or "stress-test this".
- You say "poke holes in this" or "plan and ask me".
- A change touches 3 or more files, has several approaches or has unclear scope.

Do not use it for a whole product idea or for "is this worth building?": use `vision`. Do not use it to write a spec: use `shape`. Do not use it to cut tickets: use `tickets`.

## Example

You say: "Grill me on this: users say the search is 'weird' on mobile."

1. Claude looks up the code and names a tier in one line: trivial, small or grill.
2. Claude posts a short ledger of what is settled and what it assumed.
3. Claude asks one form of up to four questions, each with a recommended first option.
4. Claude repeats rounds until no decision is open, then posts the final ledger.

You get a list of every decision with a one-line reason. Claude then offers a next step and waits for your pick.

## Install

The `planning` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install planning@cj-stack
```

To turn the plugin off, run `claude plugin disable planning@cj-stack`. This also turns off every other skill in `planning`. For other agents such as Codex, run `scripts/link-skills.sh` in the repo.

## What it does

- A trivial change gets one line with Claude's plan and the question "go?". A small change gets one question. Only a grill runs rounds. You can change the tier.
- Claude looks up code, specs, the tracker and docs before it asks you a fact. When a recommendation depends on a fact, Claude runs a small probe first.
- Each round opens with a ledger: Settled, Assumed, Out of scope and the count of open decisions. You can veto any Assumed or Out of scope item, and each cut has a reason that Claude checked.
- Claude asks through the `AskUserQuestion` form, with a concrete scenario in each question.
- A flow, a state change or a structure comes as a diagram: an inline widget where the visualize tools exist, else a mermaid block.
- Round 1 settles what "done" looks like as something you can observe.
- Claude never re-asks a Settled item. If new evidence conflicts with one, it asks about that conflict only.
- Claude recommends the smallest version that ships.

## Limits

- It writes no code, no tracker item and no document. The interview only produces the ledger.
- It does not decide for you. When you say "up to you", Claude logs its recommendation under Assumed.
- If you dismiss a form, Claude stops and follows what you type next.
- It has no settings.

## More

- [SKILL.md](SKILL.md): the method Claude follows.
- [references/claude-code.md](references/claude-code.md): the Claude Code tools for the form and the diagrams.
- [evals/triggers.json](evals/triggers.json): example requests that should and should not load the skill.
