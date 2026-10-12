---
type: concept
title: "Worked example: modules A, B, C, D"
tags: [example]
sources: [osdm-integration-summary,author-decisions-2026-10-09]
created: 2026-10-09
updated: 2026-10-09
---

# Worked example: modules A, B, C, D

The modules are illustrative. Replace them with real modules when applying the guide.

| Module | Role | Owns | Uses |
|---|---|---|---|
| A (HR Core) | owner, and consumer of C | Employee, assignment of an employee to a unit and position | Unit, Position from C |
| B (Payroll) | consumer type 1 (attributes) | pay grade, tax status | Employee from A; Unit, Position names from C |
| C (Org structure) | owner | Unit, Position | none |
| D (Requirements) | consumer type 2 (index) and projection holder | required headcount per unit | Unit from C; employee counts per unit from A |

Pattern summary:
- A broadcasts `employee_id`, `unit_id`, `position_id`, not names. Names belong to C.
- C broadcasts `unit.changed`, `position.changed`. A, B, D keep local caches.
- B resolves names by joining on IDs in its own cache of C.
- D uses `unit_id` as the business key of its requirement records, so unit lifecycle changes in C affect D directly.

Roles are defined in [guide-01-module-types](../guide/guide-01-module-types.md). Sensitive fields (salary, national ID) stay out of events; see [payload-sensitive-fields](../patterns/payload-sensitive-fields.md).
