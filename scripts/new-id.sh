#!/usr/bin/env bash
# Generate a collision-safe YYYY-MM-DD-<slug> ID.
# Usage: new-id.sh --slug <slug> [--date YYYY-MM-DD] [--dir <dir>]
#   --slug  required; [a-z0-9][a-z0-9-]*
#   --date  optional; defaults to today (UTC)
#   --dir   optional; if set, collision-check against *.md files in <dir>

set -euo pipefail

die() { echo "new-id.sh: $*" >&2; exit 1; }

slug=""
date_str=""
dir=""

while [ $# -gt 0 ]; do
  case "$1" in
    --slug) slug="${2:-}"; shift 2 ;;
    --date) date_str="${2:-}"; shift 2 ;;
    --dir)  dir="${2:-}";  shift 2 ;;
    *) die "unknown argument: $1" ;;
  esac
done

[ -n "$slug" ] || die "--slug is required"

# Validate slug: start with alnum, contain only [a-z0-9-], length 2..61
if ! printf '%s' "$slug" | grep -qE '^[a-z0-9][a-z0-9-]{1,60}$'; then
  die "invalid slug: must match [a-z0-9][a-z0-9-]{1,60}"
fi

if [ -z "$date_str" ]; then
  date_str="$(date -u +%Y-%m-%d)"
fi

if ! printf '%s' "$date_str" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
  die "invalid date: $date_str"
fi

candidate="${date_str}-${slug}"

if [ -n "$dir" ] && [ -d "$dir" ]; then
  n=1
  while [ -e "$dir/${candidate}.md" ]; do
    n=$((n + 1))
    candidate="${date_str}-${slug}-${n}"
  done
fi

printf '%s\n' "$candidate"
