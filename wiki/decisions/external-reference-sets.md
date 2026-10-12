---
type: decision
title: "External reference sets"
tags: [proposal,unverified]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# External reference sets

Reference data not produced by an internal module (region codes, tax status, education levels). Give each set one internal owner ([external-reference-owner](../modules/external-reference-owner.md)) and a named data steward.

## Keying decision

| Situation | Action |
|---|---|
| Stable public standard code (ISO etc.) | Use the external code as the shared key. Store the standard and edition. |
| Authority changes codes over time | Key by code plus edition or effective date. Keep old codes resolvable. |
| No stable code or free-text list | Owner mints an internal ID and keeps a [table-crosswalk](../tables/table-crosswalk.md) to the external entry. |
| Organisation's definition differs from the external one | Keep both and map explicitly. |

## Process
- Owner imports from the source, validates, and publishes versioned events or a dataset plus a read API.
- Other systems subscribe and reference entries by code, never by text.
- Write each set into a data dictionary entry (authority, edition, owner, update schedule, change approval); record the source choice in an ADR ([data-dictionary-and-adr](../ops/data-dictionary-and-adr.md)).
- Pin editions; announce edition changes with a cutoff date for the old one ([uc-external-edition-change](../usecases/uc-external-edition-change.md)).
- Local extensions go in the consumer's own table keyed by the code.
- One name must never carry two meanings; if meanings conflict, split into two named sets.

## Do not
Let each system download the external list itself, store only name text, or hard-delete retired entries.

Open item: identify the actual sets in use and map each to the table above.
