# Lore — Adapters MVP Design

| Field | Value |
|-------|-------|
| **Status** | Draft |
| **Date** | 2026-04-17 |
| **Type** | Spec 5 — adapters layer + harvest meta-skill |
| **Scope** | `from-git-log` adapter (Layer-3) + `lore:harvest` meta-skill (Layer-4), v0.1 |
| **Author** | host452b |
| **Depends on** | Spec 0 (charter), Spec 1 (substrate), Spec 2 (try-failed-exp), Spec 3 (journal) |
| **Defers** | `to-keep-a-changelog` outbound adapter (v0.2+); `postmortem`/`retro` harvest candidates (v0.2+) |

---

## 0. Executive summary

Spec 5 closes the inbound half of the cooling pipeline: git history →
candidate lore records. It ships two components:

1. **`scripts/from-git-log.py`** (Layer-3) — reads `git-events.sh` JSON
   output, classifies commits into `journal` (deploy/release) or
   `try-failed-exp` (revert) candidates, writes draft `.md` files to
   `.lore/.harvest/`.

2. **`skills/harvest/SKILL.md`** (Layer-4) — the meta-skill that invokes the
   adapter, presents a numbered batch to the user, and guides
   approve/edit/skip for each draft.

Scope decision: only the inbound `from-git-log` adapter ships in v0.1.
The outbound `to-keep-a-changelog` adapter (git history → CHANGELOG.md)
defers to v0.2, because it depends on `release-notes` and `api-changelog`
archetypes not yet shipped.

Harvest is **intentionally not autonomous**. The adapter produces structured
drafts; the human confirms, edits, or discards each one. Lore does not
write canon records behind your back.

---

## 1. Purpose and scope

### 1.1 The gap

Specs 1-4 gave lore structured record types and a validator. But they
assumed the user writes records by hand. Real projects have years of git
history. `from-git-log` bridges that gap: it turns a signal already
present in every repo (git commits) into lore draft candidates.

### 1.2 What the adapter does and doesn't do

**Does:**
- Read `git-events.sh` JSON output for a date range or commit window.
- Classify each commit as `journal`, `try-failed-exp`, or skip.
- Write a draft `.md` file to `.lore/.harvest/` with auto-populated
  frontmatter and template body.
- Print a summary list of staged files.

**Does not:**
- Write to `.lore/live/` or `.lore/canon/` directly. Only `.lore/.harvest/`.
- Validate the draft (drafts are pre-valid starters, not finished records).
- Make decisions about which events matter — that's the human's job.

### 1.3 Two record types (v0.1)

| Git signal | lore archetype | tier | rationale |
|------------|---------------|------|-----------|
| Deploy/release keyword in subject | `journal` | live | Every deploy is a timestamped event worth recording |
| Git tag present | `journal` | live | Tags mark releases explicitly |
| `is_revert: true` | `try-failed-exp` | canon | A revert = something was tried and immediately rolled back |

Revert commits are the clearest semantic signal in git history: something
was attempted, it didn't work, and it was undone. They map directly to the
`try-failed-exp` archetype's thesis — and they're where the "lore captures
things that failed" value proposition is most obviously demonstrated.

---

## 2. `scripts/from-git-log.py`

### 2.1 Layer and placement

Layer-3 (adapter). Sits alongside `validate.py` in `scripts/`. Both are
Python 3 scripts; no new dependencies.

### 2.2 Interface

```
python3 scripts/from-git-log.py [--since DATE] [--last N]
                                 [--out DIR] [--dry-run]
                                 [--repo DIR]
```

| Flag | Meaning |
|------|---------|
| `--since DATE` | Git date spec passed to `git-events.sh` (e.g. `"2 weeks ago"`, `2026-04-01`) |
| `--last N` | Stop after staging N candidates |
| `--out DIR` | Output directory (default: `.lore/.harvest` relative to `--repo`) |
| `--dry-run` | Print what would be created; write nothing |
| `--repo DIR` | Repo root to mine (default: `.`) |

### 2.3 Implementation

The script shells out to `git-events.sh` (located at
`<plugin-root>/scripts/git-events.sh`) and reads its newline-delimited
JSON output. For each event it calls `classify()`, then one of
`draft_journal()` or `draft_tfe()`.

Duplicate ID protection: if two commits produce the same slug+date, only
the first is staged (later commits with identical dates and subjects are
skipped).

---

## 3. Classification rules

```python
def classify(event: dict) -> str | None:
    if event.get("is_revert"):
        return "try-failed-exp"
    if event.get("tags"):
        return "journal"
    if DEPLOY_RE.search(event.get("subject", "")):
        return "journal"
    return None
```

`DEPLOY_RE = re.compile(r'\b(deploy|release|hotfix|rollout|ship|publish|cut)\b', re.IGNORECASE)`

Reverts take priority: a commit that reverts a deploy is `try-failed-exp`,
not `journal`. The order in `classify()` encodes this.

---

## 4. Draft file format

### 4.1 Journal draft

Pre-populated fields:

| Field | Source |
|-------|--------|
| `id` | `YYYY-MM-DD-<slug>` derived from commit date + subject |
| `type` | `journal` |
| `tier` | `live` |
| `date` | Commit date (YYYY-MM-DD) |
| `title` | Commit subject |
| `authors` | Commit author email (list) |
| `profile` | `git-commit` |
| `event-time` | Commit ISO 8601 date |
| `outcome` | `observed` (placeholder — user may change) |

Profile: `git-commit` (new, minimal). Requires only the archetype-level
fields (`event-time`, `outcome`, `profile`). No `event-type` or
`environment` required. User upgrades to `web-service` profile post-harvest
if they want those fields enforced.

Body: free-form `## What happened` section with a `<!-- Commit: sha -->` anchor
and TODO prompt.

### 4.2 try-failed-exp draft

Pre-populated fields:

| Field | Source |
|-------|--------|
| `id` | `YYYY-MM-DD-<slug>` (revert prefix stripped from subject) |
| `type` | `try-failed-exp` |
| `tier` | `canon` |
| `date` | Commit date (YYYY-MM-DD) |
| `title` | Commit subject |
| `authors` | Commit author email (list) |
| `profile` | `revert-commit` |
| `status` | `on-hold` (reflects "quickly reverted; reason not yet analyzed") |

Profile: `revert-commit` (new). Required sections: `## What was reverted`,
`## Why reverted`. The archetype-level `## Don't retry unless` is always
required regardless of profile.

Body: all three required sections pre-populated with TODO placeholder lines
(placeholder lines count as content for the validator — draft is structurally
valid once generated; body content must be replaced before promoting).

---

## 5. New profiles

### 5.1 `skills/journal/profiles/git-commit.yaml`

Minimal journal profile for auto-harvested events. No `fields:` block
(no required `event-type` or `environment`). Intended as a staging
profile — users upgrade to `web-service` for events worth full validation.

### 5.2 `skills/try-failed-exp/profiles/revert-commit.yaml`

Profile for auto-harvested revert commits. Required sections:
`## What was reverted`, `## Why reverted`. The archetype-level
`## Don't retry unless` is mandatory regardless of profile.

---

## 6. `skills/harvest/SKILL.md`

Layer-4 meta-skill. Governs the batch-review UX.

Workflow the skill describes:

1. Stage candidates: `python3 scripts/from-git-log.py --since "2 weeks ago"`
2. Review printed summary (adapter output).
3. For each draft in `.lore/.harvest/`:
   - **Approve**: fill in TODOs → move to `.lore/live/journal/` or
     `.lore/canon/try-failed-exp/` → `python3 scripts/validate.py <path>`.
   - **Edit**: change profile, fix fields, rewrite body.
   - **Skip**: delete the draft.
4. Commit approved records. `.lore/.harvest/` is gitignored.

The skill also describes:
- When to run harvest (post-release retro, onboarding backfill, periodic sync).
- Which events are worth promoting vs. skipping (judgment guidance).
- How to check for existing records before running (avoid duplicates).

---

## 7. `.lore/.harvest/` layout

```
.lore/.harvest/
  .gitkeep              # tracks the directory; drafts are gitignored
  2026-04-17-deploy-api-v2.md
  2026-04-16-revert-redis-cluster.md
  ...
```

`.gitignore` entry: `.lore/.harvest/*.md` (ignore drafts, keep `.gitkeep`).

Drafts are ephemeral. They are written by `from-git-log.py` and consumed
(promoted or deleted) during a harvest session. They are never committed.

---

## 8. File inventory

New files:

| Path | Layer | Purpose |
|------|-------|---------|
| `scripts/from-git-log.py` | 0/3 | Adapter script |
| `skills/journal/profiles/git-commit.yaml` | 1 | Minimal harvest profile |
| `skills/try-failed-exp/profiles/revert-commit.yaml` | 1 | Revert-commit harvest profile |
| `skills/harvest/SKILL.md` | 4 | Harvest meta-skill |
| `.lore/.harvest/.gitkeep` | — | Directory anchor |
| `tests/scripts/test_from_git_log.py` | — | Pytest tests for adapter |

Modified files:

| Path | Change |
|------|--------|
| `.gitignore` | Add `.lore/.harvest/*.md` entry |

**Total: 6 new files, 1 modified.**

No changes to `scripts/validate.py`. Drafts in `.lore/.harvest/` are not
subject to validation; validation runs only when the user promotes a draft
to `.lore/live/` or `.lore/canon/`.

---

## 9. Test plan

### 9.1 pytest (`tests/scripts/test_from_git_log.py`)

| Test | What it checks |
|------|----------------|
| `test_revert_is_tfe` | `is_revert: true` → `try-failed-exp` |
| `test_deploy_subject_is_journal` | "deploy api v2" → `journal` |
| `test_release_tag_is_journal` | non-empty `tags` → `journal` |
| `test_hotfix_subject_is_journal` | "hotfix: fix auth" → `journal` |
| `test_unrelated_commit_is_skipped` | "chore: update README" → `None` |
| `test_revert_takes_priority_over_deploy` | revert of deploy → `try-failed-exp` |
| `test_slug_basic` | "deploy api v2" → "deploy-api-v2" |
| `test_slug_strips_revert_prefix` | `Revert "redis cluster"` → no leading "revert" |
| `test_slug_truncates` | >50 chars → ≤50 chars |
| `test_slug_no_leading_trailing_hyphens` | strips edge hyphens |
| `test_journal_draft_required_frontmatter` | all required fields present |
| `test_journal_draft_id_starts_with_date` | id has correct date prefix |
| `test_journal_draft_sha_in_body` | commit sha comment present |
| `test_tfe_draft_required_frontmatter` | all required fields present |
| `test_tfe_draft_required_body_sections` | three required sections present |
| `test_dry_run_writes_no_files` | `--dry-run` → no files in tmpdir |
| `test_out_dir_created` | output directory created on run |

### 9.2 Manual validation

Run `python3 scripts/validate.py` on a promoted TFE draft (with TODOs
replaced) and confirm `OK:`. Journal drafts are not validate-clean until
the user upgrades the profile to `web-service` (adding `event-type` +
`environment`), which is by design.
