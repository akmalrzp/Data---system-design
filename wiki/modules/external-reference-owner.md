---
type: module-type
title: "Owner of external reference sets"
tags: [proposal,unverified]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Owner of external reference sets

Reference sets that come from outside the organisation (region codes, tax status, education levels) have no inter-system owner. Assign one internal module as owner and a named data steward ([external-reference-sets](../decisions/external-reference-sets.md)).

The owner:
- imports from the external authority and validates;
- publishes versioned events or a dataset plus a read API, exactly like any [data-owner-broadcaster](data-owner-broadcaster.md);
- keeps old codes resolvable and never hard-deletes retired entries;
- announces edition changes with a cutoff date ([uc-external-edition-change](../usecases/uc-external-edition-change.md)).

Consumers reference entries by code or ID, never by text.
