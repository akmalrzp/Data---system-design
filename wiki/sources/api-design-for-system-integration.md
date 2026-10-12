---
type: source
title: "API design for system integration (research report)"
tags: [source, integration, api, research]
authors: [akmal.rizkiputra]
url: ""
raw: raw/api-design-for-system-integration.md
ingested: 2026-10-09
created: 2026-10-09
updated: 2026-10-09
---

# API design for system integration (research report)

Research report on keeping independent systems consistent: ownership, identifiers, integration styles, delivery semantics, contracts and versioning, security, and an HR Core employee recommendation.

## Evidence quality (as stated in the report)
- Identifiers, ownership, system of record, anti-corruption layer: not source-verified.
- Integration styles, thin vs fat events: entirely unverified.
- Delivery semantics, outbox, idempotency keys, ETags, tombstones, sagas: partly verified (Confluent, microservices.io, Stripe, Azure, Debezium, Ed-Fi).
- Contracts, compatibility modes, versioning, deprecation, errors: partly verified (Zalando, Google AIPs, Confluent, RFC 9457, 9745, 9413).
- No usable source for: retries and backoff, dead-letter queues, circuit breakers, tracing, SLOs, drift detection, OAuth/mTLS, personal-data erasure law.

## Where this fits
[opaque-permanent-id](../concepts/opaque-permanent-id.md), [system-of-record](../concepts/system-of-record.md), [anti-corruption-layer](../concepts/anti-corruption-layer.md), [payload-thin-vs-fat-events](../patterns/payload-thin-vs-fat-events.md), [flow-events-plus-read-api](../patterns/flow-events-plus-read-api.md), [rule-idempotent-versioned-apply](../patterns/rule-idempotent-versioned-apply.md), [rule-ordering-per-entity](../patterns/rule-ordering-per-entity.md), [rule-deletes-as-state](../patterns/rule-deletes-as-state.md), [rule-additive-only-contract](../patterns/rule-additive-only-contract.md), [rule-deprecation-and-sunset](../patterns/rule-deprecation-and-sunset.md), [rule-contract-testing](../patterns/rule-contract-testing.md), [decision-contract-versioning-style](../decisions/decision-contract-versioning-style.md), [security-and-erasure-propagation](../patterns/security-and-erasure-propagation.md), [source-reliability](../ops/source-reliability.md).
