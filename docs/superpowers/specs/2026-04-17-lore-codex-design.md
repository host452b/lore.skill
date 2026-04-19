# Lore — `codex` Archetype Design

| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Date** | 2026-04-17 |
| **Type** | Spec 4 — third archetype skill (second canon-tier) |
| **Scope** | `lore:codex` archetype, v0.1 profile `adr`, validator extension for codex archetype rules (no new profile mechanism needed — reuses Spec 2 `required_sections` + Spec 3 `apply_profile_fields`) |
| **Author** | host452b |
| **Depends on** | Spec 0 (charter), Specs 1–3 all on `main` at `5cb83bf` |
| **Defers** | `rfc`, `design-doc`, `readme-extended` profiles (v0.3 per charter §5.1) |

---

## 0. Executive summary

`lore:codex` is the canon-tier home for project **decisions** — Architecture Decision Records, design choices, adopted direction. It is the positive-polarity sibling of `try-failed-exp`:

```
codex           → "do this, and here's why"
try-failed-exp  → "don't do this, and here's why — unless <condition>"
```

Both canon-tier, both supersede-able, both repeatedly cited. Codex is the conventional ADR canon; try-failed-exp is reverse-canon. A single architectural choice typically produces *both* — one codex for the adopted option, one try-failed-exp for each rejected alternative, with bidirectional cross-refs.

Spec 4 ships:

- `skills/codex/` — the archetype skill: `SKILL.md`, one profile (`adr`), template, one example record that completes an existing bidirectional dogfood pair
- Extension to `scripts/validate.py`: a `codex`-specific archetype block (~20-30 LOC) enforcing `profile` + `status` requirements and a `status: superseded → superseded_by required` consistency rule
- 5 new test cases (4 invalid fixtures + 1 valid regression)

**Smallest footprint of any archetype spec so far.** The profile mechanism was generalized to this point across Specs 2 (`required_sections`) and 3 (`apply_profile_fields`). Codex's `adr.yaml` is the **first profile to exercise both mechanisms simultaneously**, validating their compositional design.

v0.1 profile count: **one** (`adr`), matching Specs 2 and 3 precedent. `rfc`, `design-doc`, `readme-extended` (all mentioned in the charter) land in v0.3.

---

## 1. Purpose, identity, boundaries

### 1.1 What the archetype is

A canon-tier record of a project decision — architectural choice, library selection, design direction, policy, convention. Each record is:

- A positive-polarity statement: the adopted direction, not the considered alternatives
- Revisable via the supersede chain (a later codex can supersede an earlier one when the decision evolves)
- Repeatedly cited — by journal (the deploy executing the decision), by try-failed-exp (the rejected alternatives), by postmortem (the decision that led to the incident)
- Structured in the classical Michael Nygard ADR form: Context, Decision, Consequences

### 1.2 Mirror-image relationship with `try-failed-exp`

The two canon-tier archetypes are designed as mirror images:

| | codex (Spec 4) | try-failed-exp (Spec 2) |
|---|---|---|
| Polarity | positive: *"do this"* | reverse: *"don't do this"* |
| Status enum | proposed / accepted / superseded / deprecated | rejected / on-hold / reassessed |
| Supersede trigger | a later decision overturns | a rejection is overturned |
| Body anchor | Nygard: Context/Decision/Consequences | Nygard-mirror: What was considered / Why rejected / What was chosen instead + archetype-level `## Don't retry unless` |
| Falsifiability | — (the supersede chain is the mechanism) | `## Don't retry unless` clause |
| Typical cross-refs | → try-failed-exp (rejected alternatives), ← journal (deploys) | → codex (what was chosen), ← codex (earlier codex now lists this as a formally rejected option) |

A decision that went "we chose A, rejected B and C" produces one codex (A) + one or more try-failed-exp records (B, C), cross-linked in both directions.

### 1.3 Boundaries (declared in SKILL.md)

- **Not `journal`.** Journal records the *event* of a deploy or migration; codex records the *decision* behind it.
- **Not `try-failed-exp`.** Codex is what was adopted; try-failed-exp is what was rejected.
- **Not `intent-log`.** Intent-log captures "we plan to do X"; codex captures a decision that has been made.
- **Not `postmortem`.** Postmortem is retrospection on an incident; a codex entry may be created *as a result of* a postmortem (the lesson becomes a rule) but the two archetypes are distinct.

### 1.4 Proactive-invocation triggers

Claude should suggest `lore:codex` when the user:

- Says "we decided to use X", "we chose Y over Z", "our convention is W"
- Completes a design review or architecture discussion
- Finalizes a technical direction or policy
- Asks "why did we choose X?" (surfaces existing codex records)
- Finishes writing an ADR in any format (convert to `lore:codex:adr`)

### 1.5 Inheritance from prior specs

Codex is the cleanest expression of patterns already established:

- **Supersede-able canon lifecycle** (Spec 2's try-failed-exp pattern): write-once body, flip status + set `superseded_by` when overturned
- **Profile-declared required body sections** (Spec 2's `required_sections` mechanism): profile YAML lists the `## ` headings the body must contain
- **Profile-declared frontmatter fields** (Spec 3's `apply_profile_fields` + `fields:` block): profile YAML declares enum constraints
- **Same filename=id, same cross-ref grammar, same core substrate**

Virtually no new mechanism. Codex's validator block is the smallest archetype-specific addition in the suite so far.

---

## 2. Archetype contract

### 2.1 `SKILL.md` structure

Follows charter §3.3 7-part template, adapted:

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
# When NOT to use me (boundaries)
# Required fields (beyond core)
# Optional fields
# Required body sections
# Profile slots
# Lifecycle
# How to write one
# Cross-refs
# How to retrieve past decisions
```

The last section is analogous to try-failed-exp's "How to retrieve past records" — tells Claude to grep `.lore/canon/codex/` before proposing approaches that might already be decided.

### 2.2 Archetype-level frontmatter fields

Beyond core (`id`, `type`, `tier`, `date`, `title`, `authors`):

| Field | Required | Declared where | Notes |
|-------|:-:|---|-------|
| `profile` | ✓ | archetype (validator) | v0.1: must be `adr`. |
| `status` | ✓ | **profile `fields:` block** | Enum: `proposed` / `accepted` / `superseded` / `deprecated`. Validated by `apply_profile_fields` (Spec 3). |

Optional archetype-level fields:

| Field | Type | Notes |
|-------|------|-------|
| `superseded_by` | cross-ref | **Required when `status: superseded`.** Cross-ref to the newer codex record (usually another codex) that replaces this one. |
| `supersedes` | list\<cross-ref\> | List of earlier codex records this one replaces. |
| `refs` | list\<cross-ref\> | See §2.5 for cross-ref patterns. |
| `tags` | list\<string\> | Free-form. |

No codex-specific forbidden fields. (Unlike journal, codex is not immutable — supersession is the whole point.)

### 2.3 Required body sections

The `adr` profile declares three required body sections via `required_sections:` (the mechanism from Spec 2):

- `## Context`
- `## Decision`
- `## Consequences`

**No archetype-level required heading** (unlike try-failed-exp's `## Don't retry unless`). Codex doesn't need a falsifiability clause — the supersede chain is the mechanism by which decisions are revisited. Stay minimal, match the canonical Nygard form.

Future profiles may declare additional body sections (e.g., `rfc.yaml` might require `## Alternatives` or `## Open Questions`). The archetype itself enforces none.

### 2.4 Lifecycle

Write-once body, revisable status. The pattern mirrors try-failed-exp:

| Status | Meaning | Transitions |
|--------|---------|-------------|
| `proposed` | Decision drafted, not yet ratified. | May transition to `accepted` or (rarely) directly to `superseded` / `deprecated`. |
| `accepted` | Decision is in force. Dominant steady state. | May transition to `superseded` (replaced by a newer decision) or `deprecated` (no longer applies, no replacement). |
| `superseded` | Replaced by a newer decision. | Terminal. `superseded_by` must be set. |
| `deprecated` | No longer applies; no successor. | Terminal. `superseded_by` may be empty. |

**Write-once principle:** the body stays as authored. Revisiting a decision means a new codex entry with `supersedes: [...]` pointing back, and flipping the old entry's `status: accepted` → `status: superseded` + `superseded_by: [[codex:<new-id>]]`. The old body is **not rewritten**.

### 2.5 Cross-ref patterns

| Direction | Target | When |
|-----------|--------|------|
| outbound `refs` | `try-failed-exp` | "We chose A; rejected alternatives: [[try-failed-exp:B]], [[try-failed-exp:C]]." |
| outbound `refs` | `codex` | "This decision builds on [[codex:<earlier>]]." |
| outbound `refs` | `journal` | Rare — if the decision was informed by a specific experiment or incident, cite its journal entry. |
| `superseded_by` | `codex` | Usually another codex. Newer decision overturning this one. |
| `supersedes` | `codex` \| `try-failed-exp` | The records this decision replaces. Can include try-failed-exp records whose "Don't retry unless" clause has been met. |
| inbound (from try-failed-exp) | — | try-failed-exp's "What was chosen instead" section should cite this record. |
| inbound (from journal) | — | Journal entries of deploys that execute this decision should cite it. |
| inbound (from postmortem) | — | Postmortems may cite a codex when a decision contributed to the incident. |

**Bidirectional dogfood invariant:** the v0.1 ships one codex example that completes an existing cross-ref pair (§5.1 below).

### 2.6 Validator extension (scripts/validate.py)

Smallest of any archetype so far. A new `codex`-specific block in `validate()`:

1. **Required `profile`** — same pattern as try-failed-exp/journal.
2. **Profile must resolve** via existing `load_profile()`.
3. **`apply_profile_fields`** invocation (Spec 3 helper) — handles `status` required + enum from the `adr.yaml` profile. **No new code.**
4. **`required_sections`** body grep (Spec 2 mechanism) — handles Context/Decision/Consequences headings. **No new code.**
5. **`status: superseded` consistency rule** — if status is `superseded`, `superseded_by` must be present. ~3 LOC, parallel to journal's `reassessed` rule and try-failed-exp's `reassessed` rule.

**Total new code in `validate.py`: ~20-30 LOC** (mostly the `if fm.get("type") == "codex":` block scaffolding + the consistency rule).

### 2.7 How to retrieve past decisions

This section in SKILL.md instructs Claude to proactively consult `.lore/canon/codex/` before discussing architecturally significant topics:

```markdown
# How to retrieve past decisions

Before proposing an architectural direction X to the user, check the
canon for prior decisions on the same topic:

    grep -rli "<topic keywords>" .lore/canon/codex/

If a matching record exists:
- If `status: accepted`, surface the decision to the user. Don't re-propose
  something already decided. If circumstances suggest revisiting, cite the
  record and make the case for supersession.
- If `status: superseded`, follow the `superseded_by` chain to find the
  current decision.
- If `status: proposed`, the decision is still being weighed — contribute
  to the discussion rather than opening a parallel one.

Never silently re-propose something already in the canon.
```

---

## 3. `adr` profile and shipping files

### 3.1 `skills/codex/profiles/adr.yaml`

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

**First profile to declare both `fields:` and `required_sections:` in the same YAML.** This validates that the two mechanisms compose cleanly.

### 3.2 `skills/codex/templates/adr.md`

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

### 3.3 Example record — completing the dogfood cross-ref pair

The existing try-failed-exp example `2026-03-12-rejected-redis-cluster` already has `refs: ["[[codex:2026-03-15-postgres-primary-session-store]]"]`. That codex record doesn't exist yet. This spec ships it.

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

**Dogfood note:** after this record lands, the bidirectional cross-ref pair is complete. `lore:link` (v0.2 future) can enforce that every codex `refs:` entry to a try-failed-exp has a corresponding `refs:` entry back — this example is the canonical illustration.

### 3.4 File layout

```
skills/codex/
├── SKILL.md                                        (new, ~130 lines)
├── profiles/adr.yaml                               (new)
├── templates/adr.md                                (new)
└── examples/
    └── 2026-03-15-postgres-primary-session-store.md  (new — completes existing cross-ref pair)

scripts/validate.py                                 (extended: codex block ~20-30 LOC)

tests/
├── fixtures/
│   ├── valid/
│   │   └── 2026-03-15-postgres-primary-session-store.md   (copy of example)
│   └── invalid/
│       ├── 2026-04-17-codex-missing-status.md
│       ├── 2026-04-17-codex-bad-status.md
│       ├── 2026-04-17-codex-missing-decision.md
│       └── 2026-04-17-codex-superseded-without-superseded-by.md
└── scripts/
    └── test_validate.py                            (extended: ~5 new tests)
```

**Total: 9 new files, 2 extended.** Smaller than both Spec 2 (8+2) and Spec 3 (11+2) — reaping the benefit of the profile mechanism's maturity.

### 3.5 Test plan

Four invalid fixtures + one valid regression + one bidirectional-pair regression:

| Test | Asserts |
|------|---------|
| `test_codex_missing_status_fails` | no `status` field → error mentions "status" |
| `test_codex_bad_status_fails` | `status: draft` (not in adr enum) → error mentions "status" |
| `test_codex_missing_decision_fails` | no `## Decision` body heading → error mentions "Decision" |
| `test_codex_superseded_without_superseded_by_fails` | status=`superseded` but no `superseded_by` → error mentions "superseded" |
| `test_codex_example_postgres_primary_passes` | `.../2026-03-15-postgres-primary-session-store.md` validates OK |
| Full suite (Specs 1+2+3 regressions) | All 27 pre-existing pytest tests still pass |

Total after Spec 4: 27 + 5 = **32 pytest tests**, plus Spec 1's 15 bats tests (unchanged) = 47/47.

---

## 4. Success criteria

- An engineer writes a codex:adr record, runs `scripts/validate.py`, gets `OK:` in under 2 minutes using only the template.
- All 4 invalid fixtures fail with targeted error messages naming the violated rule.
- The existing `try-failed-exp:2026-03-12-rejected-redis-cluster` record and the new codex record form a bidirectional pair both validating clean.
- Specs 1+2+3 test suites continue to pass unchanged.
- Claude, asked about a past decision, grep's `.lore/canon/codex/` before offering advice (behavior from §2.7).

## 5. Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| Users write codex when they should write try-failed-exp (or vice versa). | Strong boundary section in SKILL.md + the mirror-image design. A record that says "we didn't do X" is try-failed-exp; "we did X" is codex. |
| Decisions get stale without anyone updating status. | v0.1: rely on author discipline. v0.2: `meta/audit` can flag `accepted` codex records older than N months with no recent `refs:` activity. |
| Supersede chains become tangled (A supersedes B, B supersedes C, C supersedes A). | `lore:audit` (future) detects cycles. For v0.1, not a realistic concern given manual authoring. |
| Profile declares both `fields:` and `required_sections:` — does validator apply them in the right order? | Order doesn't matter: both are additive error lists. Full test suite exercises the combination. |

## 6. Out of scope (deferred)

- `rfc`, `design-doc`, `readme-extended` profiles — v0.3.
- `meta/link` bidirectional cross-ref validation — v0.2.
- Supersede-chain cycle detection — v0.2 (`audit`).
- Stale-decision flagging — v0.2.
- ADR numbering conventions (some teams use sequential integers; lore sticks with date-slug IDs).

---

## Appendix — Implementation notes for the plan author

- **Smallest validator extension in the suite.** No new mechanism — just a scaffolded `codex` block reusing `apply_profile_fields`, `load_profile`, and `body_has_heading` from prior specs.
- **TDD order:** scaffolding (profile YAML) → validator block (4 TDD cycles, one per invalid fixture) → template → example record → SKILL.md → final verification. ~8 tasks total.
- **Bidirectional dogfood commitment:** the example record has `refs` pointing at an existing try-failed-exp record. No backfill of the try-failed-exp record needed — its `refs` already points at this codex's id.
- **Watch for PyYAML gotcha carryover:** no ISO timestamps in codex frontmatter (unlike journal), so the datetime auto-coercion issue from Spec 3 doesn't apply. `status` is a plain enum string.
- **Example filename:** `2026-03-15-postgres-primary-session-store.md` — must match the `id:` value exactly (Spec 1 Task 6 rule).
- **Keep SKILL.md under ~200 lines.** Established pattern.
