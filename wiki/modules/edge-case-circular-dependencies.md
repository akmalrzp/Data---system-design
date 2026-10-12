---
type: module-type
title: "Edge case: circular dependencies"
tags: [edge-case,proposal]
sources: [osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Edge case: circular dependencies

A consumes C; C must not consume A's entity in a way that A needs to start. Circular data dependencies prevent bootstrap and make ordering undecidable.

Rules:
- Draw the dependency graph of entities (not modules). It must be acyclic per entity.
- If two modules each need the other's data, move the shared data to a third owner, or use IDs only on one side with lazy resolution.
- Bootstrap in dependency order ([uc-initial-broadcast](../usecases/uc-initial-broadcast.md)).
