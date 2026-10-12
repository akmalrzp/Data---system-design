---
type: module-type
title: "Edge case: hierarchy changes"
tags: [edge-case,proposal]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Edge case: hierarchy changes

Reparenting a unit in C changes roll-ups in every consumer that aggregates by hierarchy (D's totals).

Rules:
- C publishes `parent_unit_id` and a version; a reparent is a normal update ([uc-update-rename-reparent](../usecases/uc-update-rename-reparent.md)).
- Consumers read the hierarchy from their local cache and recompute roll-ups; they do not store roll-ups as master data.
- Effective-date the change if history matters (totals "as of" a past date need the parent as of that date).
- Cycles in the hierarchy are rejected by the owner.
