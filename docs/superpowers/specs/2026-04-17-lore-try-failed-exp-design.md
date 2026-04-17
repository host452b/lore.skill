# Lore — `try-failed-exp` Archetype Design

| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Date** | 2026-04-17 |
| **Type** | Spec 2 — first archetype skill |
| **Scope** | `lore:try-failed-exp` archetype, v0.1 profile `rejected-adr`, validator profile-awareness extension |
| **Author** | host452b \<\> |
| **Depends on** | Spec 0 (charter) and Spec 1 (core substrate + install), both merged to `main` at `e446e06` |
| **Defers** | `spike-outcome`, `library-eval`, `perf-dead-end` profiles (v0.3 per charter §5.1) |

---

## 0. Executive summary

`lore:try-failed-exp` is the headline archetype of the lore suite — the canon-tier record of **attempts that were considered and rejected**. It is the mirror image of `codex`: where `codex` says *"do this, and here's why,"* `try-failed-exp` says *"don't do this, and here's why — unless \<specific falsifiable condition\>."* The falsifiability anchor is what keeps rejection records from ossifying into permanent prohibitions.

Spec 2 ships:

- `skills/try-failed-exp/` — the archetype skill: `SKILL.md`, one profile (`rejected-adr`), template, example record
- An extension to `scripts/validate.py` making it profile-aware: loads profile YAML, merges its `required_sections` / `fields` into the schema, greps markdown bodies for required headings
- ~6 new test cases + 4-5 new fixtures
- No changes to install infrastructure, hooks, or the core substrate

v0.1 profile scope is **intentionally one** (`rejected-adr`). The other three profiles mentioned in the charter (`spike-outcome`, `library-eval`, `perf-dead-end`) land in v0.3 once the profile mechanism has been validated against a real second archetype.

---

## 1. Purpose, thesis, and boundaries

### 1.1 What the archetype is

A canon-tier archetype for recording options that were **considered and not adopted** — libraries evaluated but not picked, architectural approaches rejected, optimizations attempted that didn't pay off, spikes that reached a "no-go" conclusion.

Structurally, it mirrors `codex`:

```
codex           → "do this, and here's why"
try-failed-exp  → "don't do this, and here's why — unless <condition>"
```

Both are canon tier. Both are re-read and revisable. Both accumulate as a project's long-term memory. The relationship between them is bidirectional: a `codex` entry naturally cites the rejected alternatives; a `try-failed-exp` entry cites the chosen path.

### 1.2 Differentiation — the falsifiability anchor

The common failure mode of rejection records in other tools is decay. "We tried X, didn't work" gets written, then years later nobody remembers the constraints that drove it; the record becomes either ignored or mistaken for a permanent prohibition. Engineers re-try X and discover a change in circumstance — but the record never told them to look.

`try-failed-exp` solves this with one required body section: **`## Don't retry unless`** — a short list of specific, falsifiable conditions that would justify revisiting. Example: *"unless Redis ships native cross-slot transactions in a GA release"* or *"unless event volume exceeds 50k writes/sec."*

This turns a fuzzy "don't do X" into a check: when reality changes, the record itself signals that re-evaluation is appropriate. The `## Don't retry unless` heading is enforced by the validator at the archetype level (every `try-failed-exp` record, every profile).

### 1.3 Boundaries (declared in SKILL.md)

- **Not `postmortem`** — postmortems record what happened during an incident. Try-failed-exp records an *intentional exploration or evaluation* that concluded in rejection.
- **Not a bug tracker** — specific bugs belong in GitHub Issues / Jira / Linear. Try-failed-exp records direction-level conclusions.
- **Not `intent-log`** — intent-log (future) captures "we plan to do X." Try-failed-exp captures "we considered X and are not doing it."
- **Not `journal`** — deploys, experiments, CI events are journal. "We tried the Redis cluster approach and are not adopting it" is try-failed-exp.

These boundaries live in the `# When NOT to use me` section of the SKILL.md and are the primary mechanism preventing the suite from degenerating into a grab-bag.

### 1.4 Proactive-invocation triggers

Claude should suggest `lore:try-failed-exp` when the user:

- Says "we tried X and gave up" / "we rejected Y" / "we evaluated Z but went with something else"
- Completes a spike / proof-of-concept whose conclusion is "don't pursue"
- Evaluates a third-party library and decides against it (v0.3 `library-eval` profile covers this more precisely; in v0.1 this fits under generic `rejected-adr`)
- Attempts a performance optimization that produces no measurable benefit
- Works through a "considered A, B, C — chose A — here's why B and C were rejected" reasoning

These triggers are listed in SKILL.md's `# How to write one` preamble so the model knows when to engage.

---

## 2. Archetype contract

### 2.1 `SKILL.md` structure

Follows the 7-part template from charter §3.3, specialized for try-failed-exp:

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
# When NOT to use me (boundaries)
# Required fields (beyond core)
# Optional fields
# Required body sections
# Profile slots
# Lifecycle
# How to write one
# Cross-refs
# How to retrieve past records
```

The last section (`# How to retrieve past records`) is specific to this archetype and is where the suite's value compounds — see §2.6.

### 2.2 Archetype-level frontmatter requirements

Beyond the core fields (`id`, `type`, `tier`, `date`, `title`, `authors`):

| Field | Required | Type | Notes |
|-------|:-:|------|-------|
| `profile` | ✓ | string | v0.1: must be `rejected-adr`. Profile must exist at `skills/try-failed-exp/profiles/<profile>.yaml`. |
| `status` | ✓ | enum | `rejected` \| `on-hold` \| `reassessed`. See §2.4 for state semantics. |

Optional:

| Field | Type | Notes |
|-------|------|-------|
| `superseded_by` | cross-ref | Required when `status == reassessed`. Points at the new canon entry (usually a `codex`) that overturned this rejection. |
| `supersedes` | list\<cross-ref\> | Usually empty. Used when one record consolidates several earlier rejections. |
| `tags`, `refs` | — | Core-schema fields; see §2.5 for cross-ref patterns. |

### 2.3 Archetype-level body requirement

Every try-failed-exp record, regardless of profile, **must** contain a `## Don't retry unless` heading followed by at least one line of content. Validator enforces this with a regex: `^## Don't retry unless\s*$` followed by at least one non-blank non-heading line.

Other body sections come from the profile (§3.1).

### 2.4 Lifecycle

| Status | Meaning | Expected transitions |
|--------|---------|---------------------|
| `rejected` | The approach was considered and ruled out. The dominant steady state. | May transition to `reassessed` if the don't-retry-unless condition triggers. |
| `on-hold` | "Not right now, maybe later." Used when the idea has merit but the moment is wrong. | May transition to `reassessed` (adopted) or stay `on-hold` indefinitely. |
| `reassessed` | The don't-retry-unless condition has been met or the decision was overturned. Record is effectively superseded. | Terminal. `superseded_by` must point at the superseding record. |

**Write-once principle:** the body of a record stays as authored. Revisiting a rejection creates a new record (usually a `codex` entry) and flips the old record's `status` to `reassessed` with `superseded_by` set. The body is **not rewritten** — the archaeological trail of "what blocked it originally, what changed" is the whole point.

**Never deleted.** The `audit` meta-skill (v0.2+) enforces that no `try-failed-exp` record is removed; it may only be superseded. This preserves institutional memory against well-meaning cleanups.

### 2.5 Cross-ref patterns

Typical cross-refs for a `try-failed-exp` record:

| Direction | Target archetype | When |
|-----------|-----------------|------|
| outbound `refs` | `codex` | Almost always — "what was chosen instead" cites the codex entry |
| outbound `refs` | `journal` | If the rejection was driven by a specific spike or experiment result |
| outbound `refs` | `postmortem` | If an incident proved the approach unworkable |
| inbound (from codex) | — | A codex entry should cite the rejected alternatives in its own `refs` |
| `superseded_by` | `codex` | When the rejection is overturned by a later decision |

`meta/link` (v0.2) will enforce bidirectional consistency: if a codex cites a try-failed-exp, the reverse reference should also exist.

### 2.6 How to retrieve past records (the skill's compounding value)

This section in SKILL.md instructs Claude to **proactively consult** `.lore/canon/try-failed-exp/` before proposing significant approaches:

```markdown
# How to retrieve past records

Before proposing approach X to the user, grep the canon for it:

    grep -rli "<approach keywords>" .lore/canon/try-failed-exp/

If a matching record exists, read it and its `## Don't retry unless` clause.
Decide:
- Conditions unchanged → surface the prior rejection to the user rather 
  than re-proposing X from scratch.
- Conditions changed (met the clause) → cite the record, explain what 
  changed, propose re-evaluation.

Never silently re-propose something the project has already rejected.
```

This is the operational payoff of the archetype — each record pays compound interest by preventing future re-tries. It's also what justifies calling the skill canon tier: records aren't written to be archived, they're written to be consulted.

### 2.7 Validator extension (scripts/validate.py)

Spec 1's validator checks only the core schema. Spec 2 extends it to be profile-aware. New behavior (roughly 60-80 lines added):

1. **Profile loader.** When a record has `profile: <name>` and `type: try-failed-exp`, load `skills/try-failed-exp/profiles/<name>.yaml`. Parse with PyYAML.

2. **Profile schema merge.** The profile YAML declares `required_sections: [...]` and optionally `fields: {...}` per charter §3.4. Merge these into the validation pass.

3. **Body section grep.** For each entry in `required_sections`, the validator reads the record's body (everything after the closing `---` frontmatter delimiter) and confirms a matching `^## <heading>\s*$` line exists. Failure → error like `"missing required section: ## What was considered"`.

4. **Archetype-level `## Don't retry unless` check.** Hard-coded for type `try-failed-exp` (not profile-specific). All four future profiles inherit this.

5. **`status` / `superseded_by` consistency.** If `status == reassessed`, `superseded_by` must be set and be a valid cross-ref. Error otherwise.

6. **Unknown profile error.** If `profile:` names a file that doesn't exist under `skills/<archetype>/profiles/`, error clearly (don't silently skip profile-level checks).

**Validator CLI unchanged.** `python3 scripts/validate.py <record>` stays the same interface; the profile-aware behavior triggers transparently when `type == try-failed-exp` (extension to other archetypes happens in their own specs).

---

## 3. `rejected-adr` profile and shipping files

### 3.1 `skills/try-failed-exp/profiles/rejected-adr.yaml`

```yaml
name: rejected-adr
extends: try-failed-exp
description: ADR-style record of an option considered but not adopted. Lists
  what was on the table, why it was ruled out, what was chosen instead, and
  the condition that would justify revisiting.

# Body sections the validator enforces (as `## ` headings).
# "## Don't retry unless" is required at the archetype level for every
# try-failed-exp record regardless of profile — not repeated here.
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

No profile-specific frontmatter fields in v0.1. The `fields:` block from charter §3.4 remains available for later profiles (e.g., `library-eval` may want `library_name`, `version_evaluated`) but isn't needed for `rejected-adr`.

### 3.2 `skills/try-failed-exp/templates/rejected-adr.md`

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

### 3.3 `skills/try-failed-exp/examples/rejected-redis-cluster.md`

A fully-filled example record, committed alongside SKILL.md. Doubles as a fixture for validator tests (copied into `tests/fixtures/valid/`).

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

### 3.4 `skills/try-failed-exp/SKILL.md`

Full content — follows the 7-part template from charter §3.3 plus the archetype-specific `# How to retrieve past records` section.

The full text is authored during the implementation plan and is long enough to belong there rather than duplicated here. Required elements (checklist for implementation):

- Frontmatter: `name`, `description` (trigger-oriented), `type: archetype`, `default-tier: canon`, `profiles: [rejected-adr]`
- `# When to use me` — the four trigger situations from §1.4
- `# When NOT to use me` — the boundaries from §1.3 (vs postmortem, bug tracker, intent-log, journal)
- `# Required fields (beyond core)` — `profile`, `status` per §2.2
- `# Optional fields` — `superseded_by`, `supersedes`, `refs`, `tags`
- `# Required body sections` — `## Don't retry unless` (archetype level) + profile-declared sections
- `# Profile slots` — point at `./profiles/rejected-adr.yaml`, mention detect hints
- `# Lifecycle` — write-once, three-status state machine, never-deleted
- `# How to write one` — the step sequence: `new-id.sh`, pick profile, fill template, save under `.lore/canon/try-failed-exp/`, run `validate.py`
- `# Cross-refs` — expected ref targets per §2.5
- `# How to retrieve past records` — the grep-before-proposing instruction from §2.6

### 3.5 File layout shipped by Spec 2

```
skills/try-failed-exp/
├── SKILL.md                                   (new)
├── profiles/
│   └── rejected-adr.yaml                      (new)
├── templates/
│   └── rejected-adr.md                        (new)
└── examples/
    └── 2026-03-12-rejected-redis-cluster.md   (new)

scripts/validate.py                            (extended: +profile loader, body grep, status/superseded_by consistency)

tests/
├── fixtures/
│   ├── valid/
│   │   └── 2026-03-12-rejected-redis-cluster.md   (new; copy of the example)
│   └── invalid/
│       ├── tfe-missing-dont-retry-unless.md       (new)
│       ├── tfe-missing-what-was-chosen-instead.md (new)
│       ├── tfe-reassessed-without-superseded-by.md (new)
│       └── tfe-unknown-profile.md                 (new)
└── scripts/
    └── test_validate.py                           (extended: +5 test cases)
```

**Total:** 8 new files, 2 files extended (`scripts/validate.py`, `tests/scripts/test_validate.py`). Approximately half the Spec 1 footprint.

### 3.6 Reconciliation with existing dogfood record

`.lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md` was written in Spec 1 without the formal archetype in place. Under the new validator:

| Required | Dogfood has it? |
|----------|:-:|
| `profile: rejected-adr` | ✓ |
| `status: rejected` | ✓ |
| `## What was considered` | ✓ |
| `## Why it was rejected` | ✓ (as "Why it was rejected") |
| `## What was chosen instead` | ✓ |
| `## Don't retry unless` | ✓ |

**No backfill commit needed.** The record already conforms to the profile. Spec 2's validator should pass it as-is; a test case should confirm this to prevent regression (retroactive compatibility is one of the charter's design properties).

---

## 4. Success criteria

- `python3 scripts/validate.py skills/try-failed-exp/examples/2026-03-12-rejected-redis-cluster.md` — `OK: ...`, exit 0.
- `python3 scripts/validate.py .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md` — `OK: ...` (existing dogfood still passes).
- Five invalid fixtures each fail with exit 1 and a clear error message naming the missing element.
- All Spec 1 tests continue to pass unchanged (10 pytest + 15 bats).
- An engineer can go from `new-id.sh` → fill template → validator `OK` → commit in under 2 minutes.
- Claude, when prompted with "let's use Redis Cluster for sessions," spontaneously runs the grep over `.lore/canon/try-failed-exp/` (per §2.6) and cites the prior rejection record.

## 5. Risks and mitigations

| Risk | Mitigation |
|------|-----------|
| `## Don't retry unless` becomes boilerplate ("if priorities change") instead of falsifiable. | Template's prompt text explicitly warns against this and gives concrete-condition examples. SKILL.md's "How to write one" reinforces. |
| Body-section grep is brittle to whitespace/formatting (e.g., `##  What was considered` with two spaces). | Validator regex tolerates `\s+` runs between `##` and text. Explicit invalid fixtures cover edge cases. |
| Profile YAML becomes a programming language over time. | v0.1 schema: `required_sections` + `fields` + `template` + `detect`. No computed logic. Escape hatch: profile may cite a sibling markdown "advanced rules" file (charter §3.4 escape-hatch). |
| Users write `try-failed-exp` when they should write `postmortem`. | SKILL.md boundary section is strong. `audit` (v0.2) flags records whose body reads more like an incident than a rejection (heuristic: presence of `## Timeline` or `## Impact` headings). |
| The "How to retrieve" behavior is prose-only, not testable. | Testable via integration test: stub a conversation "let's use Redis Cluster" and assert the model's next action is a grep over canon/try-failed-exp/ before proposing. Deferred to v0.2 when that test harness exists. |

## 6. Out of scope (deferred)

- `spike-outcome`, `library-eval`, `perf-dead-end` profiles (v0.3).
- Profile-level `fields` schema usage (no profile needs it in v0.1).
- Bidirectional cross-ref enforcement (handled by `meta/link` in v0.2).
- Auto-supersession detection (`meta/promote` in v0.2).
- Retrieval integration tests (see §5 last row).
- Profile hot-reload, profile inheritance chains, or profile mixins (YAGNI).

---

## Appendix — Implementation notes for the plan author

These are hints for the person writing Spec 2's implementation plan (not part of the design):

- **TDD order:** validator extension first (red → green → refactor) using invalid fixtures, then write SKILL.md + profile + template, then example record, then integration test (full round-trip new-id → template-fill → validate).
- **Reuse Spec 1's test infrastructure:** pytest + bats already wired; add to `tests/scripts/test_validate.py` rather than creating a new file.
- **PyYAML is already in `requirements-dev.txt`**, so the profile loader has no new deps.
- **Don't touch the charter, install infra, or hooks** — Spec 2's footprint is exactly the 8+2 files in §3.5.
- **Keep SKILL.md under ~200 lines.** The 7-part template already provides structure; prose should be tight.
