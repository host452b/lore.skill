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
