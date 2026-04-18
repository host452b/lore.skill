# Lore — `detect` Meta-Skill Implementation Plan

**Goal:** Ship `lore:detect` — the first-run scan + ambient signal detection meta-skill. Pure SKILL.md, no scripts or validator changes.

**Spec reference:** `docs/superpowers/specs/2026-04-17-lore-detect-design.md`

---

## File Structure

Files created:
- `skills/detect/SKILL.md` — detect meta-skill

**Total: 1 new file.**

---

### Task 1: Write `skills/detect/SKILL.md`

- [ ] Create `skills/detect/` directory
- [ ] Write SKILL.md with frontmatter (`name`, `description`, `type: meta`, `layer: 4`)
- [ ] Section: What this skill does (two-mode intro)
- [ ] Section: First-run scan (trigger, scan targets, starter kit logic, response format)
- [ ] Section: Ambient detection (check canon first, signal table, 5 behavior rules)
- [ ] Section: When NOT to use me
- [ ] `<SUBAGENT-STOP>` guard

### Task 2: Commit

```bash
git add skills/detect/SKILL.md \
        docs/superpowers/specs/2026-04-17-lore-detect-design.md \
        docs/superpowers/plans/2026-04-17-lore-detect.md
git commit -m "feat(detect): first-run scan + ambient signal detection meta-skill (Spec 6)"
```
