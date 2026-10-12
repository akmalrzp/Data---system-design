---
type: module-type
title: "Consumer type 1: reference data as attributes"
tags: [unverified]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Consumer type 1: reference data as attributes

**Role.** Uses another module's records as descriptive attributes of its own records. The reference does not define the consumer's records.

Example: B (Payroll) stores `employee_id` and shows the unit and position name. The payroll record exists with or without a particular unit.

**Design**
- Keep a cache of the master ([table-master-cache](../tables/table-master-cache.md)) with the ID as unique key and only the fields needed.
- Own records ([table-transaction](../tables/table-transaction.md)) hold the foreign ID; no cross-system foreign key constraint.
- Resolve names by joining on IDs in the local cache.
- Unknown ID: store it, show a placeholder, fetch from the owner on the miss.
- Inactive or replaced reference: keep the record, display the status, follow `replaced_by` for display.

**Impact of owner lifecycle**: low. Renames change display only; retirement changes display and flags.

Contrast with [consumer-index-user](consumer-index-user.md). Use cases: [guide-04-use-cases](../guide/guide-04-use-cases.md).
