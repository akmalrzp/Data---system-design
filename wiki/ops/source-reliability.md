---
type: ops
title: "Source reliability"
tags: [unverified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Source reliability

How far each part of this wiki can be trusted. Tags on pages: `unverified`, `partly-verified`, `proposal`.

| Area | Status | Pages |
|---|---|---|
| Ownership, IDs, system of record, anti-corruption layer | Not source-verified (background knowledge) | [opaque-permanent-id](../concepts/opaque-permanent-id.md), [system-of-record](../concepts/system-of-record.md), [anti-corruption-layer](../concepts/anti-corruption-layer.md) |
| Integration styles, thin vs fat events, coupling | Entirely unverified | [payload-thin-vs-fat-events](../patterns/payload-thin-vs-fat-events.md), [flow-events-plus-read-api](../patterns/flow-events-plus-read-api.md) |
| Delivery semantics, outbox, idempotency, ETags, tombstones, sagas | Partly verified (Confluent, microservices.io, Stripe, Azure, Debezium, Ed-Fi) | [rule-idempotent-versioned-apply](../patterns/rule-idempotent-versioned-apply.md), [rule-ordering-per-entity](../patterns/rule-ordering-per-entity.md), [rule-deletes-as-state](../patterns/rule-deletes-as-state.md) |
| Contracts, compatibility, versioning, deprecation, errors | Partly verified (Zalando, Google AIPs, Confluent, RFC 9457/9745/9413) | [rule-additive-only-contract](../patterns/rule-additive-only-contract.md), [rule-deprecation-and-sunset](../patterns/rule-deprecation-and-sunset.md), [decision-contract-versioning-style](../decisions/decision-contract-versioning-style.md) |
| Units, positions, headcount, external reference patterns | Design reasoning, not researched | [consumer-index-user](../modules/consumer-index-user.md), [projection-module](../modules/projection-module.md), [external-reference-sets](../decisions/external-reference-sets.md), use cases |
| Scope criteria, feature placement, accountability default | Assistant proposals | [module-scope-criteria](../modules/module-scope-criteria.md), [feature-placement-test](../modules/feature-placement-test.md), [accountability-default](../tables/accountability-default.md) |

**No usable source**: retries and backoff, dead-letter queues, circuit breakers, tracing, SLOs, drift detection, OAuth/mTLS, personal-data erasure law (UU PDP, GDPR; confirm with legal), snapshot-plus-change-feed bootstrap, event-contract testing.

**Other cautions**: the Idempotency-Key header is an expired IETF draft, not a standard; Stripe's versioning post is from 2017; page fetching was largely blocked during the research, so verify the unverified sections before relying on them in an ADR.

Origin: [api-design-for-system-integration](../sources/api-design-for-system-integration.md), [osdm-integration-summary](../sources/osdm-integration-summary.md).
