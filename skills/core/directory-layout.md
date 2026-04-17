# Directory layout

Lore produces records in a git-tracked `.lore/` directory at the root of the consuming project. The layout is:

```
<user-project>/
├── .lore/
│   ├── live/                      ← tier: live
│   │   ├── journal/
│   │   │   ├── 2026-04-10-deploy-v1.3.2.md
│   │   │   └── 2026-04-12-mlflow-run-847.md
│   │   ├── intent-log/
│   │   └── dependency-ledger/
│   │
│   ├── archive/                   ← tier: archive (year-bucketed)
│   │   └── 2026/
│   │       ├── postmortem/
│   │       │   └── 2026-03-15-payment-outage.md
│   │       ├── retro/
│   │       │   └── 2026-Q1.md
│   │       └── release-notes/
│   │           └── v1.3.md
│   │
│   └── canon/                     ← tier: canon
│       ├── codex/
│       │   └── 2026-01-04-postgres-primary-db.md
│       ├── try-failed-exp/
│       │   └── 2026-02-20-rejected-redis-cluster.md
│       └── migration-guide/
│           └── 2026-02-01-v1-to-v2.md
```

## Rules

1. **Path = `.lore/<tier>/<archetype>/<id>.md`.** No further nesting.
2. **Archive is year-bucketed** (`.lore/archive/2026/...`); live and canon are flat.
3. **Filename = `<id>.md`.** The `audit` skill enforces this.
4. **Tier directory and `tier:` frontmatter must agree.** Enforced by `scripts/validate.py`.
5. **Archetype directory and `type:` frontmatter must agree.** Enforced by `audit`.

## `.lore/config.yaml` (optional)

If present, it records the archetypes and profiles enabled for this project. Created by the `detect` skill when the user customizes the suggested starter set.

```yaml
# .lore/config.yaml (example)
archetypes_enabled:
  - journal
  - codex
  - try-failed-exp
profiles:
  journal: [web-service]
  codex: [adr]
  try-failed-exp: [rejected-adr]
```

The config is a hint, not a hard enforcement — users can write records of any archetype regardless of the config. The config drives `detect`'s suggestions and `harvest`'s scope.

## Git tracking

`.lore/` is tracked by git by default. Teams that want it gitignored should add `.lore/` to their `.gitignore`. The out-of-the-box story is "your lore ships with your repo."

## What NOT to put in `.lore/`

- Secrets. Frontmatter is YAML; body is markdown — both are plain text. If you need to cite a secret (e.g., a leaked credential in a postmortem), reference it by name, not value.
- Large binaries. Lore records are short. Link to artifacts (S3, artifact registries) instead of embedding them.
- Generated files. `.lore/` is hand-curated (or harvested from git, never from generators with no signal).
