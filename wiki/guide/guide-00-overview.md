---
type: guide
title: "0. Purpose, scope and principles"
tags: [guide]
sources: [osdm-integration-summary,api-design-for-system-integration,author-decisions-2026-10-09]
created: 2026-10-09
updated: 2026-10-09
---

# 0. Purpose, scope and principles

This guide explains how to design independent modules that share reference data, for the Organisasi & SDM domain. It is technology-neutral and written for architects and developers. Modules A, B, C, D are examples ([worked-example](../concepts/worked-example.md)).

Reading order: this section first; then module types, tables, communication, use cases; operations and appendices as reference. The sections are ordered so that each depends only on earlier ones (communication patterns come before the use cases that use them).

Sections: [guide-01-module-types](guide-01-module-types.md), [guide-02-table-types](guide-02-table-types.md), [guide-03-communication](guide-03-communication.md), [guide-04-use-cases](guide-04-use-cases.md), [guide-05-operations](guide-05-operations.md), [guide-06-appendices](guide-06-appendices.md).

Mapping to the author's starting outline: its section 1 is guide section 1, its 2 is 2, its 4 (communication) is now section 3, and its 3 (use cases) is now section 4.

Evidence is uneven; see [source-reliability](../ops/source-reliability.md). Pages tagged `proposal` are reasoned recommendations.

## Pages
- [problem-statement](../concepts/problem-statement.md)
- [principles](../concepts/principles.md)
- [system-of-record](../concepts/system-of-record.md)
- [opaque-permanent-id](../concepts/opaque-permanent-id.md)
- [anti-corruption-layer](../concepts/anti-corruption-layer.md)
- [eventual-consistency](../concepts/eventual-consistency.md)
- [glossary](../concepts/glossary.md)
- [worked-example](../concepts/worked-example.md)
