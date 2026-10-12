---
type: module-type
title: "Feature placement test"
tags: [proposal]
sources: [author-decisions-2026-10-09,osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Feature placement test

**Proposal.** Apply in order to decide whether a feature belongs in a given module. Stop at the first decisive answer.

1. **Does the feature create or change a record that this module owns?** If yes, it belongs here (owner).
2. **Does it create or change a record owned by another module?** Then it does not belong here. Call the owner's contract or ask the owner to add a capability.
3. **Does it only read another module's data to display or validate?** It belongs here, using the local cache ([table-master-cache](../tables/table-master-cache.md)).
4. **Does it need a value that must be authoritative here but derived from elsewhere?** Make it a projection ([table-projection](../tables/table-projection.md)) or own the field here.
5. **Does it need data the owner has not published?** Request a contract addition; do not read the owner's database.
6. **Does it mix data from two owners in one atomic write?** Redesign: separate each write per owner, coordinated by a compensating process, or move the entities into one module.

Record the result in the [data-dictionary-and-adr](../ops/data-dictionary-and-adr.md) entry for the entity. Scope criteria: [module-scope-criteria](module-scope-criteria.md).
