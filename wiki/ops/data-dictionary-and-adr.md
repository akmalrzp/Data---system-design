---
type: ops
title: "Data dictionary and ADRs"
tags: [proposal]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Data dictionary and ADRs

Each entity and each reference set gets a data dictionary entry, and each design choice gets an architecture decision record (ADR).

**Data dictionary entry** (minimum): entity name; owner module and data steward; ID format; business keys; fields published and their sensitivity; lifecycle states; split/merge applicability; consumers and their type; contract location and version; for external sets: authority, edition, update schedule, change approval.

**ADR** (minimum): context, options considered, decision, consequences, date. Record at least: technology choices ([technology-neutral-requirements](../patterns/technology-neutral-requirements.md)), the choices in [decision-subscribe-vs-call-on-demand](../decisions/decision-subscribe-vs-call-on-demand.md), [decision-delete-policy-and-erasure](../decisions/decision-delete-policy-and-erasure.md), [decision-contract-versioning-style](../decisions/decision-contract-versioning-style.md), and the keying choice for each external set ([external-reference-sets](../decisions/external-reference-sets.md)).

Verify the unverified research sections before an ADR relies on them ([source-reliability](source-reliability.md)).
