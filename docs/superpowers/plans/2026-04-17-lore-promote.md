# Lore — `promote` Meta-Skill Implementation Plan

**Goal:** Ship `lore:promote` — the cooling-pipeline operator meta-skill. Pure SKILL.md, no scripts or validator changes. Closes v0.1.

**Spec reference:** `docs/superpowers/specs/2026-04-17-lore-promote-design.md`

---

## File Structure

Files created:
- `skills/promote/SKILL.md` — promote meta-skill

Files modified:
- `skills/using-lore/SKILL.md` — update promote description (remove "v0.2" label)

**Total: 1 new file, 1 modified.**

---

### Task 1: Write `skills/promote/SKILL.md`

- [ ] Create `skills/promote/` directory
- [ ] Write SKILL.md with frontmatter (`name`, `description`, `type: meta`, `layer: 4`)
- [ ] Section: What this skill does (four promotion patterns)
- [ ] Section: When to use me / When NOT to use me
- [ ] Section: How to run a promote session (4 steps with grep commands)
- [ ] Section: Response format (numbered candidate list)
- [ ] Section: Promote is not autonomous

### Task 2: Update `using-lore`

- [ ] Remove "v0.2" label from `lore:promote` entry in the meta skills list
- [ ] Update description to match shipped scope

### Task 3: Commit

```bash
git add skills/promote/SKILL.md \
        skills/using-lore/SKILL.md \
        docs/superpowers/specs/2026-04-17-lore-promote-design.md \
        docs/superpowers/plans/2026-04-17-lore-promote.md
git commit -m "feat(promote): cooling-pipeline operator meta-skill (Spec 7) — closes v0.1"
```
