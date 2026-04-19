---
id: 2026-03-15-postgres-primary-session-store
type: codex
tier: canon
date: 2026-03-15
title: PostgreSQL as primary session store
authors: ["host452b"]
profile: adr
status: accepted
refs: ["[[try-failed-exp:2026-03-12-rejected-redis-cluster]]"]
tags: ["database", "session-management", "architecture"]
---

# PostgreSQL as primary session store

## Context
The application needs a reliable session store handling ~8k writes/sec
today with growth projected to ~20k/sec over 18 months. Sessions require
atomic multi-key invalidation (logout cascades, role changes invalidating
all active tokens for a user). Operational capacity is constrained:
two engineers shared across three services, concurrent migrations already
in progress.

## Decision
Use PostgreSQL with an UNLOGGED session table + denormalized session-index
view as the primary session store. Benchmark shows p99 latency of 11ms
against a 6ms target budget, well within SLO. Atomic multi-key operations
use standard PostgreSQL transactions.

## Consequences

**Easier:**
- Operational familiarity — the team already runs PostgreSQL.
- Atomic multi-key session invalidation via transactions.
- Single datastore to back up, monitor, and migrate.

**Harder:**
- Session latency (11ms p99) is higher than a pure cache would deliver
  (Redis benchmarked at 4ms), though still within SLO.
- Session table grows unbounded without a TTL job (mitigated by a daily
  cleanup of expired rows).

**Trade-offs accepted:** operational simplicity over raw latency. Revisit
if session volume exceeds 50k writes/sec AND PG hits p99 latency breach,
per the condition recorded in [[try-failed-exp:2026-03-12-rejected-redis-cluster]].

## Rejected alternatives

See [[try-failed-exp:2026-03-12-rejected-redis-cluster]] for the Redis
Cluster option that was considered and rejected.
