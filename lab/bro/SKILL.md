---
name: bro
description: "This skill should be used when the user types /bro. Stop. That last message did not land: re-pitch it. Restate the last message in plain human language, with no jargon, the context the user was missing first, and one picture."
disable-model-invocation: true
argument-hint: "[the text to re-pitch, if it is not your last message]"
---

# Bro

Wait, I don't understand where you've got to here. Re-pitch that: give me a little bit of context, talk in ASD-STE100 Simplified Technical English, and use the ubiquitous language from `GLOSSARY.md` (follow `GLOSSARY-MAP.md` to the right one if the repo has more than one).

Restate your last message. Stop using jargon and speak coherently, like one human talking to another. Simpler is the goal, not shorter: the user did not get it because something was missing, and a shorter message hides it more.

Tool mechanics (the picture, read-only tools) are in `references/claude-code.md`.

## Which message

- Re-pitch your last message before `/bro`. If `$ARGUMENTS` holds text, re-pitch that text instead.
- If your last message was itself a `/bro` re-pitch, it did not land either. Re-pitch the same original message again from a new angle: find the premise the first re-pitch still assumed, and use a different picture.

## Find what was missing

Before you write, name to yourself the premises the message took for granted:

- a term it used and never defined;
- a step it skipped, or a cause it never stated;
- a state the user did not see: a file, an error, a test result, a decision from earlier;
- why the message mattered, and what it asked the user to do.

Check each fact against the code or the chat. Read files only; change nothing.

## The project's words

Find the project's own terms, in this order: `GLOSSARY.md` (or the one `GLOSSARY-MAP.md` points to), the terms in `CLAUDE.md` or `AGENTS.md`, then the names in the code. Use each term as the project uses it, and define it at its first use. Never invent a new label for a thing that already has a name.

## Write the re-pitch

1. **Context first.** Open with the missing premises, in two to four sentences. Say what the thing is and how it worked before, then what went wrong.
2. **The point.** Then restate what the message said: what changed or what is true now, and why.
3. **One picture.** Draw the one part that is easiest to grasp as a picture: how the parts connect, the order of the steps, or a before and after. Draw boxes joined by lines: at most six boxes, with at most eight words in each. A list, a table or two columns of text is not a picture. Use the inline diagram tool; where there is none, draw a mermaid flowchart (`references/claude-code.md`).
4. **The ask.** If the original message asked something of the user, end with that question again, in one plain sentence, with your recommendation. Add no new asks and no new findings: a re-pitch says the same message.

Write in ASD-STE100:

- Full sentences, each with a subject and a verb. Keep the articles ("the", "a"). No fragments, no note style, no arrows in place of verbs.
- One idea per sentence: at most 20 words for an instruction, at most 25 for a description.
- Active voice, present tense, common words.
- Leave out hashes, flags, line numbers and tool names unless the user needs one to act.

Every `/bro` keeps these rules. A second or third re-pitch is as full as the first, never a shorter summary of it.

## Credit

Follows Matt Pocock's `wait-what` (MIT; see `LICENSE-wait-what`), whose words open this skill. Also adapted from pstack's `bro` by Lauren Tan (MIT; see `LICENSE`), without its ask for shorter output.
