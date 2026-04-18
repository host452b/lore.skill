---
id: 2026-04-17-journal-bad-event-time
type: journal
tier: live
date: 2026-04-17
title: Journal with bare-date event-time
authors: ["Joe <j@example.com>"]
profile: web-service
event-time: 2026-04-17
event-type: deploy
environment: prod
outcome: succeeded
---

# Journal with bad event-time format

event-time should be ISO 8601 with time precision, not a bare date.
