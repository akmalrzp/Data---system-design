---
type: source
title: "OSDM system integration summary"
tags: [source, integration, hr-example]
authors: [akmal.rizkiputra]
url: ""
raw: raw/osdm-integration-summary.md
ingested: 2026-10-09
created: 2026-10-09
updated: 2026-10-09
---

# OSDM system integration summary

Author's summary (dated 2026-10-09) of the integration and API design research, with an HR worked example. It is the main basis of this wiki.

## What it contains
- Core answer: one owner per record, permanent opaque ID, read-only cache in consumers, small versioned additive contract, events plus read API, idempotent version-guarded apply, anti-corruption layer, no shared databases.
- Reliability table: ownership/ID and integration-style sections are not source-verified; delivery and contract sections are partly verified.
- Worked examples: A = HR Core (Employee), B = Payroll, C = Unit and Position owner, D = unit requirements.
- Handling of external reference sets (region codes, tax status, education levels).
- Open points: verification, erasure law, subscribe vs call on demand, mapping real external reference sets.

## Reliability caveat
Sections 5 to 7 of the raw file (C owns Unit and Position, D uses units as an index, external references) are design reasoning, not cited research. Pages derived from them carry the tag `proposal`.

## Where this fits
[principles](../concepts/principles.md), [worked-example](../concepts/worked-example.md), [data-owner-broadcaster](../modules/data-owner-broadcaster.md), [consumer-attribute-user](../modules/consumer-attribute-user.md), [consumer-index-user](../modules/consumer-index-user.md), [external-reference-sets](../decisions/external-reference-sets.md), [decision-subscribe-vs-call-on-demand](../decisions/decision-subscribe-vs-call-on-demand.md). See also [api-design-for-system-integration](api-design-for-system-integration.md) and [source-reliability](../ops/source-reliability.md).
