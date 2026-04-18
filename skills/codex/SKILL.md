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

   ```bash
   bash scripts/new-id.sh --slug <short-kebab-phrase> --dir .lore/canon/codex
   ```

2. Copy the template at `./templates/adr.md` to
   `.lore/canon/codex/<id>.md`, substitute placeholders, write the three
   required sections (Context, Decision, Consequences).

3. In the Decision section, be specific enough that a future reader can
   tell whether their situation matches yours.

4. In Consequences, name the trade-offs explicitly. If rejected alternatives
   deserve their own records, create `try-failed-exp:rejected-adr` entries
   and cite them in `refs:`.

5. Validate:

   ```bash
   python3 scripts/validate.py .lore/canon/codex/<id>.md
   ```

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

```bash
grep -rli "<topic keywords>" .lore/canon/codex/
```

If a matching record exists:

- If `status: accepted`, surface the decision to the user. Don't
  re-propose something already decided. If circumstances suggest
  revisiting, cite the record and make the case for supersession.
- If `status: superseded`, follow the `superseded_by` chain to find
  the current decision.
- If `status: proposed`, the decision is still being weighed —
  contribute to the discussion rather than opening a parallel one.

Never silently re-propose something already in the canon.
