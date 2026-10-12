---
type: pattern
title: "Rule: ordering per entity"
tags: [partly-verified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Rule: ordering per entity

Global order is not needed. Partition events by entity ID so per-entity order holds, and carry a monotonic `version` so consumers can detect and discard late events ([rule-idempotent-versioned-apply](rule-idempotent-versioned-apply.md)).

For writes through APIs, use optimistic concurrency (ETag and `If-Match`; 412 on mismatch). The client refetches and reconciles, not retries blindly.

Cross-entity ordering (for example the unit exists before an assignment references it) is handled by validation and lazy resolution, not by global ordering ([rule-validate-ids-locally](rule-validate-ids-locally.md)).
