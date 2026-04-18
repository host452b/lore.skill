# Lore — `journal` Archetype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `lore:journal` archetype + `web-service` profile, and generalize the profile mechanism by introducing an archetype-agnostic `apply_profile_fields()` helper that reads `fields:` blocks from profile YAMLs.

**Architecture:** Extends Spec 2's validator with (A) a `journal`-specific archetype block enforcing ISO-8601 `event-time`, `outcome` enum, forbidden `superseded_by`/`supersedes` (live-tier immutability), and (B) a new `apply_profile_fields()` helper that implements profile-declared frontmatter field rules (`type: enum`, `required: true`) per charter §3.4. The journal block uses this helper; try-failed-exp remains untouched (its profile has no `fields:` block, so refactor is YAGNI).

**Tech Stack:** Python 3.9+ (validator), PyYAML (already installed), pytest + bats (already wired).

**Spec reference:** `docs/superpowers/specs/2026-04-17-lore-journal-design.md`

**Branch:** `feat/spec-3-journal` (exists, forked from main, spec committed at `a3940cb`)

---

## File Structure

Files created:

- `skills/journal/SKILL.md` — archetype skill (10-section template: standard 7-part + "Forbidden fields", "How the aggregate is consumed", and expanded `How to write one`)
- `skills/journal/profiles/web-service.yaml` — profile YAML with `fields:` block (event-type enum, environment enum)
- `skills/journal/templates/web-service.md` — body template
- `skills/journal/examples/2026-04-15-deploy-v1-3-2.md` — deploy event example
- `skills/journal/examples/2026-04-08-payment-api-incident.md` — incident event example

Test fixtures:
- `tests/fixtures/valid/2026-04-15-deploy-v1-3-2.md` — copy of deploy example
- `tests/fixtures/valid/2026-04-08-payment-api-incident.md` — copy of incident example
- `tests/fixtures/invalid/2026-04-17-journal-missing-event-time.md`
- `tests/fixtures/invalid/2026-04-17-journal-bad-event-time.md`
- `tests/fixtures/invalid/2026-04-17-journal-bad-outcome.md`
- `tests/fixtures/invalid/2026-04-17-journal-with-superseded-by.md`
- `tests/fixtures/invalid/2026-04-17-journal-missing-event-type.md`
- `tests/fixtures/invalid/2026-04-17-journal-bad-environment.md`

Files modified:
- `scripts/validate.py` — add `EVENT_TIME_RE`, `JOURNAL_OUTCOME` frozenset, `apply_profile_fields()` helper, and a `journal`-specific block in `validate()`. Roughly 80-100 LOC added.
- `tests/scripts/test_validate.py` — 8 new test cases (6 invalid fixtures × tests + 2 example regression tests).

**Total: 11 new files, 2 extended.**

---

## Pre-task setup

- Branch `feat/spec-3-journal` exists at commit `a3940cb` (the Spec 3 design).
- Main has Spec 1 + Spec 2 (33 tests passing: 18 pytest + 15 bats).
- `.venv/` has pytest + PyYAML from Spec 1.

---

### Task 1: Scaffolding — skill directory + profile YAML

Lays down the directory layout and creates the profile YAML. Pure data, no tests.

**Files:**
- Create: `skills/journal/profiles/web-service.yaml`

- [ ] **Step 1.1: Create directory structure**

```bash
mkdir -p skills/journal/profiles skills/journal/templates skills/journal/examples
```

- [ ] **Step 1.2: Write `skills/journal/profiles/web-service.yaml`**

```yaml
name: web-service
extends: journal
description: Events from running a web service — deploys, incidents, rollbacks,
  release cuts, migrations, CI failures. Scoped to a deployed environment.

# Profile-declared frontmatter fields (Spec 3's new `fields:` mechanism).
# Added to the archetype's own required fields (event-time, outcome, profile).
fields:
  event-type:
    type: enum
    values: [deploy, incident, rollback, release, migration, ci-failure]
    required: true
  environment:
    type: enum
    values: [prod, staging, dev, test]
    required: true

# No required_sections: journal body is free-form narrative.

template: templates/web-service.md

detect:
  suggest-when:
    - files-exist: ["package.json", "Dockerfile", "docker-compose.yml"]
    - files-exist: [".github/workflows/"]
    - has-dependency: ["express", "fastify", "django", "flask", "rails"]
```

- [ ] **Step 1.3: Sanity-check the YAML parses**

```bash
source .venv/bin/activate
python3 -c "import yaml; d = yaml.safe_load(open('skills/journal/profiles/web-service.yaml')); assert d['name'] == 'web-service'; assert d['extends'] == 'journal'; assert d['fields']['event-type']['type'] == 'enum'; assert 'deploy' in d['fields']['event-type']['values']; print('profile YAML OK')"
```

Expected: `profile YAML OK`.

- [ ] **Step 1.4: Commit**

```bash
git add skills/journal/profiles/web-service.yaml
git commit -m "feat(journal): scaffold skill dir + web-service profile YAML"
```

---

### Task 2: Validator — journal required fields + event-time format + outcome enum (TDD)

Adds a `journal`-specific archetype block to `validate.py`. The block enforces:
1. Required `profile` field
2. Required `event-time` field
3. `event-time` matches ISO 8601 (minute or second precision, Z or ±HH:MM)
4. Required `outcome` field
5. `outcome` in enum {succeeded, failed, partial, rolled-back, observed}
6. Loads profile YAML via `load_profile()` from Spec 2 (unknown-profile error is already covered by existing helper)

Three invalid fixtures + three tests; all share the same validator code block.

**Files:**
- Create: `tests/fixtures/invalid/2026-04-17-journal-missing-event-time.md`
- Create: `tests/fixtures/invalid/2026-04-17-journal-bad-event-time.md`
- Create: `tests/fixtures/invalid/2026-04-17-journal-bad-outcome.md`
- Modify: `scripts/validate.py`
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 2.1: Write three invalid fixtures**

`tests/fixtures/invalid/2026-04-17-journal-missing-event-time.md`:

```markdown
---
id: 2026-04-17-journal-missing-event-time
type: journal
tier: live
date: 2026-04-17
title: Journal missing event-time
authors: ["Joe <j@example.com>"]
profile: web-service
event-type: deploy
environment: prod
outcome: succeeded
---

# Journal missing event-time

Body narrative.
```

(No `event-time` field.)

`tests/fixtures/invalid/2026-04-17-journal-bad-event-time.md`:

```markdown
---
id: 2026-04-17-journal-bad-event-time
type: journal
tier: live
date: 2026-04-17
title: Journal with bare-date event-time
authors: ["Joe <j@example.com>"]
profile: web-service
event-time: 2026-04-17
event-type: deploy
environment: prod
outcome: succeeded
---

# Journal with bad event-time format

event-time should be ISO 8601 with time precision, not a bare date.
```

(`event-time: 2026-04-17` — date-only, missing time portion.)

`tests/fixtures/invalid/2026-04-17-journal-bad-outcome.md`:

```markdown
---
id: 2026-04-17-journal-bad-outcome
type: journal
tier: live
date: 2026-04-17
title: Journal with bad outcome
authors: ["Joe <j@example.com>"]
profile: web-service
event-time: 2026-04-17T12:00:00Z
event-type: deploy
environment: prod
outcome: maybe
---

# Journal with bad outcome

Body.
```

(`outcome: maybe` — not in enum.)

- [ ] **Step 2.2: Add failing tests**

Append to `tests/scripts/test_validate.py`:

```python

def test_journal_missing_event_time_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-journal-missing-event-time.md")
    assert r.returncode != 0
    assert "event-time" in r.stderr.lower()


def test_journal_bad_event_time_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-journal-bad-event-time.md")
    assert r.returncode != 0
    assert "event-time" in r.stderr.lower() or "iso" in r.stderr.lower()


def test_journal_bad_outcome_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-journal-bad-outcome.md")
    assert r.returncode != 0
    assert "outcome" in r.stderr.lower()
```

- [ ] **Step 2.3: Run tests — expect all three FAIL**

```bash
source .venv/bin/activate
pytest tests/scripts/test_validate.py -v -k "journal_missing_event_time or journal_bad_event_time or journal_bad_outcome"
```

Expected: 3 FAIL (validator does not yet know about journal).

- [ ] **Step 2.4: Extend `scripts/validate.py`**

Near the top with the other module-level constants, add:

```python
EVENT_TIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2}|Z)?$"
)
JOURNAL_OUTCOME = frozenset(
    {"succeeded", "failed", "partial", "rolled-back", "observed"}
)
```

Inside `validate()`, BEFORE `return errors` and AFTER the existing `try-failed-exp` block, add a new journal block:

```python
    # Archetype-specific rules: journal
    if fm.get("type") == "journal":
        if "profile" not in fm:
            errors.append("journal records require a 'profile' field")
        if "event-time" not in fm:
            errors.append("journal records require an 'event-time' field")
        elif not EVENT_TIME_RE.match(str(fm["event-time"])):
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
```

Note: this block is intentionally minimal. Forbidden-fields (Task 3) and profile `fields:` enforcement (Tasks 4–5) extend it incrementally.

- [ ] **Step 2.5: Run — expect PASS**

```bash
pytest tests/scripts/test_validate.py -v -k "journal_missing_event_time or journal_bad_event_time or journal_bad_outcome"
```

Expected: 3 PASS.

- [ ] **Step 2.6: Full suite — no regressions**

```bash
pytest tests/scripts/test_validate.py -v
```

Expected: 21/21 passing (18 prior + 3 new).

- [ ] **Step 2.7: Commit**

```bash
git add scripts/validate.py tests/scripts/test_validate.py tests/fixtures/invalid/2026-04-17-journal-missing-event-time.md tests/fixtures/invalid/2026-04-17-journal-bad-event-time.md tests/fixtures/invalid/2026-04-17-journal-bad-outcome.md
git commit -m "feat(validate): journal archetype requires event-time (ISO 8601) + outcome enum"
```

---

### Task 3: Validator — journal forbidden supersede fields (TDD)

Live-tier records are truly immutable. Validator rejects `superseded_by` / `supersedes` on journal records.

**Files:**
- Create: `tests/fixtures/invalid/2026-04-17-journal-with-superseded-by.md`
- Modify: `scripts/validate.py`
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 3.1: Write invalid fixture**

`tests/fixtures/invalid/2026-04-17-journal-with-superseded-by.md`:

```markdown
---
id: 2026-04-17-journal-with-superseded-by
type: journal
tier: live
date: 2026-04-17
title: Journal trying to supersede
authors: ["Joe <j@example.com>"]
profile: web-service
event-time: 2026-04-17T12:00:00Z
event-type: deploy
environment: prod
outcome: succeeded
superseded_by: "[[journal:2026-04-18-redeploy]]"
---

# Journal trying to supersede

Journal records are immutable — this record should fail validation.
```

- [ ] **Step 3.2: Add failing test**

Append to `tests/scripts/test_validate.py`:

```python

def test_journal_with_superseded_by_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-journal-with-superseded-by.md")
    assert r.returncode != 0
    assert "immutable" in r.stderr.lower() or "superseded_by" in r.stderr.lower()
```

- [ ] **Step 3.3: Run — expect FAIL**

```bash
pytest tests/scripts/test_validate.py::test_journal_with_superseded_by_fails -v
```

Expected: FAIL (validator currently accepts `superseded_by` on journal).

- [ ] **Step 3.4: Extend `validate.py`**

Find the journal block in `validate()`. At the end of it (inside the `if fm.get("type") == "journal":` branch, after the profile loader call from Task 2), add:

```python
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
```

- [ ] **Step 3.5: Run — expect PASS**

```bash
pytest tests/scripts/test_validate.py::test_journal_with_superseded_by_fails -v
```

Expected: PASS.

- [ ] **Step 3.6: Full suite**

```bash
pytest tests/scripts/test_validate.py -v
```

Expected: 22/22 passing.

- [ ] **Step 3.7: Commit**

```bash
git add scripts/validate.py tests/scripts/test_validate.py tests/fixtures/invalid/2026-04-17-journal-with-superseded-by.md
git commit -m "feat(validate): journal rejects superseded_by/supersedes (live-tier immutability)"
```

---

### Task 4: Validator — `apply_profile_fields` helper (required-field rule, TDD)

Introduces the archetype-agnostic `apply_profile_fields(profile_data, fm, errors)` helper that handles profile YAML's `fields:` block. Starts with the required-field rule; enum-value check lands in Task 5.

**Files:**
- Create: `tests/fixtures/invalid/2026-04-17-journal-missing-event-type.md`
- Modify: `scripts/validate.py`
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 4.1: Write invalid fixture**

`tests/fixtures/invalid/2026-04-17-journal-missing-event-type.md`:

```markdown
---
id: 2026-04-17-journal-missing-event-type
type: journal
tier: live
date: 2026-04-17
title: Journal missing event-type
authors: ["Joe <j@example.com>"]
profile: web-service
event-time: 2026-04-17T12:00:00Z
environment: prod
outcome: succeeded
---

# Journal missing event-type

Body.
```

(`event-type` is declared required by `web-service.yaml`'s `fields:` block.)

- [ ] **Step 4.2: Add failing test**

Append to `tests/scripts/test_validate.py`:

```python

def test_journal_missing_event_type_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-journal-missing-event-type.md")
    assert r.returncode != 0
    assert "event-type" in r.stderr.lower()
```

- [ ] **Step 4.3: Run — expect FAIL**

```bash
pytest tests/scripts/test_validate.py::test_journal_missing_event_type_fails -v
```

- [ ] **Step 4.4: Add `apply_profile_fields` helper**

In `scripts/validate.py`, near the other helpers (`load_profile`, `load_body`, `body_has_heading`), add:

```python
def apply_profile_fields(profile_data: dict, fm: dict, errors: list) -> None:
    """Enforce a profile YAML's `fields:` block against frontmatter.

    For each field declared in profile_data['fields']:
      - If required and missing from frontmatter, emit an error.
      - If present and declared type is 'enum', verify the value is in `values`.

    Unsupported types are silently skipped for forward compatibility.
    """
    fields_decl = profile_data.get("fields") or {}
    for field_name, field_spec in fields_decl.items():
        if not isinstance(field_spec, dict):
            continue
        required = bool(field_spec.get("required"))
        if required and field_name not in fm:
            errors.append(
                f"profile requires field {field_name!r} "
                f"(declared in profile fields:); missing from frontmatter"
            )
            continue
        # Enum-type checks land in Task 5
```

Now hook it into the journal block. Find the profile-loader call in the journal block:

```python
        if "profile" in fm:
            try:
                load_profile("journal", str(fm["profile"]))
            except ValidationError as e:
                errors.append(str(e))
```

Replace with the version that captures and applies the profile:

```python
        if "profile" in fm:
            profile_data = None
            try:
                profile_data = load_profile("journal", str(fm["profile"]))
            except ValidationError as e:
                errors.append(str(e))
            if profile_data is not None:
                apply_profile_fields(profile_data, fm, errors)
```

- [ ] **Step 4.5: Run — expect PASS**

```bash
pytest tests/scripts/test_validate.py::test_journal_missing_event_type_fails -v
```

- [ ] **Step 4.6: Full suite**

```bash
pytest tests/scripts/test_validate.py -v
```

Expected: 23/23 passing.

- [ ] **Step 4.7: Commit**

```bash
git add scripts/validate.py tests/scripts/test_validate.py tests/fixtures/invalid/2026-04-17-journal-missing-event-type.md
git commit -m "feat(validate): apply_profile_fields enforces required-field rule from profile fields: block"
```

---

### Task 5: Validator — `apply_profile_fields` enum value check (TDD)

Extends the helper to validate enum-type field values against the profile's `values:` list.

**Files:**
- Create: `tests/fixtures/invalid/2026-04-17-journal-bad-environment.md`
- Modify: `scripts/validate.py`
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 5.1: Write invalid fixture**

`tests/fixtures/invalid/2026-04-17-journal-bad-environment.md`:

```markdown
---
id: 2026-04-17-journal-bad-environment
type: journal
tier: live
date: 2026-04-17
title: Journal with bad environment
authors: ["Joe <j@example.com>"]
profile: web-service
event-time: 2026-04-17T12:00:00Z
event-type: deploy
environment: production
outcome: succeeded
---

# Journal with bad environment

`environment: production` is not in enum {prod, staging, dev, test} — should use `prod`.
```

- [ ] **Step 5.2: Add failing test**

Append to `tests/scripts/test_validate.py`:

```python

def test_journal_bad_environment_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-journal-bad-environment.md")
    assert r.returncode != 0
    assert "environment" in r.stderr.lower()
```

- [ ] **Step 5.3: Run — expect FAIL**

```bash
pytest tests/scripts/test_validate.py::test_journal_bad_environment_fails -v
```

- [ ] **Step 5.4: Extend `apply_profile_fields`**

In `scripts/validate.py`, replace the existing `apply_profile_fields` body (keeping the signature and docstring):

```python
def apply_profile_fields(profile_data: dict, fm: dict, errors: list) -> None:
    """Enforce a profile YAML's `fields:` block against frontmatter.

    For each field declared in profile_data['fields']:
      - If required and missing from frontmatter, emit an error.
      - If present and declared type is 'enum', verify the value is in `values`.

    Unsupported types are silently skipped for forward compatibility.
    """
    fields_decl = profile_data.get("fields") or {}
    for field_name, field_spec in fields_decl.items():
        if not isinstance(field_spec, dict):
            continue
        required = bool(field_spec.get("required"))
        if field_name not in fm:
            if required:
                errors.append(
                    f"profile requires field {field_name!r} "
                    f"(declared in profile fields:); missing from frontmatter"
                )
            continue
        value = fm[field_name]
        ftype = field_spec.get("type")
        if ftype == "enum":
            allowed = field_spec.get("values") or []
            if value not in allowed:
                errors.append(
                    f"profile field {field_name!r} must be one of {allowed}; "
                    f"got {value!r}"
                )
        # Other types (string, ref, markdown) are v0.2+
```

- [ ] **Step 5.5: Run — expect PASS**

```bash
pytest tests/scripts/test_validate.py::test_journal_bad_environment_fails -v
```

- [ ] **Step 5.6: Full suite**

```bash
pytest tests/scripts/test_validate.py -v
```

Expected: 24/24 passing.

- [ ] **Step 5.7: Commit**

```bash
git add scripts/validate.py tests/scripts/test_validate.py tests/fixtures/invalid/2026-04-17-journal-bad-environment.md
git commit -m "feat(validate): apply_profile_fields enforces enum-type value check"
```

---

### Task 6: Body template

Ships the web-service body template. No tests (pure content).

**Files:**
- Create: `skills/journal/templates/web-service.md`

- [ ] **Step 6.1: Write `skills/journal/templates/web-service.md`**

```markdown
---
id: <YYYY-MM-DD-slug>
type: journal
tier: live
date: <YYYY-MM-DD>
title: <short title, e.g. "Deploy v1.3.2 to prod">
authors: ["<Name <email>>"]
profile: web-service
event-time: <YYYY-MM-DDTHH:MM:SS+ZZ:ZZ or Z>
event-type: <deploy|incident|rollback|release|migration|ci-failure>
environment: <prod|staging|dev|test>
outcome: <succeeded|failed|partial|rolled-back|observed>
duration: <PT5M, omit if instantaneous>
commit-sha: <short or full sha, omit if not applicable>
metrics: {}
refs: []
tags: []
---

# <title>

<2-5 sentences: what happened, key numbers, link to runbook/dashboard
if relevant. Keep it short — journal entries aggregate, they don't drill
down individually.>
```

- [ ] **Step 6.2: Commit**

```bash
git add skills/journal/templates/web-service.md
git commit -m "feat(journal): body template for web-service profile"
```

---

### Task 7: Example records + valid-fixture regression tests

Ships the two example records + copies them into `tests/fixtures/valid/` as regression fixtures.

**Files:**
- Create: `skills/journal/examples/2026-04-15-deploy-v1-3-2.md`
- Create: `skills/journal/examples/2026-04-08-payment-api-incident.md`
- Create: `tests/fixtures/valid/2026-04-15-deploy-v1-3-2.md` (copy of deploy example)
- Create: `tests/fixtures/valid/2026-04-08-payment-api-incident.md` (copy of incident example)
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 7.1: Write deploy example**

Create `skills/journal/examples/2026-04-15-deploy-v1-3-2.md`:

```markdown
---
id: 2026-04-15-deploy-v1-3-2
type: journal
tier: live
date: 2026-04-15
title: Deploy v1.3.2 to prod
authors: ["host452b <>"]
profile: web-service
event-time: 2026-04-15T16:23:00+00:00
event-type: deploy
environment: prod
outcome: succeeded
duration: PT4M
commit-sha: 8f2e1a3
refs: ["[[codex:2026-03-15-postgres-primary-session-store]]"]
tags: ["release"]
---

# Deploy v1.3.2 to prod

Rolled the v1.3.2 tag to prod. Post-deploy health checks green. QPS
ramped from baseline 2k to 3.4k over 90 seconds as traffic cut over.
No alerts; session-store latency steady at 11ms p99.
```

- [ ] **Step 7.2: Write incident example**

Create `skills/journal/examples/2026-04-08-payment-api-incident.md`:

```markdown
---
id: 2026-04-08-payment-api-incident
type: journal
tier: live
date: 2026-04-08
title: Payment API 5xx spike — incident and recovery
authors: ["host452b <>"]
profile: web-service
event-time: 2026-04-08T09:14:00+00:00
event-type: incident
environment: prod
outcome: partial
duration: PT41M
metrics: {peak_5xx_per_min: 312, baseline_5xx_per_min: 4}
tags: ["payment", "oncall"]
---

# Payment API 5xx spike — incident and recovery

5xx rate on `/api/payments/*` jumped from baseline ~4/min to peak
312/min at 09:14Z. Root cause traced to a connection-pool exhaustion
on the payments DB after an ORM config change deployed in v1.3.1.
Mitigated by scaling the pool at 09:38Z; residual error rate returned
to baseline by 09:55Z. Postmortem to follow.
```

- [ ] **Step 7.3: Copy examples into fixtures/valid/**

```bash
cp skills/journal/examples/2026-04-15-deploy-v1-3-2.md \
   tests/fixtures/valid/2026-04-15-deploy-v1-3-2.md
cp skills/journal/examples/2026-04-08-payment-api-incident.md \
   tests/fixtures/valid/2026-04-08-payment-api-incident.md
```

- [ ] **Step 7.4: Add regression tests**

Append to `tests/scripts/test_validate.py`:

```python

def test_journal_deploy_example_passes():
    r = run_validate(FIXTURES / "valid" / "2026-04-15-deploy-v1-3-2.md")
    assert r.returncode == 0, r.stderr


def test_journal_incident_example_passes():
    r = run_validate(FIXTURES / "valid" / "2026-04-08-payment-api-incident.md")
    assert r.returncode == 0, r.stderr
```

- [ ] **Step 7.5: Run — expect PASS**

```bash
source .venv/bin/activate
pytest tests/scripts/test_validate.py::test_journal_deploy_example_passes tests/scripts/test_validate.py::test_journal_incident_example_passes -v
```

Expected: 2 PASS.

- [ ] **Step 7.6: Full suite**

```bash
pytest tests/scripts/test_validate.py -v
```

Expected: 26/26 passing (18 Spec 1+2 + 8 Spec 3).

- [ ] **Step 7.7: Commit**

```bash
git add skills/journal/examples/ tests/fixtures/valid/2026-04-15-deploy-v1-3-2.md tests/fixtures/valid/2026-04-08-payment-api-incident.md tests/scripts/test_validate.py
git commit -m "feat(journal): example records (deploy + incident) + regression tests"
```

---

### Task 8: Archetype `SKILL.md`

Ships the archetype skill. Follows the charter §3.3 7-part template + journal-specific "Forbidden fields" + "How the aggregate is consumed" sections.

**Files:**
- Create: `skills/journal/SKILL.md`

- [ ] **Step 8.1: Write `skills/journal/SKILL.md`**

Full content below. Uses real triple-backticks in the actual file (I use `‹‹‹` as a placeholder here).

```markdown
---
name: journal
description: Use when recording a discrete event — deploys, incidents,
  experiment runs, CI failures, rollbacks, version bumps. Timestamp-bearing
  facts. The raw material of the live tier.
type: archetype
default-tier: live
profiles: [web-service]
---

# When to use me

Record a discrete event that has a timestamp. Situations:

- A deploy, rollback, release cut, or version bump landed.
- An incident was detected, mitigated, and/or recovered.
- A scheduled experiment or MLflow run completed.
- A CI build of note ran (prod release build, migration CI, etc.).
- A dependency bump worth recording (major-version change, security patch).

The gatekeeper test: *could I put an ISO timestamp on this?* If yes, it's
probably journal.

# When NOT to use me (boundaries)

- **Not codex.** "We decided to use PostgreSQL" is a decision — codex.
  Journal records the event of a deploy/migration *landing*, not the decision.
- **Not try-failed-exp.** "We tried MongoDB and gave up" is a rejection —
  try-failed-exp. A rollback *event* is journal, but the conclusion is
  try-failed-exp.
- **Not postmortem.** Journal records "incident detected 14:23, resolved 15:07."
  Postmortem records the deeper retrospection. Postmortems cite journal entries
  as their timeline.
- **Not intent-log.** Intent-log captures "we plan to do X." Journal captures
  "X just happened."

# Required fields (beyond core)

- `profile` — must name a profile at `skills/journal/profiles/<name>.yaml`.
  v0.1 value: `web-service`.
- `event-time` — ISO 8601, minute or second precision:
  `2026-04-15T16:23:00+00:00` or `2026-04-15T16:23Z`.
- `outcome` — one of `succeeded`, `failed`, `partial`, `rolled-back`, `observed`.
  Use `observed` for purely informational events with no pass/fail semantics
  (dependency bump, CI green build).

# Optional fields

- `duration` — ISO 8601 duration: `PT2M`, `PT45S`, `PT1H30M`. Omit if instantaneous.
- `commit-sha` — short (7-char) or full (40-char) git SHA the event is tied to.
- `metrics` — free-form object: `{qps_before: 2000, qps_after: 3400}`.
- `refs`, `tags` — see core frontmatter schema.

# Forbidden fields (immutability)

Journal records are **truly immutable**. These fields are rejected:

- `superseded_by`
- `supersedes`

Events don't un-happen. If an event's facts were misrecorded, the correction
is a new journal record that `refs` the old one — NOT an edit. git history
preserves what was believed true at the time.

# Profile slots

- **`web-service`** — events from running a web service. Adds required
  `event-type` (`deploy`/`incident`/`rollback`/`release`/`migration`/`ci-failure`)
  and `environment` (`prod`/`staging`/`dev`/`test`). Suggested when the project
  has `package.json`, `Dockerfile`, `docker-compose.yml`, or a `.github/workflows/`
  directory.

Future profiles `ml-experiment`, `spike`, `build-log` land in v0.3.

# Lifecycle

Truly immutable. Once committed, the body and frontmatter never change.

To correct a journal record:

1. Write a new journal record with `title: "Correction to [[journal:<id>]]"`.
2. Add `refs: ["[[journal:<id>]]"]` pointing at the original.
3. Leave the original record as committed — do not edit it.

# How to write one

1. Generate the ID:

   ‹‹‹bash
   bash scripts/new-id.sh --slug <short-kebab-phrase> --dir .lore/live/journal
   ‹‹‹

   Note: dots in version tags must be replaced with hyphens
   (`v1.3.2` → `v1-3-2`) to satisfy the slug regex.

2. Start from the template at `./templates/web-service.md`. Copy to
   `.lore/live/journal/<id>.md`, substitute the placeholders, write the
   frontmatter fields and a short 2–5 sentence body.

3. Validate:

   ‹‹‹bash
   python3 scripts/validate.py .lore/live/journal/<id>.md
   ‹‹‹

   Expect `OK:`.

4. Commit.

# Cross-refs

- Outbound `refs`:
  - `[[codex:<id>]]` — the decision that drove this event (common for deploys).
  - `[[try-failed-exp:<id>]]` — when an incident confirms why something was rejected.
  - `[[journal:<id>]]` — corrections, rollback chains.
- Inbound (from other archetypes):
  - Postmortems cite multiple journal entries as their incident timeline.
  - Release-notes cite the journal entries of the deploys they summarize.
  - `meta/promote` consumes aggregate patterns, not individual records.

Journal is the most-cited-from, least-citing-out archetype in the suite.
Events are self-contained facts.

# How the aggregate is consumed

Journal records are typically read *en masse*, not one-by-one:

- **`meta/promote`** (v0.2) scans `.lore/live/journal/` for recurring patterns
  (e.g., three deploy rollbacks in the same month) and suggests codex or
  try-failed-exp entries distilling the lesson.
- **`meta/harvest`** (v0.2) and **`lore:from-git-log`** (v0.2) ingest existing
  git history and CI/incident tooling to produce candidate journal records
  for the user to confirm.
- Downstream archetypes (postmortem, release-notes) cite 3–10 journal entries
  each as timeline context.

When reading journal: `grep`, filter by `event-type` or `environment`, skim
titles — don't expect to find meaning in any single record.
```

**Write the file with REAL triple-backticks in place of `‹‹‹`.**

- [ ] **Step 8.2: Commit**

```bash
git add skills/journal/SKILL.md
git commit -m "feat(journal): archetype SKILL.md with 10-section contract"
```

---

### Task 9: Final verification + merge readiness

Runs the full test suite, validates every shipped artifact, confirms all invalid fixtures fail with targeted errors.

**Files:** verification-only.

- [ ] **Step 9.1: Run full pytest suite**

```bash
source .venv/bin/activate
pytest tests/scripts/test_validate.py -v
```

Expected: 26/26 passing (10 Spec 1 + 8 Spec 2 + 8 Spec 3).

- [ ] **Step 9.2: Run Spec 1 bats suites (no regressions)**

```bash
bats tests/scripts/test_new-id.bats
bats tests/scripts/test_git-events.bats
bats tests/hooks/test_session-start.bats
```

Expected: 7/7, 5/5, 3/3.

- [ ] **Step 9.3: Validate every shipped artifact**

```bash
python3 scripts/validate.py skills/journal/examples/2026-04-15-deploy-v1-3-2.md
python3 scripts/validate.py skills/journal/examples/2026-04-08-payment-api-incident.md
python3 scripts/validate.py skills/try-failed-exp/examples/2026-03-12-rejected-redis-cluster.md
python3 scripts/validate.py .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md
```

Expected: four `OK:` lines.

- [ ] **Step 9.4: Sanity-check every journal invalid fixture fails with targeted error**

```bash
for f in tests/fixtures/invalid/2026-04-17-journal-*.md; do
  echo "=== $f ==="
  python3 scripts/validate.py "$f" 2>&1 || true
done
```

Expected: 6 fixtures, each reports `ERROR:` with a message naming the violated rule (event-time / outcome / immutable/superseded_by / event-type / environment).

- [ ] **Step 9.5: Confirm profile YAML is well-formed**

```bash
python3 -c "import yaml; d = yaml.safe_load(open('skills/journal/profiles/web-service.yaml')); assert d['fields']['event-type']['type'] == 'enum'; assert d['fields']['environment']['required'] is True; print('profile YAML OK')"
```

- [ ] **Step 9.6: Summary**

Branch `feat/spec-3-journal` should now contain (counting from spec commit `a3940cb`):

- `a3940cb` — docs: Spec 3 design
- 1 commit from Task 1 (profile YAML scaffolding)
- 1 commit from Task 2 (journal required fields + event-time + outcome)
- 1 commit from Task 3 (forbidden supersede fields)
- 1 commit from Task 4 (apply_profile_fields — required rule)
- 1 commit from Task 5 (apply_profile_fields — enum rule)
- 1 commit from Task 6 (body template)
- 1 commit from Task 7 (example records + regression tests)
- 1 commit from Task 8 (SKILL.md)

= **9 commits** on top of main. Ready for final review + merge.

---

## Self-review

### Spec coverage

| Spec section | Task(s) |
|---|---|
| §1.1 (what the archetype is) | Task 8 (SKILL.md) |
| §1.2 (immutability vs canon) | Task 8 (SKILL.md lifecycle section) + Task 3 (validator rejects supersede fields) |
| §1.3 (boundaries) | Task 8 (SKILL.md) |
| §1.4 (proactive triggers) | Task 8 (SKILL.md) |
| §1.5 (differences from try-failed-exp) | Task 8 (SKILL.md; covered across sections) |
| §2.1 (SKILL.md structure) | Task 8 |
| §2.2 (frontmatter: event-time, outcome, profile) | Task 2 |
| §2.3 (forbidden fields) | Task 3 |
| §2.4 (lifecycle) | Task 8 (SKILL.md) |
| §2.5 (cross-ref patterns) | Task 8 (SKILL.md) |
| §2.6 (validator extension A: journal block) | Tasks 2, 3 |
| §2.7 (validator extension B: apply_profile_fields) | Tasks 4, 5 |
| §2.8 (LOC footprint ~60-90) | Distributed across Tasks 2-5 |
| §3.1 (web-service profile YAML) | Task 1 |
| §3.2 (body template) | Task 6 |
| §3.3 (example records) | Task 7 |
| §3.4 (SKILL.md) | Task 8 |
| §3.5 (file layout) | Tasks 1, 6, 7, 8 |
| §3.6 (test plan) | Tasks 2-5 (invalid fixtures), Task 7 (valid examples), Task 9 (final verification) |

No gaps.

### Placeholder scan

No "TBD", "TODO", "implement later", "similar to earlier task". Every code step contains complete code or a targeted replacement with both old and new shown.

### Type / name consistency

- `EVENT_TIME_RE`, `JOURNAL_OUTCOME` module constants — defined in Task 2, used in Task 2's block, never redefined.
- `apply_profile_fields(profile_data, fm, errors)` — signature introduced in Task 4, extended (same signature) in Task 5.
- `load_profile`, `load_body`, `body_has_heading` — existing Spec 2 helpers, reused unchanged.
- `PLUGIN_ROOT` — existing Spec 2 constant, reused by `load_profile`.
- Fixture filename stems match their `id:` fields consistently (e.g., `2026-04-17-journal-missing-event-time.md` has `id: 2026-04-17-journal-missing-event-time`). This is required by Spec 1 Task 6's filename=id rule.
- Invalid-fixture filenames use `2026-04-17-journal-<rule>.md` pattern consistently.
- Valid-example filenames use real event dates (`2026-04-15`, `2026-04-08`), not today's date, because these simulate real records.

No inconsistencies found.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-17-lore-journal.md`. Two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks, fast iteration.

2. **Inline Execution** — batch execution in this session using `executing-plans` with checkpoints.

Which approach?
