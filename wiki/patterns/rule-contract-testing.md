---
type: pattern
title: "Rule: contract testing"
tags: [partly-verified]
sources: [osdm-integration-summary,api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Rule: contract testing

Catch breaking changes before release.

- **Spec diffing in CI**: compare the new spec with the previous one; simplest when there are many or unknown consumers.
- **Consumer-driven contract tests**: consumers record what they use and replay it against the owner; viable with one producer and one known consumer. Classic tools fit event-driven systems poorly.
- **Bi-directional contract testing**: compares the owner's spec with consumers' recorded usage; lighter, weaker guarantees.

Choice by consumer count is an inference. Sources were secondary ([source-reliability](../ops/source-reliability.md)).
