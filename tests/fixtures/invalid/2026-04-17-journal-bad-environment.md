---
id: 2026-04-17-journal-bad-environment
type: journal
tier: live
date: 2026-04-17
title: Journal with bad environment
authors: ["Joe <j@example.com>"]
profile: web-service
event-time: 2026-04-17T12:00:00Z
event-type: deploy
environment: production
outcome: succeeded
---

# Journal with bad environment

`environment: production` is not in enum {prod, staging, dev, test} — should use `prod`.
