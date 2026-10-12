---
type: decision
title: "Decision: subscribe to events or call the owner on demand"
tags: [option]
sources: [osdm-integration-summary,api-design-for-system-integration,author-decisions-2026-10-09]
created: 2026-10-09
updated: 2026-10-09
---

# Decision: subscribe to events or call the owner on demand

Open point in the source summary. Both options are valid; the conditions decide.

| | Option 1: subscribe and keep a local cache | Option 2: call the owner's read API on demand |
|---|---|---|
| Availability | Consumer works if owner is down | Consumer fails with the owner |
| Freshness | Eventual; show "as of" | Exact at read time |
| Complexity | Higher: cache, apply path, reconciliation | Lower: no local copy |
| Coupling | Contract-level only | Runtime coupling plus latency |
| Load on owner | Low, steady | Proportional to reads |
| Joins and reporting | Local joins | Cross-system calls per row |
| Data duplication | Yes (erasure scope grows) | No |

**Choose option 1 when**
- the consumer must keep operating when the owner is down;
- it joins or filters by the data locally (names in lists, reports, roll-ups);
- read volume is high;
- the data changes rarely relative to reads (reference data such as units and positions).

**Choose option 2 when**
- exactness at decision time is required (for example a permission or an amount);
- the data is sensitive and should not be replicated ([payload-sensitive-fields](../patterns/payload-sensitive-fields.md));
- volume is low and the owner is highly available;
- the team cannot yet operate caches and reconciliation.

**Hybrid (common)**: cache reference data (units, positions); call on demand for sensitive or exactness-critical data; call on a cache miss.

Applies to B and D in [worked-example](../concepts/worked-example.md); for D's headcount see [projection-module](../modules/projection-module.md). Related: [flow-events-plus-read-api](../patterns/flow-events-plus-read-api.md), [edge-case-owner-unavailable](../modules/edge-case-owner-unavailable.md).
