---
id: 2026-04-08-payment-api-incident
type: journal
tier: live
date: 2026-04-08
title: Payment API 5xx spike — incident and recovery
authors: ["host452b <>"]
profile: web-service
event-time: 2026-04-08T09:14:00+00:00
event-type: incident
environment: prod
outcome: partial
duration: PT41M
metrics: {peak_5xx_per_min: 312, baseline_5xx_per_min: 4}
tags: ["payment", "oncall"]
---

# Payment API 5xx spike — incident and recovery

5xx rate on `/api/payments/*` jumped from baseline ~4/min to peak
312/min at 09:14Z. Root cause traced to a connection-pool exhaustion
on the payments DB after an ORM config change deployed in v1.3.1.
Mitigated by scaling the pool at 09:38Z; residual error rate returned
to baseline by 09:55Z. Postmortem to follow.
