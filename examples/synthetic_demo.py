"""Run a tiny, fully synthetic onboarding-fraud graph example."""

from onboarding_fraud_graph import (
    compute_graph_features,
    rank_candidates,
    transparent_scores,
)


def main() -> None:
    edges = [
        ("KNOWN_FRAUD", "RARE_COLLECTOR"),
        ("CANDIDATE_A", "RARE_COLLECTOR"),
        ("CO_FEEDER", "RARE_COLLECTOR"),
        ("KNOWN_FRAUD", "BRIDGE"),
        ("BRIDGE", "CANDIDATE_C"),
        ("CANDIDATE_C", "PRIVATE_PAYEE"),
        ("CANDIDATE_B", "PUBLIC_SERVICE"),
        ("ORDINARY_1", "PUBLIC_SERVICE"),
        ("ORDINARY_2", "PUBLIC_SERVICE"),
        ("ORDINARY_3", "PUBLIC_SERVICE"),
    ]
    candidates = {"CANDIDATE_A", "CANDIDATE_B", "CANDIDATE_C"}
    features = compute_graph_features(
        edges,
        seeds={"KNOWN_FRAUD"},
        candidates=candidates,
        max_beneficiary_fanin=3,
    )
    scores = transparent_scores(features)

    print("Synthetic candidates ranked by graph score:\n")
    for candidate, score in rank_candidates(scores):
        vector = features[candidate]
        print(
            "{:<12} score={:.3f} shared_rare={} hops={} out_degree={}".format(
                candidate,
                score,
                vector.shared_rare_beneficiaries,
                vector.min_hops_to_seed,
                vector.out_degree,
            )
        )


if __name__ == "__main__":
    main()
