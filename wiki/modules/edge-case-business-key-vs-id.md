---
type: module-type
title: "Edge case: business key vs ID"
tags: [edge-case,unverified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Edge case: business key vs ID

Business keys (employee number, unit code) are human-meaningful and may be reissued, reformatted, or corrected. IDs ([opaque-permanent-id](../concepts/opaque-permanent-id.md)) are not.

Rules:
- Join on IDs. Expose business keys as attributes only.
- Enforce uniqueness of the business key in the owner, with effective dating if it can be reused over time.
- External standard codes may be the key for external reference sets under the conditions in [external-reference-sets](../decisions/external-reference-sets.md).
