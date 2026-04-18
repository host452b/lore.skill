---
id: <YYYY-MM-DD-slug>
type: journal
tier: live
date: <YYYY-MM-DD>
title: <short title, e.g. "Deploy v1.3.2 to prod">
authors: ["<Name <email>>"]
profile: web-service
event-time: <YYYY-MM-DDTHH:MM:SS+ZZ:ZZ or Z>
event-type: <deploy|incident|rollback|release|migration|ci-failure>
environment: <prod|staging|dev|test>
outcome: <succeeded|failed|partial|rolled-back|observed>
duration: <PT5M, omit if instantaneous>
commit-sha: <short or full sha, omit if not applicable>
metrics: {}
refs: []
tags: []
---

# <title>

<2-5 sentences: what happened, key numbers, link to runbook/dashboard
if relevant. Keep it short — journal entries aggregate, they don't drill
down individually.>
