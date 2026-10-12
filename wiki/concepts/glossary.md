---
type: concept
title: "Glossary"
tags: [principle]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Glossary

- **Module**: an independently deployable system with its own database and release cycle (A, B, C, D in examples).
- **Data owner / system of record**: the module allowed to create and change a record. See [system-of-record](system-of-record.md).
- **Broadcaster**: an owner in its role of publishing change events and exposing a read API.
- **Consumer**: a module that holds references to or copies of another module's data.
- **Reference data**: data owned by one module and referred to by others (unit, position, region code).
- **Master reference table**: the owner's authoritative table. See [table-master-reference](../tables/table-master-reference.md).
- **Cache (of master)**: a consumer's read-only local copy. See [table-master-cache](../tables/table-master-cache.md).
- **Transaction table**: a consumer's or owner's own business records that reference IDs. See [table-transaction](../tables/table-transaction.md).
- **Projection**: derived data (for example counts per unit) built from events, not copied records. See [table-projection](../tables/table-projection.md).
- **Crosswalk**: mapping between internal IDs and external codes. See [table-crosswalk](../tables/table-crosswalk.md).
- **Contract**: the published, versioned shape of API responses and events.
- **Event envelope**: metadata fields on every event. See [payload-event-envelope](../patterns/payload-event-envelope.md).
- **Version**: a monotonic number per record, increased on every change.
- **Tombstone**: a retained marker that a record is deleted or inactive; here a versioned state, not an absence.
- **`replaced_by`**: pointer from a retired record to its successor(s) after merge or split.
- **Effective dating**: `effective_from` / `effective_to` on records whose meaning depends on a date.
- **Anti-corruption layer**: adapter translating an external model into the local one. See [anti-corruption-layer](anti-corruption-layer.md).
- **Data steward**: named person accountable for a reference set. See [external-reference-sets](../decisions/external-reference-sets.md).
