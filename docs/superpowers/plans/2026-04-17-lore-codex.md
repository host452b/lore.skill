# Lore — `codex` Archetype Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `lore:codex` archetype + `adr` profile — canon-tier decision records. Smallest validator extension in the suite (~20-30 LOC) because the profile mechanism already covers status enum (Spec 3 `apply_profile_fields`) and required body sections (Spec 2 `required_sections`).

**Architecture:** New `if fm.get("type") == "codex":` block in `validate.py` that declares required `profile`, invokes `load_profile`, calls `apply_profile_fields` (handles status enum via profile's `fields:` block), applies `required_sections` body grep (via profile YAML), and adds one new consistency rule: `status: superseded` requires `superseded_by`. Everything else is data (YAML profile, markdown template, SKILL.md, example record).

**Tech Stack:** Python 3.9+, PyYAML (already installed), pytest (already wired). No new dependencies, no new machinery.

**Spec reference:** `docs/superpowers/specs/2026-04-17-lore-codex-design.md`

**Branch:** `feat/spec-4-codex` (exists, forked from main, spec committed at `4218aa0`)

---

## File Structure

Files created:
- `skills/codex/SKILL.md` — archetype skill (~130 lines)
- `skills/codex/profiles/adr.yaml` — profile YAML with BOTH `fields:` (status enum) AND `required_sections:` (body headings)
- `skills/codex/templates/adr.md` — body template
- `skills/codex/examples/2026-03-15-postgres-primary-session-store.md` — example that completes existing cross-ref pair with Spec 2's try-failed-exp example
- `tests/fixtures/valid/2026-03-15-postgres-primary-session-store.md` — copy of example
- `tests/fixtures/invalid/2026-04-17-codex-missing-status.md`
- `tests/fixtures/invalid/2026-04-17-codex-bad-status.md`
- `tests/fixtures/invalid/2026-04-17-codex-missing-decision.md`
- `tests/fixtures/invalid/2026-04-17-codex-superseded-without-superseded-by.md`

Files modified:
- `scripts/validate.py` — new codex block (~20-30 LOC)
- `tests/scripts/test_validate.py` — 5 new test cases

**Total: 9 new files, 2 extended.**

---

## Pre-task setup

- Branch `feat/spec-4-codex` exists at `4218aa0` (the Spec 4 design).
- Main has Specs 1+2+3 (42 tests: 27 pytest + 15 bats).
- `.venv/` has pytest + PyYAML from Spec 1.
- Reusable helpers already in `scripts/validate.py`: `load_profile`, `load_body`, `body_has_heading`, `apply_profile_fields`, `ValidationError`, `PLUGIN_ROOT`.

---

### Task 1: Scaffolding — skill directory + `adr.yaml` profile

Create skill directory structure and the first profile YAML that uses BOTH `fields:` and `required_sections:`. Pure data, no tests.

**Files:**
- Create: `skills/codex/profiles/adr.yaml`

- [ ] **Step 1.1: Create directory structure**

```bash
mkdir -p skills/codex/profiles skills/codex/templates skills/codex/examples
```

- [ ] **Step 1.2: Write `skills/codex/profiles/adr.yaml`**

```yaml
name: adr
extends: codex
description: Michael Nygard-style Architecture Decision Record. Captures the
  context for a decision, the decision itself, and the consequences.

# Profile-declared frontmatter fields (Spec 3's `fields:` mechanism).
fields:
  status:
    type: enum
    values: [proposed, accepted, superseded, deprecated]
    required: true

# Profile-declared required body sections (Spec 2's mechanism).
required_sections:
  - "## Context"
  - "## Decision"
  - "## Consequences"

template: templates/adr.md

detect:
  suggest-when:
    - files-exist: ["docs/adr/", "docs/architecture/", "docs/decisions/"]
    - has-dependency: ["@nygard/adr-tools"]
```

- [ ] **Step 1.3: Sanity-check parse**

```bash
source .venv/bin/activate
python3 -c "import yaml; d = yaml.safe_load(open('skills/codex/profiles/adr.yaml')); assert d['name'] == 'adr'; assert d['extends'] == 'codex'; assert d['fields']['status']['type'] == 'enum'; assert 'accepted' in d['fields']['status']['values']; assert '## Decision' in d['required_sections']; print('adr profile YAML OK')"
```

Expected: `adr profile YAML OK`.

- [ ] **Step 1.4: Commit**

```bash
git add skills/codex/profiles/adr.yaml
git commit -m "feat(codex): scaffold skill dir + adr profile YAML (first to use fields+required_sections)"
```

---

### Task 2: Validator — codex block (TDD, 3 tests in one cycle)

Adds a `codex`-specific block to `validate.py`. All three failing tests exercise behavior that emerges automatically from the existing `apply_profile_fields` and `required_sections` mechanisms — the new code is just the glue block that invokes them.

**Files:**
- Create: `tests/fixtures/invalid/2026-04-17-codex-missing-status.md`
- Create: `tests/fixtures/invalid/2026-04-17-codex-bad-status.md`
- Create: `tests/fixtures/invalid/2026-04-17-codex-missing-decision.md`
- Modify: `scripts/validate.py`
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 2.1: Write three invalid fixtures**

`tests/fixtures/invalid/2026-04-17-codex-missing-status.md`:

```markdown
---
id: 2026-04-17-codex-missing-status
type: codex
tier: canon
date: 2026-04-17
title: Codex missing status
authors: ["Joe <j@example.com>"]
profile: adr
---

# Codex missing status

## Context
Stub.

## Decision
Stub.

## Consequences
Stub.
```

`tests/fixtures/invalid/2026-04-17-codex-bad-status.md`:

```markdown
---
id: 2026-04-17-codex-bad-status
type: codex
tier: canon
date: 2026-04-17
title: Codex with bad status
authors: ["Joe <j@example.com>"]
profile: adr
status: draft
---

# Codex with bad status

## Context
Stub.

## Decision
Stub.

## Consequences
Stub.
```

`tests/fixtures/invalid/2026-04-17-codex-missing-decision.md`:

```markdown
---
id: 2026-04-17-codex-missing-decision
type: codex
tier: canon
date: 2026-04-17
title: Codex missing Decision section
authors: ["Joe <j@example.com>"]
profile: adr
status: accepted
---

# Codex missing Decision section

## Context
Stub.

## Consequences
Stub.
```

(Deliberately no `## Decision` heading.)

- [ ] **Step 2.2: Add failing tests**

Append to `tests/scripts/test_validate.py`:

```python

def test_codex_missing_status_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-codex-missing-status.md")
    assert r.returncode != 0
    assert "status" in r.stderr.lower()


def test_codex_bad_status_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-codex-bad-status.md")
    assert r.returncode != 0
    assert "status" in r.stderr.lower()


def test_codex_missing_decision_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-codex-missing-decision.md")
    assert r.returncode != 0
    assert "decision" in r.stderr.lower() or "section" in r.stderr.lower()
```

- [ ] **Step 2.3: Run — expect 3 FAIL**

```bash
source .venv/bin/activate
pytest tests/scripts/test_validate.py -v -k "codex_missing_status or codex_bad_status or codex_missing_decision"
```

Expected: 3 FAIL (validator doesn't yet know about codex).

- [ ] **Step 2.4: Extend `scripts/validate.py`**

Inside `validate()`, BEFORE `return errors` and AFTER the existing journal block, add:

```python
    # Archetype-specific rules: codex
    if fm.get("type") == "codex":
        if "profile" not in fm:
            errors.append("codex records require a 'profile' field")
        # Profile existence + fields + required_sections (reuses Specs 2+3 helpers)
        if "profile" in fm:
            profile_data = None
            try:
                profile_data = load_profile("codex", str(fm["profile"]))
            except ValidationError as e:
                errors.append(str(e))
            if profile_data is not None:
                apply_profile_fields(profile_data, fm, errors)
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
```

Note: this block is intentionally identical in shape to the try-failed-exp profile block already in `validate.py`. The `status: superseded → superseded_by` consistency rule lands in Task 3.

- [ ] **Step 2.5: Run — expect 3 PASS**

```bash
pytest tests/scripts/test_validate.py -v -k "codex_missing_status or codex_bad_status or codex_missing_decision"
```

- [ ] **Step 2.6: Full suite**

```bash
pytest tests/scripts/test_validate.py -v
```

Expected: 30/30 passing (27 prior + 3 new).

- [ ] **Step 2.7: Commit**

```bash
git add scripts/validate.py tests/scripts/test_validate.py tests/fixtures/invalid/2026-04-17-codex-missing-status.md tests/fixtures/invalid/2026-04-17-codex-bad-status.md tests/fixtures/invalid/2026-04-17-codex-missing-decision.md
git commit -m "feat(validate): codex archetype block (reuses apply_profile_fields + required_sections)"
```

---

### Task 3: Validator — codex status=superseded consistency rule (TDD)

Adds the one codex-specific rule not covered by existing helpers: `status: superseded` requires `superseded_by`.

**Files:**
- Create: `tests/fixtures/invalid/2026-04-17-codex-superseded-without-superseded-by.md`
- Modify: `scripts/validate.py`
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 3.1: Invalid fixture**

`tests/fixtures/invalid/2026-04-17-codex-superseded-without-superseded-by.md`:

```markdown
---
id: 2026-04-17-codex-superseded-without-superseded-by
type: codex
tier: canon
date: 2026-04-17
title: Codex marked superseded without a forward pointer
authors: ["Joe <j@example.com>"]
profile: adr
status: superseded
---

# Codex marked superseded without a forward pointer

## Context
Stub.

## Decision
Stub.

## Consequences
Stub.
```

- [ ] **Step 3.2: Add failing test**

Append to `tests/scripts/test_validate.py`:

```python

def test_codex_superseded_without_superseded_by_fails():
    r = run_validate(FIXTURES / "invalid" / "2026-04-17-codex-superseded-without-superseded-by.md")
    assert r.returncode != 0
    assert "superseded" in r.stderr.lower()
```

- [ ] **Step 3.3: Run — expect FAIL**

```bash
pytest tests/scripts/test_validate.py::test_codex_superseded_without_superseded_by_fails -v
```

- [ ] **Step 3.4: Add the consistency rule**

In `scripts/validate.py`, find the codex block. At the END of it (inside the `if fm.get("type") == "codex":` branch, after the profile-applied checks), add:

```python
        # status: superseded must be paired with superseded_by
        if fm.get("status") == "superseded" and "superseded_by" not in fm:
            errors.append(
                "codex with status='superseded' must also set 'superseded_by' "
                "pointing at the overturning record"
            )
```

- [ ] **Step 3.5: Run — expect PASS**

```bash
pytest tests/scripts/test_validate.py::test_codex_superseded_without_superseded_by_fails -v
```

- [ ] **Step 3.6: Full suite**

```bash
pytest tests/scripts/test_validate.py -v
```

Expected: 31/31 passing.

- [ ] **Step 3.7: Commit**

```bash
git add scripts/validate.py tests/scripts/test_validate.py tests/fixtures/invalid/2026-04-17-codex-superseded-without-superseded-by.md
git commit -m "feat(validate): codex with status=superseded requires superseded_by"
```

---

### Task 4: Body template for `adr` profile

Ships the ADR body template.

**Files:**
- Create: `skills/codex/templates/adr.md`

- [ ] **Step 4.1: Write template**

`skills/codex/templates/adr.md`:

```markdown
---
id: <YYYY-MM-DD-slug>
type: codex
tier: canon
date: <YYYY-MM-DD>
title: <decision title, e.g. "Postgres as primary session store">
authors: ["<Name <email>>"]
profile: adr
status: proposed
refs: []
tags: []
---

# <title>

## Context
<what forces are at play? what's the problem?>

## Decision
<what did we decide? be specific — a future reader should be able to
tell whether their situation matches>

## Consequences
<what becomes easier? what becomes harder? what trade-offs are we
accepting? If there are rejected alternatives worth recording, write
them as `try-failed-exp:rejected-adr` records and cite them in `refs`.>
```

- [ ] **Step 4.2: Commit**

```bash
git add skills/codex/templates/adr.md
git commit -m "feat(codex): body template for adr profile"
```

---

### Task 5: Example record + bidirectional dogfood + regression test

Ships the codex example that completes the existing cross-ref pair with Spec 2's try-failed-exp example. Copies it into `tests/fixtures/valid/` and adds a regression test.

**Files:**
- Create: `skills/codex/examples/2026-03-15-postgres-primary-session-store.md`
- Create: `tests/fixtures/valid/2026-03-15-postgres-primary-session-store.md` (copy)
- Modify: `tests/scripts/test_validate.py`

- [ ] **Step 5.1: Write the example record**

`skills/codex/examples/2026-03-15-postgres-primary-session-store.md`:

```markdown
---
id: 2026-03-15-postgres-primary-session-store
type: codex
tier: canon
date: 2026-03-15
title: PostgreSQL as primary session store
authors: ["host452b"]
profile: adr
status: accepted
refs: ["[[try-failed-exp:2026-03-12-rejected-redis-cluster]]"]
tags: ["database", "session-management", "architecture"]
---

# PostgreSQL as primary session store

## Context
The application needs a reliable session store handling ~8k writes/sec
today with growth projected to ~20k/sec over 18 months. Sessions require
atomic multi-key invalidation (logout cascades, role changes invalidating
all active tokens for a user). Operational capacity is constrained:
two engineers shared across three services, concurrent migrations already
in progress.

## Decision
Use PostgreSQL with an UNLOGGED session table + denormalized session-index
view as the primary session store. Benchmark shows p99 latency of 11ms
against a 6ms target budget, well within SLO. Atomic multi-key operations
use standard PostgreSQL transactions.

## Consequences

**Easier:**
- Operational familiarity — the team already runs PostgreSQL.
- Atomic multi-key session invalidation via transactions.
- Single datastore to back up, monitor, and migrate.

**Harder:**
- Session latency (11ms p99) is higher than a pure cache would deliver
  (Redis benchmarked at 4ms), though still within SLO.
- Session table grows unbounded without a TTL job (mitigated by a daily
  cleanup of expired rows).

**Trade-offs accepted:** operational simplicity over raw latency. Revisit
if session volume exceeds 50k writes/sec AND PG hits p99 latency breach,
per the condition recorded in [[try-failed-exp:2026-03-12-rejected-redis-cluster]].

## Rejected alternatives

See [[try-failed-exp:2026-03-12-rejected-redis-cluster]] for the Redis
Cluster option that was considered and rejected.
```

- [ ] **Step 5.2: Copy into tests/fixtures/valid/**

```bash
cp skills/codex/examples/2026-03-15-postgres-primary-session-store.md \
   tests/fixtures/valid/2026-03-15-postgres-primary-session-store.md
```

Filename stem matches `id:` field (Spec 1 Task 6 rule).

- [ ] **Step 5.3: Add regression test**

Append to `tests/scripts/test_validate.py`:

```python

def test_codex_example_postgres_primary_passes():
    r = run_validate(FIXTURES / "valid" / "2026-03-15-postgres-primary-session-store.md")
    assert r.returncode == 0, r.stderr
```

- [ ] **Step 5.4: Run — expect PASS**

```bash
source .venv/bin/activate
pytest tests/scripts/test_validate.py::test_codex_example_postgres_primary_passes -v
```

- [ ] **Step 5.5: Full suite**

```bash
pytest tests/scripts/test_validate.py -v
```

Expected: 32/32 passing.

- [ ] **Step 5.6: Commit**

```bash
git add skills/codex/examples/2026-03-15-postgres-primary-session-store.md tests/fixtures/valid/2026-03-15-postgres-primary-session-store.md tests/scripts/test_validate.py
git commit -m "feat(codex): example record completing bidirectional cross-ref with try-failed-exp"
```

---

### Task 6: Archetype `SKILL.md`

Ships the archetype skill. 7-part charter template + archetype-specific "How to retrieve past decisions" section.

**Files:**
- Create: `skills/codex/SKILL.md`

- [ ] **Step 6.1: Write `skills/codex/SKILL.md`**

Use REAL triple-backticks in the file; `‹‹‹` is a placeholder in this prompt.

```markdown
---
name: codex
description: Use when recording a decision that has been made — ADR, design
  choice, adopted direction, convention. The canon-tier home for
  "do this, and here's why."
type: archetype
default-tier: canon
profiles: [adr]
---

# When to use me

Record a decision that has been made:

- Architectural choices: "we chose PostgreSQL as primary session store."
- Library or framework selections: "we chose FastAPI over Flask."
- Design direction: "we use hexagonal architecture for this service."
- Conventions and policies: "all public APIs return structured errors."

The gatekeeper test: *is this a decision we're committing to?* If yes,
codex. If it's "we're thinking about X," that's `intent-log`. If it's
"we considered X but rejected it," that's `try-failed-exp`.

# When NOT to use me (boundaries)

- **Not journal.** Journal records the *event* of a deploy or migration;
  codex records the *decision* behind it.
- **Not try-failed-exp.** Codex is what was adopted; try-failed-exp is
  what was rejected. A decision that says "we chose A, rejected B and C"
  produces one codex (A) + one or more try-failed-exp records (B, C).
- **Not intent-log.** Intent-log captures "we plan to do X"; codex
  captures a decision that has been made.
- **Not postmortem.** Postmortem is retrospection on an incident; a codex
  may be created *as a result of* a postmortem (the lesson becomes a
  rule) but the two archetypes are distinct.

# Required fields (beyond core)

- `profile` — must name a profile at `skills/codex/profiles/<name>.yaml`.
  v0.1 value: `adr`.
- `status` — declared by the `adr` profile as required. Enum:
  `proposed` / `accepted` / `superseded` / `deprecated`.

# Optional fields

- `superseded_by` — **required when `status: superseded`.** Cross-ref to
  the newer codex record that replaces this one.
- `supersedes` — list of earlier records (codex or try-failed-exp) this
  decision replaces.
- `refs` — see `# Cross-refs` below.
- `tags` — free-form.

# Required body sections

The `adr` profile requires three body sections (Michael Nygard form):

- `## Context`
- `## Decision`
- `## Consequences`

The validator (`scripts/validate.py`) enforces these via the profile's
`required_sections:` declaration. No archetype-level body heading —
the supersede chain is codex's revisitation mechanism, so no
falsifiability clause is needed.

# Profile slots

- **`adr`** — Michael Nygard-style Architecture Decision Record. Path:
  `./profiles/adr.yaml`. Template: `./templates/adr.md`. Suggested when
  the project has `docs/adr/`, `docs/architecture/`, or `docs/decisions/`
  directories, or the `@nygard/adr-tools` dependency.

Future profiles `rfc`, `design-doc`, `readme-extended` land in v0.3.

# Lifecycle

Write-once body, revisable status. The status enum state machine:

| Status | Meaning |
|--------|---------|
| `proposed` | Decision drafted, not yet ratified. |
| `accepted` | Decision in force. Dominant steady state. |
| `superseded` | Replaced by a newer decision. `superseded_by` must be set. |
| `deprecated` | No longer applies; no successor. |

To revisit a decision:

1. Create a new codex record with `supersedes: ["[[codex:<old-id>]]"]`.
2. In the old record, flip `status: accepted` → `status: superseded`
   and add `superseded_by: "[[codex:<new-id>]]"`.
3. Leave the old body as authored.

Records are never deleted. `lore:audit` (future) enforces this.

# How to write one

1. Generate the ID:

   ‹‹‹bash
   bash scripts/new-id.sh --slug <short-kebab-phrase> --dir .lore/canon/codex
   ‹‹‹

2. Copy the template at `./templates/adr.md` to
   `.lore/canon/codex/<id>.md`, substitute placeholders, write the three
   required sections (Context, Decision, Consequences).

3. In the Decision section, be specific enough that a future reader can
   tell whether their situation matches yours.

4. In Consequences, name the trade-offs explicitly. If rejected alternatives
   deserve their own records, create `try-failed-exp:rejected-adr` entries
   and cite them in `refs:`.

5. Validate:

   ‹‹‹bash
   python3 scripts/validate.py .lore/canon/codex/<id>.md
   ‹‹‹

   Expect `OK:`.

6. Commit.

# Cross-refs

- Outbound `refs`:
  - `[[try-failed-exp:<id>]]` — the rejected alternatives (most common).
  - `[[codex:<id>]]` — earlier decisions this builds on.
  - `[[journal:<id>]]` — if the decision was informed by a specific
    experiment or incident, cite its journal entry.
- `superseded_by`: `[[codex:<id>]]` — when this decision is later overturned.
- `supersedes`: list of records this one replaces; can include both codex
  and try-failed-exp records whose don't-retry-unless clause has been met.
- Inbound:
  - `try-failed-exp` records cite the chosen codex in their
    "What was chosen instead" section.
  - `journal` entries of deploys that execute this decision cite it.
  - `postmortem` may cite a codex when a decision contributed to the incident.

# How to retrieve past decisions

Before proposing an architectural direction X to the user, check the
canon for prior decisions on the same topic:

‹‹‹bash
grep -rli "<topic keywords>" .lore/canon/codex/
‹‹‹

If a matching record exists:

- If `status: accepted`, surface the decision to the user. Don't
  re-propose something already decided. If circumstances suggest
  revisiting, cite the record and make the case for supersession.
- If `status: superseded`, follow the `superseded_by` chain to find
  the current decision.
- If `status: proposed`, the decision is still being weighed —
  contribute to the discussion rather than opening a parallel one.

Never silently re-propose something already in the canon.
```

**Write with REAL triple-backticks in place of `‹‹‹`.**

- [ ] **Step 6.2: Commit**

```bash
git add skills/codex/SKILL.md
git commit -m "feat(codex): archetype SKILL.md with 10-section contract + retrieve-past-decisions section"
```

---

### Task 7: Final verification

Run the full test suite and validate every shipped artifact.

**Files:** verification-only.

- [ ] **Step 7.1: Run full pytest suite**

```bash
source .venv/bin/activate
pytest tests/scripts/test_validate.py -v
```

Expected: 32/32 passing (27 prior + 5 Spec 4).

- [ ] **Step 7.2: Run bats suites (no regressions)**

```bash
bats tests/scripts/test_new-id.bats
bats tests/scripts/test_git-events.bats
bats tests/hooks/test_session-start.bats
```

Expected: 7/7, 5/5, 3/3.

- [ ] **Step 7.3: Validate all shipped artifacts**

```bash
python3 scripts/validate.py skills/codex/examples/2026-03-15-postgres-primary-session-store.md
python3 scripts/validate.py skills/try-failed-exp/examples/2026-03-12-rejected-redis-cluster.md
python3 scripts/validate.py .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md
python3 scripts/validate.py skills/journal/examples/2026-04-15-deploy-v1-3-2.md
python3 scripts/validate.py skills/journal/examples/2026-04-08-payment-api-incident.md
```

Expected: five `OK:` lines.

- [ ] **Step 7.4: Sanity-check invalid codex fixtures**

```bash
for f in tests/fixtures/invalid/2026-04-17-codex-*.md; do
  echo "=== $(basename $f) ==="
  python3 scripts/validate.py "$f" 2>&1 | head -1
done
```

Expected: 4 fixtures, each with targeted error.

- [ ] **Step 7.5: Verify bidirectional cross-ref is complete**

```bash
grep -l "2026-03-15-postgres-primary-session-store" skills/try-failed-exp/examples/
grep -l "2026-03-12-rejected-redis-cluster" skills/codex/examples/
```

Expected: both find their match — the two records cite each other.

- [ ] **Step 7.6: Summary**

Branch `feat/spec-4-codex` should contain (from spec commit `4218aa0`):

- `4218aa0` — docs: Spec 4 design
- 1 commit from Task 1 (profile YAML)
- 1 commit from Task 2 (validator block — 3 TDD tests)
- 1 commit from Task 3 (superseded consistency rule)
- 1 commit from Task 4 (template)
- 1 commit from Task 5 (example + bidirectional dogfood + regression test)
- 1 commit from Task 6 (SKILL.md)

= **7 commits** on top of main. Smallest archetype branch so far.

---

## Self-review

### Spec coverage

| Spec section | Task(s) |
|---|---|
| §1.1 (what the archetype is) | Task 6 (SKILL.md) |
| §1.2 (mirror image with try-failed-exp) | Task 6 (SKILL.md — the table is narrative, not code) |
| §1.3 (boundaries) | Task 6 |
| §1.4 (proactive triggers) | Task 6 |
| §1.5 (inheritance from prior specs) | All validator tasks (Tasks 2, 3) inherit prior helpers |
| §2.1 (SKILL.md structure) | Task 6 |
| §2.2 (frontmatter: profile + status, superseded_by when superseded) | Task 2 (profile required), Task 3 (superseded consistency), adr.yaml (status via apply_profile_fields) |
| §2.3 (body sections: Context/Decision/Consequences) | Task 2 (required_sections mechanism) |
| §2.4 (lifecycle state machine) | Task 6 (SKILL.md) + Task 3 (enforcement of terminal state) |
| §2.5 (cross-ref patterns) | Task 6 (SKILL.md) |
| §2.6 (validator extension, ~20-30 LOC) | Tasks 2 + 3 (combined ~25 LOC) |
| §2.7 (how to retrieve past decisions) | Task 6 (SKILL.md) |
| §3.1 (adr profile YAML) | Task 1 |
| §3.2 (body template) | Task 4 |
| §3.3 (example record — bidirectional dogfood) | Task 5 |
| §3.4 (file layout) | Tasks 1, 4, 5, 6 |
| §3.5 (test plan — 5 tests) | Tasks 2 (3 tests), 3 (1 test), 5 (1 test) |

No gaps. All five test cases from §3.5 land across Tasks 2/3/5.

### Placeholder scan

No "TBD", "TODO", "implement later", "similar to earlier task". Every code step shows complete content.

### Type / name consistency

- `apply_profile_fields`, `load_profile`, `load_body`, `body_has_heading`, `ValidationError` — all Spec 2/3 helpers, reused unchanged. No new signatures.
- The codex block in `validate.py` matches the structural pattern of the try-failed-exp block (also reuses the same helper invocations).
- Fixture filename stems match `id:` fields consistently (Spec 1 Task 6 rule).
- Test function names: `test_codex_<rule>_fails` / `test_codex_example_<slug>_passes` — consistent.

No inconsistencies found.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-17-lore-codex.md`. Two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks.

2. **Inline Execution** — batch execution in this session with checkpoints.

Which approach?
