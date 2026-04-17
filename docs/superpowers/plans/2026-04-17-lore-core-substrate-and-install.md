# Lore — Core Substrate & Install Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the v0.1 foundation of the lore plugin — the shared conventions (frontmatter schema, ID scheme, cross-ref grammar, tier model, directory layout), three Layer-0 helper scripts, and the install infrastructure (package.json + Claude Code + Cursor plugin manifests + session-start hook + `using-lore` primer skill) that every later spec (2–7) builds on.

**Architecture:** Layer-0 substrate is pure documentation (5 markdown files) plus three small scripts (bash + python). Install infrastructure mirrors Superpowers exactly: a polyglot `run-hook.cmd` dispatches bash handlers; the `session-start` handler reads the `using-lore` SKILL.md, JSON-escapes it, and emits platform-aware context injection (Cursor / Claude Code / Copilot CLI formats). TDD with bats for shell scripts and pytest for Python.

**Tech Stack:** Bash 4+, Python 3.9+, bats-core (shell tests), pytest + PyYAML (python tests + validator), plain markdown for skills/docs.

**Relevant charter sections:** §2.1, §2.2 (layered architecture), §3.1, §3.2 (frontmatter, ID, cross-ref, tier mechanics), §4.1–§4.3 (plugin skeleton, distribution, session-start hook), §4.6 (naming convention).

**Out of scope for this plan:** archetype SKILL.md files (journal, codex, try-failed-exp) — those are Specs 2–4. Adapters, meta-skills, compliance overlays — Specs 5–7. `.codex/`, `.opencode/`, `gemini-extension.json` — v0.2/v0.3 per charter §5.1.

---

## File Structure

Files created in this plan:

**Plugin root:**
- `package.json` — Node-style manifest (name, version, type, main)
- `README.md` — install instructions per charter §4.2
- `LICENSE` — MIT
- `.gitignore` — minimal (Python, macOS, node)
- `CLAUDE.md` — high-level "what is lore" primer, auto-loaded by Claude Code

**Platform manifests (v0.1 = Claude Code + Cursor):**
- `.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json`
- `.cursor-plugin/plugin.json`

**Hooks:**
- `hooks/hooks.json` — Claude Code SessionStart
- `hooks/hooks-cursor.json` — Cursor SessionStart
- `hooks/run-hook.cmd` — polyglot bash/batch dispatcher
- `hooks/session-start` — bash handler (no `.sh` extension, matching Superpowers)

**Scripts (Layer-0 helpers):**
- `scripts/new-id.sh` — `YYYY-MM-DD-<slug>` generator with collision handling
- `scripts/validate.py` — frontmatter schema validator (CLI + importable)
- `scripts/git-events.sh` — git log → JSON lines for `harvest`

**Core skill (Layer 0, non-invocable):**
- `skills/core/SKILL.md` — index / reference hub
- `skills/core/frontmatter-schema.md`
- `skills/core/id-scheme.md`
- `skills/core/cross-ref-grammar.md`
- `skills/core/tier-model.md`
- `skills/core/directory-layout.md`

**Primer skill (invocable, auto-loaded via session-start):**
- `skills/using-lore/SKILL.md`

**Tests:**
- `tests/scripts/test_validate.py` — pytest
- `tests/scripts/test_new-id.bats` — bats
- `tests/scripts/test_git-events.bats` — bats
- `tests/fixtures/` — valid + invalid frontmatter example records
- `requirements-dev.txt` — pytest, PyYAML

---

## Pre-task setup

Work in the existing repo `/Users/joejiang/changelog_skill/try-failed-log.skill/` (physical dir name still pending rename to `lore.skill`). Charter is already committed as the root commit. All work here stacks on top of `main`.

---

### Task 1: Bootstrap repo skeleton

Create plugin manifest, README placeholder, LICENSE, .gitignore. No tests — pure config.

**Files:**
- Create: `package.json`
- Create: `README.md`
- Create: `LICENSE`
- Create: `.gitignore`

- [ ] **Step 1.1: Write `package.json`**

```json
{
  "name": "lore",
  "version": "0.1.0",
  "description": "Turn your project's lived history into structured, cross-referenced, git-tracked memory. Timeline · checkpoint · recall · lore · legacy.",
  "type": "module",
  "license": "MIT",
  "author": {
    "name": "host452b",
    "email": ""
  },
  "homepage": "https://github.com/host452b/lore.skill",
  "repository": {
    "type": "git",
    "url": "https://github.com/host452b/lore.skill.git"
  },
  "keywords": [
    "skills",
    "changelog",
    "adr",
    "project-memory",
    "dead-ends",
    "try-failed-exp",
    "knowledge-management"
  ]
}
```

- [ ] **Step 1.2: Write minimal `README.md`**

```markdown
# Lore

**Turn your project's lived history into structured, cross-referenced, git-tracked memory.**

`timeline` · `checkpoint` · `recall` · `lore` · `legacy`

Lore is a Claude Code / Cursor plugin that captures deploys, experiments, decisions, failed attempts, incidents, and releases as typed records, then distills them into reusable project canon. Its anchor skill — `lore:try-failed-exp` — gives every project a place to record the things that *didn't* work, so nobody tries them again.

## Installation

### Claude Code (community marketplace)

```bash
/plugin marketplace add host452b/lore-marketplace
/plugin install lore@lore-marketplace
```

### Cursor

```text
/add-plugin lore
```

(or search "lore" in the plugin marketplace)

More platforms (Codex, OpenCode, Gemini CLI) land in v0.2–v0.3.

## Design

See [`docs/superpowers/specs/2026-04-17-lore-charter-design.md`](docs/superpowers/specs/2026-04-17-lore-charter-design.md) for the architectural charter.
```

- [ ] **Step 1.3: Write `LICENSE` (MIT)**

```
MIT License

Copyright (c) 2026 host452b

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 1.4: Write `.gitignore`**

```
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# macOS
.DS_Store

# Node (if any tooling appears later)
node_modules/

# Editor
.idea/
.vscode/
*.swp

# Test artifacts
.pytest_cache/
.coverage
```

- [ ] **Step 1.5: Commit**

```bash
git add package.json README.md LICENSE .gitignore
git commit -m "chore: bootstrap plugin skeleton (package.json, README, LICENSE, .gitignore)"
```

---

### Task 2: Test infrastructure

Add dev dependencies and verify the test runners work on an empty test.

**Files:**
- Create: `requirements-dev.txt`
- Create: `tests/scripts/test_placeholder.py`
- Create: `tests/scripts/test_placeholder.bats`

- [ ] **Step 2.1: Write `requirements-dev.txt`**

```
pytest>=7.0
PyYAML>=6.0
```

- [ ] **Step 2.2: Install Python deps**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Expected: installs cleanly.

- [ ] **Step 2.3: Install bats-core**

```bash
brew install bats-core
bats --version
```

Expected: outputs e.g. `Bats 1.11.0`.

- [ ] **Step 2.4: Placeholder pytest**

```python
# tests/scripts/test_placeholder.py
def test_runner_works():
    assert 1 + 1 == 2
```

- [ ] **Step 2.5: Placeholder bats test**

```bash
# tests/scripts/test_placeholder.bats
@test "bats runner works" {
  result=$((1 + 1))
  [ "$result" -eq 2 ]
}
```

- [ ] **Step 2.6: Run both**

```bash
source .venv/bin/activate
pytest tests/scripts/test_placeholder.py -v
bats tests/scripts/test_placeholder.bats
```

Expected: both PASS.

- [ ] **Step 2.7: Commit**

```bash
git add requirements-dev.txt tests/
git commit -m "test: set up pytest + bats infrastructure with placeholder tests"
```

---

### Task 3: Frontmatter schema — TDD

Write the schema validator first (`scripts/validate.py`), then write the reference doc (`skills/core/frontmatter-schema.md`) whose examples must pass the validator.

**Files:**
- Create: `scripts/validate.py`
- Create: `tests/scripts/test_validate.py` (replace placeholder)
- Create: `tests/fixtures/valid/minimal.md`
- Create: `tests/fixtures/valid/full.md`
- Create: `tests/fixtures/invalid/missing-id.md`
- Create: `tests/fixtures/invalid/bad-tier.md`
- Create: `tests/fixtures/invalid/bad-id-format.md`
- Create: `skills/core/frontmatter-schema.md`

- [ ] **Step 3.1: Write valid minimal fixture**

```markdown
---
id: 2026-04-17-first-record
type: journal
tier: live
date: 2026-04-17
title: First record
authors: ["host452b <>"]
---

# First record

Body content.
```

Save to `tests/fixtures/valid/minimal.md`.

- [ ] **Step 3.2: Write valid full fixture**

```markdown
---
id: 2026-04-17-adr-postgres-primary
type: codex
tier: canon
date: 2026-04-17
title: Postgres as primary DB
authors: ["host452b <>"]
profile: adr
status: accepted
refs: ["[[journal:2026-04-10-db-spike]]"]
tags: ["database", "architecture"]
---

# Postgres as primary DB

## Context
We needed a primary transactional store.

## Decision
Postgres 16.

## Consequences
Operational familiarity; gives up some NoSQL flexibility.
```

Save to `tests/fixtures/valid/full.md`.

- [ ] **Step 3.3: Write invalid fixtures**

`tests/fixtures/invalid/missing-id.md`:

```markdown
---
type: journal
tier: live
date: 2026-04-17
title: Missing id
authors: ["Joe <j@example.com>"]
---
Body.
```

`tests/fixtures/invalid/bad-tier.md`:

```markdown
---
id: 2026-04-17-bad-tier
type: journal
tier: purgatory
date: 2026-04-17
title: Bad tier
authors: ["Joe <j@example.com>"]
---
Body.
```

`tests/fixtures/invalid/bad-id-format.md`:

```markdown
---
id: 2026-4-17-bad
type: journal
tier: live
date: 2026-04-17
title: Bad id format
authors: ["Joe <j@example.com>"]
---
Body.
```

- [ ] **Step 3.4: Write failing test**

```python
# tests/scripts/test_validate.py
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
VALIDATE = REPO_ROOT / "scripts" / "validate.py"
FIXTURES = Path(__file__).parent.parent / "fixtures"

def run_validate(path):
    return subprocess.run(
        ["python3", str(VALIDATE), str(path)],
        capture_output=True, text=True,
    )

def test_valid_minimal_passes():
    r = run_validate(FIXTURES / "valid" / "minimal.md")
    assert r.returncode == 0, r.stderr

def test_valid_full_passes():
    r = run_validate(FIXTURES / "valid" / "full.md")
    assert r.returncode == 0, r.stderr

def test_missing_id_fails():
    r = run_validate(FIXTURES / "invalid" / "missing-id.md")
    assert r.returncode != 0
    assert "id" in r.stderr.lower()

def test_bad_tier_fails():
    r = run_validate(FIXTURES / "invalid" / "bad-tier.md")
    assert r.returncode != 0
    assert "tier" in r.stderr.lower()

def test_bad_id_format_fails():
    r = run_validate(FIXTURES / "invalid" / "bad-id-format.md")
    assert r.returncode != 0
    assert "id" in r.stderr.lower()
```

- [ ] **Step 3.5: Run tests to verify they fail**

```bash
source .venv/bin/activate
pytest tests/scripts/test_validate.py -v
```

Expected: FAIL with `scripts/validate.py` not found.

- [ ] **Step 3.6: Implement `scripts/validate.py`**

```python
#!/usr/bin/env python3
"""Validate a lore record's YAML frontmatter against the core schema."""

from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

import yaml

ARCHETYPES = {
    "journal", "codex", "try-failed-exp", "postmortem", "retro",
    "intent-log", "deprecation-tracker", "migration-guide",
    "api-changelog", "dependency-ledger", "release-notes",
}

TIERS = {"live", "archive", "canon"}

ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]{1,60}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CROSS_REF_RE = re.compile(r"^\[\[[a-z][a-z-]*:\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]*\]\]$")


class ValidationError(Exception):
    pass


def load_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValidationError(f"{path}: missing YAML frontmatter (no leading '---')")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValidationError(f"{path}: unterminated YAML frontmatter")
    try:
        return yaml.safe_load(text[4:end]) or {}
    except yaml.YAMLError as e:
        raise ValidationError(f"{path}: YAML parse error: {e}")


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
        if str(fm["id"]).startswith(str(fm["date"])) is False:
            errors.append(
                f"id {fm['id']!r} must begin with date {fm['date']!r}"
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
```

- [ ] **Step 3.7: Make it executable**

```bash
chmod +x scripts/validate.py
```

- [ ] **Step 3.8: Run tests**

```bash
source .venv/bin/activate
pytest tests/scripts/test_validate.py -v
```

Expected: all 5 tests PASS.

- [ ] **Step 3.9: Write `skills/core/frontmatter-schema.md`**

```markdown
# Frontmatter schema

Every `.lore/**/*.md` record has YAML frontmatter. The fields below are the contract; profile extensions add more fields but never remove these.

## Required fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | `YYYY-MM-DD-<slug>`, matches regex `^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]{1,60}$`. Must equal filename (minus `.md`). Must begin with `date`. |
| `type` | enum | One of the 11 archetypes: `journal`, `codex`, `try-failed-exp`, `postmortem`, `retro`, `intent-log`, `deprecation-tracker`, `migration-guide`, `api-changelog`, `dependency-ledger`, `release-notes`. |
| `tier` | enum | `live` \| `archive` \| `canon`. Must agree with the record's directory path. |
| `date` | ISO date | `YYYY-MM-DD`. The record's *primary* date (decision / event / discovery), not wall-clock creation. |
| `title` | string | Human-readable title; appears in indexes. |
| `authors` | list\<string\> | Non-empty. Git-style identities: `"host452b <>"`. |

## Optional fields

| Field | Type | Notes |
|-------|------|-------|
| `profile` | string | Name of the profile in `skills/<archetype>/profiles/<name>.yaml`. |
| `status` | enum | Profile-defined (e.g., ADR: `proposed/accepted/superseded/deprecated`). |
| `refs` | list\<cross-ref\> | Outbound references. See `cross-ref-grammar.md`. |
| `superseded_by` | cross-ref | Forward pointer to replacement record. |
| `supersedes` | list\<cross-ref\> | Inverse of `superseded_by`. `audit` keeps them consistent. |
| `tags` | list\<string\> | Free-form. |
| `source` | object | For imported records: `{adapter: from-git-log, ref: <sha>}`. |

## Validation

Use `scripts/validate.py <path>`:

```bash
python3 scripts/validate.py .lore/canon/codex/2026-01-04-postgres-primary-db.md
# OK: .lore/canon/codex/2026-01-04-postgres-primary-db.md
```

## Examples

### Minimal (journal, live-tier)

```yaml
---
id: 2026-04-17-first-record
type: journal
tier: live
date: 2026-04-17
title: First record
authors: ["host452b <>"]
---
```

### Full (codex/ADR, canon-tier, with profile and refs)

```yaml
---
id: 2026-04-17-adr-postgres-primary
type: codex
tier: canon
date: 2026-04-17
title: Postgres as primary DB
authors: ["host452b <>"]
profile: adr
status: accepted
refs: ["[[journal:2026-04-10-db-spike]]"]
tags: ["database", "architecture"]
---
```
```

- [ ] **Step 3.10: Verify doc examples validate**

Extract the two YAML examples from `skills/core/frontmatter-schema.md` into temporary fixtures and run `validate.py` on each — both should pass. (Reuse `tests/fixtures/valid/minimal.md` and `full.md`; they mirror the doc examples.)

```bash
source .venv/bin/activate
python3 scripts/validate.py tests/fixtures/valid/minimal.md
python3 scripts/validate.py tests/fixtures/valid/full.md
```

Expected: two `OK:` lines.

- [ ] **Step 3.11: Commit**

```bash
git add scripts/validate.py skills/core/frontmatter-schema.md tests/
git commit -m "feat(core): frontmatter schema + validate.py with TDD coverage"
```

---

### Task 4: ID scheme — TDD

**Files:**
- Create: `scripts/new-id.sh`
- Create: `tests/scripts/test_new-id.bats`
- Create: `skills/core/id-scheme.md`

- [ ] **Step 4.1: Write failing bats tests**

```bash
# tests/scripts/test_new-id.bats
setup() {
  export REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  export NEW_ID="$REPO_ROOT/scripts/new-id.sh"
  export WORK="$(mktemp -d)"
}

teardown() {
  rm -rf "$WORK"
}

@test "generates YYYY-MM-DD-slug given date and slug" {
  run "$NEW_ID" --date 2026-04-17 --slug hello-world --dir "$WORK"
  [ "$status" -eq 0 ]
  [ "$output" = "2026-04-17-hello-world" ]
}

@test "uses today's date when --date omitted" {
  today=$(date +%Y-%m-%d)
  run "$NEW_ID" --slug hello --dir "$WORK"
  [ "$status" -eq 0 ]
  [ "$output" = "${today}-hello" ]
}

@test "appends -2 on collision with existing file" {
  touch "$WORK/2026-04-17-hello.md"
  run "$NEW_ID" --date 2026-04-17 --slug hello --dir "$WORK"
  [ "$status" -eq 0 ]
  [ "$output" = "2026-04-17-hello-2" ]
}

@test "appends -3 on double collision" {
  touch "$WORK/2026-04-17-hello.md" "$WORK/2026-04-17-hello-2.md"
  run "$NEW_ID" --date 2026-04-17 --slug hello --dir "$WORK"
  [ "$status" -eq 0 ]
  [ "$output" = "2026-04-17-hello-3" ]
}

@test "rejects uppercase slug" {
  run "$NEW_ID" --date 2026-04-17 --slug HELLO --dir "$WORK"
  [ "$status" -ne 0 ]
}

@test "rejects slug with spaces" {
  run "$NEW_ID" --date 2026-04-17 --slug "hello world" --dir "$WORK"
  [ "$status" -ne 0 ]
}

@test "rejects missing --slug" {
  run "$NEW_ID" --date 2026-04-17 --dir "$WORK"
  [ "$status" -ne 0 ]
}
```

- [ ] **Step 4.2: Run — expect FAIL**

```bash
bats tests/scripts/test_new-id.bats
```

Expected: all tests fail (script doesn't exist).

- [ ] **Step 4.3: Implement `scripts/new-id.sh`**

```bash
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
```

- [ ] **Step 4.4: Make executable**

```bash
chmod +x scripts/new-id.sh
```

- [ ] **Step 4.5: Run — expect PASS**

```bash
bats tests/scripts/test_new-id.bats
```

Expected: all 7 tests PASS.

- [ ] **Step 4.6: Write `skills/core/id-scheme.md`**

```markdown
# ID scheme

Every lore record has a unique, human-readable ID of the form:

```
YYYY-MM-DD-<slug>
```

Examples:
- `2026-04-10-deploy-v1.3.2`
- `2026-02-20-rejected-redis-cluster`
- `2026-01-04-postgres-primary-db`

## Why this format

- **Sortable.** Lexical sort == chronological sort.
- **Git-friendly.** Filenames are stable, no ambiguous characters.
- **Human-readable.** You can recognize "the Postgres ADR from January" at a glance.
- **Slug-stable.** The slug is a short kebab-case phrase; re-slugifying isn't required when the title changes.

## Rules

- **Date** is `YYYY-MM-DD` (zero-padded). It is the record's *primary* date:
  - `journal`: event date
  - `codex`: decision date
  - `try-failed-exp`: discovery / conclusion date
  - `postmortem`: incident date
  - Not wall-clock creation time.
- **Slug** matches `^[a-z0-9][a-z0-9-]{1,60}$`: lowercase alphanumerics and hyphens, starting alphanumeric, length 2–61.
- **Collision suffix:** if the same date + slug already exists, append `-2`, `-3`, etc.

## Generating IDs

Use `scripts/new-id.sh`:

```bash
# Today's date, collision-safe within a directory
bash scripts/new-id.sh --slug redis-cluster-spike --dir .lore/canon/try-failed-exp
# 2026-04-17-redis-cluster-spike

# Explicit date
bash scripts/new-id.sh --date 2026-03-15 --slug payment-outage --dir .lore/archive/2026/postmortem
# 2026-03-15-payment-outage
```

Every archetype SKILL.md instructs Claude to call `new-id.sh` as the first step of writing a record.

## Filename invariant

The record's filename (minus `.md`) must equal `id`. The `audit` meta-skill enforces this.
```

- [ ] **Step 4.7: Commit**

```bash
git add scripts/new-id.sh tests/scripts/test_new-id.bats skills/core/id-scheme.md
git commit -m "feat(core): new-id.sh ID generator + id-scheme.md with TDD coverage"
```

---

### Task 5: Cross-ref grammar

Extend `validate.py` is already done (it accepts `refs`/`supersedes`/`superseded_by` as cross-refs). This task writes the reference doc and adds one extra cross-file validator check.

**Files:**
- Create: `skills/core/cross-ref-grammar.md`

- [ ] **Step 5.1: Write `skills/core/cross-ref-grammar.md`**

```markdown
# Cross-ref grammar

Records reference each other using a compact, machine-parseable grammar:

```
[[<archetype>:<id>]]
```

Examples:
- `[[codex:2026-01-04-postgres-primary-db]]`
- `[[try-failed-exp:2026-02-20-rejected-redis-cluster]]`
- `[[journal:2026-04-10-deploy-v1.3.2]]`

## Where cross-refs appear

**In frontmatter (structured):**

```yaml
refs: ["[[codex:2026-01-04-postgres-primary-db]]"]
superseded_by: "[[codex:2026-05-15-postgres-partitioning]]"
supersedes: ["[[codex:2025-12-01-postgres-draft]]"]
```

**In prose body (casual):**

```markdown
This spike was motivated by the decision recorded in
[[codex:2026-01-04-postgres-primary-db]].
```

Both forms are recognized by the `meta/link` skill, which cross-checks that:
- Every cited cross-ref resolves to an existing record.
- Every prose cross-ref is also listed in `refs:` (so structural queries see it).
- Every `supersedes` entry has a matching `superseded_by` on the other side.

## Grammar

Formal:

```
cross-ref ::= "[[" archetype ":" id "]]"
archetype ::= [a-z][a-z-]*          // one of the 11 archetype names
id        ::= YYYY "-" MM "-" DD "-" slug
slug      ::= [a-z0-9][a-z0-9-]*
```

No spaces inside the brackets. No nested brackets. No additional metadata (for that, cite the ref and describe relationship in prose or frontmatter `tags`).

## What cross-refs are NOT

- Not hyperlinks. Lore records may sit in various directory hierarchies; cross-refs don't encode paths. `meta/link` resolves them at read time.
- Not version-pinned. A cross-ref to `[[codex:2026-01-04-postgres-primary-db]]` always resolves to the current state of that record (which may have been `superseded_by` something newer).

## Validation

- `scripts/validate.py` checks that frontmatter `refs`, `supersedes`, `superseded_by` entries are well-formed.
- `meta/link` (future skill) checks that they *resolve* (i.e., the target file exists).
```

- [ ] **Step 5.2: Commit**

```bash
git add skills/core/cross-ref-grammar.md
git commit -m "feat(core): cross-ref-grammar.md documenting [[type:id]] syntax"
```

---

### Task 6: Tier model

`validate.py` already checks the tier enum. This task writes the tier model doc and adds a path-vs-frontmatter consistency check to the validator.

**Files:**
- Modify: `scripts/validate.py` — add path-vs-tier consistency check
- Modify: `tests/scripts/test_validate.py` — add tier-dir-mismatch test
- Create: `tests/fixtures/invalid/tier-dir-mismatch/live/journal/2026-04-17-labeled-canon.md`
- Create: `skills/core/tier-model.md`

- [ ] **Step 6.1: Create tier-dir-mismatch fixture**

Create the nested directory under `tests/fixtures/invalid/tier-dir-mismatch/live/journal/`. The file `2026-04-17-labeled-canon.md`:

```markdown
---
id: 2026-04-17-labeled-canon
type: journal
tier: canon
date: 2026-04-17
title: Labeled canon but in live dir
authors: ["Joe <j@example.com>"]
---

The tier says canon, but the path puts it under live/. Should fail.
```

- [ ] **Step 6.2: Add failing test**

Append to `tests/scripts/test_validate.py`:

```python
def test_tier_dir_mismatch_fails():
    r = run_validate(
        FIXTURES / "invalid" / "tier-dir-mismatch" / "live" / "journal"
        / "2026-04-17-labeled-canon.md"
    )
    assert r.returncode != 0
    assert "tier" in r.stderr.lower() or "directory" in r.stderr.lower()
```

- [ ] **Step 6.3: Run test — expect FAIL**

```bash
source .venv/bin/activate
pytest tests/scripts/test_validate.py::test_tier_dir_mismatch_fails -v
```

Expected: FAIL (validator doesn't yet check path vs tier).

- [ ] **Step 6.4: Extend `validate()` in `scripts/validate.py`**

Find the `validate()` function. Before the `return errors` line, add:

```python
    # Path-vs-tier consistency: if the path contains /live/, /archive/, or /canon/,
    # the frontmatter tier must match.
    if "tier" in fm:
        parts = path.parts
        for segment in ("live", "archive", "canon"):
            if segment in parts and fm["tier"] != segment:
                errors.append(
                    f"tier/directory mismatch: frontmatter says tier={fm['tier']!r} "
                    f"but path contains /{segment}/"
                )
                break
```

- [ ] **Step 6.5: Run test — expect PASS**

```bash
pytest tests/scripts/test_validate.py -v
```

Expected: all tests PASS (5 original + 1 new = 6).

- [ ] **Step 6.6: Write `skills/core/tier-model.md`**

```markdown
# Tier model — the cooling pipeline

Every lore record lives at one of three **tiers**. Tier expresses *temperature* — how often the record changes, how reusable it is, how often it's re-read.

| Tier | Name (zh) | Meaning | Typical archetypes | Churn |
|------|-----------|---------|--------------------|-------|
| `live` | 流 (stream) | Raw, high-churn event signal | `journal`, `intent-log`, `dependency-ledger` | High |
| `archive` | 档 (record) | Crystallized one-time retrospection | `postmortem`, `retro`, `release-notes` | Low (append-only) |
| `canon` | 典 (canon) | Reusable, repeatedly-cited rule | `codex`, `try-failed-exp`, `migration-guide` | Medium (revised) |

## The cooling pipeline

```
LIVE  ──── curate ────►  ARCHIVE  ──── distill ────►  CANON
```

Information phase-transitions cold-ward over time. The `meta/promote` skill operates this pipeline:

- Scans `live/journal/` for recurring patterns → suggests `canon/codex/` entries.
- Scans `archive/postmortem/` for lessons → suggests `canon/codex/` or `canon/try-failed-exp/` entries.

Without `promote`, lore degenerates into "a directory of templates." With `promote`, lore is a knowledge-accumulation system.

## Tier is a property of the record, not the archetype

An archetype can produce records at more than one tier (rare). Example: `api-changelog` entries default to `archive`, but heavily-cited breaking-change entries can be promoted to `canon` as part of a `migration-guide`.

## Storage: directory and frontmatter must agree

A record lives at `.lore/<tier>/<archetype>/<id>.md`. The `tier:` frontmatter field must match the directory. The `audit` skill enforces this; `scripts/validate.py` enforces it for any file whose path contains `/live/`, `/archive/`, or `/canon/`.

## Tier transitions

**Cold-ward (live → archive → canon):** common, handled by `meta/promote`. Both the file location and the `tier:` field are updated atomically.

**Hot-ward (canon → archive, archive → live):** rare, user-driven only. In v0.1 and v0.2, `promote` only moves records cold-ward; hot-ward motion requires a manual move + frontmatter edit + commit.

## Why three tiers, not two or five

- Two (`live`/`canon`) loses the "write once, archive-and-done" middle category that postmortems and retros need — they aren't live, but they also aren't the reusable canon; the *distilled lesson* is.
- Five or more (e.g., adding "draft", "deprecated") overloads tier with status. Status belongs in the `status:` field, not the tier.

Three tiers is the minimum that gives the cooling pipeline a middle stage.
```

- [ ] **Step 6.7: Commit**

```bash
git add scripts/validate.py tests/ skills/core/tier-model.md
git commit -m "feat(core): tier model doc + validator path-vs-tier consistency check"
```

---

### Task 7: Directory layout doc

Pure reference doc. No code changes.

**Files:**
- Create: `skills/core/directory-layout.md`

- [ ] **Step 7.1: Write `skills/core/directory-layout.md`**

```markdown
# Directory layout

Lore produces records in a git-tracked `.lore/` directory at the root of the consuming project. The layout is:

```
<user-project>/
├── .lore/
│   ├── live/                      ← tier: live
│   │   ├── journal/
│   │   │   ├── 2026-04-10-deploy-v1.3.2.md
│   │   │   └── 2026-04-12-mlflow-run-847.md
│   │   ├── intent-log/
│   │   └── dependency-ledger/
│   │
│   ├── archive/                   ← tier: archive (year-bucketed)
│   │   └── 2026/
│   │       ├── postmortem/
│   │       │   └── 2026-03-15-payment-outage.md
│   │       ├── retro/
│   │       │   └── 2026-Q1.md
│   │       └── release-notes/
│   │           └── v1.3.md
│   │
│   └── canon/                     ← tier: canon
│       ├── codex/
│       │   └── 2026-01-04-postgres-primary-db.md
│       ├── try-failed-exp/
│       │   └── 2026-02-20-rejected-redis-cluster.md
│       └── migration-guide/
│           └── 2026-02-01-v1-to-v2.md
```

## Rules

1. **Path = `.lore/<tier>/<archetype>/<id>.md`.** No further nesting.
2. **Archive is year-bucketed** (`.lore/archive/2026/...`); live and canon are flat.
3. **Filename = `<id>.md`.** The `audit` skill enforces this.
4. **Tier directory and `tier:` frontmatter must agree.** Enforced by `scripts/validate.py`.
5. **Archetype directory and `type:` frontmatter must agree.** Enforced by `audit`.

## `.lore/config.yaml` (optional)

If present, it records the archetypes and profiles enabled for this project. Created by the `detect` skill when the user customizes the suggested starter set.

```yaml
# .lore/config.yaml (example)
archetypes_enabled:
  - journal
  - codex
  - try-failed-exp
profiles:
  journal: [web-service]
  codex: [adr]
  try-failed-exp: [rejected-adr]
```

The config is a hint, not a hard enforcement — users can write records of any archetype regardless of the config. The config drives `detect`'s suggestions and `harvest`'s scope.

## Git tracking

`.lore/` is tracked by git by default. Teams that want it gitignored should add `.lore/` to their `.gitignore`. The out-of-the-box story is "your lore ships with your repo."

## What NOT to put in `.lore/`

- Secrets. Frontmatter is YAML; body is markdown — both are plain text. If you need to cite a secret (e.g., a leaked credential in a postmortem), reference it by name, not value.
- Large binaries. Lore records are short. Link to artifacts (S3, artifact registries) instead of embedding them.
- Generated files. `.lore/` is hand-curated (or harvested from git, never from generators with no signal).
```

- [ ] **Step 7.2: Commit**

```bash
git add skills/core/directory-layout.md
git commit -m "feat(core): directory-layout.md documenting .lore/ structure"
```

---

### Task 8: git-events.sh — TDD

The inbound adapter `from-git-log` (future Spec 5) will consume this. Emits one JSON object per commit to stdout.

**Files:**
- Create: `scripts/git-events.sh`
- Create: `tests/scripts/test_git-events.bats`

- [ ] **Step 8.1: Write failing bats tests**

```bash
# tests/scripts/test_git-events.bats
setup() {
  export REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  export GIT_EVENTS="$REPO_ROOT/scripts/git-events.sh"
  export WORK="$(mktemp -d)"

  # Build a tiny throwaway repo with deterministic commits
  cd "$WORK"
  git init -q -b main
  git config user.email "test@example.com"
  git config user.name "Test"
  echo a > a.txt && git add a.txt && git commit -qm "first commit"
  echo b > b.txt && git add b.txt && git commit -qm "second commit"
  echo c > a.txt && git add a.txt && git commit -qm "Revert \"first commit\""
}

teardown() {
  rm -rf "$WORK"
}

@test "emits one JSON line per commit" {
  cd "$WORK"
  run bash "$GIT_EVENTS"
  [ "$status" -eq 0 ]
  count=$(printf '%s\n' "$output" | grep -c '^{')
  [ "$count" -eq 3 ]
}

@test "each JSON line has sha, subject, author, date fields" {
  cd "$WORK"
  run bash "$GIT_EVENTS"
  [ "$status" -eq 0 ]
  echo "$output" | head -n1 | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
for f in ('sha', 'subject', 'author', 'date'):
    assert f in o, f'{f} missing from: {o}'
"
}

@test "marks revert commits with is_revert: true" {
  cd "$WORK"
  run bash "$GIT_EVENTS"
  [ "$status" -eq 0 ]
  revert_line=$(printf '%s\n' "$output" | grep -E 'Revert' || true)
  [ -n "$revert_line" ]
  echo "$revert_line" | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
assert o.get('is_revert') is True, o
"
}

@test "non-revert commits have is_revert: false" {
  cd "$WORK"
  run bash "$GIT_EVENTS"
  [ "$status" -eq 0 ]
  first_non_revert=$(printf '%s\n' "$output" | grep -vE 'Revert' | head -n1)
  echo "$first_non_revert" | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
assert o.get('is_revert') is False, o
"
}

@test "respects --since argument" {
  cd "$WORK"
  run bash "$GIT_EVENTS" --since "1 year ago"
  [ "$status" -eq 0 ]
  count=$(printf '%s\n' "$output" | grep -c '^{')
  [ "$count" -eq 3 ]
}
```

- [ ] **Step 8.2: Run — expect FAIL**

```bash
bats tests/scripts/test_git-events.bats
```

- [ ] **Step 8.3: Implement `scripts/git-events.sh`**

```bash
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
```

- [ ] **Step 8.4: Make executable**

```bash
chmod +x scripts/git-events.sh
```

- [ ] **Step 8.5: Run — expect PASS**

```bash
bats tests/scripts/test_git-events.bats
```

Expected: all 5 tests PASS.

- [ ] **Step 8.6: Commit**

```bash
git add scripts/git-events.sh tests/scripts/test_git-events.bats
git commit -m "feat(core): git-events.sh emits JSON lines per commit with TDD coverage"
```

---

### Task 9: Core SKILL.md (index / reference hub)

`skills/core/SKILL.md` is the non-invocable "layer-0 contract" reference. Other SKILL.md files cite its docs by path.

**Files:**
- Create: `skills/core/SKILL.md`

- [ ] **Step 9.1: Write `skills/core/SKILL.md`**

```markdown
---
name: core
description: Layer-0 substrate for the lore suite — shared conventions every archetype, adapter, compliance, and meta-skill cites. Not invoked directly; referenced by name.
type: core
invocable: false
---

# Lore — Core substrate

This skill is a reference hub. It is never invoked by the user. Every other lore skill cites its documents by path.

## Documents

- **[`frontmatter-schema.md`](./frontmatter-schema.md)** — the YAML frontmatter contract. Required and optional fields. Validated by `scripts/validate.py`.
- **[`id-scheme.md`](./id-scheme.md)** — the `YYYY-MM-DD-<slug>` ID format. Generated by `scripts/new-id.sh`.
- **[`cross-ref-grammar.md`](./cross-ref-grammar.md)** — the `[[archetype:id]]` grammar for linking records.
- **[`tier-model.md`](./tier-model.md)** — the live / archive / canon tiers and the cooling pipeline thesis.
- **[`directory-layout.md`](./directory-layout.md)** — the `.lore/<tier>/<archetype>/<id>.md` layout.

## Scripts

The Layer-0 scripts are at the plugin root `scripts/`:

- **`scripts/new-id.sh`** — ID generation.
- **`scripts/validate.py`** — frontmatter schema validation.
- **`scripts/git-events.sh`** — git log → JSON lines for harvesting.

## Vocabulary (pillar concepts)

| Word | Role |
|------|------|
| **timeline** | The medium — every record has a timestamp; tiers are phases on a timeline. |
| **checkpoint** | The act of writing — what each archetype invocation produces. |
| **recall** | The retrieval motion — enabled by cross-refs, grep, `meta/link`. |
| **lore** | The canonical destination — canon-tier output, the product. |
| **legacy** | The long-horizon accumulation — what a project earns over years. |

## For authors of new archetypes, adapters, compliance skills

Every SKILL.md in the lore suite must:

1. Follow the core frontmatter schema (no custom primary fields).
2. Use `YYYY-MM-DD-<slug>` IDs generated by `scripts/new-id.sh`.
3. Use `[[archetype:id]]` cross-ref grammar.
4. Specify its default tier (`live`/`archive`/`canon`) in SKILL.md frontmatter.
5. Pass `scripts/validate.py` for any example records it publishes.

Any divergence breaks interoperability with `meta/link`, `meta/audit`, and `meta/promote`.
```

- [ ] **Step 9.2: Commit**

```bash
git add skills/core/SKILL.md
git commit -m "feat(core): SKILL.md index / reference hub for layer-0 substrate"
```

---

### Task 10: Claude Code plugin manifest

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 10.1: Write `.claude-plugin/plugin.json`**

```json
{
  "name": "lore",
  "description": "Turn your project's lived history into structured project memory. Timeline · checkpoint · recall · lore · legacy.",
  "version": "0.1.0",
  "author": {
    "name": "host452b",
    "email": ""
  },
  "homepage": "https://github.com/host452b/lore.skill",
  "repository": "https://github.com/host452b/lore.skill",
  "license": "MIT",
  "keywords": [
    "skills",
    "changelog",
    "adr",
    "project-memory",
    "dead-ends",
    "try-failed-exp",
    "knowledge-management"
  ]
}
```

- [ ] **Step 10.2: Write `.claude-plugin/marketplace.json`**

```json
{
  "name": "lore-dev",
  "description": "Development marketplace for the lore plugin",
  "owner": {
    "name": "host452b",
    "email": ""
  },
  "plugins": [
    {
      "name": "lore",
      "description": "Turn your project's lived history into structured project memory",
      "version": "0.1.0",
      "source": "./",
      "author": {
        "name": "host452b",
        "email": ""
      }
    }
  ]
}
```

- [ ] **Step 10.3: Validate JSON**

```bash
python3 -m json.tool .claude-plugin/plugin.json > /dev/null
python3 -m json.tool .claude-plugin/marketplace.json > /dev/null
```

Expected: no output (valid JSON).

- [ ] **Step 10.4: Commit**

```bash
git add .claude-plugin/
git commit -m "feat(install): Claude Code plugin + marketplace manifests"
```

---

### Task 11: Cursor plugin manifest

**Files:**
- Create: `.cursor-plugin/plugin.json`

- [ ] **Step 11.1: Write `.cursor-plugin/plugin.json`**

```json
{
  "name": "lore",
  "displayName": "Lore",
  "description": "Turn your project's lived history into structured project memory. Timeline · checkpoint · recall · lore · legacy.",
  "version": "0.1.0",
  "author": {
    "name": "host452b",
    "email": ""
  },
  "homepage": "https://github.com/host452b/lore.skill",
  "repository": "https://github.com/host452b/lore.skill",
  "license": "MIT",
  "keywords": [
    "skills",
    "changelog",
    "adr",
    "project-memory",
    "dead-ends",
    "try-failed-exp",
    "knowledge-management"
  ],
  "skills": "./skills/",
  "hooks": "./hooks/hooks-cursor.json"
}
```

- [ ] **Step 11.2: Validate JSON**

```bash
python3 -m json.tool .cursor-plugin/plugin.json > /dev/null
```

- [ ] **Step 11.3: Commit**

```bash
git add .cursor-plugin/
git commit -m "feat(install): Cursor plugin manifest"
```

---

### Task 12: Hooks — SessionStart

Modeled on Superpowers exactly. The `run-hook.cmd` is a polyglot bash/batch wrapper; `session-start` is a bash script that reads `skills/using-lore/SKILL.md`, JSON-escapes it, and emits context injection in a platform-aware envelope.

**Files:**
- Create: `hooks/hooks.json`
- Create: `hooks/hooks-cursor.json`
- Create: `hooks/run-hook.cmd`
- Create: `hooks/session-start`
- Create: `tests/hooks/test_session-start.bats`

- [ ] **Step 12.1: Write `hooks/hooks.json`**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 12.2: Write `hooks/hooks-cursor.json`**

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CURSOR_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 12.3: Write `hooks/run-hook.cmd`**

```
: << 'CMDBLOCK'
@echo off
REM Cross-platform polyglot wrapper for hook scripts.
REM On Windows: cmd.exe runs the batch portion, which finds and calls bash.
REM On Unix: the shell interprets this as a script.
REM Hook scripts use extensionless filenames so Claude Code's Windows
REM auto-detection doesn't interfere.
REM Usage: run-hook.cmd <script-name> [args...]

if "%~1"=="" (
    echo run-hook.cmd: missing script name >&2
    exit /b 1
)

set "HOOK_DIR=%~dp0"

if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)
if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    "C:\Program Files (x86)\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

where bash >nul 2>nul
if %ERRORLEVEL% equ 0 (
    bash "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

exit /b 0
CMDBLOCK

# Unix bash path
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "run-hook.cmd: missing script name" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_NAME="$1"
shift

exec bash "${SCRIPT_DIR}/${HOOK_NAME}" "$@"
```

- [ ] **Step 12.4: Write `hooks/session-start`**

```bash
#!/usr/bin/env bash
# SessionStart hook for the lore plugin.
# Reads skills/using-lore/SKILL.md and injects it into the session context.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

using_content=$(cat "${PLUGIN_ROOT}/skills/using-lore/SKILL.md" 2>&1 \
  || echo "Error reading using-lore skill")

escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

using_escaped=$(escape_for_json "$using_content")

session_context="<EXTREMELY_IMPORTANT>\nYou have lore.\n\n**Below is the full content of your 'lore:using-lore' skill - your introduction to the lore suite. For all other lore skills, use the 'Skill' tool:**\n\n${using_escaped}\n</EXTREMELY_IMPORTANT>"

# Emit platform-appropriate envelope.
# Cursor: additional_context (snake_case).
# Claude Code: hookSpecificOutput.additionalContext (nested).
# Copilot CLI and SDK standard: additionalContext (top-level).
if [ -n "${CURSOR_PLUGIN_ROOT:-}" ]; then
  printf '{\n  "additional_context": "%s"\n}\n' "$session_context"
elif [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -z "${COPILOT_CLI:-}" ]; then
  printf '{\n  "hookSpecificOutput": {\n    "hookEventName": "SessionStart",\n    "additionalContext": "%s"\n  }\n}\n' "$session_context"
else
  printf '{\n  "additionalContext": "%s"\n}\n' "$session_context"
fi

exit 0
```

- [ ] **Step 12.5: Make executables**

```bash
chmod +x hooks/run-hook.cmd hooks/session-start
```

- [ ] **Step 12.6: Write hook integration test**

```bash
# tests/hooks/test_session-start.bats
setup() {
  export REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
  export RUN_HOOK="$REPO_ROOT/hooks/run-hook.cmd"
}

@test "session-start emits Claude Code envelope when CLAUDE_PLUGIN_ROOT set" {
  CLAUDE_PLUGIN_ROOT="$REPO_ROOT" CURSOR_PLUGIN_ROOT="" COPILOT_CLI="" \
    run bash "$RUN_HOOK" session-start
  [ "$status" -eq 0 ]
  echo "$output" | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
assert 'hookSpecificOutput' in o, o
assert o['hookSpecificOutput']['hookEventName'] == 'SessionStart'
assert 'lore' in o['hookSpecificOutput']['additionalContext'].lower()
"
}

@test "session-start emits Cursor envelope when CURSOR_PLUGIN_ROOT set" {
  CLAUDE_PLUGIN_ROOT="" CURSOR_PLUGIN_ROOT="$REPO_ROOT" \
    run bash "$RUN_HOOK" session-start
  [ "$status" -eq 0 ]
  echo "$output" | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
assert 'additional_context' in o, o
assert 'lore' in o['additional_context'].lower()
"
}

@test "session-start emits SDK-standard envelope when no platform env set" {
  CLAUDE_PLUGIN_ROOT="" CURSOR_PLUGIN_ROOT="" COPILOT_CLI="1" \
    run bash "$RUN_HOOK" session-start
  [ "$status" -eq 0 ]
  echo "$output" | python3 -c "
import json, sys
o = json.loads(sys.stdin.read())
assert 'additionalContext' in o and 'hookSpecificOutput' not in o, o
"
}
```

- [ ] **Step 12.7: Run hook test — expect FAIL**

The test requires `skills/using-lore/SKILL.md` which doesn't exist yet. It will either fail with a read error, or succeed with "Error reading using-lore skill" as context. Run it:

```bash
bats tests/hooks/test_session-start.bats
```

Expected: tests fail (file not found in the cat step).

- [ ] **Step 12.8: Create a stub `skills/using-lore/SKILL.md` to unblock the hook test**

Just enough content to satisfy the read. The real content lands in Task 13.

```markdown
---
name: using-lore
description: stub
---
lore placeholder
```

- [ ] **Step 12.9: Run hook test — expect PASS**

```bash
bats tests/hooks/test_session-start.bats
```

Expected: all 3 tests PASS.

- [ ] **Step 12.10: Commit**

```bash
git add hooks/ tests/hooks/ skills/using-lore/
git commit -m "feat(install): SessionStart hook with platform-aware context injection"
```

---

### Task 13: `using-lore` SKILL.md (real content)

Replace the stub with the real primer skill that the session-start hook injects.

**Files:**
- Modify: `skills/using-lore/SKILL.md`

- [ ] **Step 13.1: Write real `skills/using-lore/SKILL.md`**

````markdown
---
name: using-lore
description: Use when starting any conversation on a project that has lore installed — establishes what lore is, the cooling-pipeline thesis, the 11 archetypes, the `lore:<skill>` naming convention, and when to proactively invoke lore skills.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# Lore

Lore turns this project's lived history — deploys, experiments, decisions, failed attempts, incidents, releases — into structured, cross-referenced, git-tracked project memory stored under `.lore/`.

## The thesis — the cooling pipeline

```
LIVE  ────► ARCHIVE ────► CANON
raw         crystallized   reusable rule
```

- **Live (流):** high-churn event signal. `journal`, `intent-log`, `dependency-ledger`.
- **Archive (档):** one-time retrospection. `postmortem`, `retro`, `release-notes`.
- **Canon (典):** reusable rules. `codex` (decisions), `try-failed-exp` (attempts that failed), `migration-guide`.

Information phase-transitions cold-ward over time. `lore:promote` operates the pipeline.

## Vocabulary

`timeline` · `checkpoint` · `recall` · `lore` · `legacy`

## Skills you can invoke

**Archetypes (the primary user-facing nouns):**

- `lore:journal` — record a discrete event (deploy, incident, experiment run)
- `lore:codex` — record a decision (ADR, design doc)
- `lore:try-failed-exp` — record an attempt that failed (spike that didn't pan out, library evaluated but not chosen, approach rejected)
- `lore:postmortem`, `lore:retro`, `lore:intent-log`, `lore:deprecation-tracker`, `lore:migration-guide`, `lore:api-changelog`, `lore:dependency-ledger`, `lore:release-notes` *(later versions)*

**Adapters (format bridges):**

- `lore:from-git-log` — harvest candidate records from git commits
- `lore:to-keep-a-changelog` — export release-notes to CHANGELOG.md

**Meta (automation glue):**

- `lore:detect` — first-run project scan, suggests starter archetypes
- `lore:harvest` — batch-import candidate records from git/issues/external sources
- `lore:promote` — cooling-pipeline operator *(v0.2)*
- `lore:link`, `lore:audit`, `lore:migrate` *(later)*

## When to proactively invoke lore

- User mentions a decision they just made → consider `lore:codex`.
- User mentions an approach they tried and abandoned → consider `lore:try-failed-exp`.
- User asks "have we tried X before?" → check `.lore/canon/try-failed-exp/`.
- User asks "why did we choose Y?" → check `.lore/canon/codex/`.
- User is starting a new session in a project with no `.lore/` yet → consider suggesting `lore:detect`.
- User is starting a session in a project with a long git history but an empty `.lore/` → consider suggesting `lore:harvest`.

## What lore is NOT

- Not a logging/observability tool. Lore records are human-written or human-confirmed.
- Not a wiki. Lore records are short, typed, cross-referenced.
- Not an incident-management platform. `postmortem` is the retrospection artifact, not the runbook.
- Not user-level memory. Lore is project-scoped; each consuming project has its own `.lore/`.

## Where lore stores things

```
<project-root>/
└── .lore/
    ├── live/<archetype>/<YYYY-MM-DD-slug>.md
    ├── archive/YYYY/<archetype>/<YYYY-MM-DD-slug>.md
    └── canon/<archetype>/<YYYY-MM-DD-slug>.md
```

All files are YAML-frontmatter + markdown. Git-tracked by default.

## Core conventions

- **ID format:** `YYYY-MM-DD-<slug>` (generator: `scripts/new-id.sh`)
- **Cross-refs:** `[[archetype:id]]` (e.g. `[[codex:2026-01-04-postgres-primary-db]]`)
- **Validation:** `scripts/validate.py <path>` checks frontmatter schema

For full details see `skills/core/`:
- `frontmatter-schema.md`, `id-scheme.md`, `cross-ref-grammar.md`, `tier-model.md`, `directory-layout.md`
````

- [ ] **Step 13.2: Re-run hook test to confirm the real content flows through**

```bash
bats tests/hooks/test_session-start.bats
```

Expected: 3 tests PASS. The "lore in output" assertion still holds because "lore" appears throughout.

- [ ] **Step 13.3: Commit**

```bash
git add skills/using-lore/SKILL.md
git commit -m "feat(install): using-lore SKILL.md primer injected by session-start hook"
```

---

### Task 14: CLAUDE.md primer

`CLAUDE.md` at the plugin root is auto-loaded by Claude Code and sets high-level context at the plugin level (complements the per-session injection from `using-lore`).

**Files:**
- Create: `CLAUDE.md`

- [ ] **Step 14.1: Write `CLAUDE.md`**

```markdown
# Claude Code guide — Lore plugin

You are working in the repo for the **lore** plugin — a Claude Code / Cursor plugin that turns a project's lived history (deploys, decisions, failed attempts, incidents, releases) into structured project memory.

## This repo is the plugin source

When Claude Code installs lore into a user's project, the files under `skills/`, `hooks/`, `scripts/`, `.claude-plugin/` are what get loaded. This repo's root is both the development repo and the plugin distribution.

## Key artifacts in this repo

- **Charter:** `docs/superpowers/specs/2026-04-17-lore-charter-design.md` — the architectural design for the full suite. Read this first when onboarding.
- **Per-spec plans:** `docs/superpowers/plans/*.md` — implementation plans per spec.
- **Skills:** `skills/<name>/SKILL.md` — each a separate lore skill.
- **Scripts:** `scripts/` — three Layer-0 helpers (`new-id.sh`, `validate.py`, `git-events.sh`).
- **Hooks:** `hooks/` — SessionStart hook that primes the `using-lore` skill each session.

## When working on this repo

- Each per-skill change should be tested (bats for shell, pytest for Python).
- The charter is the source of truth for architecture decisions. If a change diverges, update the charter first.
- Dogfood: this repo uses its own `to-keep-a-changelog` adapter for `CHANGELOG.md` (from v0.2 onward).

## When lore is installed in a *consuming* project

A session-start hook injects the `using-lore` skill content. That skill tells the agent about the 11 archetypes, the cooling pipeline, and when to proactively invoke `lore:<skill>` commands.
```

- [ ] **Step 14.2: Commit**

```bash
git add CLAUDE.md
git commit -m "feat(install): CLAUDE.md primer for plugin-development context"
```

---

### Task 15: README install instructions (final pass)

Task 1 wrote a minimal README. Expand it now that the install infrastructure exists, matching charter §4.2's install table.

**Files:**
- Modify: `README.md`

- [ ] **Step 15.1: Rewrite `README.md`**

```markdown
# Lore

**Turn your project's lived history into structured, cross-referenced, git-tracked memory.**

`timeline` · `checkpoint` · `recall` · `lore` · `legacy`

Lore is a Claude Code / Cursor plugin. Its skills capture deploys, experiments, decisions, failed attempts, incidents, and releases as typed records under `.lore/`, then distill them into reusable project canon.

Its anchor skill — `lore:try-failed-exp` — gives every project a place to record the things that *didn't* work, so future engineers don't retry them blindly.

## The three-axe MVP (v0.1)

1. **`lore:journal`** — universal event stream (profiles: `web-service`, `ml-experiment`)
2. **`lore:codex`** — curated decisions & design (profiles: `adr`, `design-doc`)
3. **`lore:try-failed-exp`** — the differentiator: a map of attempts that failed

Plus: `lore:harvest` to bootstrap from git history, `lore:to-keep-a-changelog` to export CHANGELOG.md.

## Installation

### Claude Code (community marketplace)

```bash
/plugin marketplace add host452b/lore-marketplace
/plugin install lore@lore-marketplace
```

### Cursor

```text
/add-plugin lore
```

or search "lore" in the plugin marketplace.

### Other platforms

Codex, OpenCode, and Gemini CLI support land in v0.2–v0.3. See [charter §5.1](docs/superpowers/specs/2026-04-17-lore-charter-design.md) for the roadmap.

## First-session UX

1. Install the plugin.
2. Start a fresh session — the SessionStart hook injects the `using-lore` primer so the agent knows the vocabulary and archetypes.
3. Ask the agent to `lore:detect` — it scans your project and suggests a starter set.
4. Ask `lore:harvest` — it reads your git history and drafts candidate records for you to confirm.
5. Write your first `lore:try-failed-exp` or `lore:codex` by hand in under 2 minutes.

No config file is required to start.

## Where records live

```
<your-project>/
└── .lore/
    ├── live/     ← high-churn: journal, intent-log, dependency-ledger
    ├── archive/  ← one-time: postmortem, retro, release-notes
    └── canon/    ← reusable: codex, try-failed-exp, migration-guide
```

Git-tracked by default. Your lore ships with your repo.

## Design

The full architectural charter is at [`docs/superpowers/specs/2026-04-17-lore-charter-design.md`](docs/superpowers/specs/2026-04-17-lore-charter-design.md). It covers:

- The **cooling pipeline** thesis (the core idea: information flows live → archive → canon)
- All 11 archetype skills and when to use each
- The 5-layer architecture (core, archetypes, compliance, adapters, meta)
- The installation architecture (matches Superpowers)
- Roadmap v0.1 → v1.0

## License

MIT © host452b
```

- [ ] **Step 15.2: Commit**

```bash
git add README.md
git commit -m "docs: expand README with install instructions, UX walkthrough, design pointer"
```

---

### Task 16: End-to-end validation and dogfood

Prove the substrate works against a real record: write a `try-failed-exp` record about *building lore itself* and validate it.

**Files:**
- Create: `.lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md` (dogfood)

- [ ] **Step 16.1: Generate the ID**

```bash
mkdir -p .lore/canon/try-failed-exp
bash scripts/new-id.sh --date 2026-04-17 --slug no-runtime-plugin-system \
  --dir .lore/canon/try-failed-exp
```

Expected output: `2026-04-17-no-runtime-plugin-system`.

- [ ] **Step 16.2: Write the record**

Save to `.lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md`:

```markdown
---
id: 2026-04-17-no-runtime-plugin-system
type: try-failed-exp
tier: canon
date: 2026-04-17
title: Runtime plugin system for lore extensions (rejected)
authors: ["host452b <>"]
profile: rejected-adr
status: rejected
tags: ["architecture", "extensibility"]
---

# Runtime plugin system for lore extensions (rejected)

## What was considered

Instead of YAML profiles + markdown SKILL.md as the sole extension
points, let third parties register runtime plugins (Python or JS
modules) that could hook into archetype writes, mutate records, or
add new archetypes at load time.

## Why it was rejected

- Moves the extension surface from "edit a YAML file" (non-programmer
  friendly) to "ship a Python package" (programmer-only).
- Introduces a versioning nightmare: runtime plugins depending on
  internal APIs that would change as the suite evolves.
- Breaks the Superpowers-style ethos of markdown-first, LLM-native.
- YAML profiles + a markdown "advanced rules" escape hatch cover ≥95%
  of the extension cases we can anticipate.

## What was chosen instead

- Profiles as YAML files under `skills/<archetype>/profiles/`.
- Advanced-rules markdown files referenced from a profile when a
  profile genuinely needs logic beyond declarative fields.
- Compliance overlays, adapters, and meta-skills as additional
  SKILL.md files — no plugin registry, no runtime loading.

## Don't retry unless

Someone demonstrates that:
1. A real extension use case is blocked by the YAML + markdown
   approach, AND
2. The proposed runtime plugin API has a realistic versioning /
   sandboxing story.
```

- [ ] **Step 16.3: Validate it**

```bash
source .venv/bin/activate
python3 scripts/validate.py .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md
```

Expected: `OK: .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md`

- [ ] **Step 16.4: Run the full test suite**

```bash
bats tests/scripts/test_new-id.bats
bats tests/scripts/test_git-events.bats
bats tests/hooks/test_session-start.bats
pytest tests/scripts/test_validate.py -v
```

Expected: every test PASSES.

- [ ] **Step 16.5: Commit the dogfood record**

```bash
git add .lore/
git commit -m "dogfood: first try-failed-exp record — rejected runtime plugin system"
```

- [ ] **Step 16.6: Clean up placeholder tests from Task 2**

Remove the two placeholder tests now that real tests exist:

```bash
git rm tests/scripts/test_placeholder.py tests/scripts/test_placeholder.bats
git commit -m "chore: remove placeholder tests now that real tests exist"
```

---

## Self-review

### Spec coverage check

| Charter requirement | Task # |
|---|---|
| §3.1 frontmatter schema | 3 |
| §3.2 ID scheme | 4 |
| §3.2 cross-ref grammar | 5 |
| §3.2 tier mechanics (including path-vs-frontmatter agreement) | 6 |
| §2.3 directory layout doc | 7 |
| Layer-0 scripts: `new-id.sh` | 4 |
| Layer-0 scripts: `validate.py` | 3, 6 |
| Layer-0 scripts: `git-events.sh` | 8 |
| `skills/core/SKILL.md` reference hub | 9 |
| §4.1 `package.json` | 1 |
| §4.1 `.claude-plugin/` | 10 |
| §4.1 `.cursor-plugin/` | 11 |
| §4.1 `hooks/` (hooks.json, hooks-cursor.json, run-hook.cmd, session-start) | 12 |
| §4.1 `CLAUDE.md` primer | 14 |
| §4.3 SessionStart hook primes `using-lore` | 12, 13 |
| §4.4 zero-config UX (no required config file) | 13, 15 |
| §4.6 naming convention (`lore:<name>`) | 13 |
| §4.2 install commands in README | 15 |
| End-to-end dogfood validation | 16 |

All v0.1 foundation items covered.

### Placeholder scan

No "TBD", "implement later", "similar to earlier task", or "add error handling" in any step. Every code step has complete code.

### Type / name consistency

- `validate.py` function `validate()` — consistent across Tasks 3 and 6.
- `new-id.sh` flags `--slug`, `--date`, `--dir` — consistent across Task 4 tests and implementation.
- `git-events.sh` output fields `sha`, `subject`, `author`, `email`, `date`, `files_changed`, `insertions`, `deletions`, `is_revert`, `is_merge`, `tags` — consistent between test assertions (Task 8 Step 8.1) and implementation (Task 8 Step 8.3).
- `run-hook.cmd` first-argument contract (script name) — consistent across Task 12 Steps 12.3 (impl), 12.6 (test).
- `session-start` filename (no extension) — consistent with `run-hook.cmd` invocation.
- `using-lore` SKILL.md — stub in Task 12, real content in Task 13 replaces the stub.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-17-lore-core-substrate-and-install.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Good fit here because tasks are mostly independent once Task 2 (test infra) is in.

2. **Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints for review. Better if you want to watch the TDD cycles live.

**Which approach?**
