---
name: detect
description: Use when a project has no .lore/ yet (first-run scan), or when
  the agent notices conversation signals suggesting a lore record should be
  created. Covers project bootstrapping and ambient signal detection.
type: meta
layer: 4
---

# What this skill does

`lore:detect` has two modes:

**First-run scan** — when `.lore/` is absent or empty, detect analyzes the
project and suggests a starter kit.

**Ambient detection** — during normal conversation, detect watches for signals
that something worth recording has happened, and makes a single non-intrusive
suggestion.

Detect is the entry point that makes lore active. Without it, the agent waits
for explicit invocation. With it, lore notices things on its own.

# First-run scan

## Trigger

`.lore/` does not exist, or exists but contains no record files (only
`.gitkeep`, `.harvest/`, etc.).

## What to scan

```bash
# Git history (last 6 months)
bash scripts/git-events.sh --since "6 months ago" | wc -l

# Existing decision docs
find docs/ -name "*.md" 2>/dev/null | head -30

# Changelog / release history
ls CHANGELOG.md RELEASES.md HISTORY.md 2>/dev/null

# Package manifest (project name + stack)
cat package.json pyproject.toml setup.cfg 2>/dev/null | head -20
```

## Starter kit logic

| Signal found | Recommendation |
|--------------|---------------|
| Revert commits | Run `lore:harvest` — TFE candidates in git |
| Deploy/release commits | Run `lore:harvest` — journal candidates in git |
| `docs/adr/` or `docs/decisions/` exist | Migrate key ADRs to `lore:codex` |
| Tagged releases | `python3 scripts/from-git-log.py --since <first-tag>` |
| Clean history | Start with one `lore:codex` for a current key decision |

## Response format

```
Lore first-run scan — <project-name>

Found: N deploy commits, M revert commits, K tagged releases (last 6 months).
<Existing ADR docs: yes/no>

Recommended starter kit:
1. lore:harvest — stages ~N+M candidates from git history
<2. Migrate top ADRs to lore:codex  (if ADRs found)>

Want me to start with step 1?
```

# Ambient detection

## Check canon before suggesting

Before suggesting a new record, always check whether lore already covers it:

```bash
grep -rli "<topic keywords>" .lore/canon/
```

If an existing record covers the topic, surface it instead of suggesting a
new one. Never silently re-propose something already in the canon.

## Signal → archetype table

| Signal in conversation | Suggested archetype |
|------------------------|---------------------|
| "tried X" / "attempted X" + negative outcome | `lore:try-failed-exp` |
| "decided to" / "going with X" / "chose X over Y" | `lore:codex` |
| "deployed" / "shipped" / "released" / "went live" | `lore:journal` (deploy) |
| "rolled back" / "reverted to previous" | `lore:journal` (rollback) + maybe `lore:try-failed-exp` |
| "incident" / "outage" / "production is down" | `lore:journal` (incident) |
| "didn't work" / "dead end" / "we abandoned" + approach name | `lore:try-failed-exp` |
| "evaluated X but" / "considered X but rejected" | `lore:try-failed-exp` |
| "we should always" / "the rule is" / "our convention is" | `lore:codex` |

## Behavior rules

1. **Ask once per session per topic.** If you already suggested a TFE for
   "the Redis cluster experiment" earlier in this session, don't repeat.

2. **One suggestion at a time.** Pick the highest-signal archetype; don't
   list all possibilities at once.

3. **Hold during debugging.** If the user is mid-error-fixing or reading a
   stack trace, hold the suggestion until the immediate issue is resolved.

4. **Non-intrusive phrasing.** Frame as a side-note:
   - "Sounds like a `lore:try-failed-exp` candidate — want me to draft one?"
   - "Worth a `lore:codex` entry for this decision?"
   - "This deploy sounds like a `lore:journal` entry — want me to create one?"

5. **Don't fabricate records.** Never create a lore record without explicit
   user confirmation. Suggest, don't act.

# When NOT to use me

- User explicitly asks to write a specific record type → use that archetype
  skill directly; detect is not needed as an intermediary.
- User is reviewing or editing existing `.lore/` records → use the relevant
  archetype skill or `lore:promote`.
- Subagent context (see `<SUBAGENT-STOP>` below).

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific coding task, skip
this skill. Detect is for agent–human dialogue, not automated pipelines.
</SUBAGENT-STOP>
