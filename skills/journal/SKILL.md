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

   ```bash
   bash scripts/new-id.sh --slug <short-kebab-phrase> --dir .lore/live/journal
   ```

   Note: dots in version tags must be replaced with hyphens
   (`v1.3.2` → `v1-3-2`) to satisfy the slug regex.

2. Start from the template at `./templates/web-service.md`. Copy to
   `.lore/live/journal/<id>.md`, substitute the placeholders, write the
   frontmatter fields and a short 2–5 sentence body.

3. Validate:

   ```bash
   python3 scripts/validate.py .lore/live/journal/<id>.md
   ```

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
