#!/usr/bin/env python3
"""Extract the places where the user corrected Claude from local Claude Code transcripts."""
import argparse, glob, json, os, re, sys
from datetime import datetime

CORRECTION = re.compile(
    r"^\s*(no\b|nope|why\b|stop\b|don'?t\b|do not\b|i already|i said|i meant|that's not|wrong|"
    r"huh|wait\b|actually\b|\?\?)", re.I)
INTERRUPT = "[Request interrupted by user"
PEER = "Another Claude session sent a message"
HOOK = "Stop hook feedback:"
COMMAND = re.compile(r"<command-name>\s*([^<\s]+)\s*</command-name>")
ANSWER = re.compile(r'"="([^"]*)"')
# Keep this detection in step with mods/hone-nudge/hooks/register.ts, which duplicates it.


def skill_name(raw):
    return raw.strip().lstrip("/").split(":")[-1]


def text_of(content):
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


def took_defaults(result):
    answers = ANSWER.findall(result)
    return bool(answers) and all(
        part.strip().endswith("(Recommended)") for a in answers for part in a.split(", "))


def exchanges(path, stats, skill=None):
    """Yield (kind, claude, user); with `skill`, only those made while that skill was the active one."""
    for hit in _exchanges(path, stats, skill):
        if skill is None or hit[0] == skill:
            yield hit[1:]


def _exchanges(path, stats, skill):
    last_claude, asks, active = "", {}, None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                # The live session's last line can be half-written; it's counted, not trusted.
                stats["bad_lines"] += 1
                continue
            if entry.get("isSidechain"):
                continue
            msg = entry.get("message") or {}
            content = msg.get("content")
            if entry.get("type") == "assistant":
                said = text_of(content)
                if said.strip():
                    last_claude = said
                for block in content if isinstance(content, list) else []:
                    if block.get("type") == "tool_use" and block.get("name") == "Skill":
                        named = (block.get("input") or {}).get("skill")
                        if isinstance(named, str):
                            active = skill_name(named)
                    if block.get("type") == "tool_use" and block.get("name") == "AskUserQuestion":
                        asks[block["id"]] = json.dumps(block.get("input", {}))[:1200]
                continue
            if entry.get("type") != "user":
                continue
            started = COMMAND.search(text_of(content))
            if started:
                active = skill_name(started.group(1))
                continue
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict) or block.get("type") != "tool_result":
                    continue
                result = block.get("content")
                result = result if isinstance(result, str) else text_of(result)
                if block.get("tool_use_id") in asks:
                    if not took_defaults(result):
                        yield active, "ASK", asks[block["tool_use_id"]], result[:1200]
                elif "doesn't want to proceed" in result or "rejected" in result[:200].lower():
                    yield active, "REJECTED", last_claude[-600:], result[:600]
            said = text_of(content)
            if not said.strip() or said.startswith(("<", PEER)) or len(said) > 2500:
                continue
            if said.startswith(HOOK):
                yield active, "HOOK", last_claude[-600:], said
            elif INTERRUPT in said:
                yield active, "INTERRUPT", last_claude[-600:], said
            elif CORRECTION.search(said) or "?" in last_claude[-600:]:
                yield active, "REPLY", last_claude[-600:], said
            last_claude = ""


def tool_line(block):
    args = block.get("input") or {}
    arg = args.get("command") or args.get("skill") or args.get("file_path") or args.get("description") or ""
    return f"{block.get('name')} {str(arg)[:120]}".strip()


def turns(path, stats):
    """Yield (user, tools, claude) for every user prompt, corrected or not."""
    user, tools, claude = None, [], ""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                stats["bad_lines"] += 1
                continue
            if entry.get("isSidechain"):
                continue
            content = (entry.get("message") or {}).get("content")
            if entry.get("type") == "assistant":
                said = text_of(content)
                if said.strip():
                    claude = said
                tools += [tool_line(b) for b in content if isinstance(b, dict) and b.get("type") == "tool_use"] \
                    if isinstance(content, list) else []
            elif entry.get("type") == "user":
                said = text_of(content)
                if not said.strip() or said.startswith(PEER):
                    continue
                if user is not None:
                    yield user, tools, claude
                user, tools, claude = said[:1200], [], ""
    if user is not None:
        yield user, tools, claude


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="markdown file to write")
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--project", default="", help="only transcript folders containing this text")
    ap.add_argument("--skill", default="", help="only corrections made while this skill was active (plugin prefix ok)")
    ap.add_argument("--since", default="", help="YYYY-MM-DD; skip files last modified before it")
    ap.add_argument("--turns", action="store_true", help="write every turn with its tool calls, not only corrections")
    ap.add_argument("--chunk-lines", type=int,
                    help="also write <out>.NN.md chunks of about this many lines, cut only between sessions")
    args = ap.parse_args()
    if args.chunk_lines is not None and args.chunk_lines < 1:
        ap.error("--chunk-lines takes a number of lines, 1 or more")
    if args.turns and args.skill:
        ap.error("--turns reads whole sessions; it takes no --skill")

    files = [f for f in glob.glob(os.path.join(args.root, "*", "*.jsonl"))
             if args.project in os.path.basename(os.path.dirname(f)) and "-private-" not in f]
    if args.since:
        cutoff = datetime.strptime(args.since, "%Y-%m-%d").timestamp()
        files = [f for f in files if os.path.getmtime(f) >= cutoff]

    skill = skill_name(args.skill) if args.skill else None
    stats = {"bad_lines": 0, "hits": 0}
    seen = set()
    with open(args.out, "w", encoding="utf-8") as out:
        for i, path in enumerate(files, 1):
            folder = os.path.basename(os.path.dirname(path))[-40:]
            sid = os.path.basename(path)[:-len(".jsonl")][:8]
            if args.turns:
                for user, tools, claude in turns(path, stats):
                    out.write(f"### TURN s={sid} {folder}\nUSER: {user}\nTOOLS: {'; '.join(tools)}\n"
                              f"CLAUDE: {claude[-600:]}\n\n")
                    stats["hits"] += 1
                continue
            for kind, claude, user in exchanges(path, stats, skill):
                if (folder, kind, claude, user) in seen:
                    continue
                seen.add((folder, kind, claude, user))
                out.write(f"### {kind} s={sid} {folder}\nCLAUDE: {claude}\nUSER: {user}\n\n")
                stats["hits"] += 1
            if i % 200 == 0 or i == len(files):
                print(f"[{i}/{len(files)}] files, {stats['hits']} exchanges", flush=True)
    print(f"done: {stats['hits']} exchanges from {len(files)} files -> {args.out}"
          f" ({stats['bad_lines']} unreadable lines skipped)")
    if args.chunk_lines:
        chunk(args.out, args.chunk_lines)


def chunk(path, size):
    """Split the written file into chunks a miner can read whole; a session never spans two chunks."""
    base = path[:-3] if path.endswith(".md") else path
    with open(path, encoding="utf-8") as fh:
        lines = fh.readlines()
    parts, cur, last = [], [], None
    for line in lines:
        m = re.match(r"### \w+ s=(\S+)", line)
        if m and m.group(1) != last and len(cur) >= size:
            parts.append(cur)
            cur = []
        if m:
            last = m.group(1)
        cur.append(line)
    if cur:
        parts.append(cur)
    start = 1
    for i, part in enumerate(parts):
        name = f"{base}.{i:02d}.md"
        with open(name, "w", encoding="utf-8") as out:
            out.writelines(part)
        print(f"chunk {name}: lines {start}-{start + len(part) - 1}")
        start += len(part)


if __name__ == "__main__":
    sys.exit(main())
