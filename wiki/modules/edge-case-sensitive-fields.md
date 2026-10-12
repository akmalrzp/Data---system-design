---
type: module-type
title: "Edge case: sensitive fields"
tags: [edge-case,proposal]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Edge case: sensitive fields

Salary, national ID and similar fields are not broadcast. The event carries non-sensitive fields; a consumer with a need reads the sensitive field from an authorised endpoint that checks authorisation on every read.

Consequences: the consumer cannot hold a cached copy by default; if it must, the copy is scoped, justified, and covered by [security-and-erasure-propagation](../patterns/security-and-erasure-propagation.md).

See [payload-sensitive-fields](../patterns/payload-sensitive-fields.md).
