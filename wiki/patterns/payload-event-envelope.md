---
type: pattern
title: "Payload: event envelope"
tags: [partly-verified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Payload: event envelope

Fields every event should carry (names illustrative, technology-neutral):

| Field | Purpose |
|---|---|
| `event_id` | Unique per event; duplicate detection |
| `entity_type`, `entity_id` | What changed; partition key |
| `version` | Monotonic per entity; ordering guard |
| `occurred_at` | When the change committed |
| `change_type` | Created, updated, status changed, replaced |
| `status` | Explicit lifecycle state (active, inactive, terminated, deleted) |
| `replaced_by` | For merge and split |
| `previous_*` | Previous values of fields consumers must decrement or re-index (for example `previous_unit_id`) |
| `effective_from` / `effective_to` | When the change applies, if different from `occurred_at` |
| `schema_version` | Contract version of the payload |
| fields | The non-sensitive attributes consumers need |

Rules: additive-only evolution ([rule-additive-only-contract](rule-additive-only-contract.md)); unknown fields ignored by consumers; required fields validated.
