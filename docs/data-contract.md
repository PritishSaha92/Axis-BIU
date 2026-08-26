# Normalized data contract

The generalized Spark notebooks assume pseudonymous identifiers and the following logical tables. Names can be changed through the notebook configuration section.

## Transfer edges

One row per aggregated directed transfer relationship and time period.

| Column | Type | Meaning |
|---|---|---|
| `src` | string | Pseudonymous source account identifier |
| `dst` | string | Pseudonymous destination account identifier |
| `txn_month` | string | Event month in `YYYYMM` form |
| `sum_amount` | numeric | Aggregated positive transfer amount |
| `txn_count` | integer | Number of contributing transactions |
| `first_ts` | timestamp/string | First event time in the aggregate |
| `last_ts` | timestamp/string | Last event time in the aggregate |

## Account nodes

| Column | Type | Meaning |
|---|---|---|
| `node_id` | string | Pseudonymous account identifier |
| `account_network_type` | string | Institution-neutral internal/external classification |
| `fan_in` | integer | Distinct inbound-neighbour count |
| `is_hub` | integer/boolean | High-degree infrastructure marker |

## Ownership edges

| Column | Type | Meaning |
|---|---|---|
| `src` | string | Pseudonymous customer identifier |
| `dst` | string | Pseudonymous account identifier |

## Candidate and seed nodes

One row per account and decision anchor in the extracted graph.

| Column | Type | Meaning |
|---|---|---|
| `id` | string | Pseudonymous account identifier |
| `anchor_month` | string | Decision month |
| `is_known_bad` | integer/boolean | Historical fraud seed flag available before cutoff |
| `is_candidate` | integer/boolean | Applicant/account scored at the anchor |
| `target_fraud` | integer/boolean | Held-out evaluation outcome |
| `idx` | integer | Optional contiguous graph index |

## Optional cash-out edges

| Column | Type | Meaning |
|---|---|---|
| `src` | string | Pseudonymous account identifier |
| `dst` | string | Pseudonymous terminal identifier |
| `txn_month` | string | Event month |
| `sum_amount` | numeric | Aggregated cash-out amount |
| `txn_count` | integer | Number of events |

## Privacy and quality requirements

- Direct identifiers must be removed or irreversibly tokenized before this contract is produced.
- The tokenization method and key must never be committed.
- Seed dates must represent information available at the decision cutoff, not a later final label snapshot.
- Timestamps must be precise enough to enforce temporal ordering where required.
- Missing counterparties must remain missing; do not create a single artificial null node.
- Public or merchant-like hubs should be flagged with a documented, data-driven rule.
- No real rows conforming to this contract belong in this repository.
