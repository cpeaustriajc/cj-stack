#!/usr/bin/env python3
"""Stream filter: redact stdin to stdout with the shared secret engine."""
import os
import re
import select
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

IDLE = 0.3
TOTAL_CAP = 8 * 1024 * 1024
CHUNK_CAP = 4 * 1024 * 1024
OPEN_PEM = re.compile(r"-----BEGIN[ \t]+(?:[A-Z0-9]+[ \t]+)*?PRIVATE[ \t]+KEY")
END_PEM = re.compile(r"-----END[ \t]+(?:[A-Z0-9]+[ \t]+)*?PRIVATE[ \t]+KEY")


def write(b):
    view = memoryview(b)
    while view:
        try:
            n = os.write(1, view)
        except BrokenPipeError:
            os._exit(0)
        view = view[n:]


def split_safe(text, final):
    """Return (emit, hold): hold keeps an unterminated line or an open private key block."""
    if final:
        return text, ""
    cut = text.rfind("\n") + 1
    head, tail = text[:cut], text[cut:]
    begins = [m.start() for m in OPEN_PEM.finditer(head)]
    if begins and not END_PEM.search(head, begins[-1]):
        return head[:begins[-1]], head[begins[-1]:] + tail
    return head, tail


def main():
    import secret_engine as eng
    engine = eng.Engine(os.getcwd())
    ctx = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0
    fd = sys.stdin.fileno()
    buf = b""
    pending = ""
    total = 0
    spent = 0.0
    dead = None
    while True:
        r, _, _ = select.select([fd], [], [], IDLE)
        final = False
        if r:
            chunk = os.read(fd, 1 << 20)
            if not chunk:
                final = True
            else:
                total += len(chunk)
                if dead is None and total > TOTAL_CAP:
                    dead = "oversized"
                    write((eng.WITHHELD % dead + "\n").encode())
                if dead:
                    continue
                buf += chunk
                if len(buf) < CHUNK_CAP:
                    continue
        elif not buf:
            continue
        if dead:
            if final:
                return
            continue
        data = buf
        buf = b""
        try:
            text = pending + data.decode("utf-8", "surrogateescape")
            emit, pending = split_safe(text, final)
            if emit:
                began = time.monotonic()
                engine.deadline = began + eng.REDACT_BUDGET - spent
                try:
                    out = eng.run_budget(lambda: engine.redact_text(emit, ctx), eng.REDACT_BUDGET - spent + eng.BACKSTOP)
                finally:
                    spent += time.monotonic() - began
                write(out.encode("utf-8", "surrogateescape"))
                if engine.overrun:
                    dead = engine.overrun
                    write(b"\n")
                    pending = ""
        except eng.OverBudget:
            dead = "redaction time budget exceeded"
            write((eng.WITHHELD % dead + "\n").encode())
            pending = ""
        except Exception as exc:
            dead = "error: " + type(exc).__name__
            write((eng.WITHHELD % dead + "\n").encode())
            pending = ""
        if final:
            return


if __name__ == "__main__":
    try:
        main()
    except Exception:
        os._exit(0)
