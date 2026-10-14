# Secret hook tests (the judge; implementers never edit this dir)
Run: `python3 ~/.claude/hooks/tests/secret_hooks_test.py [--e2e] [--null] [--jobs 8] [--only CASE_ID...]`
- `--null` swaps in pass-through hooks; any protective fixture that still passes is a mutation survivor (exit 1).
- `--validate-only` checks fixtures (schema, trivial, FAKESECRET marker) without hooks; `--write-manifest` locks fixtures+runner+sandbox.sb in `fixtures.sha256`.
- `--fixtures DIR` / `--hooks-dir DIR` override `tests/fixtures/` and `~/.claude/hooks/`; the manifest and `last-run.log` sit beside the fixtures dir.
- Fixture `files` paths are project-relative, or home-relative with a `~/` prefix; `{PROJECT}`, `{HOME}`, `{REALHOME}` are substituted everywhere.
- pre_exec runs only under macOS `sandbox-exec` (sandbox.sb: writes in the temp dir only, no network); otherwise it is reported failed-unsafe.
- e2e needs `--e2e` and a real `claude`; `SECRET_TEST_CLAUDE` overrides the binary. Log: `tests/last-run.log`.
- `selftest/` holds toy hooks and fixtures that prove the runner: `--fixtures selftest/fixtures --hooks-dir selftest/toy_good`.
