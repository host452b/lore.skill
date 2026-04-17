# Cross-ref grammar

Records reference each other using a compact, machine-parseable grammar:

```
[[<archetype>:<id>]]
```

Examples:
- `[[codex:2026-01-04-postgres-primary-db]]`
- `[[try-failed-exp:2026-02-20-rejected-redis-cluster]]`
- `[[journal:2026-04-10-deploy-v1.3.2]]`

## Where cross-refs appear

**In frontmatter (structured):**

```yaml
refs: ["[[codex:2026-01-04-postgres-primary-db]]"]
superseded_by: "[[codex:2026-05-15-postgres-partitioning]]"
supersedes: ["[[codex:2025-12-01-postgres-draft]]"]
```

**In prose body (casual):**

```markdown
This spike was motivated by the decision recorded in
[[codex:2026-01-04-postgres-primary-db]].
```

Both forms are recognized by the `lore:link` skill, which cross-checks that:
- Every cited cross-ref resolves to an existing record.
- Every prose cross-ref is also listed in `refs:` (so structural queries see it).
- Every `supersedes` entry has a matching `superseded_by` on the other side.

## Grammar

Formal:

```
cross-ref ::= "[[" archetype ":" id "]]"
archetype ::= [a-z][a-z-]*          // one of the 11 archetype names
id        ::= YYYY "-" MM "-" DD "-" slug
slug      ::= [a-z0-9][a-z0-9-]{1,60}
```

No spaces inside the brackets. No nested brackets. No additional metadata (for that, cite the ref and describe relationship in prose or frontmatter `tags`).

## What cross-refs are NOT

- Not hyperlinks. Lore records may sit in various directory hierarchies; cross-refs don't encode paths. `meta/link` resolves them at read time.
- Not version-pinned. A cross-ref to `[[codex:2026-01-04-postgres-primary-db]]` always resolves to the current state of that record (which may have been `superseded_by` something newer).

## Validation

- `scripts/validate.py` checks that frontmatter `refs`, `supersedes`, `superseded_by` entries are well-formed.
- `lore:link` (future skill) checks that they *resolve* (i.e., the target file exists).
