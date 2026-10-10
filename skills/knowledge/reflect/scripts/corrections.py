#!/usr/bin/env python3
"""Extract the places where the user corrected Claude from local Claude Code transcripts."""
import argparse, glob, json, os, re, sys
from datetime import datetime

CORRECTION = re.compile(
    r"^\s*(no\b|nope|why\b|stop\b|don'?t\b|do not\b|i already|i said|i meant|that's not|wrong|"
    r"huh|wait\b|actually\b|\?\?)", re.I)
INTERRUPT = "[Request interrupted by user"


def text_of(content):
    if isinstance(content, str):
        return content
    return "\n".join(b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text")


def exchanges(path, stats):
    last_claude, asks = "", {}
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
                    if block.get("type") == "tool_use" and block.get("name") == "AskUserQuestion":
                        asks[block["id"]] = json.dumps(block.get("input", {}))[:1200]
                continue
            if entry.get("type") != "user":
                continue
            for block in content if isinstance(content, list) else []:
                if not isinstance(block, dict) or block.get("type") != "tool_result":
                    continue
                result = block.get("content")
                result = result if isinstance(result, str) else text_of(result)
                if block.get("tool_use_id") in asks:
                    yield "ASK", asks[block["tool_use_id"]], result[:1200]
                elif "doesn't want to proceed" in result or "rejected" in result[:200].lower():
                    yield "REJECTED", last_claude[-600:], result[:600]
            said = text_of(content)
            if not said.strip() or said.startswith("<") or len(said) > 2500:
                continue
            if INTERRUPT in said:
                yield "INTERRUPT", last_claude[-600:], said
            elif CORRECTION.search(said) or "?" in last_claude[-600:]:
                yield "REPLY", last_claude[-600:], said
            last_claude = ""


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, help="markdown file to write")
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--project", default="", help="only transcript folders containing this text")
    ap.add_argument("--since", default="", help="YYYY-MM-DD; skip files last modified before it")
    args = ap.parse_args()

    files = [f for f in glob.glob(os.path.join(args.root, "*", "*.jsonl"))
             if args.project in os.path.basename(os.path.dirname(f)) and "-private-" not in f]
    if args.since:
        cutoff = datetime.strptime(args.since, "%Y-%m-%d").timestamp()
        files = [f for f in files if os.path.getmtime(f) >= cutoff]

    stats = {"bad_lines": 0, "hits": 0}
    with open(args.out, "w", encoding="utf-8") as out:
        for i, path in enumerate(files, 1):
            for kind, claude, user in exchanges(path, stats):
                folder = os.path.basename(os.path.dirname(path))[-40:]
                out.write(f"### {kind} {folder}\nCLAUDE: {claude}\nUSER: {user}\n\n")
                stats["hits"] += 1
            if i % 200 == 0 or i == len(files):
                print(f"[{i}/{len(files)}] files, {stats['hits']} exchanges", flush=True)
    print(f"done: {stats['hits']} exchanges from {len(files)} files -> {args.out}"
          f" ({stats['bad_lines']} unreadable lines skipped)")


if __name__ == "__main__":
    sys.exit(main())
