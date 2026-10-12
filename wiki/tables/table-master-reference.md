---
type: table-type
title: "Master reference table (owner)"
tags: [unverified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Master reference table (owner)

The authoritative table in the [data-owner-broadcaster](../modules/data-owner-broadcaster.md).

**Typical columns** (illustrative)
- `id` (opaque permanent), business key as attribute, `version` (monotonic), `status` (`active`, `inactive`, plus domain states), `replaced_by` (list), `effective_from`, `effective_to`, `updated_at`.
- Attributes owned by this module.
- Parent references for hierarchies (`parent_id`).

**Rules**
- Only the owner writes.
- Every change increments `version`.
- Retirement is a status, not a delete (exception: [decision-delete-policy-and-erasure](../decisions/decision-delete-policy-and-erasure.md)).
- Every change writes an outbox record in the same transaction ([flow-events-plus-read-api](../patterns/flow-events-plus-read-api.md)).

**Accountability**: transaction log or outbox for every change, plus history where past values matter. See [accountability-options](accountability-options.md) and [accountability-default](accountability-default.md).
