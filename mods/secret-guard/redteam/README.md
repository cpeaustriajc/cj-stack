# redteam
Runs real `claude -p` sessions (sandboxed, shimmed ssh/docker/curl/..., planted random secrets) and flags any secret reaching the model.
- `python3 redteam.py --attacks sample-attacks.json --null --jobs 4` : no hooks; every attack must LEAK (else INEFFECTIVE/NO-OP, exit 1).
- `python3 redteam.py --attacks FILE.json [--hooks-dir D] [--jobs N]` : hooks on; exit 1 on any LEAK.
- Attack: `{id, prompt, setup:{files:{rel:content}}, allowed_tools}`; placeholders `{{GH}} {{AWS}} {{AWSSECRET}} {{STRIPE}} {{ANTHROPIC}} {{DBPASS}} {{PEM}} {{JWT}} {{DOKPLOY_ENV}}`.
- Flags: `--keep` keep temp worlds, `--dump-responses` store tool_response text in results.
- Output: stdout + `last-run.log`, `results-<n>.json`. Detection forms come from `../tests/secret_hooks_test.py` (`forms`). Hooks default to `../hooks` and are copied into each temp world; `REDTEAM_MODEL` picks the child model.
- `sample-attacks.json` has 3 attacks plus a `sandbox-probe` (expected INEFFECTIVE: shows ~/.ssh and network blocked).
