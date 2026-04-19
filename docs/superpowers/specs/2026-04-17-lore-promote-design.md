# Lore — `promote` Meta-Skill Design

| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Date** | 2026-04-17 |
| **Type** | Spec 7 — promote meta-skill (v0.1 closeout) |
| **Scope** | `lore:promote` Layer-4 skill — cooling-pipeline operator |
| **Author** | host452b |
| **Depends on** | Spec 0 (charter), Spec 1 (substrate), Specs 2-5 |
| **Defers** | Automated scoring, cross-project promote (v0.3+) |

---

## 0. Executive summary

`lore:promote` is the cooling-pipeline operator. Where `lore:detect` watches
for signals in the current conversation, `lore:promote` reads the *existing
record corpus* and surfaces what should move cold-ward:

- `journal` rollbacks/failures with no `try-failed-exp` counterpart
- High-frequency recurring events that suggest a `codex` pattern
- `codex` records stuck at `status: proposed`
- Orphaned TFE records with no `refs:` link to the decision that won

Promote is invoked explicitly, not always-on. It's a periodic review
tool — run it after a sprint, before a planning session, or when asking
"what have we learned?"

Promote never writes records autonomously. It surfaces candidates; you decide.

---

## 1. Four promotion heuristics

### 1.1 Rollback/failure → try-failed-exp

```bash
grep -rli "outcome: rolled-back\|outcome: failed" .lore/live/journal/
```

For each result: check whether a corresponding `try-failed-exp` exists on
the same component or approach:

```bash
grep -rli "<component-keyword>" .lore/canon/try-failed-exp/
```

If no TFE exists → suggest `lore:try-failed-exp` (profile: `revert-commit`
if the failure was a revert; `rejected-adr` if it was an intentional
evaluation that concluded in rejection).

### 1.2 Recurring events → codex candidate

```bash
grep -rh "event-type:" .lore/live/journal/ | sort | uniq -c | sort -rn
```

Three or more `journal` entries with the same `event-type` and similar
service/component names suggest a repeatable pattern. That pattern may
deserve a `codex` rule: "we deploy X this way, for these reasons."

Threshold: 3+ events of the same type within 90 days → suggest a codex.

### 1.3 Proposed codex → resolve or withdraw

```bash
grep -rli "status: proposed" .lore/canon/codex/
```

For each: check the record's `date:` field. If it has been `proposed` for
more than 14 days without becoming `accepted`, surface it:
- Was the decision made and the status forgotten to update?
- Is the decision still open — if so, what's blocking it?
- Should it be `deprecated` (withdrawn without a successor)?

### 1.4 Orphaned TFE → add cross-ref

```bash
grep -rL "^refs:" .lore/canon/try-failed-exp/
```

For each TFE with no `refs:` field: search for a `codex` record that
represents the winning alternative (topic keywords overlap).

If a match exists → suggest adding `refs: ["[[codex:<id>]]"]` to the TFE,
and `refs: ["[[try-failed-exp:<id>]]"]` to the codex (bidirectional link).

---

## 2. Response format

```
Promote scan — <date>

Found N promotion candidate(s):

[1] ROLLBACK → TFE
    .lore/live/journal/2026-04-15-api-gateway-rollback.md (outcome: rolled-back)
    No matching try-failed-exp found.
    → Suggest: lore:try-failed-exp (profile: revert-commit)

[2] PROPOSED CODEX (29 days old)
    .lore/canon/codex/2026-03-20-database-sharding.md
    → Resolve: accept / deprecate / document the blocker

[3] ORPHANED TFE → possible link
    .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md
    Possible match: .lore/canon/codex/2026-03-15-postgres-primary-session-store.md
    → Add refs: on both sides

Want me to process [1]?
```

---

## 3. What promote is not

- **Not an autonomous writer.** All canon changes require human confirmation.
- **Not a duplicate detector.** Looks for *missing* records and *missing links*,
  not duplicates (that's `lore:audit`, a future skill).
- **Not a linter.** Schema errors are `scripts/validate.py`'s job.

---

## 4. File inventory

| Path | Layer | Purpose |
|------|-------|---------|
| `skills/promote/SKILL.md` | 4 | Promote meta-skill |

No scripts, no validator changes, no tests. Pure skill content.

**Total: 1 new file.**

---

## 5. v0.1 completion note

With `lore:promote` shipped, the v0.1 skill set is complete:

| Layer | Skills shipped |
|-------|---------------|
| 0 — substrate | `core` (schema, id, cross-ref, tier, layout) |
| 1 — archetypes | `journal`, `codex`, `try-failed-exp` |
| 2 — compliance | *(v0.2)* |
| 3 — adapters | `from-git-log` (harvest adapter) |
| 4 — meta | `harvest`, `detect`, `promote` |
| primer | `using-lore` (session-start hook) |

v0.2 scope (next): `postmortem`, `migration-guide`, compliance overlays
(`semver`, `keep-a-changelog`), `to-keep-a-changelog` outbound adapter,
`.codex/` + `.opencode/` install shims.
