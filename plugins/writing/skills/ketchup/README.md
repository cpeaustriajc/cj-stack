# ketchup

A typed `/ketchup` command that catches you up on a chat after you step away. It tells you what changed since your last message and what waits on you.

## When to use it

Use it when you come back to a long session and the state is spread over many messages, agent reports and pull requests.

- For a one-line status of this session, run the built-in `/recap` command. Claude Code also shows one on its own when the terminal is unfocused for 3 minutes and the session has 3 or more turns.
- For the work of past sessions in this project, use `recall`.
- For why code has its shape, use `why`.

## Example

You type `/ketchup` after a session where you asked for two fixes and Claude waits on one decision.

1. Claude reads the chat after your last message, the agent reports and each pull request's state.
2. Claude checks each number against its source.
3. Claude writes one short reply and changes nothing.

You get one sentence that says one thing needs you, then a small diagram and one line for each fix with its state. Last comes the decision, with a recommendation and what happens if you do not answer.

## Install

The `writing` plugin ships this skill. Add the marketplace, then install the plugin:

```
/plugin marketplace add cpeaustriajc/dotfiles
/plugin install writing@dotfiles
```

The skill then loads as `/writing:ketchup`.

## What it does

- Reads the chat, the agents this chat started, and the pull requests and checks it touched.
- Writes no file, runs no build or test, starts no agent and posts nothing.
- Keeps the text well under 150 words, apart from the pictures.
- Shows the diagrams in the desktop app. A click on a box asks about that part. In a terminal, it prints a mermaid flowchart.
- Says so in one line and stops when nothing changed and nothing waits on you.

## Limits

- It shows only screenshots and videos that the work already saved. It does not take new ones.
- It does not do the open work. It names the work that Claude can still do.

## More

- [SKILL.md](SKILL.md): the method and the reply layout.
- [references/claude-code.md](references/claude-code.md): the read-only tools and the diagrams.
- [LICENSE](LICENSE): adapted from pstack by Lauren Tan, under the MIT licence.
