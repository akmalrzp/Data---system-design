

# System Design Guide: Integrating Independent OSDM Modules

**Technology-neutral guide for architects and developers**  
*Generated from `wiki/` pages; edit the source pages, not this file.*

---

## 0. Overview, Purpose, and Core Principles

### What This Guide Solves

**Problem**: System A produces data that System B needs. Both must stay independent—with separate release cycles, separate databases, and tolerance for downtime—while keeping consistent reference data.

**Domain**: **OSDM** = Organisasi & SDM (Organization & Human Resources/Personnel).

**Four Questions Answered**:
1. What kinds of modules exist, and where does each feature belong?
2. What kinds of tables exist, and how is accountability ensured?
3. How do modules communicate without becoming tightly coupled?
4. What happens in common situations (bootstrap, new records, splits, merges, deletions)?

---

### Core Principles

| # | Principle | Why It Matters |
|---|-----------|----------------|
| 1 | **One owner per record** | Exactly one module creates and changes a record; everyone else holds a derived copy |
| 2 | **Permanent opaque ID** | The owner issues an identifier that never changes, is never reused, and carries no business meaning |
| 3 | **Consumers store only what they need** | Consumers store the ID plus required fields as a read-only cache. Authoritative fields belong to their owner |
| 4 | **Small, versioned, additive contract** | The published API is separate from the owner's internal model |
| 5 | **Changes flow as events; read API for lookup** | Events give timeliness; read API enables recovery and catch-up |
| 6 | **Assume duplicates, disorder, and loss** | Apply changes idempotently; only accept newer versions |
| 7 | **Translate at the edge** | Each consumer converts the owner's model into its own via an anti-corruption layer |
| 8 | **No shared databases, no cross-module foreign keys** | Prevents tight coupling and accidental schema dependencies |
| 9 | **State changes, not absence** | Deletion is a lifecycle state (`inactive`, `terminated`), not row removal |
| 10 | **Accept eventual consistency** | Copies lag the owner; show freshness timestamps |

> ⚠️ **Note on reliability**: Principles 1–3, 7 are established practice but not source-verified in this research. See [Source Reliability](#source-reliability) at the end.

---

### Key Concepts Defined Early

| Term | Definition |
|------|------------|
| **Module** | An independently deployable system with its own database and release cycle (examples: Module A = HR Core, Module C = Org Structure) |
| **System of Record** (Data Owner) | The single module authorized to create and change a record |
| **Consumer** | A module that holds references or copies of another module's data |
| **Reference Data** | Data owned by one module and referred to by others (e.g., unit names, position codes) |
| **Opaque Permanent ID** | A globally unique identifier (like UUID) issued by the owner: never changes, never reused, no business meaning |
| **Anti-corruption Layer** | An adapter at the consumer's edge that translates the owner's vocabulary into the consumer's local model |
| **Contract** | The published, versioned shape of API responses and events |
| **Projection** | Derived data (e.g., counts per unit) built from events, not copied records |

---

### Worked Example: Modules A, B, C, D

| Module | Role | Owns | Uses |
|--------|------|------|------|
| **A (HR Core)** | Owner + Consumer of C | Employee records, employee-to-unit assignments | Unit, Position data from C |
| **B (Payroll)** | Consumer type 1 (uses data as attributes) | Pay grade, tax status | Employee from A; Unit/Position names from C |
| **C (Org Structure)** | Owner | Unit, Position | None (pure owner) |
| **D (Requirements)** | Consumer type 2 (uses data as index) + Projection holder | Required headcount per unit | Unit from C; employee counts per unit from A |

**Pattern Summary**:
- A broadcasts `employee_id`, `unit_id`, `position_id`—not names (names belong to C)
- C broadcasts `unit.changed`, `position.changed`; A, B, D keep local caches
- B resolves names by joining on IDs in its own cache of C
- D uses `unit_id` as the business key for its requirement records

---

## 1. Module Types

Modules are classified per entity by their relationship to the data: **owner**, **consumer using data as attributes**, or **consumer using data as index**. Real modules are usually hybrid (own some entities, consume others).

### Module Scope Criteria

Use these measurements to decide where module boundaries fall:

| Criterion | Question | Boundary Signal |
|-----------|----------|-----------------|
| **Decision authority** | Who decides the value of this data? | Different decision-makers → different modules |
| **Accountability** | Who answers for correctness and audit? | One accountable role per entity |
| **Rate and reason of change** | Does it change for the same reasons and pace as neighbors? | Different change drivers → split |
| **Lifecycle** | Created/retired on the same schedule? | Different lifecycles → split |
| **Access and sensitivity** | Same audience or authorization? | Different confidentiality → separate module or fields |
| **Consistency need** | Must data change atomically with neighbors? | Atomic need → same module |
| **Consumer pattern** | Need live data or can lagged copy work? | Lag-tolerant → can live elsewhere |
| **Team independence** | Can one team release without others? | Separate teams → separate modules |

**Rules of thumb**:
- Entities requiring atomic transactions belong together
- If a boundary forces constant synchronous calls, it's likely drawn incorrectly

### Feature Placement Test

Apply in order to decide where a feature belongs:

1. **Creates/changes a record this module owns?** → Belong here (owner)
2. **Creates/changes a record owned by another?** → Call the owner's contract
3. **Only reads another module's data for display/validation?** → Belong here, using local cache
4. **Needs authoritative value derived from elsewhere?** → Make a projection or own the field here
5. **Needs unpublishised data from the owner?** → Request contract addition; don't read owner's database
6. **Mixes two owners' data in one atomic write?** → Redesign: separate writes per owner

---

### Owner and Broadcaster (Source of Truth)

**Role**: Creates, changes, and retires records; publishes changes.

**Must provide**:
- Master reference tables
- Change feed: versioned events via transactional outbox
- Read API for lookup by ID and cursor-paginated catch-up
- Published, versioned, additive contract
- Lifecycle states instead of hard delete (with `replaced_by` for merge/split)

**Must not**:
- Publish data it doesn't own
- Expose internal model or database
- Reuse or change an ID

---

### Consumer Type 1: Reference Data as Attributes

**Role**: Uses another module's records as descriptive attributes. The reference doesn't define the consumer's records.

**Example**: Payroll stores `employee_id` and shows unit/position names. The payroll record exists regardless of unit.

**Design**:
- Keep a cache of the master with ID as unique key, only needed fields
- Transaction records hold foreign ID (no cross-system foreign key constraint)
- Resolve names by joining on IDs in local cache
- Unknown ID: store it, show placeholder, fetch from owner

**Impact of owner lifecycle**: Low. Renames change display only; retirement adds status flags.

---

### Consumer Type 2: Reference Data as Index

**Role**: Uses another module's ID as the business key or classification axis. The reference defines what the consumer's records mean.

**Example**: "Required employees per unit" — `unit_id` identifies the requirement.

**Additional design**:
- Validate referenced entity exists and is active before accepting records
- Use effective dates (`effective_from` / `effective_to`) so records stay meaningful after reference changes
- Treat owner lifecycle events as business events (inactive → flag for review; merge/split → don't move silently)
- Show "as of" timestamps on projections

**Impact of owner lifecycle**: High. Agree lifecycle contract with owner early.

---

### Hybrid Module (Owner and Consumer)

Most real modules own some entities and consume others.

**Rules**:
- Classify per entity, not per module
- Keep owned tables and caches physically/logically separate
- Validate assignments against local cache before acceptance
- Never republish consumed entity's attributes (A publishes `unit_id`, not unit name)

---

### Edge Cases

| Edge Case | Resolution |
|-----------|------------|
| **Field ownership disputes** | If B needs a field authoritative, B owns it in its own table; name it differently (`legal_name` vs `payroll_display_name`) |
| **Sensitive fields** | Salary, national ID not broadcast. Owner exposes via authorised endpoint per read |
| **Hierarchy changes** | Owner publishes `parent_unit_id`; consumers recompute roll-ups from local cache |
| **Circular dependencies** | Dependency graph must be acyclic per entity. Move shared data to third owner if needed |
| **Owner unavailable** | Consumer works from local cache; queue events; reject or accept pending writes per business rule |
| **Business key vs ID** | Join on IDs only. Business keys are attributes, not join keys |
| **Divergent reference caches** | Reconcile each cache against owner, never against another consumer |

---

## 2. Table Types and Accountability

| Table Type | Purpose | Accountability Mechanism |
|------------|---------|--------------------------|
| **Master Reference** (owner) | Authoritative table | Transaction log / outbox; `version`, `updated_by`, `updated_at` |
| **Cache of Master** (consumer) | Read-only local copy | `source_version`, `last_synced_at`; processed-event log |
| **Transaction** | Module's own business records | `created_by`, `created_at`, change reason; append-only log |
| **Projection** | Derived facts from other owner's events | `as_of`; rebuild-and-compare; processed-event log |
| **Crosswalk** | Maps external codes to internal IDs | Never delete; `valid_from`/`valid_to`; approval recorded |

### Recommended Default Accountability

| Table Type | Default Mechanism |
|------------|-------------------|
| Master Reference | Outbox/transaction log; `version`, `updated_by`, `updated_at`; effective-dated history only where needed |
| Cache | `source_version`, `last_synced_at`; processed-event log; reconciliation record |
| Transaction | `created_by`, `created_at`, change reason; append-only log for business facts |
| Projection | `as_of`; rebuild-and-compare; processed-event log |
| Crosswalk | Never delete; `valid_from`/`valid_to`; approval recorded |

---

## 3. Inter-system Communication Patterns

### Flow: Events Plus Read API

**Default pattern**: Owner writes business change + outbox record in one transaction. Relay publishes as change event. Consumers apply idempotently. Read API provides lookup and catch-up.

```
Owner → [business change + outbox] → relay → event channel → Consumer → [idempotent apply]
Consumer ↔ (lookup / catch-up) ↔ Owner read API
```

**Why both**: Events give timeliness and independence; read API gives recovery and bootstrap.

**Properties to assume**:
- At-least-once delivery (consumers must be idempotent)
- Per-entity order, not global order
- Exactly-once not assumed across separate systems

---

### Bootstrap and Catch-up

A new consumer or rebuilt consumer uses the same path:

1. Page through owner's list endpoint with `updated_after` (or from start)
2. Apply each record through the normal version-guarded apply path
3. Switch to events (or consume events during backfill with version check)
4. Run reconciliation

---

### Reconciliation Flow

Scheduled comparison between consumer's copy and owner:

1. Compare counts/hashes per range
2. For mismatching ranges, re-fetch from owner
3. Apply through version-guarded path
4. Record result for drift monitoring

**Frequency**: Nightly as starting point

---

### Payload: Thin vs Fat Events

| Type | Content | Trade-offs |
|------|---------|------------|
| **Thin** (notification) | ID and change type only | Consumer must call back; owner stays authoritative |
| **Fat** (state transfer) | Carries fields consumers need | Works without owner call; wider contract; eventual consistency |

**Recommended**: Fat events for non-sensitive attributes; thin + authorised read for sensitive attributes.

---

### Event Envelope Fields

Every event should carry:

| Field | Purpose |
|-------|---------|
| `event_id` | Unique per event; duplicate detection |
| `entity_type`, `entity_id` | What changed; partition key |
| `version` | Monotonic per entity; ordering guard |
| `occurred_at` | When change committed |
| `change_type` | Created, updated, status changed, replaced |
| `status` | Explicit lifecycle state |
| `replaced_by` | For merge/split successor pointers |
| `previous_*` | Previous values for decrement/re-index |
| `schema_version` | Contract version |
| fields | Non-sensitive attributes consumers need |

---

### Critical Rules

| Rule | Description |
|------|-------------|
| **No shared databases** | Consumers never access owner's database; no cross-system foreign keys |
| **Additive-only contract** | Safe: add fields/enum values. Breaking: remove/rename/retype/change format |
| **Idempotent, version-guarded apply** | Accept only if event version > stored version; commit event ID with change |
| **Ordering per entity** | Global order not needed. Partition by entity ID for per-entity order |
| **Validate IDs against local cache** | Before accepting writes referencing other modules, validate in local cache |
| **Deletes are explicit versioned states** | Mark `inactive`/`terminated` with new version; don't remove rows |
| **Deprecation and sunset** | Mark deprecated → watch usage → remove only when zero usage |
| **Contract testing** | Catch breaking changes before release (spec diffing or consumer-driven contracts) |

---

## 4. Use Cases

### Initial Master Broadcast to Empty Caches

**Trigger**: New owner goes live, or consumer added with empty cache.

**Steps**:
1. Order entities by dependency (referenced before referencing)
2. Owner populates master with IDs and `version`
3. Consumers backfill through list endpoint
4. Apply via idempotent path
5. Reconcile
6. Enable validations only after

---

### New Record

**Steps**:
1. Owner validates, creates record, issues ID, `version = 1`, writes outbox
2. Event published; consumers apply as insert in cache
3. Consumer records referencing new ID can now pass validation

---

### Update, Rename, Reparent

**Steps**: Owner changes record, increments `version`, publishes; consumers apply if newer.

**Effects**:
- **Type 1**: Cache updated; displays change. Historical docs show new name unless snapshot stored
- **Type 2**: Rename has no business effect. Reparent changes roll-up totals

---

### Split

**Owner steps**:
1. Create new records with new IDs
2. Retire original: `inactive`, `replaced_by = [new IDs]`, new version, `effective_to`
3. Publish events for retired and new records

**Type 2 consumer**: **Does not move records silently.** Records flagged for review; person distributes them.

---

### Merge

**Owner steps**:
1. Choose surviving record
2. Retire others: `inactive`, `replaced_by = [surviving ID]`, new version, `effective_to`
3. Publish events for all affected records

**Type 2 consumer**: Flags requirements; person decides whether to add/replace/keep. Never silently re-key.

---

### Delete

**Normal retirement**:
1. Owner sets `inactive`/`terminated`, new version, `effective_to`; publishes
2. Consumers apply status; referencing records remain

**Erasure exception** (personal data):
1. Owner anonymises or hard-deletes; publishes erasure event
2. Every consumer applies, including caches, projections, logs
3. Reconcile to confirm

---

### Late Joiner, Missed or Out-of-order Events

- **Late joiner**: Bootstrap and catch-up; retained delete state needed
- **Missed events**: Reconciliation detects range; re-fetch and apply
- **Out-of-order**: Older versions ignored by version check
- **Unknown dependent ID**: Placeholder or fetch on miss

---

## 5. Operations and Governance

### External Reference Sets

Reference data from outside the organization (region codes, tax status).

**Keying decision**:

| Situation | Action |
|-----------|--------|
| Stable public standard code (ISO) | Use external code as shared key |
| Authority changes codes over time | Key by code + edition; keep old codes resolvable |
| No stable code | Owner mints internal ID; keep crosswalk table |
| Organisation definition differs | Keep both; map explicitly |

---

### Data Dictionary and ADRs

**Data dictionary entry** (minimum):
- Entity name; owner module and data steward
- ID format; business keys; fields published and sensitivity
- Lifecycle states; split/merge applicability
- Consumers and their type; contract location/version
- For external sets: authority, edition, update schedule, change approval

**ADR** (minimum): Context, options considered, decision, consequences, date.

---

### Freshness and Drift Monitoring

Measure per consumer and entity:
- **Lag**: Time from owner's `occurred_at` to consumer's `last_synced_at`
- **Drift**: Mismatches from reconciliation
- **Rejects**: Events refused for malformed data
- **Placeholders**: Unknown-ID rows awaiting resolution

---

## 6. Appendices

### Decision: Subscribe to Events or Call Owner On Demand

| Aspect | Option 1: Subscribe + Cache | Option 2: Call On Demand |
|--------|---------------------------|--------------------------|
| Availability | Works if owner down | Fails with owner |
| Freshness | Eventual; show "as of" | Exact at read time |
| Complexity | Higher (cache, apply, reconciliation) | Lower |
| Coupling | Contract-level only | Runtime coupling + latency |
| Load on owner | Low, steady | Proportional to reads |
| Joins/reporting | Local joins | Cross-system calls per row |

**Choose Option 1 when**: Consumer must work offline, joins/filter locally, high read volume, data changes rarely

**Choose Option 2 when**: Exactness required at decision time, sensitive data, low volume, cannot yet operate caches

**Hybrid (common)**: Cache reference data; call on demand for sensitive/exactness-critical data; call on cache miss

---

### Decision: Delete Policy and Erasure Exception

**Default**: No hard delete. Set lifecycle status with new version; consumers keep state.

**Exception** (allowed): Legal erasure/anonymisation of personal data, correction of records created in error.

| Case | Mechanism |
|------|-----------|
| Normal retirement | Status `inactive`/`terminated` (reversible; history kept) |
| Merge/split | Status + `replaced_by` |
| Created in error | Mark `void`; hard delete only if never published |
| Personal-data erasure | Anonymise in place (recommended) or hard delete with erasure event |

---

### Design Checklist for New Module

**Scope**
- [ ] Entities owned/consumed listed and classified
- [ ] Scope criteria applied; features placed
- [ ] Dependency graph per entity is acyclic

**Tables**
- [ ] Each table typed; accountability chosen
- [ ] No cross-system foreign keys; ID columns unique

**Communication**
- [ ] Owner: ID format, versioning, outbox, events, read API, contract
- [ ] Consumer: idempotent apply path; adapter at edge; unknown-ID handling
- [ ] Bootstrap and reconciliation planned

**Lifecycle**
- [ ] Statuses, `replaced_by`, effective dating defined
- [ ] Type 2 consumers have review process for flagged records
- [ ] Erasure path defined

**Governance**
- [ ] Data dictionary entry and ADRs written
- [ ] Monitoring defined

---

### Source Reliability

| Area | Status |
|------|--------|
| Ownership, IDs, system of record, anti-corruption layer | Not source-verified (background knowledge) |
| Integration styles, thin vs fat events, coupling | Entirely unverified |
| Delivery semantics, outbox, idempotency, ETags | Partly verified (Confluent, microservices.io, etc.) |
| Contracts, compatibility, versioning, deprecation | Partly verified (Zalando, Google AIPs, RFCs) |
| Units, positions, headcount, external reference patterns | Design reasoning, not researched |
| Scope criteria, feature placement, accountability default | Assistant proposals |

**No usable source found**: Retries/backoff, dead-letter queues, circuit breakers, tracing, SLOs, drift detection, OAuth/mTLS, erasure law (confirm with legal counsel).

**Other cautions**: Idempotency-Key header is expired IETF draft; verify unverified sections before relying on them in architecture decisions.

---

## Glossary

| Term | Definition |
|------|------------|
| **Module** | Independently deployable system with own database and release cycle |
| **Data owner / System of record** | Module allowed to create and change a record |
| **Broadcaster** | Owner's role of publishing change events and exposing read API |
| **Consumer** | Module holding references/copies of another module's data |
| **Reference data** | Data owned by one module and referred to by others |
| **Master reference table** | Owner's authoritative table |
| **Cache (of master)** | Consumer's read-only local copy |
| **Transaction table** | Consumer's/owner's own business records that reference IDs |
| **Projection** | Derived data (counts) built from events, not copied records |
| **Crosswalk** | Mapping between internal IDs and external codes |
| **Contract** | Published, versioned shape of API responses and events |
| **Event envelope** | Metadata fields on every event (ID, version, timestamp, etc.) |
| **Version** | Monotonic number per record, increased on every change |
| **Tombstone** | Retained marker that record is deleted/inactive; here a versioned state |
| **`replaced_by`** | Pointer from retired record to successor(s) after merge/split |
| **Effective dating** | `effective_from`/`effective_to` on records whose meaning depends on date |
| **Anti-corruption layer** | Adapter translating external model into local one |
| **Data steward** | Named person accountable for a reference set |
| **OSDM** | Organisasi & SDM (Organization & Human Resources/Personnel domain) |
| **ADR** | Architecture Decision Record—document explaining design choices |
