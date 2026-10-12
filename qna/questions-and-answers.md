Monotonic means `version` only moves one way: it goes up on every change to a record and never goes down or gets reused. In your design (per [System design guide.md:189](System design guide.md#L189)) it is a per-record counter, so each `id` has its own sequence.

- **Increase on every change:** v1, v2, v3 and so on. Whether the steps must be exactly +1 (gap-free) or just strictly greater depends on the design. Monotonic only requires "never decreases".
- **Never reset or reuse:** a rollback or correction is a new, higher version with the old content, not a lower number.
- **Why it matters:** it is the ordering guard. Consumers compare the incoming version to their stored one and apply it only if it is higher, so late or duplicate events are discarded ([System design guide.md:787](System design guide.md#L787)). Without monotonicity that check breaks.

It also helps with the A/D disagreement case in your last commit. Two copies of C that disagree can be compared by version, and the higher one is the newer one. That only works if versions come from a single authoritative writer, the master. If two places can bump the version independently, they can pick the same number for different content.

- `Glossary` says: “Version: a monotonic number per record, increased on every change.”
- `Rule: ordering per entity` says events are partitioned by entity ID and carry a monotonic version so consumers can detect and discard late events.
- `Rule: idempotent, version-guarded apply` explains the actual behavior: compare the incoming version with stored source_version and ignore duplicates, stale updates, or late arrivals.

So in this wiki, a monotonic version is basically a per-record version counter that only moves forward, used as an ordering/idempotency guard.

---

Short answer: Daily refresh can be good for a reporting/projection workload, but it is usually a bad practice for anything that needs timely accuracy or operational correctness.

Why this wiki says so:
- `Eventual consistency and freshness` explicitly says consumer copies lag the owner and that you should show an “as of” timestamp.
- `Freshness and drift monitoring` treats lag and drift as measurable operational concerns, not just a batch job detail.
- The TL;DR in `qna/tldr.md` says consumers keep read-only local copies and should monitor freshness, not assume real-time sync.

So:
- Good: daily refresh is acceptable for a derived projection or aggregate used for dashboards, monthly/weekly reporting, or non-critical summaries.
- Bad: it is a poor fit for reference data or any table used in operational decisions, transactions, or user-facing data that must reflect recent changes.

Best practice in this design style:
- Keep the owner as the source of truth.
- Let consumers maintain versioned caches/projections.
- Refresh incrementally or by event-driven updates when possible.
- If a daily batch is necessary, document the freshness SLA and alert on lag/drift.
- Always display “as of” time so consumers know the data is stale by design.

So the real rule is not “never refresh daily,” but “only if the business accepts the delay.” If the delay is more than the use case tolerates, it becomes bad practice.