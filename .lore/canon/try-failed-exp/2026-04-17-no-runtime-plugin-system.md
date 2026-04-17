---
id: 2026-04-17-no-runtime-plugin-system
type: try-failed-exp
tier: canon
date: 2026-04-17
title: Runtime plugin system for lore extensions (rejected)
authors: ["Joe Jiang <joejiang@nvidia.com>"]
profile: rejected-adr
status: rejected
tags: ["architecture", "extensibility"]
---

# Runtime plugin system for lore extensions (rejected)

## What was considered

Instead of YAML profiles + markdown SKILL.md as the sole extension
points, let third parties register runtime plugins (Python or JS
modules) that could hook into archetype writes, mutate records, or
add new archetypes at load time.

## Why it was rejected

- Moves the extension surface from "edit a YAML file" (non-programmer
  friendly) to "ship a Python package" (programmer-only).
- Introduces a versioning nightmare: runtime plugins depending on
  internal APIs that would change as the suite evolves.
- Breaks the Superpowers-style ethos of markdown-first, LLM-native.
- YAML profiles + a markdown "advanced rules" escape hatch cover ≥95%
  of the extension cases we can anticipate.

## What was chosen instead

- Profiles as YAML files under `skills/<archetype>/profiles/`.
- Advanced-rules markdown files referenced from a profile when a
  profile genuinely needs logic beyond declarative fields.
- Compliance overlays, adapters, and meta-skills as additional
  SKILL.md files — no plugin registry, no runtime loading.

## Don't retry unless

Someone demonstrates that:
1. A real extension use case is blocked by the YAML + markdown
   approach, AND
2. The proposed runtime plugin API has a realistic versioning /
   sandboxing story.
