---
type: decision
title: "Decision: contract versioning style"
tags: [option,partly-verified]
sources: [api-design-for-system-integration]
created: 2026-10-09
updated: 2026-10-09
---

# Decision: contract versioning style

The guides read disagree. The choice is a team convention, not a correctness issue.

| Style | Source position | Notes |
|---|---|---|
| Major version in the URL path (`/v1/`), no minor versions | Google API guidance | Simple; visible; new major only for incompatible change |
| Avoid versions; media-type versioning only for incompatible change; no URL versions | Zalando guidelines | Pushes toward compatible evolution |
| Date-based version pinned per account, responses transformed backward | Stripe (2017 post, may be dated) | Heavy for two internal systems |

**Suggestion for a few internal modules** (inference): additive change within one major version; a new major version only for a truly incompatible change.

For events, use schema compatibility in a registry ([rule-additive-only-contract](../patterns/rule-additive-only-contract.md)). Retirement: [rule-deprecation-and-sunset](../patterns/rule-deprecation-and-sunset.md).
