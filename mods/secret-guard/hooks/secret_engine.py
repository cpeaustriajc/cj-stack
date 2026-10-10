#!/usr/bin/env python3
"""Shared secret detection and redaction engine for the secret hooks. Stdlib only."""
import base64
import bisect
import codecs
import hashlib
import html
import json
import os
import re
import signal
import sys
import tempfile
import threading
import time
import urllib.parse
import unicodedata

MARK = "[REDACTED]"
WITHHELD = "[REDACTED: output withheld (%s)]"
MAX_TEXT = 64 * 1024 * 1024

# ---------------------------------------------------------------- names

_CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_SPLIT = re.compile(r"[^A-Za-z0-9]+")

SECRET_WORDS = {
    "pass", "pwd", "pw", "passwd", "password", "passwords", "passphrase", "passcode", "secret", "secrets",
    "token", "tokens", "credential", "credentials", "cred", "creds", "auth", "authorization", "bearer",
    "apikey", "apikeys", "cookie", "cookies", "dsn", "salt", "signature", "hmac", "jwt", "otp", "totp",
    "privatekey", "secretkey", "accesskey", "authkey", "signingkey", "encryptionkey", "masterkey",
    "sessionkey", "clientsecret", "connectionstring", "pat", "bearertoken", "authtoken", "xauth",
    "mnemonic", "seed",
}
SECRET_STEMS = ("passw", "passphrase", "secret", "token", "credential", "apikey", "privatekey", "accesskey",
                "authkey", "signingkey", "encryptionkey", "masterkey", "sessionkey")
STEM_EXCEPT = {"tokenizer", "tokenizers", "tokenize", "tokenized", "tokenization", "secretary", "secretariat",
               "tokenizing", "passwordless", "passwordstrength"}
KEY_MODS = {"api", "private", "secret", "access", "auth", "license", "licence", "encryption", "signing", "master",
            "ssh", "preshared", "service", "account", "client", "app", "admin", "session", "crypto", "hmac", "jwt", "deploy",
            "decryption", "shared", "root", "backup", "bearer", "webhook", "stripe", "sentry", "x"}
NON_SECRET_LAST = {
    "count", "limit", "ttl", "type", "file", "path", "dir", "directory", "url", "uri", "name", "id", "ids",
    "length", "len", "size", "enabled", "disabled", "timeout", "format", "expires", "expiry", "expiration",
    "age", "prefix", "mode", "version", "algorithm", "alg", "endpoint", "ref", "status", "error", "hint",
    "policy", "rotation", "label", "header", "location", "provider", "scheme", "method", "env", "var",
    "variable", "field", "source", "user", "username", "host", "port", "domain", "title", "description",
    "message", "required", "optional", "flag", "lifetime", "interval", "max", "min", "expire", "kind",
    "store", "manager", "helper", "command", "cmd", "script", "option", "options", "config", "mount",
    "volume", "class", "regex", "pattern", "example", "template", "doc", "docs", "page", "link", "text",
    "placeholder", "strategy", "namespace", "bytes", "chars", "rounds", "cost", "check", "validator",
    "verified", "valid", "exists", "present", "set", "missing", "usage", "refresh_interval", "rate",
    "param", "params", "parameter", "key_name", "attr", "attribute", "selector", "tag", "tags", "color",
    "icon", "role", "scope", "scopes", "audience", "issuer", "claim", "claims", "event", "events", "handler",
    "hook", "callback", "redirect", "channel", "state", "level", "default", "defaults", "info", "reason",
    "mask", "masked", "display", "fingerprint", "hash_algo", "digest", "index", "order", "sort", "region",
    "right", "rights", "seconds", "secs", "sec", "minutes", "mins", "hours", "days", "ms", "millis", "budget", "date", "time",
    "timestamp", "headers", "name", "names", "regex", "length", "lengths", "words", "chars", "tokens_max",
    "limit", "limits", "doc", "docs", "note", "notes", "santa", "ui", "mgr", "service", "verification",
}
LEAD_NON_SECRET = {"max", "min", "num", "total", "input", "output", "prompt", "completion", "cache", "reasoning",
                   "remaining", "used", "avg", "count", "no", "is", "has", "use", "enable", "disable", "allow",
                   "skip", "require", "show", "hide", "mask", "default"}
PUBLIC_WORDS = {"public", "publishable", "pub", "anon"}


def words(name):
    return [w for w in _SPLIT.split(_CAMEL.sub(" ", name)) if w]


_name_cache = {}


def classify(name):
    """0 not secret, 1 secret, 2 weak (secret only when the value looks random)."""
    r = _name_cache.get(name)
    if r is not None:
        return r
    r = _classify(name)
    if len(_name_cache) < 20000:
        _name_cache[name] = r
    return r


FILE_EXT_NAME = re.compile(r"\.(?:ts|tsx|js|jsx|mjs|cjs|py|rb|go|rs|java|kt|swift|c|h|cc|cpp|php|sh|md|txt|json|ya?ml|toml|ini|cfg|conf|html|css|log|lock)$", re.I)


def _classify(name):
    if FILE_EXT_NAME.search(name):
        return 0
    ws = [w.lower() for w in words(name)]
    if not ws:
        return 0
    joined = "".join(ws)
    flat = [w for w in ws]
    if any(w in PUBLIC_WORDS for w in flat):
        return 0
    idx = None
    for i, w in enumerate(flat):
        if w in STEM_EXCEPT:
            continue
        if w in SECRET_WORDS or any(w.startswith(s) or (len(w) > 6 and s in w and w.endswith(s))
                                    for s in SECRET_STEMS):
            idx = i
            break
    if idx is None:
        for i, w in enumerate(flat):
            if w in ("key", "keys"):
                if any(m in KEY_MODS for m in flat[:i]):
                    idx = i
                    break
        if idx is None:
            for s in SECRET_STEMS:
                if s in joined and not any(e in joined for e in STEM_EXCEPT):
                    idx = 0
                    break
    if idx is None:
        if flat[-1] in ("key", "keys") and (len(flat) == 1 or name.isupper()):
            return 2
        return 0
    if flat[-3:] == ["access", "key", "id"]:
        return 1
    last = flat[-1]
    if idx != len(flat) - 1 and any(w in NON_SECRET_LAST for w in flat[idx + 1:]):
        return 0
    if idx != len(flat) - 1 and len(flat) > 1 and last.endswith("s") and last[:-1] in NON_SECRET_LAST:
        return 0
    if flat[0] in LEAD_NON_SECRET and flat[-1] in ("token", "tokens") and idx == len(flat) - 1:
        return 0
    return 1


def looks_random(v):
    if len(v) < 12:
        return False
    return bool(re.search(r"\d", v)) and bool(re.search(r"[A-Za-z]", v)) and " " not in v


BENIGN_EXACT = {"true", "false", "null", "none", "nil", "undefined", "yes", "no", "on", "off", "required",
                "optional", "string", "number", "boolean", "bool", "int", "integer", "secret", "password",
                "token", "text", "json", "bearer", "basic", "enabled", "disabled", "redacted", "masked",
                "hidden", "empty", "unset", "n/a", "na", "-", "--", "...", "***", "****", "*****", "********",
                "xxxxx", "xxxxxxxx", "0", "1", "()", "[]", "{}", "''", '""'}


def benign_h(v):
    if re.fullmatch(r"eyJ[\w\-]{6,}\.[\w\-]{6,}\.[\w\-]{1,19}", v.strip()):
        return False
    return benign(v)


def benign(v):
    s = v.strip().strip("\"'`,;")
    if not s:
        return True
    low = s.lower()
    if low in BENIGN_EXACT:
        return True
    if s.startswith("[REDACTED") or s.startswith("[WITHHELD") or MARK in s[:12]:
        return True
    if s[0] == "$" and re.match(r"\$(?:\{[^}]*\}|\(|[A-Za-z_][A-Za-z0-9_]*)", s):
        return True
    if s.startswith(("{{", "<%", "%(", "${", "#{")):
        return True
    if s[0] == "<" and s[-1] == ">":
        return True
    if s[0] == "%" and s[-1] == "%":
        return True
    if re.fullmatch(r"(?:(?:your|my|insert|enter|put)[\w\-]*[_\-](?:here|value|placeholder|goes[_\-]here)|(?:change|replace)[_\-]?me\w*|placeholder\w*)", low):
        return True
    if re.fullmatch(r"eyJ[\w\-]{6,}\.[\w\-]{6,}\.[\w\-]{1,19}", s):
        return True
    if s.startswith("ENC[") or re.fullmatch(r"\d{1,4}", s):
        return True
    if re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*){2,}", s) and not re.search(r"\d", s):
        return True
    if re.fullmatch(r"(?:[A-Za-z]+[_\-])*[xX*]{8,}", s):
        return True
    if re.fullmatch(r"\*+", s) or re.fullmatch(r"[xX*•·.]{4,}", s):
        return True
    if re.match(r"(?:process\.env|os\.environ|os\.getenv|getenv|env\(|ENV\[|System\.getenv|Deno\.env|import\.meta\.env"
                r"|config\(|settings\.|self\.|this\.|std::env)", s):
        return True
    if re.fullmatch(r"(?:\.{0,2}/|~/)[\w./\-]*", s) and len(s) > 3 and "/" in s and not re.search(r"\d{4,}", s):
        return True
    return False


# ---------------------------------------------------------------- patterns

TOKEN_PATTERNS = [
    r"gh[pousr]_[A-Za-z0-9_]{12,}",
    r"github_pat_[A-Za-z0-9_]{16,}",
    r"\b(?:AKIA|ASIA|AIDA|AROA|AGPA|ANPA)[0-9A-Z_]{12,}",
    r"\b[sr]k_(?:live|test)_[A-Za-z0-9]{10,}",
    r"\bwhsec_[A-Za-z0-9]{16,}",
    r"sk-ant-[A-Za-z0-9_\-]{10,}",
    r"\bsk-(?:proj-|svcacct-|admin-)?(?=[A-Za-z0-9_\-]*[\dA-Z])[A-Za-z0-9_\-]{10,}",
    r"\bxox[abposr]-[A-Za-z0-9\-]{10,}",
    r"\bxapp-[A-Za-z0-9\-]{10,}",
    r"\bpolar_[a-z]{2,5}_[A-Za-z0-9_\-]{12,}",
    r"\bcf(?:ut|k|at)_[A-Za-z0-9]{16,}",
    r"\bSK[0-9a-fA-F]{32}\b",
    r"\bSG\.[A-Za-z0-9_\-]{12,}\.[A-Za-z0-9_\-]{12,}",
    r"\bnpm_[A-Za-z0-9]{16,}",
    r"\bpypi-[A-Za-z0-9_\-]{16,}",
    r"\bAIza[0-9A-Za-z_\-]{30,}",
    r"\bya29\.[0-9A-Za-z_\-]{20,}",
    r"\bglpat-[A-Za-z0-9_\-]{16,}",
    r"\bdckr_pat_[A-Za-z0-9_\-]{16,}",
    r"\bhf_[A-Za-z0-9]{30,}",
    r"\bshp(?:at|ca|pa|ss)_[A-Fa-f0-9]{16,}",
    r"\bdop_v1_[a-f0-9]{32,}",
    r"(?<=AGE-SECRET-KEY-1)[A-Za-z0-9_]{8,}",
    r"\btskey-[A-Za-z0-9\-]{16,}",
    r"\bSG_[A-Za-z0-9_\-]{20,}",
    r"\beyJ[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{6,}\.(?:[A-Za-z0-9_\-]{20,}|(?![A-Za-z0-9_\-]))",
]
TOKEN_RE = re.compile("|".join("(?:%s)" % p for p in TOKEN_PATTERNS))

PEM_BEGIN = re.compile(r"-----BEGIN[ \t]+(?:[A-Z0-9]+[ \t]+)*?PRIVATE[ \t]+KEY(?:[ \t]+BLOCK)?-----")
PEM_END = re.compile(r"-----END[ \t]+(?:[A-Z0-9]+[ \t]+)*?PRIVATE[ \t]+KEY(?:[ \t]+BLOCK)?-----")
PEM_BODY = re.compile(r"(?:\\[nrt]|[A-Za-z0-9+/=\s\"',|>#*:;.\-\\\x1b\[0-9;m]|\x1b\[[0-9;]*m)+?")
PGP_BEGIN = re.compile(r"-----BEGIN PGP PRIVATE KEY BLOCK-----")
PEM_ASSIGN_NAME = re.compile(r"(?<![\w.\-])([A-Za-z_][\w.\-]{2,})=\Z")
PEM_BARE_HDR = re.compile(r"(?<![\w-])BEGIN[ \t]+(?:[A-Z0-9]+[ \t]+)*?PRIVATE[ \t]+KEY(?:[ \t]+BLOCK)?[ \t]+(?P<v>[^\s\\\"'<>]{8,})")

URL_USERINFO = re.compile(
    r"(?P<pre>[A-Za-z][A-Za-z0-9+.\-]{1,20}://(?:[^\s:/@'\"<>`\\]*:)?)(?P<pw>[^\s/'\"<>`\\]+?)@(?=[A-Za-z0-9_\[\-.%${]|$)")
URL_USER_ONLY = re.compile(r"(?P<pre>[A-Za-z][A-Za-z0-9+.\-]{1,20}://)(?P<pw>[A-Za-z0-9._~%+\-]{16,})@(?=[A-Za-z0-9])")

BEARER = re.compile(r"(?i)\b(?:bearer|basic|token|digest|negotiate|api-?key)[ \t]+(?P<v>[A-Za-z0-9._~+/=\-]{8,})")
SCHEME_RE = re.compile(r"(?i)(?:bearer|basic|token|digest|negotiate|api-?key)")

NAME_RE = re.compile(
    r"(?<![\w])(?P<q>\\*[\"'])?(?P<name>[A-Za-z_0-9][\w.\-]{0,100})(?P<q2>\\*[\"'])?[ \t]*(?P<sep>=>|:=|\?=|\+=|=(?!=)|:(?!//))")
PAIR_RE = re.compile(
    r"(?i)(?<![\w])\\*[\"']?(?:name|key)\\*[\"']?[ \t]*[:=][ \t]*\\*[\"']?(?P<n>[A-Za-z_][\w.\-]*)\\*[\"']?"
    r"[\s,;]*(?:\\n|\\r|\s)*[\s,;]*\\*[\"']?value\\*[\"']?[ \t]*[:=][ \t]*")
FLAG_RE = re.compile(
    r"(?<![\w])(?:--(?P<name>[A-Za-z][\w\-]*)|-(?P<name1>[a-z][a-z\-]*))(?:[ \t]+|=)(?=\S)")
CURL_U = re.compile(r"(?<![\w/.\-])(?:-u|--user|--proxy-user|-U)[ \t]*=?[ \t]*(?P<q>[\"']?)(?P<u>[^\s:\"']+):(?P<pw>[^\s\"']+)(?P=q)")
SHORT_PW = re.compile(r"(?<![\w\-])-p(?P<v>[^\s\-=][^\s]*)")
SHORT_PW_SP = re.compile(r"(?<![\w\-])-p[ \t]+(?P<v>[^\s\-=][^\s]*)")
CMD_PAIR = re.compile(r"(?<![\w.\-])(?P<n>[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+)[ \t]+(?![A-Za-z_][\w.\-]*=)(?P<v>[^\s'\"|;&]{12,})")
LINE_PRE = re.compile(r"[ \t]*(?:export[ \t]+|set[ \t]+|declare[ \t]+(?:-x[ \t]+)?|-[ \t]+|ENV[ \t]+|ARG[ \t]+|(?:\w+[ \t]*\|[ \t]*)?)?[\"']?$")
STOP_UNQUOTED = re.compile(r"[\s\"'`;&]|\\[nrt]|,(?=[\s\"']|$)|\\[\"']")


def _read_value(text, i, rest_of_line):
    """Return (start, end) of the value beginning at i, or None."""
    n = len(text)
    if i >= n:
        return None
    c = text[i]
    if c == "\\" and i + 1 < n and text[i + 1] in "\"'":
        q = text[i + 1]
        j = i + 2
        close = "\\" + q
        e = text.find(close, j)
        if e < 0:
            e = _eol(text, j)
        return j, e
    if c in "\"'":
        j = i + 1
        k = j
        while k < n:
            ch = text[k]
            if ch == "\\":
                k += 2
                continue
            if ch == c:
                break
            if ch == "\n":
                break
            k += 1
        return j, min(k, n)
    if c == "`":
        e = text.find("`", i + 1)
        return (i + 1, e if e > 0 else _eol(text, i + 1))
    if rest_of_line:
        e = _eol(text, i)
        m = re.search(r"\\[nrt]", text[i:e])
        if m:
            e = i + m.start()
        while e > i and text[e - 1] in " \t\r":
            e -= 1
        while e > i and text[e - 1] == "\\" and e < len(text) and text[e] == "\n":
            e = _eol(text, e + 1)
            while e > i and text[e - 1] in " \t\r":
                e -= 1
        return i, e
    m = STOP_UNQUOTED.search(text, i)
    return i, (m.start() if m else n)


def _eol(text, j):
    e = text.find("\n", j)
    return len(text) if e < 0 else e


def _value_span(text, i, name_start, name_cls):
    """Span of a value after a separator, applying the scheme-word and benign rules."""
    n = len(text)
    while i < n and text[i] in " \t":
        i += 1
    ls = text.rfind("\n", 0, name_start) + 1
    rest = bool(LINE_PRE.match(text[ls:name_start]))
    if i < n and text[i] in "[{" and not text.startswith("{{", i):
        return None
    sp = _read_value(text, i, rest)
    if not sp:
        return None
    s, e = sp
    if rest and text[s - 1:s] in "\"'" and s > 0:
        m3 = re.compile(r"(?:[ \t]+[\"'][^\"'\n]*[\"'])+").match(text, e + 1)
        if m3:
            e = m3.end() - 1
    if e <= s:
        return None
    v = text[s:e]
    mkv = re.match(r"[A-Za-z_][\w.\-]*=(?=[^=\s])", v)
    if mkv and text[name_start:s].count("=") == 0 and ":" in text[name_start:s]:
        s += mkv.end()
        v = text[s:e]
    if SCHEME_RE.fullmatch(v):
        j = e
        while j < n and text[j] in " \t":
            j += 1
        m2 = re.compile(r"[A-Za-z0-9._~+/=\-]+").match(text, j) if j > e else None
        if not m2:
            return None
        s, e = m2.start(), m2.end()
        v = text[s:e]
    else:
        m = re.match(r"(?i)(?:bearer|basic|token|digest|negotiate|api-?key)[ \t]+", v)
        if m:
            s += m.end()
            v = text[s:e]
            if v == "test":
                return None
    if benign(v):
        return None
    if name_cls == 2 and not looks_random(v):
        nm = re.match(r"[\w.\-]+", text[name_start:name_start + 101])
        if not (nm and nm.group().isupper() and ctx_secretish(v)):
            return None
    return s, e


def _first_line_has_sep(text):
    return ("=" in text) or (":" in text)


# ---------------------------------------------------------------- tables

def _psql_header(ln, nxt):
    """psql aligned output has no separator line: a pipe header with a secret-named column and a matching row."""
    return (ln.count("|") >= 2 and nxt.count("|") == ln.count("|")
            and any(classify(c[2].strip()) == 1 for c in _cells(ln, False)))


def _table_spans(text, spans):
    if "|" not in text:
        return
    lines = text.split("\n")
    pos = 0
    offs = []
    for ln in lines:
        offs.append(pos)
        pos += len(ln) + 1
    k = 0
    n = len(lines)
    while k < n:
        ln = lines[k]
        sep_ok = k + 1 < n and re.fullmatch(r"[\s+\-|=:]+", lines[k + 1]) and "-" in lines[k + 1]
        if ln.count("|") >= 1 and k + 1 < n and (sep_ok or _psql_header(ln, lines[k + 1])):
            lead = ln.lstrip().startswith("|")
            cols = _cells(ln, lead)
            sec = [classify(c[2].strip()) for c in cols]
            sec = [1 if x == 1 else 0 for x in sec]
            namecol = None
            for ci, c in enumerate(cols):
                if c[2].strip().lower() in ("name", "key", "variable", "var", "setting", "parameter", "option",
                                              "env", "field", "property"):
                    namecol = ci
            j = k + 2 if sep_ok else k + 1
            last_hit = set()
            while j < n and "|" in lines[j] and not re.fullmatch(r"[\s+\-|=:]*", lines[j]):
                cells = _cells(lines[j], lead)
                cont = namecol is not None and namecol < len(cells) and not cells[namecol][2].strip()
                now_hit = set()
                for ci, c in enumerate(cells):
                    hit = ci < len(sec) and sec[ci]
                    if not hit and namecol is not None and ci != namecol and namecol < len(cells):
                        nm = cells[namecol][2].strip()
                        if classify(nm) == 1 and ci > namecol:
                            hit = True
                    if cont and ci in last_hit:
                        hit = True
                    if hit:
                        now_hit.add(ci)
                    if hit:
                        val = c[2]
                        st = c[0] + (len(val) - len(val.lstrip()))
                        en = c[0] + len(val.rstrip())
                        if en > st and not benign(text[offs[j] + st:offs[j] + en]):
                            spans.append((offs[j] + st, offs[j] + en))
                if not cont:
                    last_hit = now_hit
                j += 1
            k = j
            continue
        k += 1


def _cells(line, lead=True):
    out = []
    pos = 0
    for part in line.split("|"):
        out.append((pos, pos + len(part), part))
        pos += len(part) + 1
    if lead and out and not out[0][2].strip():
        out = out[1:]
    if out and not out[-1][2].strip():
        out = out[:-1]
    return out


# ---------------------------------------------------------------- scanning

CTX_KEEP_NAMES = frozenset(["path", "port", "home", "user", "shell", "lang", "pwd", "oldpwd", "hostname", "tz", "term",
                            "node_env", "logname", "tmpdir", "editor", "pager", "shlvl", "_", "colorterm", "display",
                            "type", "name", "id", "title", "status", "state", "version", "host", "mode", "image",
                            "created", "size", "description", "format", "level"])
def ctx_secretish(v):
    if " " in v or v.startswith((".", "/", "~")) or "://" in v or "=" in v or re.fullmatch(r"\d{4}-\d\d-\d\d[T ]?[\d:.+Z\-]*", v):
        return False
    up, dig, us = re.search(r"[A-Z]", v), re.search(r"\d", v), "_" in v
    if up and (dig or us) and len(v) >= 6:
        return True
    return len(v) >= 16 and bool(dig) and bool(re.search(r"[A-Za-z]", v)) and bool(re.fullmatch(r"[A-Za-z0-9_+/\-]+", v))


def _is_dsn_name(name):
    ws = [w.lower() for w in words(name)]
    return len(ws) > 1 and ws[-1] in ("url", "uri", "dsn")


def _ctx_name_ok(name, m, text):
    if not re.match(r"[A-Za-z_]", name) or name.lower() in CTX_KEEP_NAMES or name.lower().startswith(("lc_", "xdg_")):
        return False
    if any(w in PUBLIC_WORDS for w in (x.lower() for x in words(name))):
        return False
    if m.group("sep") == ":" and m.end() < len(text) and text[m.end()] not in " \t\n\r\"'\\":
        return False
    return True


GREP_LN = re.compile(r"\d+:")
COOKIE_NAMES = frozenset(['session', 'sid', 'sessionid', 'session_id', 'auth', 'jwt', 'csrf', 'csrftoken'])
URL_UI = re.compile(r'[A-Za-z][A-Za-z0-9+.\-]{1,20}://[^\s/@"\']+@')


def _has_userinfo(text, sp):
    return bool(URL_UI.search(text, sp[0], sp[1]))


NESTED_JSON = re.compile(r'"(?P<n>[A-Za-z0-9_.-]{3,80})"\s*:\s*\{\s*"(?:value|data|secret|content|string)"\s*:\s*"(?P<v>[^"\\\n]{2,})')


def _block_scalar(text, name_start, ind_end):
    ls = text.rfind("\n", 0, name_start) + 1
    base = len(text[ls:name_start]) - len(text[ls:name_start].lstrip())
    pos = ind_end + 1
    first = last = None
    while pos < len(text):
        nl = text.find("\n", pos)
        e = len(text) if nl < 0 else nl
        ln = text[pos:e]
        if ln.strip():
            if len(ln) - len(ln.lstrip()) <= base:
                break
            if first is None:
                first = pos + len(ln) - len(ln.lstrip())
            last = pos + len(ln.rstrip())
        pos = e + 1
    return (first, last) if first is not None else None


def _json_str_end(text, i):
    k = i
    n = len(text)
    while k < n:
        ch = text[k]
        if ch == "\\":
            k += 2
            continue
        if ch == '"' or ch == "\n":
            break
        k += 1
    return min(k, n) if k < n and text[k] == '"' else i


def _scan_names(text, spans, ctx=0):
    for m in NAME_RE.finditer(text):
        name = m.group("name")
        if re.search(r"(?i)(?<![A-Za-z0-9])public[ \t_\-]*$", text[max(0, m.start() - 10):m.start()]):
            continue
        if m.start() >= 3 and text.startswith("://", m.start() - 3):
            continue
        if m.group("sep") == ":" and GREP_LN.match(text, m.end()):
            continue
        cls = classify(name)
        if not cls:
            if (ctx or _is_dsn_name(name)) and _ctx_name_ok(name, m, text):
                sp = _value_span(text, m.end(), m.start(), 0)
                if sp and ctx_secretish(text[sp[0]:sp[1]]) and not _has_userinfo(text, sp):
                    spans.append(sp)
            continue
        if m.group("q") == '"' and not m.group("q2") and m.group("sep") == "=" and not re.match(r"[ \t]*\\?[\"']", text[m.end():m.end() + 8]):
            e = _json_str_end(text, m.end())
            if e > m.end() and not benign(text[m.end():e]) and not _has_userinfo(text, (m.end(), e)):
                spans.append((m.end(), e))
                if cls == 1:
                    _strong.append((m.end(), e))
                continue
        sp = _value_span(text, m.end(), m.start(), cls)
        if sp and re.fullmatch(r"(?:%[-\d.]*[sdiuxXoqfv]|\\?n)+", text[sp[0]:sp[1]]):
            continue
        if sp and cls == 1:
            _strong.append(sp)
        if sp and re.fullmatch(r"[|>][+-]?\d?", text[sp[0]:sp[1]]) and text[sp[1]:sp[1] + 1] in ("\n", ""):
            blk = _block_scalar(text, m.start(), sp[1])
            if blk:
                spans.append(blk)
            continue
        if sp and not _has_userinfo(text, sp):
            spans.append(sp)
    for m in NESTED_JSON.finditer(text):
        if classify(m.group("n")) == 1:
            spans.append((m.start("v"), m.end("v")))
    for m in PAIR_RE.finditer(text):
        cls = classify(m.group("n"))
        if cls != 1 and not (m.group("n").lower() in COOKIE_NAMES and "cookie" in text[max(0, m.start() - 400):m.start()].lower()):
            continue
        sp = _value_span(text, m.end(), m.start(), 1)
        if sp:
            spans.append(sp)


SPACED_SECRET = re.compile(r"(?i)(?<![\w.\-])(?P<n>token|password|passwd|secret|pwd|apikey|api[ \t]+key|credentials?)[ \t]+(?P<v>[^\s'\"=`<>|;&,]{6,})")


def _scan_spaced(text, spans):
    for m in SPACED_SECRET.finditer(text):
        if ctx_secretish(m.group("v")) and not benign(m.group("v")):
            spans.append(m.span("v"))


def _scan_flags(text, spans):
    if "-" not in text:
        return
    for m in FLAG_RE.finditer(text):
        name = m.group("name") or m.group("name1")
        cls = classify(name)
        if not cls or text.startswith("-", m.end()):
            continue
        sp = _value_span(text, m.end(), m.start(), cls)
        if sp:
            spans.append(sp)
    for m in CURL_U.finditer(text):
        v = m.group("pw")
        if not benign(v):
            spans.append((m.start("pw"), m.end("pw")))
    for m in SHORT_PW.finditer(text):
        ls = text.rfind("\n", 0, m.start()) + 1
        if re.search(r"\b(?:mysql|mysqld|mysqldump|mysqladmin|mariadb|mariadbd|mongo|mongosh|redis-cli|psql)\b", text[ls:m.start()]):
            if not benign(m.group("v")) and len(m.group("v")) > 1:
                spans.append((m.start("v"), m.end("v")))
    for m in SHORT_PW_SP.finditer(text):
        ls = text.rfind("\n", 0, m.start()) + 1
        if re.search(r"\b(?:mysql|mysqld|mysqldump|mysqladmin|mariadb|mariadbd|mongo|mongosh|redis-cli|psql)\b", text[ls:m.start()]):
            if not benign(m.group("v")) and looks_random(m.group("v")):
                spans.append((m.start("v"), m.end("v")))


def _scan_cmd_pairs(text, spans):
    for m in CMD_PAIR.finditer(text):
        if classify(m.group("n")) == 1 and looks_random(m.group("v")) and not benign(m.group("v")):
            spans.append((m.start("v"), m.end("v")))


def _scan_urls(text, spans):
    if "://" not in text:
        return
    for m in URL_USERINFO.finditer(text):
        pw = m.group("pw")
        if benign(pw) or pw.startswith("$"):
            continue
        spans.append((m.start("pw"), m.end("pw")))
    for m in URL_USER_ONLY.finditer(text):
        pw = m.group("pw")
        if looks_random(pw) or len(pw) >= 24:
            spans.append((m.start("pw"), m.end("pw")))


def _scan_pem(text, spans):
    if "PRIVATE" not in text and "private" not in text:
        return
    for m in PEM_BEGIN.finditer(text):
        nm = PEM_ASSIGN_NAME.search(text, max(0, m.start() - 200), m.start())
        if nm:
            spans.append(nm.span(1))
        e = PEM_END.search(text, m.end())
        if e and e.start() - m.end() < 400000:
            spans.append((m.end(), e.start()))
            continue
        spans.append((m.end(), min(len(text), m.end() + 400000)))
    for e in PEM_END.finditer(text):
        a = max(0, e.start() - 4000)
        hdr = [h.end() for h in PEM_BEGIN.finditer(text, a, e.start())]
        if hdr:
            continue
        ls = text.rfind("\n", 0, e.start()) + 1
        b = e.start()
        while ls > a:
            prev = text.rfind("\n", 0, ls - 1) + 1
            if not re.fullmatch(r"[A-Za-z0-9+/=\s]*", text[prev:ls]):
                break
            ls = prev
        if b - ls > 40:
            spans.append((ls, b))
    for m in PEM_BARE_HDR.finditer(text):
        spans.append(m.span("v"))
    if "b3BlbnNzaC1rZXk" in text:
        for m in re.finditer(r"b3BlbnNzaC1rZXk[A-Za-z0-9+/=\s\\n]{20,}", text):
            spans.append((m.start(), m.end()))


PUBLISHED_SAMPLES = frozenset(['1a5d44a2dca19669d72edf4c4f1c27c4c1ca4b4408fbb17f6ce4ad452d78ddb3', '78314b11be2e581549ac1c4f616563fad3fdf0c3b71678f6e2299182080e0598'])


COLUMN_ROW = re.compile(r"(?m)^[ \t]*(?P<n>[A-Za-z_][\w.\-]{2,100})(?:[ \t]{2,}|\t)(?P<v>[^\s|]{6,})(?:[ \t]{2,}[^\s|]+)*[ \t]*\r?$")


def _scan_columns(text, spans):
    for m in COLUMN_ROW.finditer(text):
        if classify(m.group("n")) != 1:
            continue
        if re.fullmatch(r"[a-z]+(?:_[a-z]+)+", m.group("v")):
            continue
        if not benign(m.group("v")):
            spans.append(m.span("v"))


def _scan_tokens(text, spans):
    for m in TOKEN_RE.finditer(text):
        if hashlib.sha256(m.group().encode()).hexdigest() in PUBLISHED_SAMPLES or benign(m.group()):
            continue
        spans.append(m.span())
    for m in BEARER.finditer(text):
        v = m.group("v")
        if benign(v):
            continue
        if re.search(r"\d", v) or len(v) >= 20:
            if SCHEME_RE.fullmatch(v):
                continue
            spans.append((m.start("v"), m.end("v")))


XML_EL = re.compile(r"<(?P<n>[A-Za-z_][\w.\-]*)(?:\s[^<>]*)?>(?P<v>[^<>]{4,})</(?P=n)>")
PLIST_KV = re.compile(r"<key>(?P<n>[^<]+)</key>(?:\s|\\[nrt])*<string>(?P<v>[^<]*)</string>")
NETRC_PW = re.compile(r"(?i)\b(?:machine|login|account|default)\b[^\n]*?\bpassword[ \t]+(?P<v>[^\s=:]\S*)|(?m:^[ \t]+password[ \t]+(?P<v2>[^\s=:]\S*))")
ERL_TUPLE = re.compile(r'\{\s*(?:<<)?"(?P<n>[\w.\-]{3,80})"(?:>>)?\s*,\s*(?:<<)?"(?P<v>[^"\n]{4,})"(?:>>)?\s*\}')
SESSION_KV = re.compile(r"(?i)(?<![\w.\-])(?:sessionid|session_id|session|phpsessid|jsessionid|connect\.sid|sid)=(?P<v>[^;\s\"'&]{6,})")
PGPASS = re.compile(r"(?m)^(?:[\w.\-*]+|\*):(?:\d+|\*):(?:[\w.\-*]+):(?:[\w.\-*]+):(?P<v>[^\s:]{4,})$")
GROOVY_PW = re.compile(r"(?i)\b(?P<n>\w*(?:password|passwd|secret|token|apikey)\w*)[ \t]+(?P<q>['\"])(?P<v>[^'\"\n]{4,})(?P=q)")
BUNDLE_URL = re.compile(r"(?m)^(?P<k>BUNDLE_[A-Z0-9_]+)[ \t]*:[ \t]*[\"']?(?P<u>[^:\s\"']+):(?!//)(?P<v>[^\s\"']+)[\"']?[ \t]*$")
PPK_LINES = re.compile(r"(?mi)^Private-Lines:[ \t]*(?P<n>\d+)[ \t]*\r?\n")
QUERY_SECRET = re.compile(r"(?i)[?&;](?:sig|signature|code|x-amz-signature|x-amz-security-token|access_token|token|key|api_key|apikey|client_secret|refresh_token|id_token)=(?P<v>[^&\s\"'<>#]{6,})")
SLACK_HOOK = re.compile(r"hooks\.slack\.com/services/[A-Z0-9]+/[A-Z0-9]+/(?P<v>[A-Za-z0-9_\-]{12,})")
WG_KEY = re.compile(r"(?im)^[ \t]*(?:PresharedKey|PrivateKey)[ \t]*=[ \t]*(?P<v>[^\s]{12,})")
COOKIE_JS = re.compile(r"(?i)document\.cookie[ \t]*=[ \t]*[\"']?[\w.\-]+=(?P<v>[^;\"'\s]{4,})")


def _scan_forms(text, spans):
    if "<" in text:
        for m in XML_EL.finditer(text):
            if m.group("n").lower() != "key" and classify(m.group("n")) and not benign(m.group("v").strip()):
                spans.append((m.start("v"), m.end("v")))
        for m in PLIST_KV.finditer(text):
            if classify(m.group("n")) and not benign(m.group("v").strip()):
                spans.append((m.start("v"), m.end("v")))
    if "password" in text.lower():
        for m in NETRC_PW.finditer(text):
            g = "v" if m.group("v") else "v2"
            v = m.group(g)
            if v and not benign(v):
                spans.append((m.start(g), m.end(g)))
    if text.count(":") >= 4:
        for m in PGPASS.finditer(text):
            spans.append((m.start("v"), m.end("v")))
    for m in GROOVY_PW.finditer(text):
        if classify(m.group("n")) and not benign(m.group("v")):
            spans.append((m.start("v"), m.end("v")))
    if "BUNDLE_" in text:
        for m in BUNDLE_URL.finditer(text):
            if not benign(m.group("v")):
                spans.append((m.start("v"), m.end("v")))
    if "Private-Lines" in text or "private-lines" in text:
        for m in PPK_LINES.finditer(text):
            pos = m.end()
            for _ in range(int(m.group("n"))):
                nl = text.find("\n", pos)
                if nl < 0:
                    nl = len(text)
                ln = text[pos:nl].rstrip("\r")
                if ln:
                    spans.append((pos, pos + len(ln)))
                pos = nl + 1
    if "=" in text:
        for m in QUERY_SECRET.finditer(text):
            if not benign(m.group("v")):
                spans.append((m.start("v"), m.end("v")))
        for m in WG_KEY.finditer(text):
            spans.append((m.start("v"), m.end("v")))
    if "slack.com" in text:
        for m in SLACK_HOOK.finditer(text):
            spans.append((m.start("v"), m.end("v")))
    if "{" in text:
        for m in ERL_TUPLE.finditer(text):
            if classify(m.group("n")) == 1 and not benign(m.group("v")):
                spans.append((m.start("v"), m.end("v")))
    if "=" in text:
        for m in SESSION_KV.finditer(text):
            if not benign(m.group("v")):
                spans.append((m.start("v"), m.end("v")))
    if "document.cookie" in text:
        for m in COOKIE_JS.finditer(text):
            spans.append((m.start("v"), m.end("v")))


_strong = []


ASSIGN = re.compile(r"^[ \t]*(?:export[ \t]+)?(?P<n>[A-Z][A-Z0-9_]{2,})=(?P<v>[^\s\"'`]{12,})", re.M)


def _scan_assigns(text, spans):
    for m in ASSIGN.finditer(text):
        n, v = m.group("n"), m.group("v")
        if classify(n) or any(w.lower() in PUBLIC_WORDS for w in words(n)):
            continue
        if re.fullmatch(r"[A-Za-z0-9_+/=]+", v) and looks_random(v) and not benign(v):
            spans.append((m.start("v"), m.end("v")))


INLINE_ENV = re.compile(r"(?:^|(?<=[\s;|&]))(?:export[ \t]+)?(?P<n>[A-Za-z_][\w.\-]{2,})=(?P<v>[^\s\"'`;|&]{6,})")


def _scan_inline_env(text, spans):
    for m in INLINE_ENV.finditer(text):
        v = m.group("v")
        n = m.group("n")
        if n.lower() in CTX_KEEP_NAMES or any(w.lower() in PUBLIC_WORDS for w in words(n)):
            continue
        if ctx_secretish(v) and not benign(v):
            spans.append(m.span("v"))


_DOC_SEP = re.compile(r"(?m)^(?:---|\.\.\.)(?:[ \t].*)?$")
_K8S_KEY = re.compile(r"(?m)^(?P<pre>[ \t]*(?:-[ \t]+)*)(?P<k>[\"']?(?:data|stringData)[\"']?)[ \t]*:")
_K8S_KIND = re.compile(r"(?m)^(?P<pre>[ \t]*(?:-[ \t]+)*)[\"']?kind[\"']?[ \t]*:[ \t]*[\"']?Secret[\"']?[ \t]*(?:#[^\n]*)?$")
_YAML_ITEM = re.compile(r"(?:-[ \t]+)?(?:[\"'][^\"'\n]*[\"']|[^\s#\"'][^:\n]*?)[ \t]*:(?:[ \t]+|$)")
_BLOCK_IND = re.compile(r"[|>][-+0-9]*(?:[ \t]+#.*)?$")
_JSON_TOK = re.compile(r'"(?:[^"\\\n]|\\.)*"|[{}]')
_JSON_DATA = re.compile(r'"(?:data|stringData)"[ \t\r\n]*:[ \t\r\n]*\{')
_JSON_KIND = re.compile(r'"kind"[ \t\r\n]*:[ \t\r\n]*"Secret"')
_JSON_COLON = re.compile(r'[ \t\r\n]*:')


def _k8s_yaml_block(text, colon, col, spans):
    """Mark every value under a data key at column col; key names stay visible."""
    le = text.find("\n", colon)
    le = len(text) if le < 0 else le
    rest = text[colon + 1:le]
    val = rest.strip()
    block = None
    if val and not val.startswith("#") and val not in ("{}", "[]"):
        if _BLOCK_IND.match(val):
            block = col
        else:
            vs = colon + 1 + len(rest) - len(rest.lstrip())
            spans.append((vs, vs + len(val)))
    pos = le + 1
    while pos < len(text):
        nl = text.find("\n", pos)
        e = len(text) if nl < 0 else nl
        ln = text[pos:e]
        body = ln.lstrip(" \t")
        ind = len(ln) - len(body)
        if body.strip():
            if ind <= col:
                break
            off = pos + ind
            end_body = pos + len(ln.rstrip())
            if block is not None and ind > block:
                spans.append((off, end_body))
            else:
                block = None
                if not body.startswith("#"):
                    mm = _YAML_ITEM.match(body)
                    if mm:
                        vs, ve = off + mm.end(), end_body
                        v = text[vs:ve]
                        if _BLOCK_IND.match(v):
                            block = ind
                        elif v:
                            spans.append((vs, ve))
                    elif body.startswith("- "):
                        if body[2:].strip():
                            spans.append((off + 2, end_body))
                    else:
                        spans.append((off, end_body))
        pos = e + 1


def _k8s_yaml(text, spans):
    seps = [m.start() for m in _DOC_SEP.finditer(text)]
    for m in _K8S_KEY.finditer(text):
        col = len(m.group("pre"))
        j = bisect.bisect_right(seps, m.start())
        ds = seps[j - 1] if j > 0 else 0
        de = seps[j] if j < len(seps) else len(text)
        if not any(len(k.group("pre")) == col for k in _K8S_KIND.finditer(text, ds, de)):
            continue
        _k8s_yaml_block(text, text.index(":", m.end("k")), col, spans)


def _k8s_json(text, spans):
    objs = {}
    stack = []
    spans_obj = []
    for t in _JSON_TOK.finditer(text):
        g = t.group()
        if g == "{":
            stack.append(t.start())
        elif g == "}" and stack:
            o = stack.pop()
            objs[o] = t.end()
            spans_obj.append((o, t.end()))
    for m in _JSON_DATA.finditer(text):
        bopen = m.end() - 1
        close = objs.get(bopen)
        if close is None:
            continue
        encl = [o for o in spans_obj if o[0] < m.start() and m.end() <= o[1]]
        if not encl:
            continue
        outer = min(encl, key=lambda o: o[1] - o[0])
        if not _JSON_KIND.search(text, outer[0], outer[1]):
            continue
        for t in _JSON_TOK.finditer(text, bopen, close):
            if t.group().startswith('"') and t.end() - t.start() > 2 and not _JSON_COLON.match(text, t.end()):
                spans.append((t.start() + 1, t.end() - 1))


def _scan_k8s(text, spans):
    if "Secret" not in text or "ata" not in text:
        return
    _k8s_yaml(text, spans)
    if '"kind"' in text:
        _k8s_json(text, spans)


def structural_spans(text, ctx=0):
    del _strong[:]
    spans = []
    _scan_pem(text, spans)
    _scan_tokens(text, spans)
    _scan_urls(text, spans)
    _scan_names(text, spans, ctx)
    _scan_spaced(text, spans)
    _scan_flags(text, spans)
    _scan_cmd_pairs(text, spans)
    _scan_assigns(text, spans)
    _scan_forms(text, spans)
    _scan_columns(text, spans)
    _table_spans(text, spans)
    _scan_k8s(text, spans)
    if ctx:
        _scan_inline_env(text, spans)
    return spans


def merge(spans):
    if not spans:
        return []
    spans = sorted(spans)
    out = [list(spans[0])]
    for s, e in spans[1:]:
        if s <= out[-1][1]:
            if e > out[-1][1]:
                out[-1][1] = e
        else:
            out.append([s, e])
    return out


B64_RUN = re.compile(r"[A-Za-z0-9+/]{16,}={0,2}(?:\r?\n[A-Za-z0-9+/]{16,}={0,2})*")


def _b64_named_spans(scan, spans):
    for m in B64_RUN.finditer(scan):
        body = re.sub(r"\s", "", m.group()).rstrip("=")
        for k in range(4):
            part = body[k:]
            part = part[:len(part) - len(part) % 4]
            if len(part) < 8:
                continue
            dec = base64.b64decode(part).decode("utf-8", "replace")
            if structural_spans(dec):
                spans.append((m.start(), m.end()))
                break


def apply(text, spans):
    spans = merge(spans)
    if not spans:
        return text
    out = []
    pos = 0
    for s, e in spans:
        out.append(text[pos:s])
        out.append(MARK)
        pos = e
    out.append(text[pos:])
    return "".join(out)


# ---------------------------------------------------------------- known values

SQUEEZE = re.compile(
    r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\\[nrt]|[\s\x00-\x08\x0b-\x1f\x7f]|(?m:^[0-7]{7}(?=[ \t]))")
NONHEX = re.compile(r"[^0-9A-Fa-f]+|\\[nrt]|\x1b\[[0-9;?]*[ -/]*[@-~]")


def _view(text, rx, keep_lower=True):
    """Return (view, starts, origs) where view is text with rx matches removed (lowercased)."""
    parts = []
    starts = []
    origs = []
    pos = 0
    sq = 0
    for m in rx.finditer(text):
        if m.start() > pos:
            parts.append(text[pos:m.start()])
            starts.append(sq)
            origs.append(pos)
            sq += m.start() - pos
        pos = m.end()
    if pos < len(text):
        parts.append(text[pos:])
        starts.append(sq)
        origs.append(pos)
    return "".join(parts).lower(), starts, origs


FOLD_ENT = re.compile(r"&(?:amp;)*(?:#\d{1,7}|#[xX][0-9a-fA-F]{1,6}|[A-Za-z][A-Za-z0-9]{1,31});")


def _fold_view(text):
    """One view char per source unit: entities decoded, NFKC applied, Mn and Cf dropped. Returns (view, starts, origs, ends)."""
    units = []
    pos = 0
    for m in FOLD_ENT.finditer(text):
        units.extend((i, i + 1, text[i]) for i in range(pos, m.start()))
        d = m.group()
        for _ in range(4):
            nd = html.unescape(d)
            if nd == d:
                break
            d = nd
        units.append((m.start(), m.end(), d if len(d) == 1 else m.group()))
        pos = m.end()
    units.extend((i, i + 1, text[i]) for i in range(pos, len(text)))
    parts, starts, origs, ends = [], [], [], []
    for i, j, c in units:
        if len(c) == 1 and unicodedata.category(c) in ("Mn", "Cf"):
            continue
        k = unicodedata.normalize("NFKC", c).lower()
        if len(k) != 1:
            k = c.lower() if len(c.lower()) == 1 else c
        starts.append(len(parts))
        origs.append(i)
        ends.append(j)
        parts.append(k)
    return "".join(parts), starts, origs, ends


def _unmap(a, b, starts, origs, text_len, lens):
    k = bisect.bisect_right(starts, a) - 1
    s = origs[k] + (a - starts[k])
    k2 = bisect.bisect_right(starts, b - 1) - 1
    e = origs[k2] + (b - 1 - starts[k2]) + 1
    return s, e


def _sq(s):
    return SQUEEZE.sub("", s).lower()


def _b64_cores(b):
    out = []
    for k in range(3):
        data = b"\0" * k + b
        start = -(-k * 8 // 6)
        for fn in (base64.b64encode, base64.urlsafe_b64encode):
            e = fn(data).decode()
            core = e.rstrip("=")
            if len(data) % 3:
                core = core[:-1]
            core = core[start:]
            if len(core) >= 8:
                out.append(core)
            if k == 0:
                out.append(e)
                out.append(core if False else e.rstrip("="))
    return out


PCT_RUN = re.compile(r"(?:%[0-9A-Fa-f]{2})+")


def _low(s):
    lo = s.lower()
    return lo if len(lo) == len(s) else s


def _pct_view(text):
    """Lowered view with %XX runs decoded. Returns (view, vstarts, ostarts, oends, decoded) for _pct_span."""
    parts, vst, ost, oen, dec = [], [], [], [], []
    vlen = pos = 0
    for m in PCT_RUN.finditer(text):
        if m.start() > pos:
            seg = _low(text[pos:m.start()])
            parts.append(seg)
            vst.append(vlen)
            ost.append(pos)
            oen.append(m.start())
            dec.append(False)
            vlen += len(seg)
        d = _low(urllib.parse.unquote(m.group(), errors="replace"))
        parts.append(d)
        vst.append(vlen)
        ost.append(m.start())
        oen.append(m.end())
        dec.append(True)
        vlen += len(d)
        pos = m.end()
    if pos < len(text):
        seg = _low(text[pos:])
        parts.append(seg)
        vst.append(vlen)
        ost.append(pos)
        oen.append(len(text))
        dec.append(False)
    return "".join(parts), vst, ost, oen, dec


def _pct_span(a, b, vst, ost, oen, dec):
    """Source span of view range [a, b); a decoded run maps to its whole %XX source."""
    k = bisect.bisect_right(vst, a) - 1
    k2 = bisect.bisect_right(vst, b - 1) - 1
    s = ost[k] if dec[k] else ost[k] + (a - vst[k])
    e = oen[k2] if dec[k2] else ost[k2] + (b - 1 - vst[k2]) + 1
    return s, e


def _index(needles):
    """Anchor table over needles: keyed by the first n chars, n = the shortest needle, so no needle is skipped."""
    if not needles:
        return None
    n = min(map(len, needles))
    table = {}
    for nd in needles:
        table.setdefault(nd[:n], []).append(nd)
    return n, table


def _scan(view, idx):
    """(start, needle) for every occurrence of every indexed needle in view, found in one pass over the view."""
    if idx is None:
        return []
    n, table = idx
    get = table.get
    out = []
    for i in range(len(view) - n + 1):
        cands = get(view[i:i + n])
        if cands is not None:
            for nd in cands:
                if view.startswith(nd, i):
                    out.append((i, nd))
    return out


def _json_u_escaped(v, only_punct=False):
    out = []
    for ch in v:
        if only_punct and re.match(r"[A-Za-z0-9]", ch):
            out.append(ch)
            continue
        b = ch.encode("utf-16-be", "surrogatepass")
        out.append("".join("\\u%04x" % int.from_bytes(b[i:i + 2], "big") for i in range(0, len(b), 2)))
    return "".join(out)


def needles_for(v):
    """(plain needles, hex needles, b64 needles) for a secret value, all lowered and squeezed."""
    plain = set()
    hexn = set()
    b64 = set()
    forms = [v, v[::-1], codecs.encode(v, "rot13"), urllib.parse.quote(v, safe=""), urllib.parse.quote_plus(v),
             json.dumps(v, ensure_ascii=True)[1:-1], json.dumps(v, ensure_ascii=False)[1:-1],
             json.dumps(v, ensure_ascii=True)[1:-1].replace("/", "\\/"), _json_u_escaped(v),
             _json_u_escaped(v, only_punct=True),
             html.escape(v, quote=True),
             html.escape(v, quote=True).replace("&#x27;", "&#39;"), html.escape(v, quote=False),
             re.sub(r"([^A-Za-z0-9_])", r"\\\1", v), re.sub(r"([$`\"\\])", r"\\\1", v)]
    for f in forms:
        q = _sq(f)
        if len(q) >= 6:
            plain.add(q)
    for enc in ("utf-8", "utf-16-le", "utf-16-be"):
        try:
            b = v.encode(enc, "surrogatepass")
        except UnicodeError:
            continue
        h = b.hex()
        if len(h) >= 12:
            hexn.add(h)
        for c in _b64_cores(b):
            q = c.lower()
            if len(q) >= 8:
                b64.add(q)
                if len(v) >= 12:
                    for i in range(0, min(len(q) - 11, 80)):
                        b64.add(q[i:i + 12])
    if len(v) >= 8:
        raw = v.encode("utf-8", "surrogatepass")
        for c in _b64_cores(raw[::-1]):
            if len(c) >= 8:
                b64.add(c.lower())
    return plain, hexn, b64


SECRET_FILE_RE = re.compile(
    r"(?:^\.env(?:\..+)?$|^.+\.env$|^\.dev\.vars(?:\..+)?$|^\.npmrc$|^\.netrc$|^_netrc$|^\.pgpass$|^\.git-credentials$|"
    r"^credentials$|^\.my\.cnf$|^config\.json$|^.+\.(?:pem|key|p8|p12|pfx|ppk)$|^id_(?:rsa|dsa|ecdsa|ed25519)(?:_.*)?$|"
    r"^\.pypirc$|^\.s3cfg$|^\.boto$|^auth\.json$|^\.envrc$|^\.yarnrc(?:\.yml)?$|^\.vault-token$|^service-account.*\.json$)")
EXAMPLE_SUFFIX = (".example", ".sample", ".template", ".dist", ".tpl", ".defaults", ".pub")
SKIP_DIRS = {"node_modules", ".git", ".venv", "venv", "__pycache__", ".next", ".turbo", "target", "dist", "build",
             "Pods", "DerivedData", ".cache", ".npm", ".pnpm-store", ".cargo", ".rustup", ".nvm", "Library",
             ".Trash", ".gradle", ".m2", "vendor", ".terraform", ".tox", ".mypy_cache", ".pytest_cache", "coverage",
             "site-packages", ".idea", ".vscode", ".expo", ".yarn", ".bun", ".deno", "Applications", "Pictures",
             "Movies", "Music", "Downloads", "Desktop"}
HOME_SECRET_DIRS = (".ssh", ".aws", ".docker", ".config/gh", ".kube", ".gnupg", ".azure", ".config/gcloud", ".gcloud")


def _is_secret_file(base):
    if not SECRET_FILE_RE.match(base):
        return False
    low = base.lower()
    if low.endswith(EXAMPLE_SUFFIX):
        return False
    if base == "config.json" or base == "credentials":
        return None
    return True


def _home():
    return os.environ.get("SECRET_HOOK_HOME") or os.path.expanduser("~")


def _roots():
    r = os.environ.get("SECRET_HOOK_ROOTS")
    if r is None:
        return [os.path.join(_home(), "Projects")]
    return [p for p in r.split(os.pathsep) if p]


def _walk(root, depth, found, deadline):
    try:
        it = os.scandir(root)
    except OSError:
        return
    with it:
        for ent in it:
            if time.time() > deadline:
                return
            name = ent.name
            try:
                if ent.is_dir(follow_symlinks=False):
                    if name in SKIP_DIRS or depth <= 0:
                        continue
                    _walk(ent.path, depth - 1, found, deadline)
                elif ent.is_file(follow_symlinks=False):
                    ok = _is_secret_file(name)
                    if ok:
                        found.append(ent.path)
                    elif ok is None:
                        parent = os.path.basename(root)
                        if (name == "config.json" and parent == ".docker") or (name == "credentials" and parent == ".aws"):
                            found.append(ent.path)
            except OSError:
                continue


def _cache_path(key):
    h = hashlib.sha256(key.encode("utf-8", "surrogateescape")).hexdigest()[:24]
    return os.path.join(tempfile.gettempdir(), "secret-hooks-%s-%s.json" % (os.getuid() if hasattr(os, "getuid") else 0, h))


HARVEST_DIR = "secret-guard"
HARVEST_NAME = "harvest-cache.json"


def harvest_path():
    return os.path.join(_home(), ".claude", HARVEST_DIR, HARVEST_NAME)


def _load_harvest():
    try:
        with open(harvest_path(), "r", encoding="utf-8") as f:
            c = json.load(f)
        return c if isinstance(c, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_harvest(data):
    p = harvest_path()
    tmp = "%s.%d" % (p, os.getpid())
    try:
        os.makedirs(os.path.dirname(p), mode=0o700, exist_ok=True)
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        os.chmod(tmp, 0o600)
        os.replace(tmp, p)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass


def find_secret_files(cwd=None):
    home = _home()
    roots = _roots()
    key = "\0".join([home] + roots)
    cp = _cache_path(key)
    now = time.time()
    files = None
    try:
        with open(cp, "r", encoding="utf-8") as f:
            c = json.load(f)
        if now - c.get("t", 0) < 10 and c.get("key") == key:
            files = [p for p in c["files"] if os.path.exists(p)]
    except (OSError, ValueError, KeyError, TypeError):
        files = None
    if files is None:
        files = []
        deadline = now + 2.0
        for d in HOME_SECRET_DIRS:
            _walk(os.path.join(home, d), 2, files, deadline)
        for r in roots:
            _walk(r, 7, files, deadline)
        try:
            tmp = cp + ".%d" % os.getpid()
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump({"t": now, "key": key, "files": files}, f)
            os.replace(tmp, cp)
        except OSError:
            pass
    fresh = []
    deadline = time.time() + 1.0
    try:
        for ent in os.scandir(home):
            if ent.is_file(follow_symlinks=False) and _is_secret_file(ent.name) and ent.name != "config.json":
                fresh.append(ent.path)
    except OSError:
        pass
    if cwd and os.path.isdir(cwd):
        _walk(cwd, 3, fresh, deadline)
    hp = harvest_path()
    if os.path.isfile(hp):
        fresh.append(hp)
    out = []
    seen = set()
    for p in files + fresh:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _public_secret(name):
    ws = [w.lower() for w in words(name)]
    return ws[-1] in ("pass", "password", "passwd", "pwd", "secret", "passphrase") and any(w in PUBLIC_WORDS for w in ws)


def _secretish(name, value):
    if classify(name) == 0 and _public_secret(name):
        return True
    c = classify(name)
    if c == 1:
        return True
    if c == 2 or c == 0:
        return looks_random(value) and len(value) >= 16 and not re.fullmatch(r"[\w.\-]+/[\w.\-/]+", value)
    return False


def _mixed(v):
    if len(v) < 10 or re.search(r"\s", v) or "://" in v:
        return False
    return sum(bool(re.search(r, v)) for r in (r"[A-Z]", r"[a-z]", r"[0-9]", r"[^\w.\-/:]|_")) >= 3 and bool(re.search(r"[^\w.\-/:]|_", v))


ENV_LINE = re.compile(
    r"(?m)^[ \t]*(?:export[ \t]+)?(?P<k>[A-Za-z_][\w.\-]*)[ \t]*[=:][ \t]*(?:\"(?P<dq>(?:[^\"\\]|\\.)*)\"|'(?P<sq>[^']*)'|(?P<raw>[^\r\n]*))")


def _file_values(path, text):
    vals = []
    base = os.path.basename(path)
    low = base.lower()
    if low.endswith((".pem", ".key", ".p8", ".ppk")) or base.startswith("id_") or "PRIVATE KEY" in text:
        body = []
        for ln in text.splitlines():
            ln = ln.strip()
            if ln and not ln.startswith("-----") and ":" not in ln[:20]:
                body.append(ln)
                if len(ln) >= 16:
                    vals.append(ln)
        if body:
            vals.append("".join(body))
        if low.endswith((".pem", ".key", ".p8", ".ppk", ".p12", ".pfx")) or base.startswith("id_") or body:
            if not any("=" in x[:3] for x in body[:1]):
                pass
    if low == ".netrc" or low == "_netrc":
        for m in re.finditer(r"\bpassword[ \t\r\n]+(\S+)", text):
            vals.append(m.group(1))
        for m in re.finditer(r"\blogin[ \t\r\n]+(\S{16,})", text):
            vals.append(m.group(1))
        return vals
    if low == ".pgpass":
        for ln in text.splitlines():
            parts = ln.split(":")
            if len(parts) >= 5 and not ln.startswith("#"):
                vals.append(":".join(parts[4:]))
        return vals
    if low == ".git-credentials":
        for m in re.finditer(r"://[^:/@\s]*:([^@\s]+)@", text):
            vals.append(m.group(1))
        return vals
    if low.endswith(".json") or text.lstrip().startswith(("{", "[")):
        try:
            _json_values(json.loads(text), "", vals, low == "auth.json")
            return vals
        except ValueError:
            pass
    for m in ENV_LINE.finditer(text):
        k = m.group("k")
        v = m.group("dq")
        if v is None:
            v = m.group("sq")
        if v is None:
            v = m.group("raw")
            v = re.sub(r"\s+#.*$", "", v) if not re.search(r"#\S", v) else v
            v = v.strip()
        if not v or benign_h(v) or (any(w.lower() in PUBLIC_WORDS for w in words(k)) and not _public_secret(k)):
            continue
        if k.startswith("//") or "_auth" in k.lower():
            pass
        if _secretish(k, v) or low.startswith((".env", ".dev.vars", ".npmrc", ".pypirc", ".boto", ".s3cfg")) and (looks_random(v) or _mixed(v)):
            if "://" in v and not URL_USERINFO.search(v):
                us = []
                _scan_forms(v, us)
                _scan_tokens(v, us)
                if us:
                    vals.extend(v[a:b] for a, b in us)
                else:
                    vals.append(v)
            elif "://" not in v:
                vals.append(v)
            if "\\n" in v:
                vals.append(v.replace("\\n", "\n"))
            for um in URL_USERINFO.finditer(v):
                vals.append(um.group("pw"))
    for m in re.finditer(r"//[^\s:=]+/:(_auth\w*|_password)=(\S+)", text):
        vals.append(m.group(2))
    return vals


def _json_values(o, key, out, every=False):
    if isinstance(o, dict):
        for k, v in o.items():
            _json_values(v, str(k), out, every)
    elif isinstance(o, list):
        for v in o:
            _json_values(v, key, out, every)
    elif isinstance(o, str):
        if o and not benign_h(o) and ((every and len(o) >= 6) or classify(key) == 1 or (key.lower() in ("auth", "identitytoken", "registrytoken")) or
                                    (looks_random(o) and len(o) >= 24)):
            out.append(o)


SOURCE_CMD = re.compile(
    r"(?:\bpass\s+show\b|\bkeyctl\s+(?:print|pipe|read)\b|\bsystemd-creds\b|\bsecurity\s+(?:find-|dump-|export)|"
    r"\bop\s+(?:read|item\s+get|inject|document)\b|\bgh\s+auth\s+token\b|\bpbpaste\b|\bvault\s+(?:read|kv\s+get)\b|"
    r"\baws\s+(?:ssm\s+get|secretsmanager\s+get|sts\s+get)|\bgcloud\s+(?:secrets|auth\s+print)|"
    r"\bkubectl\s+(?:get|describe)\s+secrets?\b|\bbw\s+get\b|\bsops\s+(?:-d|--decrypt)\b|\bage\s+(?:-d|--decrypt)\b|"
    r"\bansible-vault\s+(?:view|decrypt)\b|/run/credentials|/proc/[^\s/]*/environ|\bgpg2?\s+(?:-d|--decrypt)\b|"
    r"\bterraform\s+(?:output|show|state\s+show)\b|\bdoppler\s+secrets\b|\binfisical\b|\blpass\s+show\b|"
    r"\bheroku\s+config\b|\bfly(?:ctl)?\s+(?:secrets|ssh\s+console)\b|\bosascript\b|"
    r"\bcredential|\bkeychain\b|\bsecret|\bpassw|\btoken\b|\bactuator/env\b|"
    r"\bdocker\s+(?:inspect|compose\s+config|service\s+inspect)\b|\bprintenv\b|(?:^|[\s;|&(])env(?:\s*$|\s*[|;&)])|"
    r"(?:^|[\s/\"'~=])(?:\.env[\w.\-]*|\.dev\.vars[\w.\-]*|\.npmrc|\.netrc|\.pgpass|id_(?:rsa|ed25519|ecdsa|dsa)\b|"
    r"[\w.\-]+\.(?:pem|key|p8|p12|pfx|ips|crash|dump))(?:[\s\"';|&)]|$))", re.I)
PRINTENV_ARGS = re.compile(r"\bprintenv\s+((?:[A-Za-z_]\w*\s*)+)")
VAR_REF = re.compile(r"\$\{?([A-Za-z_]\w*)")
SECRET_DIR_RE = re.compile(r"(?:/environ$|\.ssh/|\.aws/|\.docker/|\.kube/|\.gnupg/|/credentials?/)", re.I)
SECRET_FILE_NAME_RE = re.compile(r"(?:\.env|\.dev\.vars|\.npmrc|\.netrc|\.pgpass|id_(?:rsa|ed25519|ecdsa|dsa)|\.pem|\.key|\.p8|\.p12|"
                                 r"credential|secret|passw|token|keychain)", re.I)


INJECT_CMD = re.compile(r"(?:^|[\s;|&(])(?:op\s+run|doppler\s+run|dotenvx\s+run)\b|--env-file[=\s]")


def command_ctx(tool, ti):
    if not isinstance(ti, dict):
        return 0
    if tool == "Bash":
        c = ti.get("command")
        if not isinstance(c, str) or not c:
            return 0
        if re.match(r"\s*(?:ls|find|stat|readlink|du|tree|file)\b", c):
            return 0
        if SOURCE_CMD.search(c):
            if re.search(r"\b(?:docker|podman)\s+\S*\s*inspect\b.*(?:-f|--format)\b", c):
                return 0
            pe = PRINTENV_ARGS.search(c)
            if pe and not re.search(r"\bprintenv\s*(?:$|[|;&])", c) and not SOURCE_CMD.search(c[:pe.start()] + c[pe.end():]):
                return 1 if any(classify(n) for n in pe.group(1).split()) else 0
            return 1
        if INJECT_CMD.search(c):
            return 1
        for m in VAR_REF.finditer(c):
            if classify(m.group(1)) == 1:
                return 1
        return 0
    if tool in ("Read", "Grep", "Glob", "NotebookRead"):
        p = ti.get("file_path") or ti.get("path") or ""
        return 1 if isinstance(p, str) and (SECRET_DIR_RE.search(p) or SECRET_FILE_NAME_RE.search(re.split(r"[/\\]", p)[-1])) else 0
    return 0


# Only transforms that obscure a value from the redactor: encoders and byte or char dumps. Decoders and display stay R1.
TRANSFORM_CMD = re.compile(
    r"(?:^|[\s;|&(])(?:od|hexdump|uuencode)(?=[\s;|&)]|$)"
    r"|(?:^|[\s;|&(])cmp\b[^|;&]*\s-\w*l"
    r"|(?:^|[\s;|&(])fold\b[^|;&]*-(?:w\s*)?1(?!\d)"
    r"|(?:^|[\s;|&(])(?:xxd|base64|base32|basenc)\b(?![^|;&]*\s(?:-r|-d|-D|--decode|--reverse)(?=[\s;|&)\"'`]|$))"
    r"|\bbtoa\(|b64encode|encodebytes|hexlify|b2a_hex|b2a_uu|b2a_base64|encode_base64|"
    r"toString\(\s*['\"](?:base64|hex)", re.M)
JS_TRANSFORM = re.compile(r"btoa|atob|charCodeAt|codePointAt|fromCharCode|toString\(|encodeURI|escape\(|JSON\.stringify|"
                          r"\.split\(|\.reverse\(|\.join\(|Array\.from|TextEncoder|\.slice\(|\.substr|\.map\(|\.replace\(")
SCREEN_CMD = re.compile(r"\bosascript\b.*\bvalue of\b", re.S)
JS_STORE = re.compile(r"localStorage|sessionStorage|document\.cookie")
IDENT_RE = re.compile(r"[A-Za-z_]\w*")


def withhold_ctx(tool, ti):
    """True when a command or script reads a secret source through a transform; its whole output is withheld."""
    if not isinstance(ti, dict) or not isinstance(tool, str):
        return False
    if tool == "Bash":
        c = ti.get("command")
        if isinstance(c, str) and SCREEN_CMD.search(c):
            return True
        return isinstance(c, str) and bool(TRANSFORM_CMD.search(c)) and command_ctx(tool, ti) == 1
    if "javascript" in tool or "evaluate_script" in tool:
        for v in ti.values():
            if isinstance(v, str) and JS_TRANSFORM.search(v) and (
                    JS_STORE.search(v) or any(classify(n) == 1 for n in IDENT_RE.findall(v))):
                return True
    return False


def marked_like(o, key=None):
    if isinstance(o, str):
        return o if key in CTX_SKIP_KEYS or not o else MARK
    if isinstance(o, list):
        return [marked_like(x, key) for x in o]
    if isinstance(o, dict):
        return {k: marked_like(v, k) for k, v in o.items()}
    return o


BARE_LINE =re.compile(r"(?:^|(?<=\n)|(?<=\\n)|(?<=\r))[ \t]*(?P<t>[^\s\\\"'<>=,;{}\[\]()#]{6,})[ \t]*(?=\r|\n|\\n|\\r|$)")
HARMLESS_BARE = frozenset(["production", "development", "staging", "localhost", "undefined", "installed", "enabled",
                           "disabled", "unknown", "running", "healthy", "unhealthy", "starting", "stopped"])


def _bare_spans(text):
    out = []
    for m in BARE_LINE.finditer(text):
        t = m.group("t")
        if t.startswith(("/", "~", ".", "-", "[", "http://", "https://")) or t.endswith(":"):
            continue
        if "/" in t and len(t) < 40 or "://" in t or "@" in t and "." in t.split("@")[-1]:
            continue
        if re.fullmatch(r"[a-z0-9][a-z0-9_\-]*(?:\.[a-z0-9_\-]+)+", t):
            continue
        if benign(t) or t == MARK or t.lower() in HARMLESS_BARE or t.isdigit():
            continue
        if t.isalpha() and t.islower() and len(t) <= 12:
            continue
        if re.fullmatch(r"\d[\d.:\-T+Z]*", t):
            continue
        out.append((m.start("t"), m.end("t")))
    return out


FLIP_LINE = re.compile(r"(?m)^[ \t]*(?P<l>[^\s=\"'<>]{6,200})=(?P<r>[^\s=\"'<>]{6,200})[ \t]*$")
IDENT = re.compile(r"[A-Za-z_][\w.\-]*")


def _flip_secretish(s):
    """True when a reversed or rot13 form of s reads as a secret-ish identifier."""
    for dec in (s[::-1], codecs.encode(s, "rot13")):
        if IDENT.fullmatch(dec) and classify(dec) == 1:
            return True
    return False


def _flipped_lines(text, spans):
    """Whole-line span for `A=B` where a known value is redacted and one side is a reversed or rot13 secret name."""
    merged = merge(spans)
    ends = [e for _, e in merged]
    out = []
    pos = 0
    for line in text.split("\n"):
        start = pos
        pos += len(line) + 1
        m = FLIP_LINE.match(line)
        if not m:
            continue
        i = bisect.bisect_right(ends, start)
        if i == len(merged) or merged[i][0] >= start + len(line):
            continue
        if _flip_secretish(m.group("l")) or _flip_secretish(m.group("r")):
            out.append((start + m.start(), start + m.end()))
    return out


def _masked(v):
    m = re.match(r"(?i)(?:bearer|basic|token|digest|negotiate|api-?key)[ \t]+(?=\S)", v)
    if m and not benign(v[m.end():]):
        return v[:m.end()] + MARK
    return MARK


FOLD = {0x200b: "_", 0x200c: "_", 0x200d: "_", 0x2060: "_", 0xfeff: "_", 0xad: "_"}
for _a, _b in zip("АВЕКМНОРСТХаеорсхуіѕ", "ABEKMHOPCTXaeopcxyis"):
    FOLD[ord(_a)] = _b


WRAP_TOK = re.compile(r"[^\s=:\"'&<>\[\]{}()|,;/\\\-][^\s=:\"'&<>\[\]{}()|,;/\\]*")


ADJ_CHUNK = re.compile(r"[ \t]+([\"'])([^\"'\n]*)\1")


def _wrap_spans(text, spans):
    out = []
    for a, b in spans:
        if b < len(text) and text[b] in "\"'":
            m = ADJ_CHUNK.match(text, b + 1)
            if m and m.end(2) > m.start(2):
                out.append((m.start(2), m.end(2)))
            continue
        if b >= len(text) or text[b] != "\n" or b - a < 2 or text[b - 1] in " \t" or "\n" in text[a:b]:
            continue
        m = WRAP_TOK.match(text, b + 1)
        if not m:
            continue
        t = m.group()
        e = m.end()
        if e < len(text) and text[e] not in " \t\r\n&":
            continue
        if not (re.search(r"[A-Za-z]", t) and re.search(r"[0-9#@_$%!]", t)) or MARK in t or re.match(r"\d{2,4}[-:/.]\d", t):
            continue
        if not (text[b - 1] in "_-@#$%!+/=" or re.search(r"[@#$%!]", text[a:b])) or re.match(r"[ \t]*[=:+?]", text[e:]):
            continue
        out.append((m.start(), e))
    return out


HINT_TOKEN = re.compile(r"[^\s\"'<>=:,;|&()\[\]{}`\\]{12,}")
HINT_NAME_AFTER = re.compile(r"=|:\d+[:-]")
HINT_GREP_PREFIX = re.compile(r"[^\s:]+?[-:]\d+[-:]")


def grep_hint_words(tool, ti):
    """Words of a Grep content search that names credentials; empty for any other call."""
    if tool != "Grep" or not isinstance(ti, dict) or ti.get("output_mode") != "content":
        return ()
    pat = ti.get("pattern")
    return tuple(re.findall(r"[a-z]{4,}", pat.lower())) if isinstance(pat, str) else ()


def _hint_spans(text, words):
    if not words:
        return []
    spans = []
    for m in HINT_TOKEN.finditer(text):
        if HINT_NAME_AFTER.match(text, m.end()):
            continue
        tok, start = m.group(), m.start()
        pre = HINT_GREP_PREFIX.match(tok)
        if pre:
            tok, start = tok[pre.end():], start + pre.end()
        if len(tok) >= 12 and any(w in tok.lower() for w in words) and looks_random(tok) and not benign(tok):
            spans.append((start, start + len(tok)))
    return spans


class Engine:
    def __init__(self, cwd=None, harvest=True):
        self.cwd = cwd
        self.grep_words = ()
        self._values = None
        self._needles = None
        self._idx = None
        self._blob = None
        self.harvest = harvest
        self.learned = set()
        self.deadline = None
        self.overrun = None

    def known_values(self):
        if self._values is None:
            vals = set()
            if self.harvest:
                cache = _load_harvest()
                fresh = {}
                hp = harvest_path()
                for p in find_secret_files(self.cwd):
                    if p == hp:
                        # The cache is a secret source, but its own text churns on every save: union its stored values.
                        for e in cache.values():
                            if isinstance(e, dict) and isinstance(e.get("v"), list):
                                vals.update(x for x in e["v"] if isinstance(x, str))
                        continue
                    try:
                        st = os.stat(p)
                        if st.st_size > 2_000_000:
                            continue
                        ent = cache.get(p)
                        if ent and ent.get("m") == st.st_mtime_ns and ent.get("s") == st.st_size:
                            fresh[p] = ent
                            vals.update(ent["v"])
                            continue
                        with open(p, "r", encoding="utf-8", errors="replace") as f:
                            text = f.read()
                    except OSError:
                        continue
                    got = []
                    for v in _file_values(p, text):
                        v = v.strip()
                        if len(v) >= 6 and not benign_h(v) and not v.startswith(MARK):
                            got.append(v)
                    vals.update(got)
                    fresh[p] = {"m": st.st_mtime_ns, "s": st.st_size, "v": got}
                if fresh != cache:
                    _save_harvest(fresh)
            self._values = sorted(vals, key=lambda x: (-len(x), x))
        return self._values

    def needles(self):
        if self._needles is None:
            plain, hexn, b64 = set(), set(), set()
            for v in self.known_values():
                p, h, b = needles_for(v)
                plain |= p
                hexn |= h
                b64 |= b
            self._needles = (sorted(plain), sorted(hexn), sorted(b64))
            self._idx = (_index(plain), _index(hexn), _index(b64))
        return self._needles

    def fragments(self, text, ctx):
        if self._blob is None:
            self._blob = "\x00".join(self.known_values())
        blob = self._blob
        out = []
        if not blob:
            return out
        seen = {}
        for m in re.finditer(r"[^\s\"'<>]+", text):
            t = m.group().strip(",;:()[]{}")
            t = re.sub(r"^(?:\\[0-7]{3}|\\x[0-9a-fA-F]{2})+", "", t)
            if len(t) < 4 or MARK in t or t.endswith(("_", "-")):
                continue
            if len(t) < 8 and not (ctx and not t.islower() and not t.isdigit()):
                continue
            if len(t) >= 8 and not re.search(r"[0-9_\-]|[a-z][A-Z]", t):
                continue
            hit = seen.get(t)
            if hit is None:
                hit = seen[t] = t in blob
                if len(seen) > 20000:
                    break
            if hit:
                a = m.start() + m.group().find(t)
                out.append((a, a + len(t)))
        return out

    def known_spans(self, text, encoded=True):
        plain, hexn, b64 = self.needles()
        if not encoded:
            hexn, b64 = (), ()
        if not (plain or hexn or b64):
            return []
        p_idx, h_idx, b_idx = self._idx
        if not encoded:
            h_idx = b_idx = None
        spans = []
        sq, starts, origs = _view(text, SQUEEZE)
        if sq and starts:
            for p, nd in _scan(sq, p_idx):
                spans.append(_unmap(p, p + len(nd), starts, origs, len(text), None))
            for p, nd in _scan(sq, b_idx):
                s, e = _unmap(p, p + len(nd), starts, origs, len(text), None)
                while s > 0 and text[s - 1] in B64CH:
                    s -= 1
                while e < len(text) and text[e] in B64CH:
                    e += 1
                spans.append((s, e))
        if plain and (not text.isascii() or "&" in text ):
            fv, fs, fo, fe = _fold_view(text)
            for p, nd in _scan(fv, p_idx):
                spans.append((fo[p], fe[p + len(nd) - 1]))
        if plain and "%" in text:
            pv, vst, ost, oen, dec = _pct_view(text)
            for p, nd in _scan(pv, p_idx):
                spans.append(_pct_span(p, p + len(nd), vst, ost, oen, dec))
        if hexn:
            hv, hs, ho = _view(text, NONHEX)
            if hv and hs:
                for p, nd in _scan(hv, h_idx):
                    spans.append(_unmap(p, p + len(nd), hs, ho, len(text), None))
        return spans

    def redact_text(self, text, ctx=0):
        if not text or len(text) < 3:
            return text
        parts, pos = [], 0
        while pos < len(text):
            if self.deadline is not None and time.monotonic() > self.deadline:
                # Fail-closed: the scanned prefix is kept, the unscanned rest is withheld.
                self.overrun = OVERRUN_REASON
                tail = WITHHELD % OVERRUN_REASON
                parts.append(tail if not parts or parts[-1].endswith("\n") else "\n" + tail)
                break
            end = _chunk_end(text, pos)
            parts.append(self._redact_whole(text[pos:end], ctx))
            pos = end
        return "".join(parts)

    def _redact_whole(self, text, ctx=0):
        if not text or len(text) < 3:
            return text
        scan = text.replace("\x00", "\n") if "\x00" in text else text
        if not scan.isascii():
            scan = scan.translate(FOLD)
        spans = structural_spans(scan, ctx)
        spans += _wrap_spans(scan, spans)
        self._learn_spans(scan, spans)
        _b64_named_spans(scan, spans)
        for v in self.learned:
            i = text.find(v)
            while i >= 0:
                spans.append((i, i + len(v)))
                i = text.find(v, i + len(v))
        spans += self.known_spans(text)
        spans += self.fragments(text, ctx)
        spans += _hint_spans(scan, self.grep_words)
        spans += _flipped_lines(text, spans)
        if ctx:
            st = merge(spans)
            spans += [b for b in _bare_spans(scan) if not any(x[0] < b[1] and b[0] < x[1] for x in st)]
        return apply(text, spans)

    def has_secret(self, text):
        return bool(structural_spans(text) or self.known_spans(text))

    def _learn_spans(self, scan, spans):
        strong = set(_strong)
        for x in spans:
            v = scan[x[0]:x[1]]
            if (looks_random(v) or (x in strong and len(v) >= 8)) and len(v) < 200 and not v.startswith("[") and "\n" not in v:
                self.learned.add(v)

    def _learn_obj(self, o, key, ctx, leaves):
        if isinstance(o, str):
            leaves.append((o, 0 if key in CTX_SKIP_KEYS else ctx))
        elif isinstance(o, list):
            for x in o:
                self._learn_obj(x, key, ctx, leaves)
        elif isinstance(o, dict):
            for k, v in o.items():
                self._learn_obj(v, k if isinstance(k, str) else str(k), ctx, leaves)

    def _split_withheld(self, o):
        """A known value cut between stdout and stderr is withheld from both fields."""
        if not (isinstance(o, dict) and isinstance(o.get("stdout"), str) and isinstance(o.get("stderr"), str)):
            return o
        out, err = o["stdout"], o["stderr"]
        if not (out and err):
            return o
        if any(s < len(out) < e for s, e in self.known_spans(out + err)):
            return dict(o, stdout=MARK, stderr=MARK)
        return o

    def redact_obj(self, o, key=None, secret_ctx=False, ctx=0):
        o = self._split_withheld(o)
        # Learn values from every string first, so a value seen in one field (file content) is hidden in another (its path).
        leaves = []
        self._learn_obj(o, key, ctx, leaves)
        if len([s for s, _ in leaves if len(s) >= 3]) > 1:
            for s, c in leaves:
                if len(s) >= 3:
                    scan = s.replace("\x00", "\n") if "\x00" in s else s
                    if not scan.isascii():
                        scan = scan.translate(FOLD)
                    spans = structural_spans(scan, c)
                    spans += _wrap_spans(scan, spans)
                    self._learn_spans(scan, spans)
        return self._redact_obj(o, key, secret_ctx, ctx)

    def _redact_obj(self, o, key=None, secret_ctx=False, ctx=0):
        if isinstance(o, str):
            if secret_ctx and not benign(o):
                return _masked(o)
            return self.redact_text(o, 0 if key in CTX_SKIP_KEYS else ctx)
        if isinstance(o, list):
            return [self._redact_obj(x, key, secret_ctx, ctx) for x in o]
        if isinstance(o, dict):
            out = {}
            nv = _pair_secret(o)
            for k, v in o.items():
                ks = k if isinstance(k, str) else str(k)
                sec = secret_ctx or classify(ks) == 1
                if nv and k in nv[1] and nv[0]:
                    sec = True
                if isinstance(v, str):
                    if sec and not benign(v):
                        out[k] = _masked(v)
                    else:
                        out[k] = self.redact_text(v, 0 if ks in CTX_SKIP_KEYS else ctx)
                elif isinstance(v, (dict, list)):
                    out[k] = self._redact_obj(v, ks, sec, ctx)
                else:
                    out[k] = v
            return out
        return o


CTX_SKIP_KEYS = frozenset(["type", "mode", "filePath", "file_path", "path", "command", "filenames", "matches", "interrupted"])
B64CH = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=_-")


def _is_pair_list(o):
    return False


def _pair_secret(d):
    n = None
    for nk in ("name", "Name", "key", "Key", "NAME", "KEY", "field", "Field", "FIELD"):
        if isinstance(d.get(nk), str):
            n = d[nk]
            break
    if n is None:
        return None
    vs = [k for k in d if k in ("value", "Value", "VALUE", "val")]
    if not vs:
        return None
    return (classify(n) == 1 or n.lower() in COOKIE_NAMES, vs)


SHAPE_PH = "[REDACTED: redactor error, output withheld] (WITHHELD)"


def has_surrogate(o):
    if isinstance(o, str):
        return bool(re.search("[\ud800-\udfff]", o))
    if isinstance(o, list):
        return any(has_surrogate(x) for x in o)
    if isinstance(o, dict):
        return any(has_surrogate(k) or has_surrogate(v) for k, v in o.items())
    return False


def odd_shape(tool, resp):
    if tool != "Grep" and has_surrogate(resp):
        return True
    if tool == "Bash":
        if not isinstance(resp, dict) or resp.get("isImage") is True:
            return True
        return "stdout" in resp and not (isinstance(resp["stdout"], str))
    if tool == "Read" and isinstance(resp, dict):
        f = resp.get("file")
        b = f.get("base64") if isinstance(f, dict) else None
        return resp.get("type") == "image" and not (isinstance(b, str) and b.startswith(("iVBORw0KGgo", "/9j/", "R0lGOD", "UklGR")))
    return False


def withhold_shape(o, key=None):
    if isinstance(o, str):
        return o if key in CTX_SKIP_KEYS else SHAPE_PH
    if isinstance(o, list):
        return [withhold_shape(x, key) for x in o]
    if isinstance(o, dict):
        return {k: withhold_shape(v, k) for k, v in o.items()}
    return o


def placeholder_like(o, reason):
    ph = WITHHELD % reason
    if isinstance(o, str):
        return ph
    if isinstance(o, list):
        return [placeholder_like(x, reason) for x in o]
    if isinstance(o, dict):
        return {k: placeholder_like(v, reason) for k, v in o.items()}
    return o


REDACT_BUDGET = 10.0
BACKSTOP = 1.0
OVERRUN_REASON = "redaction time budget exceeded"
CHUNK_BYTES = 64 * 1024
_PEM_OPEN = re.compile(r"-----BEGIN[ \t]+(?:[A-Z0-9]+[ \t]+)*?PRIVATE[ \t]+KEY")
_PEM_END = re.compile(r"-----END[ \t]+(?:[A-Z0-9]+[ \t]+)*?PRIVATE[ \t]+KEY")


def _chunk_end(text, start):
    """End of the next chunk: a line break past CHUNK_BYTES, extended past any private key block it opens."""
    cut = text.find("\n", start + CHUNK_BYTES)
    if cut < 0:
        return len(text)
    cut += 1
    head = text[start:cut]
    begins = [m.start() for m in _PEM_OPEN.finditer(head)]
    if begins and not _PEM_END.search(head, begins[-1]):
        m = _PEM_END.search(text, cut)
        if not m:
            return len(text)
        nl = text.find("\n", m.end())
        return len(text) if nl < 0 else nl + 1
    return cut


class OverBudget(BaseException):
    """BaseException so the engine's narrow excepts never swallow it."""


def _alarm(signum, frame):
    raise OverBudget()


def run_budget(fn, seconds=REDACT_BUDGET):
    """Return fn(); raise OverBudget when it runs longer than seconds (SIGALRM where available)."""
    if seconds <= 0:
        raise OverBudget()
    if not hasattr(signal, "SIGALRM") or threading.current_thread() is not threading.main_thread():
        began = time.monotonic()
        out = fn()
        if time.monotonic() - began > seconds:
            raise OverBudget()
        return out
    old = signal.signal(signal.SIGALRM, _alarm)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        return fn()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)
