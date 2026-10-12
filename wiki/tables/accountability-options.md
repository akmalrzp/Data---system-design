---
type: table-type
title: "Accountability options compared"
tags: [option,proposal]
sources: [author-decisions-2026-10-09,osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Accountability options compared

How to make every table type answerable for "who changed what, when, and why". No audit requirement exists yet ([author-decisions-2026-10-09](../sources/author-decisions-2026-10-09.md)); this page compares the options. The recommended default is in [accountability-default](accountability-default.md).

| Option | What it is | Best for | Cost | Weakness |
|---|---|---|---|---|
| Lineage columns | `version`, `source_version`, `updated_by`, `updated_at`, `last_synced_at` on rows | Caches, quick traceability | Very low | Shows state only, not history |
| Transaction log / outbox | Append-only record of every change, written in the same transaction | Owner master tables | Low to medium | Needs retention and indexing |
| Processed-event log | Consumer records event ID (or entity ID plus version) applied | Caches, projections | Low | Grows; needs pruning policy |
| Versioned history table | Prior row versions with validity intervals | Entities where past values matter (assignment, unit name) | Medium | Query complexity |
| Bitemporal history | Both valid time and recorded time | Retroactive corrections with legal weight | High | Complexity; use only if required |
| Event store | Events are the source of truth | Rebuild-heavy projections | High | Whole-system commitment |
| Snapshot on write | Copy of referenced values stored with the transaction | Documents that must reproduce the past | Low | Duplicates data on purpose |
| Reconciliation record | Result of comparing copy to owner | Detecting drift | Low | Detects, does not explain |

Select per table type: [table-master-reference](table-master-reference.md), [table-master-cache](table-master-cache.md), [table-transaction](table-transaction.md), [table-projection](table-projection.md), [table-crosswalk](table-crosswalk.md).
