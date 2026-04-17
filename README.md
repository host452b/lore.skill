# Lore

**Turn your project's lived history into structured, cross-referenced, git-tracked memory.**

`timeline` · `checkpoint` · `recall` · `lore` · `legacy`

Lore is a Claude Code / Cursor plugin that captures deploys, experiments, decisions, failed attempts, incidents, and releases as typed records, then distills them into reusable project canon. Its anchor skill — `lore:try-failed-exp` — gives every project a place to record the things that *didn't* work, so nobody tries them again.

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

(or search "lore" in the plugin marketplace)

More platforms (Codex, OpenCode, Gemini CLI) land in v0.2–v0.3.

## Design

See [`docs/superpowers/specs/2026-04-17-lore-charter-design.md`](docs/superpowers/specs/2026-04-17-lore-charter-design.md) for the architectural charter.
