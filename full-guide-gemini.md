# System Design Guide: Integrating Independent OSDM Modules

A technology-neutral guide for software architects and developers building decoupled Organization & Human Resource (OSDM) modules.

---

## Glossary

| Term | Plain English Definition |
|---|---|
| **System of Record (SoR)** | The single authoritative module allowed to create, modify, or retire a specific record. |
| **Data Owner** | The module responsible for maintaining and publishing a specific set of master records. |
| **Consumer** | A module that uses or stores copies of data owned by another module. |
| **Opaque Permanent ID** | A unique identifier (like a UUID) that has no embedded meaning (no dates, names, or codes) and never changes or gets reused. |
| **Anti-Corruption Layer (ACL)** | A translator component built into a consuming module that converts external API/event formats into its internal database format, shielding core logic from outside contract changes. |
| **Eventual Consistency** | A model where local data copies temporarily lag behind the owner system but guaranteed to match over time. |
| **Transactional Outbox** | A pattern where database changes and outgoing event messages are saved together in a single local transaction, ensuring events are never lost if the system crashes. |
| **Idempotent Application** | Processing the same message multiple times without changing the end result or creating duplicate side effects. |
| **Tombstone / Explicit State** | Marking a record as `inactive`, `retired`, or `deleted` with a new version number, rather than physically wiping the database row. |
| **`replaced_by` Pointer** | A reference recorded on a retired entity pointing to its successor(s) after a merge or split operation. |
| **Crosswalk Table** | A translation table mapping internal database IDs to external, third-party codes (e.g., standard national labor codes). |

---

## 1. Purpose & Core Principles

### Problem Statement
When Module A produces core organizational data and Module B consumes it, both systems must stay synchronized without becoming tightly coupled. They must maintain independent database structures, separate deployment cycles, and fault tolerance when one module is unavailable.

### Core Principles
1. **Single Ownership:** Exactly one module owns a record (System of Record). All other systems store derived, read-only copies.
2. **Immutable IDs:** The owner generates an opaque identifier that never changes, is never reused, and carries no embedded business data.
3. **Minimal Local Caches:** Consumers store only the fields they explicitly need alongside the external ID.
4. **Additive Contracts:** Data contracts evolve strictly by adding fields. Removing or renaming fields is forbidden within a version.
5. **Dual-Channel Communication:** State changes broadcast as events; a REST/RPC Read API handles lookups and bulk synchronization.
6. **Out-of-Order Resiliency:** Consumers handle duplicate, missing, or out-of-order messages using monotonic version numbers.
7. **Boundary Translation:** Each consumer uses an Anti-Corruption Layer (ACL) at its entry point to translate incoming payloads.
8. **No Database Sharing:** Modules never read or write directly to another module's database.
9. **Explicit Lifecycle States:** Record deletions, merges, and splits are recorded as versioned state updates rather than row deletions.
10. **Visibility of Freshness:** UI elements displaying cached or calculated data state how current the data is (e.g., "Data as of 10:15 AM").

---

## 2. Practical Reference Architecture

To illustrate these concepts, this guide references four sample modules:

| Module | Role | Data Owned | Data Consumed |
|---|---|---|---|
| **A (HR Core)** | Owner & Consumer | Employee records, employee-to-unit assignments | Units & Positions (from C) |
| **B (Payroll)** | Consumer (Attribute User) | Pay grades, tax records | Employees (from A); Unit & Position names (from C) |
| **C (Org Structure)** | Owner | Units, Positions | None |
| **D (Headcount Requirements)** | Consumer (Index User) & Projection Holder | Target headcount per unit | Units (from C); Active employee counts (from A) |

---

## 3. Module Roles & Scoping

Modules are categorized per entity based on how they interact with data.

### Scope Decision Criteria
When deciding whether to place a feature in an existing module or create a new one, evaluate these eight factors:

1. **Authority:** Who makes business decisions regarding this data?
2. **Accountability:** Who answers for auditing and accuracy?
3. **Change Rate:** Does this data change at the same pace and for the same reasons as adjacent data?
4. **Lifecycle:** Are these records archived on the same schedule?
5. **Security:** Does this data share the same access control policies?
6. **Transactional Boundaries:** Must this data update atomically in a single database transaction?
7. **Lag Tolerance:** Can consumers operate on a slight time delay?
8. **Team Boundaries:** Is a separate team deploying and maintaining this component?

### Module Scoping Rules
* **Data Owner / Broadcaster:** Issues permanent IDs, maintains master reference tables, publishes change events via an outbox, and provides a pagination-supported Read API.
* **Consumer Type 1 (Attribute User):** Treats external data as descriptive labels (e.g., Payroll storing `employee_id` to display unit names). Updates to external labels do not affect Payroll's business validity.
* **Consumer Type 2 (Index User):** Uses external data as a structural key (e.g., Requirements indexing target headcount by `unit_id`). Changes in the owner module directly impact the consumer's business rules.
* **Hybrid Module:** Owns certain entities while consuming others (e.g., HR Core owns Employees, but consumes Units from Org Structure).
* **Projection Holder:** Computes aggregate stats (e.g., active employee counts per unit) from streamed events without replicating full master records.

---

## 4. Data Storage & Table Design

Each table type serves a specific architectural boundary and accountability requirement.


```

```
   DATA OWNER                                CONSUMER MODULE

```

+-----------------------+            +-------------------------------------+
| Master Reference Table|            | Cache Table (Read-Only Copy)        |
|  - id (UUID)          |            |  - local_id                         |
|  - version (Monotonic)|===Events==>|  - source_id (UUID)                 |
|  - business_attrs     |            |  - source_version                   |
+-----------------------+            |  - cached_attrs                     |
+-------------------------------------+
|
Joined via ID
v
+-------------------------------------+
| Transaction Table                   |
|  - transaction_id                   |
|  - foreign_source_id (UUID)         |
|  - local_business_attrs             |
+-------------------------------------+

```

### Table Definitions & Rules

#### 1. Master Reference Table (Owner)
* **Purpose:** The single source of truth for an entity.
* **Core Columns:** `id` (UUID), `version` (integer, increments on every edit), `status` (`active`, `inactive`, `deleted`), `replaced_by` (array of UUIDs for splits/merges), `effective_from`, `effective_to`, `updated_at`.
* **Rules:** Written strictly by the owner module. Every change appends an entry to an event outbox table within the same database transaction.

#### 2. Cache Table (Consumer)
* **Purpose:** A read-only local store of external reference data.
* **Core Columns:** `local_id`, `source_id` (owner's UUID), `source_version`, `cached_fields`, `status`, `last_synced_at`.
* **Rules:** Populated exclusively by background event processors or sync jobs. Never modified directly by user actions or local application code.

#### 3. Transaction Table (Consumer/Owner)
* **Purpose:** Stores core operational data (e.g., payroll entries, employee assignments).
* **Rules:** Holds references to external entities using their permanent IDs (`source_id`). Avoids storing external descriptive text (e.g., unit names) unless an immutable historical snapshot is legally required.

#### 4. Projection Table (Consumer)
* **Purpose:** Holds calculated summaries (e.g., total headcount per unit).
* **Rules:** Completely disposable and rebuildable at any time by replaying event history or querying the owner's Read API.

#### 5. Crosswalk Table (Owner/Consumer)
* **Purpose:** Maps internal UUIDs to third-party or legacy external codes (e.g., government job codes).
* **Rules:** Contains mapping fields (`internal_id`, `external_code`, `valid_from`, `valid_to`). Entries are closed via dates, never hard-deleted.

---

## 5. Inter-System Communication

### Communication Flow
Modules combine **Event Broadcasting** with a **Read API**:

1. **Transactional Outbox:** The owner writes business data and an event record in a single local database transaction.
2. **Event Relay:** A background worker reads the outbox and publishes messages to the event bus.
3. **Consumer Ingestion:** Consumers process events idempotently, updating local caches.
4. **Catch-Up & Recovery:** If a consumer falls behind or drops events, it queries the owner's Read API using cursor pagination (`?updated_after=timestamp`).


```

[Owner DB Transaction]
├── Write Master Record
└── Write Outbox Event ──> [Relay Worker] ──> [Event Bus] ──> [Consumer Local Apply]
|
[Consumer API Sync] <────── REST / Read API (Catch-up / Recovery) ──────┘

```

### Critical Integration Rules

1. **No Shared Databases:** Inter-module communication occurs strictly via APIs and event streams.
2. **Additive Contract Changes:** Adding new fields or endpoints is allowed. Modifying existing field names, removing fields, or changing data types requires a new major API/schema version.
3. **Idempotent Apply Loop:** Consumers must check event versions before applying changes:

```

IF event.version > cached_row.source_version:
UPDATE cache SET data = event.data, source_version = event.version
ELSE:
DISCARD event (Duplicate or Out-of-Order)

```
4. **Local Validation:** Before a module accepts a user request referencing an external entity (e.g., assigning an employee to a unit), it validates the ID against its *local cache*, not via a live blocking call to the owner.
5. **Handling Divergent Caches:** If Consumer A passes an event containing a `unit_id` to Consumer B, Consumer B validates the unit against its own local cache. If missing, Consumer B creates a temporary placeholder row and asynchronously queries the owner's Read API.

---

## 6. Common System Workflows

### 1. Initial System Sync / Bootstrap
* The owner exposes a cursor-paginated endpoint sorted by `updated_at`.
* The consumer fetches records in pages, applying them through its standard idempotent import logic.
* Once caught up, the consumer switches to processing real-time events.

### 2. Record Creation
* Owner creates the record (`version = 1`) and emits a `Created` event.
* Consumers add the row to their local cache. Other local operations referencing this new ID can now pass validation.

### 3. Record Update / Reparenting
* Owner updates attributes or hierarchy relations (`parent_id`), increments the version (`version + 1`), and emits an `Updated` event.
* Consumers update their local cache. Systems calculating hierarchical roll-ups clear local view caches to reflect the structural shift.

### 4. Record Merge
* Owner designates one surviving record and marks absorbed records as `status = inactive`, setting `replaced_by = [surviving_id]`.
* Consumers update their cache to display the `inactive` state. Existing transaction records retain historical links to the absorbed ID, but UI views provide navigation links to the surviving ID.

### 5. Record Split
* Owner creates $N$ new records with fresh IDs and marks the original record `status = inactive` with `replaced_by = [new_id_1, new_id_2]`.
* Consumers store the new records in their local cache. Systems managing dependent business rules (e.g., headcount limits) flag the affected entries for human review rather than automatically reassigning records.

### 6. Data Erasure (GDPR / Privacy Compliance)
* When personal data must be erased, the owner anonymizes fields in place or issues an explicit `Erasure` event while retaining the record's UUID and version number to preserve referential integrity.
* Consumers execute matching anonymization scripts across local caches, projections, and logs.

---

## 7. Design Checklist for New Modules

- [ ] **Data Ownership:** Are all entities explicitly classified as either *Owned* or *Consumed*?
- [ ] **Identifier Policy:** Does every owned entity use an opaque, non-business permanent ID (e.g., UUID)?
- [ ] **Database Isolation:** Is the module database entirely independent with zero direct external reads/writes?
- [ ] **Outbox Pattern:** Is state modification paired with an event outbox in a single local transaction?
- [ ] **Idempotent Ingestion:** Does the apply pipeline check `event.version > local.source_version` before writing?
- [ ] **Resilience:** Can the module continue serving read-and-write requests using its local cache if external dependency systems go offline?
- [ ] **Catch-Up Mechanism:** Is there a scheduled reconciliation process that queries the owner's Read API for drift detection?
- [ ] **Contract Integrity:** Are API schemas enforced as additive-only, with deprecation headers specified for retiring fields?

```
