---
type: usecase
title: "Use case: late joiner, missed or out-of-order events"
tags: [proposal]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Use case: late joiner, missed or out-of-order events

- **Late joiner or rebuilt consumer**: [flow-bootstrap-and-catch-up](../patterns/flow-bootstrap-and-catch-up.md); a retained delete state is needed so history is not lost ([rule-deletes-as-state](../patterns/rule-deletes-as-state.md)).
- **Missed events**: reconciliation detects the range ([flow-reconciliation](../patterns/flow-reconciliation.md)); re-fetch and apply through the version check.
- **Out-of-order**: older versions ignored ([rule-idempotent-versioned-apply](../patterns/rule-idempotent-versioned-apply.md)).
- **Event for an unknown dependent ID**: placeholder or fetch on miss.
- **Poison event** (malformed): reject and route to a holding area for review; do not block the entity stream. Dead-letter handling was not researched ([source-reliability](../ops/source-reliability.md)).
