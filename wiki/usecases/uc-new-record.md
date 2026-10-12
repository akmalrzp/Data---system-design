---
type: usecase
title: "Use case: new record"
tags: [proposal]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Use case: new record

**Steps**
1. Owner validates and creates the record, issues the ID ([opaque-permanent-id](../concepts/opaque-permanent-id.md)), `version = 1`, writes the outbox row.
2. Event published; consumers apply it as an insert in their cache.
3. Consumer records referencing the new ID can now pass local validation ([rule-validate-ids-locally](../patterns/rule-validate-ids-locally.md)).

**Effect by module type**
- Owner: new master row.
- Type 1: new cache row; nothing else changes.
- Type 2: new possible index value; no existing records change. D may prompt for a requirement for a new unit.

**Edge cases**
- A consumer sees an ID in a dependent event before the record event (order across entities is not guaranteed): store a placeholder or fetch on miss ([eventual-consistency](../concepts/eventual-consistency.md)).
- Duplicate event: ignored by version check.
- Duplicate real-world entity (created twice): handle by [uc-merge](uc-merge.md).
