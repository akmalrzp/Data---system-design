---
type: pattern
title: "Rule: deletes are explicit versioned states"
tags: [partly-verified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Rule: deletes are explicit versioned states

- The owner marks records `inactive` (or `terminated`, `deleted`) with a new `version`; it does not remove the row by default.
- Merge and split use `replaced_by`.
- A null-value tombstone in a compacted log means earlier records may be removed and does not protect a late joiner; a retained, versioned status does (the second point is an inference).
- Consumers keep the state so late or stale updates cannot resurrect the record.

Exception for erasure: [decision-delete-policy-and-erasure](../decisions/decision-delete-policy-and-erasure.md). Use cases: [uc-delete](../usecases/uc-delete.md).
