---
type: module-type
title: "Edge case: divergent reference caches"
tags: [edge-case,proposal]
sources: [osdm-integration-summary]
created: 2026-10-12
updated: 2026-10-12
---

# Edge case: divergent reference caches

Two consumers cache the same owner's entity, and one of them emits events that the other interprets through its own copy. They can disagree for a while.

Example: A and D both subscribe to C's units. A validates assignments against its cache of C and emits `employee.changed` with `unit_id`. D keeps a headcount projection `unit_id -> active count` ([projection-module](projection-module.md)) and reads unit status and `parent_unit_id` from its own cache of C.

This page is design reasoning, not from a cited source.

## Who is authoritative
- C is authoritative for what a unit is (exists, active, name, parent).
- A is authoritative for which unit an employee is assigned to.
- Neither A's nor D's cache of C is authoritative. Both are read-only copies ([table-master-cache](../tables/table-master-cache.md)).
- A does not send unit data to D. It sends `unit_id` only. D builds the projection itself.

Both caches come from the same versioned stream, so a mismatch is normally lag: one copy is behind. Lasting divergence means a cache missed events.

## Case 1: A's cache is ahead of D's
C creates a unit. A learns of it first, accepts an assignment, and emits an event with a `unit_id` that D does not know yet.

- D applies the count, keyed by `unit_id`. It does not reject A's event against its own cache: A already validated it. [rule-validate-ids-locally](../patterns/rule-validate-ids-locally.md) applies to writes D accepts from its users, not to events from an owner.
- D shows a placeholder for the unit and calls C's read API on the miss.
- Roll-ups cannot place the count until D has the unit's `parent_unit_id` ([edge-case-hierarchy-changes](edge-case-hierarchy-changes.md)).

## Case 2: D's cache is ahead of A's
C marks a unit `inactive` or sets `replaced_by`. D learns of it first. A, still on the older copy, keeps assigning to the old unit.

- D's count shows employees on an inactive unit. That matches what A holds, so the count is correct; the assignments are what need correcting.
- D flags the unit. It does not move counts via `replaced_by` itself ([uc-merge](../usecases/uc-merge.md), [uc-split](../usecases/uc-split.md)).
- When A reassigns, its events carry `previous_unit_id` and the count moves.
- If A keeps assigning to the unit beyond normal lag, A's cache is stale or A is not processing C's lifecycle events. Alert on it ([freshness-and-drift-monitoring](../ops/freshness-and-drift-monitoring.md)).

## Case 3: lasting divergence
A missed event or a bug leaves a cache wrong indefinitely.

- A and D each reconcile their cache against C ([flow-reconciliation](../patterns/flow-reconciliation.md)). Never reconcile one consumer's cache against another's.
- D also reconciles its projection against A per unit (A's headcount read API, or a recount by range).

## Optional: carry the version A validated against
A adds the unit version it validated against (for example `unit_version`) to its assignment event. D compares it with its own cache:
- A's version is newer: D re-fetches the unit from C.
- D's version is newer: A acted on an older view; D can flag the record.

This lets D tell lag from a real conflict without guessing. It is an additive field ([rule-additive-only-contract](../patterns/rule-additive-only-contract.md)).

## Rule
The projection trusts A for who sits where and C for what the unit is. D never checks A's facts against its own cache of C.
