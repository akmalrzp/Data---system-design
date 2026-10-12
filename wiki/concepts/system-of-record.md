---
type: concept
title: "System of record"
tags: [principle,unverified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# System of record

For each entity exactly one module is the system of record: the only place where the entity is created, changed, retired. All other copies are derived and read-only.

Consequences:
- Ownership is decided once per entity, and recorded in the data dictionary ([data-dictionary-and-adr](../ops/data-dictionary-and-adr.md)).
- A consumer that needs an authoritative field of its own owns that field in its own table, rather than editing the owner's copy.
- Field-level disputes: see [edge-case-field-ownership](../modules/edge-case-field-ownership.md).

Related: [data-owner-broadcaster](../modules/data-owner-broadcaster.md), [opaque-permanent-id](opaque-permanent-id.md). Evidence: established practice, not source-verified.
