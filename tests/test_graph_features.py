import unittest

from onboarding_fraud_graph import (
    compute_graph_features,
    rank_candidates,
    transparent_scores,
)


class GraphFeatureTests(unittest.TestCase):
    def setUp(self):
        self.edges = [
            ("SEED", "RARE_COLLECTOR"),
            ("CANDIDATE_A", "RARE_COLLECTOR"),
            ("CO_FEEDER", "RARE_COLLECTOR"),
            ("SEED", "BRIDGE"),
            ("BRIDGE", "CANDIDATE_C"),
            ("CANDIDATE_C", "PRIVATE_PAYEE"),
            ("CANDIDATE_B", "PUBLIC_SERVICE"),
            ("ORDINARY_1", "PUBLIC_SERVICE"),
            ("ORDINARY_2", "PUBLIC_SERVICE"),
            ("ORDINARY_3", "PUBLIC_SERVICE"),
        ]
        self.features = compute_graph_features(
            self.edges,
            seeds={"SEED"},
            candidates={"CANDIDATE_A", "CANDIDATE_B", "CANDIDATE_C"},
            max_beneficiary_fanin=3,
        )

    def test_shared_rare_beneficiary_excludes_public_hub(self):
        self.assertEqual(
            self.features["CANDIDATE_A"].shared_rare_beneficiaries, 1
        )
        self.assertEqual(
            self.features["CANDIDATE_B"].shared_rare_beneficiaries, 0
        )

    def test_minimum_hops(self):
        self.assertEqual(self.features["CANDIDATE_A"].min_hops_to_seed, 2)
        self.assertEqual(self.features["CANDIDATE_C"].min_hops_to_seed, 2)
        self.assertIsNone(self.features["CANDIDATE_B"].min_hops_to_seed)

    def test_transparent_scores_are_bounded_and_ranked(self):
        scores = transparent_scores(self.features)
        self.assertTrue(all(0.0 <= score <= 1.0 for score in scores.values()))
        ranked = list(rank_candidates(scores))
        self.assertEqual(ranked[-1][0], "CANDIDATE_B")

    def test_invalid_fanin_threshold(self):
        with self.assertRaises(ValueError):
            compute_graph_features([], {"SEED"}, {"CANDIDATE"}, max_beneficiary_fanin=0)


if __name__ == "__main__":
    unittest.main()
