---
id: <YYYY-MM-DD-slug>
type: try-failed-exp
tier: canon
date: <YYYY-MM-DD>
title: <human title, e.g. "Redis Cluster as primary cache (rejected)">
authors: ["<Name <email>>"]
profile: rejected-adr
status: rejected
refs: []
tags: []
---

# <title>

## What was considered
<what approach, library, or architecture was on the table>

## Why it was rejected
<the constraints, evidence, or trade-offs that ruled it out — be specific enough
that a future reader can tell whether the reasoning still holds>

## What was chosen instead
<what was adopted in its place; cite the codex entry: [[codex:<id>]]>

## Don't retry unless
<specific, falsifiable condition(s) that would justify revisiting.
Avoid "if priorities change"; prefer concrete triggers like
"if Redis ships native cross-region replication" or
"if our event volume exceeds 50k writes/sec">
