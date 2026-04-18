---
name: promote
description: Use to run the cooling-pipeline operator — scans live and canon
  tiers for patterns that warrant promotion, identifies orphaned cross-refs,
  and surfaces proposed codex records that need resolution.
type: meta
layer: 4
---

# What this skill does

`lore:promote` reads the existing record corpus and surfaces what should
move cold-ward in the cooling pipeline:

- `journal` rollbacks or failures with no `try-failed-exp` counterpart
- High-frequency recurring events suggesting a `codex` pattern
- `codex` records stuck at `status: proposed`
- `try-failed-exp` records with no `refs:` link to the decision that won

Promote never writes records autonomously. It surfaces candidates; you decide.

# When to use me

- After a sprint or release cycle — what happened that should be crystallized?
- When `.lore/live/` has grown significantly without new canon records.
- When asking "what have we learned?" — promote synthesizes the answer.
- Periodically (e.g., once per release) as a pipeline health check.

# When NOT to use me

- To fix schema errors — use `scripts/validate.py` for that.
- To create records from scratch — use the relevant archetype skill.
- To find duplicate records — that's `lore:audit` (future skill).

# How to run a promote session

## Step 1 — Rollback/failure → try-failed-exp

```bash
grep -rli "outcome: rolled-back\|outcome: failed" .lore/live/journal/
```

For each result, check whether a `try-failed-exp` already exists:

```bash
grep -rli "<component-keyword>" .lore/canon/try-failed-exp/
```

If none found: suggest `lore:try-failed-exp`. Use profile:
- `revert-commit` — if the failure was a git revert
- `rejected-adr` — if it was a deliberate "we tried this and stopped"

## Step 2 — Recurring events → codex candidate

```bash
grep -rh "event-type:" .lore/live/journal/ | sort | uniq -c | sort -rn
```

Three or more events of the same `event-type` for the same service within
90 days suggest a repeatable pattern worth a `codex` rule.

Example: five "deploy api-gateway to prod" entries → consider a codex:
"we deploy api-gateway using blue-green; canary threshold is 5% error rate."

## Step 3 — Proposed codex → resolve or withdraw

```bash
grep -rli "status: proposed" .lore/canon/codex/
```

For each: check `date:`. If proposed for more than 14 days, surface it:
- Was the decision made but status not updated → flip to `accepted`
- Still open → document what's blocking it in the body
- Withdrawn → flip to `deprecated`

## Step 4 — Orphaned TFE → add cross-ref

```bash
grep -rL "^refs:" .lore/canon/try-failed-exp/
```

For each TFE with no `refs:` field: search for a `codex` that represents
the winning alternative (overlapping topic keywords).

If a match exists, suggest adding bidirectional links:
- TFE: `refs: ["[[codex:<id>]]"]`
- Codex: `refs: ["[[try-failed-exp:<id>]]"]`

# Response format

Present findings as a numbered list before acting:

```
Promote scan — <YYYY-MM-DD>

Found N candidate(s):

[1] ROLLBACK → TFE
    .lore/live/journal/2026-04-15-api-gateway-rollback.md
    No matching try-failed-exp found.
    → lore:try-failed-exp (profile: revert-commit)

[2] PROPOSED CODEX (29 days)
    .lore/canon/codex/2026-03-20-database-sharding.md
    → Accept / deprecate / document blocker

[3] ORPHANED TFE
    .lore/canon/try-failed-exp/2026-04-17-no-runtime-plugin-system.md
    Possible codex match: .lore/canon/codex/2026-03-15-postgres-primary-session-store.md
    → Add refs: on both sides

Want me to process [1]?
```

Process one candidate at a time. After each, ask whether to continue
to the next.

# Promote is not autonomous

Promote reads and suggests; it does not write. Every record created or
modified during a promote session requires explicit user confirmation.
When in doubt: surface the candidate, explain why, wait for "yes."
