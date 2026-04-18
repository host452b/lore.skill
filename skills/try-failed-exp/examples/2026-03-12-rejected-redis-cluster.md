---
id: 2026-03-12-rejected-redis-cluster
type: try-failed-exp
tier: canon
date: 2026-03-12
title: Redis Cluster as primary session store (rejected)
authors: ["host452b <>"]
profile: rejected-adr
status: rejected
refs: ["[[codex:2026-03-15-postgres-primary-session-store]]"]
tags: ["database", "caching", "session-management"]
---

# Redis Cluster as primary session store (rejected)

## What was considered
Using Redis Cluster as the primary store for user sessions, replacing
the current PostgreSQL-backed sessions table. Target: 3-node cluster,
hash-slotted keyspace.

## Why it was rejected
- Cross-slot transaction limitations conflict with our atomic
  multi-key session invalidation pattern.
- Operational complexity of running a cluster exceeded the team's
  capacity given concurrent migrations.
- Benchmark showed PostgreSQL with UNLOGGED session table meets p99
  latency budget (12 ms vs 6 ms target — well within SLO).

## What was chosen instead
Stayed on PostgreSQL with an UNLOGGED session table and denormalized
session-index view. See [[codex:2026-03-15-postgres-primary-session-store]].

## Don't retry unless
- Session volume exceeds 50k writes/sec (currently ~8k) AND PG hits
  p99 latency breach, OR
- Redis ships native cross-slot transactions in a GA release.
