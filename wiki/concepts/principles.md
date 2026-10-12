---
type: concept
title: "Core principles"
tags: [principle]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Core principles

1. **One owner per record.** Exactly one module creates and changes a record: the [system-of-record](system-of-record.md). Everyone else holds a derived copy.
2. **Permanent opaque ID.** The owner issues an identifier that never changes, is never reused, and carries no business meaning. See [opaque-permanent-id](opaque-permanent-id.md).
3. **Consumers store the ID plus only the fields they need**, as a read-only cache. Fields that must be authoritative in a consumer belong to that consumer, not to the owner.
4. **A small, versioned, additive contract**, separate from the owner's internal model. See [rule-additive-only-contract](../patterns/rule-additive-only-contract.md).
5. **Changes flow as events; a read API serves lookup and catch-up.** See [flow-events-plus-read-api](../patterns/flow-events-plus-read-api.md).
6. **Assume duplicates, disorder, and loss.** Apply changes idempotently and only when the version is newer. See [rule-idempotent-versioned-apply](../patterns/rule-idempotent-versioned-apply.md).
7. **Translate at the edge.** Each consumer converts the owner's model into its own. See [anti-corruption-layer](anti-corruption-layer.md).
8. **No shared databases, no cross-module foreign keys.**
9. **State changes, not absence.** Lifecycle changes (inactive, replaced, deleted) are explicit versioned states. See [rule-deletes-as-state](../patterns/rule-deletes-as-state.md).
10. **Accept eventual consistency** and show freshness. See [eventual-consistency](eventual-consistency.md).

Evidence: items 1, 2, 3, 7 are well-established practice but not source-verified (see [source-reliability](../ops/source-reliability.md)).
