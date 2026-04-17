# Tier model — the cooling pipeline

Every lore record lives at one of three **tiers**. Tier expresses *temperature* — how often the record changes, how reusable it is, how often it's re-read.

| Tier | Name (zh) | Meaning | Typical archetypes | Churn |
|------|-----------|---------|--------------------|-------|
| `live` | 流 (stream) | Raw, high-churn event signal | `journal`, `intent-log`, `dependency-ledger` | High |
| `archive` | 档 (record) | Crystallized one-time retrospection | `postmortem`, `retro`, `release-notes` | Low (append-only) |
| `canon` | 典 (canon) | Reusable, repeatedly-cited rule | `codex`, `try-failed-exp`, `migration-guide` | Medium (revised) |

## The cooling pipeline

```
LIVE  ──── curate ────►  ARCHIVE  ──── distill ────►  CANON
```

Information phase-transitions cold-ward over time. The `lore:promote` skill operates this pipeline:

- Scans `live/journal/` for recurring patterns → suggests `canon/codex/` entries.
- Scans `archive/postmortem/` for lessons → suggests `canon/codex/` or `canon/try-failed-exp/` entries.

Without `promote`, lore degenerates into "a directory of templates." With `promote`, lore is a knowledge-accumulation system.

## Tier is a property of the record, not the archetype

An archetype can produce records at more than one tier (rare). Example: `api-changelog` entries default to `archive`, but heavily-cited breaking-change entries can be promoted to `canon` as part of a `migration-guide`.

## Storage: directory and frontmatter must agree

A record lives at `.lore/<tier>/<archetype>/<id>.md`. The `tier:` frontmatter field must match the directory. The `lore:audit` skill enforces this; `scripts/validate.py` enforces it for any file located under a `.lore/<tier>/` directory layout.

## Tier transitions

**Cold-ward (live → archive → canon):** common, handled by `lore:promote`. Both the file location and the `tier:` field are updated atomically.

**Hot-ward (canon → archive, archive → live):** rare, user-driven only. In v0.1 and v0.2, `lore:promote` only moves records cold-ward; hot-ward motion requires a manual move + frontmatter edit + commit.

## Why three tiers, not two or five

- Two (`live`/`canon`) loses the "write once, archive-and-done" middle category that postmortems and retros need — they aren't live, but they also aren't the reusable canon; the *distilled lesson* is.
- Five or more (e.g., adding "draft", "deprecated") overloads tier with status. Status belongs in the `status:` field, not the tier.

Three tiers is the minimum that gives the cooling pipeline a middle stage.
