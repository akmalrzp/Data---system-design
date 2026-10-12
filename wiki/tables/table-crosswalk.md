---
type: table-type
title: "Crosswalk table"
tags: [proposal,unverified]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Crosswalk table

Maps an external code or entry to an internal ID, used for external reference sets where there is no stable code, or the organisation's definition differs from the external one ([external-reference-sets](../decisions/external-reference-sets.md)).

**Columns** (illustrative): `internal_id`, `external_authority`, `external_code`, `external_edition`, `valid_from`, `valid_to`, `mapping_type` (exact, broader, narrower), `approved_by`.

**Rules**
- Owned by the reference set owner; changes need steward approval.
- Never delete a mapping: close it with `valid_to`.
- Keep both definitions when they differ and map explicitly.
