---
type: pattern
title: "Flow: reconciliation"
tags: [unverified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Flow: reconciliation

A scheduled comparison between a consumer's copy and the owner.

1. Compare counts or hashes per range (for example per ID range or per `updated_at` window).
2. For mismatching ranges, re-fetch records from the owner.
3. Apply through the normal version-guarded path.
4. Record the result (ranges checked, mismatches, repairs) for [freshness-and-drift-monitoring](../ops/freshness-and-drift-monitoring.md).

Frequency: nightly as a starting point; tune to freshness needs. Standard practice, unsourced in the research ([source-reliability](../ops/source-reliability.md)).
