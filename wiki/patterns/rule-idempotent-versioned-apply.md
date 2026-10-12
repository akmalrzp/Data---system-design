---
type: pattern
title: "Rule: idempotent, version-guarded apply"
tags: [partly-verified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Rule: idempotent, version-guarded apply

The consumer's only way to change a cache or projection.

1. Read the event (or fetched record).
2. In one transaction: compare `version` with stored `source_version`.
   - Greater: apply; store new version; record processed event ID.
   - Equal: duplicate; ignore.
   - Lower: late; ignore.
3. Commit.

Properties:
- Safe under duplicates, reordering and replays.
- Deleted or inactive state is a versioned state, so a stale update cannot resurrect a record ([rule-deletes-as-state](rule-deletes-as-state.md)).
- Same path for events and for bootstrap or repair ([flow-bootstrap-and-catch-up](flow-bootstrap-and-catch-up.md)).
- Unknown IDs on dependent events: store or fetch, do not drop silently.

Storing the processed event ID in the same transaction as the change is the relational adaptation of the "commit state with offset" idea (inference).
