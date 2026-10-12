---
type: pattern
title: "Flow: events plus read API"
tags: [partly-verified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Flow: events plus read API

**Default flow.** The owner writes the business change and an outbox record in one local transaction. A relay publishes the outbox record as a change event. Consumers apply the event to their cache. A read API gives lookup by ID and catch-up by cursor.

```
Owner: [business change + outbox row] -> relay -> event channel -> Consumer: [idempotent apply]
Consumer --(lookup / catch-up)--> Owner read API
```

**Why both.** Events give timeliness and independence; the read API gives recovery, bootstrap and on-demand lookup.

**Properties to assume**
- At-least-once delivery. The relay may publish twice, so consumers must be idempotent ([rule-idempotent-versioned-apply](rule-idempotent-versioned-apply.md)).
- Per-entity order, not global order ([rule-ordering-per-entity](rule-ordering-per-entity.md)).
- Exactly-once across separate systems is not assumed.

**Alternatives by need** (shared database ruled out first)
- Answer needed now: synchronous API with timeouts and a circuit breaker; consumer depends on owner availability.
- React to change or keep a copy: events (this page).
- External organisation consumer: signed webhooks, retries, list endpoint for reconciliation.
- Bulk or analytical: batch files or a governed data product, separate from the operational interface.

Evidence: outbox and delivery semantics are partly verified (Confluent, microservices.io); the style comparison is unverified ([source-reliability](../ops/source-reliability.md)). Related: [flow-bootstrap-and-catch-up](flow-bootstrap-and-catch-up.md), [flow-reconciliation](flow-reconciliation.md), [decision-subscribe-vs-call-on-demand](../decisions/decision-subscribe-vs-call-on-demand.md).
