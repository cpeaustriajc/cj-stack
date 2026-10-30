#!/usr/bin/env bash
# Claude Code statusline: where/ship state, budget, then one row per rate limit.
#
# Two things about the host worth knowing before editing:
#   - Each row is rendered with wrap="truncate", so anything past the terminal
#     width is silently cut — the rate limits at the tail are what you lose.
#     Segments carry a priority; the fit loop below drops high numbers first,
#     per line.
#   - Output is split on \n into one row per line, so multi-line is legal.
#
# Fields below were read off the 2.1.226 payload builder. worktree/pr/effort/
# fast_mode/rate_limits appear only when they apply. resets_at is epoch seconds.
# The payload has no field for the auto-compact window; it is resolved below.
# Runs on macOS bash 3.2: no associative arrays, mapfile or ${x,,}.

# Character-based ${#var} and substring, for the block bar.
[ -n "${LC_ALL:-}" ] || export LC_ALL=en_US.UTF-8

input=$(cat)

command -v jq >/dev/null 2>&1 || { printf 'statusline: install jq'; exit 0; }
have_git=; command -v git >/dev/null 2>&1 && have_git=1

# One jq pass — the previous version spawned a jq per field, ~20 per refresh.
eval "$(printf '%s' "$input" | jq -r '
  def s(v): (v // "") | tostring;
  # `//` treats false as absent, so booleans need their own extractor.
  def b(v): if v == null then "" else (v | tostring) end;
  (.context_window.current_usage // {}) as $u |
  @sh "session_id=\(s(.session_id))",
  @sh "cwd=\(s(.workspace.current_dir // .cwd))",
  @sh "model_name=\(s(.model.display_name))",
  @sh "model_id=\(s(.model.id))",
  @sh "vim_mode=\(s(.vim.mode))",
  @sh "output_style=\(s(.output_style.name))",
  @sh "effort=\(s(.effort.level))",
  @sh "fast_mode=\(b(.fast_mode))",
  @sh "thinking=\(b(.thinking.enabled))",
  @sh "wt_name=\(s(.worktree.name))",
  @sh "wt_branch=\(s(.worktree.branch))",
  @sh "wt_orig=\(s(.worktree.original_cwd))",
  @sh "agent_name=\(s(.agent.name))",
  @sh "pr_num=\(s(.pr.number))",
  @sh "pr_state=\(s(.pr.review_state))",
  @sh "used=\(s(.context_window.used_percentage))",
  @sh "ctx_size=\(s(.context_window.context_window_size))",
  @sh "ctx_has=\(if .context_window.current_usage then 1 else "" end)",
  @sh "ctx_used=\(($u.input_tokens // 0) + ($u.cache_read_input_tokens // 0) + ($u.cache_creation_input_tokens // 0))",
  @sh "ctx_cr=\($u.cache_read_input_tokens // 0)",
  @sh "dur_ms=\(.cost.total_duration_ms // 0)",
  @sh "r5=\(s(.rate_limits.five_hour.used_percentage))",
  @sh "r5_reset=\(s(.rate_limits.five_hour.resets_at))",
  @sh "r7=\(s(.rate_limits.seven_day.used_percentage))",
  @sh "r7_reset=\(s(.rate_limits.seven_day.resets_at))"
' 2>/dev/null)"

# Windows payload paths: basename and bash cd need forward slashes.
case "$cwd" in [A-Za-z]:[\\/]*) cwd=${cwd//\\//} ;; esac
case "$wt_orig" in [A-Za-z]:[\\/]*) wt_orig=${wt_orig//\\//} ;; esac

esc=$(printf '\033')
cyan="${esc}[36m"
green="${esc}[32m"
yellow="${esc}[33m"
red="${esc}[31m"
magenta="${esc}[35m"
magenta_b="${esc}[95m"
blue="${esc}[34m"
dim="${esc}[2m"
bold="${esc}[1m"
reset="${esc}[0m"

case "$model_id" in
  *opus*|*Opus*) model_color="$magenta" ;;
  *haiku*|*Haiku*) model_color="$blue" ;;
  *) model_color="$green" ;;
esac

int() { local n=${1%%.*}; [ -n "$n" ] && [ "$n" -eq "$n" ] 2>/dev/null && echo "$n" || echo 0; }

format_k() {
  local n; n=$(int "$1")
  if [ "$n" -ge 1000000 ]; then echo "$(( n / 1000000 ))M"
  elif [ "$n" -ge 1000 ]; then echo "$(( n / 1000 ))k"
  else echo "$n"; fi
}

trunc() {
  local t=$1 m=$2 head
  if [ "${#t}" -gt "$m" ]; then
    head=${t:0:$((m-1))}
    printf '%s…' "${head%"${head##*[![:space:]]}"}"
  else
    printf '%s' "$t"
  fi
}

# Lowercase, punctuation flattened, worktree- prefix dropped: enough to spot that
# "fix/a-b", "fix+a-b" and "worktree-fix-a-b" are all the same thing said thrice.
slug() { local s; s=$(printf '%s' "$1" | tr 'A-Z/+_.' 'a-z----'); printf '%s' "${s#worktree-}"; }

# The slider paints "max" with rainbow-animated, cycling the ramp per character.
# A statusline renders once, so take a fixed slice of the same ramp.
rainbow_ramp=(31 91 33 32 36 34 35)
rainbow() {
  local t=$1 i=0 out=""
  while [ "$i" -lt "${#t}" ]; do
    out="${out}${esc}[1;${rainbow_ramp[i % 7]}m${t:i:1}"
    i=$((i + 1))
  done
  printf '%s%s' "$out" "$reset"
}

heat() {
  local n; n=$(int "$1")
  if [ "$n" -ge 80 ]; then printf '%s' "$red"
  elif [ "$n" -ge 50 ]; then printf '%s' "$yellow"; fi
}

US=$(printf '\037')
segs=()
# add <line> <priority> <column> <text>
add() { segs+=("$1${US}$2${US}$3${US}$4"); }

# Width is best-effort: no tty (background/headless runs) means render in full and
# let the host truncate. Known width does two jobs — it sizes the long segments
# below, and it drives the drop loop at the end.
cols=0
if [ -n "${COLUMNS:-}" ] && [ "$COLUMNS" -gt 0 ] 2>/dev/null; then
  cols=$COLUMNS
elif size=$(stty size 2>/dev/null </dev/tty); then
  cols=${size#* }
fi

# A narrow terminal can't fit the must-keep segments at full length, so shrink
# them rather than lose the rate limits off the right edge.
place_max=28; branch_max=60; bar_width=16; rates_tight=; eff_short=
sep="   "
if [ "$cols" -gt 0 ] && [ "$cols" -lt 140 ]; then
  place_max=14; branch_max=40; bar_width=10
fi
if [ "$cols" -gt 0 ] && [ "$cols" -lt 100 ]; then
  place_max=10; branch_max=24; bar_width=6; rates_tight=1; eff_short=1; sep="  "
fi

now=$(date +%s)
cache_dir="${XDG_CACHE_HOME:-$HOME/.cache}/claude-statusline"
mkdir -p "$cache_dir" 2>/dev/null

# GNU first: on GNU, `stat -f` is filesystem mode and can exit 0 with junk.
mtime() { stat -c %Y "$1" 2>/dev/null || stat -f %m "$1" 2>/dev/null || echo 0; }
key_hash() { printf '%s' "$1" | cksum | tr ' ' '-'; }
# fresh <file> <ttl-seconds>
fresh() { [ -f "$1" ] && [ $(( now - $(mtime "$1") )) -lt "$2" ]; }

# Detached refresh, one per cache file. The lock is a directory because mkdir is
# atomic; a lock older than 60s is a crashed job. Never call this inside $( ).
bg_refresh() {
  local lock="$1.lock"
  if [ -d "$lock" ] && [ $(( now - $(mtime "$lock") )) -gt 60 ]; then rmdir "$lock" 2>/dev/null; fi
  mkdir "$lock" 2>/dev/null || return 0
  ( "$2" "$1"; rmdir "$lock" ) </dev/null >/dev/null 2>&1 &
  disown
}

run_timeout() {
  local secs=$1; shift
  if command -v timeout >/dev/null 2>&1; then timeout "$secs" "$@"
  elif command -v perl >/dev/null 2>&1; then perl -e 'alarm shift; exec @ARGV' "$secs" "$@"
  else "$@"; fi
}

# Background job: writes "<num> <state> <draft> <review|-> <ci>" or an empty file.
pr_fetch() {
  local tmp="$1.$$" out
  out=$(cd "$cwd" 2>/dev/null && run_timeout 8 gh pr view --json number,state,isDraft,reviewDecision,statusCheckRollup 2>/dev/null)
  if [ -n "$out" ]; then
    printf '%s' "$out" | jq -r '
      ([.statusCheckRollup[]?
        | ((.conclusion // .state // "") | ascii_upcase) as $c
        | ((.status // "") | ascii_upcase) as $st
        | if ($c | IN("FAILURE","ERROR","TIMED_OUT","CANCELLED","ACTION_REQUIRED","STARTUP_FAILURE")) then "f"
          elif ($c == "" or $c == "PENDING" or $c == "EXPECTED" or ($st | IN("IN_PROGRESS","QUEUED","PENDING","WAITING","REQUESTED"))) then "p"
          else "o" end]) as $r
      | [.number, .state, (.isDraft | tostring),
         ((.reviewDecision // "") | if . == "" then "-" else . end),
         (if ($r | length) == 0 then "none" elif ($r | index("f")) then "fail" elif ($r | index("p")) then "pend" else "ok" end)]
      | join(" ")' > "$tmp" 2>/dev/null || : > "$tmp"
  else
    : > "$tmp"
  fi
  mv "$tmp" "$1"
}

# Background job: listening ports whose owning process cwd is inside $ports_root.
ports_fetch() {
  local tmp="$1.$$" pids
  lsof -nP -iTCP -sTCP:LISTEN -Fpn 2>/dev/null \
    | awk '/^p/{p=substr($0,2)} /^n/{n=$0; sub(/.*:/,"",n); print p, n}' > "$tmp.l"
  pids=$(awk '{print $1}' "$tmp.l" | sort -u | paste -sd, -)
  if [ -n "$pids" ]; then
    lsof -a -d cwd -p "$pids" -Fpn 2>/dev/null \
      | awk -v root="$ports_root" '/^p/{p=substr($0,2)} /^n/{d=substr($0,2); if (d == root || index(d, root "/") == 1) print p}' > "$tmp.c"
    ps -o pid=,comm= -p "$pids" 2>/dev/null | awk '$2 ~ /(^|\/)claude$/{print $1}' > "$tmp.x"
    awk 'FILENAME==ARGV[1]{skip[$1]=1; next} FILENAME==ARGV[2]{if (!skip[$1]) ok[$1]=1; next} ok[$1]{print $2}' "$tmp.x" "$tmp.c" "$tmp.l" | sort -un | paste -sd' ' - > "$tmp"
  else
    : > "$tmp"
  fi
  rm -f "$tmp.l" "$tmp.c" "$tmp.x"
  mv "$tmp" "$1"
}

# --- Git: one status call carries branch, ahead/behind and dirty count ---
g_head=; g_oid=; g_ahead=0; g_behind=0; g_n=0
gs=; toplevel=
[ -n "$have_git" ] && gs=$(git --no-optional-locks -C "$cwd" status --porcelain=v2 --branch 2>/dev/null)
if [ -n "$gs" ]; then
  eval "$(printf '%s\n' "$gs" | awk '
    /^# branch.head/ {h=$3}
    /^# branch.oid/  {o=$3}
    /^# branch.ab/   {a=substr($3,2); b=substr($4,2)}
    !/^#/            {n++}
    END {printf "g_head=%s g_oid=%s g_ahead=%d g_behind=%d g_n=%d", h, o, a, b, n}')"
fi
[ -n "$have_git" ] && toplevel=$(git --no-optional-locks -C "$cwd" rev-parse --show-toplevel 2>/dev/null)

# --- Place: the project, not the worktree checkout ---
# A worktree dir is named after its branch, so basename(cwd) inside one just
# repeats the branch. original_cwd is the repo you actually came from.
if [ -n "$wt_orig" ]; then place=$(basename "$wt_orig"); else place=$(basename "$cwd"); fi
[ -n "$place" ] && add 1 1 1 "$(trunc "$place" "$place_max")"

# --- Branch ---
detached=
if [ -n "$wt_branch" ]; then
  branch=$wt_branch; in_wt=1
else
  branch=$g_head
  if [ "$branch" = "(detached)" ]; then branch="@${g_oid:0:7}"; detached=1; fi
  in_wt=
fi
if [ -n "$branch" ]; then
  shown=$branch
  if [ -n "$in_wt" ]; then
    # The harness derives the branch as worktree-<name>; that prefix is pure
    # overhead once "wt:" already says where you are. Prefer the name you typed.
    if [ -n "$wt_name" ] && [ "$(slug "$wt_name")" = "$(slug "$branch")" ]; then
      shown=$wt_name
    else
      shown=${branch#worktree-}
    fi
  fi

  on_default=
  if [ -z "$detached" ] && [ -n "$toplevel" ]; then
    default_branch=$(git -C "$cwd" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)
    default_branch=${default_branch#origin/}
    if [ -z "$default_branch" ]; then
      for cand_b in main master; do
        if git -C "$cwd" show-ref --verify --quiet "refs/heads/$cand_b" 2>/dev/null; then default_branch=$cand_b; break; fi
      done
    fi
    [ -n "$default_branch" ] && [ "$branch" = "$default_branch" ] && on_default=1
  fi

  if [ -n "$on_default" ]; then
    label="${bold}${red}${in_wt:+wt:}$(trunc "$shown" "$branch_max") ⚠${reset}"
  else
    label="${in_wt:+wt:}$(trunc "$shown" "$branch_max")"
  fi
  # The worktree name only earns space when it isn't the branch respelled.
  if [ -n "$in_wt" ] && [ -n "$wt_name" ] && [ "$(slug "$wt_name")" != "$(slug "$branch")" ]; then
    label="${label}${dim}@$(trunc "$wt_name" 16)${reset}"
  fi
  [ "$g_n" -gt 0 ] && label="${label} ${yellow}●${g_n}${reset}"
  [ "$g_ahead" -gt 0 ] && label="${label} ${dim}⇡${g_ahead}${reset}"
  [ "$g_behind" -gt 0 ] && label="${label} ${dim}⇣${g_behind}${reset}"
  add 1 1 2 "$label"
fi

# --- Mod state: modes and loop-brake streak, published by mods as files ---
# Each file is parsed on its own so a corrupt one cannot hide the other.
mod_mode=; mod_streak=0; mod_cap=3
mod_dir="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/mod-state"
case "$session_id" in ""|*[!A-Za-z0-9._-]*) ;; *)
  mod_m=; mod_l=
  [ -f "$mod_dir/$session_id.session-modes.json" ] && IFS= read -r -d '' mod_m < "$mod_dir/$session_id.session-modes.json"
  [ -f "$mod_dir/$session_id.loop-brake.json" ] && IFS= read -r -d '' mod_l < "$mod_dir/$session_id.loop-brake.json"
  if [ -n "$mod_m$mod_l" ]; then
    for mod_line in $(jq -rn --arg m "$mod_m" --arg l "$mod_l" '
      ($m | try fromjson catch {}) as $a
      | ($l | try fromjson catch {}) as $b
      | (if ($a.mode | IN("audit","no-pr","chat")) then "m:\($a.mode)" else empty end),
        (if ($b.streak | type) == "number" then
           "s:\($b.streak | floor):\(if ($b.cap | type) == "number" then $b.cap | floor else 3 end)"
         else empty end)
    ' 2>/dev/null); do
      case "$mod_line" in
        m:*) mod_mode=${mod_line#m:} ;;
        s:*) mod_rest=${mod_line#s:}; mod_streak=$(int "${mod_rest%%:*}"); mod_cap=$(int "${mod_rest##*:}") ;;
      esac
    done
  fi
  ;;
esac
case "$mod_mode" in
  audit) add 1 1 3 "${bold}${yellow}audit mode${reset}" ;;
  no-pr) add 1 1 3 "${bold}${yellow}no-PR mode${reset}" ;;
  chat)  add 1 1 3 "${bold}${yellow}chat mode${reset}" ;;
esac
[ "$mod_streak" -gt 0 ] && add 2 1 3 "${yellow}loop ${mod_streak}/${mod_cap}${reset}"

# --- PR for this branch: cached gh result, refreshed off the render path ---
pr_ci=
if [ -n "$toplevel" ] && [ -n "$branch" ] && [ -z "$detached" ] && command -v gh >/dev/null 2>&1; then
  pr_file="$cache_dir/pr-$(key_hash "$toplevel|$branch")"
  fresh "$pr_file" 60 || bg_refresh "$pr_file" pr_fetch
  if [ -f "$pr_file" ]; then
    read -r c_num c_state c_draft c_review c_ci < "$pr_file"
    if [ -n "$c_num" ]; then
      pr_num=$c_num; pr_gstate=$c_state; pr_ci=$c_ci
      if [ "$c_state" = "OPEN" ]; then
        if [ "$c_draft" = "true" ]; then pr_state=draft
        elif [ "$c_review" = "APPROVED" ]; then pr_state=approved
        elif [ "$c_review" = "CHANGES_REQUESTED" ]; then pr_state=changes_requested
        else pr_state=; fi
      fi
    else
      pr_num=; pr_state=
    fi
  fi
fi
if [ -n "$pr_num" ]; then
  case "${pr_gstate:-OPEN}" in
    MERGED) add 1 2 3 "${yellow}#${pr_num} merged → new branch${reset}" ;;
    CLOSED) add 1 2 3 "${dim}#${pr_num} closed${reset}" ;;
    *)
      case "$pr_state" in
        approved)          pr_word=" approved" ;;
        changes_requested) pr_word=" ${red}changes requested${reset}" ;;
        draft)             pr_word=" ${dim}draft${reset}" ;;
        *)                 pr_word= ;;
      esac
      add 1 2 3 "#${pr_num}${pr_word}"
      case "$pr_ci" in
        fail) add 1 2 3 "${red}checks ✗${reset}" ;;
        pend) add 1 2 3 "${yellow}checks ◷${reset}" ;;
        ok)   add 1 2 3 "${dim}checks${reset} ${green}✔${reset}" ;;
      esac
      ;;
  esac
fi

# --- Listening ports owned by processes running inside this repo ---
ports_root=${toplevel:-$cwd}
if [ -n "$ports_root" ] && command -v lsof >/dev/null 2>&1; then
  ports_file="$cache_dir/ports-$(key_hash "$ports_root")"
  fresh "$ports_file" 10 || bg_refresh "$ports_file" ports_fetch
  if [ -s "$ports_file" ]; then
    ports_out=
    for p in $(cat "$ports_file"); do ports_out="${ports_out:+$ports_out }:$p"; done
    add 1 2 3 "${dim}${ports_out}${reset}"
  fi
fi

[ -n "$agent_name" ] && add 1 2 3 "${dim}agent:${agent_name}${reset}"

if [ -n "$output_style" ] && [ "$output_style" != "default" ]; then
  add 1 3 3 "${dim}${output_style}${reset}"
fi

if [ -n "$vim_mode" ]; then
  if [ "$vim_mode" = "NORMAL" ]; then add 1 1 3 "${bold}${yellow}NORMAL${reset}"
  else add 1 1 3 "${bold}${cyan}INSERT${reset}"; fi
fi

# --- Model, effort, fast mode, thinking ---
if [ -n "$model_name" ]; then
  # Labels are the /effort slider's own; max gets the slider's rainbow.
  case "$effort" in
    low) eff_t=low; eff_s=lo ;;
    medium) eff_t=medium; eff_s=md ;;
    high) eff_t=high; eff_s=hi ;;
    xhigh) eff_t=xhigh; eff_s=xh ;;
    max) eff_t=max; eff_s=max ;;
    *) eff_t=; eff_s= ;;
  esac
  [ -n "$eff_short" ] && eff_t=$eff_s
  label="$model_name"
  if [ -n "$eff_t" ]; then
    if [ "$effort" = "max" ]; then eff_out=$(rainbow "$eff_t")
    else eff_out="${dim}${eff_t}${reset}"; fi
    label="${label} ${eff_out}"
  fi
  [ "$fast_mode" = "true" ] && label="${label} ${yellow}⚡${reset}"
  [ "$thinking" = "false" ] && label="${label} ${dim}nothink${reset}"
  add 2 1 1 "$label"
fi

# --- Auto-compact window: the budget that matters, not the full context window ---
# Precedence mirrors Claude Code: env, per-model setting, global setting, full window.
win=$(int "$ctx_size")
cand=$(int "${CLAUDE_CODE_AUTO_COMPACT_WINDOW:-}")
if [ "$cand" -eq 0 ] && [ -f "$HOME/.claude/settings.json" ]; then
  cand=$(int "$(jq -r --arg a "$model_id" --arg b "${model_id%%\[*}" '
    (.modelSettings // {}) as $m
    | ($b | sub("-[0-9]{8}$"; "")) as $c
    | ($m[$a].autoCompactWindow // $m[$b].autoCompactWindow // $m[$c].autoCompactWindow // .autoCompactWindow // "") | tostring
  ' "$HOME/.claude/settings.json" 2>/dev/null)")
fi
if [ "$cand" -gt 0 ] && { [ "$win" -eq 0 ] || [ "$cand" -lt "$win" ]; }; then win=$cand; fi

# --- Context bar against that window ---
if [ "$win" -gt 0 ] || [ -n "$used" ]; then
  if [ "$win" -gt 0 ]; then
    if [ -n "$ctx_has" ]; then pct=$(( ctx_used * 100 / win )); else pct=0; fi
  else
    pct=$(int "$used")
  fi
  if [ "$pct" -ge 90 ]; then bar_color=$red
  elif [ "$pct" -ge 70 ]; then bar_color=$yellow
  else bar_color=$model_color; fi

  full='━━━━━━━━━━━━━━━━'; empty='────────────────'
  # A non-UTF-8 locale would make these count as bytes; fall back to ASCII.
  [ ${#full} -ne 16 ] && { full='================'; empty='----------------'; }
  filled=$(( pct * bar_width / 100 ))
  [ "$filled" -gt "$bar_width" ] && filled=$bar_width

  usage=""
  if [ "$win" -gt 0 ]; then
    if [ -n "$ctx_has" ]; then
      num=""; [ "$pct" -ge 70 ] && num=$bar_color
      usage=" ${num}$(format_k "$ctx_used")/$(format_k "$win")${num:+${reset}}"
      if [ "$pct" -ge 70 ]; then
        left_tok=$(( win - ctx_used )); [ "$left_tok" -lt 0 ] && left_tok=0
        usage="${usage} ${bar_color}$(format_k "$left_tok") left${reset}"
      fi
    else usage=" ${dim}—/$(format_k "$win")${reset}"; fi
  fi
  add 2 1 2 "${bar_color}${full:0:$filled}${reset}${dim}${empty:0:$((bar_width - filled))}${reset}${usage}"
fi

# --- Cache hit rate of the last call ---
if [ -n "$ctx_has" ] && [ "$ctx_used" -gt 0 ]; then
  cache_pct=$(( ctx_cr * 100 / ctx_used ))
  if [ "$cache_pct" -ge 80 ]; then cache_c=
  elif [ "$cache_pct" -ge 40 ]; then cache_c=$yellow
  else cache_c=$red; fi
  add 2 2 3 "${dim}cache${reset} ${cache_c}${cache_pct}%${reset}"
fi

# --- Rate limits: one row each, gauge with a pace tick at how far through the window we are ---
g_full='━'; g_empty='─'; g_tick='│'
[ ${#g_full} -ne 1 ] && { g_full='='; g_empty='-'; g_tick='|'; }

week_clock() {
  local t; t=$(date -r "$1" '+%a %l:%M %p' 2>/dev/null || date -d "@$1" '+%a %l:%M %p' 2>/dev/null)
  printf '%s' "${t/  / }"
}
hour_clock() {
  local t; t=$(date -r "$1" '+%l:%M %p' 2>/dev/null || date -d "@$1" '+%l:%M %p' 2>/dev/null)
  printf '%s' "${t# }"
}

# rate_row <row> <label> <used> <resets_at> <window-s> <min-elapsed-s> <red-gap-s> <five|week>
# State: red at 100%, or when the projected run-out is >= red-gap before reset or used >= 90;
# yellow when it runs out before reset; calm otherwise or while pace is undefined.
rate_row() {
  local row=$1 label=$2 raw=$3 rst=$4 win_s=$5 min_s=$6 gap_s=$7 kind=$8
  local u end start=0 el=-1 left=0 state=calm pace= out_at= fc= w fill tick i g= dur h m rtxt
  u=$(int "$(printf '%.0f' "$raw" 2>/dev/null)")
  end=$(int "$rst")
  if [ "$end" -gt "$now" ]; then
    start=$(( end - win_s )); el=$(( now - start )); left=$(( end - now ))
    [ "$el" -lt 0 ] && el=0
    [ "$el" -gt "$win_s" ] && el=$win_s
  fi
  if [ "$u" -ge 100 ]; then state=red
  elif [ "$u" -gt 0 ] && [ "$el" -ge "$min_s" ]; then
    pace=1
    out_at=$(( start + el * 100 / u ))
    if [ "$out_at" -ge "$end" ]; then out_at=
    elif [ $(( end - out_at )) -ge "$gap_s" ] || [ "$u" -ge 90 ]; then state=red
    else state=yellow; fi
  fi
  case "$state" in red) fc=$red ;; yellow) fc=$yellow ;; esac

  w=$bar_width
  fill=$(( (u * w + 50) / 100 )); [ "$fill" -gt "$w" ] && fill=$w
  tick=-1
  if [ "$el" -ge 0 ]; then
    tick=$(( (el * w * 2 + win_s) / (2 * win_s) )); [ "$tick" -gt $(( w - 1 )) ] && tick=$(( w - 1 ))
  fi
  i=0
  while [ "$i" -lt "$w" ]; do
    if [ "$i" -eq "$tick" ]; then g="${g}${dim}${g_tick}${reset}"
    elif [ "$i" -lt "$fill" ]; then g="${g}${fc}${g_full}${fc:+$reset}"
    else g="${g}${dim}${g_empty}${reset}"; fi
    i=$(( i + 1 ))
  done
  add "$row" 1 1 "${dim}${label}${reset}"
  add "$row" 1 2 "${g} ${fc}${u}%${fc:+$reset}"

  [ "$kind" = week ] && [ -n "$pace" ] && [ -z "$out_at" ] && [ -z "$rates_tight" ] && {
    add "$row" 1 3 "${dim}$(( ((100 - u) * 86400 * 2 + left) / (2 * left) ))%/day${reset}"
  }
  if [ -n "$out_at" ]; then
    if [ "$kind" = week ]; then add "$row" 1 3 "${fc}out ~$(week_clock "$out_at")${reset}"
    else add "$row" 1 3 "${fc}out ~$(hour_clock "$out_at")${reset}"; fi
  fi
  if [ "$left" -gt 0 ]; then
    if [ "$kind" = week ]; then
      if [ -n "$rates_tight" ]; then rtxt="↻$(week_clock "$end")"; else rtxt="resets $(week_clock "$end")"; fi
    else
      h=$(( left / 3600 )); m=$(( (left % 3600) / 60 ))
      if [ "$h" -gt 0 ]; then dur=$(printf '%dh%02dm' "$h" "$m"); else dur="${m}m"; fi
      if [ -n "$rates_tight" ]; then rtxt="↻${dur}"; else rtxt="resets in ${dur}"; fi
    fi
    if [ "$u" -ge 100 ]; then add "$row" 1 3 "${red}${rtxt}${reset}"
    else add "$row" 1 3 "${dim}${rtxt}${reset}"; fi
  fi
}
[ -n "$r5" ] && rate_row 3 "5-hour" "$r5" "$r5_reset" 18000 1800 1800 five
[ -n "$r7" ] && rate_row 4 "week" "$r7" "$r7_reset" 604800 43200 86400 week


# --- Session time ---
dur_min=$(( $(int "$dur_ms") / 60000 ))
if [ "$(int "$dur_ms")" -gt 0 ]; then
  if [ "$dur_min" -ge 60 ]; then dur_txt=$(printf '%dh%02dm' $(( dur_min / 60 )) $(( dur_min % 60 )))
  else dur_txt="${dur_min}m"; fi
  add 2 3 3 "${dim}${dur_txt}${reset}"
fi

# --- Instruction size: only speaks when the always-loaded files blow the budget ---
instr_limit=150000
instr_root=${toplevel:-$cwd}
if [ -n "$instr_root" ]; then
  instr_file="$cache_dir/instr-$(key_hash "$instr_root")"
  if ! fresh "$instr_file" 60; then
    {
      cat "$HOME/.claude/CLAUDE.md" "$instr_root/CLAUDE.md" "$instr_root/CLAUDE.local.md" "$instr_root/AGENTS.md" 2>/dev/null
      [ -d "$instr_root/.claude/rules" ] && find "$instr_root/.claude/rules" -name '*.md' -type f -exec cat {} + 2>/dev/null
    } | wc -m | tr -d ' ' > "$instr_file.$$" && mv "$instr_file.$$" "$instr_file"
  fi
  instr_chars=$(int "$(cat "$instr_file" 2>/dev/null)")
  if [ "$instr_chars" -gt "$instr_limit" ]; then
    add 2 1 3 "${red}instr $(( instr_chars / 1000 ))k/$(( instr_limit / 1000 ))k${reset}"
  fi
fi

# render <line> <max-priority>: the unaligned fallback
render() {
  local out="" s l p t rest
  for s in "${segs[@]}"; do
    l=${s%%"$US"*}; rest=${s#*"$US"}
    p=${rest%%"$US"*}; rest=${rest#*"$US"}; t=${rest#*"$US"}
    [ "$l" = "$1" ] || continue
    [ "$p" -gt "$2" ] && continue
    out="${out:+${out}${sep}}${t}"
  done
  printf '%s' "$out"
}

# Sets VL (no subshell: this runs per cell per priority on the render path).
vlen() {
  local s=$1 o=""
  while [[ $s == *"$esc"* ]]; do o+=${s%%"$esc"*}; s=${s#*"$esc"}; s=${s#*m}; done
  VL=$(( ${#o} + ${#s} ))
}

# cell <line> <col> <max-priority>: the column's segments joined by the gap
cell() {
  local out="" s l p c t rest
  for s in "${segs[@]}"; do
    l=${s%%"$US"*}; rest=${s#*"$US"}
    p=${rest%%"$US"*}; rest=${rest#*"$US"}
    c=${rest%%"$US"*}; t=${rest#*"$US"}
    [ "$l" = "$1" ] && [ "$c" = "$2" ] && [ "$p" -le "$3" ] || continue
    out="${out:+${out}${sep}}${t}"
  done
  printf '%s' "$out"
}

# aligned <max-priority>: sets ALN1..ALN4 and ALN_W (widest line); a column empty on both lines takes no gap
aligned() {
  local c ln v k pad line total=0 n=0 off=0
  local widths=() cells=()
  for c in 1 2 3; do
    widths[c]=0
    for ln in 1 2 3 4; do
      v=$(cell "$ln" "$c" "$1"); cells[ln*4+c]=$v
      vlen "$v"; [ "$VL" -gt "${widths[c]}" ] && widths[c]=$VL
    done
    [ "${widths[c]}" -gt 0 ] && { total=$(( total + widths[c] )); n=$(( n + 1 )); }
  done
  [ "$n" -gt 1 ] && total=$(( total + (n - 1) * ${#sep} ))
  ALN_W=$total
  for ln in 1 2 3 4; do
    line=""; k=0
    for c in 1 2 3; do
      [ "${widths[c]}" -gt 0 ] || continue
      k=$(( k + 1 ))
      v=${cells[ln*4+c]}
      if [ "$k" -lt "$n" ]; then
        vlen "$v"; pad=$(( widths[c] - VL ))
        line="${line}${v}$(printf '%*s' "$pad" '')${sep}"
      else
        line="${line}${v}"
      fi
    done
    line=${line%"${line##*[![:space:]]}"}
    printf -v "ALN$ln" '%s' "$line"
  done
  offs=""
  for c in 1 2; do
    [ "${widths[c]}" -gt 0 ] && { off=$(( off + widths[c] + ${#sep} )); offs="$offs $off"; }
  done
}

# Fit to the terminal rather than letting the host truncate the tail.
fit() {
  local ln=$1 out max
  out=$(render "$ln" 4)
  if [ "$cols" -gt 20 ] 2>/dev/null; then
    for max in 4 3 2 1; do
      out=$(render "$ln" "$max")
      vlen "$out"
      [ "$VL" -le $(( cols - 2 )) ] && break
    done
  fi
  printf '%s' "$out"
}

use_aligned=
if [ "$cols" -gt 20 ] 2>/dev/null; then
  for max in 4 3 2 1; do
    aligned "$max"
    [ "$ALN_W" -le $(( cols - 2 )) ] && { use_aligned=1; break; }
  done
else
  aligned 4; use_aligned=1
fi
if [ -n "$use_aligned" ]; then
  line1=$ALN1; line2=$ALN2; line3=$ALN3; line4=$ALN4
  [ -n "${STATUSLINE_DEBUG_COLS:-}" ] && echo "ALIGN$offs" >&2
else
  line1=$(fit 1); line2=$(fit 2); line3=$(fit 3); line4=$(fit 4)
  [ -n "${STATUSLINE_DEBUG_COLS:-}" ] && echo "FALLBACK" >&2
fi
result=""
for line in "$line1" "$line2" "$line3" "$line4"; do
  [ -n "$line" ] && result="${result:+${result}$'\n'}${line}"
done
printf '%s' "$result"
