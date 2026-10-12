---
type: module-type
title: "Edge case: owner unavailable"
tags: [edge-case,proposal]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Edge case: owner unavailable

A consumer working from its local cache continues to operate; it cannot create new references to IDs it has never seen. A consumer calling the owner on demand fails with the owner.

Rules:
- Prefer local cache for validation and display.
- Queue events for later application ([rule-idempotent-versioned-apply](../patterns/rule-idempotent-versioned-apply.md)).
- For writes that need an unseen reference, either reject with a clear error or accept as pending and re-validate later; decide per business rule.
- Document the owner's availability expectation in the contract.

See [decision-subscribe-vs-call-on-demand](../decisions/decision-subscribe-vs-call-on-demand.md).
