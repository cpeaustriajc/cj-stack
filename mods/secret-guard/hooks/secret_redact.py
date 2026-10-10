#!/usr/bin/env python3
"""PostToolUse hook: redact secrets from tool_response, keeping its exact shape.

The parent imports only the standard library. It runs the engine in a worker
process under a hard wall-clock deadline and withholds the whole response when
the worker overruns, crashes or prints anything but a redacted envelope.
"""
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True

DEADLINE = 15.0
MAX_BYTES = 48 * 1024 * 1024
WORKER_ARG = "--worker"
WITHHELD = "[REDACTED: output withheld (%s)]"


class Withhold(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def envelope(obj):
    return json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedToolOutput": obj}},
                      ensure_ascii=True).encode("ascii")


def emit_bytes(data):
    view = memoryview(data)
    while view:
        n = os.write(1, view)
        view = view[n:]


def placeholder_like(o, reason):
    if isinstance(o, str):
        return WITHHELD % reason
    if isinstance(o, list):
        return [placeholder_like(x, reason) for x in o]
    if isinstance(o, dict):
        return {k: placeholder_like(v, reason) for k, v in o.items()}
    return o


def run_worker(raw, started):
    proc = subprocess.Popen([sys.executable, os.path.abspath(__file__), WORKER_ARG],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    try:
        out, _ = proc.communicate(raw, timeout=max(0.1, DEADLINE - (time.monotonic() - started)))
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate()
        raise Withhold("timeout")
    except BaseException:
        proc.kill()
        proc.communicate()
        raise
    if proc.returncode != 0:
        raise Withhold("error: worker exited")
    try:
        obj = json.loads(out.decode("utf-8"))
    except ValueError:
        raise Withhold("error: bad worker output")
    hso = obj.get("hookSpecificOutput") if isinstance(obj, dict) else None
    if not isinstance(hso, dict) or "updatedToolOutput" not in hso:
        raise Withhold("error: bad worker output")
    return out


def main():
    started = time.monotonic()
    raw = sys.stdin.buffer.read()
    try:
        ev = json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        return
    resp = ev.get("tool_response") if isinstance(ev, dict) else None
    if resp is None:
        return
    try:
        out = run_worker(raw, started)
    except Withhold as w:
        reason = w.reason
    except Exception as exc:
        reason = "error: " + type(exc).__name__
    else:
        emit_bytes(out)
        return
    emit_bytes(envelope(placeholder_like(resp, reason)))


def worker():
    raw = sys.stdin.buffer.read()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        ev = json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        return
    resp = ev.get("tool_response") if isinstance(ev, dict) else None
    if resp is None:
        return
    import secret_engine as eng

    try:
        if len(raw) > MAX_BYTES:
            out = eng.placeholder_like(resp, "oversized")
        elif eng.odd_shape(ev.get("tool_name"), resp):
            out = eng.withhold_shape(resp)
        elif eng.withhold_ctx(ev.get("tool_name"), ev.get("tool_input")):
            out = eng.marked_like(resp)
        else:
            cwd = ev.get("cwd") if isinstance(ev.get("cwd"), str) else None
            engine = eng.Engine(cwd)
            engine.grep_words = eng.grep_hint_words(ev.get("tool_name"), ev.get("tool_input"))
            ctx = eng.command_ctx(ev.get("tool_name"), ev.get("tool_input"))
            engine.deadline = time.monotonic() + eng.REDACT_BUDGET
            out = eng.run_budget(lambda: engine.redact_obj(resp, ctx=ctx), eng.REDACT_BUDGET + eng.BACKSTOP)
    except eng.OverBudget:
        out = eng.placeholder_like(resp, "redaction time budget exceeded")
    except Exception as exc:
        out = eng.placeholder_like(resp, "error: " + type(exc).__name__)
    emit_bytes(envelope(out))


if __name__ == "__main__":
    if sys.argv[1:] == [WORKER_ARG]:
        worker()
    else:
        try:
            main()
        except Exception as exc:
            raise SystemExit(0) from exc
