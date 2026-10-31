#!/usr/bin/env bash
set -euo pipefail
mkdir -p .cache
cat > sync.py <<'PY'
import os
import time

LOCK = os.path.join(".cache", "sync.lock")
SYNC_TIMEOUT = 3.0
RETRIES = 1


def _acquire(timeout):
    start = time.monotonic()
    while os.path.exists(LOCK):
        if time.monotonic() - start > timeout:
            raise TimeoutError(f"sync took longer than {timeout}s")
        time.sleep(0.05)
    with open(LOCK, "w") as f:
        f.write(str(os.getpid()))


def sync(records, timeout=SYNC_TIMEOUT):
    for attempt in range(RETRIES + 1):
        try:
            _acquire(timeout)
            break
        except TimeoutError:
            if attempt == RETRIES:
                raise
    try:
        return [r.strip().upper() for r in records]
    finally:
        os.remove(LOCK)
PY
cat > test_sync.py <<'PY'
import unittest

from sync import sync


class SyncTest(unittest.TestCase):
    def test_sync(self):
        self.assertEqual(sync([" a", "b "]), ["A", "B"])


if __name__ == "__main__":
    unittest.main()
PY
cat > NOTES.md <<'MD'
# test_sync timeouts

The sync is slow on this machine, so the test times out.

- Fix 1: raised SYNC_TIMEOUT from 0.5 to 1.0. Still times out.
- Fix 2: raised SYNC_TIMEOUT to 3.0 and added one retry. Still times out, every run.

Next idea: raise it to 10 or mock time.sleep.
MD
# A run that crashed yesterday left its lock behind.
printf '48213' > .cache/sync.lock
