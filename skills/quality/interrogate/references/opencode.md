# OpenCode adapter

- List what's reachable: `opencode models`. Ids look like `<provider>/<model>`. Pick one model
  per vendor: for example the newest GPT, Gemini and Grok the account can run.
- Probe before use: `opencode run -m <id> --agent plan "reply OK"`. Errors such as "subscription
  is required" or "Reconnect OpenCode Console" mean that provider is unavailable. Tell me the
  fix (`opencode auth login`) and move on to the next model.
- Run a review from the repo root, attaching the bundle:
  `opencode run -m <id> --agent review -f <bundle.md> "<review prompt>" > <id-slug>.md`
- Never use `plan`: in `opencode run` it executed shell commands without asking. Use a `review`
  agent defined in `opencode.jsonc` with `edit` and `webfetch` set to `deny`, and `bash` set
  to `deny` except read-only commands (`git diff/log/show/status`, `cat`, `ls`, `grep`, `rg`).
  If no such agent exists, add it first. Never pass `--auto`.
- Run reviewers in parallel as background commands. Each prints its own output file.
- Pay-per-use providers bill by tokens. A bundle over about 100k tokens is too big; split it
  by area.
