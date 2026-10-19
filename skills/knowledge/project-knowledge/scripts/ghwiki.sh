#!/usr/bin/env bash
# One managed clone per GitHub wiki, shared by every session and agent.
# Usage: ghwiki.sh <detect|path|list|save|push|status> [owner/repo] [-m message]
# GHWIKI_REMOTE overrides the wiki URL (a local bare repo, for tests).
set -euo pipefail

cmd=${1:?usage: ghwiki.sh <detect|path|list|save|push|status> [owner/repo] [-m msg]}
shift
repo="" msg=""
while [ $# -gt 0 ]; do
  case $1 in
    -m) msg=${2:?-m needs a message}; shift 2 ;;
    *) repo=$1; shift ;;
  esac
done

if [ -z "$repo" ]; then
  url=$(git remote get-url origin 2>/dev/null) || { echo "no owner/repo given and no origin remote" >&2; exit 2; }
  repo=$(printf '%s' "$url" | sed -E 's#^(git@|https://)github\.com[:/]##; s#\.git$##')
fi
case $repo in */*) ;; *) echo "expected owner/repo, got '$repo'" >&2; exit 2 ;; esac

remote=${GHWIKI_REMOTE:-https://github.com/$repo.wiki.git}
dir=${XDG_CACHE_HOME:-$HOME/.cache}/project-knowledge/github/$repo
[ -n "${GHWIKI_REMOTE:-}" ] && dir=$dir-test

git_auth() {
  if [ -z "${GHWIKI_REMOTE:-}" ]; then
    git -c credential.helper='!gh auth git-credential' "$@"
  else
    git "$@"
  fi
}

ensure_clone() {
  if [ -d "$dir/.git" ]; then
    if [ -z "$(git -C "$dir" status --porcelain)" ]; then
      git_auth -C "$dir" pull -q --rebase >&2 || echo "warning: pull failed; using the cached copy" >&2
    else
      echo "note: uncommitted changes in $dir; not pulling" >&2
    fi
  else
    mkdir -p "$(dirname "$dir")"
    git_auth clone -q "$remote" "$dir" >&2
  fi
}

commit_all() {
  [ -n "$msg" ] || { echo "$cmd needs -m \"message\"" >&2; exit 2; }
  git -C "$dir" add -A
  if git -C "$dir" diff --cached --quiet; then
    echo "nothing to commit" >&2
  else
    git -C "$dir" commit -q -m "$msg"
    echo "committed $(git -C "$dir" rev-parse --short HEAD)" >&2
  fi
}

case $cmd in
  detect)
    if git_auth ls-remote "$remote" HEAD >/dev/null 2>&1; then
      echo exists
    elif [ -z "${GHWIKI_REMOTE:-}" ] && [ "$(gh api "repos/$repo" --jq .has_wiki 2>/dev/null)" = "true" ]; then
      echo missing
    else
      echo disabled
    fi ;;
  path) ensure_clone; echo "$dir" ;;
  list) ensure_clone; (cd "$dir" && ls -1 *.md 2>/dev/null | sed 's/\.md$//; s/-/ /g') ;;
  save) [ -d "$dir/.git" ] || ensure_clone; commit_all ;;
  push)
    [ -d "$dir/.git" ] || ensure_clone
    commit_all
    git_auth -C "$dir" pull -q --rebase >&2 || { echo "rebase conflict: resolve in $dir, then push again. Never force." >&2; exit 1; }
    git_auth -C "$dir" push -q origin HEAD >&2
    echo "pushed $(git -C "$dir" rev-parse --short HEAD)" >&2 ;;
  status)
    [ -d "$dir/.git" ] || { echo "no clone yet at $dir"; exit 0; }
    git -C "$dir" status --short
    git_auth -C "$dir" fetch -q >&2 || true
    git -C "$dir" rev-list --left-right --count 'HEAD...@{u}' 2>/dev/null | awk '{print "ahead " $1 ", behind " $2}' ;;
  *) echo "unknown command: $cmd" >&2; exit 2 ;;
esac
