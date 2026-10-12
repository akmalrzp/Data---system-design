---
type: module-type
title: "Hybrid module (owner and consumer)"
tags: [proposal]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Hybrid module (owner and consumer)

Most real modules own some entities and consume others. A owns Employee and consumes Unit and Position from C ([worked-example](../concepts/worked-example.md)).

Rules:
- Classify per entity, not per module. A is an owner for Employee and a type 1 or 2 consumer for Unit.
- Keep owned tables and caches physically and logically separate ([table-master-reference](../tables/table-master-reference.md) vs [table-master-cache](../tables/table-master-cache.md)).
- Validate an assignment (employee to unit and position) against the local cache before accepting it.
- Never republish a consumed entity's attributes (A publishes `unit_id`, not the unit's name).
- Watch for dependency cycles ([edge-case-circular-dependencies](edge-case-circular-dependencies.md)).
