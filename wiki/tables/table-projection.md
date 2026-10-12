---
type: table-type
title: "Projection table"
tags: [proposal]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Projection table

Derived facts from another owner's events, for example `unit_id -> active employee count` in D ([projection-module](../modules/projection-module.md)).

**Rules**
- Rebuildable from the owner's events or API (full rebuild path documented and tested).
- Updated by the same idempotent apply path as caches; events must carry previous values where needed (for example `previous_unit_id`).
- Carries `as_of` timestamp and source versions processed.
- Never treated as master data.

**Accountability**: rebuild-and-compare against the owner is the audit ([flow-reconciliation](../patterns/flow-reconciliation.md)); the processed-event log shows what was applied.
