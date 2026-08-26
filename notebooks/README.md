# Spark notebooks

The `pipeline/` directory contains generalized, output-free Jupyter notebooks from the algorithm portion of the project. The original executed notebooks remain in the ignored local archive.

The public sequence begins at subgraph construction because source-system extraction is institution-specific and intentionally not published.

| Stage | File | Purpose |
|---|---|---|
| 03 | `03_seed_subgraph.ipynb` | Build a bounded, point-in-time seed/candidate neighbourhood |
| 04 | `04_graph_features.ipynb` | Compute proximity, shared-neighbour, diffusion, and component features |
| 04b | `04b_communities.ipynb` | Compute isolated label-propagation community features |
| 05 | `05_motifs.ipynb` | Compute collector, cash-out, cycle, pass-through, and dense-block motifs |
| 06 | `06_final_score.ipynb` | Select incremental features and build an interpretable blended score |
| 07 | `07_scorecard.ipynb` | Explore a regularized WOE-logistic cross-check |
| 08 | `08_investigation.ipynb` | Produce reason codes and small investigation graphs |
| 09 | `09_anomaly.ipynb` | Experimental unsupervised features for graph-isolated candidates |
| 98 | `98_sensitivity_sweep.ipynb` | Read-only sensitivity logic for rare-counterparty thresholds |

Prerequisites:

- an existing Spark session named `spark`;
- normalized tables matching [the public data contract](../docs/data-contract.md);
- a writable, isolated development schema;
- GraphFrames on the cluster classpath for optional GraphFrames branches;
- NumPy, pandas, matplotlib, and NetworkX for the relevant analysis or visualization cells.

Review every configuration cell before execution. Several stages overwrite their own configured output tables.
Operational tuning values in the public configuration cells are illustrative and intentionally differ from internal settings; many can be overridden through environment variables. Calendar anchors are synthetic examples. Review and recalibrate every setting on authorized development data.

These exports are generalized code references, not a claim of end-to-end reproducibility. Stage 09 was not executed in the archived internship run, and the archived stage-98 notebook contains no saved result evidence. Stage 07 is an exploratory comparison, not a deployment-ready model. Production use would additionally require deterministic tie handling, tests against approved data, monitoring, access controls, and independent model-risk review.
