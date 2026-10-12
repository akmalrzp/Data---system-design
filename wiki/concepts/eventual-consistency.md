---
type: concept
title: "Eventual consistency and freshness"
tags: [principle]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Eventual consistency and freshness

Copies in consumers lag the owner. Design for it:
- Show an "as of" timestamp wherever a consumer displays cached or projected data (counts, names).
- Validate against the local cache, not a live call, unless exactness at decision time is required (see [decision-subscribe-vs-call-on-demand](../decisions/decision-subscribe-vs-call-on-demand.md)).
- Detect and repair drift with [flow-reconciliation](../patterns/flow-reconciliation.md) and [freshness-and-drift-monitoring](../ops/freshness-and-drift-monitoring.md).
- A consumer must tolerate an unknown ID: store it, show a placeholder, fetch from the owner on the miss.
