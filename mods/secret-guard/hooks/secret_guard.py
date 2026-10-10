#!/usr/bin/env python3
"""PreToolUse hook: deny secret-source plus transform combos and tampering; route Bash output through the filter."""
import json
import urllib.parse
import os
import re
import shlex
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SAFE = {
    "read": "Read the file or run the command plainly and let the redactor hide the values.",
    "status": "Ask for non-secret fields only, for example docker inspect --format '{{.State.Health.Status}}'.",
    "compose": "Use docker compose config --no-interpolate, which prints names without values.",
    "names": "List names only (for example grep -o '^[A-Z_]*=' .env | cut -d= -f1 is not allowed; use wrangler secret list or vercel env ls).",
    "tool": "Use the tool's non-secret listing form (for example wrangler secret list, vercel env ls, op item list).",
    "edit": "Ask the owner to make this change; hooks, settings and tests are not edited by the agent.",
}

SECRET_NAME_WORDS = r"(?:secret|token|passw(?:or)?d|passwd|pwd|api[_-]?key|apikey|private[_-]?key|credential|auth|bearer|dsn|database_url|db_url)"

ENV_FILE = r"(?:\.env(?!rc\b|\.example\b|\.sample\b|\.template\b|\.dist\b)(?:\.[\w.-]*)?|[\w.-]+\.env(?:\.(?!example\b|sample\b|template\b)[\w-]+)?|\.dev\.vars[\w.-]*|\.npmrc|\.netrc|\.pgpass|_netrc)"
SECRET_FILES = (
    r"(?:(?<![\w.-])" + ENV_FILE + r"(?![\w-])"
    r"|\.docker/config\.json|docker_config\.json|\.aws/credentials|\.aws/config|\.ssh/|id_(?:rsa|ed25519|ecdsa|dsa)\b"
    r"|[\w.-]+\.(?:pem|key|p8|p12|pfx|jks|keystore|gpg|asc)(?![\w-])|\.kube/config|\.gnupg|\.my\.cnf|\.pypirc"
    r"|secrets?\.(?:json|ya?ml|toml|txt)|credentials?\.(?:json|ya?ml|txt)|\.git-credentials|\.config/gh/hosts\.yml"
    r"|\.gem/credentials|\.composer/auth\.json|\.m2/settings\.xml|\.gradle/|rclone\.conf|wg\d+\.conf|/etc/wireguard"
    r"|tailscaled\.state|\.cloudflared|identity\.secret|\.mcp-auth|krb5cc|\.config/[\w.-]*creds[\w./-]*|/run/credentials"
    r"|\.?harvest-cache\.json|\.claude/secret-guard/|/run/secrets|/run/app/token|private_keys|login\.keychain|\.keychain|svc/key|vault\.ya?ml|\.cursor/mcp\.json)"
)
SECRET_FILES_RE = re.compile(SECRET_FILES, re.I)

SENS_COMMON = [
    r"\.claude/projects", r"\.(?:zsh|bash)_history", r"\.zsh_sessions", r"\.lesshst", r"\.python_history", r"\.psql_history",
    r"\.mysql_history", r"\.node_repl_history", r"/proc/[^\s'\"]*/(?:environ|mem|maps|cmdline)", r"/proc/self",
    r"/cores\b", r"/tmp/tfplan", r"tfplan", r"quicklook", r"/screenshots?\b", r"timemachine", r"\.trash",
    r"/cookies\b", r"cookies\.sqlite", r"local storage", r"logins\.json", r"key[34]\.db",
    r"application support/(?:slack|notion|discord|claude|google/chrome|firefox|1password|signal|code/|cursor|zoom)",
    r"\.config/(?:slack|discord|google-chrome|chromium|1password)", r"group containers", r"/library/containers/",
    r"library/keychains", r"mobilesync", r"library/messages", r"library/mail", r"library/safari", r"library/cookies",
    r"library/clipboard", r"clipboard[\w-]*/", r"clipboard[\w.-]*\.(?:db|sqlite)", r"library/logs/iterm2", r"iterm2/session",
    r"sleepimage", r"swapfile", r"/private/var/vm", r"com\.apple\.quicklook", r"/var/folders/[^\s]*/c/", r"\.cast\b",
    r"/tmp/io\.log", r"\.bash_logout", r"/private/etc/svc", r"\.ssh\b", r"\.my\.cnf",
    r"\.zshrc|\.bashrc|\.zprofile|\.bash_profile|\.zshenv|(?<![\w])\.profile\b|\.zlogin",
]
SENS_TOOL = [
    r"/dev/fd", r"\.(?:png|jpe?g|gif|pdf|ps|heic|tiff?)$", r"coresimulator", r"library/preferences/[^/]+\.plist",
    r"/typescript$", r"derivedData/[^\s]*(?:googleservice|\.plist)", r"xcode/archives", r"library/mobile documents",
    r"cloudstorage", r"/volumes/", r"xcresult", r"\.env(?!rc)", r"/library/application support/",
]
IMAGE_RE = re.compile(r"\.(?:png|jpe?g|gif|heic|tiff?)$")
PROJECT_ASSET_RE = re.compile(r"/(?:docs?|assets|public|static|images?|img|design|icons?|logos?)/")
CAPTURE_RE = re.compile(r"screen|shot|capture|snap|/desktop/|/downloads/|/tmp/|/var/folders|scratch|\.env|secret|credential|/ql|term|dashboard|photo|token|key")
SENS_COMMON_RE = re.compile("|".join(SENS_COMMON), re.I)
SENS_TOOL_RE = re.compile("|".join(SENS_TOOL), re.I)

PROT_PATHS = re.compile(
    r"\.claude/settings[\w.-]*\.json|managed-settings\.json|\.claude/hooks/|hooks/tests/|secret_(?:engine|redact|guard|filter)\.py"
    r"|redact(?:or)?[\w.-]*\.(?:sh|js|py)(?![\w])|path_guard\.py|\.config/renav-redactor|\.claude/statusline|\.mcp\.json|\.ssh/config"
    r"|(?<![\w])\.(?:zshrc|bashrc|zprofile|bash_profile|profile|zshenv)\b|\.git/config|\.git/hooks|\.githooks|\.claude/worktrees"
    r"|\.claude/commands|\.claude/agents|\.claude/skills|session-start\.sh|\.claude/plugins|\.rprofile|sitecustomize\.py|usercustomize\.py"
    r"|\.claude/[\w./-]*\.command|\.claude/leak|\.claude/settings",
    re.I,
)
PROT_BASE = re.compile(r"(?:^|/)(?:settings(?:\.local)?\.json|managed-settings\.json|\.mcp\.json|\.rprofile|sitecustomize\.py|usercustomize\.py|statusline[\w.-]*)$", re.I)
CLAUDE_DIR = re.compile(r"(?:^|/)\.claude(?:/|$)", re.I)

# HARD_IDX selects CRED_TOOLS entries by position: append new rules at the end, never insert.
CRED_TOOLS = [
    (r"\bsecurity\s+(?:-\S+\s+)*find-(?:generic|internet)-password\b[^|;&]*\s-[a-zA-Z]*[wg]", "keychain"),
    (r"\bsecurity\s+(?:-\S+\s+)*export\b[^|;&]*(?:-t\s+(?:privKeys|identities|all)|-P\b|-f\s+pkcs12)", "keychain"),
    (r"\bsecurity\s+(?:-\S+\s+)*(?:dump-keychain|unlock-keychain|import|delete-\S+|set-\S+|show-keychain-info|list-keychains\s+-d|add-(?:generic|internet)-password\b[^|;&]*\s-[a-zA-Z]*w\s+['\"]?[^\s'\"-])", "keychain"),
    (r"\bgh\s+auth\s+(?:token|status\b.*--show-token)", "tool"),
    (r"\bgh\s+(?:ssh-key|gpg-key)\s+list", None),
    (r"\bgcloud\s+(?:auth\s+(?:print-access-token|print-identity-token|application-default\s+print-access-token)|secrets\s+versions\s+access)", "tool"),
    (r"\baws\s+(?:secretsmanager\s+get-secret-value|ssm\s+get-parameters?\b.*--with-decryption|sts\s+(?:assume-role|get-session-token|get-federation-token)|configure\s+(?:get|export)|ecr\s+get-login-password|codeartifact\s+get-authorization-token|eks\s+get-token)", "tool"),
    (r"\bkubectl\s+(?:get\s+secrets?|config\s+view\s+--raw|exec\b.*\b(?:env|printenv|cat\s+/proc|cat\s+/var/run/secrets)|describe\s+secret|create\s+token|logs\b.*--previous)", "tool"),
    (r"\bkubectl\s+(?:-\S+\s+\S+\s+)*get\s+secrets?\b", "tool"),
    (r"\bsops\s+(?:-d\b|--decrypt\b|decrypt\b|exec-env\b|exec-file\b|edit\b|-e\b|-i\b)", "tool"),
    (r"\bvercel\s+env\s+(?:pull|ls\s+.*--decrypt|list\s+.*--decrypt)", "tool"),
    (r"\bdotenvx\s+(?:get|decrypt|run)\b", "tool"),
    (r"\bop\s+(?:read|inject|run|item\s+get|signin|document\s+get)\b", "tool"),
    (r"\bbw\s+(?:get\s+(?:password|totp|item|notes|username|uri)|unlock|login|export)\b", "tool"),
    (r"\bpass\s+(?:show|-c|insert|edit|generate|git)\b|\bpass\s+(?!ls\b)[\w/.-]+$", "tool"),
    (r"\bcloudflared\s+tunnel\s+token\b", "tool"),
    (r"\bgit\s+credential\s+(?:fill|approve|reject)\b|\bgit\s+config\s+(?:--get\S*\s+)?(?:--\S+\s+)*credential\b", "tool"),
    (r"\bdocker-credential-\w+", "tool"),
    (r"\bdocker\s+login\b.*(?:-p\b|--password(?!-stdin))", "tool"),
    (r"\bpulumi\s+.*--show-secrets\b|\bpulumi\s+config\s+get\b", "tool"),
    (r"\bdocker\s+(?:save|export)\b", "status"),
    (r"\bdocker\s+(?:compose|-compose)?\s*(?:-\S+\s+\S+\s+)*config\b(?!.*--no-interpolate)", "compose"),
    (r"\bdocker[- ]compose\s+(?:-\S+\s+\S+\s+)*config\b(?!.*--no-interpolate)", "compose"),
    (r"\bdocker\s+run\b.*\s-v\s+/:/", "tool"),
    (r"\bdocker\s+run\b.*\bcat\s+\S*(?:\.env|secret|credential|/run/secrets)", "status"),
    (r"\bdocker\s+(?:service\s+inspect|stack\s+config|config\s+inspect|secret\s+inspect)\b", "status"),
    (r"\bwg\s+(?:show\s+\S+\s+(?:private-key|preshared-keys)|showconf|show\s+all\s+private)", "tool"),
    (r"\bwg\s+show\s+\S+\s*$", None),
    (r"\btailscale\s+up\b.*--authkey", "tool"),
    (r"\bage-keygen\b(?!.*(?:\s-o\b|>))", "tool"),
    (r"\bminisign\s+-G\b", "tool"),
    (r"\bssh-keygen\s+(?:-\S+\s+)*-p\b|\bssh-keygen\s+(?:-\S+\s+)*-(?:f\s+\S+\s+)?-?[Ee]\b|\bssh-keygen\s+(?:-t\s+\S+\s+)", "tool"),
    (r"\bgpg2?\s+(?:--\S+\s+)*--export-secret-(?:keys|subkeys)\b", "tool"),
    (r"\bgpg2?\s+(?:--\S+\s+)*(?:--decrypt|-d)\b", "tool"),
    (r"\bgpg-connect-agent\s+['\"]?(?:PK|GET_PASSPHRASE|EXPORT|READKEY|GETKEYINFO|KEYINFO\s+--list.*--data)", "tool"),
    (r"\bopenssl\s+pkcs12\b(?!.*-nokeys)(?=.*(?:-nodes|-out|-nocerts|-passin\s+pass:))", "tool"),
    (r"\bopenssl\s+(?:rsa|ec|pkey|pkcs8|dsa)\b(?=.*(?:-text|-out\b|-nocrypt|-outform))(?!.*-pubout)", "tool"),
    (r"\bopenssl\s+enc\b.*-in\s+\S*(?:key|\.p8|\.pem|credentials|\.env)", "tool"),
    (r"\bpkcs11-tool\b.*--read-object|\bpkcs11-tool\b.*--(?:login|pin)", "tool"),
    (r"\bterraform\s+(?:show\s+.*-json|output\b.*-json|state\s+(?:show|pull)|console)\b", "tool"),
    (r"169\.254\.169\.254/.*(?:iam/security-credentials|api/token|user-data|identity/oauth2)", "tool"),
    (r"169\.254\.169\.254/latest/api/token", "tool"),
    (r"\bcurl\b.*(?:localhost|127\.0\.0\.1):9222|\b(?:cdp|devtools)[-_\w]*client|--remote-debugging-port", "tool"),
    (r"\bpbpaste\b|\bpbcopy\b(?=.*(?:security|op\s|printenv|\.env|token|secret|passw|key))", "tool"),
    (r"\bosascript\b(?=.*(?:clipboard|keystroke|System Events|do shell script|do script|iTerm|get contents|entireContents|key code|display dialog.*hidden))", "tool"),
    (r"\btmux\s+(?:capture-pane|pipe-pane|save-buffer|show-buffer|send-keys)|\btmux\s+new(?:-session)?\b|\bscreen\s+(?:-\S+\s+)*(?:-dmS|-S\s+\S+\s+-X|-X|-L)", "tool"),
    (r"\bscreencapture\b|\bqlmanage\b(?!\s+-m\b)|\bsimctl\s+io\b.*screenshot|\bsimctl\s+spawn\b.*defaults\s+read\b(?=.*(?:token|key|secret))", "tool"),
    (r"\b(?:lldb|gcore|dtrace|fs_usage|dtruss|strace|ltrace|gdb)\b", "tool"),
    (r"(?<![\w-])(?:leaks|heap)\s+(?!-noContent)(?:-\S+\s+)*[\w\"$]+", "tool"),
    (r"\bstrings\s+.*sleepimage", "tool"),
    (r"\bsudo\b(?!\s+-n\s+systemctl\s+status)(?!\s+systemctl\s+status)", "tool"),
    (r"\bopen\b(?:\s+-\S+(?:\s+\w+)?)*\s+\S*\.command\b|\bxargs\s+open\b|\b(?:command|env|nohup)\s+open\s+\S*\.command|(?<![\w-])open\s+[\"']?(?:alfred|raycast)://", "tool"),
    (r"\bcurl\b[^|;&]*\|\s*(?:sudo\s+)?(?:ba|z|da)?sh\b|\bcurl\b[^|;&]*\|\s*osascript|\bwget\b[^|;&]*\|\s*(?:ba|z)?sh\b|\bcurl\b[^|;&]*\|\s*python", "tool"),
    (r"\bssh\s+(?:-\S+\s+)*-F\b|\bssh\s+.*-o\s*(?:ProxyCommand|LocalCommand|PermitLocalCommand|IdentityAgent)|\bssh\s+(?:-\S+\s+)*-S\s", "tool"),
    (r"\bssh\s+(?:-\S+\s+)*-[a-zA-Z]*A\b|\bssh\s+.*-o\s*ForwardAgent\s*=?\s*yes|\bssh\s+-R\s+\S*(?:gpg|agent|ssh-auth)", "tool"),
    (r"\bnc\s+-U\b|\bsocat\b.*UNIX-CONNECT|AF_UNIX|SSH_AUTH_SOCK=", "tool"),
    (r"\bssh-keygen\b(?!\s+-y\b)(?!.*-l\b)", "tool"),
    (r"\bdefaults\s+(?:write|export)\b|\bdefaults\s+read\b(?=.*(?:token|key|secret|password|auth))", "tool"),
    (r"\bPlistBuddy\b", "tool"),
    (r"\bxattr\b|\brsync\b.*\s-[a-zA-Z]*E[a-zA-Z]*\s|\bditto\b(?=.*(?:Application Support|MobileSync|CoreSimulator|Library))", "tool"),
    (r"\bulimit\s+-c\b|\blaunchctl\s+(?:setenv|submit|load|bootstrap|kickstart|print)", "tool"),
    (r"\bsftp\s+.*-b\b", "tool"),
    (r"\bredis-cli\b.*\s-a\s|\bmysql\b.*\s-p\S|\bmysql\b.*--password=\S", "tool"),
    (r"\bbash\s+-x\s+\./|\bsh\s+-x\s+\./", "tool"),
    (r"\bnpx\s+jest\b.*(?:\s-u\b|--updateSnapshot|--ci=false)", "tool"),
    (r"\bat\s+now\b|\bcrontab\b|\bat\s+-f\b", "edit"),
    (r"\bmkfifo\b(?=.*(?:cat|sh|bash|read|\.env|secret))", "tool"),
    (r"\bscript\s+(?:-\S+\s+)*(?:--log-\w+|-q|-c|\S+\.log|\S+typescript)|\bscriptreplay\b|\bsudoreplay\b|\basciinema\b|\btlog\b", "tool"),
    (r"\bidevicebackup2\b|\bmdls\b(?![-.\w])|\bmdfind\b(?=.*(?:kMDItemTextContent|-onlyin\s+\S*(?:creds|secret|\.config|\.ssh|\.aws|Library)|key|token|secret|password|\.env|credential))|\blocate\b|\bmdfind\b\s+\S+$", "tool"),
    (r"\bxcrun\s+xcresulttool\b|\bxcrun\s+simctl\s+(?:keychain|openurl|pbpaste)", "tool"),
    (r"\bgit\s+(?:reflog\s+expire|gc\s+--prune|prune\b|filter-branch|filter-repo)", "edit"),
    (r"\bgit\s+(?:-C\s+\S+\s+)?(?:-c\s+\S+\s+)*log\b.*-g\b.*--walk-reflogs|\bgit\s+.*--walk-reflogs", "tool"),
    (r"\bgit\s+(?:-c\s+\S+\s+)*(?:-C\s+\S+\s+)?(?:-c\s+\S+\s+)*-c\s*(?:core\.(?:fsmonitor|sshCommand|editor|pager=\S*[a-z]+\s+(?:push|fetch))|diff\.\S+\.(?:textconv|command)|filter\.\S+\.(?:clean|smudge|process)|alias\.)", "edit"),
    (r"\bgit\s+config\b(?!\s+--(?:get|list|local\s+--get))(?=.*(?:textconv|fsmonitor|sshCommand|filter\.|core\.(?:editor|pager)|alias\.|credential))", "edit"),
    (r"(?!x)x", "edit"),
    (r"\bgit\s+(?:checkout|restore)\b[^|;&]*(?:--\s+)?\S*\.claude/|\bgit\s+reset\s+--hard\b|\bgit\s+clean\s+-[a-z]*f", "edit"),
    (r"\bgit\s+clone\b(?![^|;&]*https://)[^|;&]*\s~?/?[^\s]*\.claude/(?:hooks|plugins\b)", "edit"),
    (r"\bgit\s+clone\s+git@", None),
    (r"\bgit\s+add\s+(?:-\S*f\S*|--force)\b", "edit"),
    (r"\bmise\s+trust\b|\basdf\s+direnv\b", "edit"),
    (r"\bclaude\b(?=.*(?:--bare|--settings|--setting-sources|--dangerously-skip-permissions|--allow-dangerously|--permission-mode\s+bypass|--mcp-config|--append-system-prompt-file|--plugin-dir))", "edit"),
    (r"\bCLAUDE_(?:CONFIG_DIR|CODE_[A-Z_]*)\s*=", "edit"),
    (r"disableAllHooks|disable_all_hooks|CLAUDE_CODE_DISABLE\w*HOOK|SECRET_HOOK_(?:HOME|ROOTS)\s*=|PYTHONPATH\s*=|PYTHONSTARTUP\s*=|NODE_OPTIONS\s*=\s*--(?:require|import)|BASH_ENV\s*=|\bENV\s*=\s*\S+\s+(?:ba)?sh|LD_PRELOAD\s*=|DYLD_INSERT_LIBRARIES\s*=", "edit"),
    (r"\bexport\s+PATH=\S*(?:\$HOME|~|/tmp|\.)\S*shim|\bPATH=\S*shim", "edit"),
    (r"\bpython3?\s+\S*\.claude/hooks/secret_(?:redact|guard|filter|engine)\.py|\bpython3?\s+\S*secret_(?:redact|guard)\.py|\bsecret_(?:redact|guard|filter)\.py\b(?=.*(?:<|\|))", "edit"),
    (r"\bln\s+(?:-\S+\s+)*\S*\.claude\b|\bln\s+(?:-\S+\s+)*\S*settings[\w.]*\s", "edit"),
    (r"\b(?:ansible|ansible-playbook)\b(?=.*(?:-m\s+shell|-m\s+command|-m\s+raw|-a\s+['\"]?(?:env|printenv|cat )))", "tool"),
    (r"\bcurl\b[^|;&]*(?:127\.0\.0\.1|localhost)(?::\d+)?/(?:debug/(?:vars|pprof)|actuator/(?:env|heapdump|configprops|beans|mappings|loggers)|env\b|heapdump|metrics/env)|\bwget\b[^|;&]*actuator/env|actuator/env", "tool"),
    (r"/dev/tcp/", "tool"),
    (r"\bconsole\.log\(\s*process\.env|print\(\s*os\.environ|Sys\.getenv\(\)", "tool"),
    (r"\bpsql\b[^|;]*\$\{?(?:DATABASE_URL|DB_URL)\}?[^|;]*(?:token|password|secret|users|credential|api_key|session)", "tool"),
    (r"\bsqlite3\b(?=.*(?:Application Support|Library/(?:Group|Containers|Messages|Mail|Safari|Cookies|Clipboard)|history\.(?:db|sqlite)|\.sqlite|notion|slack|manifest\.db|n\.db))(?!.*\./app\.db)", "tool"),
    (r"\bcat\s+/Users/[^/\s]+/\.config/\w*[sS]ecret", "tool"),
    (r"\bclaude\s+plugins?\s+(?:(?:disable|uninstall|remove|rm)\b[^|;&]*(?:secret-guard|--all)|marketplace\s+(?:remove|rm)\b[^|;&]*\bcj-stack\b)", "edit"),
]

EDIT_RES = [re.compile(rx, re.I) for rx, kind in CRED_TOOLS if kind == "edit"]
CRED_CMD = r"security\\s+find|gh\\s+auth|op\\s+read|aws\\s|gcloud\\s|pass\\s|gpg\\s"
HARD_IDX = (1, 7, 8, 9, 10, 11, 19, 20, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 47, 49, 51, 52, 53, 54, 55, 56, 61, 62, 63, 64, 66, 67, 68, 69, 86, 90, 92)
HARD_TOOLS = [(re.compile(rx, re.I), kind) for i, (rx, kind) in enumerate(CRED_TOOLS) if i in HARD_IDX]
TOOL_SRC_RES = [re.compile(rx, re.I) for i, (rx, kind) in enumerate(CRED_TOOLS) if kind not in (None, "edit") and i not in HARD_IDX]

XFORM = re.compile(
    r"(?:^|[\s|;&(`{])(?:(?:base64|base32|b64encode|xxd|od|hexdump|hd|cut|rev|fold|tr|shasum|md5sum|md5|sha\d+sum|sha\d+|cksum|b2sum|wc|"
    r"cmp|comm|(?<!git )diff|expr|awk|gawk|nl|paste|split|dd|iconv|uuencode|zlib-flate|gzip|bzip2|xz|zstd|strings)(?![\w.-])|"
    r"openssl\s+(?:enc|dgst|base64|sha\d*|md5)|sort\s+-c|sort\s+-C|head\s+-c|tail\s+-c|head\s+-[a-z]*c|"
    r"python3?\s+-c|python3?\s+-|python3?\s+<<|node\s+-e|node\s+-p|ruby\s+-e|perl\s+-[a-z]*e|perl\s+-[a-z]*p|php\s+-r|jq\s+.*(?:@base64|@uri|@sh|length|explode|tojson|ltrimstr|test\(|split)|"
    r"test\s+-[nz]|\[\s+-[nz]\s|\[\[\s+-[nz]|grep\s+(?:-[a-zA-Z]*[cqbo][a-zA-Z]*\s)|grep\s+--(?:count|quiet|silent|only-matching|byte-offset)|egrep\s+-[a-z]*[cqo]|"
    r"sed\s+-[a-zA-Z]*[nE]*[a-zA-Z]*\s+['\"]?\d|sed\s+(?:-[a-zA-Z]+\s+)*['\"]?s[/#|,]|sed\s+-[a-zA-Z]*e\s|printf\s+['\"]%[^'\"]*\\?[xXodiu]|xargs\s+-[a-zA-Z]*I|"
    r"bc\b|dc\b|sum\b|cat\s+-[a-z]*[vet]|less\b|tee\s+/dev/(?:tty|stderr))",
    re.I,
)
SHELL_XFORM = re.compile(r"\$\{#\w+\}|\$\{\w+:\d+(?::\d+)?\}|\$\{\w+(?:##?|%%?|//?|\^\^?|,,?)[^}]*\}|\$\(\(.*\)\)|\bcase\s+\S+\s+in\b|\bread\s+-[a-z]*n\d", re.I)

SOURCE_RES = [
    re.compile(r"(?<![\w-])printenv\b(?!\s+(?:PATH|HOME|USER|SHELL|PWD|LANG|TERM|TMPDIR|HOSTNAME|EDITOR|PAGER|LOGNAME)\b)", re.I),
    re.compile(r"(?:^|[\s|;&(`{\"'])env\s*(?:$|[|;&)`}>\"'<]|\s+(?:-0|-i|--)?\s*(?:$|[|;&>]))", re.I),
    re.compile(r"(?<![\w-])export\s+-p\b|(?<![\w-])declare\s+-[a-z]*x|(?<![\w-])set\s*(?:$|[|;&])|\bcompgen\s+-e\b", re.I),
    re.compile(r"/proc/[^\s'\"]*/environ", re.I),
    re.compile(r"\bdocker\s+(?:container\s+)?inspect\b(?!.*--format\s+['\"]?\{\{\s*\.(?:State|Image|Name|Config\.Image|Id|NetworkSettings)\b)(?!.*-f\s+['\"]?\{\{\s*\.(?:State|Image|Name|Config\.Image|Id|NetworkSettings)\b)", re.I),
    re.compile(r"\bdocker\s+history\b.*--no-trunc", re.I),
    re.compile(r"\bdocker\s+exec\b.*\b(?:env|printenv|cat\s+\S*(?:\.env|secret|credential|/proc|/run/secrets)|/proc/)", re.I),
    re.compile(r"\bdocker\s+(?:compose|-compose)?\s*(?:-\S+\s+\S+\s+)*config\b(?!.*--no-interpolate)", re.I),
    re.compile(r"\bkubectl\s+(?:exec|get\s+secret)\b", re.I),
    re.compile(r"\bsops\s+-d\b|\bsops\s+--decrypt\b|\bop\s+read\b|\bbw\s+get\s+password\b|\bsecurity\s+find-\w+-password\b[^|;&]*-w|\bgpg\s+--export-secret-keys|\bdefaults\s+read\b|\bgh\s+auth\s+token|\bvercel\s+env\s+pull|\bwrangler\s+secret\s+(?:get|download)", re.I),
    re.compile(r"\bsecurity\s+find-\w+-password", re.I),
    re.compile(r"\bcurl\b[^|;&]*(?:actuator/env|/debug/vars|169\.254\.169\.254/latest/(?:api|meta-data/iam|user-data))", re.I),
    re.compile(r"\bhistory\b|\bgit\s+(?:reflog|log|show|diff|stash)\b[^|;&]*(?:\.env|secret|credential|\.pem|\.key)", re.I),
    re.compile(r"\$\{?#?[A-Za-z_]*(?:SECRET|TOKEN|PASSWORD|PASSWD|API_?KEY|PRIVATE_?KEY|CREDENTIAL|AUTH|DATABASE_URL|DB_URL)[A-Za-z_]*\}?", re.I),
    re.compile(r"\b[A-Za-z_]*(?:SECRET|TOKEN|PASSWORD|PASSWD|API_?KEY|PRIVATE_?KEY)[A-Za-z_]*\s*=\s*\$\(", re.I),
    re.compile(r"\bcat\s+(?:/run/secrets|/etc/(?:shadow|sudoers))", re.I),
]

ENV_EXEC = re.compile(r"\b(?:ssh|docker\s+exec|kubectl\s+exec|sh\s+-c|bash\s+-c|zsh\s+-c|eval)\b", re.I)

WRAP_RE = re.compile(
    r"""(?:\b(?:ssh|sh|bash|zsh|dash|ksh|eval|su|sudo|xargs|nohup|env|time|watch|timeout|nice|command)\b)""", re.I
)


def emit_deny(reason):
    out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}
    os.write(1, json.dumps(out, ensure_ascii=True).encode("ascii"))


def denial(what, safe):
    return "Blocked: %s. Safe alternative: %s" % (what, safe)


def norm(c):
    c = c.replace("\\\n", "")
    c = re.sub(r"'\s*\+\s*'|\"\s*\+\s*\"", "", c)
    c = re.sub(r"(?<=[\w./-])(?:''|\"\")(?=[\w./-])", "", c)
    c = re.sub(r"(?<![\w\\])(?:''|\"\")(?=[\w./-])", "", c)
    c = re.sub(r"\\(?=[A-Za-z/.~$_])", "", c)
    return c


def unquote_layers(c):
    """Return the command plus the bodies of quoted shell strings and substitutions, so inner commands are scanned as well."""
    texts = [c]
    seen = set()
    stack = [c]
    n = 0
    while stack and n < 200:
        t = stack.pop()
        n += 1
        for m in re.finditer(r"\$\(([^()]*(?:\([^()]*\)[^()]*)*)\)|`([^`]*)`|<\(([^()]*)\)|'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"", t):
            inner = next((g for g in m.groups() if g), None)
            if inner and inner not in seen and len(inner) > 2:
                seen.add(inner)
                texts.append(inner)
                stack.append(inner)
    return texts


DATA_CMDS = frozenset(("printf", "echo", "yes", "seq", "true", "false", ":", "print"))
TRIVIAL_CMDS = DATA_CMDS | frozenset(("head", "tail", "tr", "sleep", "return", "exit", "cat", "read", "local", "wait"))
SHELLS = frozenset(("sh", "bash", "zsh", "dash", "ksh", "ash"))
WRAP = frozenset(("ssh", "sudo", "su", "xargs", "nohup", "env", "time", "watch", "timeout", "nice", "command", "exec", "eval",
                  "docker", "kubectl", "stdbuf", "setsid", "doas", "podman", "script"))
PREFIX_WORDS = frozenset(("command", "builtin", "nohup", "time", "exec", "then", "do", "else", "if", "while", "until", "!", "elif"))
INTERP_HERE = re.compile(r"\b(?:sh|bash|zsh|dash|python3?|node|ruby|perl|php|ssh|docker|kubectl|sudo|xargs|eval|sqlite3|psql|mysql|source)\b")
REDIR_TOK = re.compile(r"^(?:\d*|&)(?:>>?|<<?<?|>&|<&)")
FUNC_DEF = re.compile(r"(?:^|(?<=[;&|\n{(]))\s*(?:function\s+)?([A-Za-z_][\w:.-]*)\s*(?:\(\s*\))?\s*\{")


def strip_heredocs(t):
    lines = t.split("\n")
    out = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        out.append(ln)
        i += 1
        m = re.search(r"(?<!<)<<-?\s*(['\"]?)([A-Za-z_]\w*)\1", ln)
        if m:
            word = m.group(2)
            body = []
            while i < len(lines) and lines[i].strip() != word:
                body.append(lines[i])
                i += 1
            i += 1
            if INTERP_HERE.search(ln[:m.start()]):
                out.extend(body)
    return "\n".join(out)


def skip_paren(t, j):
    depth = 0
    n = len(t)
    q = None
    while j < n:
        c = t[j]
        if q:
            if c == "\\" and q == '"':
                j += 1
            elif c == q:
                q = None
        elif c in "'\"":
            q = c
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return n


def skip_brace(t, j):
    depth = 0
    n = len(t)
    q = None
    while j < n:
        c = t[j]
        if q:
            if c == "\\" and q == '"':
                j += 1
            elif c == q:
                q = None
        elif c in "'\"":
            q = c
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    return n


def scan(t):
    n = len(t)
    i = 0
    segs = []
    toks = []
    buf = []
    val = []
    st = {"in": False, "sep": ""}

    def endword():
        if st["in"]:
            toks.append(["".join(buf), "".join(val)])
            del buf[:]
            del val[:]
            st["in"] = False

    def endseg(sp):
        endword()
        if toks:
            segs.append((st["sep"], list(toks)))
            del toks[:]
        elif st["sep"] in ("|", "|&") and sp in (";", "{", "}"):
            return
        st["sep"] = sp

    def add(raw, v):
        buf.append(raw)
        val.append(v)
        st["in"] = True

    while i < n:
        c = t[i]
        nx = t[i + 1] if i + 1 < n else ""
        if c == "'":
            j = t.find("'", i + 1)
            j = n - 1 if j < 0 else j
            add(t[i:j + 1], t[i + 1:j])
            i = j + 1
        elif c == '"':
            j = i + 1
            while j < n and t[j] != '"':
                if t[j] == "\\":
                    j += 2
                elif t[j] == "$" and t[j + 1:j + 2] == "(":
                    j = skip_paren(t, j + 1)
                elif t[j] == "`":
                    k = t.find("`", j + 1)
                    j = (k if k >= 0 else n) + 1
                else:
                    j += 1
            add(t[i:j + 1], t[i + 1:j])
            i = j + 1
        elif c == "\\" and nx:
            add(t[i:i + 2], nx)
            i += 2
        elif (c in "$<>" and nx == "(") :
            j = skip_paren(t, i + 1)
            add(t[i:j], t[i:j])
            i = j
        elif c == "$" and nx == "{":
            j = skip_brace(t, i + 1)
            add(t[i:j], t[i:j])
            i = j
        elif c == "`":
            k = t.find("`", i + 1)
            j = (k if k >= 0 else n - 1) + 1
            add(t[i:j], t[i:j])
            i = j
        elif c in " \t\r":
            endword()
            i += 1
        elif c in "\n;":
            endseg(c)
            i += 1
        elif c == "|":
            j = i + 1
            if nx in "|&":
                j += 1
            endseg(t[i:j])
            i = j
        elif c == "&":
            if nx == "&":
                endseg("&&")
                i += 2
            elif nx == ">" or (st["in"] and buf and buf[-1][-1:] in "<>"):
                add(c, c)
                i += 1
            else:
                endseg("&")
                i += 1
        elif c in "(){}" and not st["in"]:
            if c in "{}" and nx not in " \t\n;":
                add(c, c)
            else:
                endseg(c if c in "{}" else ";")
            i += 1
        elif c == ")" and st["in"]:
            endseg(";")
            i += 1
        else:
            add(c, c)
            i += 1
    endseg("")
    return segs


def cmd_index(toks):
    k = 0
    n = len(toks)
    while k < n:
        v = toks[k][1]
        r = toks[k][0]
        if re.fullmatch(r"[A-Za-z_]\w*\+?=.*", v, re.S) and not r.startswith(("'", '"')):
            k += 1
        elif REDIR_TOK.match(r):
            k += 2 if REDIR_TOK.fullmatch(r) else 1
        elif v in PREFIX_WORDS:
            k += 1
        else:
            return k
    return -1


def read_script(path, cwd):
    try:
        p = os.path.expanduser(path)
        if not os.path.isabs(p):
            p = os.path.join(cwd or os.getcwd(), p)
        if not os.path.isfile(p) or os.path.getsize(p) > 65536:
            return None
        with open(p, "r", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def find_functions(t):
    funcs = {}
    out = []
    pos = 0
    while True:
        m = FUNC_DEF.search(t, pos)
        if not m:
            break
        brace = m.end() - 1
        end = skip_brace(t, brace)
        body = t[brace + 1:end - 1]
        name = m.group(1)
        if name in ("if", "while", "until", "for", "do", "then", "else", "case", "select", "time"):
            out.append(t[pos:m.end()])
            pos = m.end()
            continue
        out.append(t[pos:m.start()])
        funcs[name] = body
        pos = end
    out.append(t[pos:])
    return "".join(out), funcs


def trivial_body(body):
    if re.search(r"\$[@*]|\$\{?[1-9@*]", body):
        return False
    for _, toks in scan(strip_heredocs(body)):
        k = cmd_index(toks)
        if k >= 0 and os.path.basename(toks[k][1]) not in TRIVIAL_CMDS:
            return False
    return True


def subst_bodies(raw):
    out = []
    i = 0
    n = len(raw)
    while i < n:
        c = raw[i]
        if c == "'" :
            j = raw.find("'", i + 1)
            if j < 0:
                break
            i = j + 1
            continue
        if c in "$<>" and raw[i + 1:i + 2] == "(":
            j = skip_paren(raw, i + 1)
            body = raw[i + 2:j - 1]
            if body.startswith("(") and body.endswith(")"):
                body = ""
            out.append(body)
            i = j
        elif c == "`":
            j = raw.find("`", i + 1)
            if j < 0:
                break
            out.append(raw[i + 1:j])
            i = j + 1
        else:
            i += 1
    return out


def effective(t, cwd, depth=0, budget=None):
    """Return the pipelines of a command as strings, with output-only text blanked and wrapped bodies expanded."""
    if budget is None:
        budget = [200000]
    t = strip_heredocs(t)
    t, funcs = find_functions(t)
    dropped = {k for k, b in funcs.items() if trivial_body(b)}
    pipes = []
    cur = []

    def flush():
        if cur:
            pipes.append(" | ".join(cur))
            del cur[:]

    def sub(txt):
        budget[0] -= len(txt)
        return effective(txt, cwd, depth + 1, budget) if depth < 5 and budget[0] > 0 else []

    for sep, toks in scan(t):
        if sep not in ("|", "|&"):
            flush()
        k = cmd_index(toks)
        raws = [x[0] for x in toks]
        if k < 0:
            cur.append(" ".join(raws))
            continue
        cmd = os.path.basename(toks[k][1])
        if cmd in dropped:
            continue
        if cmd in DATA_CMDS:
            keepi = [j for j in range(len(toks)) if j <= k or REDIR_TOK.match(toks[j][0]) or REDIR_TOK.fullmatch(toks[j - 1][0])]
            cur.append(" ".join(raws[j] for j in keepi))
            for j in range(k + 1, len(toks)):
                for body in subst_bodies(toks[j][0]):
                    pipes.extend(sub(body))
            continue
        for j in range(k + 1, len(toks)):
            for body in subst_bodies(toks[j][0]):
                pipes.extend(sub(body))
        done = False
        if cmd in SHELLS:
            ci = None
            script = None
            for j in range(k + 1, len(toks)):
                v = toks[j][1]
                if v.startswith("-") and not v.startswith("--") and "c" in v:
                    ci = j + 1
                    break
                if v.startswith("-"):
                    continue
                script = j
                break
            if ci is not None and ci < len(toks):
                inner = sub(toks[ci][1])
                pipes.extend(inner)
                cur.append(" ".join(raws[:ci] + ["(" + " ; ".join(inner) + ")"] + raws[ci + 1:]))
                done = True
            elif script is not None:
                src = read_script(toks[script][1], cwd)
                if src is not None:
                    inner = sub(src)
                    pipes.extend(inner)
                    cur.append("(" + " ; ".join(inner) + ")")
                    done = True
        elif cmd in WRAP:
            new = list(raws)
            for j in range(k + 1, len(toks)):
                if raws[j][:1] in ("'", '"') and re.search(r"[\s;|&$`]", toks[j][1]):
                    inner = sub(toks[j][1])
                    pipes.extend(inner)
                    new[j] = "(" + " ; ".join(inner) + ")"
            cur.append(" ".join(new))
            done = True
        if not done:
            cur.append(" ".join(raws))
    flush()
    for k, b in funcs.items():
        if k not in dropped:
            pipes.extend(sub(b))
    return pipes


def sensitive_path(p, tool_mode):
    if not isinstance(p, str):
        return None
    q = p.replace("\\u00e9", "é")
    q = re.sub(r"/+", "/", q)
    q = re.sub(r"/\./", "/", q)
    while re.search(r"/[^/]+/\.\./", q):
        q = re.sub(r"/[^/]+/\.\./", "/", q, count=1)
    ql = q.lower()
    base = os.path.basename(ql.rstrip("/"))
    if SECRET_FILES_RE.search(q) and not re.search(r"\.env\.(?:example|sample|template|dist)$|\.envrc$", ql):
        return "a secret-bearing file"
    if SENS_COMMON_RE.search(ql):
        return "a path that holds secrets or session data"
    if tool_mode and IMAGE_RE.search(ql) and PROJECT_ASSET_RE.search(ql) and not CAPTURE_RE.search(ql):
        return None
    if tool_mode and SENS_TOOL_RE.search(ql):
        return "a path that holds secrets or opaque data the redactor cannot clean"
    if tool_mode and base.startswith(".env") and not base.startswith(".envrc"):
        return "a secret-bearing file"
    return None


GEN_RE = re.compile(r"\bsecrets\.(?:token_\w+|choice|randbelow)|\bos\.urandom\b|\bopenssl\s+rand\b|\buuidgen\b|/dev/u?random\b|\brandomBytes\(", re.I)
SECRET_NAME_RE = re.compile(r"secret|token|passw|pwd|api[_-]?key|apikey|private[_-]?key|credential|auth|bearer|dsn|access[_-]?key|signing", re.I)
BENIGN_NAME_RE = re.compile(r"ttl|expir|budget|count|header|tokenizer|path|file|url$|dir$|enabled|mode|timeout|length|size|limit|prefix|type|name$|region", re.I)
HDR_LITERAL = re.compile(
    r"(?:authorization|x-api-key|x-auth-token|api-key|apikey|x-token|private-token|x-access-token)['\"]?\s*[:=]\s*['\"]?(?:(?:bearer|basic|token)\s+)?(?![$<{\[])[A-Za-z0-9_\-+/=.:]{6,}",
    re.I)
PIPE_LITERAL = re.compile(
    r"(?:printf|echo)\s+(?:-\S+\s+)*(?:['\"]%s\\?n?['\"]\s+)?(['\"])(?![$<])[^'\"]+\1\s*\|\s*(?:vercel\s+env\s+add|wrangler\s+secret\s+put|gh\s+secret\s+set|fly\s+secrets\s+(?:set|import)|heroku\s+config:set)")
FLAG_ASSIGN = re.compile(r"(?:-e|--env|--build-arg|--secret|--set-env-vars?|--env-vars?)[\s=]+['\"]?([A-Za-z_]\w*)=([^\s'\"]*)")
USERINFO = re.compile(r"[a-z][a-z0-9+.\-]*://[^/\s:@'\"]+:([^/\s@'\"]+)@", re.I)
ENCODER_RE = re.compile(r"\b(?:xxd|od|hexdump|base64|base32|basenc|uuencode|b2a_\w+|hexlify|b64encode|encodebytes|btoa)\b")
TYPED_ASSIGN = re.compile(r"\b([A-Za-z_]\w*)=([^\s'\"\\;|&`]+)")
PASS_FLAG = re.compile(r"\bsshpass\s+-p\s*\S|\bmysql(?:admin|dump)?\b[^|;&]*(?:\s-p\S|--password=\S)|\bcurl\b[^|;&]*\s(?:-u|--user|--proxy-user|-U)\s*['\"]?[^\s'\"$<]+:[^\s'\"$<]+|\b(?:pg_dump|psql)\b[^|;&]*://[^\s:@]+:[^\s@$]+@")


def _lit(v):
    from secret_engine import benign
    v = v.strip().strip("'\"")
    return bool(v) and not benign(v) and not re.match(r"[$<{\[]", v) and not re.fullmatch(r"(?:%[-\d.]*[sdiuxXoqfv]|\\?n)+", v)


def literal_cred(raw, allt):
    from secret_engine import TOKEN_RE
    if PIPE_LITERAL.search(raw):
        return "a secret value piped into a secrets tool"
    if re.search(r"\b(?:claude|codex|gemini)\s+mcp\s+add\b[^\n]*(?:--header|-H|-e|--env)\s+['\"]?[^\s'\"]*[:=]\s*(?:Bearer\s+)?['\"]?[A-Za-z0-9_.-]{8,}", allt, re.I):
        return "a token saved into an agent's config"
    if TOKEN_RE.search(allt) and re.search(r"\bgit\s+(?:\S+\s+)*commit\b|\bgh\s+(?:gist|issue|pr|release)\s+\w+|\bgist\b|(?:^|[;&\n]\s*)export\s+\w+=|\bbase64\b|\bxxd\b", allt):
        return "a token written into a commit, post, export or encoder"
    for m in USERINFO.finditer(allt):
        if _lit(m.group(1)):
            return "a password inside a URL"
    if PASS_FLAG.search(allt):
        return "a password on the command line"
    if ENCODER_RE.search(raw + "\n" + allt) and any(SECRET_NAME_RE.search(m.group(1)) and not BENIGN_NAME_RE.search(m.group(1)) and _lit(m.group(2))
                                       for m in TYPED_ASSIGN.finditer(raw)):
        return "a typed secret fed to an encoder"
    for m in FLAG_ASSIGN.finditer(allt):
        if SECRET_NAME_RE.search(m.group(1)) and not BENIGN_NAME_RE.search(m.group(1)) and _lit(m.group(2)):
            return "a secret passed as a flag"
    for sep, toks in scan(allt):
        k = cmd_index(toks)
        if k <= 0:
            continue
        for raw_t, val in toks[:k]:
            mm = re.match(r"([A-Za-z_]\w*)=(.*)$", val, re.S)
            if mm and SECRET_NAME_RE.search(mm.group(1)) and not BENIGN_NAME_RE.search(mm.group(1)) and _lit(mm.group(2)) and not re.search(r"\b(?:printenv|env|sh\s+-c|bash\s+-c)\b", allt):
                return "a secret in the environment of a command"
    return None


_ARG = r"(?:(?!\$\()[^|;&<>`])*"
_DS = r"(?:\s*2>(?:&1|/dev/null))*\s*$"
_SINK = r"(?:\s*\|\s*(?:head|tail|xxd|base64|less|more|od)\b" + _ARG + r")*"
DISPLAY_OK = [re.compile(rx, re.I) for rx in (
    r"^(?:\w+=\S+\s+)*kubectl\s+(?:-\S+\s+\S+\s+)*config\s+view(?:\s+--raw)?" + _DS,
    r"^sops\s+(?:-d|--decrypt|decrypt)\s+\S+" + _DS,
    r"^vercel\s+env\s+(?:ls|list)\b" + _ARG + _DS,
    r"^(?:mdfind|locate|plocate)\b(?!.*kMDItemTextContent)" + _ARG + _DS,
    r"^ssh\s+(?:-\S+\s+)*-F\s+(?![/~])\S+\s+" + _ARG + _DS,
    r"^SSH_AUTH_SOCK=(?:\"[^\"]*\"|'[^']*'|\S+)\s+ssh-add\s+-L" + _DS,
    r"^redis-cli\b(?:[^|;&<>`]|<[\w -]+>)*\s-a\s+\"?\$\{?\w+\}?\"?\s+CONFIG\s+GET\s+\w+" + _DS,
    r"^(?:sudo\s+(?:-n\s+)?)?(?:asciinema\s+play|sudoreplay|scriptreplay|journalctl)\b" + _ARG + _DS,
    r"^ssh\s+(?:-\S+\s+)*\S+\s+\((?:sudo\s+(?:-n\s+)?)?(?:asciinema\s+play|sudoreplay|scriptreplay|journalctl|curl\s+-s\s+https?://169\.254\.169\.254/latest/meta-data/iam/security-credentials/?)\b" + _ARG + r"\)?" + _DS,
    r"^xattr\s+(?:-[plxsz]+\s+)*\S+\s+\S+" + _SINK + _DS,
    r"^pbpaste\s*\|\s*head\s+-c\s*\d+" + _DS,
    r"^gpg2?\s+(?:--batch\s+)?(?:--decrypt|-d)\s+\S+(?:\s*>\s*[^\s|;&<>`$]+)?" + _DS,
    r"^curl\s+(?:-\S+\s+)*['\"]?https?://169\.254\.169\.254/latest/meta-data/iam/security-credentials/?['\"]?" + _DS,
    r"^git\s+diff\s+(?:--\s+)?\S+" + _DS,
    r"^tr\s+'\\0'\s+'\\n'\s*<\s*/proc/[\w$]+/environ" + _DS,
)]
def _unq(s):
    return re.sub(r"'[^']*'|\"[^\"]*\"", "''", s)


SEG_SPLIT = re.compile(r"\s*(?:&&|\|\||;|\n)\s*")


def drop_display(allt):
    kept = []
    for seg in SEG_SPLIT.split(allt):
        if seg and not any(rx.match(seg.strip()) for rx in DISPLAY_OK):
            kept.append(seg)
    return "\n".join(kept)



_SF = SECRET_FILES
_PATH_DENY = re.compile(
    r"Library/Application\\?\s+Support/(?:Google/Chrome|Slack|Firefox|BraveSoftware|Microsoft\s+Edge|Arc|discord|MobileSync)|MobileSync/Backup|Library/Cookies|"
    r"group\.com\.apple\.usernoted|Library/Clipboard|CoreSimulator/Devices/[^/\s]*/data|\.config/Slack|Local\\?\s+Storage|Cookies\.binarycookies|"
    r"Backups\.backupdb|com\.apple\.TimeMachine|localsnapshots|\.claude/shell-snapshots", re.I)
_EXTRA_FILE = re.compile(r"\.(?:pcapng?|har|hprof|dmp|memgraph)\b|(?:^|[\s/'\"])secrets?/", re.I)
_CRED_SHAPE = r"(?:AKIA\[?|ghp_|gho_|sk_live|sk-ant|xox[bp]-|eyJ|-----BEGIN)"
EXTRA_DENY = [(re.compile(rx, re.I), why) for rx, why in (
    (r"\bscreencapture\b", "an image of the screen cannot be redacted. Describe what you need to see in text"),
    (r"\b(?:grep|egrep|fgrep|rg|ag|ack|awk)\b[^\n]*<\s*<\(\s*(?:cat|head|tail|sed)\s+[^)]*(?:credential|\.env|\.pem|id_rsa|\.netrc|secret|token)", "testing a secret file through process substitution. Read the file; values are redacted"),
    (r"(?:^|[;&|(\n]\s*)(?:\.|source)\s+['\"]?\S*\.env(?!rc\b|\.example\b|\.sample\b|\.template\b|\.dist\b)\b", "sourcing an env file into the shell. Read the file; values are redacted"),
    (r"\b(?:grep|egrep|fgrep|rg|ag|ack)\b[^\n_]*(?:~|\$HOME|\$\{HOME\}|/Users/[^/\s]+|/home/[^/\s]+)/\.claude/(?:projects|history|sessions|todos)", "searching past session transcripts. Ask for the specific non-secret fact"),
    (r"\bxattr\b[^\n]*\|\s*(?:base64|xxd|od|hexdump|rev|tr)\b", "encoding file attributes. Read them without a pipe"),
    (r"/debug/pprof/(?:heap|allocs)\b[^\n]*(?:\s-o\s*\S+|\s-O\b|>\s*\S+|--output)|(?:\s-o\s*\S+|\s-O\b|--output)[^\n]*/debug/pprof/(?:heap|allocs)\b", "saving a heap profile to decode it. Read the plain response"),
    (r"\bdirenv\s+allow\b|\bgit\s+commit\b[^\n]*\s--no-verify\b|\btruncate\b[^\n]*harvest", "loosening a guard (direnv, git hooks, harvest cache). Ask the owner to do it"),
    (r"\bps\s+e\w*\b[^\n|]*\|\s*(?:base64|xxd|cut|awk|sed)\b|/proc/[^\s/]*/environ[^\n]*\|", "filtering environment output. Read a named variable you need instead"),
    (r"\blog\s+show\b[^\n]*\|\s*(?:base64|xxd|od)\b|\b(?:xxd|od)\b[^\n|]*\.pcap\b", "encoding system logs or captures. Ask for the specific non-secret lines"),
    (r"\bsqlite3\b[^\n]*(?:Chrome|usernoted|Clipboard)[^\n]*\bhex\(", "dumping a browser, notification or clipboard database. Ask for non-secret columns"),
    (r"--user-data-dir=?\s*['\"]?[^\n]*?(?:Library/Application\s+Support|\.config/(?:google-chrome|chromium)|\.mozilla)","starting a browser on the real profile. Use a fresh --user-data-dir under TMPDIR"),
    (r"\b(?:grep|rg)\b[^\n]*\s(?:~|\$HOME|/Users/\w+)/?(?:\.mcp-auth)?/?\s*(?:$|[|;&])|\bcat\s+\S*\.claude/projects/\S*\*", "searching saved sessions or the whole home for credentials. Search the project folder"),
    (r"\bxargs\s+(?:-\S+\s+)*(?:grep|rg)\b[^\n]*(?:token|secret|passw|key)|\|\s*xargs\s+(?:-\S+\s+)*grep\b", "mass-searching for credentials. Search the project folder"),
    (r"\bcat\s+\S*\.npmrc\s*\|", "filtering a credentials file. Read the file whole; values are redacted"),
    (r"\brsync\b(?:\s+-\S+)*\s+[\w.-]+@[\w.-]+:\S+\s+\S+","pulling a remote tree that may hold secrets. Name the files you need"),
    (r"\bgit\s+add\s+-A\b", "staging everything, including secrets. Add files by name"),
    (r"\bsed\s+-n\s+p\b[^\n]*\.env\b|\bls\s+-l\w*\s+[^\n|;]*(?<![\w-])(?:\.dev\.vars|\.env)", "probing secret file size or content. Read the file; values are redacted"),
    (r"\bkubectl\b[^\n]*\bexec\b[^\n]*\benv\b[^\n]*\|", "filtering a remote environment. Read a named variable"),
    (r"\bdocker\s+exec\b[^\n]*\$\w*(?:KEY|SECRET|TOKEN|PASS\w*)[^\n]*\|\s*(?:cut|base64|xxd|awk|sed)", "transforming a secret variable"),
    (r"\bos\.environ\[[^\]]*\][^\n]*\^|\bcut\s+-c\S*\s*<<<|\bpython3?\s+-c[^\n]*\^0x", "a transform over a secret variable"),
    (r"\bsudo\s+-n\s+less\b", "sudo paging a file"),
    (r"\bgit\s+submodule\s+foreach\b[^\n]*\b(?:cat|grep|rg|env|printenv|base64|xxd|strings|curl)\b", "running arbitrary commands over submodules"),
    (r"\btar\s+-?[a-z]*x[a-z]*f?\s+\S*(?:blobs|layer)", "unpacking image layers"),
    (r"(?:\[\[?|\btest)\s+\\?[\"']?\$\{?\w*(?:SECRET|TOKEN|PASS\w*|KEY|DSN)\w*\}?\\?[\"']?\s+(?:=|==|!=|\\?<|\\?>|-[a-z]{2}\b)", "a comparison oracle on a secret variable"),
    (r"\{\{[^}]*\b(?:if\s+eq|len)\b[^}]*Config\.Env|println\s+\(len\s+\.\)", "a template oracle over container environment"),
    (r"\bgit\s+log\b[^|;&\n]*\s-[SG]\s*(?-i:(?!['\"]?[A-Z][A-Z0-9_]*['\"\s]))['\"]?\S{6,}", "a pickaxe search with a value guess"),
    (r"\bulimit\s+-c\s+(?!0\b)\w", "enabling core dumps"),
    (r"ApplicationServices|AXUIElement|\bAXValue\b", "reading other apps through accessibility"),
    (r"\bosascript\b[^\n]*(?:keystroke|key\s+code|do\s+shell\s+script|\bdo\s+script\b|display\s+dialog)", "scripted keystrokes, shell or dialogs"),
    (r"\bosascript\b[^\n]*display\s+notification[^\n]*(?:token|secret|passw|key)\w*\s*[=:]", "a notification carrying a credential"),
    (r"\bsudo\b(?:\s+-\S+)*\s+(?:cp|mv|dd|tar|rsync|tee|sh|bash|zsh|sqlite3)\b", "sudo copying files"),
    (r"\|\s*sudo\s+(?:-\S+\s+)*-S\b|\bsudo\s+(?:-\S+\s+)*-S\b[^|;&\n]*<", "a password piped to sudo"),
    (r"\b(?:curl|wget|http)\b[^|;&\n]*\$\(\s*(?:printenv|env\b|security\s+find|op\s+read|gh\s+auth|aws\s|gcloud\s|pass\s|gpg\s)", "a credential tool's output sent in a request"),
    (r"(?:(?:eval|\$\()[^;\n]*|(?:\bsh\b|\bbash\b)[^;\n|]*)base64\s+(?:-d|-D|--decode)|base64\s+(?:-d|-D|--decode)[^;\n]*\|\s*(?:ba|z)?sh\b", "decoding and running hidden commands"),
    (r"\b(?:gpg2?\b[^|;&\n]*(?:--decrypt|-d)\b|age\s+(?:-\S+\s+)*-d\b|sops\s+(?:-\S+\s+)*(?:-d|--decrypt))[^|;&\n]*\s(?:-o|--output)\s*\S+", "decrypting into a file"),
    (r"\bdefaults\s+write\b[^;\n]*\$\(\s*defaults\s+read", "copying a stored credential"),
    (r"\bmount_apfs\b|\btmutil\s+(?:mount|restore|listlocalsnapshots)|\bsshfs\b[^;\n]*&&", "mounting snapshots or remote file systems"),
    (r"\brsync\b[^|;&\n]*(?:\s-[a-zA-Z]*E[a-zA-Z]*\b|--extended-attributes)", "copying extended attributes"),
    (r"\b(?:getxattr|listxattr)\b", "reading extended attributes in code"),
    (r"\bRIPGREP_CONFIG_PATH\s*=", "pointing ripgrep at a config"),
    (r"\b(?:cp|ln|ditto|rsync|mv|install|tar|zip)\b[^|;&\n]*(?:~|\$HOME|/Users/[\w.-]+)/\.(?:ssh|aws|gnupg|kube|config/gh|npmrc|netrc|docker)\b", "copying a credential folder"),
    (r"\bclient[_-]?secret\s*=", "a client secret on the command line"),
    (r"\b(?:printenv|env)\s*(?:\|[^>\n;&]*)?>>?\s*(?!/dev/|&|\(?\"?\$\{?TMPDIR)[^\s&]", "writing the environment to a file"),
    (r"\bqlmanage\b(?![^\n]*-m\b)(?![^\n]*\.(?:png|jpe?g|gif|heic)\b)", "previewing files as images"),
    (r"\bssh\b[^;&\n]*\bcat\b\s+[^'\"|;&]*(?:" + _SF + r")[^|;&\n]*['\"]\s*>>?\s*[^\s&]", "pulling a remote secret file into a local file"),
    (r"\bssh\b[^;&\n]*\btar\b[^;&\n]*\.(?:aws|ssh|gnupg|kube)", "copying remote credential folders"),
    (r"\b(?:scp|rsync)\b(?:\s+-\S+)*\s+(?:[\w.-]+@)?[\w.-]+:(?!/run/credentials)\S*(?:" + _SF + r")\S*\s+\S+", "pulling secret files from a remote host"),
    (r"\b(?:scp|rsync)\b[^|;&\n]*\.\{(?:npmrc|netrc|aws)", "pulling credential files from a host"),
    (r"\bredis-cli\b[^\n]*\bxargs\b[^\n]*\bredis-cli\b[^\n]*\bGET\b", "bulk reading session values"),
    (r"(?:^|[;&|(]\s*)(?:\w+=\S+\s+)+(?:ba|z|da)?sh\s+-[a-z]*x\b|\bssh\b[^\n]*\b(?:ba|z|da)?sh\s+-[a-z]*x\b|\bset\s+-[a-z]*x\b[^\n]*(?:\bsource\b|\.\s+\S*\.env|\bprintenv\b|\benv\b)|\bset\s+-o\s+xtrace","shell tracing prints expanded secrets"),
    (r"\bssh\b[^;&\n]*\s-F\s+<\(|\bssh\b[^;&\n]*['\"][^'\"]*Match\s+exec|\bProxyCommand\b|\bLocalCommand\b", "an ssh config that runs commands"),
    (r">\s*(\S+)[^;|\n]*&&\s*ssh\s+(?:-\S+\s+)*-F\s+\1\b", "an ssh config written then used"),
    (r"\bpod\s+trunk\b", "registry token access"),
    (r"\bagentcookie\b", "syncing browser cookies"),
    (r"\bfind\b[^|;&\n]*-exec\s+(?:cat|grep|head|tail|less|strings|base64|xxd)\b[^\n]*", "bulk reading found files"),
    (r"\bscreen\s+-[a-zA-Z]*dm|\btmux\s+send-keys\b|\bssh\b[^\n]*\btmux\s+new\b", "an unattended shell session"),
    (r"\bwhile\s+read\b[^;\n]*;\s*do\s+(?:ba|z)?sh\s+-c\s+[\"']?\$", "a command relay loop"),
    (r"\bssh\s+['\"][^'\"]*[;|&$`]", "ssh with shell metacharacters in the host"),
    (r"\bsed\s+-i\S*\s[^|;&\n]*(?:ssh-guard|guard\.sh|redact\w*|\bhooks?\b)", "editing a guard script"),
    (r"\bgit\s+(?:-\S+\s+\S+\s+)*-c\s+core\.hooksPath\s*=", "pointing git at other hooks"),
    (r"\bjq\b[^|\n]*\b(?:apiKeyHelper|awsCredentialExport|otelHeadersHelper)\b[^\n]*\|", "running a credential helper"),
    (r"\bssh\s+(?:-\S+\s+)*-A\b", "agent forwarding"),
    (r"(?<![\w-])leaks\s+(?:-\S+\s+)*(?:-fullContent|--outputGraph)", "dumping process memory. Use leaks -noContent"),
    (r"(?:^|[;&|(\n]\s*)SSH_AUTH_SOCK=(?![\"'$])\S+\s+(?:ssh|scp|sftp|rsync|git|ssh-add|ssh-keygen)\b", "pointing ssh at another agent socket"),
    (r"\bGIT_(?:EXTERNAL_DIFF|PAGER)\s*=", "running a program over a diff. Use plain git diff"),
    (r"\bsed\s+(?:-\S+\s+)*-i\.\w+\b[^\n]*(?:\.env|\.dev\.vars|credentials|\.npmrc|\.netrc)", "leaving a backup copy of a secret file. Edit with your own editor"),
    (r"\brg\b(?=[^\n]*(?:\s-u{2,}\b|--no-ignore|--hidden))[^\n]*(?:AKIA|ghp_|sk[-_]|xox|-----BEGIN)", "a credential sweep that ignores ignore files. Search the project folder"),
    (r"\b(?:grep|rg)\s+(?:-\S+\s+)*-[a-zA-Z]*[lcqo][a-zA-Z]*\s[^\n|;]*\.claude/projects", "an oracle over saved sessions. Search the project folder"),
    (r"\bstrings\b[^\n|;]*(?:usernoted|Cookies|QuickLook|Library/Keychains|Library/Messages|Google/Chrome|Slack|Firefox|MobileSync|Clipboard|\.ssh|\.aws|\.env\b|credentials)", "reading a credential or message store. Ask for specific non-secret lines"),
)]


def bash_check(cmd, eng, cwd):
    n = norm(cmd)
    raw = "\n".join(unquote_layers(n))
    allt = drop_display("\n".join(effective(n, cwd)))
    if "$(" in raw:
        allt = allt + "\n" + drop_display("\n".join(s for m in re.findall(r"\$\(([^()]*)\)", raw) for s in effective(norm(m), cwd)))

    for rx in EDIT_RES:
        if rx.search(raw):
            return denial("a command that weakens the redaction setup", SAFE["edit"])

    for rx, kind in HARD_TOOLS:
        if rx.search(allt):
            return denial("a command that exposes credentials or weakens the redaction setup",
                          SAFE.get(kind if kind in SAFE else "tool", SAFE["tool"]))

    w = write_to_protected(raw)
    if w:
        return denial(w, SAFE["edit"])

    if re.search(r"(?:^|[;&|(\n]\s*)\.\s+\S*(?:zshrc|bashrc|profile)\b|\bsource\s+\S*(?:zshrc|bashrc|profile)\b", allt, re.I):
        return denial("sourcing a shell rc file", SAFE["read"])

    lc = literal_cred(raw, allt)
    if lc:
        return denial(lc, "Reference it by name ($VAR or a file) and never type the value.")

    both = raw + "\n" + allt
    for rx, why in EXTRA_DENY:
        if why.startswith("sourcing an env") and (re.search(r"\b(?:env|printenv)\s*\|\s*grep\s+(?:-[a-zA-Z]+\s+)*\w+\s*$", raw)
                                                  or (re.search(r"(?:^|[;&|(\n]\s*)(?:echo|printf|printenv|env)\b", both) and "${#" not in both)):
            continue
        if rx.search(both):
            return denial(why, SAFE["read"] + " " + SAFE["status"])
    if _PATH_DENY.search(both) and re.search(r"\b(?:cp|ditto|rsync|scp|tar|zip|curl|nc|base64|xxd|od|openssl|python3?|node|ruby|perl|jq|plutil|sed|awk)\b", raw):
        return denial("a path that holds browser, message or backup data", SAFE["read"])
    if eng is not None:
        try:
            if (re.search(r"[^>&\d]>>?\s*[^\s&]|\btee\b|\bsed\s+-\S*i|\bcurl\b[^\n]*(?:\s-d\b|--data|\s-F\b|\?[\w%-]+=)", _unq(raw))
                    or re.search(r"\bgit\s+(?:\S+\s+)*commit\b|\bgh\s+(?:gist|issue|pr|release)\s+\w+|\bpb(?:copy)\b|\bbase64\b|\bxxd\b|\bawk\b|\bod\b|\buuencode\b|\bb2a_\w+", raw)) and (
                    eng.known_spans(raw, encoded=False) or eng.known_spans(urllib.parse.unquote(raw), encoded=False)):
                return denial("a known secret value inside the command", "Reference it by name ($VAR or a file) and never type the value.")
            if re.search(r"\b(?:echo|printf)\b[^|;&\n]*>>?\s*[^\s&]", _unq(raw)) and eng.has_secret(raw):
                return denial("writing a secret value into a file", "Reference it by name and never type the value.")
        except Exception as exc:
            return denial("could not analyse the command (%s)" % type(exc).__name__, SAFE["read"])
    srcs = [r for r in SOURCE_RES + TOOL_SRC_RES if r.search(allt)]
    secret_file = (bool(SECRET_FILES_RE.search(allt)) and not only_example_files(allt)) or bool(bash_sensitive(allt)) or bool(_EXTRA_FILE.search(allt))
    srcs_raw = [r for r in SOURCE_RES if r.search(raw)]
    if srcs_raw and not srcs:
        srcs = srcs_raw
    if (srcs or secret_file) and raw != allt:
        x = xform_hit(raw + "\n" + allt, srcs, secret_file, cwd)
        if x:
            return denial("a secret source combined with a transform or test (%s)" % x, SAFE["read"] + " " + SAFE["status"])
    if srcs or secret_file:
        x = xform_hit(allt, srcs, secret_file, cwd)
        if x:
            return denial("a secret source combined with a transform or test (%s)" % x, SAFE["read"] + " " + SAFE["status"])
        e = exfil_hit(allt, secret_file, srcs)
        if e:
            return denial(e, SAFE["read"])
    return None


def only_example_files(t):
    t2 = re.sub(r"\.env\.(?:example|sample|template|dist)\b", "", t, flags=re.I)
    t2 = re.sub(r"\.envrc\b", "", t2, flags=re.I)
    return not SECRET_FILES_RE.search(t2)


def strip_safe_literals(t):
    return re.sub(r"\$\{?[A-Za-z_][A-Za-z0-9_]*\}?|<[A-Za-z_ ]+>", "", t)


def write_to_protected(t):
    tl = t
    for m in re.finditer(r">>?\s*['\"]?([^\s'\"|;&<>)]+)", tl):
        tgt = m.group(1)
        if PROT_PATHS.search(tgt) or PROT_BASE.search(tgt):
            return "writing to a hook, settings or shell-startup file"
    if not PROT_PATHS.search(tl):
        return None
    if re.search(r"\btee\b|\bsed\s+(?:-\S+\s+)*-i|\bperl\s+(?:-\S+\s+)*-i|\bcp\b|\bmv\b|\brm\b|\bln\b|\btruncate\b|\binstall\b|\bchmod\b|\bchown\b|\bdd\b|\bsponge\b|\bmkdir\b|"
                 r"write_text|write_bytes|\.write\(|writeFile|appendFile|open\([^)]*['\"][wa]|json\.dump|\bgit\s+(?:checkout|restore|reset|stash|clean)|\bed\b|\bawk\b.*inplace|\bpatch\b|\btouch\b|\bunlink\b|\bshred\b|"
                 r"\bprintf\b[^|;&]*\|\s*tee|\bsetdefault\b|\bjq\b[^|;]*(?:del\(|\+\s*\{|=\s)", tl, re.I):
        if re.search(r"\b(?:cat|jq|head|tail|grep|less|sed\s+-n|stat|ls|wc|diff|file|python3?)\b", tl, re.I) and not re.search(
                r"\btee\b|\bsed\s+(?:-\S+\s+)*-i|\bcp\b|\bmv\b|\brm\b|\bln\b|\btruncate\b|write_text|\.write\(|open\([^)]*['\"][wa]|json\.dump|setdefault|\bjq\b[^|;]*(?:del\(|\+\s*\{|=\s)|\bgit\s+(?:checkout|restore|reset)", tl, re.I):
            return None
        return "modifying a hook, settings, startup or tamper-sensitive file"
    return None


def bash_sensitive(t):
    if re.search(r"\b(?:ls|stat|file|test|\[)\b", t) and not re.search(r"\b(?:cat|head|tail|less|more|grep|rg|sed|awk|strings|xxd|od|base64|sqlite3|cp|mv|tar|zip|ditto|rsync|scp|find|source|python3?|node|jq|plutil|type|bat|nl|cut|sort|uniq|wc|tee|open|xargs|curl|strings|ssh)\b", t):
        return None
    m = SENS_COMMON_RE.search(t.lower())
    if m:
        if re.search(r"\.ssh\b", m.group(0)) and re.search(r"\bssh-add\b|\bssh-keygen\s+-y\b", t):
            m2 = SENS_COMMON_RE.search(t.lower().replace(".ssh", ""))
            if not m2:
                return None
        if m.group(0) in ("tfplan",) and re.search(r"terraform\s+plan|\.gitignore", t):
            return None
        return "a path that holds secrets or session data (%s)" % m.group(0)[:30]
    return None


_SEARCH_PROGS = ("grep", "egrep", "fgrep", "rg")
_SEARCH_OP_CHARS = set("|&;()")
_SEARCH_SHORT_VALUE = {"grep": set("efmABCdDX"), "rg": set("efmABCgtrEMTjd")}
_SEARCH_LONG_VALUE = {"--regexp", "--file", "--max-count", "--after-context", "--before-context", "--context",
                      "--include", "--exclude", "--exclude-dir", "--label", "--glob", "--iglob", "--type", "--type-not",
                      "--replace", "--max-depth", "--encoding", "--threads", "--max-columns", "--color", "--colors", "--engine"}
_SEARCH_ORACLE_SHORT = set("cqlLob")
_SEARCH_ORACLE_LONG = {"--count", "--count-matches", "--quiet", "--silent", "--files-with-matches",
                       "--files-without-match", "--only-matching", "--byte-offset"}
_DOTENV_KEY = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][\w.-]*)\s*=", re.M)
_YAML_KEY = re.compile(r"^\s*-?\s*([A-Za-z_][\w.-]*)\s*:(?:\s|$)", re.M)
_JSON_KEY = re.compile(r"\"([A-Za-z_][\w.-]*)\"\s*:")
_IDENT = re.compile(r"[A-Za-z_][\w.-]*")
_UPPER_SNAKE = re.compile(r"[A-Z][A-Z0-9_]*")
_KEY_SCAN_BYTES = 1 << 20


def _search_tokens(line):
    lex = shlex.shlex(line, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    return list(lex)


def _search_parse(prog, args):
    short_val = _SEARCH_SHORT_VALUE[prog]
    flags, pats, pos = set(), [], []
    i = 0
    while i < len(args):
        a = args[i]
        i += 1
        if a == "--":
            pos.extend(args[i:])
            break
        if a.startswith("--"):
            name, eq, val = a.partition("=")
            if name in _SEARCH_LONG_VALUE:
                if not eq:
                    val = args[i] if i < len(args) else ""
                    i += 1
                if name == "--regexp":
                    pats.append(val)
                elif name == "--file":
                    pats.append(None)
            else:
                flags.add(name)
            continue
        if a.startswith("-") and len(a) > 1:
            k = 1
            while k < len(a):
                ch = a[k]
                k += 1
                if ch in short_val:
                    if k < len(a):
                        val = a[k:]
                    else:
                        val = args[i] if i < len(args) else ""
                        i += 1
                    if ch == "e":
                        pats.append(val)
                    elif ch == "f":
                        pats.append(None)
                    break
                flags.add(ch)
            continue
        pos.append(a)
    return flags, pats, pos


def _secret_path(f):
    return bool((SECRET_FILES_RE.search(f) and not only_example_files(f)) or _EXTRA_FILE.search(f))


def _file_keys(path, cwd):
    full = path if os.path.isabs(path) else os.path.join(cwd or os.getcwd(), path)
    try:
        with open(full, "rb") as fh:
            body = fh.read(_KEY_SCAN_BYTES).decode("utf-8", "replace")
    except OSError:
        return None
    keys = set(_DOTENV_KEY.findall(body)) | set(_YAML_KEY.findall(body))
    if body.lstrip()[:1] in ("{", "["):
        keys |= set(_JSON_KEY.findall(body))
    return keys or None


def _is_key_name(p, keys):
    q = p[1:] if p.startswith("^") else p
    if q.endswith("="):
        q = q[:-1]
    if keys is None:
        return bool(_UPPER_SNAKE.fullmatch(q))
    return bool(_IDENT.fullmatch(q)) and q in keys


def _search_unsafe_target(f, cwd):
    full = f if os.path.isabs(f) else os.path.join(cwd or os.getcwd(), f)
    return bool(re.search(r"[*?\[]", f)) or os.path.isdir(full)


def search_oracle_hit(text, cwd, secret_file):
    for line in text.split("\n"):
        try:
            toks = _search_tokens(line)
        except ValueError:
            toks = line.split()
        for i, tk in enumerate(toks):
            prog = os.path.basename(tk)
            if prog not in _SEARCH_PROGS:
                continue
            args, stop, j = [], None, i + 1
            while j < len(toks):
                t2 = toks[j]
                if any(c in "<>" for c in t2):
                    j += 2 if re.fullmatch(r"\d*[<>]+&?", t2) else 1
                    continue
                if t2.isdigit() and j + 1 < len(toks) and any(c in "<>" for c in toks[j + 1]):
                    j += 1
                    continue
                if t2 and set(t2) <= _SEARCH_OP_CHARS:
                    stop = t2
                    break
                args.append(t2)
                j += 1
            chained = stop in ("&&", "||")
            flags, pats, pos = _search_parse(prog, args)
            oracle = chained or any(len(f) == 1 and f in _SEARCH_ORACLE_SHORT for f in flags) or bool(flags & _SEARCH_ORACLE_LONG)
            if not oracle:
                continue
            if None in pats:
                return "a search that takes its pattern from a file"
            if pats:
                patterns, files = pats, pos
            elif pos:
                patterns, files = [pos[0]], pos[1:]
            else:
                return "a search with no pattern"
            targets = [f for f in files if _secret_path(f)]
            if (not files and secret_file) or any(_search_unsafe_target(f, cwd) for f in files if not _secret_path(f)):
                targets.append(None)
            for tgt in targets:
                keys = _file_keys(tgt, cwd) if tgt is not None else None
                if not all(_is_key_name(p, keys) for p in patterns):
                    return "a count, test or list whose pattern is not a key name"
    return None


def xform_hit(t, srcs, secret_file, cwd=None):
    low = re.sub(r"\btr\s+['\"]?\\0['\"]?\s+['\"]?\\?n['\"]?", " ", t)
    x = search_oracle_hit(low, cwd, secret_file)
    if x:
        return x
    # pipeline-aware: a transform only counts when it is not merely the source's own plain use
    s = SHELL_XFORM.search(low)
    if s and (secret_file or srcs):
        if re.search(r"\$\{#|\$\{\w+:\d", low):
            return "shell substring or length probe"
    plain_grep = re.compile(r"\bgrep\b(?!\s+-[a-zA-Z]*[cqo])")
    cleaned = low
    # oracle with value literal: grep -q/-c PATTERN where the pattern has a value after '='
    m = XFORM.search(cleaned)
    while m:
        tok = m.group(0).strip(" \t\n|;&(`{").lower()
        if tok.startswith("grep") or tok.startswith("egrep"):
            m = XFORM.search(cleaned, m.end())
            continue
        if tok in ("sed", ) or tok.startswith("sed"):
            seg = cleaned[m.start(): m.start() + 120]
            if re.search(r"sed\s+-i", seg):
                m = XFORM.search(cleaned, m.end())
                continue
        if tok.startswith("head -c") or tok.startswith("tail -c"):
            return tok
        if tok.startswith("python") or tok.startswith("node") or tok.startswith("ruby") or tok.startswith("perl") or tok.startswith("php"):
            if re.search(r"print\(\s*[\d\"'(]|console\.log\(\s*[\d\"'(]", cleaned) and not (secret_file or srcs):
                m = XFORM.search(cleaned, m.end())
                continue
            seg = cleaned[m.start():]
            if re.search(r"print\(\s*\d+\s*[+\-*/]\s*\d+\s*\)", seg) and not re.search(r"environ|getenv|process\.env|open\(|read|\.env|secret|token|key|stdin", seg, re.I):
                m = XFORM.search(cleaned, m.end())
                continue
            if GEN_RE.search(seg) and not re.search(r"environ|getenv|process\.env|open\(|stdin|\bread", seg, re.I):
                m = XFORM.search(cleaned, m.end())
                continue
            return "interpreter one-liner touching a secret source"
        if tok in ("gzip", "bzip2", "xz", "zstd", "strings", "less") and not re.search(r"\|\s*" + re.escape(tok), cleaned):
            m = XFORM.search(cleaned, m.end())
            continue
        if tok in ("wc",) or tok in ("sum", "bc", "dc"):
            return tok
        return tok
    return None


def exfil_hit(t, secret_file, srcs):
    low = t
    tool_srcs = [r for r in srcs if r in TOOL_SRC_RES and not r.search('sudo')]
    if re.search(r"\b(?:curl|wget|http|nc|ncat|telnet)\b[^|;&\n]*(?:-d\s*@|--data(?:-binary|-raw|-urlencode)?\s*@|-F\s*\S*=@|-T\s|--upload-file|-X\s*(?:POST|PUT)[^|;]*@)", low, re.I) and (secret_file or srcs):
        return "sending a secret source over the network"
    if re.search(r"\|\s*(?:curl|wget|nc|ncat|http|telnet|ssh|openssl\s+s_client|socat|tee\s+/dev/tcp)\b", low, re.I) and (secret_file or srcs) and not re.search(r"\|\s*ssh\b[^|]*$", "") :
        return "piping a secret source to the network"
    if re.search(r"\b(?:scp|rsync|sftp|ftp|rclone(?=\s)|aws\s+s3\s+cp|gsutil\s+cp|az\s+storage)\b", low, re.I) and secret_file:
        if re.search(r"[\w.-]+@[\w.:-]+:|\b(?:s3|gs)://|\brclone\s", low, re.I):
            return "copying a secret file off the machine"
    if re.search(r"\b(?:cp|mv|ln|install|ditto)\b", low) and secret_file:
        dest = re.findall(r"\b(?:cp|mv|ln|install|ditto)\s+(?:-\S+\s+)*(\S+)\s+(\S+)", low)
        for a, b in dest:
            if SECRET_FILES_RE.search(a) and not SECRET_FILES_RE.search(b):
                return "copying a secret file to a name that hides what it is"
            if SECRET_FILES_RE.search(a) and re.search(r"dropbox|icloud|clouddocs|onedrive|googledrive|cloudstorage|mobile documents|/tmp/|/volumes/", b):
                return "copying a secret file into a synced or shared location"
    if re.search(r">>?\s*['\"]?(?:\S*(?:dropbox|cloudstorage|mobile documents|onedrive|clouddocs|googledrive)\S*)", low, re.I) and (secret_file or srcs):
        return "writing a secret source into a synced folder"
    if re.search(r"\b(?:cat|env|printenv|kubectl|sops|op|security|aws|gcloud)\b[^|;&]*>>?\s*(?!/dev/null|/dev/stderr|&)['\"]?[^\s'\"|;&]+", low) and (secret_file or srcs):
        m = re.search(r">>?\s*['\"]?([^\s'\"|;&]+)", low)
        tgt = m.group(1) if m else ""
        if tgt and not SECRET_FILES_RE.search(tgt) and not tgt.startswith("&") and not re.fullmatch(r"\$\{?tmpdir\}?/(?:debug|out|env)[\w.-]*|\"?\$tmpdir\"?/debug\.txt", tgt):
            if re.search(r"\b(?:cat|less|head|tail|more|source|\.|grep)\s+['\"]?" + re.escape(tgt.strip("'\"")), low) or re.search(r"\b(?:kubectl|sops|op|security|aws|gcloud|gpg|age)\b", low):
                return "writing a secret source to a plain file that is read back"
    if tool_srcs and re.search(r">>?\s*(?!&|/dev/(?:null|std|tcp/(?:127\.0\.0\.1|localhost)/))['\"]?[\w$~./]|\|\s*(?:tee|pbcopy)\b|[\"'=]\$\(\s*(?:" + CRED_CMD + ")", low):
        return "sending a credential tool's output somewhere other than the screen"
    if re.search(r"\bmkfifo\b", low) and secret_file:
        return "relaying a secret file through a named pipe"
    if re.search(r"\b(?:cat|cp|ln)\s+\S*(?:secret\.env|\.env|\.dev\.vars)\b[^|;]*\s>\s*pipe|\bln\b\s+(?:-s\s+)?\S*(?:\.env|secret\.env)\s", low) and secret_file:
        return "linking or relaying a secret file"
    if re.search(r"\bdiff\s+<\(|\bcomm\s+|\bcmp\s+", low) and (secret_file or srcs):
        return "comparing a secret source"
    if re.search(r"\b(?:ssh|docker\s+exec|kubectl\s+exec)\b[^;&]*(?:/proc/\S*environ|\bprintenv\b[^;]*\|\s*(?:od|xxd|base64|cut|tr|rev))", low) and srcs:
        return "reading remote environment through a transform"
    return None


def read_check(tool, ti):
    paths = []
    for k in ("file_path", "path", "notebook_path", "filepath", "filename", "directory", "dir"):
        v = ti.get(k)
        if isinstance(v, str):
            paths.append(v)
    out = None
    for p in paths:
        if tool == "Glob" and re.search(r"coresimulator", p, re.I) and not SECRET_FILES_RE.search(p) and not SENS_COMMON_RE.search(p):
            continue
        r = sensitive_path(p, True)
        if r:
            return denial("%s is %s" % (os.path.basename(p) or p, r), SAFE["read"] + " Ask for a different, non-secret file.")
    pat = ti.get("pattern")
    if tool == "Glob" and isinstance(pat, str):
        pass
    if tool == "Grep":
        p = ti.get("path") or ""
        home_wide = re.fullmatch(r"(?:~|\$HOME|/Users(?:/[^/]+)?|/home(?:/[^/]+)?|\$TMPDIR|/private/var/folders[\w/.-]*|/var/folders[\w/.-]*|/tmp|/private/tmp|/)/?", p) is not None
        if home_wide and isinstance(pat, str) and re.search(r"secret|token|key|password|bearer|sk_|AKIA|eyJ|credential", pat, re.I):
            return denial("a credential search across the home or temp folder", "Search the project (path: src) instead.")
    return out


def string_leaves(o, out):
    if isinstance(o, str):
        out.append(o)
    elif isinstance(o, dict):
        for v in o.values():
            string_leaves(v, out)
    elif isinstance(o, list):
        for v in o:
            string_leaves(v, out)


SETTINGS_KEYS = re.compile(
    r"statusLine|apiKeyHelper|otelHeadersHelper|awsCredentialExport|awsAuthRefresh|fileSuggestion|\"hooks\"|disableAllHooks|"
    r"excludedCommands|\"sandbox\"|enableAllProjectMcpServers|mcpServers|ANTHROPIC_(?:BASE_URL|AUTH_TOKEN)|OTEL_|CLAUDE_CODE_|permissions", re.I)


def write_check(tool, ti, eng):
    paths = [ti.get(k) for k in ("file_path", "path", "notebook_path", "filepath", "target", "destination") if isinstance(ti.get(k), str)]
    texts = []
    for k, v in ti.items():
        if k in ("file_path", "path", "notebook_path", "filepath"):
            continue
        string_leaves(v, texts)
    body = "\n".join(texts)
    for p in paths:
        pn = re.sub(r"/+", "/", p.replace("\\\\", "/"))
        while re.search(r"/[^/.][^/]*/\.\./", pn):
            pn = re.sub(r"/[^/.][^/]*/\.\./", "/", pn, count=1)
        pn = re.sub(r"/\./", "/", pn)
        if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit") or "write" in tool.lower() or "edit" in tool.lower():
            if PROT_PATHS.search(pn) or PROT_BASE.search(pn) and CLAUDE_DIR.search(pn):
                return denial("editing a hook, settings or startup file", SAFE["edit"])
            if PROT_BASE.search(pn) and re.search(r"settings|managed|\.mcp", pn, re.I) and not re.search(r"/src/|docs?/", pn, re.I):
                if re.search(r"(?:^|/)\.claude/|managed-settings|\.mcp\.json", pn, re.I):
                    return denial("editing a hook, settings or startup file", SAFE["edit"])
            if re.search(r"\.command$|\.envrc$|sitecustomize\.py$|\.rprofile$|(?:^|/)\.(?:zshrc|bashrc|profile)$", pn, re.I) and (
                    re.search(r"\.command$", pn, re.I) or re.search(r"env\b|printenv|cat\s|\$\(|exec |script|curl|nc |os\.environ|Sys\.getenv", body)):
                return denial("writing a startup or launcher file that could run commands", SAFE["edit"])
            if re.search(r"\.github/workflows/", pn) and re.search(r"secrets\.|curl|env\b|printenv", body) and re.search(r"(?:curl|printenv|\benv\b)", body):
                return denial("a workflow that could send secrets out", SAFE["edit"])
            if re.search(r"(?:^|/)\.gitleaksignore$|(?:^|/)\.secretlintignore$", pn):
                return denial("editing a secret-scanner ignore list", SAFE["edit"])
            if tool == "Edit" and SECRET_FILES_RE.search(pn) and ti.get("old_string") and len(ti.get("new_string") or "") <= 2:
                return denial("probing a secret file by trial edits", "Read the file instead; reads are redacted.")
            if re.search(r"actuator/(?:env|heapdump)", body) and re.search(r"\bcurl\b|\bwget\b", body):
                return denial("a script that dumps a service's environment", SAFE["edit"])
            if SECRET_FILES_RE.search(pn) and "[REDACTED" in body:
                return denial("writing the redaction marker into a secret file would destroy the real value", "Edit the real value with your own editor.")
        if re.search(r"dropbox|cloudstorage|mobile documents|onedrive|clouddocs|google ?drive", pn, re.I):
            if SECRET_FILES_RE.search(pn) or eng is not None and (eng.has_secret(body) or re.search(r"\b(?:api[_-]?key|token|secret|passw)", body, re.I)):
                return denial("writing secrets into a synced folder", "Keep secrets out of cloud-synced folders.")
    if re.search(r"\[REDACTED(?::[^\]]*)?\]", body) and any(SECRET_FILES_RE.search(p) for p in paths):
        return denial("the redaction marker used as a value would overwrite a real secret", "Keep the real value; do not paste redacted output back into config files.")
    if eng is not None:
        try:
            if eng.has_secret(body):
                return denial("the content contains a secret value", "Reference it by name (process.env.NAME or a secrets manager) and never write the value.")
        except Exception as exc:
            return denial("could not analyse the content (%s)" % type(exc).__name__, SAFE["read"])
    return None


def generic_check(tool, ti, eng, writer=False):
    texts = []
    string_leaves(ti, texts)
    body = "\n".join(texts)
    if tool == "WebFetch":
        url = ti.get("url") or ""
        if re.match(r"\s*file:", url, re.I):
            return denial("fetching a local file through the web tool", "Ask for the specific non-secret output instead.")
        if re.search(r"pastebin|transfer\.sh|file\.io", url, re.I):
            return denial("fetching a recorded terminal session", "Ask for the specific non-secret output instead.")
        if re.match(r"https?://(?:[\w-]+\.)*(?:apple|github|githubusercontent|stripe|anthropic|openai|cloudflare|googleapis|slack|amazonaws|atlassian|linear|sentry|vercel|polar)\.(?:com|app|sh|io|dev)(?:[:/?]|$)", url, re.I):
            return None
    paths = [ti.get(k) for k in ("path", "file_path", "filepath", "source", "directory", "repo_path") if isinstance(ti.get(k), str)]
    if tool.startswith("mcp__") and re.search(r"git_(?:init|add|commit|push)|write|move|copy", tool, re.I) and re.search(r"(?:^|/)\.(?:ssh|aws|gnupg)(?:/|$)", " ".join(paths)):
        return denial("an MCP tool acting inside a credentials folder", "Work in the project folder instead.")
    if re.search(r"localStorage|sessionStorage|document\.cookie", body) and re.search(r"btoa|charCodeAt|encodeURI|toString\(16\)|fetch\(|XMLHttpRequest|sendBeacon", body):
        return denial("page script that transforms or sends stored tokens", "Read the page text instead; tokens are redacted.")
    if eng is not None:
        try:
            if eng.has_secret(body) or eng.known_spans(urllib.parse.unquote(body)):
                return denial("the request contains a secret value", "Reference it by name instead of sending the value.")
        except Exception as exc:
            return denial("could not analyse the request (%s)" % type(exc).__name__, SAFE["read"])
    return None


def decide(ev, eng):
    tool = ev.get("tool_name") or ""
    ti = ev.get("tool_input")
    if not isinstance(ti, dict):
        return None
    cwd = ev.get("cwd") if isinstance(ev.get("cwd"), str) else None
    if tool == "Bash":
        cmd = ti.get("command")
        if not isinstance(cmd, str):
            return None
        if ti.get("dangerouslyDisableSandbox") and re.search(r"/[^\s/]*(?:creds|credential|secret|token)[^\s/]*", cmd, re.I):
            return {"deny": denial("a Bash call that disables the sandbox", "Run the command without dangerouslyDisableSandbox.")}
        d = bash_check(cmd, eng, cwd)
        if d:
            return {"deny": d}
        import secret_engine as _e
        return {"rewrite": rewrite(cmd, _e.command_ctx("Bash", ti))}
    if tool == "Grep":
        gp = ti.get("path") or ""
        gpat = ti.get("pattern") or ""
        if isinstance(gp, str) and isinstance(gpat, str) and re.search(r"group\.com\.apple\.usernoted", gp) and re.search(r"\[0-9\]|\\d", gpat):
            return {"deny": denial("a Grep for codes in the notifications database", "Ask the owner to paste the notification text.")}
        if isinstance(gp, str) and isinstance(gpat, str) and SECRET_FILES_RE.search(gp) and re.search(r"=\s*[\w$-]{3,}|\bsk_(?:live|test)_", gpat) and not re.search(r"\[|\\w|\.\*|\\S", gpat.split("=", 1)[-1]):
            return {"deny": denial("a Grep that guesses a secret's value", "Read the file instead; values are redacted.")}
    if tool in ("Read", "Grep", "Glob", "NotebookRead", "LS"):
        return None
    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit", "SendMessage", "TaskCreate", "TaskUpdate", "SubagentHandback", "Agent", "Task", "WebFetch", "WebSearch") or tool.startswith("mcp__"):
        writer = tool in ("Write", "Edit", "MultiEdit", "NotebookEdit") or bool(re.search(r"write|edit|create|move|copy|update", tool, re.I))
        if writer:
            d = write_check(tool, ti, eng)
            if d:
                return {"deny": d}
        d = generic_check(tool, ti, eng, writer and tool in ("Write", "Edit", "MultiEdit", "NotebookEdit"))
        return {"deny": d} if d else None
    return None


FILTER = os.path.join(HERE, "secret_filter.py")


def sq(s):
    return "'" + s.replace("'", "'\\''") + "'"


def rewrite(cmd, ctx=0):
    f = sq(FILTER) + " " + str(int(ctx))
    head = (
        "__sg_py=$(command -v python3 || command -v python) || __sg_py=python3\n"
        "__sg_d=$(mktemp -d \"${TMPDIR:-/tmp}/sg.XXXXXX\") && mkfifo \"$__sg_d/o\" \"$__sg_d/e\" || { echo '[REDACTED: output withheld (filter unavailable)]' >&2; false; }\n"
        "( \"$__sg_py\" " + f + " < \"$__sg_d/o\" & echo $! > \"$__sg_d/po\" )\n"
        "( \"$__sg_py\" " + f + " < \"$__sg_d/e\" >&2 & echo $! > \"$__sg_d/pe\" )\n"
        "exec 7>&1 8>&2\n"
        "exec >\"$__sg_d/o\" 2>\"$__sg_d/e\"\n"
        "__sg_ue=; __sg_done=\n"
        "trap() { if [ $# -eq 2 ] && { [ \"$2\" = EXIT ] || [ \"$2\" = 0 ]; }; then __sg_ue=$1; else builtin trap \"$@\"; fi; }\n"
        "__sg_fin() { { set +x; } 2>/dev/null; __sg_rc=$?; [ -n \"$__sg_done\" ] && return $__sg_rc; __sg_done=1; "
        "if [ -n \"$__sg_ue\" ]; then __sg_u=$__sg_ue; __sg_ue=; eval \"$__sg_u\"; fi; "
        "exec >&7 2>&8 7>&- 8>&-; __sg_po=$(cat \"$__sg_d/po\" 2>/dev/null); __sg_pe=$(cat \"$__sg_d/pe\" 2>/dev/null); __sg_n=0; "
        "while { kill -0 $__sg_po 2>/dev/null || kill -0 $__sg_pe 2>/dev/null; } && [ $__sg_n -lt 100 ]; do sleep 0.1; __sg_n=$((__sg_n+1)); done; "
        "kill $__sg_po $__sg_pe 2>/dev/null; rm -rf \"$__sg_d\"; return $__sg_rc; }\n"
        "__sg_exit() { __sg_ec=$?; __sg_fin; exit $__sg_ec; }\n"
        "builtin trap __sg_exit EXIT\n"
    )
    return head + cmd + "\n__sg_x=$?; __sg_fin; (exit $__sg_x)\n"


def main():
    raw = sys.stdin.buffer.read()
    try:
        ev = json.loads(raw.decode("utf-8", "replace"))
    except ValueError:
        return
    if not isinstance(ev, dict):
        return
    try:
        import secret_engine as eng_mod
        cwd = ev.get("cwd") if isinstance(ev.get("cwd"), str) else None
        eng = eng_mod.Engine(cwd)
        d = decide(ev, eng)
    except Exception as exc:
        emit_deny("Blocked: the secret guard could not analyse this call (%s). Safe alternative: retry with a simpler command." % type(exc).__name__)
        return
    if not d:
        return
    if "deny" in d:
        emit_deny(d["deny"])
        return
    if "rewrite" in d:
        ti = dict(ev.get("tool_input"))
        ti["command"] = d["rewrite"]
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow", "updatedInput": ti}}
        os.write(1, json.dumps(out, ensure_ascii=True).encode("ascii"))


if __name__ == "__main__":
    main()
