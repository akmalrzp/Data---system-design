## 1. Validation

**Overall:** The guide is coherent and internally consistent. Its structure is logical: principles → module types → table types → communication → use cases → operations → appendices. Cross-references and anchors appear consistent. The evidence notes are unusually honest and useful.

**Strengths**
- Clear core rule: one owner per record, opaque permanent ID, consumers keep read-only copies.
- Good separation of owner vs consumer types (attributes vs index).
- Strong communication rules: no shared DB, additive contracts, idempotent version-guarded apply.
- Use cases cover the hard cases: bootstrap, split, merge, delete, late joiner, external edition change.
- Accountability defaults are practical and revisable.

**Issues found**
1. **Jargon overload.** Many terms are used before or without plain definitions: outbox, idempotent, version-guarded, reconciliation, bootstrap, catch-up, projection, crosswalk, effective dating, optimistic concurrency, tombstone, etc.
2. **Repetition.** The same rules are restated in multiple sections. This is safe but makes it harder to scan.
3. **Minor ambiguity.** “Publish only data it owns” can confuse when an owner publishes a reference ID owned by another module. Clarify: publish your own facts and IDs you reference, not another owner’s descriptive attributes.
4. **Erasure practicality.** Backups and logs are correctly in scope, but no operational mechanism is described. This is an open legal/ops item.
5. **Contract testing gap.** The guide says classic consumer-driven tools fit event-driven systems poorly, but does not name a preferred alternative beyond spec diffing and bi-directional testing.

**Conclusion:** Valid as a design guide. It should be treated as a set of reasoned proposals, not a fully source-verified standard. The revised version below keeps the same structure, shortens the prose, and expands the glossary.

---

# Revised guide: integrating independent OSDM modules

Technology-neutral guide for architects and developers. Modules A, B, C, D are examples.

## Contents

- [0. Purpose, scope and principles](#guide-00-overview)
- [1. Module types](#guide-01-module-types)
- [2. Table types and accountability](#guide-02-table-types)
- [3. Inter-system communication patterns](#guide-03-communication)
- [4. Use cases](#guide-04-use-cases)
- [5. Operations and governance](#guide-05-operations)
- [6. Appendices: decisions, checklist, reliability](#guide-06-appendices)

---

<a id="guide-00-overview"></a>
# 0. Purpose, scope and principles

This guide explains how independent modules share reference data while staying independent: separate databases, release cycles, and tolerance for downtime.

Example: System A produces data A1. System B uses it. Both must refer to the same A1, but neither should depend on the other’s database or release cycle.

The guide answers four questions:
1. What module types exist, and where does a feature belong?
2. What table types exist, and how is each made accountable?
3. How do modules communicate without coupling?
4. What happens in bootstrap, new record, update, split, merge, delete?

## Problem statement

System A owns data A1. System B uses it. They must agree on the reference while remaining independent: separate releases, separate databases, and tolerance for the other being down or changing.

## Core principles

1. **One owner per record.** Exactly one module creates and changes a record: the system of record. Everyone else keeps a derived copy.
2. **Permanent opaque ID.** The owner issues an ID that never changes, is never reused, and carries no business meaning.
3. **Consumers store the ID plus only the fields they need.** This is a read-only cache. If a consumer must control a field, that field belongs in the consumer’s own table.
4. **Small, versioned, additive contract.** Keep the published contract separate from the owner’s internal model.
5. **Changes flow as events; a read API serves lookup and catch-up.**
6. **Assume duplicates, disorder, and loss.** Apply changes idempotently and only when the version is newer.
7. **Translate at the edge.** Each consumer converts the owner’s model into its own.
8. **No shared databases. No cross-module foreign keys.**
9. **State changes, not absence.** Inactive, replaced, and deleted are explicit versioned states.
10. **Accept eventual consistency.** Show freshness.

## System of record

For each entity, exactly one module is the system of record: the only place where the entity is created, changed, or retired. All other copies are derived and read-only.

Consequences:
- Ownership is decided once per entity and recorded in the data dictionary.
- A consumer that needs its own authoritative field owns that field in its own table.
- Field-level disputes: ask whether the consumer really needs authority. If yes, name the fields differently.

## Opaque permanent ID

The owner issues an identifier at record creation.

Rules:
- **Immutable:** never changes.
- **Never reused:** not even after deletion.
- **Opaque:** no name, unit, date, or national-ID content.
- **Not a business key:** `employee_number` is an attribute, not the join key.
- **Globally unique enough:** UUID or equivalent.

Consumers store it as a foreign reference with a local unique constraint.

## Anti-corruption layer

An adapter at the consumer’s edge converts the owner’s published shape into the consumer’s internal model. Only the adapter knows the owner’s vocabulary.

Practical rules:
- Parse and validate in one place.
- Ignore unknown additive fields and unknown enum values.
- Reject malformed or missing required data.
- Never expose the owner’s types inside the consumer’s domain code.

Alternative: one enterprise-wide canonical model. This couples all modules to one change process. The guide prefers a small published model per owner.

## Eventual consistency and freshness

Copies in consumers lag the owner. Design for it:
- Show an “as of” timestamp wherever cached or projected data is displayed.
- Validate against the local cache, not a live call, unless exactness at decision time is required.
- Detect and repair drift with reconciliation and monitoring.
- Tolerate an unknown ID: store it, show a placeholder, fetch from the owner on the miss.

## Glossary

Plain-language definitions of terms used in this guide.

- **Module:** An independently deployable system with its own database and release cycle.
- **System of record / data owner:** The module allowed to create and change a record.
- **Broadcaster:** An owner in its role of publishing change events and exposing a read API.
- **Consumer:** A module that holds references to or copies of another module’s data.
- **Reference data:** Data owned by one module and referred to by others, e.g. unit, position, region code.
- **Master reference table:** The owner’s authoritative table.
- **Cache of master reference:** A consumer’s read-only local copy.
- **Transaction table:** A module’s own business records that reference IDs.
- **Projection / projection table:** Derived data built from events, e.g. counts per unit. Not copied records.
- **Crosswalk table:** A mapping between internal IDs and external codes.
- **Contract:** The published, versioned shape of API responses and events.
- **Event envelope:** Metadata fields on every event, e.g. event ID, entity ID, version, timestamp.
- **Version:** A monotonic number per record, increased on every change.
- **Tombstone:** A retained marker that a record is deleted or inactive. Here it is a versioned state, not an absence.
- **`replaced_by`:** A pointer from a retired record to its successor(s) after merge or split.
- **Effective dating:** `effective_from` / `effective_to` on records whose meaning depends on a date.
- **Anti-corruption layer:** An adapter that translates an external model into the local one.
- **Data steward:** A named person accountable for a reference set.
- **Outbox:** A table where the owner writes a change event in the same transaction as the business change. A relay publishes it later.
- **Idempotent:** Safe to apply more than once. The result is the same as applying it once.
- **Version-guarded apply:** Only apply an event if its version is greater than the stored version.
- **Reconciliation:** A scheduled comparison between a consumer’s copy and the owner, followed by repair.
- **Bootstrap:** Filling an empty cache from the owner’s read API or a replay of current state.
- **Catch-up:** Fetching changes missed since a cursor or last event.
- **Cursor pagination:** Paging through a list using an opaque token, not page numbers.
- **Optimistic concurrency:** Prevent lost updates by checking a version or ETag before writing.
- **ETag / `If-Match`:** HTTP headers used for optimistic concurrency. A mismatch returns 412.
- **Schema registry:** A service that stores and enforces event schema compatibility.
- **FULL / FULL_TRANSITIVE:** Schema compatibility modes that let either side upgrade first.
- **Thin event:** An event with only ID and change type. The consumer calls back for details.
- **Fat event:** An event carrying the fields consumers need.
- **Sensitive fields:** Salary, national ID, etc. Not broadcast by default.
- **Drift:** A lasting mismatch between a copy and its owner.
- **Lag:** The delay between the owner’s change and the consumer’s copy.
- **Placeholder:** A temporary local row for an unknown ID, resolved later.
- **Snapshot:** A stored copy of referenced values, kept so a document can reproduce the past.
- **Lineage columns:** Columns such as `source_version`, `updated_at`, `last_synced_at`.
- **Processed-event log:** A consumer record of which event IDs or versions were applied.
- **Bitemporal history:** History that tracks both valid time and recorded time.
- **Event store:** A system where events are the source of truth.
- **Saga:** A coordinated sequence of local transactions with compensating actions.
- **Partition key:** The key used to keep related events in order, usually entity ID.
- **At-least-once delivery:** A message may be delivered more than once.
- **Exactly-once delivery:** A message is processed once. Not assumed across separate systems.
- **Tolerant reader:** A consumer that ignores unknown fields and enum values.
- **Deprecation / Sunset:** Headers or markers that warn a contract field or endpoint will be removed.
- **Consumer-driven contract testing:** Consumers record what they use and replay it against the owner.
- **Bi-directional contract testing:** Compare the owner’s spec with consumers’ recorded usage.
- **Erasure:** Removing or anonymising personal data on legal request.
- **Anonymisation:** Replacing personal fields with null or placeholder values.
- **Data dictionary:** A record of each entity’s owner, fields, lifecycle, consumers, and contract.
- **ADR:** Architecture decision record. Context, options, decision, consequences, date.
- **SLO:** Service-level objective, e.g. maximum acceptable lag.
- **Dead-letter queue:** A holding area for events that cannot be processed.
- **Circuit breaker:** A pattern that stops calls to a failing dependency.
- **mTLS / OAuth:** Security mechanisms for service identity and authorisation.
- **Business key:** A human-facing identifier, e.g. employee number or unit code.
- **Hybrid module:** A module that owns some entities and consumes others.
- **External reference set:** Reference data from outside the organisation, e.g. region codes.

## Worked example: modules A, B, C, D

| Module | Role | Owns | Uses |
|---|---|---|---|
| A (HR Core) | Owner, consumer of C | Employee, assignment to unit and position | Unit, Position from C |
| B (Payroll) | Consumer type 1: attributes | Pay grade, tax status | Employee from A; Unit, Position names from C |
| C (Org structure) | Owner | Unit, Position | None |
| D (Requirements) | Consumer type 2: index and projection | Required headcount per unit | Unit from C; employee counts per unit from A |

Patterns:
- A broadcasts `employee_id`, `unit_id`, `position_id`, not names. Names belong to C.
- C broadcasts `unit.changed`, `position.changed`. A, B, D keep local caches.
- B resolves names by joining on IDs in its own cache of C.
- D uses `unit_id` as the business key of its requirement records. Unit lifecycle changes in C affect D directly.
- Sensitive fields stay out of events.

---

<a id="guide-01-module-types"></a>
# 1. Module types

Modules are classified per entity: owner, consumer using data as attributes, or consumer using data as an index. A real module is usually several at once.

## Module scope criteria

Use these measurements to decide where a module boundary falls.

| # | Criterion | Question | Boundary signal |
|---|---|---|---|
| 1 | Decision authority | Who decides the value? | Different decision-makers mean different modules |
| 2 | Accountability | Who answers for correctness and audit? | One accountable role per entity |
| 3 | Rate and reason of change | Does it change for the same reasons and pace? | Different change drivers mean different modules |
| 4 | Lifecycle | Is it created, retired, archived on the same schedule? | Different lifecycles mean different modules |
| 5 | Access and sensitivity | Is audience or authorisation the same? | Different confidentiality means separate module or fields |
| 6 | Consistency need | Must it change atomically with neighbours? | Atomic need means same module |
| 7 | Consumer pattern | Do consumers need it live or lagged? | Lag-tolerant data can live elsewhere |
| 8 | Team and release independence | Can one team release it alone? | Separate teams suggest separate modules |

Rules of thumb:
- Entities that must change in one transaction belong together.
- If two entities differ on criteria 1, 2, and 5, split them.
- If a boundary forces constant synchronous calls, it is probably wrong.

## Feature placement test

Apply in order. Stop at the first decisive answer.

1. Does the feature create or change a record this module owns? → Yes: it belongs here.
2. Does it create or change a record owned by another module? → No: call the owner’s contract or ask for a capability.
3. Does it only read another module’s data to display or validate? → Yes: use the local cache.
4. Does it need a value that must be authoritative here but derived elsewhere? → Make it a projection or own the field here.
5. Does it need data the owner has not published? → Request a contract addition. Do not read the owner’s database.
6. Does it mix data from two owners in one atomic write? → Redesign: separate writes per owner, use a compensating process, or move entities into one module.

## Data owner and broadcaster

**Role:** Creates, changes, and retires records. Issues IDs. Publishes changes.

**Must provide**
- Master reference tables.
- A change feed: versioned events through a transactional outbox.
- A read API for lookup by ID and cursor-paginated catch-up by `updated_after`.
- A published, versioned, additive contract.
- Lifecycle states instead of hard delete, with `replaced_by` for merge and split.
- Field scoping per consumer for sensitive data.

**Must not**
- Publish data it does not own. It may publish IDs it references, but not another owner’s descriptive attributes.
- Expose its internal model or database.
- Reuse or change an ID.

## Consumer type 1: reference data as attributes

**Role:** Uses another module’s records as descriptive attributes of its own records. The reference does not define the consumer’s records.

Example: B stores `employee_id` and shows the unit and position name. The payroll record exists with or without a particular unit.

**Design**
- Keep a cache of the master. ID is unique key. Store only needed fields.
- Own records hold the foreign ID. No cross-system foreign key constraint.
- Resolve names by joining on IDs in the local cache.
- Unknown ID: store it, show a placeholder, fetch from the owner on the miss.
- Inactive or replaced reference: keep the record, display status, follow `replaced_by` for display.

**Impact of owner lifecycle:** Low. Renames change display only. Retirement changes display and flags.

## Consumer type 2: reference data as index

**Role:** Uses another module’s ID as the business key or classification axis of its own records. The reference defines what the consumer’s records mean.

Example: D stores “required employees per unit.” `unit_id` identifies the requirement.

**Design**
- Same cache pattern as type 1, plus:
- Validate the referenced entity exists and is active before accepting a record. For effective-dated records, validate on the effective date.
- Effective-date records so they stay meaningful after the reference changes.
- Treat owner lifecycle events as business events:
  - Inactive: flag for review or close with `effective_to`.
  - Merge or split: flag records and let a person decide. Never move them silently.
  - Hierarchy change: roll-up totals change. Read `parent_unit_id` from the local cache.
- If it needs derived data from another owner, keep a projection, not copies.
- Show “as of” timestamps on projections.
- If another module emits the events the projection counts, its cache may differ from yours. See divergent reference caches.

**Impact of owner lifecycle:** High. Agree the lifecycle contract with the owner early.

## Hybrid module

Most real modules own some entities and consume others.

Rules:
- Classify per entity, not per module.
- Keep owned tables and caches physically and logically separate.
- Validate assignments against the local cache before accepting them.
- Never republish a consumed entity’s attributes. Publish the ID only.
- Watch for dependency cycles.

## Projection holder

A module that needs facts derived from another owner’s data, not the records themselves.

Example: D needs active headcount per unit. It subscribes to A and keeps `unit_id -> active count`, not employee records.

Rules:
- Events must carry what the projection needs, including previous values. A transfer event includes `previous_unit_id` so the old unit is decremented.
- The projection must be rebuildable from the owner’s events or API.
- Display “as of” timestamps.
- Do not reject the owner’s events against your own cache of a third module.
- Alternative: call the owner’s read API when exactness at read time matters.

## Owner of external reference sets

Reference sets from outside the organisation have no inter-system owner. Assign one internal module as owner and a named data steward.

The owner:
- Imports from the external authority and validates.
- Publishes versioned events or a dataset plus a read API.
- Keeps old codes resolvable and never hard-deletes retired entries.
- Announces edition changes with a cutoff date.

Consumers reference entries by code or ID, never by text.

## Edge case: field ownership disputes

Situation: Consumer B needs a field to be authoritative, but A owns the record.

Resolution, in order:
1. Ask whether B really needs authority. If not, B uses A’s value.
2. If B needs its own value, B owns that field in its own table, keyed by the same ID.
3. If both are needed, name them differently. One name must never carry two meanings.

## Edge case: sensitive fields

Salary, national ID, and similar fields are not broadcast. The event carries non-sensitive fields. A consumer with a need reads the sensitive field from an authorised endpoint that checks authorisation on every read.

Consequences:
- The consumer cannot hold a cached copy by default.
- If it must, the copy is scoped, justified, and covered by erasure propagation.

## Edge case: hierarchy changes

Reparenting a unit in C changes roll-ups in every consumer that aggregates by hierarchy.

Rules:
- C publishes `parent_unit_id` and a version. A reparent is a normal update.
- Consumers read the hierarchy from their local cache and recompute roll-ups. Do not store roll-ups as master data.
- Effective-date the change if history matters.
- Cycles in the hierarchy are rejected by the owner.

## Edge case: circular dependencies

A consumes C. C must not consume A’s entity in a way that A needs to start. Circular data dependencies prevent bootstrap and make ordering undecidable.

Rules:
- Draw the dependency graph of entities, not modules. It must be acyclic per entity.
- If two modules each need the other’s data, move the shared data to a third owner, or use IDs only on one side with lazy resolution.
- Bootstrap in dependency order.

## Edge case: owner unavailable

A consumer working from its local cache continues to operate. It cannot create new references to IDs it has never seen. A consumer calling the owner on demand fails with the owner.

Rules:
- Prefer local cache for validation and display.
- Queue events for later application.
- For writes that need an unseen reference, reject with a clear error or accept as pending and re-validate later. Decide per business rule.
- Document the owner’s availability expectation in the contract.

## Edge case: business key vs ID

Business keys are human-meaningful and may be reissued, reformatted, or corrected. IDs are not.

Rules:
- Join on IDs. Expose business keys as attributes only.
- Enforce uniqueness of the business key in the owner. Use effective dating if it can be reused.
- External standard codes may be the key for external reference sets under the conditions in External reference sets.

## Edge case: divergent reference caches

Two consumers cache the same owner’s entity. One emits events that the other interprets through its own copy. They can disagree for a while.

Example: A and D both subscribe to C’s units. A validates assignments against its cache of C and emits `employee.changed` with `unit_id`. D keeps a headcount projection and reads unit status and `parent_unit_id` from its own cache of C.

### Who is authoritative
- C is authoritative for what a unit is: exists, active, name, parent.
- A is authoritative for which unit an employee is assigned to.
- Neither A’s nor D’s cache of C is authoritative.
- A does not send unit data to D. It sends `unit_id` only. D builds the projection itself.

Both caches come from the same versioned stream. A mismatch is normally lag. Lasting divergence means a cache missed events.

### Case 1: A’s cache is ahead of D’s
C creates a unit. A learns first, accepts an assignment, and emits an event with a `unit_id` D does not know.

- D applies the count keyed by `unit_id`. It does not reject A’s event against its own cache. A already validated it.
- D shows a placeholder for the unit and calls C’s read API on the miss.
- Roll-ups cannot place the count until D has the unit’s `parent_unit_id`.

### Case 2: D’s cache is ahead of A’s
C marks a unit inactive or sets `replaced_by`. D learns first. A, still on the older copy, keeps assigning to the old unit.

- D’s count shows employees on an inactive unit. That matches what A holds, so the count is correct. The assignments need correcting.
- D flags the unit. It does not move counts via `replaced_by` itself.
- When A reassigns, its events carry `previous_unit_id` and the count moves.
- If A keeps assigning beyond normal lag, A’s cache is stale or A is not processing C’s lifecycle events. Alert on it.

### Case 3: lasting divergence
A missed event or bug leaves a cache wrong indefinitely.

- A and D each reconcile their cache against C. Never reconcile one consumer’s cache against another’s.
- D also reconciles its projection against A per unit.

### Optional: carry the version A validated against
A adds the unit version it validated against, e.g. `unit_version`, to its assignment event. D compares it with its own cache:
- A’s version is newer: D re-fetches the unit from C.
- D’s version is newer: A acted on an older view. D can flag the record.

This is an additive field.

### Rule
The projection trusts A for who sits where and C for what the unit is. D never checks A’s facts against its own cache of C.

---

<a id="guide-02-table-types"></a>
# 2. Table types and accountability

Each table type has different accountability needs. No audit requirement exists yet, so the default is revisable.

## Master reference table (owner)

The authoritative table in the data owner module.

**Typical columns**
- `id` (opaque permanent), business key as attribute, `version`, `status`, `replaced_by`, `effective_from`, `effective_to`, `updated_at`.
- Attributes owned by this module.
- Parent references for hierarchies, e.g. `parent_id`.

**Rules**
- Only the owner writes.
- Every change increments `version`.
- Retirement is a status, not a delete. Exception: erasure.
- Every change writes an outbox record in the same transaction.

**Accountability:** Transaction log or outbox for every change, plus history where past values matter.

## Cache of master reference (consumer)

A consumer’s read-only local copy of an owner’s records.

**Typical columns**
- Local primary key, `source_id` (owner’s ID, unique), `source_version`, only needed cached fields, `status`, `replaced_by`, `last_synced_at`.

**Rules**
- Written only by the apply path. Never edited by users or other processes.
- Apply only if event version is greater than `source_version`.
- Store deletion and inactive states, not absence.
- Unknown IDs: placeholder row or lazy fetch.
- Local extensions go in a separate table keyed by the owner’s ID, not in the cache.

**Accountability:** Processed-event log committed with the change, plus reconciliation results. Lineage columns show which owner state the copy reflects.

## Transaction table

A module’s own business records: assignments, requirements, payroll runs. They reference IDs from caches or from their own master tables.

**Rules**
- Hold foreign IDs, not copied descriptive text, unless the record must be reproducible as it was.
- No cross-system foreign key constraint. Validate against the local cache on write.
- Effective-date records whose meaning depends on time.
- Append-only or versioned for records that must be auditable.

**Snapshot or reference?**
- Store the reference when the current name is wanted.
- Store a snapshot, value plus source version, when the document must reproduce what was true at the time.

**Accountability:** Record who, when, and why for each write. Keep an append-only log when the record is a business fact.

## Projection table

Derived facts from another owner’s events, e.g. `unit_id -> active employee count`.

**Rules**
- Rebuildable from the owner’s events or API. Full rebuild path documented and tested.
- Updated by the same idempotent apply path as caches.
- Events must carry previous values where needed, e.g. `previous_unit_id`.
- Carries `as_of` timestamp and source versions processed.
- Never treated as master data.

**Accountability:** Rebuild-and-compare against the owner. Processed-event log shows what was applied.

## Crosswalk table

Maps an external code or entry to an internal ID. Used for external reference sets where there is no stable code, or the organisation’s definition differs.

**Columns:** `internal_id`, `external_authority`, `external_code`, `external_edition`, `valid_from`, `valid_to`, `mapping_type` (exact, broader, narrower), `approved_by`.

**Rules**
- Owned by the reference set owner. Changes need steward approval.
- Never delete a mapping. Close it with `valid_to`.
- Keep both definitions when they differ and map explicitly.

## Accountability options compared

| Option | What it is | Best for | Cost | Weakness |
|---|---|---|---|---|
| Lineage columns | `version`, `source_version`, `updated_by`, `updated_at`, `last_synced_at` | Caches, quick traceability | Very low | Shows state only, not history |
| Transaction log / outbox | Append-only record of every change, same transaction | Owner master tables | Low to medium | Needs retention and indexing |
| Processed-event log | Consumer records event ID or version applied | Caches, projections | Low | Grows; needs pruning |
| Versioned history table | Prior row versions with validity intervals | Entities where past values matter | Medium | Query complexity |
| Bitemporal history | Valid time and recorded time | Retroactive corrections with legal weight | High | Complexity; use only if required |
| Event store | Events are the source of truth | Rebuild-heavy projections | High | Whole-system commitment |
| Snapshot on write | Copy of referenced values stored with the transaction | Documents that must reproduce the past | Low | Duplicates data on purpose |
| Reconciliation record | Result of comparing copy to owner | Detecting drift | Low | Detects, does not explain |

## Accountability default (recommended)

**Proposal, revisable once audit or regulatory requirements are known.**

| Table type | Default mechanism |
|---|---|
| Master reference | Outbox / transaction log with every change; `version`, `updated_by`, `updated_at`; effective-dated history only where past values matter |
| Cache | `source_version`, `last_synced_at`; processed-event log committed with each apply; reconciliation record |
| Transaction | `created_by`, `created_at`, change reason; append-only log for business facts; snapshot where reproduction is required |
| Projection | `as_of`; rebuild-and-compare; processed-event log |
| Crosswalk | Never delete; `valid_from` / `valid_to`; approval recorded |

Upgrade to versioned or bitemporal history only when a requirement demands it. Reconcile log retention with erasure obligations.

---

<a id="guide-03-communication"></a>
# 3. Inter-system communication patterns

Flow, payload, technology requirements, and rules that preserve data integrity and independence. Technology-neutral: capabilities are specified, products are not.

## Flow: events plus read API

**Default flow.** The owner writes the business change and an outbox record in one local transaction. A relay publishes the outbox record as a change event. Consumers apply the event to their cache. A read API gives lookup by ID and catch-up by cursor.

```
Owner: [business change + outbox row] -> relay -> event channel -> Consumer: [idempotent apply]
Consumer --(lookup / catch-up)--> Owner read API
```

**Why both.** Events give timeliness and independence. The read API gives recovery, bootstrap, and on-demand lookup.

**Properties to assume**
- At-least-once delivery. The relay may publish twice. Consumers must be idempotent.
- Per-entity order, not global order.
- Exactly-once across separate systems is not assumed.

**Alternatives by need**
- Answer needed now: synchronous API with timeouts and a circuit breaker. Consumer depends on owner availability.
- React to change or keep a copy: events.
- External organisation consumer: signed webhooks, retries, list endpoint for reconciliation.
- Bulk or analytical: batch files or a governed data product, separate from the operational interface.

## Flow: bootstrap and catch-up

A new consumer, a rebuilt consumer, or a consumer that missed events uses the same path:

1. Page through the owner’s list endpoint with `updated_after`, using opaque cursors.
2. Apply each record through the normal version-guarded apply.
3. Switch to events, or begin consuming events during step 1 and rely on the version check to discard older data.
4. Run reconciliation.

Using one apply path for both bootstrap and events removes a class of divergence bugs.

## Flow: reconciliation

A scheduled comparison between a consumer’s copy and the owner.

1. Compare counts or hashes per range, e.g. per ID range or per `updated_at` window.
2. For mismatching ranges, re-fetch records from the owner.
3. Apply through the normal version-guarded path.
4. Record the result: ranges checked, mismatches, repairs.

Reconcile each cache against the owner, never against another consumer’s copy.

Frequency: nightly as a starting point. Tune to freshness needs.

## Payload: thin vs fat events

- **Thin (notification):** ID and change type only. The consumer calls back for details. The owner stays authoritative and checks authorisation on each read. The consumer cannot finish work while the owner is down.
- **Fat (state transfer):** Carries the fields consumers need. Consumers work without calling the owner. The contract is wider, data is duplicated, and consistency is eventual.

**Recommended split:** Fat events for non-sensitive attributes. Thin event plus authorised read for sensitive attributes.

**Rule:** An owner publishes only data it owns. A broadcasts `unit_id` and `position_id`, not their names.

## Payload: event envelope

Fields every event should carry. Names are illustrative.

| Field | Purpose |
|---|---|
| `event_id` | Unique per event. Duplicate detection. |
| `entity_type`, `entity_id` | What changed. Partition key. |
| `version` | Monotonic per entity. Ordering guard. |
| `occurred_at` | When the change committed. |
| `change_type` | Created, updated, status changed, replaced. |
| `status` | Explicit lifecycle state: active, inactive, terminated, deleted. |
| `replaced_by` | For merge and split. |
| `previous_*` | Previous values of fields consumers must decrement or re-index, e.g. `previous_unit_id`. |
| `effective_from` / `effective_to` | When the change applies, if different from `occurred_at`. |
| `schema_version` | Contract version of the payload. |
| fields | The non-sensitive attributes consumers need. |

Rules: additive-only evolution. Consumers ignore unknown fields and validate required fields.

## Payload: sensitive fields

Keep salary, national ID, and similar data out of events. The owner exposes them through an endpoint that authorises each read and scopes fields per consumer.

Reasons:
- Replicated sensitive data multiplies erasure and breach obligations.
- Per-read authorisation is defeated by cached copies.

## Technology requirements (neutral)

Choose any technology that provides these capabilities. Examples are illustrative only.

| Capability | Requirement | Example |
|---|---|---|
| Atomic change plus outbox | Business change and outbox record in one local transaction | Relational transaction with an outbox table |
| Event channel | At-least-once delivery; ordering per entity key; retention long enough for catch-up; consumer-side offset or equivalent | A message broker or log |
| Schema registry / contract store | Enforce compatibility; stored versions; FULL or FULL_TRANSITIVE preferred | A schema registry |
| Request/response contract | Machine-readable, reviewed before implementation | An OpenAPI document |
| Read API | Lookup by ID; cursor-paginated list with `updated_after` | REST or RPC |
| Error format | Standard, machine-readable | `application/problem+json` |
| Idempotency | Idempotency key policy for retried writes | Header-based key |
| Concurrency | Optimistic concurrency on writes | ETag with `If-Match`; 412 on mismatch |
| Identity and authorisation | Per-consumer authorisation, field scoping | Team’s standard |
| Observability | Trace and correlation IDs, lag metrics | Team’s standard |

Not covered by research: retries and backoff, dead-letter handling, circuit breakers, tracing, SLOs, OAuth/mTLS. Choose these deliberately and record them in an ADR.

## Rule: no shared databases

A consumer never reads or writes another module’s database. No cross-system foreign keys exist.

Why: A shared database makes the owner’s schema a public contract. Every internal change becomes a cross-team change.

Consumers get data only through the owner’s contract and keep their own copy.

## Rule: additive-only contract

**Safe changes:** Add fields, endpoints, enum values.
**Breaking changes:** Remove, rename, or retype a field. Change resource names, value formats, or defaults. Add a new required field.

Practices:
- Contract first: write and review the spec before implementing.
- Expose the minimum set of fields at first. What is exposed and relied on is effectively permanent.
- Keep the published model separate from the internal model.
- Consumers read only the fields they need, ignore unknown fields and enum values, and fail loudly on missing or malformed required data.
- For events, enforce compatibility in a registry. FULL or FULL_TRANSITIVE lets either side upgrade first.
- Retire fields through deprecation and sunset.
- Verify with contract testing.

## Rule: idempotent, version-guarded apply

The consumer’s only way to change a cache or projection.

1. Read the event or fetched record.
2. In one transaction: compare `version` with stored `source_version`.
   - Greater: apply; store new version; record processed event ID.
   - Equal: duplicate; ignore.
   - Lower: late; ignore.
3. Commit.

Properties:
- Safe under duplicates, reordering, and replays.
- Deleted or inactive state is a versioned state, so a stale update cannot resurrect a record.
- Same path for events and for bootstrap or repair.
- Unknown IDs on dependent events: store or fetch. Do not drop silently.

Storing the processed event ID in the same transaction as the change is the relational adaptation of “commit state with offset.”

## Rule: ordering per entity

Global order is not needed. Partition events by entity ID so per-entity order holds. Carry a monotonic `version` so consumers can detect and discard late events.

For writes through APIs, use optimistic concurrency: ETag and `If-Match`; 412 on mismatch. The client refetches and reconciles, not retries blindly.

Cross-entity ordering, e.g. the unit exists before an assignment references it, is handled by validation and lazy resolution, not by global ordering.

## Rule: validate IDs against the local cache

Before accepting a write that references another module’s entity, validate the ID against the local cache: it exists and is active, or valid on the effective date.

Examples:
- A validates `unit_id` and `position_id` against its cache of C before accepting an assignment.
- D validates the unit before accepting a requirement.
- Unknown ID: reject, or accept as pending and re-validate, per business rule.
- No cross-system foreign key constraints.
- This rule covers writes a module accepts from its users. It does not apply to events from an owner. Those were validated by the owner.

## Rule: deletes are explicit versioned states

- The owner marks records `inactive`, `terminated`, or `deleted` with a new `version`. It does not remove the row by default.
- Merge and split use `replaced_by`.
- A null-value tombstone in a compacted log means earlier records may be removed and does not protect a late joiner. A retained, versioned status does.
- Consumers keep the state so late or stale updates cannot resurrect the record.

Exception for erasure: see delete policy and erasure exception.

## Rule: deprecation and sunset

To remove a field or endpoint:
1. Mark deprecated in the spec.
2. Send `Deprecation` and `Sunset` headers. These are hints; clients must work without them.
3. Watch usage until it reaches zero.
4. Remove only then. For incompatible changes, publish a new major version.

Release pipeline: a contract check blocks removals, renames, retypings, and new required fields.

## Rule: contract testing

Catch breaking changes before release.

- **Spec diffing in CI:** Compare the new spec with the previous one. Simplest when there are many or unknown consumers.
- **Consumer-driven contract tests:** Consumers record what they use and replay it against the owner. Viable with one producer and one known consumer. Classic tools fit event-driven systems poorly.
- **Bi-directional contract testing:** Compares the owner’s spec with consumers’ recorded usage. Lighter, weaker guarantees.

Choice by consumer count is an inference. Sources were secondary.

## Security and erasure propagation

- Scope fields per consumer so a copy holds only what it needs.
- Validate the owner’s payloads instead of trusting them.
- Inventory interfaces and versions.
- Idempotency keys are high-entropy and cached under a composite key so one client cannot read another’s cached response.
- Erasure: when the owner deletes or anonymises a person, the change must reach every consumer’s copy, including caches, projections, backups, and logs.
- Applicable law, e.g. Indonesia’s UU PDP or GDPR, was not researched. Confirm with legal counsel.

Design hook: erasure is the one case where hard delete or anonymisation is allowed. Accountability logs must be consistent with it.

---

<a id="guide-04-use-cases"></a>
# 4. Use cases

What happens to each module type and table type in common situations. Split and merge apply to any entity whose business rules allow them.

## Use case: initial master broadcast to empty caches

**Trigger:** A new owner goes live, or a consumer is added with an empty cache.

**Steps**
1. Order entities by dependency: referenced before referencing.
2. Owner populates its master with IDs and `version`.
3. Consumers backfill through the list endpoint or the owner replays current state as events.
4. Consumers apply through the idempotent path.
5. Reconcile.
6. Only then enable validations that depend on the cache.

**Effect by module type**
- Owner: serves list and events. No schema change.
- Type 1: cache fills. Placeholders resolve. No business impact.
- Type 2: validate that existing index records match cached IDs. List unmatched ones for review.

**Effect by table type:** Master gains rows. Cache gains rows with `source_version`. Transaction tables unchanged. Projections are rebuilt.

**Edge cases:** Records arriving before their parent: store, resolve later. Large volume: page by cursor. Events arriving mid-backfill: version guard discards older.

## Use case: new record

**Steps**
1. Owner validates and creates the record, issues the ID, sets `version = 1`, writes the outbox row.
2. Event published. Consumers apply it as an insert in their cache.
3. Consumer records referencing the new ID can now pass local validation.

**Effect by module type**
- Owner: new master row.
- Type 1: new cache row. Nothing else changes.
- Type 2: new possible index value. No existing records change. D may prompt for a requirement for a new unit.

**Edge cases**
- A consumer sees an ID in a dependent event before the record event. Store a placeholder or fetch on miss.
- Duplicate event: ignored by version check.
- Duplicate real-world entity: handle by merge.

## Use case: update, rename, reparent

**Steps:** Owner changes the record, increments `version`, publishes. Consumers apply if newer.

**Effect by module type**
- Owner: master row updated. History row where kept.
- Type 1: cache updated. Displays change. Historical documents show the new name unless a snapshot was stored.
- Type 2: rename has no business effect. Reparent changes roll-up totals. Effective-dated requirements remain valid.
- Projections: events must carry previous values when a field changes the grouping, e.g. transfer between units.

**Edge cases:** Names needed “as of” a past date require effective-dated names in the owner. Cycles in hierarchy are rejected by the owner. Late events are ignored by version.

## Use case: split

**Applicability:** Any entity where business rules allow one record to become several. Decide per entity.

**Owner steps**
1. Create the new records with new IDs.
2. Retire the original: status `inactive` or `split`, `replaced_by = [new IDs]`, new version, `effective_to`.
3. Publish events for the retired and new records.

**Effect by module type**
- Owner: original kept as history. New rows.
- Type 1: cache shows the original as inactive and links to successors. Records keep pointing to the original until reassigned, with a visible status.
- Type 2: does not move records silently. Records indexed by the original are flagged for review. A person decides how to distribute them. A, as holder of assignments, reassigns affected employees to the new units.

**Rules**
- The split mapping is rarely one-to-one for children. `replaced_by` states possible successors, not the distribution.
- A consumer that stores quantities against the original needs a business decision, not an automatic rule.
- Past records keep the original ID so history stays true.

**Edge cases:** Split in progress: successors created before original retired. Partial reassignment. Reversal: do not reuse the original; create a new record or merge.

## Use case: merge

**Applicability:** Any entity where business rules allow several records to become one. Decide per entity.

**Owner steps**
1. Choose the surviving record, existing or new ID.
2. Retire the others: status `inactive` or `merged`, `replaced_by = [surviving ID]`, new version, `effective_to`.
3. Publish events for all affected records.

**Effect by module type**
- Owner: absorbed records remain as history.
- Type 1: cache marks absorbed records and links successor. Owner’s holders reassign affected employees. Consumer records are updated by their own module’s process, not by repointing blindly.
- Type 2: flags the requirements of absorbed units. A person decides whether to add, replace, or keep them. Never silently re-key.
- Projections: counts for absorbed units move after reassignments. Show “as of.”

**Rules**
- Never reuse absorbed IDs. Resolve references through `replaced_by` chains. Keep chain length bounded; resolve transitively.
- A merge can be chained with later changes. Consumers apply by version.

**Edge cases:** Conflicting attribute values between merged records: owner decides. A merge reversed later: treat as a split. Duplicates created in error in a consumer’s own table: its own matter.

## Use case: delete

Policy: see delete policy and erasure exception.

**Normal retirement**
1. Owner sets status `inactive` or `terminated`, new version, `effective_to`. Publishes.
2. Consumers apply the status. Records referencing the entity remain.

**Effect by module type**
- Owner: row remains.
- Type 1: shows status. New records may not reference it unless history entry.
- Type 2: flag or close records with `effective_to`. Do not delete.

**Erasure (exception)**
1. Owner anonymises in place or hard-deletes, and publishes a versioned erasure event.
2. Every consumer applies it, including caches, projections, snapshots, and logs.
3. Reconcile to confirm.

**Edge cases:** Stale update after delete: rejected by version; state is retained. Delete of an entity still referenced by open records: block or archive per business rule. Resurrection by an old batch: version guard. Consumer unreachable during erasure: queue; track completion.

## Use case: late joiner, missed or out-of-order events

- **Late joiner or rebuilt consumer:** Bootstrap and catch-up. A retained delete state is needed so history is not lost.
- **Missed events:** Reconciliation detects the range. Re-fetch and apply through the version check.
- **Out-of-order:** Older versions ignored.
- **Event for an unknown dependent ID:** Placeholder or fetch on miss.
- **Poison event (malformed):** Reject and route to a holding area for review. Do not block the entity stream. Dead-letter handling was not researched.

## Use case: external reference edition change

An external authority publishes a new edition of a code set.

1. The steward reviews the change and approves.
2. The owner imports the new edition, adds new entries, closes changed ones with `valid_to`, and updates the crosswalk.
3. The owner publishes the new edition with a cutoff date for the old one.
4. Consumers apply it. Old codes stay resolvable.
5. Consumers with local extensions check their keys.

**Edge cases:** Entries split or merged by the authority: use `replaced_by` like split and merge. The organisation’s definition differs from the new edition: keep both, map explicitly.

---

<a id="guide-05-operations"></a>
# 5. Operations and governance

Governance of reference data, including external sets, and monitoring of freshness.

## External reference sets

Reference data not produced by an internal module, e.g. region codes, tax status, education levels. Give each set one internal owner and a named data steward.

### Keying decision

| Situation | Action |
|---|---|
| Stable public standard code, e.g. ISO | Use the external code as the shared key. Store the standard and edition. |
| Authority changes codes over time | Key by code plus edition or effective date. Keep old codes resolvable. |
| No stable code or free-text list | Owner mints an internal ID and keeps a crosswalk to the external entry. |
| Organisation’s definition differs | Keep both and map explicitly. |

### Process
- Owner imports from the source, validates, and publishes versioned events or a dataset plus a read API.
- Other systems subscribe and reference entries by code, never by text.
- Write each set into a data dictionary entry: authority, edition, owner, update schedule, change approval. Record the source choice in an ADR.
- Pin editions. Announce edition changes with a cutoff date for the old one.
- Local extensions go in the consumer’s own table keyed by the code.
- One name must never carry two meanings. If meanings conflict, split into two named sets.

### Do not
- Let each system download the external list itself.
- Store only name text.
- Hard-delete retired entries.

Open item: identify the actual sets in use and map each to the table above.

## Data dictionary and ADRs

Each entity and each reference set gets a data dictionary entry. Each design choice gets an architecture decision record.

**Data dictionary entry minimum:** Entity name; owner module and data steward; ID format; business keys; fields published and their sensitivity; lifecycle states; split/merge applicability; consumers and their type; contract location and version. For external sets: authority, edition, update schedule, change approval.

**ADR minimum:** Context, options considered, decision, consequences, date.

Record at least:
- Technology choices.
- Subscribe vs call on demand.
- Delete policy and erasure exception.
- Contract versioning style.
- Keying choice for each external set.

Verify the unverified research sections before an ADR relies on them.

## Freshness and drift monitoring

Measure, per consumer and entity:
- **Lag:** Time from the owner’s `occurred_at` to the consumer’s `last_synced_at`.
- **Drift:** Mismatches found by reconciliation and repair counts.
- **Rejects:** Events refused for malformed required data.
- **Placeholders:** Unknown-ID rows awaiting resolution.

Display “as of” timestamps in UIs. Alerting thresholds, SLOs, tracing, and dead-letter handling had no usable source. Define them in ADRs.

---

<a id="guide-06-appendices"></a>
# 6. Appendices: decisions, checklist, reliability

Open choices with options and the conditions that favour each, a design checklist, and the reliability of the evidence.

## Decision: subscribe to events or call the owner on demand

Both options are valid. The conditions decide.

| | Subscribe and keep a local cache | Call the owner’s read API on demand |
|---|---|---|
| Availability | Consumer works if owner is down | Consumer fails with the owner |
| Freshness | Eventual; show “as of” | Exact at read time |
| Complexity | Higher: cache, apply path, reconciliation | Lower: no local copy |
| Coupling | Contract-level only | Runtime coupling plus latency |
| Load on owner | Low, steady | Proportional to reads |
| Joins and reporting | Local joins | Cross-system calls per row |
| Data duplication | Yes; erasure scope grows | No |

**Choose subscribe when**
- The consumer must keep operating when the owner is down.
- It joins or filters by the data locally, e.g. names in lists, reports, roll-ups.
- Read volume is high.
- The data changes rarely relative to reads, e.g. reference data.

**Choose call on demand when**
- Exactness at decision time is required, e.g. permission or amount.
- The data is sensitive and should not be replicated.
- Volume is low and the owner is highly available.
- The team cannot yet operate caches and reconciliation.

**Hybrid (common):** Cache reference data. Call on demand for sensitive or exactness-critical data. Call on a cache miss.

## Decision: delete policy and the erasure exception

**Default:** No hard delete. The owner sets a lifecycle status with a new version. Consumers keep the state.

**Exception:** Legal erasure or anonymisation of personal data, and correction of records created in error.

| Case | Mechanism | Notes |
|---|---|---|
| Normal retirement | Status `inactive` or `terminated` | Reversible; history kept |
| Merge / split | Status plus `replaced_by` | See merge and split |
| Created in error | Mark `void`; hard delete only if never published | If published, treat as erasure |
| Personal-data erasure | Anonymise fields in place and keep ID and version; or hard delete with an erasure event | Event must reach every copy |

**Erasure design options**
- **Anonymise in place** (recommended starting point): Replace personal fields with null or placeholder, keep the ID, status, and version. Consumers apply it as a normal update. No stale copy can resurrect the data. References stay valid.
- **Hard delete plus erasure event:** Remove the row and send an event telling consumers to remove theirs. Use when law or policy requires the identifier itself to go. Consumers must handle dangling references. The “never reuse an ID” rule must still hold.

**Required for either**
- The erasure event is versioned and idempotent. Consumers apply it via version-guarded apply.
- Reconciliation confirms no copy remains.
- Logs, projections, backups, and snapshots are in scope.
- Legal requirements, e.g. UU PDP, GDPR, were not researched. Confirm with legal counsel.

## Decision: contract versioning style

The guides read disagree. The choice is a team convention, not a correctness issue.

| Style | Source position | Notes |
|---|---|---|
| Major version in URL path, e.g. `/v1/`, no minor versions | Google API guidance | Simple; visible; new major only for incompatible change |
| Avoid versions; media-type versioning only for incompatible change; no URL versions | Zalando guidelines | Pushes toward compatible evolution |
| Date-based version pinned per account, responses transformed backward | Stripe 2017 post, may be dated | Heavy for two internal systems |

**Suggestion for a few internal modules:** Additive change within one major version. A new major version only for a truly incompatible change.

For events, use schema compatibility in a registry. Retirement: deprecation and sunset.

## Design checklist for a new module

**Scope**
- [ ] Entities owned and consumed listed; each classified.
- [ ] Scope criteria applied; features placed.
- [ ] Dependency graph per entity is acyclic.

**Tables**
- [ ] Each table typed; accountability chosen.
- [ ] No cross-system foreign keys; ID columns unique; business keys as attributes.

**Communication**
- [ ] Owner: ID format, versioning, outbox, events, read API, contract, sensitive-field scoping.
- [ ] Consumer: apply path idempotent and version-guarded; adapter at the edge; unknown-ID handling.
- [ ] Bootstrap and reconciliation planned.

**Lifecycle**
- [ ] Statuses, `replaced_by`, effective dating defined; split/merge applicability decided.
- [ ] Type 2 consumers have a review process for flagged records.
- [ ] Erasure path defined.

**Governance**
- [ ] Data dictionary entry and ADRs written.
- [ ] Monitoring defined.

## Source reliability

How far each part of this guide can be trusted.

| Area | Status | Pages |
|---|---|---|
| Ownership, IDs, system of record, anti-corruption layer | Not source-verified; background knowledge | Opaque permanent ID, System of record, Anti-corruption layer |
| Integration styles, thin vs fat events, coupling | Entirely unverified | Payload: thin vs fat events, Flow: events plus read API |
| Delivery semantics, outbox, idempotency, ETags, tombstones, sagas | Partly verified | Idempotent version-guarded apply, Ordering per entity, Deletes as states |
| Contracts, compatibility, versioning, deprecation, errors | Partly verified | Additive-only contract, Deprecation and sunset, Contract versioning style |
| Units, positions, headcount, external reference patterns | Design reasoning, not researched | Consumer type 2, Projection holder, External reference sets, use cases |
| Scope criteria, feature placement, accountability default | Assistant proposals | Module scope criteria, Feature placement test, Accountability default |

**No usable source:** Retries and backoff, dead-letter queues, circuit breakers, tracing, SLOs, drift detection, OAuth/mTLS, personal-data erasure law (UU PDP, GDPR; confirm with legal), snapshot-plus-change-feed bootstrap, event-contract testing.

**Other cautions:** The Idempotency-Key header is an expired IETF draft, not a standard. Stripe’s versioning post is from 2017. Page fetching was largely blocked during research, so verify the unverified sections before relying on them in an ADR.

Origin: *API design for system integration* and *OSDM system integration summary*.
