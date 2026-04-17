---
id: 2026-04-17-adr-postgres-primary
type: codex
tier: canon
date: 2026-04-17
title: Postgres as primary DB
authors: ["host452b <>"]
profile: adr
status: accepted
refs: ["[[journal:2026-04-10-db-spike]]"]
tags: ["database", "architecture"]
---

# Postgres as primary DB

## Context
We needed a primary transactional store.

## Decision
Postgres 16.

## Consequences
Operational familiarity; gives up some NoSQL flexibility.
