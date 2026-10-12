---
type: module-type
title: "Edge case: field ownership disputes"
tags: [edge-case,proposal]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Edge case: field ownership disputes

Situation: consumer B needs a field to be authoritative (for example a corrected display name) but A owns the record.

Resolution, in order:
1. Ask whether B really needs authority. If not, B uses A's value.
2. If B needs its own value, B owns that field in its own table, keyed by the same ID. It is not added to A's contract.
3. If both are legitimately needed, name them differently (`legal_name` vs `payroll_display_name`). One name must never carry two meanings.

Related: [system-of-record](../concepts/system-of-record.md), [feature-placement-test](feature-placement-test.md).
