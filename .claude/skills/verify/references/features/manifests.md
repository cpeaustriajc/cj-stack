# Manifests and READMEs

What exists: `.claude-plugin/marketplace.json`, each plugin's `plugin.json`, the root README's
tables, and a README per skill and mod.

- **Code:** `**/.claude-plugin/**`, `README.md`, `**/README.md`, `scripts/check_readmes.py`,
  `scripts/test_check_readmes.py`
- **Tests:** `python3 -I scripts/check_readmes.py` prints `readmes ok`;
  `python3 -I scripts/test_check_readmes.py` prints `OK`.
- **Check:** `claude plugin validate .` exits 0; each changed `plugin.json` parses with
  `python3 -c 'import json,sys; json.load(open(sys.argv[1]))' <file>`.
