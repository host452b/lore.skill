# Lore — `journal` Archetype Design

| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Date** | 2026-04-17 |
| **Type** | Spec 3 — second archetype skill (first live-tier) |
| **Scope** | `lore:journal` archetype, v0.1 profile `web-service`, validator extension for journal rules + profile-declared `fields:` mechanism |
| **Author** | host452b |
| **Depends on** | Spec 0 (charter), Spec 1 (core substrate), Spec 2 (try-failed-exp + profile-aware validator) — all on `main` at `5367843` |
| **Defers** | `ml-experiment`, `spike`, `build-log` profiles (v0.3 per charter §5.1) |

---

## 0. Executive summary

`lore:journal` is the first **live-tier** archetype — a chronological stream of discrete events that happened during the project's lifetime: deploys, incidents, experiment runs, CI failures, rollbacks. Individually each record is low-value; in aggregate they are the raw material of the cooling pipeline.

Spec 3 ships:

- `skills/journal/` — the archetype skill: `SKILL.md`, one profile (`web-service`), template, two example records covering the two most common event-types (deploy + incident)
- Extension to `scripts/validate.py`:
  - **A.** A `journal`-specific archetype block: ISO-8601 `event-time`, `outcome` enum, forbidden `superseded_by`/`supersedes` fields (live-tier immutability), reuse of the profile loader from Spec 2
  - **B.** A generalization of the profile mechanism: profile YAML gains a `fields:` block (per charter §3.4) that declares additional frontmatter-level field requirements with type/enum/required constraints. This complements Spec 2's `required_sections:` body grep.
- ~7 new test cases, 6 invalid fixtures, 2 valid fixtures

Scope discipline: v0.1 profile count is **one** (`web-service`), matching Spec 2's precedent. The other three profiles mentioned in the charter (`ml-experiment`, `spike`, `build-log`) land in v0.3 once the archetype mechanism has been validated against a second archetype — that's what this spec accomplishes.

---

## 1. Purpose, immutability, boundaries

### 1.1 What the archetype is

A chronological stream of **discrete events** — deploys, incidents, experiment runs, CI failures, dependency bumps, rollbacks. Each record is:

- Timestamp-bearing (down to the minute at least)
- Factual and verifiable (a reader can check the deploy's commit SHA, the incident's metrics, etc.)
- Short (typically a 2–5 sentence narrative; the frontmatter carries most of the structure)
- Immutable once written (see §1.2)

Individually, journal records are low-value — nobody reads back the specific deploy of `v1.3.2` on 2026-04-15. In aggregate, they are the raw material of the cooling pipeline (charter §1.3): `meta/promote` scans `live/journal/` for recurring patterns and suggests canon entries. `meta/harvest` and `lore:from-git-log` bootstrap journal records from existing git history. Downstream archetypes (`postmortem`, `release-notes`) cite journal entries as their source material.

### 1.2 Immutability — the opposite of canon's write-once

Both canon-tier and live-tier records are "write-once" but the two ideas are distinct:

| | Canon (try-failed-exp) | Live (journal) |
|---|---|---|
| Body stays as authored after writing | ✓ | ✓ |
| Record can be *superseded* by a newer entry | ✓ (via `status: reassessed` + `superseded_by`) | ✗ — events don't un-happen |
| Correct-the-record pattern | Flip status to `reassessed`, add `superseded_by` | Write a NEW record noting the correction; leave the old record untouched |

Concrete validator implication: journal records **must not** have `superseded_by` or `supersedes` frontmatter fields. The validator rejects them with a clear error.

If an event's facts were misrecorded, the fix is to write a new journal record (title: `"Correction to [[journal:<id>]]"`, `refs: [...]` pointing at the incorrect one). The old record stays as written — git history preserves what was believed true at the time, and live-tier auditing depends on the assumption that old records do not mutate.

### 1.3 Boundaries (declared in SKILL.md)

- **Not `codex`.** "We decided to use PostgreSQL" is a decision — codex. Journal records the event of a deploy or migration *landing*; the decision behind it belongs in codex.
- **Not `try-failed-exp`.** "We tried MongoDB and gave up" is a rejection — try-failed-exp. "A MongoDB migration attempt got rolled back" *could* be a journal entry (the event itself is an event), but the rejection conclusion belongs in try-failed-exp.
- **Not `postmortem`.** Journal records "incident detected 14:23, resolved 15:07, session writes failed." Postmortem records the deeper retrospection. Postmortems typically cite several journal entries as their timeline.
- **Not `intent-log`.** Intent-log captures "we plan to do X." Journal captures "X just happened."

### 1.4 Proactive-invocation triggers

Claude should suggest `lore:journal` when the user:

- Mentions a deploy, rollback, release cut, or version bump
- Reports an incident (detection, mitigation, recovery)
- Completes a scheduled experiment or MLflow run
- Triggers a CI build of note (prod release build, migration CI, etc.)
- Mentions a dependency bump worth recording (major-version changes, security patches)

The gatekeeper question: *could I put an ISO timestamp on this?* If yes, it's probably journal. If no (e.g., "we're leaning toward Postgres for the next release"), it's one of the other archetypes.

### 1.5 Key differences from `try-failed-exp`

| | try-failed-exp (Spec 2) | journal (this spec) |
|---|---|---|
| Tier | canon | live |
| Lifecycle | supersede-able | truly immutable |
| Falsifiability anchor | `## Don't retry unless` (body heading) | none — events aren't predictions |
| Required body sections | yes (profile declares via `required_sections`) | none — frontmatter carries structure |
| Profile-declared frontmatter fields | none in v0.1 | yes — `event-type`, `environment` (Spec 3 introduces `fields:` mechanism) |
| Read pattern | individual records cited repeatedly | aggregate consumption by `promote`/`harvest` |

---

## 2. Archetype contract

### 2.1 `SKILL.md` structure

Follows charter §3.3 7-part template, adapted:

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
# When NOT to use me (boundaries)
# Required fields (beyond core)
# Optional fields
# Forbidden fields (immutability)
# Profile slots
# Lifecycle
# How to write one
# Cross-refs
# How the aggregate is consumed
```

The last section replaces try-failed-exp's "How to retrieve past records" — it tells Claude that journal records are typically consumed *en masse* (by `meta/promote`, `meta/harvest`, `lore:from-git-log`) rather than looked up individually.

### 2.2 Archetype-level frontmatter fields

Beyond core (`id`, `type`, `tier`, `date`, `title`, `authors`):

| Field | Required | Type | Notes |
|-------|:-:|------|-------|
| `event-time` | ✓ | ISO 8601 string | Precise to at least the minute: `2026-04-15T16:23:00+00:00` or `2026-04-15T16:23:00Z`. Seconds optional but recommended. More precise than `date`. |
| `outcome` | ✓ | enum | `succeeded` \| `failed` \| `partial` \| `rolled-back` \| `observed`. `observed` covers purely informational events (dependency bump, CI green build) with no pass/fail semantics. |
| `profile` | ✓ | string | v0.1: must be `web-service`. Profile extensions live in `skills/journal/profiles/<name>.yaml`. |

Optional archetype-level fields:

| Field | Type | Notes |
|-------|------|-------|
| `duration` | string | ISO 8601 duration: `PT2M`, `PT45S`, `PT1H30M`. Omit if instantaneous. |
| `commit-sha` | string | Git SHA the event is tied to. Accepts 7-character short or 40-character full. Validator tolerates both. |
| `metrics` | object (free-form) | `{qps_before: 2000, qps_after: 3400}`. Not validated; profiles may constrain shape. |

### 2.3 Forbidden fields

Journal records **reject** these core-schema fields:

- `superseded_by`
- `supersedes`

Validator error: *"journal records are immutable; 'superseded_by'/'supersedes' not permitted on live-tier events."*

`status` is **not** universally forbidden — some future profiles might want an `in-progress` vs `completed` distinction. But for v0.1, no journal profile declares a `status` field.

### 2.4 Lifecycle

Truly immutable. Once committed, the body and frontmatter never change. Corrections are new records, not edits.

This is operationally enforced by a combination of:
1. Validator rule rejecting `superseded_by`/`supersedes` (prevents the canon-style "soft supersede")
2. Author norm documented in SKILL.md
3. `lore:audit` (v0.2) will detect post-commit mutations in `.lore/live/**/*.md` that contradict prior git history

### 2.5 Cross-ref patterns

| Direction | Target | When |
|-----------|--------|------|
| outbound `refs` | `codex` | "This deploy executed decision [[codex:\<id\>]]" |
| outbound `refs` | `try-failed-exp` | "This incident confirmed why [[try-failed-exp:\<id\>]] was right" |
| outbound `refs` | `journal` (same archetype) | Corrections, rollback chains |
| inbound (from postmortem) | — | Postmortems cite 3-10 journal events as their incident timeline |
| inbound (from release-notes) | — | Future release-notes cite journal entries of the deploys they summarize |
| inbound (from promote) | — | `meta/promote` reads aggregate patterns, not single records |

Journal is the most-cited-from, least-citing-out archetype. Events are self-contained facts.

### 2.6 Validator extension A — journal-specific archetype rules

New `if fm.get("type") == "journal":` block in `validate()`. Rules (each is one TDD cycle):

1. **Required `event-time`** + ISO 8601 format check:
   ```python
   EVENT_TIME_RE = re.compile(
       r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2})?([+-]\d{2}:\d{2}|Z)?$"
   )
   ```
   Rejects bare dates (`2026-04-15`), rejects sub-minute (`2026-04-15T16:23:45.123Z`) — we only need minute precision for v0.1.

2. **Required `outcome`** + enum check:
   ```python
   JOURNAL_OUTCOME = frozenset({"succeeded", "failed", "partial", "rolled-back", "observed"})
   ```

3. **Required `profile`** + profile file must resolve (reuses `load_profile` from Spec 2).

4. **Forbidden `superseded_by` / `supersedes`** — if either key in frontmatter, error.

5. Optional: validate `duration` (ISO 8601 duration regex), `commit-sha` (hex, 7-40 chars). These pass silently if absent, error if present and malformed.

Each rule is a separate test case + implementation increment.

### 2.7 Validator extension B — profile-declared `fields:` mechanism

Spec 2 added `required_sections:` to profile YAML (body heading grep). Spec 3 generalizes the profile mechanism to also support `fields:` — frontmatter-level field requirements per charter §3.4.

Profile YAML gains an optional `fields:` dict. Example:

```yaml
fields:
  event-type:
    type: enum
    values: [deploy, incident, rollback, release, migration, ci-failure]
    required: true
  environment:
    type: enum
    values: [prod, staging, dev, test]
    required: true
```

Validator logic:

```python
def apply_profile_fields(profile_data, fm, errors):
    fields_decl = profile_data.get("fields") or {}
    for field_name, field_spec in fields_decl.items():
        if field_spec.get("required") and field_name not in fm:
            errors.append(
                f"profile requires field {field_name!r} (missing from frontmatter)"
            )
            continue
        if field_name not in fm:
            continue  # optional and absent — fine
        value = fm[field_name]
        ftype = field_spec.get("type")
        if ftype == "enum":
            allowed = field_spec.get("values") or []
            if value not in allowed:
                errors.append(
                    f"profile field {field_name!r} must be one of {allowed}; "
                    f"got {value!r}"
                )
        # future types: string, ref — not implemented in v0.1
```

**v0.1 supports `type: enum` only.** Other types from the charter (`string`, `markdown`, `ref`) are deferred:
- `string` — `type` field can be declared, just serves as documentation; no validation
- `markdown` — `required_sections:` already handles this at a simpler level
- `ref` — deferred; cross-ref validation is already done generically by the core validator at the archetype level

When a profile declares an unsupported type, validator silently ignores it (logs nothing — keeps the profile forward-compatible). When a profile declares `type: enum` without a `values:` list, validator errors: *"profile field X declares type: enum but no values list."*

### 2.8 Validator change footprint

Approximate LOC added to `scripts/validate.py`:
- Extension A (journal archetype block): ~35-50 LOC
- Extension B (profile `fields:` mechanism): ~25-40 LOC, factored into its own helper `apply_profile_fields()` so future archetypes' profiles can use it without duplication

Both extensions are independent; each is a separate task in the implementation plan.

---

## 3. `web-service` profile and shipping files

### 3.1 `skills/journal/profiles/web-service.yaml`

```yaml
name: web-service
extends: journal
description: Events from running a web service — deploys, incidents, rollbacks,
  release cuts, migrations, CI failures. Scoped to a deployed environment.

# Profile-declared frontmatter fields (Spec 3's new `fields:` mechanism).
# Added to the archetype's requirements (event-time, outcome, profile).
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

### 3.2 Body template — `skills/journal/templates/web-service.md`

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

### 3.3 Example records

Two ship with the skill, covering the two most common event-types. Both double as valid test fixtures.

#### `skills/journal/examples/2026-04-15-deploy-v1-3-2.md` (deploy event, succeeded)

```markdown
---
id: 2026-04-15-deploy-v1-3-2
type: journal
tier: live
date: 2026-04-15
title: Deploy v1.3.2 to prod
authors: ["host452b"]
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

#### `skills/journal/examples/2026-04-08-payment-api-incident.md` (incident event, partial recovery)

```markdown
---
id: 2026-04-08-payment-api-incident
type: journal
tier: live
date: 2026-04-08
title: Payment API 5xx spike — incident and recovery
authors: ["host452b"]
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

### 3.4 `skills/journal/SKILL.md`

Full text authored in the implementation plan. Required elements:

- Frontmatter: `name`, `description` (trigger-oriented), `type: archetype`, `default-tier: live`, `profiles: [web-service]`
- `# When to use me` — §1.4 triggers
- `# When NOT to use me` — §1.3 boundaries
- `# Required fields (beyond core)` — §2.2 table
- `# Optional fields` — `duration`, `commit-sha`, `metrics`, `refs`, `tags`
- `# Forbidden fields (immutability)` — §2.3
- `# Profile slots` — point at `./profiles/web-service.yaml` and its detect hints
- `# Lifecycle` — §2.4 immutability + correction pattern
- `# How to write one` — `new-id.sh`, pick profile, fill template, `validate.py`, commit
- `# Cross-refs` — §2.5 asymmetry
- `# How the aggregate is consumed` — `meta/promote`, `meta/harvest`, `lore:from-git-log`, downstream archetypes

### 3.5 File layout

```
skills/journal/
├── SKILL.md                                          (new)
├── profiles/
│   └── web-service.yaml                              (new)
├── templates/
│   └── web-service.md                                (new)
└── examples/
    ├── 2026-04-15-deploy-v1-3-2.md                   (new)
    └── 2026-04-08-payment-api-incident.md            (new)

scripts/validate.py                                   (extended: journal block + profile `fields:` helper)

tests/
├── fixtures/
│   ├── valid/
│   │   ├── 2026-04-15-deploy-v1-3-2.md               (new; copy of example)
│   │   └── 2026-04-08-payment-api-incident.md        (new; copy of example)
│   └── invalid/
│       ├── 2026-04-17-journal-missing-event-time.md    (new)
│       ├── 2026-04-17-journal-bad-outcome.md            (new)
│       ├── 2026-04-17-journal-bad-event-time-format.md  (new)
│       ├── 2026-04-17-journal-with-superseded-by.md     (new; forbidden-field rule)
│       ├── 2026-04-17-journal-bad-environment.md        (new; profile field enum)
│       └── 2026-04-17-journal-missing-event-type.md     (new; profile required field)
└── scripts/
    └── test_validate.py                              (extended: ~7 new tests)
```

**Total: 11 new files, 2 extended.**

### 3.6 Test plan

Six invalid fixtures, each tests one rule. Two valid examples act as regression fixtures. Plus a full-suite guard that Spec 1 + Spec 2 tests continue to pass.

| Test | Asserts |
|------|---------|
| `test_journal_missing_event_time_fails` | missing event-time → error mentioning "event-time" |
| `test_journal_bad_outcome_fails` | outcome=`maybe` → error mentioning "outcome" |
| `test_journal_bad_event_time_format_fails` | event-time=`2026-04-17` (date only) → error mentioning "event-time" or "ISO" |
| `test_journal_with_superseded_by_fails` | superseded_by set → error mentioning "immutable" or "superseded_by" |
| `test_journal_bad_environment_fails` | environment=`production` (not in enum) → error mentioning "environment" |
| `test_journal_missing_event_type_fails` | no event-type → error mentioning "event-type" |
| `test_journal_deploy_example_passes` | `.../2026-04-15-deploy-v1-3-2.md` → OK |
| `test_journal_incident_example_passes` | `.../2026-04-08-payment-api-incident.md` → OK |
| Full suite (Spec 1 + Spec 2) | All 18 pre-existing pytest tests still pass |

Total after Spec 3: 18 + 8 = **26 pytest tests**, plus Spec 1's 15 bats tests (unchanged) = 41/41.

---

## 4. Success criteria

- A user writes a `journal:web-service` record, runs `scripts/validate.py`, gets `OK:` within 2 minutes.
- All six invalid fixtures fail with exit code 1 and a targeted error message naming the violated rule.
- The two example records validate clean and are cited as the canonical examples in `SKILL.md`.
- Spec 1 + Spec 2 regression tests all continue to pass (the existing try-failed-exp dogfood record still validates under the extended `validate.py`).
- Claude, given a deploy + post-deploy metrics, can proactively suggest `lore:journal:web-service` and produce a draft record matching the template.

## 5. Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| Journal records get edited in place (violating immutability), especially via the easy path of "fix the title". | SKILL.md explicitly prescribes the correction pattern. `lore:audit` (v0.2) adds a git-history check for post-commit mutation on `live/**/*.md`. For v0.1 we rely on author discipline + the documented rule. |
| `event-time` regex is too strict for valid ISO 8601 forms (e.g., fractional seconds, Z vs +00:00). | Current regex covers the common cases (minute or second precision, Z or ±HH:MM). Documented as a pragmatic v0.1 subset; tightenable in a minor release without breaking existing records. |
| Profile `fields:` mechanism becomes too powerful (turns into a programming language). | v0.1 supports only `type: enum`. Other types (`string`, `ref`, `markdown`) are deferred until a real archetype needs them. Complex validation logic remains in code, not YAML. |
| Journal volume explodes `.lore/live/journal/` (hundreds of records per project per quarter). | `.lore/` is git-tracked; `git log` scales fine. Future: `meta/promote` archives records older than N days after the canon they informed has been written. Not a v0.1 problem. |
| Users put decisions, rejections, or postmortems in journal because it's the "catch-all." | Strong `# When NOT to use me` section in SKILL.md + `audit` flag (future) when a journal body reads like a codex/postmortem (heuristic: headings like `## Decision`, `## Timeline`). |

## 6. Out of scope (deferred)

- `ml-experiment`, `spike`, `build-log` profiles — v0.3.
- `fields: ref` validation (cross-ref target-archetype constraints) — v0.2.
- Profile inheritance / composition (one profile extending another) — YAGNI.
- Automatic event detection from git hooks, CI webhooks, etc. — handled by `meta/harvest` + `lore:from-git-log` (Specs 5 & 6).
- Post-commit mutation detection — `lore:audit`, v0.2.
- Sub-minute `event-time` precision — not needed for v0.1; regex can tighten later.
- Journal-specific search/indexing — handled by grep over `.lore/live/journal/` for v0.1.

---

## Appendix — Implementation notes for the plan author

- **TDD order:** extension A first (five rules as five small TDD cycles), then extension B (the `fields:` helper) with its own TDD cycles, then the skill files (profile YAML, template, SKILL.md, examples) with validator confirming the examples pass.
- **Refactor opportunity**: extension B's `apply_profile_fields` helper can also be called from the existing try-failed-exp block in `validate()` — if `rejected-adr.yaml` ever adds a `fields:` section, it'll work automatically. Don't proactively refactor try-failed-exp to use it in this spec; just make the helper archetype-agnostic.
- **Profile YAML forward-compat:** when the validator encounters an unknown `fields[].type` value (e.g., `type: ref`), log nothing and skip. This keeps profile YAML forward-compatible with future types.
- **Example fixture ID format note:** `2026-04-15-deploy-v1-3-2` is chosen deliberately — the dots in `v1.3.2` violate the slug regex (`[a-z0-9][a-z0-9-]{1,60}`), so dots are replaced with hyphens. This is a real-world authoring gotcha worth documenting in the SKILL.md's "How to write one" section.
- **Don't introduce parallel machinery for live-tier immutability** — the `superseded_by`/`supersedes` rejection is sufficient for v0.1. Leave post-commit-mutation detection to `lore:audit`.
- **Keep `SKILL.md` under ~200 lines.** The 10-section structure is generous; prose in each section should be tight.
