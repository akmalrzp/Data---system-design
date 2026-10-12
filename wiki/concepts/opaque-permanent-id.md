---
type: concept
title: "Opaque permanent ID"
tags: [principle,unverified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Opaque permanent ID

The owner issues an identifier at record creation. Rules:
- **Immutable**: never changes.
- **Never reused**: not even after the record is deleted.
- **Opaque**: no name, unit, date, or national-ID content, so it cannot go stale or leak.
- **Not a business key**: a human-facing number (for example `employee_number`) is an ordinary attribute and is not the join key between modules.
- **Global enough** to be unique across owners (UUID or equivalent). The format is a technology choice.

Consumers store it as a foreign reference with a unique constraint in their own cache or transaction table.

Evidence: established practice, not source-verified (see [source-reliability](../ops/source-reliability.md)).
