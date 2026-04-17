#!/usr/bin/env bash
# Emit one JSON object per commit from the current git repo to stdout.
# Usage: git-events.sh [--since <git-date-spec>] [--until <git-date-spec>]
#
# Each JSON line has: sha, subject, author, email, date (ISO 8601),
# files_changed (int), insertions (int), deletions (int), is_revert (bool),
# is_merge (bool), tags (list<string>).

set -euo pipefail

since=""
until_=""

while [ $# -gt 0 ]; do
  case "$1" in
    --since) since="${2:-}"; shift 2 ;;
    --until) until_="${2:-}"; shift 2 ;;
    *) echo "git-events.sh: unknown arg: $1" >&2; exit 1 ;;
  esac
done

log_args=(log --reverse "--pretty=format:%H%x1f%s%x1f%an%x1f%ae%x1f%aI%x1f%P%x1f%D" --shortstat)
[ -n "$since" ]  && log_args+=(--since "$since")
[ -n "$until_" ] && log_args+=(--until "$until_")

git "${log_args[@]}" | python3 -c '
import json, re, sys

SEP = "\x1f"
SHORT_STAT_RE = re.compile(
    r"(\d+) files? changed(?:, (\d+) insertions?\(\+\))?(?:, (\d+) deletions?\(-\))?"
)

def emit(record):
    sys.stdout.write(json.dumps(record, ensure_ascii=False) + "\n")

current = None
for raw in sys.stdin:
    line = raw.rstrip("\n")
    if SEP in line:
        if current is not None:
            emit(current)
        sha, subject, author, email, date, parents, refs = line.split(SEP)
        tags = []
        for r in refs.split(", "):
            r = r.strip()
            if r.startswith("tag: "):
                tags.append(r[5:])
        current = {
            "sha": sha,
            "subject": subject,
            "author": author,
            "email": email,
            "date": date,
            "files_changed": 0,
            "insertions": 0,
            "deletions": 0,
            "is_revert": subject.lower().startswith("revert"),
            "is_merge": len(parents.split()) > 1,
            "tags": tags,
        }
    else:
        m = SHORT_STAT_RE.search(line)
        if m and current is not None:
            current["files_changed"] = int(m.group(1))
            current["insertions"] = int(m.group(2) or 0)
            current["deletions"] = int(m.group(3) or 0)

if current is not None:
    emit(current)
'
