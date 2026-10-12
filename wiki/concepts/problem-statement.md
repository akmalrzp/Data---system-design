---
type: concept
title: "Problem statement"
tags: [principle]
sources: [osdm-integration-summary,author-decisions-2026-10-09]
created: 2026-10-09
updated: 2026-10-09
---

# Problem statement

System A produces data A1 and system B uses it. Both must keep the same reference to A1 while staying independent: separate release cycles, separate databases, and tolerance for the other being down or changing.

The guide answers four questions:
1. What kinds of modules exist, and where does each feature belong? See [guide-01-module-types](../guide/guide-01-module-types.md).
2. What kinds of tables exist, and how is each one made accountable? See [guide-02-table-types](../guide/guide-02-table-types.md).
3. How do modules talk without becoming coupled? See [guide-03-communication](../guide/guide-03-communication.md).
4. What happens to each module and table in common situations (bootstrap, new record, split, merge, delete)? See [guide-04-use-cases](../guide/guide-04-use-cases.md).

The answer rests on [principles](principles.md). Vocabulary is in [glossary](glossary.md). Examples use [worked-example](worked-example.md).
