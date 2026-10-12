---
type: ops
title: "Freshness and drift monitoring"
tags: [proposal]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Freshness and drift monitoring

Measure, per consumer and entity:
- **Lag**: time from the owner's `occurred_at` to the consumer's `last_synced_at`.
- **Drift**: mismatches found by [flow-reconciliation](../patterns/flow-reconciliation.md) and repair counts.
- **Rejects**: events refused for malformed required data.
- **Placeholders**: unknown-ID rows awaiting resolution.

Display "as of" timestamps in UIs ([eventual-consistency](../concepts/eventual-consistency.md)). Alerting thresholds, SLOs, tracing and dead-letter handling had no usable source ([source-reliability](source-reliability.md)); define them in ADRs ([data-dictionary-and-adr](data-dictionary-and-adr.md)).
