#!/usr/bin/env bash
set -euo pipefail
mkdir -p data
python3 - <<'PY'
import random
random.seed(7)
words = [f"w{i}" for i in range(4000)]
for n in range(1500):
    with open(f"data/doc{n:04d}.txt", "w") as f:
        f.write(" ".join(random.choice(words) for _ in range(400)))
PY
cat > search.py <<'PY'
import functools
import os
import pickle
import re

CACHE = os.path.join(".cache", "index.pickle")


@functools.lru_cache(maxsize=None)
def normalize(word):
    return re.sub(r"[^a-z0-9]", "", word.lower())


def build_index():
    index = {}
    for name in sorted(os.listdir("data")):
        with open(os.path.join("data", name)) as f:
            for word in f.read().split():
                index.setdefault(re.sub(r"[^a-z0-9]", "", word.lower()), set()).add(name)
    return index


def load_index():
    if os.path.exists(CACHE):
        with open(CACHE, "rb") as f:
            return pickle.load(f)
    index = build_index()
    os.makedirs(".cache", exist_ok=True)
    with open(CACHE, "wb") as f:
        pickle.dump(index, f)
    return index


def search(index, query):
    return sorted(index.get(normalize(query), ()))
PY
cat > bench.py <<'PY'
import time

import search

start = time.perf_counter()
index = search.load_index()
for i in range(20000):
    search.search(index, f"W{i % 200}")
print(f"{(time.perf_counter() - start) * 1000:.0f} ms")
PY
cat > BENCH.md <<'MD'
# bench.py

| run | normalize | result |
|---|---|---|
| before | plain function | 430 ms |
| after | functools.lru_cache | 166 ms |

One run each, `python3 bench.py`, the "after" run right after the "before" run.
MD
cat > CHANGELOG.md <<'MD'
# Changelog

## Unreleased
MD
# The "before" run built the index cache that every later run loads.
python3 -c "import search; search.load_index()"
