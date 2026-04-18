#!/usr/bin/env python3
"""Validate a lore record's YAML frontmatter against the core schema."""

from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

import yaml

# Plugin root for profile lookup. This file is at <plugin-root>/scripts/validate.py.
PLUGIN_ROOT = Path(__file__).resolve().parent.parent

ARCHETYPES = frozenset({
    "journal", "codex", "try-failed-exp", "postmortem", "retro",
    "intent-log", "deprecation-tracker", "migration-guide",
    "api-changelog", "dependency-ledger", "release-notes",
})

TIERS = frozenset({"live", "archive", "canon"})

TFE_STATUS = frozenset({"rejected", "on-hold", "reassessed"})

EVENT_TIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2}|Z)?$"
)
JOURNAL_OUTCOME = frozenset(
    {"succeeded", "failed", "partial", "rolled-back", "observed"}
)

ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]{1,60}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CROSS_REF_RE = re.compile(r"^\[\[[a-z][a-z-]*:\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]{1,60}\]\]$")


class ValidationError(Exception):
    pass


def load_profile(archetype: str, profile_name: str) -> dict:
    """Load a profile YAML for the given archetype. Raises ValidationError if not found."""
    profile_path = PLUGIN_ROOT / "skills" / archetype / "profiles" / f"{profile_name}.yaml"
    if not profile_path.exists():
        raise ValidationError(
            f"profile {profile_name!r} not found at {profile_path} "
            f"(archetype: {archetype!r})"
        )
    try:
        with profile_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        raise ValidationError(f"profile {profile_path}: YAML parse error: {e}")


def load_body(path: Path) -> str:
    """Return the markdown body (everything after the closing frontmatter delimiter)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end < 0:
        return ""
    return text[end + 5:]


def body_has_heading(body: str, heading_text: str) -> bool:
    """Return True iff the body contains a level-2 heading whose text
    (after '## ' and optional whitespace) matches heading_text exactly,
    case-insensitive, AND the heading is followed by at least one
    non-blank, non-heading line of content.

    Lines inside fenced code blocks (```...```) are ignored.
    """
    lines = body.splitlines()
    target = heading_text.strip().lower()
    in_fence = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if stripped.lower() == f"## {target}":
            # Look for at least one non-blank, non-## line after this one.
            # Must also ignore lines inside fenced code blocks in the content region.
            follow_in_fence = False
            for follow in lines[i + 1:]:
                fs = follow.strip()
                if fs.startswith("```"):
                    follow_in_fence = not follow_in_fence
                    # A fence-start line counts as non-blank non-heading content.
                    if not follow_in_fence:
                        # This was a fence close; keep scanning
                        continue
                    return True  # Fence-open as first content = valid
                if follow_in_fence:
                    continue
                if not fs:
                    continue
                if fs.startswith("##"):
                    return False  # Next heading hit with no content between
                return True
            return False
    return False


def load_frontmatter(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValidationError(f"{path}: file not found")
    if not text.startswith("---\n"):
        raise ValidationError(f"{path}: missing YAML frontmatter (no leading '---')")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValidationError(f"{path}: unterminated YAML frontmatter")
    try:
        return yaml.safe_load(text[4:end]) or {}
    except (yaml.YAMLError, ValueError) as e:
        raise ValidationError(f"{path}: YAML parse error (likely invalid date or malformed value): {e}")


def validate(path: Path, fm: dict) -> list[str]:
    errors = []

    for field in ("id", "type", "tier", "date", "title", "authors"):
        if field not in fm:
            errors.append(f"missing required field: {field}")

    if "id" in fm and not ID_RE.match(str(fm["id"])):
        errors.append(f"id format invalid (want YYYY-MM-DD-slug): {fm['id']!r}")

    if "type" in fm and fm["type"] not in ARCHETYPES:
        errors.append(f"type must be one of {sorted(ARCHETYPES)}; got {fm['type']!r}")

    if "tier" in fm and fm["tier"] not in TIERS:
        errors.append(f"tier must be one of {sorted(TIERS)}; got {fm['tier']!r}")

    if "date" in fm and not DATE_RE.match(str(fm["date"])):
        errors.append(f"date format invalid (want YYYY-MM-DD): {fm['date']!r}")

    if "authors" in fm and not (isinstance(fm["authors"], list) and fm["authors"]):
        errors.append("authors must be a non-empty list")

    for ref_field in ("refs", "supersedes"):
        if ref_field in fm:
            val = fm[ref_field]
            if not isinstance(val, list):
                errors.append(f"{ref_field} must be a list")
                continue
            for r in val:
                if not CROSS_REF_RE.match(str(r)):
                    errors.append(f"{ref_field} entry {r!r} is not a valid cross-ref")

    if "superseded_by" in fm and not CROSS_REF_RE.match(str(fm["superseded_by"])):
        errors.append(f"superseded_by {fm['superseded_by']!r} is not a valid cross-ref")

    if "id" in fm and "date" in fm:
        if not str(fm["id"]).startswith(str(fm["date"])):
            errors.append(
                f"id {fm['id']!r} must begin with date {fm['date']!r}"
            )

    # I-3: filename (minus .md) must equal id
    if "id" in fm and path.stem != str(fm["id"]):
        errors.append(
            f"filename stem {path.stem!r} must equal id {fm['id']!r}"
        )

    # Task 6 main: path-vs-tier consistency
    # Only enforces tier<->directory agreement for records located under a
    # `.lore/<tier>/...` layout. Records outside a `.lore/` tree are not
    # subject to this check (they're likely fixtures or user-relocated files).
    if "tier" in fm:
        parts = path.parts
        try:
            lore_idx = parts.index(".lore")
        except ValueError:
            lore_idx = -1
        if lore_idx >= 0 and lore_idx + 1 < len(parts):
            tier_segment = parts[lore_idx + 1]
            if tier_segment in TIERS and tier_segment != fm["tier"]:
                errors.append(
                    f"tier/directory mismatch: frontmatter says tier={fm['tier']!r} "
                    f"but path locates record under .lore/{tier_segment}/"
                )

    # Archetype-specific rules: try-failed-exp
    if fm.get("type") == "try-failed-exp":
        # Pre-compute body once for all heading checks below.
        body = None  # Lazily loaded only if needed
        if "profile" not in fm:
            errors.append("try-failed-exp records require a 'profile' field")
        if "status" not in fm:
            errors.append("try-failed-exp records require a 'status' field")
        elif fm["status"] not in TFE_STATUS:
            errors.append(
                f"try-failed-exp status must be one of {sorted(TFE_STATUS)}; "
                f"got {fm['status']!r}"
            )
        if "profile" in fm:
            profile_data = None
            try:
                profile_data = load_profile("try-failed-exp", str(fm["profile"]))
            except ValidationError as e:
                errors.append(str(e))
            if profile_data is not None:
                required = profile_data.get("required_sections") or []
                if required:
                    body = load_body(path)
                    for section in required:
                        heading = str(section).strip()
                        if heading.startswith("## "):
                            heading = heading[3:]
                        if not body_has_heading(body, heading):
                            errors.append(
                                f"profile {fm['profile']!r} requires "
                                f"'## {heading}' section (profile required_sections); "
                                f"missing from body"
                            )
        # Archetype-level: '## Don't retry unless'
        if body is None:
            body = load_body(path)
        if not body_has_heading(body, "Don't retry unless"):
            errors.append(
                "try-failed-exp records must contain a "
                "'## Don't retry unless' section with at least one line of content"
            )
        # status: reassessed must be paired with superseded_by
        if fm.get("status") == "reassessed" and "superseded_by" not in fm:
            errors.append(
                "try-failed-exp with status='reassessed' must also set "
                "'superseded_by' pointing at the overturning record"
            )

    # Archetype-specific rules: journal
    if fm.get("type") == "journal":
        if "profile" not in fm:
            errors.append("journal records require a 'profile' field")
        if "event-time" not in fm:
            errors.append("journal records require an 'event-time' field")
        else:
            ev = fm["event-time"]
            # PyYAML auto-parses unquoted ISO timestamps into datetime objects.
            # Normalize: if it has isoformat(), use that (yields the T form);
            # otherwise stringify and check as-is.
            ev_str = ev.isoformat() if hasattr(ev, "isoformat") else str(ev)
            if not EVENT_TIME_RE.match(ev_str):
                errors.append(
                    f"event-time must be ISO 8601 "
                    f"(YYYY-MM-DDTHH:MM[:SS][Z|±HH:MM]); "
                    f"got {fm['event-time']!r}"
                )
        if "outcome" not in fm:
            errors.append("journal records require an 'outcome' field")
        elif fm["outcome"] not in JOURNAL_OUTCOME:
            errors.append(
                f"journal outcome must be one of {sorted(JOURNAL_OUTCOME)}; "
                f"got {fm['outcome']!r}"
            )
        # Profile existence (reuses Spec 2's load_profile helper)
        if "profile" in fm:
            try:
                load_profile("journal", str(fm["profile"]))
            except ValidationError as e:
                errors.append(str(e))
        # Live-tier immutability: journal records must not supersede or be superseded
        if "superseded_by" in fm:
            errors.append(
                "journal records are immutable; 'superseded_by' not permitted "
                "on live-tier events"
            )
        if "supersedes" in fm:
            errors.append(
                "journal records are immutable; 'supersedes' not permitted "
                "on live-tier events"
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate a lore record frontmatter.")
    ap.add_argument("path", type=Path, help="Path to the .md record")
    args = ap.parse_args(argv)

    try:
        fm = load_frontmatter(args.path)
    except ValidationError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    errors = validate(args.path, fm)
    if errors:
        for e in errors:
            print(f"ERROR: {args.path}: {e}", file=sys.stderr)
        return 1
    print(f"OK: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
