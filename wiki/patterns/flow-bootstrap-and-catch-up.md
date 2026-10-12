---
type: pattern
title: "Flow: bootstrap and catch-up"
tags: [partly-verified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Flow: bootstrap and catch-up

A new consumer, a rebuilt consumer, or a consumer that missed events uses the same path:

1. Page through the owner's list endpoint with `updated_after` (or from the start), using opaque cursors.
2. Apply each record through the normal version-guarded apply ([rule-idempotent-versioned-apply](rule-idempotent-versioned-apply.md)).
3. Switch to events, or begin consuming events during step 1 and rely on the version check to discard older data.
4. Run reconciliation ([flow-reconciliation](flow-reconciliation.md)).

Using one apply path for both bootstrap and events removes a class of divergence bugs. Details in [uc-initial-broadcast](../usecases/uc-initial-broadcast.md) and [uc-late-joiner-and-gaps](../usecases/uc-late-joiner-and-gaps.md).

Snapshot-plus-change-feed bootstrap had no usable source in the research ([source-reliability](../ops/source-reliability.md)); treat the ordering in step 3 as design reasoning.
