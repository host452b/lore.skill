# Claude Code guide — Lore plugin

You are working in the repo for the **lore** plugin — a Claude Code / Cursor plugin that turns a project's lived history (deploys, decisions, failed attempts, incidents, releases) into structured project memory.

## This repo is the plugin source

When Claude Code installs lore into a user's project, the files under `skills/`, `hooks/`, `scripts/`, `.claude-plugin/` are what get loaded. This repo's root is both the development repo and the plugin distribution.

## Key artifacts in this repo

- **Charter:** `docs/superpowers/specs/2026-04-17-lore-charter-design.md` — the architectural design for the full suite. Read this first when onboarding.
- **Per-spec plans:** `docs/superpowers/plans/*.md` — implementation plans per spec.
- **Skills:** `skills/<name>/SKILL.md` — each a separate lore skill.
- **Scripts:** `scripts/` — three Layer-0 helpers (`new-id.sh`, `validate.py`, `git-events.sh`).
- **Hooks:** `hooks/` — SessionStart hook that primes the `using-lore` skill each session.

## When working on this repo

- Each per-skill change should be tested (bats for shell, pytest for Python).
- The charter is the source of truth for architecture decisions. If a change diverges, update the charter first.
- Dogfood: this repo uses its own `to-keep-a-changelog` adapter for `CHANGELOG.md` (from v0.2 onward).

## When lore is installed in a *consuming* project

A session-start hook injects the `using-lore` skill content. That skill tells the agent about the 11 archetypes, the cooling pipeline, and when to proactively invoke `lore:<skill>` commands.
