---
type: pattern
title: "Rule: no shared databases"
tags: [unverified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Rule: no shared databases

A consumer never reads or writes another module's database, and no cross-system foreign keys exist. A shared database makes the owner's schema a public contract, so every internal change becomes a cross-team change.

Consumers get data only through the owner's contract ([rule-additive-only-contract](rule-additive-only-contract.md)) and keep their own copy ([table-master-cache](../tables/table-master-cache.md)).
