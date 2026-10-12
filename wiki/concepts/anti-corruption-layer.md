---
type: concept
title: "Anti-corruption layer"
tags: [principle,unverified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Anti-corruption layer

An adapter at the consumer's edge converts the owner's published shape into the consumer's internal model. Only the adapter knows the owner's vocabulary, so a contract change touches one place.

Practical rules:
- Parse and validate in one place.
- Ignore unknown additive fields and unknown enum values; reject malformed or missing required data (see [rule-additive-only-contract](../patterns/rule-additive-only-contract.md)).
- Never expose the owner's types inside the consumer's domain code.

The alternative, one enterprise-wide canonical model that every module must follow, couples all modules to one change process. This guide prefers a small published model per owner. Evidence: not source-verified (see [source-reliability](../ops/source-reliability.md)).
