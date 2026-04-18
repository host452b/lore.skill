---
id: 2026-04-17-journal-with-superseded-by
type: journal
tier: live
date: 2026-04-17
title: Journal trying to supersede
authors: ["Joe <j@example.com>"]
profile: web-service
event-time: 2026-04-17T12:00:00Z
event-type: deploy
environment: prod
outcome: succeeded
superseded_by: "[[journal:2026-04-18-redeploy]]"
---

# Journal trying to supersede

Journal records are immutable — this record should fail validation.
