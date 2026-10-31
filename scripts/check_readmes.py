#!/usr/bin/env python3
"""Checks that each skill and mod folder has a README.md that follows .claude/rules/readme.md."""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_HEADINGS = ["When to use it", "Example", "Install", "What it does", "Limits", "More"]
MOD_HEADINGS = ["Why", "Install", "Example", "What it does", "Settings", "Limits", "More"]
STATUS = {"in-progress": "> In progress: not shipped in any plugin."}
MAX_LINES = 100
MAX_WORDS = 25
MAX_STEP_WORDS = 20
BANNED = re.compile(r"\b(?:simply|just|powerful|seamless)\b|\b(?:e\.g|i\.e)\.|[\U0001F000-\U0001FAFF]|.\uFE0F", re.I)


def folders():
    for d in sorted(ROOT.glob("plugins/*/skills/*/")):
        yield d, SKILL_HEADINGS, None
    for d in sorted(ROOT.glob("lab/*/")):
        if d.name != "evals":
            yield d, SKILL_HEADINGS, "in-progress"
    for d in sorted(ROOT.glob("mods/*/")):
        yield d, MOD_HEADINGS, None


def words(text):
    text = re.sub(r"`[^`]*`", "CODE", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return len(text.split())


def sentences(text):
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def prose(lines):
    """Yields (line number, text, limit) for each piece of prose outside code fences."""
    fenced = False
    for n, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or line.startswith("#") or not line.strip():
            continue
        if line.lstrip().startswith("|"):
            if re.fullmatch(r"\s*\|[\s|:-]*", line):
                continue
            for cell in line.strip().strip("|").split("|"):
                yield n, cell, MAX_WORDS
            continue
        step = re.match(r"\s*\d+\.\s+(.*)", line)
        if step:
            yield n, step.group(1), MAX_STEP_WORDS
        else:
            yield n, line, MAX_WORDS


def banned(lines):
    """Returns (line number, match) for each word or sign that .claude/rules/readme.md forbids."""
    fenced = False
    found = []
    for n, line in enumerate(lines, 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        text = re.sub(r"\]\([^)]*\)", "]", re.sub(r"`[^`]*`", " ", line))
        found += [(n, m.group()) for m in BANNED.finditer(text)]
    return found


def status_line(bucket):
    """The status line a README needs under its title, or None."""
    return STATUS.get(bucket)


def check(folder, headings, bucket):
    rel = folder.relative_to(ROOT)
    readme = folder / "README.md"
    if not readme.is_file():
        return [f"{rel}: no README.md (see .claude/rules/readme.md)"]
    lines = readme.read_text().splitlines()
    path = readme.relative_to(ROOT)
    errors = []
    if not lines or lines[0] != f"# {folder.name}":
        errors.append(f"{path}:1: first line must be '# {folder.name}'")
    status = status_line(bucket)
    if status and status not in lines[:6]:
        errors.append(f"{path}: needs the status line '{status}' under the title")
    found = [line[3:].strip() for line in lines if line.startswith("## ")]
    if found != headings:
        errors.append(f"{path}: ## headings are {found}, expected {headings}")
    if len(lines) > MAX_LINES:
        errors.append(f"{path}: {len(lines)} lines, at most {MAX_LINES}")
    for n, text, limit in prose(lines):
        for s in sentences(text):
            if words(s) > limit:
                errors.append(f"{path}:{n}: {words(s)} words, at most {limit}: {s[:60]}...")
    for n, match in banned(lines):
        errors.append(f"{path}:{n}: banned \"{match}\" (see .claude/rules/readme.md)")
    return errors


def main():
    errors = [e for args in folders() for e in check(*args)]
    print("\n".join(errors) if errors else "readmes ok")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
