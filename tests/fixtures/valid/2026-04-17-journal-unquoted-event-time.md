---
id: 2026-04-17-journal-unquoted-event-time
type: journal
tier: live
date: 2026-04-17
title: Journal with unquoted event-time
authors: ["Joe <j@example.com>"]
profile: web-service
event-time: 2026-04-17T12:00:00Z
event-type: deploy
environment: prod
outcome: succeeded
---

# Journal with unquoted event-time

This fixture proves PyYAML's datetime auto-coercion is handled by
the validator. The event-time value above is NOT quoted — PyYAML
will parse it as a datetime.datetime object — and the validator
must tolerate that via isoformat() normalization.
