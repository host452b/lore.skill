# Lore

**Turn your project's lived history into structured, cross-referenced, git-tracked memory.**

`timeline` · `checkpoint` · `recall` · `lore` · `legacy`

Lore is a Claude Code / Cursor plugin. Its skills capture deploys, experiments, decisions, failed attempts, incidents, and releases as typed records under `.lore/`, then distill them into reusable project canon.

Its anchor skill — `lore:try-failed-exp` — gives every project a place to record the things that *didn't* work, so future engineers don't retry them blindly.

## The three-axe MVP (v0.1)

1. **`lore:journal`** — universal event stream (profiles: `web-service`, `ml-experiment`)
2. **`lore:codex`** — curated decisions & design (profiles: `adr`, `design-doc`)
3. **`lore:try-failed-exp`** — the differentiator: a map of attempts that failed

Plus: `lore:harvest` to bootstrap from git history, `lore:to-keep-a-changelog` to export CHANGELOG.md.

## Installation

### Claude Code (community marketplace)

```bash
/plugin marketplace add host452b/lore-marketplace
/plugin install lore@lore-marketplace
```

### Cursor

```text
/add-plugin lore
```

or search "lore" in the plugin marketplace.

### Other platforms

Codex, OpenCode, and Gemini CLI support land in v0.2–v0.3. See [charter §5.1](docs/superpowers/specs/2026-04-17-lore-charter-design.md) for the roadmap.

## First-session UX

1. Install the plugin.
2. Start a fresh session — the SessionStart hook injects the `using-lore` primer so the agent knows the vocabulary and archetypes.
3. Ask the agent to `lore:detect` — it scans your project and suggests a starter set.
4. Ask `lore:harvest` — it reads your git history and drafts candidate records for you to confirm.
5. Write your first `lore:try-failed-exp` or `lore:codex` by hand in under 2 minutes.

No config file is required to start.

## Where records live

```
<your-project>/
└── .lore/
    ├── live/     ← high-churn: journal, intent-log, dependency-ledger
    ├── archive/  ← one-time: postmortem, retro, release-notes
    └── canon/    ← reusable: codex, try-failed-exp, migration-guide
```

Git-tracked by default. Your lore ships with your repo.

## Design

The full architectural charter is at [`docs/superpowers/specs/2026-04-17-lore-charter-design.md`](docs/superpowers/specs/2026-04-17-lore-charter-design.md). It covers:

- The **cooling pipeline** thesis (the core idea: information flows live → archive → canon)
- All 11 archetype skills and when to use each
- The 5-layer architecture (core, archetypes, compliance, adapters, meta)
- The installation architecture (matches Superpowers)
- Roadmap v0.1 → v1.0

## License

MIT © Joe Jiang
