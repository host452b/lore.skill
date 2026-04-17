# Frontmatter schema

Every `.lore/**/*.md` record has YAML frontmatter. The fields below are the contract; profile extensions add more fields but never remove these.

## Required fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | `YYYY-MM-DD-<slug>`, matches regex `^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]{1,60}$`. Must equal filename (minus `.md`). Must begin with `date`. |
| `type` | enum | One of the 11 archetypes: `journal`, `codex`, `try-failed-exp`, `postmortem`, `retro`, `intent-log`, `deprecation-tracker`, `migration-guide`, `api-changelog`, `dependency-ledger`, `release-notes`. |
| `tier` | enum | `live` \| `archive` \| `canon`. Must agree with the record's directory path. |
| `date` | ISO date | `YYYY-MM-DD`. The record's *primary* date (decision / event / discovery), not wall-clock creation. |
| `title` | string | Human-readable title; appears in indexes. |
| `authors` | list\<string\> | Non-empty. Git-style identities: `"Joe Jiang <joejiang@nvidia.com>"`. |

## Optional fields

| Field | Type | Notes |
|-------|------|-------|
| `profile` | string | Name of the profile in `skills/<archetype>/profiles/<name>.yaml`. |
| `status` | enum | Profile-defined (e.g., ADR: `proposed/accepted/superseded/deprecated`). |
| `refs` | list\<cross-ref\> | Outbound references. See `cross-ref-grammar.md`. |
| `superseded_by` | cross-ref | Forward pointer to replacement record. |
| `supersedes` | list\<cross-ref\> | Inverse of `superseded_by`. `audit` keeps them consistent. |
| `tags` | list\<string\> | Free-form. |
| `source` | object | For imported records: `{adapter: from-git-log, ref: <sha>}`. |

## Validation

Use `scripts/validate.py <path>`:

```bash
python3 scripts/validate.py .lore/canon/codex/2026-01-04-postgres-primary-db.md
# OK: .lore/canon/codex/2026-01-04-postgres-primary-db.md
```

## Examples

### Minimal (journal, live-tier)

```yaml
---
id: 2026-04-17-first-record
type: journal
tier: live
date: 2026-04-17
title: First record
authors: ["Joe Jiang <joejiang@nvidia.com>"]
---
```

### Full (codex/ADR, canon-tier, with profile and refs)

```yaml
---
id: 2026-04-17-adr-postgres-primary
type: codex
tier: canon
date: 2026-04-17
title: Postgres as primary DB
authors: ["Joe Jiang <joejiang@nvidia.com>"]
profile: adr
status: accepted
refs: ["[[journal:2026-04-10-db-spike]]"]
tags: ["database", "architecture"]
---
```
