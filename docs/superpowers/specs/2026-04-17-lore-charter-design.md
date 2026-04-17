# Lore — Charter Design Document

| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Date** | 2026-04-17 |
| **Type** | Architectural charter (Spec 0) |
| **Scope** | Full `lore` plugin suite — all layers, all archetypes |
| **Author** | Joe Jiang \<joejiang@nvidia.com\> |
| **Supersedes** | Working name `chronicle`; prior directory name `try-failed-log.skill` |

---

## 0. Executive summary

**Lore** is a Claude Code plugin that turns a software project's lived history — deploys, experiments, decisions, failed attempts, incidents, releases — into structured, cross-referenced, git-tracked project memory.

Its thesis is not "11 archetypes of record." Its thesis is the **cooling pipeline**: raw signal (live tier) is crystallized into single-use retrospection (archive tier) and then distilled into reusable rules (canon tier). Most projects have plenty of signal and almost no canon. Lore makes the transitions first-class.

Lore's differentiation anchor is `try-failed-exp` — a canon-tier archetype for recording attempts that failed. The postmortem space is saturated (Jeli, Blameless, FireHydrant); the "attempts-that-failed" space has no mature tooling. `try-failed-exp` is the skill the suite will be remembered for.

The suite is structured as one plugin containing ~34 small SKILL.md files organized into 5 layers: core substrate, archetypes, compliance overlays, adapters, and meta-skills. Superpowers is the prior art — not just for skill granularity, but also for **installation architecture and user experience**: multi-platform support (Claude Code, Cursor, Codex, OpenCode, Gemini CLI) via thin per-platform adapter dirs, one-line install via marketplace or fetch-and-follow-README, zero-config auto-discovery, and a session-start hook that primes the intro skill every session. Lore adopts this pattern wholesale. v0.1 ships 8 of the 34 skills; v1.0 ships the full set.

---

## 1. Goals, non-goals, and central insight

### 1.1 Goal

Turn a project's lived history into structured, cross-referenced, git-tracked project memory, optimized for how software teams actually work: plenty of raw signal (git, CI, runtime), almost no structured synthesis ("why did we reject Redis?", "what's the canonical migration story?").

### 1.2 Non-goals

- **Not a logging or observability tool.** Lore interops with Sentry, MLflow, etc.; it does not replace them.
- **Not a wiki.** Lore records are structured, short, typed; long-form design docs stay in `docs/`.
- **Not an incident-management platform.** `postmortem` in lore is the retrospection *artifact*, not the paging/runbook tool.
- **Not a PM/ticketing system.** `intent-log` captures design intent, not sprint tickets.
- **Not general memory.** Lore is project-scoped and git-tracked under `.lore/` in the consuming repo. User-level memory belongs elsewhere.
- **Not a knowledge base for the code itself.** API documentation stays in docstrings/READMEs.
- **Not single-platform.** Lore is distributed cross-platform from v0.1 (Claude Code + Cursor) and adds Codex, OpenCode, and Gemini CLI adapters by v1.0 — matching Superpowers' distribution footprint. Deep platform-specific skill adaptations beyond the install shim are deferred past v1.0.

### 1.3 Central insight — the cooling pipeline

```
LIVE (流)  ─────────►  ARCHIVE (档)  ─────────►  CANON (典)
raw signal             crystallized event         reusable rule
high churn             single-use retrospection   repeatedly cited

journal           ─── postmortem               ─── codex
intent-log            retro                        try-failed-exp
dependency-ledger     release-notes                migration-guide
                      api-changelog (mixed)
```

Information phase-transitions from hot/fine-grained/ephemeral (left) to cold/coarse-grained/persistent (right). Most tools optimize one band. Lore optimizes the **transitions**.

The `meta/promote` skill is the pipeline operator: it scans live-tier for recurring patterns and suggests canon rules, scans archive (postmortems, retros) for lessons and suggests codex or try-failed-exp entries.

Without `promote`, lore is "a directory of markdown templates." With it, lore is the thing that turns a team's ambient noise into institutional knowledge.

### 1.4 Vocabulary (pillar concepts)

| Word | Role |
|------|------|
| **timeline** | The medium — every record has a timestamp; tiers are *phases on a timeline*, not separate stores. |
| **checkpoint** | The act of writing — what each archetype invocation produces. |
| **recall** | The retrieval motion — enabled by `meta/link`, cross-refs, grep. |
| **lore** | The canonical destination — canon-tier output, the product. |
| **legacy** | The long-horizon accumulation — what a project earns over years. |

These terms are pinned in the glossary (Appendix A) and used consistently in the README, SKILL.md descriptions, and user-facing prose.

### 1.5 Differentiation anchor — `try-failed-exp`

`try-failed-exp` is the canon-tier archetype for recording attempts that failed. It is the anchor identity of the suite, for three reasons:

1. **Postmortem space is saturated** — no differentiation there.
2. **Tried-and-failed knowledge is almost entirely absent from software tooling.** Every experienced engineer says "I wish I'd known someone already tried that." Lore makes this knowledge a first-class record type.
3. **It is reverse-canon.** If codex says "do this," `try-failed-exp` says "don't do this, and here's exactly why." The structural parallel to codex is load-bearing: both are canon-tier, both are repeatedly cited, both are revisable. They are two faces of the same pattern.

---

## 2. Layered architecture & physical layout

### 2.1 Five layers

| Layer | Role | Examples | User-invoked? |
|------:|------|----------|:-:|
| **0** | **Core substrate** — shared conventions (ID, frontmatter, cross-ref, tier model) + 3 tiny scripts | `core/SKILL.md`, `scripts/new-id.sh` | No (referenced by others) |
| **1** | **Archetypes** — one skill per noun, each with profile slots | `journal`, `codex`, `try-failed-exp`, `postmortem`, `retro`, `intent-log`, `deprecation-tracker`, `migration-guide`, `api-changelog`, `dependency-ledger`, `release-notes` (11 total) | Yes |
| **2** | **Compliance overlays** — audit-only, no content | `semver`, `keep-a-changelog`, `sbom-spdx`, `cve-tracking`, `openapi-diff`, `slsa` | Yes (declaratively hook into archetypes) |
| **3** | **Adapters** — format translation in/out | `from-git-log`, `from-sentry`, `from-mlflow`, `to-keep-a-changelog`, `to-release-please` | Yes |
| **4** | **Meta / automation** — cross-skill glue | `detect`, `link`, `harvest`, `promote`, `audit`, `migrate` | Yes |

**Dependency rule (strict, unidirectional):** layer *N* may depend on layer *N−k* for any *k ≥ 0*; never the other direction. Archetypes never reference compliance. Compliance never references adapters. Core references nothing.

### 2.2 Physical layout — plugin side (skills view)

This view shows only the skills-relevant portion of the plugin tree. The full top-level layout (including install shim dirs `.claude-plugin/`, `.cursor-plugin/`, `.codex/`, `.opencode/`, platform primer files, and `hooks/`) is specified in §4.1.

```
lore.skill/
├── package.json                   ← plugin manifest (details in §4.1)
├── README.md                      ← uses timeline/checkpoint/recall/lore/legacy vocabulary
├── CHANGELOG.md                   ← dogfooded from our own to-keep-a-changelog adapter
├── scripts/                       ← Layer-0 helpers
│   ├── new-id.sh                  ← YYYY-MM-DD-slug generator, collision-safe
│   ├── validate.py                ← frontmatter schema check
│   └── git-events.sh              ← stable git log → JSON lines for harvest
│
└── skills/
    ├── core/                      ← Layer 0 (non-invokable, reference-only)
    │   ├── SKILL.md
    │   ├── frontmatter-schema.md
    │   ├── id-scheme.md
    │   ├── cross-ref-grammar.md
    │   ├── tier-model.md
    │   └── directory-layout.md
    │
    ├── journal/                   ← Layer 1 archetype (pattern repeated for all 11)
    │   ├── SKILL.md
    │   ├── profiles/
    │   │   ├── web-service.yaml
    │   │   ├── ml-experiment.yaml
    │   │   ├── spike.yaml
    │   │   └── build-log.yaml
    │   └── templates/
    │       └── default.md
    ├── codex/
    ├── try-failed-exp/            ← HEADLINE
    ├── postmortem/
    ├── retro/
    ├── intent-log/
    ├── deprecation-tracker/
    ├── migration-guide/
    ├── api-changelog/
    ├── dependency-ledger/
    ├── release-notes/
    │
    ├── compliance/                ← Layer 2
    │   ├── semver/
    │   ├── conventional-commits/
    │   ├── keep-a-changelog/
    │   ├── sbom-spdx/
    │   ├── sbom-cyclonedx/
    │   ├── cve-tracking/
    │   ├── openapi-diff/
    │   └── slsa/
    │
    ├── adapters/                  ← Layer 3
    │   ├── from-git-log/
    │   ├── from-github-releases/
    │   ├── from-sentry/
    │   ├── from-mlflow/
    │   ├── to-keep-a-changelog/
    │   ├── to-conventional-changelog/
    │   ├── to-openapi-diff/
    │   └── to-release-please/
    │
    └── meta/                      ← Layer 4
        ├── detect/
        ├── link/
        ├── harvest/
        ├── promote/               ← the cooling-pipeline operator
        ├── audit/
        └── migrate/
```

**Count at full buildout:** 1 core + 11 archetypes + 8 compliance + 8 adapters + 6 meta = **34 SKILL.md files**. v0.1 ships 8 of them.

### 2.3 Physical layout — user-project side

When a user installs lore and starts using it, `.lore/` materializes at the consuming project's root, git-tracked:

```
<user-project>/
├── .lore/
│   ├── live/                      ← "timeline" — high-churn checkpoints
│   │   ├── journal/
│   │   │   ├── 2026-04-10-deploy-v1.3.2.md
│   │   │   └── 2026-04-12-mlflow-run-847.md
│   │   ├── intent-log/
│   │   └── dependency-ledger/
│   │
│   ├── archive/                   ← crystallized events; one-and-done
│   │   └── 2026/
│   │       ├── postmortem/2026-03-15-payment-outage.md
│   │       ├── retro/2026-Q1.md
│   │       └── release-notes/v1.3.md
│   │
│   └── canon/                     ← "lore" — the reusable rules
│       ├── codex/
│       │   └── 2026-01-04-postgres-primary-db.md
│       ├── try-failed-exp/
│       │   └── 2026-02-20-rejected-redis-cluster.md
│       └── migration-guide/
│
├── src/
├── package.json
└── ...
```

Design choices baked in:

1. **Tier is both directory AND frontmatter.** The directory lets humans (and `grep`) eyeball tier; frontmatter lets `promote` update tier atomically without a rename. `audit` enforces they agree.
2. **Archive is year-bucketed**; canon and live are flat. Archive is append-only cold storage; canon and live are working sets.
3. **No cross-archetype sub-nesting.** Every record sits at exactly `.lore/<tier>/<archetype>/<id>.md`.
4. **`.lore/` is git-tracked by default.** Teams that want it gitignored can opt out; the out-of-the-box story is "your lore ships with your repo."

### 2.4 Dependency & invocation rules

- **Core is never invoked by user.** It only publishes conventions; other SKILL.md files cite it by path.
- **Archetypes are the user's mental model.** "I want to write an ADR" → `/lore:codex`. "I want to record a failed spike" → `/lore:try-failed-exp`.
- **Compliance is declarative.** A compliance SKILL.md declares `hooks-into: [api-changelog, release-notes]` in frontmatter. When an archetype runs, Claude (reading both SKILL.mds) links them by matching `type` against `hooks-into`. No runtime coupling.
- **Adapters are explicit.** User invokes `/lore:adapters/from-git-log` directly, or `meta/harvest` invokes them internally.
- **Meta is the glue.** These are how `.lore/` gets populated without manual work.

---

## 3. Layer contracts

### 3.1 Core substrate — frontmatter schema

Every `.lore/**/*.md` file has YAML frontmatter with these fields:

| Field | Required | Type | Notes |
|-------|:-:|------|-------|
| `id` | ✓ | string | `YYYY-MM-DD-<slug>`, regex `^\d{4}-\d{2}-\d{2}-[a-z0-9][a-z0-9-]{1,60}$`. Matches filename (minus `.md`). |
| `type` | ✓ | enum | One of 11 archetype names. |
| `tier` | ✓ | enum | `live` \| `archive` \| `canon`. Must match directory path. |
| `date` | ✓ | ISO date | `YYYY-MM-DD`, same as ID prefix. |
| `title` | ✓ | string | Human-readable; shown in indexes. |
| `authors` | ✓ | list\<string\> | Git-style identities. |
| `profile` | ✗ | string | Profile name if applicable (e.g., `web-service`, `adr`, `rejected-adr`). |
| `status` | ✗ | enum | Profile-defined (e.g., ADR: `proposed/accepted/superseded/deprecated`). |
| `refs` | ✗ | list\<ref\> | Outbound cross-refs: `["[[codex:2026-01-04-postgres-primary-db]]"]`. |
| `superseded_by` | ✗ | ref | Forward pointer to replacement record. |
| `supersedes` | ✗ | list\<ref\> | Inverse of `superseded_by`. `audit` keeps them consistent. |
| `tags` | ✗ | list\<string\> | Free-form. |
| `source` | ✗ | object | If imported: `{adapter: from-git-log, ref: <sha>}`. |

Profile-specific fields are layered on top via the profile's YAML (see §3.4).

### 3.2 Core substrate — ID, cross-ref grammar, tier mechanics

**ID:** `YYYY-MM-DD-<slug>`. Date is the record's *primary* date (decision date for codex, event date for journal, discovery date for try-failed-exp), not wall-clock creation time. `scripts/new-id.sh` handles collision-safe suffixes (`-2`, `-3`) when two records share slug+date.

**Cross-ref grammar:** `[[<archetype>:<id>]]`. Appears in frontmatter (`refs`, `superseded_by`, `supersedes`) for structured relationships, and in prose body for casual mentions. `meta/link` validates both.

**Tier rules:**

- Tier is a property of the record, not the archetype. An archetype can produce records at multiple tiers (rare; `api-changelog` entries default to archive but can be promoted to canon).
- Tier transitions are explicit; `meta/promote` moves files between dirs and updates the `tier` field atomically.
- Directory and frontmatter must agree; `audit` enforces.
- Hot-ward tier motion (canon → archive, archive → live) is rare and user-driven only; `promote` only goes cold-ward in v0.1–v0.2.

### 3.3 Archetype contract — SKILL.md template

Every archetype's SKILL.md follows this fixed 7-part structure:

```markdown
---
name: journal
description: Use when recording a discrete event that happened — deploys,
  incidents, experiment runs, CI failures. Captures WHAT happened, not WHY.
type: archetype
default-tier: live
profiles: [web-service, ml-experiment, spike, build-log]
---

# When to use me
Record-a-happening situations:
- A deploy just landed
- An incident was detected/resolved
- An experiment was run
- A dependency version changed

# When NOT to use me (boundaries)
- "We decided to use PostgreSQL" → that's `codex`, not journal
- "We tried MongoDB but gave up" → that's `try-failed-exp`, not journal
- Journal is for observable events only

# Required fields (beyond core)
- `event-time` (ISO timestamp, more precise than `date`)
- `outcome` (succeeded | failed | partial | rolled-back)

# Optional fields
- `duration`, `metrics`, `commit-sha`, `environment`

# Profile slots
See `./profiles/*.yaml`. If user's project has a web framework, suggest
`web-service`. If MLflow/W&B artifacts, suggest `ml-experiment`.

# Lifecycle
Journal entries are write-once. Events don't un-happen. A later event may
`refs` this one, but this record stays.

# How to write one
1. Generate ID: `bash scripts/new-id.sh journal <slug>`
2. Pick profile (or none)
3. Fill frontmatter + body
4. Save to `.lore/live/journal/<id>.md`
5. If any compliance skills declare `hooks-into: [journal]`, invoke them

# Cross-refs
Journal entries commonly ref: codex (for decisions behind the event),
try-failed-exp (if the event is a known failure recurring), intent-log
(if this executes a prior intent).
```

Every archetype uses this same 7-part structure. Users learn one archetype, they know all of them. Boundary sections are the load-bearing part; without them the suite degenerates into a grab-bag.

### 3.4 Profile mechanism — data-driven archetype extensions

A profile is a YAML file that extends an archetype's field set and template.

```yaml
# skills/codex/profiles/adr.yaml
name: adr
extends: codex
description: Michael Nygard-style Architecture Decision Record
fields:
  status:
    type: enum
    values: [proposed, accepted, superseded, deprecated]
    required: true
  context:
    type: markdown
    required: true
    prompt: "What forces are at play? What's the problem?"
  decision:
    type: markdown
    required: true
    prompt: "What did we decide?"
  consequences:
    type: markdown
    required: true
    prompt: "What becomes easier? What becomes harder?"
template: templates/adr.md
detect:
  suggest-when:
    - files-exist: ["docs/adr/", "docs/architecture/"]
    - has-dependency: ["@nygard/adr-tools"]
```

**How Claude uses a profile:** the archetype SKILL.md tells Claude "if user specifies `--profile adr`, read `profiles/adr.yaml`, merge its `fields` into the frontmatter requirements, use `template` as the body skeleton, ask the `prompt` questions one by one."

**Authoring bar:** writing a new profile is editing one YAML file. No code changes. Non-programmers can extend the suite.

**Escape hatch:** profiles needing logic beyond declarative fields can cite a sibling markdown file for advanced rules (prose instructions Claude reads). Runtime plugins are explicitly rejected.

### 3.5 Compliance overlay mechanism

Compliance skills do not produce records. They *audit* and *enhance* records produced by archetypes.

```markdown
---
name: semver
description: Validate that release-notes and api-changelog entries are
  semver-consistent (breaking changes bump major, etc.)
type: compliance
hooks-into: [release-notes, api-changelog, migration-guide]
---

# When I run
After any archetype I hook into writes a record. The archetype's SKILL.md
instructs Claude to run all compliance skills whose `hooks-into` includes
the archetype's type.

# What I check
- If the record has `breaking-changes: true` but version bump is patch/minor → flag
- If version bump is major but no `breaking-changes` listed → flag
- Inconsistent version references across sibling records → flag

# Output
I do not write to .lore/. I produce a structured report:
{passed: [...], warnings: [...], errors: [...]}
```

**No runtime hooks.** Claude Code skills have no event system, so the coupling is textual: the archetype's SKILL.md says "after saving, run compliance skills where `hooks-into` includes my type." Claude reads both SKILL.md files and does the linking. Simple, robust, inspectable.

### 3.6 Adapter mechanism — format bridges

Two directions.

**Inbound (`from-*`):** read external data, produce candidate records. Do NOT write to `.lore/` directly. Present candidates to the user (usually via `meta/harvest`, which orchestrates batch imports).

```markdown
---
name: from-git-log
type: adapter
direction: inbound
produces: [journal, try-failed-exp, codex]
---

# What I do
Run `scripts/git-events.sh` to get structured commits. Classify each:
- Deploys, reverts, tag-bumps → candidate journal records
- Commits reverting previous commits within <24h → candidate try-failed-exp
- Merge commits linking to RFC/ADR issues → candidate codex references

# Output
A list of candidate records, each a complete frontmatter-ready blob.
User (via harvest) confirms or discards each.
```

**Outbound (`to-*`):** read `.lore/` and produce external artifacts.

```markdown
---
name: to-keep-a-changelog
type: adapter
direction: outbound
consumes: [release-notes, api-changelog]
---

# What I produce
A CHANGELOG.md at repo root conforming to keepachangelog.com 1.1.0.

# Mapping
- `release-notes` entries grouped by version → `## [X.Y.Z] - YYYY-MM-DD`
- `api-changelog` entries with `breaking: true` → `### Changed` + BREAKING CHANGE
- Superseded release-notes (superseded_by set) → excluded
```

### 3.7 Meta-skills — the glue

Six of them, each tightly scoped.

| Meta-skill | What it does |
|-----------|--------------|
| `detect` | On first run (and on demand), scan the user's project (package.json, Dockerfile, workflows, `docs/adr/`, etc.) and suggest which archetypes + profiles to enable. Writes `.lore/config.yaml`. |
| `link` | Scan all `.lore/**/*.md` for prose cross-refs (`[[...]]`) and implied refs (e.g., two records naming the same feature). Suggest structured `refs:` entries. |
| `harvest` | Orchestrate inbound adapters. "Scan last 6 months of git + last quarter's GitHub releases + open issues tagged `decision`. Produce candidate records. User confirms in batches." The zero-to-one skill. |
| `promote` | The **cooling-pipeline operator**. Scan live-tier for recurring patterns → suggest canon records. Scan archive (postmortems, retros) for lessons → suggest codex or try-failed-exp entries. Move records between tiers with user confirmation. |
| `audit` | Cross-file consistency: tier-in-dir matches tier-in-frontmatter; every `supersedes` has a matching `superseded_by`; every `[[ref]]` resolves; no orphan files. Read-only; reports. |
| `migrate` | One-shot: ingest an existing `docs/adr/`, `CHANGELOG.md`, or postmortem folder into `.lore/` structure. Users run this once when adopting lore. |

---

## 4. Installation architecture and user experience

Lore's distribution model matches Superpowers exactly. The rationale: Superpowers already solved the hard parts (marketplace listing, multi-platform install, zero-config activation, session-start priming). Lore reuses the pattern rather than reinventing it.

### 4.1 Plugin skeleton — top-level layout

```
lore.skill/                         ← repo root, also the plugin root
├── package.json                    ← plugin manifest (Node-style, matches Superpowers)
├── README.md                       ← install instructions prominent up top (one section per platform)
├── CLAUDE.md                       ← auto-loaded by Claude Code; high-level "what is lore"
├── AGENTS.md                       ← auto-loaded by OpenCode
├── GEMINI.md                       ← auto-loaded by Gemini CLI
├── gemini-extension.json           ← Gemini extension manifest
├── CHANGELOG.md                    ← dogfooded from our own `to-keep-a-changelog`
├── RELEASE-NOTES.md                ← human-readable per-version notes
├── LICENSE
├── CODE_OF_CONDUCT.md
│
├── .claude-plugin/                 ← Claude Code plugin manifest
├── .cursor-plugin/                 ← Cursor plugin manifest
├── .codex/                         ← Codex install shim (INSTALL.md + any helper)
├── .opencode/                      ← OpenCode install shim (INSTALL.md + plugin JS)
│
├── hooks/                          ← Claude Code hooks
│   ├── hooks.json                  ← registers SessionStart hook
│   ├── hooks-cursor.json           ← Cursor-specific hook config
│   ├── run-hook.cmd                ← single cmd dispatcher (shell wrapper)
│   └── session-start               ← the session-start handler (primes using-lore skill)
│
├── skills/                         ← the 34 SKILL.md files (see §2.2)
├── commands/                       ← slash-command thin wrappers (optional; prefer skill-based)
├── agents/                         ← subagent definitions (if any)
├── scripts/                        ← Layer-0 helpers (new-id.sh, validate.py, git-events.sh)
├── docs/                           ← in-depth docs + the charter + per-archetype specs
└── tests/                          ← integration tests
```

The six platform dotdirs (`.claude-plugin/`, `.cursor-plugin/`, `.codex/`, `.opencode/`, plus `gemini-extension.json` at root and `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` primer files) are the **platform shim layer**. Each contains only what that platform needs to discover and load the shared `skills/` tree — they are ~10–50 lines apiece. All real content lives in `skills/` and is platform-agnostic markdown.

### 4.2 Distribution — one line per platform

Matches Superpowers exactly. README's install section lists each:

| Platform | Install command |
|----------|-----------------|
| **Claude Code (official marketplace)** | `/plugin install lore@claude-plugins-official` |
| **Claude Code (community)** | `/plugin marketplace add host452b/lore-marketplace` then `/plugin install lore@lore-marketplace` |
| **Cursor** | `/add-plugin lore` (search "lore" in plugin marketplace) |
| **Codex** | "Fetch and follow instructions from `https://raw.githubusercontent.com/host452b/lore.skill/main/.codex/INSTALL.md`" |
| **OpenCode** | "Fetch and follow instructions from `https://raw.githubusercontent.com/host452b/lore.skill/main/.opencode/INSTALL.md`" |
| **Gemini CLI** | `gemini-extension.json` at repo root → install via Gemini's extension mechanism |

v0.1 ships with Claude Code + Cursor working (marketplaces). v0.2 adds the `.codex/` and `.opencode/` INSTALL.md shims. v1.0 has all five platforms first-class.

### 4.3 Session-start hook — priming the intro skill

Following Superpowers' model, a `SessionStart` hook fires on session startup/clear/compact and runs a single script that injects a short primer reminding Claude that lore exists and how to invoke it. The primer is the `using-lore` skill's content.

```json
// hooks/hooks.json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          { "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false }
        ]
      }
    ]
  }
}
```

The `using-lore` skill is the analog of `using-superpowers`: it tells Claude that skills like `lore:journal`, `lore:codex`, `lore:try-failed-exp` exist, when to invoke them, and how to find the rest. Without this hook, skills are discoverable but not actively brought into mind at session start.

### 4.4 Zero-config UX

Design target — the experience mirrors Superpowers:

1. User runs `/plugin install lore@...`.
2. First new session: `SessionStart` hook fires → `using-lore` skill content loaded → Claude knows the vocabulary (timeline, checkpoint, recall, lore, legacy) and the archetypes.
3. User (or Claude, proactively) can immediately invoke any skill: `/lore:try-failed-exp`, `/lore:harvest`, etc.
4. On first invocation of any write-producing skill, lore checks for `.lore/` in the project root; if absent, runs `lore:detect` → suggests a starter set → creates `.lore/` with the right subdirs.
5. No config file is required to start writing. `.lore/config.yaml` is optional and only appears if the user customizes detect's suggestions.

**Uninstall is clean:** `/plugin uninstall lore` removes the plugin; the user's `.lore/` directory stays in their repo (it's their data, not the plugin's).

### 4.5 Versioning and release

- Semantic versioning (MAJOR.MINOR.PATCH).
- `CHANGELOG.md` maintained by our own `to-keep-a-changelog` adapter — dogfooding from v0.2 forward.
- `package.json` version is the source of truth.
- `scripts/bump-version.sh` (modeled on Superpowers') handles the version bump + tag + release-notes generation.
- Release artifacts: a GitHub Release per tag. Marketplaces pick up the release automatically (Claude Code) or require a manual sync (Cursor/OpenCode).

### 4.6 Skill naming convention

All user-invocable skills are namespaced `lore:<skill-name>` at invocation time. Internally:

- Archetypes: `lore:journal`, `lore:codex`, `lore:try-failed-exp`, etc.
- Adapters: `lore:from-git-log`, `lore:to-keep-a-changelog`
- Meta: `lore:detect`, `lore:harvest`, `lore:promote`, `lore:link`, `lore:audit`, `lore:migrate`
- Compliance: `lore:semver`, `lore:keep-a-changelog`, etc.
- Layer-0 `core` is non-invocable; no `lore:core` slash-command exists.

Skill descriptions (frontmatter `description:`) follow Superpowers' trigger-oriented style: "Use when [situation] — [what it does]." This drives automatic invocation by Claude.

### 4.7 Platform-adapter boundaries (non-goals)

Lore's multi-platform story is **install-level portability**, not content-level portability:

- All SKILL.md content is shared across platforms.
- Platform differences are absorbed in the dotdirs (`.codex/`, `.opencode/`, etc.) and the platform-specific primer files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`).
- If a platform lacks a primitive lore depends on (e.g., no slash-commands), that platform's adapter documents the workaround ("tell the agent to invoke `lore:journal` by name").
- Lore does not maintain separate skill codepaths per platform.

---

## 5. Roadmap, risks, and spec sequencing

### 5.1 Versioning

| Version | Scope | What it proves |
|--------:|-------|----------------|
| **v0.1** | Core + journal(web-service, ml-experiment) + codex(adr, design-doc) + try-failed-exp(rejected-adr, spike-outcome) + from-git-log + to-keep-a-changelog + harvest + detect + **install infrastructure**: `package.json`, `.claude-plugin/`, `.cursor-plugin/`, `CLAUDE.md` primer, `hooks/` (session-start), `using-lore` skill, marketplace listings for Claude Code and Cursor | 3-axe MVP ships end-to-end; one-line install works on Claude Code + Cursor; `harvest` defeats the empty-state problem. |
| **v0.2** | + postmortem + migration-guide + compliance/semver + compliance/keep-a-changelog + `promote` + `.codex/` and `.opencode/` install shims | The cooling pipeline becomes real; install footprint extends to Codex + OpenCode. |
| **v0.3** | + api-changelog + intent-log + more profiles (rfc, library-eval, perf-dead-end, rest-api) + from-sentry, from-mlflow + `gemini-extension.json` + `GEMINI.md` | Covers common software-team archetype set; install footprint extends to Gemini CLI. |
| **v1.0** | All 11 archetypes + all 6 meta-skills + core compliance set + main adapters + all 5 platforms first-class | Full suite, full install footprint. |

### 5.2 Spec sequencing (this document is Spec 0 — the charter)

| Spec | Name | What it pins |
|-----:|------|--------------|
| **0** | **lore charter** (this doc) | Architecture, 5 layers, tier model, vocabulary, roadmap, layer contracts |
| 1 | lore:core details | Frontmatter schema file, id-scheme.md, cross-ref-grammar.md, tier-model.md, 3 scripts |
| 2 | lore:try-failed-exp | Headline archetype SKILL.md, 2 profiles (rejected-adr, spike-outcome), examples |
| 3 | lore:journal | Archetype SKILL.md, 2 profiles (web-service, ml-experiment) |
| 4 | lore:codex | Archetype SKILL.md, 2 profiles (adr, design-doc) |
| 5 | lore:adapters-mvp | from-git-log + to-keep-a-changelog |
| 6 | lore:meta-mvp | harvest + detect |
| 7 | lore:promote | The cooling-pipeline operator (kicks off v0.2) |

Each spec gets its own implementation plan via the `writing-plans` skill. Each plan is executed as its own branch/PR.

### 5.3 Open questions / deferred decisions

The charter pins architecture; it intentionally defers:

- **Exact field sets per archetype** — pinned per-archetype in Specs 2–4.
- **Profile YAML schema finalization** — needs 2+ archetypes to validate generality. v0.1 schema is provisional; frozen in v0.2.
- **Compliance coupling mechanism** — textual `hooks-into` in frontmatter is the v0.1 contract; revisit if it gets messy.
- **Platform portability** (Codex / Gemini CLI) — deferred past v1.0.
- **Search/indexing of `.lore/`** — rely on `grep`/`ripgrep` for now; revisit if `.lore/` grows past ~1000 records in real projects.
- **Visibility / access control** (public / internal / private records) — not in v1.0; add a `visibility:` frontmatter field later.
- **Tier demotion** (cold → hot) — `promote` only goes cold-ward in v0.1–v0.2; hot-ward is user-driven only.

### 5.4 Success criteria (charter-level)

- **Install UX:** A user on Claude Code or Cursor can go from "never heard of lore" to "wrote my first try-failed-exp" in a single session — install is one line, session-start hook primes the skill, no config file required.
- A user installing lore on an existing project can run `/lore:harvest` and produce ≥10 candidate records in under 10 minutes.
- A user adopting lore from scratch can write their first `try-failed-exp` in under 2 minutes.
- Cross-refs and tier transitions stay internally consistent across ≥3 archetypes by v0.1 (proves `core`).
- `to-keep-a-changelog` output passes the community linter.
- Any engineer reading the README grasps the **cooling pipeline** thesis in under 2 minutes.

### 5.5 Risks & mitigations

| Risk | Mitigation |
|------|-----------|
| 34 skills dilute discoverability. | `detect` picks a 4–6 skill starter set based on project type. Docs emphasize "you only need 3 skills to start." |
| `promote` never runs → no cooling pipeline → lore is just a log tool. | Periodic reminders when live-tier grows; `harvest` invokes `promote` by default. |
| Archetype boundaries blur in practice. | Strong boundary sections in every SKILL.md; `audit` flags misplaced records; `promote` can relocate. |
| Profile YAML becomes a programming language. | Cap v0.1 profile schema at fields/prompts/templates/detect-hints. Escape hatch: markdown "advanced rules" file for complex logic. |
| `.lore/` bloat — thousands of files in git. | Year-bucket `archive/`; compress-on-supersede policy for canon (keep superseded file but mark archive). |
| Compliance/adapter sprawl. | Profile YAML + adapter SKILL.md are the only extension points. Reject runtime plugin systems. |
| Vocabulary dilution — "lore" becomes generic. | Pin the terms: timeline, checkpoint, recall, lore, legacy. Glossary in `core/`. README enforces consistent usage. |

---

## Appendix A — Glossary

| Term | Definition |
|------|-----------|
| **archetype** | One of 11 record types. Each has its own SKILL.md and lives in `skills/<name>/`. |
| **canon / 典** | Tier 3. Records that are reread, revised, and cited — the project's "constitution." |
| **checkpoint** | The act of writing a lore record. |
| **compliance overlay** | A skill that audits records produced by archetypes; does not write records itself. |
| **cooling pipeline** | The flow live → archive → canon. Lore's thesis: most value is in the transitions. |
| **cross-ref** | The `[[archetype:id]]` grammar linking records. |
| **legacy** | The long-horizon accumulation of a project's lore. |
| **live / 流** | Tier 1. High-churn, append-only event signal. |
| **lore (product)** | This plugin suite. |
| **lore (concept)** | The canonical, reusable wisdom a project accrues — the canon-tier output. |
| **archive / 档** | Tier 2. Crystallized one-time retrospection (postmortems, retros, release notes). |
| **profile** | A YAML file extending an archetype's fields and template for a specific sub-domain. |
| **recall** | The retrieval motion — finding relevant records by cross-ref, grep, or index. |
| **timeline** | The medium — lore's records are ordered events, and tiers are phases on that line. |

## Appendix B — Terminology mapping (historical)

| Was called | Now called | Reason |
|-----------|-----------|--------|
| `chronicle` (project) | `lore` | Name the destination (canon), not the timeline. |
| `dead-ends` (archetype) | `try-failed-exp` | Clearer on its purpose: logs *attempted experiments that failed*. |
| `try-failed-log.skill` (repo dir) | `lore.skill` (rename pending) | Match the project name. |
| `_core` | `core` | `.lore/`-style hidden dirs are for user data; plugin internals don't need the underscore. |
