# Author decisions, 2026-10-09 (verbatim from chat)

Audience: both architects and developers.
Modules A, B, C, D are examples; no real OSDM modules.
Scope criteria for module boundaries: assistant to suggest.
Split and merge apply to other entities too; "when applicable" refers to business rules.
Technology: neutral.
Delete: allow an exception (for example personal-data erasure).
Audit or regulatory requirement for accountability: none yet.
Language and format: English, Markdown, atomic pages, to be uploaded to GitHub or another repository.
Open choices (subscribe vs call on demand; unverified source sections): list options and explain the conditions under which each applies.
Accountability default: assistant proposes a recommended default, revisable.

Starting outline (author):
1. Module types: a. source of truth / data owner / broadcaster; b. data user type 1 (reference data as attributes); c. data user type 2 (reference data as index).
2. Table types: a. master reference; b. cache of master reference; c. transaction.
3. Use cases: a. initial master broadcast to empty caches; b. new record; c. split; d. merge; e. delete.
4. Inter-system communication: a. flow; b. payload; c. technology; d. rules for integrity and independence.
