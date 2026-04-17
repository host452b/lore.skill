---
name: using-lore
description: Use when starting any conversation on a project that has lore installed — establishes what lore is, the cooling-pipeline thesis, the 11 archetypes, the `lore:<skill>` naming convention, and when to proactively invoke lore skills.
type: primer
invocable: true
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# Lore

Lore turns this project's lived history — deploys, experiments, decisions, failed attempts, incidents, releases — into structured, cross-referenced, git-tracked project memory stored under `.lore/`.

## The thesis — the cooling pipeline

```
LIVE  ────► ARCHIVE ────► CANON
raw         crystallized   reusable rule
```

- **Live (流):** high-churn event signal. `journal`, `intent-log`, `dependency-ledger`.
- **Archive (档):** one-time retrospection. `postmortem`, `retro`, `release-notes`.
- **Canon (典):** reusable rules. `codex` (decisions), `try-failed-exp` (attempts that failed), `migration-guide`.

Information phase-transitions cold-ward over time. `lore:promote` operates the pipeline.

## Vocabulary

`timeline` · `checkpoint` · `recall` · `lore` · `legacy`

## Skills you can invoke

**Archetypes (the primary user-facing nouns):**

- `lore:journal` — record a discrete event (deploy, incident, experiment run)
- `lore:codex` — record a decision (ADR, design doc)
- `lore:try-failed-exp` — record an attempt that failed (spike that didn't pan out, library evaluated but not chosen, approach rejected)
- `lore:postmortem`, `lore:retro`, `lore:intent-log`, `lore:deprecation-tracker`, `lore:migration-guide`, `lore:api-changelog`, `lore:dependency-ledger`, `lore:release-notes` *(later versions)*

**Adapters (format bridges):**

- `lore:from-git-log` — harvest candidate records from git commits
- `lore:to-keep-a-changelog` — export release-notes to CHANGELOG.md

**Meta (automation glue):**

- `lore:detect` — first-run project scan, suggests starter archetypes
- `lore:harvest` — batch-import candidate records from git/issues/external sources
- `lore:promote` — cooling-pipeline operator *(v0.2)*
- `lore:link`, `lore:audit`, `lore:migrate` *(later)*

## When to proactively invoke lore

- User mentions a decision they just made → consider `lore:codex`.
- User mentions an approach they tried and abandoned → consider `lore:try-failed-exp`.
- User asks "have we tried X before?" → check `.lore/canon/try-failed-exp/`.
- User asks "why did we choose Y?" → check `.lore/canon/codex/`.
- User is starting a new session in a project with no `.lore/` yet → consider suggesting `lore:detect`.
- User is starting a session in a project with a long git history but an empty `.lore/` → consider suggesting `lore:harvest`.

## What lore is NOT

- Not a logging/observability tool. Lore records are human-written or human-confirmed.
- Not a wiki. Lore records are short, typed, cross-referenced.
- Not an incident-management platform. `postmortem` is the retrospection artifact, not the runbook.
- Not user-level memory. Lore is project-scoped; each consuming project has its own `.lore/`.

## Where lore stores things

```
<project-root>/
└── .lore/
    ├── live/<archetype>/<YYYY-MM-DD-slug>.md
    ├── archive/YYYY/<archetype>/<YYYY-MM-DD-slug>.md
    └── canon/<archetype>/<YYYY-MM-DD-slug>.md
```

All files are YAML-frontmatter + markdown. Git-tracked by default.

## Core conventions

- **ID format:** `YYYY-MM-DD-<slug>` (generator: `scripts/new-id.sh`)
- **Cross-refs:** `[[archetype:id]]` (e.g. `[[codex:2026-01-04-postgres-primary-db]]`)
- **Validation:** `scripts/validate.py <path>` checks frontmatter schema

For full details see `skills/core/`:
- `frontmatter-schema.md`, `id-scheme.md`, `cross-ref-grammar.md`, `tier-model.md`, `directory-layout.md`
