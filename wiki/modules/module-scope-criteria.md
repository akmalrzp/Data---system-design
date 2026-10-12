---
type: module-type
title: "Module scope criteria"
tags: [proposal]
sources: [author-decisions-2026-10-09,osdm-integration-summary]
created: 2026-10-09
updated: 2026-10-09
---

# Module scope criteria

**Proposal** (assistant's suggestion, not from a source; revise to fit the organisation). Use these measurements to decide where a module boundary falls.

| # | Criterion | Question | Boundary signal |
|---|---|---|---|
| 1 | Decision authority | Who decides the value of this data? | Different decision-makers mean different modules |
| 2 | Accountability | Who answers for its correctness and audit? | One accountable role per entity |
| 3 | Rate and reason of change | Does it change for the same reasons and at the same pace as its neighbours? | Different change drivers mean different modules |
| 4 | Lifecycle | Is it created, retired and archived on the same schedule? | Different lifecycles mean different modules |
| 5 | Access and sensitivity | Is the audience or authorisation the same? | Different confidentiality means a separate module or separate fields |
| 6 | Consistency need | Must the data change atomically with its neighbours? | Atomic need means same module |
| 7 | Consumer pattern | Do consumers need it live, or can they work from a lagged copy? | Lag-tolerant data can live elsewhere |
| 8 | Team and release independence | Can one team release it without others? | Separate teams suggest separate modules |

Rules of thumb:
- Entities that must change in one transaction belong together (criterion 6).
- If two entities differ on criteria 1, 2 and 5, split them.
- If a boundary forces constant synchronous calls to work, it is probably drawn wrongly.

See [feature-placement-test](feature-placement-test.md) for assigning single features.
