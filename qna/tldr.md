**TL;DR: Integrating Independent OSDM Modules**

### Core Idea
Design independent modules that share reference data without coupling. Each entity has **exactly one owner** (system of record). Everyone else holds a derived, read-only copy. No shared databases, no cross-module foreign keys.

### 10 Core Principles
1. One owner per record.
2. Permanent opaque ID (immutable, never reused, no business meaning — UUID-style).
3. Consumers store only the ID + fields they need (local cache).
4. Small, versioned, additive public contract (separate from internal model).
5. Changes flow as events + a read API for lookup/catch-up.
6. Assume duplicates, disorder, and loss → apply idempotently with version guards.
7. Translate at the edge (anti-corruption layer).
8. No shared DBs or cross-module FKs.
9. Lifecycle changes are explicit versioned states (not absence).
10. Accept eventual consistency and show freshness (“as of” timestamps).

### Module Types (per entity)
| Type | Role | Example |
|------|------|---------|
| **Owner / Broadcaster** | Creates, changes, retires records; publishes events + read API | C owns Unit/Position; A owns Employee |
| **Consumer Type 1** (attributes) | Uses data as descriptive fields | B (Payroll) shows unit/position names |
| **Consumer Type 2** (index) | Uses ID as business key of its own records | D stores “required headcount per unit” |
| **Hybrid** | Owns some entities, consumes others | A owns Employee, consumes Unit/Position |
| **Projection holder** | Derives facts (e.g. headcount) from events, not full copies | D’s unit → active count |

### Table Types
- **Master reference** (owner only) — authoritative, versioned, outbox on every change.
- **Cache** (consumer) — read-only copy of owner’s data; apply only newer versions.
- **Transaction** — module’s own business records (hold foreign IDs, validate against local cache).
- **Projection** — rebuildable derived facts (must carry previous values where needed).
- **Crosswalk** — maps external codes ↔ internal IDs.

### Communication Rules
- **Default flow**: Owner writes business change + outbox in one transaction → relay publishes event → consumers apply idempotently. Read API for bootstrap, catch-up, lookup.
- **Thin vs fat events**: Fat for non-sensitive attributes; thin + authorised read for sensitive data.
- **Key rules**:
  - Additive-only contracts (add fields/enums OK; never remove/rename/retype).
  - Idempotent, version-guarded apply (ignore ≤ current version).
  - Ordering per entity only (partition by ID + monotonic version).
  - Validate IDs against local cache before accepting writes.
  - Deletes = explicit status (`inactive`/`terminated`/`deleted`) + version; use `replaced_by` for merge/split.
  - No hard deletes except legal erasure (then propagate to every copy).

### Common Use Cases (what happens)
- **New record / update / rename / reparent** → owner increments version, publishes; consumers update cache if newer.
- **Split / Merge** → owner creates successors or chooses survivor, marks original(s) inactive with `replaced_by`. Type-2 consumers **never auto-move** records — flag for human review.
- **Delete / Erasure** → normal retirement = status change; legal erasure = anonymise or hard-delete + force propagation + reconcile.
- **Bootstrap / late joiner / gaps** → page owner’s list API → same apply path → reconcile.
- **Owner down** → consumers keep working from cache; cannot create references to unknown IDs.

### Operations Essentials
- Assign a data steward for every external reference set.
- Maintain a data dictionary entry + ADR for every entity and design choice.
- Monitor lag, drift (via reconciliation), rejects, and placeholders.
- Prefer local cache for reference data; call owner on demand only for sensitive or exactness-critical data.

### Design Checklist (quick)
- Classify every entity (owner / type-1 / type-2).
- Acyclic dependency graph.
- Correct table types + accountability mechanism.
- Owner provides: opaque IDs, versions, outbox, events, read API, additive contract.
- Consumer has: version-guarded apply path, anti-corruption layer, unknown-ID handling, bootstrap + reconciliation.
- Lifecycle states + `replaced_by` defined; Type-2 has review process for flagged records.
- Erasure path designed and tested.

**Bottom line**: Own once, publish a small additive contract via events + read API, let everyone else keep a version-guarded local cache, and treat lifecycle changes as explicit states. Independence + eventual consistency by design.