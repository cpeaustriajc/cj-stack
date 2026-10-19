#!/usr/bin/env python3
"""Check that a change holds moves only: every declaration that left a file arrived in another.

Usage, from inside the repo:
  python3 -I moves_only.py BASE HEAD   compare two commits
  python3 -I moves_only.py BASE        compare BASE with the staged index

Each file splits into top-level blocks: a line that starts at column 0 opens a block, and the
indented lines under it belong to it. A decorator or comment at column 0 opens no block of its
own: it belongs to the declaration that follows it. Blocks must match exactly, in any file and
any order. Top-level import statements, re-export lists, blank lines and a leading `export` or
`export default` on a top-level line are ignored: a move forces them. Any other added, removed,
reordered or reindented line inside a block is a logic edit, and so is code after an import's
`;` on the same line. Exit 0: moves only. Exit 1: logic edits, each printed. Exit 2: bad input or
nothing to check.
"""
import re
import subprocess
import sys
from collections import Counter

JS = (".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts")
JS_IMPORT = re.compile(r"""^import(\s+|(?=[{"']))(type\s+)?[\w{*"']""")
JS_EXPORT_LIST = re.compile(r"^export\s+(type\s+)?(\{|\*)")
JS_FROM = re.compile(r"""\bfrom\s*["']""")
JS_FROM_LINE = re.compile(r"""^from\s*["']""")
JS_SIDE_EFFECT = re.compile(r"""^import\s*["']""")
JS_END = re.compile(r"""\bfrom\s*(["'])[^"']*\1\s*;?|^import\s*(["'])[^"']*\2\s*;?""")
JS_LIST_END = re.compile(r"\}\s*;?")
PY_IMPORT = re.compile(r"^(from\s+\S+\s+import\b|import\s+\w)")
EXPORT_PREFIX = re.compile(r"^export\s+(default\s+)?")


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, errors="replace")


def js_body(lines):
    body, in_stmt, is_list, lines = [], False, False, list(lines)
    for i, raw in enumerate(lines):
        line = raw.strip()
        if not in_stmt and (JS_IMPORT.match(line) or JS_EXPORT_LIST.match(line)):
            in_stmt, is_list = True, bool(JS_EXPORT_LIST.match(line))
        if not in_stmt:
            body.append(EXPORT_PREFIX.sub("", raw.rstrip()))
            continue
        end = None
        if JS_FROM.search(line) or JS_SIDE_EFFECT.match(line):
            in_stmt, end = False, JS_END.search(line)
        elif "}" in line and is_list:
            following = next((l.strip() for l in lines[i + 1:] if l.strip()), "")
            in_stmt = bool(JS_FROM_LINE.match(following))
            end = None if in_stmt else JS_LIST_END.search(line)
        elif line.endswith(";") and "{" not in line and "}" not in line:
            in_stmt = False
        if end and line[end.end():].strip():
            lines.insert(i + 1, line[end.end():].strip())
    return body


def py_body(lines):
    body, open_paren, cont, lines = [], False, False, list(lines)
    for i, raw in enumerate(lines):
        line = raw.strip()
        if open_paren or cont or PY_IMPORT.match(raw):
            line, _, rest = line.partition(";")
            open_paren = (open_paren or "(" in line) and ")" not in line
            cont = line.endswith("\\")
            if rest.strip():
                lines.insert(i + 1, rest.strip())
            continue
        body.append(raw.rstrip())
    return body


def body(path, text):
    lines = text.splitlines()
    if path.endswith(JS):
        kept, leads = js_body(lines), ("@", "//", "/*")
    elif path.endswith(".py"):
        kept, leads = py_body(lines), ("@", "#")
    else:
        kept, leads = [line.rstrip() for line in lines], ()
    blocks, block, lead = [], None, []
    for line in kept:
        if not line.strip():
            continue
        top = not line[0].isspace() and line[0] not in "})]"
        if (top and line.startswith(leads)) or (lead and not top):
            lead.append(line)
        elif block is None or top:
            block = lead + [line]
            blocks.append(block)
            lead = []
        else:
            block.append(line)
    if lead:
        blocks.append(lead)
    return Counter(tuple(b) for b in blocks)


def content(rev, path):
    shown = git("show", f"{rev}:{path}")
    return shown.stdout if shown.returncode == 0 else ""


def main(argv):
    if len(argv) not in (1, 2):
        print(__doc__.strip())
        return 2
    base, head = argv[0], (argv[1] if len(argv) == 2 else None)
    for ref in [r for r in (base, head) if r]:
        if git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}").returncode != 0:
            print(f"unknown ref: {ref}")
            return 2
    names = git("diff", "-z", "--name-only", "--no-renames", base, head) if head else \
        git("diff", "-z", "--cached", "--name-only", "--no-renames", base)
    if names.returncode != 0:
        print(f"git diff failed: {names.stderr.strip()}")
        return 2
    paths = [p for p in names.stdout.split("\0") if p]
    if not paths:
        print(f"nothing to check: no change between {base} and {head or 'the staged index'}")
        return 2
    old, new = {}, {}
    for path in paths:
        old[path] = body(path, content(base, path))
        new[path] = body(path, content(head or "", path))
    total_old = sum(old.values(), Counter())
    total_new = sum(new.values(), Counter())
    problems = []
    for sign, extra, side, other in (("+", total_new - total_old, new, old),
                                     ("-", total_old - total_new, old, new)):
        for block, count in sorted(extra.items()):
            where = [p for p in paths if side[p][block] > other[p][block]]
            size = f"  ({len(block)} lines)" if len(block) > 1 else ""
            times = f"  (x{count})" if count > 1 else ""
            problems.append(f"{sign} {', '.join(where)}: {block[0].strip()}{size}{times}")
    if problems:
        print(f"logic edits: {len(problems)} block(s) did not move unchanged")
        print("\n".join(problems))
        return 1
    moved = sum(len(b) * n for p in paths for b, n in (old[p] - new[p]).items())
    print(f"moves only: {len(paths)} file(s), {moved} line(s) moved")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
