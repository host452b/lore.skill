---
name: harvest
description: Use to pull candidate lore records from git history into the
  cooling pipeline. Runs from-git-log adapter, presents a numbered batch of
  draft journal and try-failed-exp candidates, and guides the user to
  approve, edit, or skip each one.
type: meta
layer: 4
---

# What this skill does

`lore:harvest` mines recent git history for events worth recording and
presents them as a batch for review. It is the inbound half of the cooling
pipeline — raw git signal → structured lore candidates.

Produces two record types:

- **journal** (deploy, release, hotfix commits) — live tier
- **try-failed-exp** (revert commits) — canon tier

Harvest is intentionally not autonomous. The adapter stages drafts; you
confirm, edit, or discard each one. Lore does not write canon records
without your review.

# When to use me

- At the start of a retrospective to catch up on events not yet recorded.
- After a period of quiet (e.g., post-release) to harvest the deploy and
  rollback history.
- When onboarding a project to lore — run once with `--since` set far back
  to backfill history.

# When NOT to use me

- For real-time event capture — use `lore:journal` directly at the time of
  the event. Harvest is for backfilling, not live recording.
- For architectural decisions — use `lore:codex` directly.
- For manually written rejection records not derived from git — use
  `lore:try-failed-exp` directly.

# How to run a harvest session

## Step 1 — Stage candidates

Run the adapter with a date range:

```bash
python3 scripts/from-git-log.py --since "2 weeks ago" --out .lore/.harvest
```

Or cap at N candidates:

```bash
python3 scripts/from-git-log.py --last 10 --out .lore/.harvest
```

Preview without writing files:

```bash
python3 scripts/from-git-log.py --since "2 weeks ago" --dry-run
```

## Step 2 — Review the printed summary

The adapter prints a numbered list of what was staged:

```
Staged 3 candidate(s) to .lore/.harvest/:
  journal                  2026-04-15-deploy-api-v2.md
  journal                  2026-04-17-release-v1-3-0.md
  try-failed-exp           2026-04-16-revert-redis-cluster.md
```

## Step 3 — Process each candidate

For each draft file in `.lore/.harvest/`:

**Approve:**
1. Open the draft and replace all `TODO:` lines with real content.
2. For `try-failed-exp` drafts, make `## Don't retry unless` specific and
   falsifiable (e.g., "unless Redis ships native cross-slot transactions in
   a GA release"), not vague ("unless the situation changes").
3. Move to the correct permanent location:
   - journal → `.lore/live/journal/<id>.md`
   - try-failed-exp → `.lore/canon/try-failed-exp/<id>.md`
4. Validate: `python3 scripts/validate.py <path>` — expect `OK:`.

**Edit profile (optional):**
For journal drafts that use `profile: git-commit`, upgrade to
`profile: web-service` if you want `event-type` and `environment` enforced.
You'll need to add those fields to the frontmatter before validate passes.

**Skip:**
Delete the draft from `.lore/.harvest/`. Nothing is committed.

## Step 4 — Commit approved records

```bash
git add .lore/live/journal/ .lore/canon/try-failed-exp/
git commit -m "lore: harvest deploy + rollback events (YYYY-MM-DD)"
```

`.lore/.harvest/` is gitignored — only promoted records land in git.

# Draft format

Each staged draft has:

- All required frontmatter auto-populated from git metadata (id, type,
  tier, date, title, authors, profile, event-time/status).
- Body sections pre-filled with `TODO:` placeholder lines. Placeholders
  count as body content structurally, but must be replaced before the
  record is useful to future readers.
- A `<!-- Commit: <sha> -->` comment anchoring the draft to its source.

**Journal drafts** use `profile: git-commit` (minimal). Outcome is set to
`observed` as a placeholder — change to `succeeded`, `failed`,
`partial`, or `rolled-back` as appropriate.

**try-failed-exp drafts** use `profile: revert-commit`. All three required
sections (`## What was reverted`, `## Why reverted`,
`## Don't retry unless`) are present. Replace placeholders before promoting.

# Signals worth promoting

Not every event needs a lore record. Harvest is a judgment exercise.
Promote events that:

- Represent a first-time event type (first deploy to a new environment,
  first rollback of a particular service).
- Had a notable outcome — a rollback, incident, non-trivial migration.
- Would answer a question a future team member might ask ("why did we
  revert the Redis cluster approach?").
- Are deploys that execute a prior codex decision — cross-reference them
  with `refs: ["[[codex:<id>]]"]`.

Skip:

- Routine, repeated deploys of stable services with no notable outcome.
- Revert commits that were trivial fixes (typo, missing semicolon) with no
  architectural lesson.

# How to avoid duplicates

Before running harvest, check whether recent events are already recorded:

```bash
grep -rli "<service-name>" .lore/live/journal/
grep -rli "<component-name>" .lore/canon/try-failed-exp/
```

Alternatively, use `--since` with a date after your last harvest run. The
adapter does not deduplicate against existing lore records — only against
other drafts in the current batch.
