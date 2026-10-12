---
type: module-type
title: "Projection holder"
tags: [proposal]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-12
---

# Projection holder

A module that needs facts derived from another owner's data, not the records themselves. Example: D needs active headcount per unit; it subscribes to A and keeps `unit_id -> active count`, not employee records.

Rules:
- The events must carry what the projection needs, including previous values (a transfer event includes `previous_unit_id`, so the old unit is decremented).
- The projection must be rebuildable from the owner's events or API ([table-projection](../tables/table-projection.md)).
- Display "as of" timestamps.
- Do not reject the owner's events against your own cache of a third module; see [edge-case-divergent-reference-caches](edge-case-divergent-reference-caches.md).
- Alternative: call the owner's read API when exactness at read time matters. See [decision-subscribe-vs-call-on-demand](../decisions/decision-subscribe-vs-call-on-demand.md).
