# Methodology

## Analytical objective

The goal is to rank new onboarding candidates for review using relational evidence that is unavailable to a conventional one-row-per-applicant model. The graph layer is designed to be explainable and additive to existing controls.

## Point-in-time design

Each evaluation anchor separates three concepts:

- **seeds:** fraud confirmed and available before the decision cutoff;
- **candidates:** applications being scored at the cutoff;
- **targets:** later outcomes used only for evaluation.

Graph edges and node attributes are restricted to a trailing observation window that ends before the candidate decision. This prevents future transactions, later fraud confirmation, and post-onboarding performance from leaking into features.

## Graph construction

The logical graph can contain account, customer, terminal, and other institution-neutral entity types. Directed transfer edges retain their event time and amount. Ownership and other structural edges are kept separate from money-flow edges so algorithms can use the appropriate semantics.

Subgraph extraction uses iterative joins from seeds and candidates. Expansion is bounded by hop count and guarded against high-degree infrastructure. A hub may remain measurable while being prevented from expanding the frontier.

## Feature families

### Local topology

Distinct inbound and outbound neighbours provide a simple activity baseline. Counts can be calculated on the full graph and on a rare-counterparty projection.

### Time-respecting proximity

Multi-source breadth-first expansion measures the shortest valid path between a candidate and historical fraud. Temporal constraints ensure that a chain follows feasible event order. Closeness can be represented as `1 / (1 + hops)`.

### Shared rare infrastructure

A counterparty used by only a small number of distinct senders is more specific than a widely used merchant or public service. A candidate sharing such a node with a known seed receives an interpretable exposure count.

### Personalized diffusion

Personalized PageRank or a related restart walk spreads a fixed amount of risk mass from the historical seed set. It complements minimum-hop distance by accounting for multiple paths and graph connectivity.

### Components and communities

Connected components identify isolated clusters. Label propagation provides a scalable community approximation. Seed density within a community can be used only when the calculation excludes candidate targets.

### Motifs and dense blocks

Motifs encode hypotheses such as shared collectors, common cash-out terminals, directed cycles, fan-in/fan-out structures, and pass-through chains. Dense-subgraph scoring provides an unsupervised view of coordinated behaviour.

## Feature selection

The project uses incremental-then-select evaluation:

1. establish a small, interpretable baseline;
2. add one candidate feature at a time;
3. measure marginal change in rank-based capture metrics;
4. reject redundant or unstable features;
5. verify selections on held-out time anchors.

This is preferable to choosing features from a single noisy ranking, especially when fraud prevalence is low.

## Validation

Primary measures are capture at a fixed review percentage and lift over the population base rate. Supporting checks include risk-bin sloping, information value, monotonicity, feature correlation, leave-one-anchor-out evaluation, and sensitivity sweeps for graph thresholds.

All metrics in this public repository are demonstrated only with synthetic data. Employer-specific values and conclusions are not published.

## Explainability

The final output includes both a sortable score and reason codes such as shared rare counterparty, short path to a seed, dense block, or unusual fan-out. Review graphs should be deliberately small, pseudonymous, and limited to the evidence needed for an investigator.
