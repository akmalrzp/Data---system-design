# OSDM system design: integration and API design summary

Date: 2026-10-09
Scope: best practice for integrating independent systems, with an HR (Organisasi & SDM) example.

## 1. Question

System A produces data A1 and system B uses it. How do both keep the same reference to A1 while staying independent?

## 2. Core answer

- One system owns each record (the system of record).
- The owner issues a permanent, opaque ID (e.g. UUID). It never changes, is never reused, and carries no business meaning.
- Consumers store that ID as a foreign reference, plus only the fields they need, as a read-only cache.
- The owner publishes a small, versioned contract (OpenAPI for request/response, a schema registry for events), separate from its internal model. Changes are additive only.
- Changes flow as events (transactional outbox on the producer), with a read API for lookups and catch-up.
- Consumers apply events idempotently and only when the version is newer.
- Each consumer translates the owner's model into its own at its edge (anti-corruption layer).
- No shared databases.

## 3. Research report and its reliability

Full report: `API design for system integration.md` (delivered earlier in the session).

| Topic | Status |
|---|---|
| Ownership, identifiers, system of record, anti-corruption layer | Not source-verified (background knowledge) |
| Integration styles, thin vs fat events, coupling | Entirely unverified |
| Delivery semantics, outbox, idempotency, ETags, tombstones, sagas | Partly verified (Confluent, microservices.io, Stripe, Azure, Debezium, Ed-Fi) |
| Contracts, compatibility modes, versioning, deprecation, errors | Partly verified (Zalando, Google AIPs, Confluent, RFC 9457/9745/9413) |

Not covered by any usable source: retries/backoff, dead-letter queues, circuit breakers, tracing, SLOs, drift detection, OAuth/mTLS, personal-data erasure rules (UU PDP, GDPR; confirm with legal). Page fetching was largely blocked, so the unverified sections should be checked before they go into an architecture decision record. The Idempotency-Key header is an expired IETF draft, not a standard.

## 4. Worked example: employee record (A = HR Core, B = Payroll)

- A owns Employee and issues `employee_id`. `employee_number` is an ordinary attribute, not the join key.
- A publishes `employee.changed` with `event_id`, `employee_id`, monotonic `version`, and non-sensitive fields only. Salary and national ID stay out of the event and are read through an authorised endpoint.
- B keeps its own table: own primary key, `employee_id` (unique), `source_version`, cached fields, and its own data (e.g. `pay_grade`).
- Apply rule: apply only if event version > stored version. Duplicates and late events are ignored. Termination is a versioned status, not a deletion, so stale updates cannot resurrect a record.
- Catch-up and bootstrap: cursor-paginated `GET /v1/employees?updated_after=...`, applied through the same version check.
- Nightly reconciliation compares counts or hashes per range and repairs gaps by re-fetching.
- Unknown fields and enum values are ignored. Malformed required fields are rejected.

## 5. System C owns Unit and Position

- A broadcasts `unit_id` and `position_id` only, not text. The names belong to C, so copying them would republish data A does not own, and a rename in C would leave stale copies.
- C publishes `unit.changed` and `position.changed`. A and B subscribe and keep local copies of C's data. B resolves names by joining on IDs in its own copy.
- A validates `unit_id` and `position_id` against its C cache before accepting an assignment.
- Unknown ID in B: store it, show a placeholder, call C's read API on the miss. Do not use cross-system foreign keys.
- C never hard-deletes. It marks entries `inactive`. Merges and splits use `replaced_by`, and A then reassigns affected employees.
- History: A includes `effective_from` on assignments. C needs effective-dated names if labels are needed as of a past date.
- Optional non-authoritative `unit_name` in A's event is possible but not recommended.

## 6. System D uses units as an index for business rules

D fills the number of employees required per unit.

- Same pattern as B: subscribe to C, keep a local copy, reference `unit_id`.
- Difference: `unit_id` is the business key of D's own records, so unit lifecycle changes in C affect D.
- D validates that the unit exists and is active before accepting a requirement.
- Inactive unit: flag the requirement for review or close it with `effective_to`.
- Merge or split: D flags requirements and lets a person decide. It does not move them silently.
- Hierarchy changes in C change D's roll-up totals, so D reads `parent_unit_id` from its C copy.
- Requirements are effective-dated.
- Actual headcount comes from A. D subscribes to A and keeps a projection `unit_id -> active count`, not employee records. A read API for headcount is an alternative when exactness at read time matters.
- Transfers: A's event should include `previous_unit_id` so D can decrement the old unit.
- Counts are eventually consistent, so D's UI should show an "as of" timestamp.

## 7. External references not provided by inter-system communication

Examples: region codes, tax status, education levels. Give each reference set one internal owner and a named data steward.

| Situation | Action |
|---|---|
| Stable public standard code (ISO etc.) | Use the external code as the shared key. Store the standard and edition. |
| Authority changes codes over time | Key by code plus edition or effective date. Keep old codes resolvable. |
| No stable code or free-text list | Owner mints an internal ID and keeps a crosswalk to the external entry. |
| Organisation's definition differs from the external one | Keep both and map explicitly. |

Process:
- The owner imports from the external source, validates it, and publishes it as versioned events or a dataset plus a read API.
- Other systems subscribe and reference entries by code, never by text.
- Write each set into a data dictionary entry (authority, edition, owner, update schedule, change approval). Record the source choice in an ADR.
- Pin editions. The owner announces edition changes with a cutoff date for the old one.
- Local extensions go in the consumer's own table keyed by the code.
- One name must never carry two meanings. If meanings conflict, split into two named sets.
- Do not let each system download the external list itself, store only name text, or hard-delete retired entries.

## 8. Reasoning basis

Sections 5 to 7 are design reasoning from the report's ownership and contract principles, not from cited sources. Unit, position and reference-data patterns were not separately researched.

## 9. Open points

- Verify the unverified report sections with working source access before any architecture decision record.
- Confirm personal-data erasure obligations (UU PDP, GDPR) with legal, since deletes must reach every consumer's copy.
- Decide whether B and D subscribe to C or call its read API on demand (simpler, but depends on C being up).
- Identify the actual external reference sets in use and map each to the table in section 7.
