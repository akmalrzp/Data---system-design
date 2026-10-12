---
type: usecase
title: "Use case: update, rename, reparent"
tags: [proposal]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Use case: update, rename, reparent

**Steps**: owner changes the record, increments `version`, publishes; consumers apply if newer.

**Effect by module type**
- Owner: master row updated (history row where kept; [accountability-default](../tables/accountability-default.md)).
- Type 1: cache updated; displays change. Historical documents show the new name unless a snapshot was stored ([table-transaction](../tables/table-transaction.md)).
- Type 2: rename has no business effect. Reparent changes roll-up totals ([edge-case-hierarchy-changes](../modules/edge-case-hierarchy-changes.md)); effective-dated requirements remain valid.
- Projections: events must carry previous values when a field changes the grouping (transfer between units; [projection-module](../modules/projection-module.md)).

**Edge cases**: names needed "as of" a past date require effective-dated names in the owner; cycles in hierarchy rejected by the owner; late events ignored by version.
