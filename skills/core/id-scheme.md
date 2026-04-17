# ID scheme

Every lore record has a unique, human-readable ID of the form:

```
YYYY-MM-DD-<slug>
```

Examples:
- `2026-04-10-deploy-v1.3.2`
- `2026-02-20-rejected-redis-cluster`
- `2026-01-04-postgres-primary-db`

## Why this format

- **Sortable.** Lexical sort == chronological sort.
- **Git-friendly.** Filenames are stable, no ambiguous characters.
- **Human-readable.** You can recognize "the Postgres ADR from January" at a glance.
- **Slug-stable.** The slug is a short kebab-case phrase; re-slugifying isn't required when the title changes.

## Rules

- **Date** is `YYYY-MM-DD` (zero-padded). It is the record's *primary* date:
  - `journal`: event date
  - `codex`: decision date
  - `try-failed-exp`: discovery / conclusion date
  - `postmortem`: incident date
  - Not wall-clock creation time.
- **Slug** matches `^[a-z0-9][a-z0-9-]{1,60}$`: lowercase alphanumerics and hyphens, starting alphanumeric, length 2–61.
- **Collision suffix:** if the same date + slug already exists, append `-2`, `-3`, etc.

## Generating IDs

Use `scripts/new-id.sh`:

```bash
# Today's date, collision-safe within a directory
bash scripts/new-id.sh --slug redis-cluster-spike --dir .lore/canon/try-failed-exp
# 2026-04-17-redis-cluster-spike

# Explicit date
bash scripts/new-id.sh --date 2026-03-15 --slug payment-outage --dir .lore/archive/2026/postmortem
# 2026-03-15-payment-outage
```

Every archetype SKILL.md instructs Claude to call `new-id.sh` as the first step of writing a record.

## Filename invariant

The record's filename (minus `.md`) must equal `id`. The `audit` meta-skill enforces this.
