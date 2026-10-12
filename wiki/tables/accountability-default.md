---
type: table-type
title: "Accountability default (recommended)"
tags: [proposal]
sources: [author-decisions-2026-10-09,osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Accountability default (recommended)

**Proposal, revisable** once an audit or regulatory requirement is known.

| Table type | Default mechanism |
|---|---|
| Master reference ([table-master-reference](table-master-reference.md)) | Outbox / transaction log written with every change; `version`, `updated_by`, `updated_at` columns; effective-dated history only for entities where past values matter |
| Cache ([table-master-cache](table-master-cache.md)) | `source_version`, `last_synced_at`; processed-event log committed with each apply; reconciliation record |
| Transaction ([table-transaction](table-transaction.md)) | `created_by`, `created_at`, change reason; append-only log for business facts; snapshot where reproduction is required |
| Projection ([table-projection](table-projection.md)) | `as_of`; rebuild-and-compare; processed-event log |
| Crosswalk ([table-crosswalk](table-crosswalk.md)) | Never delete; `valid_from` / `valid_to`; approval recorded |

Upgrade to versioned or bitemporal history only when a requirement demands it. Retention of logs must be reconciled with erasure obligations ([decision-delete-policy-and-erasure](../decisions/decision-delete-policy-and-erasure.md)).

Options: [accountability-options](accountability-options.md).
