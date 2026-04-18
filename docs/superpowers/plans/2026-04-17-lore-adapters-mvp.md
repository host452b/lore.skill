# Lore — Adapters MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `from-git-log` inbound adapter (Layer-3) and `lore:harvest` meta-skill (Layer-4). No changes to `validate.py`. Six new files, one `.gitignore` edit.

**Architecture:** `scripts/from-git-log.py` shells out to `git-events.sh`, classifies commits via `classify()`, and writes draft `.md` files to `.lore/.harvest/`. Two new profiles (`git-commit` for journal, `revert-commit` for try-failed-exp) support auto-generated drafts with minimal required fields. `skills/harvest/SKILL.md` describes the batch-review UX.

**Tech Stack:** Python 3.9+, PyYAML already installed, pytest already wired. No new dependencies.

**Spec reference:** `docs/superpowers/specs/2026-04-17-lore-adapters-mvp-design.md`

---

## File Structure

Files created:
- `scripts/from-git-log.py` — adapter script (~120 LOC)
- `skills/journal/profiles/git-commit.yaml` — minimal harvest profile
- `skills/try-failed-exp/profiles/revert-commit.yaml` — revert-commit profile
- `skills/harvest/SKILL.md` — harvest meta-skill
- `.lore/.harvest/.gitkeep` — directory anchor
- `tests/scripts/test_from_git_log.py` — 17 pytest tests

Files modified:
- `.gitignore` — add `.lore/.harvest/*.md` entry

**Total: 6 new files, 1 modified.**

---

## Pre-task setup

- Main has Specs 1+2+3+4 (all merged).
- `scripts/git-events.sh` exists and emits JSON lines with `is_revert`, `tags`, `subject`, `date`, `sha`, `email`.
- `skills/journal/profiles/web-service.yaml` exists (reference for git-commit profile design).
- `skills/try-failed-exp/profiles/rejected-adr.yaml` exists (reference for revert-commit profile design).
- `.venv/` has pytest + PyYAML.

---

### Task 1: New profiles

Create the two new profile YAML files that support auto-generated drafts.

- [ ] **Step 1.1: Create `skills/journal/profiles/git-commit.yaml`**

```yaml
name: git-commit
extends: journal
description: Journal entry auto-generated from a git commit during harvest.
  Minimal required fields — no event-type or environment required.
  Upgrade to the web-service profile post-harvest to add those constraints.

# No fields: block — accepts any values for optional fields.
# The archetype-level requirements (event-time, outcome, profile) still apply.

# No required_sections — journal body is free-form narrative.
```

- [ ] **Step 1.2: Create `skills/try-failed-exp/profiles/revert-commit.yaml`**

```yaml
name: revert-commit
extends: try-failed-exp
description: A try-failed-exp entry auto-generated from a git revert commit.
  Captures what was attempted and immediately rolled back.

required_sections:
  - "## What was reverted"
  - "## Why reverted"
  # Note: "## Don't retry unless" is enforced at the archetype level.
```

---

### Task 2: `scripts/from-git-log.py`

Core adapter script. Shells out to `git-events.sh`, classifies, writes drafts.

- [ ] **Step 2.1: Write `scripts/from-git-log.py`**

Full implementation — see spec §2 for interface spec. Key functions:

```python
DEPLOY_RE = re.compile(r'\b(deploy|release|hotfix|rollout|ship|publish|cut)\b', re.IGNORECASE)

def classify(event: dict) -> str | None:
    if event.get("is_revert"):
        return "try-failed-exp"
    if event.get("tags"):
        return "journal"
    if DEPLOY_RE.search(event.get("subject", "")):
        return "journal"
    return None

def make_slug(subject: str) -> str:
    # strip Revert prefix and quotes, lowercase, non-alnum→hyphen, truncate to 50

def draft_journal(event: dict) -> str:
    # returns full frontmatter + body string, profile=git-commit

def draft_tfe(event: dict) -> str:
    # returns full frontmatter + body with 3 required sections, profile=revert-commit

def stream_events(script_path, since, repo) -> Iterator[dict]:
    # shells out to git-events.sh, yields JSON dicts

def main(argv=None) -> int:
    # argparse: --since, --last, --out, --dry-run, --repo
    # dedup by record_id; write or print per --dry-run
```

---

### Task 3: `skills/harvest/SKILL.md`

Meta-skill describing the batch-review workflow.

- [ ] **Step 3.1: Create `skills/harvest/` directory and write `SKILL.md`**

Sections to include (from spec §6):
- Frontmatter: `name`, `description`, `type: meta`, `layer: 4`
- When to use / When NOT to use
- How to run a harvest session (4 steps: stage, review summary, process each, commit)
- Draft format explanation
- Signals worth promoting vs. skipping
- How to retrieve past harvest records (grep before running)

---

### Task 4: `.lore/.harvest/` and `.gitignore`

- [ ] **Step 4.1: Create `.lore/.harvest/.gitkeep`**

Empty file to anchor the directory in git.

- [ ] **Step 4.2: Update `.gitignore`**

Add at the end:
```
# Lore harvest staging area (ephemeral drafts — never committed)
.lore/.harvest/*.md
```

---

### Task 5: Tests

- [ ] **Step 5.1: Write `tests/scripts/test_from_git_log.py`**

17 tests covering: `classify`, `make_slug`, `draft_journal`, `draft_tfe`, CLI `--dry-run`, CLI `--out` creates directory.

Import style: `sys.path.insert(0, str(REPO_ROOT / "scripts"))` then `from from_git_log import classify, make_slug, draft_journal, draft_tfe`.

Note: the script file is `from-git-log.py` but Python imports use `from_git_log` (hyphen → underscore is not automatic). To import, either rename or use `importlib`. Use `importlib.util.spec_from_file_location` pattern to load `from-git-log.py` directly.

- [ ] **Step 5.2: Run tests**

```bash
cd /path/to/repo && .venv/bin/pytest tests/scripts/test_from_git_log.py -v
```

All 17 tests must pass.

---

### Task 6: Commit

- [ ] **Step 6.1: Stage and commit**

```bash
git add scripts/from-git-log.py \
        skills/journal/profiles/git-commit.yaml \
        skills/try-failed-exp/profiles/revert-commit.yaml \
        skills/harvest/SKILL.md \
        .lore/.harvest/.gitkeep \
        tests/scripts/test_from_git_log.py \
        .gitignore \
        docs/superpowers/specs/2026-04-17-lore-adapters-mvp-design.md \
        docs/superpowers/plans/2026-04-17-lore-adapters-mvp.md
git commit -m "feat(adapters): from-git-log adapter + harvest meta-skill (Spec 5)"
```
