#!/usr/bin/env python3
"""from-git-log: bridge git history to lore candidate drafts.

Layer-3 adapter. Reads git-events.sh JSON output, classifies commits into
journal (deploy/release) or try-failed-exp (revert) candidates, and writes
frontmatter-populated draft .md files to .lore/.harvest/.

CLI
---
  python3 scripts/from-git-log.py [--since DATE] [--last N]
                                   [--out DIR] [--dry-run]
                                   [--repo DIR]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterator

# Plugin root: this file lives at <plugin-root>/scripts/from-git-log.py
PLUGIN_ROOT = Path(__file__).resolve().parent.parent

DEPLOY_RE = re.compile(
    r"\b(deploy|release|hotfix|rollout|ship|publish|cut)\b", re.IGNORECASE
)

SLUG_MAX = 50
_SLUG_STRIP_PREFIX = re.compile(r"^revert\s+\"?", re.IGNORECASE)
_SLUG_STRIP_QUOTES = re.compile(r'"')
_SLUG_NONALNUM = re.compile(r"[^a-z0-9]+")


def make_slug(subject: str) -> str:
    """Convert a commit subject to a lore ID slug (max SLUG_MAX chars)."""
    s = _SLUG_STRIP_PREFIX.sub("", subject)
    s = _SLUG_STRIP_QUOTES.sub("", s)
    s = s.lower()
    s = _SLUG_NONALNUM.sub("-", s)
    s = s.strip("-")
    s = s[:SLUG_MAX].rstrip("-")
    return s or "unnamed"


def classify(event: dict) -> str | None:
    """Return 'try-failed-exp', 'journal', or None (skip)."""
    if event.get("is_revert"):
        return "try-failed-exp"
    if event.get("tags"):
        return "journal"
    if DEPLOY_RE.search(event.get("subject", "")):
        return "journal"
    return None


def _event_date(event: dict) -> str:
    return str(event["date"])[:10]


def _safe_title(subject: str) -> str:
    return subject.replace('"', "'")


def draft_journal(event: dict) -> str:
    date = _event_date(event)
    slug = make_slug(str(event["subject"]))
    record_id = f"{date}-{slug}"
    event_time = str(event["date"]).replace("+00:00", "Z")
    sha_short = str(event["sha"])[:12]

    return (
        f"---\n"
        f"id: {record_id}\n"
        f"type: journal\n"
        f"tier: live\n"
        f'date: "{date}"\n'
        f'title: "{_safe_title(str(event["subject"]))}"\n'
        f"authors:\n"
        f'  - "{event["email"]}"\n'
        f"profile: git-commit\n"
        f'event-time: "{event_time}"\n'
        f"outcome: observed\n"
        f"---\n"
        f"\n"
        f"<!-- Commit: {sha_short} ({event_time}) -->\n"
        f"<!-- Subject: {event['subject']} -->\n"
        f"\n"
        f"## What happened\n"
        f"\n"
        f"TODO: Describe what this event was and its outcome.\n"
    )


def draft_tfe(event: dict) -> str:
    date = _event_date(event)
    slug = make_slug(str(event["subject"]))
    record_id = f"{date}-{slug}"
    sha_short = str(event["sha"])[:12]

    return (
        f"---\n"
        f"id: {record_id}\n"
        f"type: try-failed-exp\n"
        f"tier: canon\n"
        f'date: "{date}"\n'
        f'title: "{_safe_title(str(event["subject"]))}"\n'
        f"authors:\n"
        f'  - "{event["email"]}"\n'
        f"profile: revert-commit\n"
        f"status: on-hold\n"
        f"---\n"
        f"\n"
        f"<!-- Commit: {sha_short} ({event['date']}) -->\n"
        f"<!-- Subject: {event['subject']} -->\n"
        f"\n"
        f"## What was reverted\n"
        f"\n"
        f"TODO: Describe what the reverted commit was attempting to accomplish.\n"
        f"\n"
        f"## Why reverted\n"
        f"\n"
        f"TODO: Describe the reason for the revert (broken tests, production error, etc.).\n"
        f"\n"
        f"## Don't retry unless\n"
        f"\n"
        f"TODO: List specific, falsifiable conditions under which this approach could be retried.\n"
    )


def stream_events(
    script_path: Path, since: str | None, repo: Path
) -> Iterator[dict]:
    """Yield parsed event dicts from git-events.sh output."""
    cmd = ["bash", str(script_path)]
    if since:
        cmd += ["--since", since]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo)
    if result.returncode != 0:
        print(f"git-events.sh error: {result.stderr.strip()}", file=sys.stderr)
        return
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            pass


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Stage git history as lore candidate drafts in .lore/.harvest/."
    )
    ap.add_argument(
        "--since",
        help='Git date spec (e.g. "2 weeks ago", "2026-04-01")',
    )
    ap.add_argument(
        "--last",
        type=int,
        metavar="N",
        help="Stop after staging N candidates",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output directory for draft files (default: .lore/.harvest under --repo)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be staged without writing files",
    )
    ap.add_argument(
        "--repo",
        type=Path,
        default=Path("."),
        help="Repo root to mine (default: current directory)",
    )
    args = ap.parse_args(argv)

    repo = args.repo.resolve()
    script = PLUGIN_ROOT / "scripts" / "git-events.sh"
    out_dir: Path = (
        args.out if args.out is not None else repo / ".lore" / ".harvest"
    )

    if not args.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    staged: list[tuple[str, Path]] = []
    seen_ids: set[str] = set()
    count = 0

    for event in stream_events(script, args.since, repo):
        if args.last is not None and count >= args.last:
            break

        kind = classify(event)
        if kind is None:
            continue

        date = _event_date(event)
        slug = make_slug(str(event.get("subject", "")))
        record_id = f"{date}-{slug}"

        if record_id in seen_ids:
            continue
        seen_ids.add(record_id)

        draft = draft_journal(event) if kind == "journal" else draft_tfe(event)
        fname = f"{record_id}.md"
        out_path = out_dir / fname

        if args.dry_run:
            print(f"  would stage: {fname}  [{kind}]")
        else:
            out_path.write_text(draft, encoding="utf-8")
            staged.append((kind, out_path))

        count += 1

    if not args.dry_run:
        if staged:
            print(f"Staged {len(staged)} candidate(s) to {out_dir}/:")
            for kind, p in staged:
                print(f"  {kind:<22}  {p.name}")
        else:
            print("No candidates found.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
