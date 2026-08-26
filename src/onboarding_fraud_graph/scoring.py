"""Transparent percentile-rank scoring for the synthetic graph features."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, Mapping, Sequence, Tuple

from .features import FeatureVector

DEFAULT_FEATURES: Tuple[str, ...] = (
    "shared_rare_beneficiaries",
    "closeness_to_seed",
    "out_degree",
)


def _percentile_ranks(values: Mapping[str, float]) -> Dict[str, float]:
    """Return average-tie percentile ranks in the inclusive range [0, 1]."""

    if not values:
        return {}
    if len(values) == 1:
        return {next(iter(values)): 1.0}

    grouped = defaultdict(list)
    for key, value in values.items():
        grouped[float(value)].append(key)

    ranks: Dict[str, float] = {}
    position = 0
    denominator = float(len(values) - 1)
    for value in sorted(grouped):
        keys = grouped[value]
        first = position
        last = position + len(keys) - 1
        percentile = ((first + last) / 2.0) / denominator
        for key in keys:
            ranks[key] = percentile
        position += len(keys)
    return ranks


def transparent_scores(
    features: Mapping[str, FeatureVector],
    feature_names: Sequence[str] = DEFAULT_FEATURES,
) -> Dict[str, float]:
    """Average within-population feature percentiles into a transparent score."""

    if not feature_names:
        raise ValueError("feature_names cannot be empty")
    if not features:
        return {}

    component_ranks = []
    for feature_name in feature_names:
        raw = {}
        for candidate, vector in features.items():
            values = vector.as_mapping()
            if feature_name not in values:
                raise ValueError("unknown feature: {}".format(feature_name))
            raw[candidate] = values[feature_name]
        component_ranks.append(_percentile_ranks(raw))

    return {
        candidate: sum(ranks[candidate] for ranks in component_ranks)
        / len(component_ranks)
        for candidate in features
    }


def rank_candidates(scores: Mapping[str, float]) -> Iterable[Tuple[str, float]]:
    """Sort candidates from highest to lowest score with a stable ID tie-break."""

    return sorted(scores.items(), key=lambda item: (-item[1], item[0]))
