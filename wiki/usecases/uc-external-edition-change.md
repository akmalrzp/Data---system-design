---
type: usecase
title: "Use case: external reference edition change"
tags: [proposal,unverified]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Use case: external reference edition change

An external authority publishes a new edition of a code set ([external-reference-sets](../decisions/external-reference-sets.md)).

1. The steward reviews the change and approves.
2. The owner imports the new edition, adds new entries, closes changed ones with `valid_to`, and updates the [table-crosswalk](../tables/table-crosswalk.md).
3. The owner publishes the new edition with a cutoff date for the old one.
4. Consumers apply it; old codes stay resolvable.
5. Consumers with local extensions ([table-transaction](../tables/table-transaction.md)) check their keys.

**Edge cases**: entries split or merged by the authority (use `replaced_by` like [uc-split](uc-split.md), [uc-merge](uc-merge.md)); the organisation's definition differs from the new edition (keep both, map explicitly).
