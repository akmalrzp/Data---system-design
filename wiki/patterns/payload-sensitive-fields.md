---
type: pattern
title: "Payload: sensitive fields"
tags: [proposal]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Payload: sensitive fields

Keep salary, national ID and similar data out of events. The owner exposes them through an endpoint that authorises each read and scopes fields per consumer.

Reasons: replicated sensitive data multiplies erasure and breach obligations ([security-and-erasure-propagation](security-and-erasure-propagation.md)) and defeats per-read authorisation.

Edge case: [edge-case-sensitive-fields](../modules/edge-case-sensitive-fields.md). Grounding: API object-property-level authorisation and unsafe API consumption are named risks in the OWASP API Top 10 (2023), per the research report; the field-scoping rule is an inference.
