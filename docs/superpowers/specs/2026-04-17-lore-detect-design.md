# Lore — `detect` Meta-Skill Design

| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Date** | 2026-04-17 |
| **Type** | Spec 6 — detect meta-skill |
| **Scope** | `lore:detect` Layer-4 skill — first-run scan + ambient signal detection |
| **Author** | host452b |
| **Depends on** | Spec 0 (charter), Spec 1 (substrate), Specs 2-5 (archetypes + harvest) |
| **Defers** | Automated pattern scoring, ML-assisted signal detection (v0.3+) |

---

## 0. Executive summary

`lore:detect` is a Layer-4 meta-skill with two modes:

1. **First-run scan** — when `.lore/` is absent or empty, detect analyzes
   project structure and git history and recommends a starter kit.

2. **Ambient detection** — during normal conversation, detect watches for
   linguistic signals that indicate something worth recording has happened and
   makes a single, non-intrusive suggestion.

Detect is the entry point that turns "lore is installed" into "lore is
actively capturing." Without it, the agent waits for the user to invoke
`lore:journal` or `lore:try-failed-exp` explicitly. With it, the agent
notices on its own.

---

## 1. First-run scan

### 1.1 Trigger condition

`.lore/` directory does not exist in the project root, or exists but contains
no record files (only `.gitkeep`, `.harvest/`, etc.).

### 1.2 Scan targets

| Target | Command | What to infer |
|--------|---------|---------------|
| Git history | `bash scripts/git-events.sh --since "6 months ago"` | Count deploys, reverts, tagged releases |
| Existing docs | `find docs/ -name "*.md" \| head -30` | Presence of ADRs, design docs, architecture notes |
| Changelog | `ls CHANGELOG.md RELEASES.md HISTORY.md 2>/dev/null` | Existing release history |
| Package manifest | `cat package.json pyproject.toml setup.cfg 2>/dev/null` | Project name, version, stack |

### 1.3 Starter kit recommendations

| Signal | Recommendation |
|--------|---------------|
| Revert commits found | Run `lore:harvest` — TFE candidates already in git |
| Deploy/release commits found | Run `lore:harvest` — journal candidates already in git |
| Existing `docs/adr/` or `docs/decisions/` | Migrate key ADRs to `lore:codex` |
| Tagged releases | `lore:harvest --since <first-tag>` to backfill |
| Clean history, no notable events | Start fresh with one `lore:codex` for a current key decision |

### 1.4 Response format

```
Lore first-run scan — <project-name>

Found: N deploy commits, M revert commits, K tagged releases (last 6 months)
Existing docs: <yes/no ADRs found>

Recommended starter kit:
1. `lore:harvest --since "6 months ago"` → stages ~N+M candidates
2. <if ADRs found> Migrate top-3 ADRs to `lore:codex`

Want me to start with step 1?
```

---

## 2. Ambient detection

### 2.1 Signal → archetype table

| Signal phrase pattern | Suggested archetype |
|----------------------|---------------------|
| "tried X" / "attempted X" + negative outcome | `try-failed-exp` |
| "decided to" / "going with X" / "chose X over Y" | `codex` |
| "deployed" / "shipped" / "released" / "went live" | `journal` (deploy) |
| "rolled back" / "reverted to" | `journal` (rollback) + maybe `try-failed-exp` |
| "incident" / "outage" / "production is down" | `journal` (incident) |
| "didn't work" / "dead end" / "abandoned" + approach name | `try-failed-exp` |
| "evaluated X but" / "considered X but" | `try-failed-exp` |

### 2.2 Behavior rules

1. **Check canon first.** Before suggesting a new record, grep `.lore/canon/`
   for the topic. If an existing record covers it, surface it — don't create
   a duplicate.

2. **Ask once per session per topic.** If you suggested a TFE for "the Redis
   cluster experiment" earlier in this session, don't repeat.

3. **One suggestion at a time.** Don't fire multiple archetype suggestions at
   once. Pick the highest-signal one.

4. **Hold during debugging.** If the user is mid-error-fixing or mid-stack-trace,
   hold the suggestion until the immediate issue is resolved.

5. **Non-intrusive phrasing.** Side-note, not an interruption:
   - "This sounds like a `try-failed-exp` candidate — want me to draft one?"
   - "Worth a `lore:codex` entry for this decision?"

---

## 3. File inventory

| Path | Layer | Purpose |
|------|-------|---------|
| `skills/detect/SKILL.md` | 4 | Detect meta-skill |

No scripts, no validator changes, no tests. Pure skill content.

**Total: 1 new file.**
