#!/usr/bin/env bash
set -euo pipefail
git init -q -b main . && git config user.email e@x && git config user.name e
mkdir -p runner tests
cat > runner/store.py <<'EOF'
"""A key-value store shared by all workers. Each call is one round trip."""


class Store:
    def __init__(self):
        self._rows = {}

    def get(self, key):
        return self._rows.get(key)

    def put(self, key, value):
        self._rows[key] = value
EOF
cat > runner/lease.py <<'EOF'
"""A worker runs a job only while it holds the job's lease."""

LEASE_SECONDS = 30


def try_acquire(store, job_id, worker, now):
    """Take the lease if nobody holds it or the holder's lease timed out."""
    row = store.get(f"lease:{job_id}")
    if row is not None and row["expires"] > now and row["holder"] != worker:
        return False
    store.put(f"lease:{job_id}", {"holder": worker, "expires": now + LEASE_SECONDS})
    return True


def renew(store, job_id, worker, now):
    row = store.get(f"lease:{job_id}")
    if row is None or row["holder"] != worker:
        return False
    store.put(f"lease:{job_id}", {"holder": worker, "expires": now + LEASE_SECONDS})
    return True


def release(store, job_id, worker):
    row = store.get(f"lease:{job_id}")
    if row is not None and row["holder"] == worker:
        store.put(f"lease:{job_id}", None)
EOF
cat > runner/worker.py <<'EOF'
"""Each worker polls for jobs and runs one only while it holds the lease."""
from runner import lease


def run_once(store, job_id, worker, now, side_effect):
    if not lease.try_acquire(store, job_id, worker, now):
        return False
    side_effect(job_id, worker)  # charges the customer
    lease.release(store, job_id, worker)
    return True
EOF
touch runner/__init__.py tests/__init__.py
cat > tests/test_lease.py <<'EOF'
import unittest

from runner import lease
from runner.store import Store


class LeaseTest(unittest.TestCase):
    def test_first_worker_takes_the_lease(self):
        s = Store()
        self.assertTrue(lease.try_acquire(s, "j1", "a", now=0))
        self.assertFalse(lease.try_acquire(s, "j1", "b", now=1))

    def test_lease_times_out(self):
        s = Store()
        lease.try_acquire(s, "j1", "a", now=0)
        self.assertTrue(lease.try_acquire(s, "j1", "b", now=31))

    def test_holder_can_renew(self):
        s = Store()
        lease.try_acquire(s, "j1", "a", now=0)
        self.assertTrue(lease.renew(s, "j1", "a", now=20))
        self.assertFalse(lease.try_acquire(s, "j1", "b", now=31))

    def test_release_frees_the_lease(self):
        s = Store()
        lease.try_acquire(s, "j1", "a", now=0)
        lease.release(s, "j1", "a")
        self.assertTrue(lease.try_acquire(s, "j1", "b", now=1))


if __name__ == "__main__":
    unittest.main()
EOF
printf '__pycache__/\n' > .gitignore
git add . && git commit -q -m "runner: job leases with timeout and renew"
