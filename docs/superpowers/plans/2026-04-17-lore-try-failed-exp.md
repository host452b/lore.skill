# Lore — `try-failed-exp` Archetype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `lore:try-failed-exp` archetype and the `rejected-adr` profile, extending `scripts/validate.py` to be profile-aware so future archetypes can declare their own required fields and body sections.

**Architecture:** Extends Spec 1's Layer-0 substrate. `validate.py` gains a profile loader (reads `skills/<archetype>/profiles/<name>.yaml`) and a body-section grep, plus one archetype-specific hardcoded check (the "Don't retry unless" heading for every `try-failed-exp` record). The archetype itself ships as a standard SKILL.md + one YAML profile + one markdown template + one example record. No changes to install infrastructure, hooks, or other Spec 1 artifacts.

**Tech Stack:** Python 3.9+ (validator), PyYAML (profile loader — already installed in Spec 1), pytest (test runner — already wired), plain markdown (skill content).

**Spec reference:** `docs/superpowers/specs/2026-04-17-lore-try-failed-exp-design.md`

**Branch:** `feat/spec-2-try-failed-exp` (already exists, forked from `main`, spec already committed at `24cedf5`)

---

## File Structure

Files created:

- `skills/try-failed-exp/SKILL.md` — archetype skill (7-part template + "How to retrieve past records")
- `skills/try-failed-exp/profiles/rejected-adr.yaml` — profile YAML
- `skills/try-failed-exp/templates/rejected-adr.md` — body template with placeholder tokens
- `skills/try-failed-exp/examples/2026-03-12-rejected-redis-cluster.md` — fully-filled example record

Test fixtures:

- `tests/fixtures/valid/2026-03-12-rejected-redis-cluster.md` — copy of the example, used as regression fixture
- `tests/fixtures/invalid/tfe-missing-dont-retry-unless.md`
- `tests/fixtures/invalid/tfe-missing-what-was-chosen-instead.md`
- `tests/fixtures/invalid/tfe-reassessed-without-superseded-by.md`
- `tests/fixtures/invalid/tfe-unknown-profile.md`
- `tests/fixtures/invalid/tfe-bad-status.md`

Files modified:

- `scripts/validate.py` — add `load_body()`, profile loader, archetype-specific try-failed-exp block (status enum, `## Don't retry unless` check, profile-declared `required_sections` body grep, `status: reassessed` ↔ `superseded_by` consistency, unknown-profile error). Roughly 80-100 LOC added.
- `tests/scripts/test_validate.py` — 6 new test cases (5 invalid fixtures + 1 dogfood-regression test).

Total: **10 new files, 2 extended.**

---

## Pre-task setup

Current state at the start of this plan:

- Branch `feat/spec-2-try-failed-exp` exists, based on `main` at `e446e06`.
- One commit on the branch: `24cedf5` (the design doc for Spec 2).
- Working dir: `/Users/joejiang/changelog_skill/try-failed-log.skill/`
- Spec 1's test suite on main: 10 pytest + 7 + 5 + 3 bats = 25/25 passing. Must still pass after every task in this plan.
- `.venv/` already has pytest + PyYAML installed.
- `scripts/validate.py` currently validates core schema only (no profile awareness).

---

### Task 1: Scaffolding — skill directory + profile YAML

Lays down the directory layout and creates the profile YAML file. Pure data, no tests.

**Files:**
- Create: `skills/try-failed-exp/profiles/rejected-adr.yaml`

- [ ] **Step 1.1: Create skill dir structure**

```bash
mkdir -p skills/try-failed-exp/profiles skills/try-failed-exp/templates skills/try-failed-exp/examples
```

- [ ] **Step 1.2: Write `skills/try-failed-exp/profiles/rejected-adr.yaml`**

```yaml
name: rejected-adr
extends: try-failed-exp
description: ADR-style record of an option considered but not adopted. Lists
  what was on the table, why it was ruled out, what was chosen instead, and
  the condition that would justify revisiting.

# Body sections the validator enforces (as `## ` headings).
# "## Don't retry unless" is required at the archetype level for every
# try-failed-exp record regardless of profile and is NOT repeated here.
required_sections:
  - "## What was considered"
  - "## Why it was rejected"
  - "## What was chosen instead"

template: templates/rejected-adr.md

detect:
  suggest-when:
    - files-exist: ["docs/adr/", "docs/architecture/", "docs/decisions/"]
    - has-dependency: ["@nygard/adr-tools"]
```

- [ ] **Step 1.3: Sanity-check the YAML parses**

```bash
source .venv/bin/activate
python3 -c "import yaml; print(yaml.safe_load(open('skills/try-failed-exp/profiles/rejected-adr.yaml')))"
```

Expected: prints a dict with keys `name`, `extends`, `description`, `required_sections`, `template`, `detect`. No exceptions.

- [ ] **Step 1.4: Commit**

```bash
git add skills/try-failed-exp/profiles/rejected-adr.yaml
git commit -m "feat(try-failed-exp): scaffold skill dir + rejected-adr profile YAML"
```

---

### Task 2: Validator — try-failed-exp required fields + status enum (TDD)

Adds two required-field rules when `type == try-failed-exp`: `profile` is required, `status` must be one of `{rejected, on-hold, reassessed}`. These are the archetype-level fields per spec §2.2.

**Files:**
- Create: `tests/fixtures/invalid/tfe-bad-status.md`
- Modify: `scripts/validate.py`
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 2.1: Write invalid fixture — bad status**

Create `tests/fixtures/invalid/tfe-bad-status.md`:

```markdown
---
id: 2026-04-17-bad-status-tfe
type: try-failed-exp
tier: canon
date: 2026-04-17
title: Bad status
authors: ["Joe <j@example.com>"]
profile: rejected-adr
status: maybe
---

# Bad status

## What was considered
Stub.

## Why it was rejected
Stub.

## What was chosen instead
Stub.

## Don't retry unless
Stub.
```

- [ ] **Step 2.2: Add failing test**

Append to `tests/scripts/test_validate.py`:

```python
def test_tfe_bad_status_fails():
    r = run_validate(FIXTURES / "invalid" / "tfe-bad-status.md")
    assert r.returncode != 0
    assert "status" in r.stderr.lower()
```

- [ ] **Step 2.3: Run test — expect FAIL**

```bash
source .venv/bin/activate
pytest tests/scripts/test_validate.py::test_tfe_bad_status_fails -v
```

Expected: FAIL — the validator currently accepts any `status` value for try-failed-exp.

- [ ] **Step 2.4: Extend `scripts/validate.py`**

Near the top of the file (with the other module-level constants), add:

```python
TFE_STATUS = frozenset({"rejected", "on-hold", "reassessed"})
```

In `validate()`, after the existing archetype-generic checks and BEFORE `return errors`, add:

```python
    # Archetype-specific rules: try-failed-exp
    if fm.get("type") == "try-failed-exp":
        if "profile" not in fm:
            errors.append("try-failed-exp records require a 'profile' field")
        if "status" not in fm:
            errors.append("try-failed-exp records require a 'status' field")
        elif fm["status"] not in TFE_STATUS:
            errors.append(
                f"try-failed-exp status must be one of {sorted(TFE_STATUS)}; "
                f"got {fm['status']!r}"
            )
```

- [ ] **Step 2.5: Run new test — expect PASS**

```bash
pytest tests/scripts/test_validate.py::test_tfe_bad_status_fails -v
```

Expected: PASS.

- [ ] **Step 2.6: Run the full validator test suite — expect no regressions**

```bash
pytest tests/scripts/test_validate.py -v
```

Expected: all previous tests still pass + the new one passes.

NOTE: The existing dogfood record `.lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md` has `profile: rejected-adr` and `status: rejected` — both valid. Verify directly:

```bash
python3 scripts/validate.py .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md
```

Expected: `OK: ...`, exit 0.

- [ ] **Step 2.7: Commit**

```bash
git add scripts/validate.py tests/scripts/test_validate.py tests/fixtures/invalid/tfe-bad-status.md
git commit -m "feat(validate): try-failed-exp requires profile + enum-validated status"
```

---

### Task 3: Validator — profile loader + unknown-profile error (TDD)

Adds profile-file lookup. If a record declares `profile: <name>` with a known archetype, the validator attempts to load `skills/<archetype>/profiles/<name>.yaml`. Missing profile file → clear error.

**Files:**
- Create: `tests/fixtures/invalid/tfe-unknown-profile.md`
- Modify: `scripts/validate.py`
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 3.1: Write fixture — unknown profile**

Create `tests/fixtures/invalid/tfe-unknown-profile.md`:

```markdown
---
id: 2026-04-17-unknown-profile
type: try-failed-exp
tier: canon
date: 2026-04-17
title: Unknown profile
authors: ["Joe <j@example.com>"]
profile: nonexistent
status: rejected
---

# Unknown profile

## What was considered
Stub.

## Why it was rejected
Stub.

## What was chosen instead
Stub.

## Don't retry unless
Stub.
```

- [ ] **Step 3.2: Add failing test**

Append to `tests/scripts/test_validate.py`:

```python
def test_tfe_unknown_profile_fails():
    r = run_validate(FIXTURES / "invalid" / "tfe-unknown-profile.md")
    assert r.returncode != 0
    assert "profile" in r.stderr.lower()
    assert "nonexistent" in r.stderr.lower() or "not found" in r.stderr.lower()
```

- [ ] **Step 3.3: Run — expect FAIL**

```bash
pytest tests/scripts/test_validate.py::test_tfe_unknown_profile_fails -v
```

Expected: FAIL (validator currently ignores unknown profile names).

- [ ] **Step 3.4: Implement profile loader**

Near the top of `scripts/validate.py`, after the imports, add:

```python
# Plugin root for profile lookup. This file lives at <plugin-root>/scripts/validate.py,
# so the plugin root is the parent of scripts/.
PLUGIN_ROOT = Path(__file__).resolve().parent.parent
```

Add a loader helper (place it near `load_frontmatter`):

```python
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
```

In `validate()`, after the try-failed-exp `status` check from Task 2, add a profile-loading branch. Replace the existing Task 2 block:

```python
    # Archetype-specific rules: try-failed-exp
    if fm.get("type") == "try-failed-exp":
        if "profile" not in fm:
            errors.append("try-failed-exp records require a 'profile' field")
        if "status" not in fm:
            errors.append("try-failed-exp records require a 'status' field")
        elif fm["status"] not in TFE_STATUS:
            errors.append(
                f"try-failed-exp status must be one of {sorted(TFE_STATUS)}; "
                f"got {fm['status']!r}"
            )
```

…with the extended version that also loads the profile:

```python
    # Archetype-specific rules: try-failed-exp
    if fm.get("type") == "try-failed-exp":
        if "profile" not in fm:
            errors.append("try-failed-exp records require a 'profile' field")
        if "status" not in fm:
            errors.append("try-failed-exp records require a 'status' field")
        elif fm["status"] not in TFE_STATUS:
            errors.append(
                f"try-failed-exp status must be one of {sorted(TFE_STATUS)}; "
                f"got {fm['status']!r}"
            )
        # Profile must resolve to a real file under skills/try-failed-exp/profiles/
        if "profile" in fm:
            try:
                load_profile("try-failed-exp", str(fm["profile"]))
            except ValidationError as e:
                errors.append(str(e))
```

- [ ] **Step 3.5: Run — expect PASS**

```bash
pytest tests/scripts/test_validate.py::test_tfe_unknown_profile_fails -v
```

Expected: PASS.

- [ ] **Step 3.6: Full suite — no regressions**

```bash
pytest tests/scripts/test_validate.py -v
python3 scripts/validate.py .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md
```

Expected: all pass; dogfood record still `OK:`.

- [ ] **Step 3.7: Commit**

```bash
git add scripts/validate.py tests/scripts/test_validate.py tests/fixtures/invalid/tfe-unknown-profile.md
git commit -m "feat(validate): load profile YAML for try-failed-exp; error on unknown profile"
```

---

### Task 4: Validator — archetype-level "## Don't retry unless" body heading (TDD)

Every try-failed-exp record must have a `## Don't retry unless` heading followed by non-empty content. Validator greps body.

**Files:**
- Create: `tests/fixtures/invalid/tfe-missing-dont-retry-unless.md`
- Modify: `scripts/validate.py`
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 4.1: Write fixture — missing the heading**

Create `tests/fixtures/invalid/tfe-missing-dont-retry-unless.md`:

```markdown
---
id: 2026-04-17-missing-dru
type: try-failed-exp
tier: canon
date: 2026-04-17
title: Missing Don't retry unless
authors: ["Joe <j@example.com>"]
profile: rejected-adr
status: rejected
---

# Missing Don't retry unless

## What was considered
Stub.

## Why it was rejected
Stub.

## What was chosen instead
Stub.
```

(No `## Don't retry unless` section — deliberately.)

- [ ] **Step 4.2: Add failing test**

Append to `tests/scripts/test_validate.py`:

```python
def test_tfe_missing_dont_retry_unless_fails():
    r = run_validate(FIXTURES / "invalid" / "tfe-missing-dont-retry-unless.md")
    assert r.returncode != 0
    assert "don't retry unless" in r.stderr.lower() or "retry" in r.stderr.lower()
```

- [ ] **Step 4.3: Run — expect FAIL**

```bash
pytest tests/scripts/test_validate.py::test_tfe_missing_dont_retry_unless_fails -v
```

Expected: FAIL.

- [ ] **Step 4.4: Add body loader and heading-grep helpers**

In `scripts/validate.py`, add:

```python
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
    (after `## ` and optional whitespace) matches heading_text exactly,
    case-insensitive, and the heading is followed by at least one
    non-blank, non-heading line of content.
    """
    lines = body.splitlines()
    target = heading_text.strip().lower()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.lower() == f"## {target}":
            # Look for at least one non-blank, non-## line after this one
            for follow in lines[i + 1:]:
                fs = follow.strip()
                if not fs:
                    continue
                if fs.startswith("##"):
                    return False  # Next heading hit with no content between
                return True
            return False
    return False
```

In `validate()`, inside the `try-failed-exp` block (same block you modified in Task 3), at the end — after the profile loader call — add:

```python
        # Archetype-level body requirement: "## Don't retry unless"
        body = load_body(path)
        if not body_has_heading(body, "Don't retry unless"):
            errors.append(
                "try-failed-exp records must contain a "
                "'## Don't retry unless' section with at least one line of content"
            )
```

- [ ] **Step 4.5: Run — expect PASS**

```bash
pytest tests/scripts/test_validate.py::test_tfe_missing_dont_retry_unless_fails -v
```

Expected: PASS.

- [ ] **Step 4.6: Full suite — no regressions**

```bash
pytest tests/scripts/test_validate.py -v
python3 scripts/validate.py .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md
```

Expected: all pass; dogfood still `OK:` (it has the heading).

- [ ] **Step 4.7: Commit**

```bash
git add scripts/validate.py tests/scripts/test_validate.py tests/fixtures/invalid/tfe-missing-dont-retry-unless.md
git commit -m "feat(validate): enforce '## Don't retry unless' heading for try-failed-exp"
```

---

### Task 5: Validator — profile-declared `required_sections` body grep (TDD)

Reads `required_sections` from the loaded profile YAML and checks each heading exists in the body.

**Files:**
- Create: `tests/fixtures/invalid/tfe-missing-what-was-chosen-instead.md`
- Modify: `scripts/validate.py`
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 5.1: Write fixture — missing "What was chosen instead"**

Create `tests/fixtures/invalid/tfe-missing-what-was-chosen-instead.md`:

```markdown
---
id: 2026-04-17-missing-chosen
type: try-failed-exp
tier: canon
date: 2026-04-17
title: Missing What was chosen instead
authors: ["Joe <j@example.com>"]
profile: rejected-adr
status: rejected
---

# Missing What was chosen instead

## What was considered
Stub.

## Why it was rejected
Stub.

## Don't retry unless
Stub.
```

(Missing `## What was chosen instead` — which is required by the `rejected-adr` profile but not by the archetype itself.)

- [ ] **Step 5.2: Add failing test**

Append to `tests/scripts/test_validate.py`:

```python
def test_tfe_missing_what_was_chosen_instead_fails():
    r = run_validate(FIXTURES / "invalid" / "tfe-missing-what-was-chosen-instead.md")
    assert r.returncode != 0
    assert "what was chosen instead" in r.stderr.lower() or "section" in r.stderr.lower()
```

- [ ] **Step 5.3: Run — expect FAIL**

```bash
pytest tests/scripts/test_validate.py::test_tfe_missing_what_was_chosen_instead_fails -v
```

Expected: FAIL.

- [ ] **Step 5.4: Extend try-failed-exp block to honor profile's `required_sections`**

In `scripts/validate.py`, find the try-failed-exp block you added in earlier tasks. Replace the `if "profile" in fm:` try/except block (which currently only does `load_profile` and appends its error):

```python
        if "profile" in fm:
            try:
                load_profile("try-failed-exp", str(fm["profile"]))
            except ValidationError as e:
                errors.append(str(e))
```

…with the version that also applies the profile's `required_sections`:

```python
        if "profile" in fm:
            profile_data = None
            try:
                profile_data = load_profile("try-failed-exp", str(fm["profile"]))
            except ValidationError as e:
                errors.append(str(e))
            if profile_data is not None:
                required = profile_data.get("required_sections") or []
                for section in required:
                    # Each entry is expected to look like "## What was considered".
                    # Strip the leading "## " for body_has_heading's heading_text arg.
                    heading = str(section).strip()
                    if heading.startswith("## "):
                        heading = heading[3:]
                    if not body_has_heading(load_body(path), heading):
                        errors.append(
                            f"profile {fm['profile']!r} requires "
                            f"'## {heading}' section (profile: "
                            f"required_sections); missing from body"
                        )
```

Note: this re-calls `load_body(path)` inside the loop. For v0.1 that's fine (files are small). If profiles grow to declare many sections we could cache `body` once; not now.

- [ ] **Step 5.5: Run — expect PASS**

```bash
pytest tests/scripts/test_validate.py::test_tfe_missing_what_was_chosen_instead_fails -v
```

Expected: PASS.

- [ ] **Step 5.6: Full suite — no regressions**

```bash
pytest tests/scripts/test_validate.py -v
python3 scripts/validate.py .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md
```

Expected: all pass; dogfood still `OK:` (it has all three profile-required sections).

- [ ] **Step 5.7: Commit**

```bash
git add scripts/validate.py tests/scripts/test_validate.py tests/fixtures/invalid/tfe-missing-what-was-chosen-instead.md
git commit -m "feat(validate): apply profile-declared required_sections to body"
```

---

### Task 6: Validator — status=reassessed requires `superseded_by` (TDD)

If `status == reassessed`, the record must have `superseded_by` pointing at the record that overturned it.

**Files:**
- Create: `tests/fixtures/invalid/tfe-reassessed-without-superseded-by.md`
- Modify: `scripts/validate.py`
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 6.1: Write fixture — reassessed without superseded_by**

Create `tests/fixtures/invalid/tfe-reassessed-without-superseded-by.md`:

```markdown
---
id: 2026-04-17-reassessed-orphan
type: try-failed-exp
tier: canon
date: 2026-04-17
title: Reassessed without superseded_by
authors: ["Joe <j@example.com>"]
profile: rejected-adr
status: reassessed
---

# Reassessed without superseded_by

## What was considered
Stub.

## Why it was rejected
Stub.

## What was chosen instead
Stub.

## Don't retry unless
Stub.
```

(Status is `reassessed` but `superseded_by` is absent.)

- [ ] **Step 6.2: Add failing test**

Append to `tests/scripts/test_validate.py`:

```python
def test_tfe_reassessed_without_superseded_by_fails():
    r = run_validate(FIXTURES / "invalid" / "tfe-reassessed-without-superseded-by.md")
    assert r.returncode != 0
    assert "superseded_by" in r.stderr.lower() or "reassessed" in r.stderr.lower()
```

- [ ] **Step 6.3: Run — expect FAIL**

```bash
pytest tests/scripts/test_validate.py::test_tfe_reassessed_without_superseded_by_fails -v
```

Expected: FAIL.

- [ ] **Step 6.4: Add the consistency rule**

In `scripts/validate.py`, at the end of the `try-failed-exp` block (after the body heading / required_sections checks), add:

```python
        # status: reassessed must be paired with superseded_by
        if fm.get("status") == "reassessed" and "superseded_by" not in fm:
            errors.append(
                "try-failed-exp with status='reassessed' must also set "
                "'superseded_by' pointing at the overturning record"
            )
```

- [ ] **Step 6.5: Run — expect PASS**

```bash
pytest tests/scripts/test_validate.py::test_tfe_reassessed_without_superseded_by_fails -v
```

Expected: PASS.

- [ ] **Step 6.6: Full suite**

```bash
pytest tests/scripts/test_validate.py -v
python3 scripts/validate.py .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md
```

Expected: all pass; dogfood `OK:` (its status is `rejected`, so the rule is a no-op for it).

- [ ] **Step 6.7: Commit**

```bash
git add scripts/validate.py tests/scripts/test_validate.py tests/fixtures/invalid/tfe-reassessed-without-superseded-by.md
git commit -m "feat(validate): reassessed try-failed-exp must set superseded_by"
```

---

### Task 7: Body template for `rejected-adr`

Ships `skills/try-failed-exp/templates/rejected-adr.md`. No tests (pure content).

**Files:**
- Create: `skills/try-failed-exp/templates/rejected-adr.md`

- [ ] **Step 7.1: Write the template**

Create `skills/try-failed-exp/templates/rejected-adr.md`:

```markdown
---
id: <YYYY-MM-DD-slug>
type: try-failed-exp
tier: canon
date: <YYYY-MM-DD>
title: <human title, e.g. "Redis Cluster as primary cache (rejected)">
authors: ["<Name <email>>"]
profile: rejected-adr
status: rejected
refs: []
tags: []
---

# <title>

## What was considered
<what approach, library, or architecture was on the table>

## Why it was rejected
<the constraints, evidence, or trade-offs that ruled it out — be specific enough
that a future reader can tell whether the reasoning still holds>

## What was chosen instead
<what was adopted in its place; cite the codex entry: [[codex:<id>]]>

## Don't retry unless
<specific, falsifiable condition(s) that would justify revisiting.
Avoid "if priorities change"; prefer concrete triggers like
"if Redis ships native cross-region replication" or
"if our event volume exceeds 50k writes/sec">
```

- [ ] **Step 7.2: Commit**

```bash
git add skills/try-failed-exp/templates/rejected-adr.md
git commit -m "feat(try-failed-exp): body template for rejected-adr profile"
```

---

### Task 8: Example record + valid fixture + regression tests

Ships the fully-filled example that also doubles as a valid-fixture regression test. Adds a test asserting the pre-existing dogfood record still validates.

**Files:**
- Create: `skills/try-failed-exp/examples/2026-03-12-rejected-redis-cluster.md`
- Create: `tests/fixtures/valid/2026-03-12-rejected-redis-cluster.md` (identical content)
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 8.1: Write the example record**

Create `skills/try-failed-exp/examples/2026-03-12-rejected-redis-cluster.md`:

```markdown
---
id: 2026-03-12-rejected-redis-cluster
type: try-failed-exp
tier: canon
date: 2026-03-12
title: Redis Cluster as primary session store (rejected)
authors: ["host452b <>"]
profile: rejected-adr
status: rejected
refs: ["[[codex:2026-03-15-postgres-primary-session-store]]"]
tags: ["database", "caching", "session-management"]
---

# Redis Cluster as primary session store (rejected)

## What was considered
Using Redis Cluster as the primary store for user sessions, replacing
the current PostgreSQL-backed sessions table. Target: 3-node cluster,
hash-slotted keyspace.

## Why it was rejected
- Cross-slot transaction limitations conflict with our atomic
  multi-key session invalidation pattern.
- Operational complexity of running a cluster exceeded the team's
  capacity given concurrent migrations.
- Benchmark showed PostgreSQL with UNLOGGED session table meets p99
  latency budget (12 ms vs 6 ms target — well within SLO).

## What was chosen instead
Stayed on PostgreSQL with an UNLOGGED session table and denormalized
session-index view. See [[codex:2026-03-15-postgres-primary-session-store]].

## Don't retry unless
- Session volume exceeds 50k writes/sec (currently ~8k) AND PG hits
  p99 latency breach, OR
- Redis ships native cross-slot transactions in a GA release.
```

- [ ] **Step 8.2: Copy the example into the fixtures directory**

```bash
cp skills/try-failed-exp/examples/2026-03-12-rejected-redis-cluster.md tests/fixtures/valid/2026-03-12-rejected-redis-cluster.md
```

Note: the filename stem matches the `id:` field (as required by the filename=id rule added in Spec 1 Task 6).

- [ ] **Step 8.3: Add regression tests**

Append to `tests/scripts/test_validate.py`:

```python
def test_tfe_example_rejected_redis_cluster_passes():
    r = run_validate(FIXTURES / "valid" / "2026-03-12-rejected-redis-cluster.md")
    assert r.returncode == 0, r.stderr


def test_tfe_dogfood_still_passes():
    """The dogfood record written in Spec 1 before the archetype formally
    existed must still validate under the new profile-aware rules."""
    repo_root = REPO_ROOT
    dogfood = repo_root / ".lore" / "canon" / "try-failed-exp" \
        / "2026-04-17-no-runtime-plugin-system.md"
    r = run_validate(dogfood)
    assert r.returncode == 0, r.stderr
```

- [ ] **Step 8.4: Run new tests — expect PASS**

```bash
pytest tests/scripts/test_validate.py::test_tfe_example_rejected_redis_cluster_passes tests/scripts/test_validate.py::test_tfe_dogfood_still_passes -v
```

Expected: both PASS.

- [ ] **Step 8.5: Run full suite**

```bash
pytest tests/scripts/test_validate.py -v
```

Expected: all pass. Count should be the Spec 1 count (10) + this plan's 6 new tests = 16 total, all green.

- [ ] **Step 8.6: Commit**

```bash
git add skills/try-failed-exp/examples/2026-03-12-rejected-redis-cluster.md tests/fixtures/valid/2026-03-12-rejected-redis-cluster.md tests/scripts/test_validate.py
git commit -m "feat(try-failed-exp): example record + valid-fixture regression tests"
```

---

### Task 9: Archetype `SKILL.md`

The archetype skill itself — the primary user-facing file. Follows the 7-part template from charter §3.3, plus the archetype-specific "How to retrieve past records" section.

**Files:**
- Create: `skills/try-failed-exp/SKILL.md`

- [ ] **Step 9.1: Write `skills/try-failed-exp/SKILL.md`**

Create the file with exactly this content (use real triple-backticks in the actual file; placeholder `‹‹‹` in this prompt is three backticks):

```markdown
---
name: try-failed-exp
description: Use when recording a decision to NOT adopt an approach — library
  evaluated but not picked, spike that didn't pan out, architectural option
  rejected. The canon-tier home for "don't retry this unless <specific condition>."
type: archetype
default-tier: canon
profiles: [rejected-adr]
---

# When to use me

Record a considered-but-not-adopted approach. Situations:

- The team evaluated a library/approach/architecture and decided against it.
- A spike or proof-of-concept reached a "no-go" conclusion.
- A performance optimization was attempted but produced no measurable benefit.
- An ADR-style decision chose A, rejecting B and C — capture B and C here.

# When NOT to use me (boundaries)

- **Not postmortem.** Postmortems record what happened during an incident.
  try-failed-exp records an intentional exploration that concluded in rejection.
- **Not a bug tracker.** Specific bugs belong in GitHub Issues / Jira / Linear.
- **Not intent-log.** intent-log captures "we plan to do X." try-failed-exp
  captures "we considered X and are not doing it."
- **Not journal.** Deploys, experiments, CI events are journal. "We tried the
  Redis cluster approach and are not adopting it" is try-failed-exp.

# Required fields (beyond core)

- `profile` — must name a profile at `skills/try-failed-exp/profiles/<name>.yaml`.
  v0.1 value: `rejected-adr`.
- `status` — one of `rejected`, `on-hold`, `reassessed`.

# Optional fields

- `superseded_by` — required when `status: reassessed`. Cross-ref to the record
  that overturned this rejection (usually a `codex` entry).
- `supersedes` — list of earlier try-failed-exp records this one consolidates.
- `refs` — outbound cross-refs. See `# Cross-refs` below.
- `tags`, `source` — see core frontmatter schema.

# Required body sections

Every try-failed-exp record must include this heading with non-empty content:

- `## Don't retry unless`

Additional required sections come from the profile. `rejected-adr` requires:

- `## What was considered`
- `## Why it was rejected`
- `## What was chosen instead`

The validator (`scripts/validate.py`) enforces both the archetype-level
heading and the profile-declared ones.

# Profile slots

- `rejected-adr` — ADR-style "option considered but not adopted" record.
  Path: `./profiles/rejected-adr.yaml`. Template: `./templates/rejected-adr.md`.
  Suggested when the project has `docs/adr/`, `docs/architecture/`, or
  `docs/decisions/` directories, or the `@nygard/adr-tools` dependency.

(Future profiles `spike-outcome`, `library-eval`, `perf-dead-end` land in v0.3
per the lore roadmap.)

# Lifecycle

Write-once. Records are not rewritten after authoring. To revisit a rejection:

1. Create a new canon entry (usually a `codex`) that overturns it.
2. In the old `try-failed-exp` record, flip `status: rejected` → `status: reassessed`
   and add `superseded_by: "[[codex:<new-id>]]"`.
3. Leave the body as authored — the archaeological trail ("what blocked it,
   what changed") is the whole point.

Records are never deleted. `lore:audit` (future) enforces this.

# How to write one

1. Generate the ID:

   ```bash
   bash scripts/new-id.sh --slug <short-kebab-phrase> --dir .lore/canon/try-failed-exp
   ```

2. Start from the template at `./templates/rejected-adr.md`. Copy to
   `.lore/canon/try-failed-exp/<id>.md`, substitute the placeholders, and
   write the four required sections.

3. In `## Don't retry unless`, state specific falsifiable conditions. Avoid
   vague phrases like "if priorities change" — prefer concrete triggers such
   as "if Redis ships native cross-slot transactions in a GA release" or
   "if event volume exceeds 50k writes/sec."

4. Validate:

   ```bash
   python3 scripts/validate.py .lore/canon/try-failed-exp/<id>.md
   ```

   Expect `OK:`. If the validator reports missing sections or fields, fix them.

5. Commit.

# Cross-refs

- Outbound `refs`:
  - `[[codex:<id>]]` (almost always) — the decision that was adopted instead.
  - `[[journal:<id>]]` — if the rejection was driven by a specific spike or
    experiment result.
  - `[[postmortem:<id>]]` — if an incident proved the approach unworkable.
- Inbound: a related `codex` entry should list this record in its own `refs`
  to document the rejected alternatives. `lore:link` (future) enforces the
  bidirectional pair.
- `superseded_by`: `[[codex:<id>]]` when the rejection is overturned.

# How to retrieve past records

Before proposing an approach X to the user, search the canon for it:

```bash
grep -rli "<approach keywords>" .lore/canon/try-failed-exp/
```

If a matching record exists, read it — especially its `## Don't retry unless`
clause. Decide:

- **Conditions unchanged.** Surface the prior rejection to the user rather
  than re-proposing X from scratch. Cite the record ID.
- **Conditions changed** (the don't-retry-unless clause has been met). Cite
  the record, explain what changed, and propose re-evaluation. If the new
  direction is adopted, write a `codex` entry and set the old try-failed-exp
  record's `status: reassessed` with `superseded_by` pointing at the new codex.

Never silently re-propose something the project has already rejected.
```

- [ ] **Step 9.2: Commit**

```bash
git add skills/try-failed-exp/SKILL.md
git commit -m "feat(try-failed-exp): archetype SKILL.md with 7-part contract + retrieve section"
```

---

### Task 10: Final verification + merge readiness

Run the entire test suite (Spec 1 + Spec 2), confirm every v0.1 behavior, and validate the ships-as-documentation example record.

**No new files. Verification-only task.**

- [ ] **Step 10.1: Run the full validator suite**

```bash
source .venv/bin/activate
pytest tests/scripts/test_validate.py -v
```

Expected: 16 tests passing (Spec 1's 10 + Spec 2's 6). All green.

- [ ] **Step 10.2: Run the full Spec 1 test suite (ensure no regressions)**

```bash
bats tests/scripts/test_new-id.bats
bats tests/scripts/test_git-events.bats
bats tests/hooks/test_session-start.bats
```

Expected: 7/7, 5/5, 3/3.

- [ ] **Step 10.3: Validate every shipped artifact**

```bash
python3 scripts/validate.py skills/try-failed-exp/examples/2026-03-12-rejected-redis-cluster.md
python3 scripts/validate.py .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md
python3 scripts/validate.py tests/fixtures/valid/2026-03-12-rejected-redis-cluster.md
python3 scripts/validate.py tests/fixtures/valid/2026-04-17-first-record.md
python3 scripts/validate.py tests/fixtures/valid/2026-04-17-adr-postgres-primary.md
```

Expected: five `OK:` lines.

- [ ] **Step 10.4: Sanity-check every invalid fixture still fails**

```bash
for f in tests/fixtures/invalid/tfe-*.md; do
  echo "=== $f ==="
  python3 scripts/validate.py "$f" || true
done
```

Expected: each fixture reports `ERROR:` with a clear message.

- [ ] **Step 10.5: Confirm profile YAML is well-formed**

```bash
python3 -c "import yaml; d = yaml.safe_load(open('skills/try-failed-exp/profiles/rejected-adr.yaml')); assert d['name'] == 'rejected-adr'; assert d['extends'] == 'try-failed-exp'; assert '## What was considered' in d['required_sections']; print('profile YAML OK')"
```

Expected: `profile YAML OK`.

- [ ] **Step 10.6: Commit a verification record**

None — Task 10 adds no artifacts. If any of the above failed, back up to the relevant task.

- [ ] **Step 10.7: Summary**

Branch `feat/spec-2-try-failed-exp` should now contain (counting from spec commit `24cedf5`):

- `24cedf5` — docs: spec
- 1 commit from Task 1 (profile YAML)
- 1 commit from each of Tasks 2-6 (validator TDD cycles)
- 1 commit from Task 7 (template)
- 1 commit from Task 8 (example + regression tests)
- 1 commit from Task 9 (SKILL.md)

= **10 commits** on top of main.

Ready for final cross-branch review + merge.

---

## Self-review

### Spec coverage

Mapping from design doc sections to tasks:

| Spec section | Task(s) |
|---|---|
| §1 (purpose / thesis / boundaries / triggers) | Task 9 (SKILL.md) |
| §2.1 (SKILL.md structure) | Task 9 |
| §2.2 (frontmatter: profile + status) | Task 2 (status enum), Task 3 (profile presence + loader) |
| §2.3 (body: `## Don't retry unless`) | Task 4 |
| §2.4 (lifecycle / state machine) | Task 9 (SKILL.md), Task 6 (reassessed + superseded_by enforcement) |
| §2.5 (cross-ref patterns) | Task 9 (SKILL.md documentation) |
| §2.6 (how to retrieve past records) | Task 9 (SKILL.md documentation) |
| §2.7 (validator extension) | Tasks 2-6 (profile loader, body grep, heading checks, consistency) |
| §3.1 (rejected-adr profile YAML) | Task 1 |
| §3.2 (body template) | Task 7 |
| §3.3 (example record) | Task 8 |
| §3.4 (SKILL.md checklist) | Task 9 |
| §3.5 (file layout) | Tasks 1, 7, 8, 9 create the files; Tasks 2-6 extend validate.py + test_validate.py |
| §3.6 (dogfood reconciliation — passes) | Task 8 regression test; verified in Task 10 |
| §4 (success criteria) | Task 10 |

No gaps.

### Placeholder scan

No "TBD", "TODO", "implement later", "similar to earlier task", or "add error handling". Every code step is either (a) a complete file from scratch or (b) a targeted find-and-replace with both the old block and the new block shown in full.

### Type / name consistency

- `TFE_STATUS` frozenset — defined in Task 2, used as-is in Task 2's validator branch. Not redefined later.
- `load_profile(archetype, profile_name)` — defined in Task 3, called in Task 3 and Task 5.
- `load_body(path)` — defined in Task 4, called in Tasks 4 and 5.
- `body_has_heading(body, heading_text)` — defined in Task 4, called in Tasks 4 and 5.
- `PLUGIN_ROOT` — defined in Task 3, used only by `load_profile`.
- The `try-failed-exp` branch in `validate()` is updated incrementally across Tasks 2-6. Each task shows the full replacement block that includes the accumulated logic from prior tasks, so reading any task in isolation gives the engineer the complete state of that block.
- Fixture filenames start with `tfe-` (try-failed-exp) consistently. Test function names use the full `test_tfe_...` prefix consistently.

No inconsistencies found.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-17-lore-try-failed-exp.md`. Two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks, fast iteration.

2. **Inline Execution** — execute tasks in this session using `executing-plans`, batch execution with checkpoints.

Which approach?
