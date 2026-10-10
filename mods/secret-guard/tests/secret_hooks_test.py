#!/usr/bin/env python3
"""Judge for secret_redact.py, secret_guard.py and secret_filter.py. See README.md and test-spec.md.

Implementers of the hooks must not edit this file, sandbox.sb or any fixture: fixtures.sha256 locks them.
"""
import argparse
import base64
import binascii
import codecs
import concurrent.futures as cf
import functools
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER = Path(__file__).resolve()
SANDBOX_SB = HERE / "sandbox.sb"
HOOK_FILES = {"post": "secret_redact.py", "pre": "secret_guard.py", "filter": "secret_filter.py"}
KINDS = ("post", "pre", "pre_exec", "e2e")
EXEC_TIMEOUT = 20
E2E_TIMEOUT = 300
SAFE_PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

NULL_STUBS = {
    "secret_redact.py": "# null stub: pass-through\n",
    "secret_guard.py": "# null stub: pass-through\n",
    "secret_filter.py": "import sys, shutil\nshutil.copyfileobj(sys.stdin.buffer, sys.stdout.buffer)\n",
}

RECORDER = (
    "import json, sys\n"
    "d = json.load(sys.stdin)\n"
    "open(sys.argv[1], 'a').write(json.dumps(d) + '\\n')\n"
)

TOKEN_RES = [
    re.compile(p) for p in (
        r"gh[pousr]_[A-Za-z0-9]{36,}", r"github_pat_[A-Za-z0-9_]{20,}", r"(?:AKIA|ASIA)[0-9A-Z]{16}",
        r"[sr]k_(?:live|test)_[A-Za-z0-9]{16,}", r"sk-ant-[A-Za-z0-9_-]{20,}", r"sk-(?:proj-)?[A-Za-z0-9_-]{32,}",
        r"xox[abposr]-[A-Za-z0-9-]{10,}",
        r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----[ \t]*\r?\n(?:[A-Za-z0-9+/=]{16,}[ \t]*\r?\n?)+",
    )
]
PLACEHOLDER_WORDS = ("example", "your_", "_here", "placeholder", "xxxx", "changeme")
EXEMPT_PLACEHOLDERS = ("[REDACTED]", "[WITHHELD]")


# ---------------------------------------------------------------- helpers

def subst(obj, mapping):
    if isinstance(obj, str):
        for k, v in mapping.items():
            obj = obj.replace(k, v)
        return obj
    if isinstance(obj, list):
        return [subst(x, mapping) for x in obj]
    if isinstance(obj, dict):
        return {subst(k, mapping): subst(v, mapping) for k, v in obj.items()}
    return obj


def leaves(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for x in obj:
            yield from leaves(x)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(k)
            yield from leaves(v)


def dumps_forms(obj):
    return [json.dumps(obj, ensure_ascii=True), json.dumps(obj, ensure_ascii=False)]


def in_text(s, text):
    """s present raw or JSON-escaped."""
    if s in text:
        return True
    return any(json.dumps(s, ensure_ascii=ea)[1:-1] in text for ea in (True, False))


def in_json(s, obj):
    return any(in_text(s, d) for d in dumps_forms(obj))


def shape_diff(a, b, path="tool_response"):
    if type(a) is not type(b):
        return f"{path}: type {type(a).__name__} -> {type(b).__name__}"
    if isinstance(a, dict):
        if set(a) != set(b):
            return f"{path}: keys {sorted(set(a) ^ set(b))} differ"
        for k in a:
            d = shape_diff(a[k], b[k], f"{path}.{k}")
            if d:
                return d
    elif isinstance(a, list):
        if len(a) != len(b):
            return f"{path}: length {len(a)} -> {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            d = shape_diff(x, y, f"{path}[{i}]")
            if d:
                return d
    return None


def encoded_forms(text):
    raw = text.encode("utf-8", "replace")
    forms = {text, text[::-1], text.upper(), text.lower(), codecs.encode(text, "rot13"),
             urllib.parse.quote(text, safe=""), raw.hex(), raw.hex().upper(),
             base64.b64encode(raw).decode(), base64.urlsafe_b64encode(raw).decode(),
             base64.b64encode(raw).decode().rstrip("=")}
    forms |= {" ".join(text), "\n".join(text)}
    return forms


def derived_from(s, texts):
    for t in texts:
        pieces = {t} | set(t.split()) | set(t.splitlines())
        for p in pieces:
            if p and any(s in f for f in encoded_forms(p)):
                return True
    return False


_NOTES = threading.local()
SEP = r"(?:[ \t\r\n]|\\n|\\t|\\r|(?<=\n)[0-7]{7}|(?<=\\n)[0-7]{7})+"


def note(msg):
    getattr(_NOTES, "v", []).append(msg)


def b64_runs(b):
    out = {}
    for k in range(3):
        data = b"\0" * k + b
        start = -(-k * 8 // 6)
        for kind, fn in (("std", base64.b64encode), ("urlsafe", base64.urlsafe_b64encode)):
            e = fn(data).decode()
            if k == 0:
                out[f"base64-{kind}-padded"] = e
                out[f"base64-{kind}-unpadded"] = e.rstrip("=")
            core = e.rstrip("=")
            if len(data) % 3:
                core = core[:-1]
            core = core[start:]
            if len(core) >= 8:
                out[f"base64-{kind}-align{k}"] = core
    return out


@functools.lru_cache(maxsize=None)
def forms(text):
    """Every shape a leaked copy of text can take: name -> str or compiled regex."""
    out = {"raw": text, "reversed": text[::-1], "upper": text.upper(), "lower": text.lower(),
           "rot13": codecs.encode(text, "rot13"), "url-encoded": urllib.parse.quote(text, safe=""),
           "url-encoded-plus": urllib.parse.quote_plus(text)}
    if len(text) > 1:
        out["spaced"] = re.compile(SEP.join(re.escape(c) for c in text), re.I)
    for enc in ("utf-8", "utf-16-le", "utf-16-be"):
        b = text.encode(enc, "surrogatepass")
        if enc != "utf-8":
            out[f"{enc}-raw"] = b.decode("latin-1")
        h = b.hex()
        pairs = [h[i:i + 2] for i in range(0, len(h), 2)]
        out[f"hex-lower[{enc}]"] = h
        out[f"hex-upper[{enc}]"] = h.upper()
        if len(pairs) > 1:
            out[f"hex-separated[{enc}]"] = re.compile(r"[ :]+".join(pairs), re.I)
        out[f"hex-escaped[{enc}]"] = "\\x" + "\\x".join(pairs)
        for name, v in b64_runs(b).items():
            out[f"{name}[{enc}]"] = v
    return out


def texts_of(hay):
    if isinstance(hay, str):
        return [hay]
    return dumps_forms(hay) + list(leaves(hay))


def hit(s, *hays):
    """Name of the first form of s found in any haystack (FAKE entries expand; others match raw only)."""
    ts = [t for h in hays for t in texts_of(h)]
    fs = forms(s) if "fake" in s.lower() else {"raw": s}
    for name, f in fs.items():
        if isinstance(f, str):
            if f and any(in_text(f, t) for t in ts):
                return name
        elif any(f.search(t) for t in ts):
            return name
    return None


def fake_tokens(fx):
    toks = set()
    for t in fake_pool(fx):
        for w in re.split(r"[\s\"'=:,;()\[\]{}<>]+", t):
            if "fake" in w.lower():
                toks.add(w.lower())
    return toks


def strip_variants(s):
    sep = r"\\x|0x|[\s:,\0]"
    return re.sub(sep, "", s), re.sub(sep, "", re.sub(r"(?m)^[ \t]*\d+[ \t:|]*", "", s))


def decoded_variants(s):
    out = {s}
    st, nl = strip_variants(s)
    out.update((st, nl))
    for v in (s, st):
        blobs = []
        if re.fullmatch(r"(?:[0-9a-fA-F]{2}){4,}", v):
            blobs.append(bytes.fromhex(v))
        if re.fullmatch(r"[0-9a-fA-F]{9,}", v) and len(v) % 2:
            blobs.append(bytes.fromhex(v[1:]))
        if re.fullmatch(r"[A-Za-z0-9+/_=-]{8,}", v):
            for off in range(4):
                c = v[off:].rstrip("=")
                if len(c) % 4 == 1:
                    c = c[:-1]
                c += "=" * (-len(c) % 4)
                try:
                    blobs.append(base64.urlsafe_b64decode(c))
                except (binascii.Error, ValueError):
                    continue
        for b in blobs:
            for enc in ("utf-8", "utf-16-le", "utf-16-be"):
                out.add(b.decode(enc, "ignore").replace("\0", ""))
            out.add(b.decode("latin-1").replace("\0", ""))
    return out


def decoded_overlap(fx, s):
    toks = fake_tokens(fx)
    short = {v for v in strip_variants(s) if v != s and len(v) >= 3}
    for v in decoded_variants(s):
        low = v.lower()
        w = min(6, len(v)) if v in short else 6
        for t in toks:
            if any(t[i:i + w] in low for i in range(len(t) - w + 1)):
                return True
    return False


def trivial_found(s, hays, record=False):
    """Why s counts as present in the raw input: the form that matched, or None."""
    f = hit(s, *hays)
    if f is None and any(derived_from(s, texts_of(h)) for h in hays):
        f = "substring of an encoding"
    if f is None and "fake" not in s.lower():
        for v in decoded_variants(s) - {s}:
            if len(v) < 6 and "fake" not in v.lower():
                continue
            g = hit(v, *hays) if "fake" in v.lower() else (
                "decoded raw" if any(in_text(v, t) for h in hays for t in texts_of(h)) else None)
            if g:
                f = f"decoded entry, {g}"
                break
    if f and record:
        note(f"{s[:40]!r} found as {f}")
    return f


def scan_secrets(text):
    bad = []
    for rx in TOKEN_RES:
        for m in rx.finditer(text):
            low = m.group(0).lower()
            if "fake" not in low and not any(w in low for w in PLACEHOLDER_WORDS):
                bad.append(m.group(0)[:60])
    return bad


def exempt(fx, s):
    return s in EXEMPT_PLACEHOLDERS and bool(fx.get("must_see"))


def fake_pool(fx):
    pool = list(files_of(fx).values()) + list(leaves({k: v for k, v in fx.items() if k != "files"}))
    return [t for t in pool if "fake" in t.lower()]


def marker_ok(fx, s):
    if "fake" in s.lower():
        return True
    return derived_from(s, fake_pool(fx)) or decoded_overlap(fx, s)


def files_of(fx):
    return fx.get("files") or {}


def validate_static(case, fx):
    """Return an error string or None."""
    _NOTES.v = []
    kind = fx.get("kind")
    if kind not in KINDS:
        return f"unknown kind {kind!r}"
    if not isinstance(fx.get("name"), str) or not fx["name"]:
        return "missing name"
    files = files_of(fx)
    if not isinstance(files, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in files.items()):
        return "files must map relpath -> string"
    for rel in files:
        r = rel[2:] if rel.startswith("~/") else rel
        if not r or Path(r).is_absolute() or ".." in Path(r).parts or r.startswith(("/", "\\")):
            return f"files path {rel!r} escapes the temp project/home"
    for key in ("must_not_see", "must_see"):
        v = fx.get(key, [])
        if not isinstance(v, list) or not all(isinstance(x, str) and x for x in v):
            return f"{key} must be a list of non-empty strings"
    has_assert = bool(fx.get("must_not_see") or fx.get("must_see"))
    texts = list(files.values())
    if kind == "post":
        ev = fx.get("event")
        if not isinstance(ev, dict) or ev.get("hook_event_name") != "PostToolUse" or "tool_response" not in ev:
            return "post needs a PostToolUse event with tool_response"
        if not has_assert:
            return "asserts nothing (no must_not_see or must_see)"
        for s in fx.get("must_not_see", []):
            if not exempt(fx, s) and not trivial_found(s, [ev], record=True):
                return f"TRIVIAL: must_not_see {s!r} is not in the raw event"
        texts += list(leaves(ev))
    elif kind == "pre":
        ev = fx.get("event")
        if not isinstance(ev, dict) or ev.get("hook_event_name") != "PreToolUse" or not ev.get("tool_name"):
            return "pre needs a PreToolUse event with tool_name"
        if fx.get("expect") not in ("deny", "allow"):
            return "pre needs expect deny|allow"
        texts += list(leaves(ev))
    elif kind == "pre_exec":
        if not isinstance(fx.get("command"), str) or not fx["command"]:
            return "pre_exec needs command"
        if "exit_code" in fx and not isinstance(fx["exit_code"], int):
            return "exit_code must be an int"
        if "cwd_after" in fx and not isinstance(fx["cwd_after"], str):
            return "cwd_after must be a string"
        if not (has_assert or "exit_code" in fx or "cwd_after" in fx):
            return "asserts nothing"
        texts.append(fx["command"])
    else:
        if not isinstance(fx.get("prompt"), str) or not fx["prompt"]:
            return "e2e needs prompt"
        if not isinstance(fx.get("allowed_tools"), str) or not fx["allowed_tools"]:
            return "e2e needs allowed_tools"
        if not has_assert:
            return "asserts nothing"
        for s in fx.get("must_not_see", []):
            if not (exempt(fx, s) or trivial_found(s, list(files.values()) + [fx["prompt"]], record=True)):
                return f"TRIVIAL: must_not_see {s!r} is not in the files or an encoding of them"
        texts.append(fx["prompt"])
    for s in fx.get("must_not_see", []):
        if not exempt(fx, s) and not marker_ok(fx, s):
            return f"MARKER: must_not_see {s!r} lacks FAKE and is not derived from a FAKE string"
    for t in list(files.values()) + list(leaves({k: v for k, v in fx.items() if k != "files"})):
        bad = scan_secrets(t)
        if bad:
            return f"MARKER: real-looking token format without FAKE: {bad[0]!r}"
    return None


# ---------------------------------------------------------------- sandbox + processes

class Sandbox:
    def __init__(self, hooks_dir):
        self.hooks_dir = hooks_dir
        self.pyfw = os.path.realpath(sys.base_prefix)
        self.available = sys.platform == "darwin" and shutil.which("sandbox-exec") is not None and SANDBOX_SB.exists()
        self.why = "" if self.available else "sandbox-exec or sandbox.sb unavailable"

    def argv(self, tmp, argv):
        return ["sandbox-exec", "-f", str(SANDBOX_SB), "-D", f"TMP={tmp}", "-D", f"HOOKS={self.hooks_dir}",
                "-D", f"PYFW={self.pyfw}"] + argv

    def probe(self):
        if not self.available:
            return
        tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="sechook-probe-")))
        try:
            home = os.path.realpath(str(Path.home()))
            outside = tmp.parent / f"sechook-probe-{os.getpid()}"
            checks = [
                (["/bin/ls", home], "listing the real home must fail"),
                (["/bin/sh", "-c", f"echo x > {shlex.quote(str(outside))}"], "writing outside the temp dir must fail"),
            ]
            for argv, msg in checks:
                r = subprocess.run(self.argv(str(tmp), argv), capture_output=True, text=True, timeout=20)
                if r.returncode == 0:
                    outside.unlink(missing_ok=True)
                    self.available, self.why = False, f"sandbox self-check failed: {msg}"
                    return
            ok = subprocess.run(self.argv(str(tmp), ["/bin/sh", "-c", "echo ok"]), capture_output=True, text=True, timeout=20)
            if ok.returncode != 0 or ok.stdout.strip() != "ok":
                self.available, self.why = False, f"sandbox cannot run a shell: {ok.stderr.strip()[:120]}"
        except (OSError, subprocess.SubprocessError) as e:
            self.available, self.why = False, f"sandbox probe error: {e}"
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class Ctx:
    """One temp world per fixture: root/home/Projects/proj, rebuilt before each execution."""

    def __init__(self, fx, hooks_dir, sandbox, require_sandbox):
        self.fx, self.sandbox, self.require = fx, sandbox, require_sandbox
        self.hooks_dir = hooks_dir
        self.root = Path(os.path.realpath(tempfile.mkdtemp(prefix="sechook-")))
        self.home = self.root / "home"
        self.project = self.home / "Projects" / "proj"
        self.meta = self.root / "meta"
        self.mapping = {"{PROJECT}": str(self.project), "{HOME}": str(self.home),
                        "{REALHOME}": os.path.realpath(str(Path.home()))}
        self.reset()

    def reset(self):
        for child in self.root.iterdir():
            shutil.rmtree(child, ignore_errors=True) if child.is_dir() else child.unlink()
        for d in (self.project, self.meta, self.root / "tmp", self.home / ".claude"):
            d.mkdir(parents=True, exist_ok=True)
        link = self.home / ".claude" / "hooks"
        try:
            link.symlink_to(self.hooks_dir)
        except OSError:
            pass
        for rel, content in files_of(self.fx).items():
            dest = self.home / rel[2:] if rel.startswith("~/") else self.project / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(subst(content, self.mapping))

    def env(self):
        py = shutil.which("python3") or sys.executable
        return {"PATH": f"{Path(py).parent}:{SAFE_PATH}", "HOME": str(self.home), "SECRET_HOOK_HOME": str(self.home),
                "SECRET_HOOK_ROOTS": str(self.home / "Projects"), "TMPDIR": str(self.root / "tmp"),
                "LANG": "en_US.UTF-8", "PYTHONDONTWRITEBYTECODE": "1", "TERM": "dumb"}

    def run(self, argv, stdin="", timeout=EXEC_TIMEOUT):
        """Returns (rc, stdout, stderr); rc None on timeout. Sandboxed when available."""
        if self.sandbox.available:
            argv = self.sandbox.argv(str(self.root), argv)
        elif self.require:
            raise UnsafeError(self.sandbox.why)
        p = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             cwd=str(self.project), env=self.env(), start_new_session=True)
        try:
            out, err = p.communicate(stdin.encode(), timeout=timeout)
            return p.returncode, out.decode("utf-8", "replace"), err.decode("utf-8", "replace")
        except subprocess.TimeoutExpired:
            try:
                os.killpg(p.pid, signal.SIGKILL)
            except OSError:
                pass
            p.communicate()
            return None, "", ""

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)


class UnsafeError(Exception):
    pass


def hook_argv(hooks_dir, name):
    return [shutil.which("python3") or sys.executable, str(Path(hooks_dir) / name)]


def parse_hook_json(out):
    out = out.strip()
    if not out:
        return None, None
    try:
        obj = json.loads(out)
    except ValueError:
        return None, "stdout is not JSON"
    if not isinstance(obj, dict):
        return None, "stdout JSON is not an object"
    return obj, None


def need_hooks(hooks_dir, *names):
    missing = [n for n in names if not (Path(hooks_dir) / n).is_file()]
    return f"hook file missing: {', '.join(missing)}" if missing else None


# ---------------------------------------------------------------- fixture runners (return (status, reason))

def run_post(fx, ctx, hooks_dir):
    miss = need_hooks(hooks_dir, HOOK_FILES["post"])
    if miss:
        return "FAIL", miss
    ev = subst(fx["event"], ctx.mapping)
    for s in fx.get("must_not_see", []):
        if not exempt(fx, s) and not trivial_found(s, [ev]):
            return "INVALID", f"TRIVIAL: must_not_see {s!r} is not in the raw event"
    feed = dict(ev)
    feed.setdefault("cwd", str(ctx.project))
    rc, out, err = ctx.run(hook_argv(hooks_dir, HOOK_FILES["post"]), json.dumps(feed))
    if rc is None:
        return "FAIL", f"hook timed out after {EXEC_TIMEOUT}s"
    if rc != 0:
        return "FAIL", f"hook exited {rc}: {err.strip()[:120]!r}"
    obj, perr = parse_hook_json(out)
    if perr:
        return "FAIL", perr
    hso = (obj or {}).get("hookSpecificOutput")
    visible = ev["tool_response"]
    if isinstance(hso, dict) and "updatedToolOutput" in hso:
        visible = hso["updatedToolOutput"]
        d = shape_diff(ev["tool_response"], visible)
        if d:
            return "FAIL", f"updatedToolOutput shape changed: {d}"
    for s in fx.get("must_not_see", []):
        f = hit(s, visible)
        if f:
            return "FAIL", f"saw {s} ({f}) in model-visible output"
        f = hit(s, err)
        if f:
            return "FAIL", f"saw {s} ({f}) in hook stderr"
        f = hit(s, out)
        if f:
            return "FAIL", f"saw {s} ({f}) in hook stdout"
    for s in fx.get("must_see", []):
        if not (any(s in t for t in leaves(visible)) or in_json(s, visible)):
            return "FAIL", f"missing {s!r} in model-visible output"
    return "PASS", ""


def guard_decision(fx_event, ctx, hooks_dir):
    feed = dict(fx_event)
    feed.setdefault("cwd", str(ctx.project))
    rc, out, err = ctx.run(hook_argv(hooks_dir, HOOK_FILES["pre"]), json.dumps(feed))
    if rc is None:
        return None, None, f"guard timed out after {EXEC_TIMEOUT}s"
    if rc != 0:
        return None, None, f"guard exited {rc}: {err.strip()[:120]!r}"
    obj, perr = parse_hook_json(out)
    if perr:
        return None, None, f"guard {perr}"
    hso = (obj or {}).get("hookSpecificOutput")
    hso = hso if isinstance(hso, dict) else {}
    return hso.get("permissionDecision") == "deny", hso, None


def run_pre(fx, ctx, hooks_dir):
    miss = need_hooks(hooks_dir, HOOK_FILES["pre"])
    if miss:
        return "FAIL", miss
    ev = subst(fx["event"], ctx.mapping)
    denied, _hso, err = guard_decision(ev, ctx, hooks_dir)
    if err:
        return "FAIL", err
    got = "deny" if denied else "allow"
    if got != fx["expect"]:
        return "FAIL", f"expected {fx['expect']}, guard said {got}"
    return "PASS", ""


def shell_list():
    shells = [("bash", "/bin/bash" if Path("/bin/bash").exists() else shutil.which("bash"))]
    if Path("/bin/zsh").exists():
        shells.append(("zsh", "/bin/zsh"))
    return [(n, p) for n, p in shells if p]


def exec_command(ctx, shell_path, command):
    """Run command with an EXIT trap recording the final cwd. Returns (rc, stdout, stderr, cwd)."""
    ctx.reset()
    cwdfile = ctx.meta / "cwd"
    wrapped = f"trap 'pwd -P > {shlex.quote(str(cwdfile))}' EXIT\n{command}"
    rc, out, err = ctx.run([shell_path, "-c", wrapped])
    cwd = cwdfile.read_text().strip() if cwdfile.exists() else None
    return rc, out, err, cwd


def run_pre_exec(fx, ctx, hooks_dir, validate_only=False):
    command = subst(fx["command"], ctx.mapping)
    if not ctx.sandbox.available:
        return "UNSAFE", f"sandbox unavailable ({ctx.sandbox.why}); not running unsandboxed"
    must_not = fx.get("must_not_see", [])
    originals = {}
    for sh, path in shell_list():
        rc, out, err, _cwd = exec_command(ctx, path, command)
        if rc is None:
            return "FAIL", f"original timed out under {sh}"
        originals[sh] = (rc, out, err)
        for s in must_not:
            if not exempt(fx, s) and not trivial_found(s, [out + err]):
                return "INVALID", f"TRIVIAL: must_not_see {s!r} not in original {sh} output"
        if "exit_code" in fx and rc != fx["exit_code"]:
            return "INVALID", f"original exit {rc} != exit_code {fx['exit_code']} under {sh}"
    if validate_only:
        return "PASS", ""
    miss = need_hooks(hooks_dir, HOOK_FILES["pre"], HOOK_FILES["filter"])
    if miss:
        return "FAIL", miss
    ctx.reset()
    ev = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": command}}
    denied, hso, err = guard_decision(ev, ctx, hooks_dir)
    if err:
        return "FAIL", err
    if denied:
        if "must_see" in fx or "exit_code" in fx or "cwd_after" in fx:
            return "FAIL", "denied but fixture requires the command to run"
        return "PASS", ""
    new = (hso.get("updatedInput") or {}).get("command", command)
    if not isinstance(new, str):
        return "FAIL", "updatedInput.command is not a string"
    for sh, path in shell_list():
        rc, out, err, cwd = exec_command(ctx, path, new)
        if rc is None:
            return "FAIL", f"rewritten command timed out under {sh}"
        for s in must_not:
            f = hit(s, out)
            if f:
                return "FAIL", f"saw {s} ({f}) in stdout ({sh})"
            f = hit(s, err)
            if f:
                return "FAIL", f"saw {s} ({f}) in stderr ({sh})"
        combined = out + err
        for s in fx.get("must_see", []):
            if s not in combined:
                return "FAIL", f"missing {s!r} in output ({sh})"
        if "exit_code" in fx and rc != fx["exit_code"]:
            return "FAIL", f"exit code {rc}, expected {fx['exit_code']} ({sh})"
        if "cwd_after" in fx:
            want = os.path.realpath(str(ctx.project / fx["cwd_after"]))
            if cwd is None or os.path.realpath(cwd) != want:
                return "FAIL", f"cwd after is {cwd!r}, expected {want!r} ({sh})"
    return "PASS", ""


def run_e2e(fx, ctx, hooks_dir):
    miss = need_hooks(hooks_dir, HOOK_FILES["post"], HOOK_FILES["pre"], HOOK_FILES["filter"])
    if miss:
        return "FAIL", miss
    claude = os.environ.get("SECRET_TEST_CLAUDE") or shutil.which("claude")
    if not claude:
        return "FAIL", "claude binary not found"
    py = shutil.which("python3") or sys.executable
    # The child's sandbox denies reads of the real home, so the hooks must live outside it.
    local_hooks = ctx.root / "hooks"
    shutil.copytree(hooks_dir, local_hooks, ignore=shutil.ignore_patterns("__pycache__"))
    hooks_dir = local_hooks
    record = ctx.root / "record.jsonl"
    recorder = ctx.root / "recorder.py"
    recorder.write_text(RECORDER)
    q = shlex.quote
    settings = {"hooks": {
        "PostToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": f"{q(py)} {q(str(Path(hooks_dir) / HOOK_FILES['post']))}"}]}],
        "PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": f"{q(py)} {q(str(Path(hooks_dir) / HOOK_FILES['pre']))}"}]}],
        "PostToolBatch": [{"hooks": [{"type": "command", "command": f"{q(py)} {q(str(recorder))} {q(str(record))}"}]}],
    }}
    real_home = str(Path.home())
    settings["sandbox"] = {"enabled": True, "autoAllowBashIfSandboxed": True, "allowUnsandboxedCommands": False,
                           "filesystem": {"denyRead": [real_home]}, "network": {"allowedDomains": []}}
    settings["permissions"] = {"deny": [f"{t}(/{real_home}/**)" for t in ("Read", "Edit")]}
    spath = ctx.root / "settings.json"
    spath.write_text(json.dumps(settings))
    prompt = subst(fx["prompt"], ctx.mapping)
    env = dict(os.environ)
    env.update({"SECRET_HOOK_HOME": str(ctx.home), "SECRET_HOOK_ROOTS": str(ctx.home / "Projects")})
    argv = [claude, "-p", prompt, "--settings", str(spath), "--setting-sources", "project,local",
            "--allowedTools", fx["allowed_tools"]]
    if os.environ.get("SECRET_TEST_MODEL"):
        argv += ["--model", os.environ["SECRET_TEST_MODEL"]]
    try:
        with open(os.devnull, "rb") as devnull:
            r = subprocess.run(argv, cwd=str(ctx.project), env=env, stdin=devnull, capture_output=True,
                               text=True, timeout=E2E_TIMEOUT)
    except subprocess.TimeoutExpired:
        return "FAIL", f"claude timed out after {E2E_TIMEOUT}s"
    responses = []
    if record.exists():
        for line in record.read_text().splitlines():
            for call in json.loads(line).get("tool_calls", []):
                responses.append(call.get("tool_response"))
    if not responses:
        return "FAIL", "no tool call was recorded (the model never used a tool)"
    seen = responses + [r.stdout]
    for s in fx.get("must_not_see", []):
        f = next((f for f in (hit(s, x) for x in responses) if f), None)
        if f:
            return "FAIL", f"saw {s} ({f}) in a recorded tool_response"
        f = hit(s, r.stdout)
        if f:
            return "FAIL", f"saw {s} ({f}) in the final reply"
    for s in fx.get("must_see", []):
        if not any(in_json(s, x) or (isinstance(x, str) and s in x) for x in seen):
            return "FAIL", f"missing {s!r} in tool responses or final reply"
    return "PASS", ""


RUNNERS = {"post": run_post, "pre": run_pre, "pre_exec": run_pre_exec, "e2e": run_e2e}


def run_item(item, hooks_dir, sandbox):
    if item["static_error"]:
        return "INVALID", item["static_error"]
    fx = item["fx"]
    ctx = Ctx(fx, hooks_dir, sandbox, require_sandbox=(fx["kind"] == "pre_exec"))
    try:
        if item["validate_only"]:
            if fx["kind"] == "pre_exec":
                return run_pre_exec(fx, ctx, hooks_dir, validate_only=True)
            return "PASS", ""
        return RUNNERS[fx["kind"]](fx, ctx, hooks_dir)
    except UnsafeError as e:
        return "UNSAFE", str(e)
    except Exception as e:  # runner bug or hook-induced oddity: a failure, never a silent pass
        return "FAIL", f"runner error: {type(e).__name__}: {e}"
    finally:
        ctx.cleanup()


# ---------------------------------------------------------------- manifest

def manifest_entries(fixtures_dir):
    entries = {}
    for p in sorted(fixtures_dir.rglob("*")):
        if p.is_file():
            entries["fixtures/" + p.relative_to(fixtures_dir).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    entries["RUNNER"] = hashlib.sha256(RUNNER.read_bytes()).hexdigest()
    entries["SANDBOX"] = hashlib.sha256(SANDBOX_SB.read_bytes()).hexdigest()
    return entries


def manifest_text(entries):
    return "".join(f"{h}  {k}\n" for k, h in sorted(entries.items()))


def check_manifest(fixtures_dir, path):
    if not path.exists():
        return [f"manifest missing: {path} (fixture author runs --write-manifest)"]
    want = {}
    for line in path.read_text().splitlines():
        if line.strip():
            h, _, k = line.partition("  ")
            want[k] = h
    have = manifest_entries(fixtures_dir)
    problems = [f"changed: {k}" for k in have if k in want and have[k] != want[k]]
    problems += [f"added (not in manifest): {k}" for k in have if k not in want]
    problems += [f"removed (in manifest): {k}" for k in want if k not in have]
    return problems


# ---------------------------------------------------------------- main

def load_items(fixtures_dir, only, validate_only):
    items, not_testable, e2e_skipped_cases = [], [], []
    for p in sorted(fixtures_dir.glob("*.json")):
        stem = p.stem
        if only and stem not in only:
            continue
        try:
            case = json.loads(p.read_text())
        except ValueError as e:
            items.append({"case_id": stem, "kind": "case", "name": "unreadable fixture file", "fx": None,
                          "static_error": f"bad JSON: {e}", "validate_only": validate_only})
            continue
        cid = case.get("case_id") if isinstance(case, dict) else None
        if cid != stem:
            items.append({"case_id": stem, "kind": "case", "name": "case_id", "fx": None,
                          "static_error": f"case_id {cid!r} != file name {stem!r}", "validate_only": validate_only})
            continue
        level = case.get("level")
        if level == "not-testable":
            reason = case.get("reason_not_testable")
            if not reason:
                items.append({"case_id": cid, "kind": "case", "name": "not-testable", "fx": None,
                              "static_error": "not-testable without reason_not_testable", "validate_only": validate_only})
            else:
                not_testable.append((cid, case.get("title", ""), reason))
            continue
        fxs = case.get("fixtures")
        if level not in ("unit", "e2e") or not isinstance(fxs, list) or not fxs:
            items.append({"case_id": cid, "kind": "case", "name": case.get("title", ""), "fx": None,
                          "static_error": "needs level unit|e2e|not-testable and a non-empty fixtures list",
                          "validate_only": validate_only})
            continue
        seen = set()
        for fx in fxs:
            fx = fx if isinstance(fx, dict) else {}
            err = validate_static(case, fx)
            notes = list(_NOTES.v)
            if not err and fx["name"] in seen:
                err = "duplicate fixture name in case"
            seen.add(fx.get("name"))
            items.append({"case_id": cid, "kind": fx.get("kind", "case"), "name": fx.get("name", "?"), "fx": fx,
                          "static_error": err, "validate_only": validate_only, "notes": notes})
    return items, not_testable


def is_protective(fx):
    if not fx:
        return False
    if fx["kind"] == "pre":
        return fx.get("expect") == "deny"
    return any(not exempt(fx, s) for s in fx.get("must_not_see", []))


def main():
    ap = argparse.ArgumentParser(description="Judge for the secret-redaction hooks.")
    ap.add_argument("--fixtures", default=str(HERE / "fixtures"))
    ap.add_argument("--hooks-dir", default=str(Path(__file__).resolve().parent.parent / "hooks"))
    ap.add_argument("--null", action="store_true", help="swap in pass-through hooks; report mutation survivors")
    ap.add_argument("--e2e", action="store_true")
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--only", nargs="+", default=[], metavar="CASE_ID")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--verbose", action="store_true", help="on passing lines, show which encoded form the trivial check found")
    ap.add_argument("--write-manifest", action="store_true")
    a = ap.parse_args()

    fixtures_dir = Path(a.fixtures).expanduser().resolve()
    manifest = fixtures_dir.parent / "fixtures.sha256"
    logpath = fixtures_dir.parent / "last-run.log"
    if not fixtures_dir.is_dir():
        print(f"fixtures dir not found: {fixtures_dir}")
        return 2
    logf = open(logpath, "w", buffering=1)
    lock = threading.Lock()

    def emit(line=""):
        with lock:
            print(line, flush=True)
            logf.write(line + "\n")
            logf.flush()

    if not a.write_manifest:
        problems = check_manifest(fixtures_dir, manifest)
        if problems:
            emit("REFUSING TO RUN: fixtures/runner/sandbox do not match tests/fixtures.sha256")
            for p in problems[:30]:
                emit("  " + p)
            return 3

    hooks_dir = Path(a.hooks_dir).expanduser().resolve()
    null_dir = None
    if a.null:
        null_dir = Path(os.path.realpath(tempfile.mkdtemp(prefix="sechook-null-")))
        for n, body in NULL_STUBS.items():
            (null_dir / n).write_text(body)
        hooks_dir = null_dir

    validate_only = a.validate_only or a.write_manifest
    items, not_testable = load_items(fixtures_dir, set(a.only), validate_only)
    if a.only and not items and not not_testable:
        emit(f"--only matched no case in {fixtures_dir}")
        return 2
    runnable, e2e_not_run = [], []
    for it in items:
        if it["kind"] == "e2e" and not a.e2e and not it["static_error"] and not validate_only:
            e2e_not_run.append(it)
        else:
            runnable.append(it)
    if not runnable and not e2e_not_run:
        emit("no fixtures to run")
        return 1

    sandbox = Sandbox(hooks_dir)
    sandbox.probe()
    emit(f"fixtures: {fixtures_dir}  hooks: {hooks_dir}{'  (NULL hooks)' if a.null else ''}  jobs: {a.jobs}")
    emit(f"sandbox: {'on' if sandbox.available else 'OFF - ' + sandbox.why}; log: {logpath}")
    if not sandbox.available:
        emit("WARNING: pre_exec fixtures will be reported failed-unsafe; post/pre run unsandboxed")

    total = len(runnable)
    width = len(str(total))
    done = [0]
    results = [None] * total

    def work(i):
        it = runnable[i]
        status, reason = run_item(it, hooks_dir, sandbox)
        if a.null and status == "PASS" and is_protective(it["fx"]):
            status, reason = "SURVIVOR", "passes with no protection (mutation survivor)"
        with lock:
            done[0] += 1
            n = done[0]
        mark = "✔" if status == "PASS" or (a.null and status == "FAIL") else "✘"
        label = f'{it["case_id"]} {it["kind"]:<5} "{it["name"]}"'
        line = f"[{n:>{width}}/{total}] {mark} {label}"
        if status == "PASS" and a.verbose and it.get("notes"):
            line += " [" + "; ".join(it["notes"]) + "]"
        if status != "PASS":
            line += f" -> {status}: {reason}" if status in ("INVALID", "UNSAFE", "SURVIVOR") else f" -> {reason}"
        emit(line)
        results[i] = (status, reason)

    with cf.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        list(ex.map(work, range(total)))

    kinds = sorted({it["kind"] for it in runnable})
    emit()
    emit("== summary ==")
    for k in kinds:
        rs = [results[i][0] for i, it in enumerate(runnable) if it["kind"] == k]
        emit(f"{k:<9} total {len(rs):>5}  pass {rs.count('PASS'):>5}  fail {rs.count('FAIL'):>5}  "
             f"invalid {rs.count('INVALID'):>4}  unsafe {rs.count('UNSAFE'):>4}  survivors {rs.count('SURVIVOR'):>4}")
    ordered = [(runnable[i], results[i]) for i in range(total)]
    invalid = [(it, r) for it, r in ordered if r[0] == "INVALID"]
    unsafe = [(it, r) for it, r in ordered if r[0] == "UNSAFE"]
    survivors = [(it, r) for it, r in ordered if r[0] == "SURVIVOR"]
    failed = [(it, r) for it, r in ordered if r[0] == "FAIL"]
    emit(f"\ninvalid fixtures ({len(invalid)}):")
    for it, r in invalid:
        emit(f'  {it["case_id"]} {it["kind"]} "{it["name"]}": {r[1]}')
    emit(f"mutation survivors ({len(survivors)}):" if a.null else "mutation survivors: n/a (run with --null)")
    for it, r in survivors:
        emit(f'  {it["case_id"]} {it["kind"]} "{it["name"]}"')
    emit(f"failed-unsafe ({len(unsafe)}):")
    for it, r in unsafe:
        emit(f'  {it["case_id"]} {it["kind"]} "{it["name"]}": {r[1]}')
    emit(f"not testable ({len(not_testable)}):")
    for cid, title, reason in not_testable:
        emit(f"  {cid} {title!r}: {reason}")
    emit(f"not run: e2e ({len(e2e_not_run)}):")
    for it in e2e_not_run:
        emit(f'  {it["case_id"]} "{it["name"]}"')

    if a.write_manifest:
        manifest.write_text(manifest_text(manifest_entries(fixtures_dir)))
        emit(f"manifest written: {manifest}")
        if invalid:
            emit("WARNING: manifest written but invalid fixtures exist; fix them before handing over")
        return 1 if invalid else 0

    if a.null:
        killed = len(failed)
        bad = len(survivors) + len(invalid) + len(unsafe)
        emit(f"\nNULL RUN: {killed} fixtures failed without protection (expected); "
             f"{len(survivors)} survivors; verdict {'FAIL' if bad else 'OK'}")
        verdict = bad == 0
    else:
        bad = len(failed) + len(invalid) + len(unsafe)
        emit(f"\nVERDICT: {'PASS' if bad == 0 else 'FAIL'} ({bad} failing of {total} run)")
        verdict = bad == 0
    if null_dir:
        shutil.rmtree(null_dir, ignore_errors=True)
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())
