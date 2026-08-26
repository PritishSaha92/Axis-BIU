"""Dependency-free graph features used by the synthetic example.

The production-scale project used distributed Spark implementations. These
functions intentionally operate on tiny, synthetic graphs so the core ideas can
be reviewed without any institutional data or infrastructure.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import DefaultDict, Dict, Iterable, Mapping, Optional, Sequence, Set, Tuple

Node = str
Edge = Tuple[Node, Node]


@dataclass(frozen=True)
class FeatureVector:
    """Interpretable graph features for one candidate node."""

    in_degree: int
    out_degree: int
    shared_rare_beneficiaries: int
    min_hops_to_seed: Optional[int]
    closeness_to_seed: float

    def as_mapping(self) -> Mapping[str, float]:
        return {
            "in_degree": float(self.in_degree),
            "out_degree": float(self.out_degree),
            "shared_rare_beneficiaries": float(self.shared_rare_beneficiaries),
            "closeness_to_seed": self.closeness_to_seed,
        }


def _distinct_edges(edges: Iterable[Edge]) -> Set[Edge]:
    clean: Set[Edge] = set()
    for src, dst in edges:
        if not src or not dst or src == dst:
            continue
        clean.add((str(src), str(dst)))
    return clean


def _degrees(edges: Set[Edge]) -> Tuple[Dict[Node, int], Dict[Node, int]]:
    inbound: DefaultDict[Node, Set[Node]] = defaultdict(set)
    outbound: DefaultDict[Node, Set[Node]] = defaultdict(set)
    for src, dst in edges:
        outbound[src].add(dst)
        inbound[dst].add(src)
    return (
        {node: len(neighbours) for node, neighbours in inbound.items()},
        {node: len(neighbours) for node, neighbours in outbound.items()},
    )


def _multi_source_hops(edges: Set[Edge], seeds: Set[Node]) -> Dict[Node, int]:
    """Return undirected minimum hops from any seed.

    The distributed notebooks additionally enforce event-time ordering. The
    synthetic helper omits timestamps to keep its contract deliberately small.
    """

    adjacency: DefaultDict[Node, Set[Node]] = defaultdict(set)
    for src, dst in edges:
        adjacency[src].add(dst)
        adjacency[dst].add(src)

    distance: Dict[Node, int] = {seed: 0 for seed in seeds}
    frontier = deque(seeds)
    while frontier:
        node = frontier.popleft()
        for neighbour in adjacency.get(node, set()):
            if neighbour in distance:
                continue
            distance[neighbour] = distance[node] + 1
            frontier.append(neighbour)
    return distance


def compute_graph_features(
    edges: Sequence[Edge],
    seeds: Iterable[Node],
    candidates: Iterable[Node],
    *,
    max_beneficiary_fanin: int = 3,
) -> Dict[Node, FeatureVector]:
    """Compute a compact feature set for candidate nodes.

    A rare beneficiary is a destination paid by no more than
    ``max_beneficiary_fanin`` distinct source nodes. The shared-neighbour feature
    counts rare beneficiaries paid by both the candidate and at least one seed.
    """

    if max_beneficiary_fanin < 1:
        raise ValueError("max_beneficiary_fanin must be at least 1")

    clean_edges = _distinct_edges(edges)
    seed_set = {str(node) for node in seeds}
    candidate_set = {str(node) for node in candidates}
    in_degree, out_degree = _degrees(clean_edges)

    senders_by_beneficiary: DefaultDict[Node, Set[Node]] = defaultdict(set)
    beneficiaries_by_sender: DefaultDict[Node, Set[Node]] = defaultdict(set)
    for src, dst in clean_edges:
        senders_by_beneficiary[dst].add(src)
        beneficiaries_by_sender[src].add(dst)

    rare_beneficiaries = {
        beneficiary
        for beneficiary, senders in senders_by_beneficiary.items()
        if len(senders) <= max_beneficiary_fanin
    }
    seed_rare_beneficiaries = {
        beneficiary
        for seed in seed_set
        for beneficiary in beneficiaries_by_sender.get(seed, set())
        if beneficiary in rare_beneficiaries
    }

    hops = _multi_source_hops(clean_edges, seed_set)
    result: Dict[Node, FeatureVector] = {}
    for candidate in sorted(candidate_set):
        candidate_rare = (
            beneficiaries_by_sender.get(candidate, set()) & rare_beneficiaries
        )
        distance = hops.get(candidate)
        result[candidate] = FeatureVector(
            in_degree=in_degree.get(candidate, 0),
            out_degree=out_degree.get(candidate, 0),
            shared_rare_beneficiaries=len(
                candidate_rare & seed_rare_beneficiaries
            ),
            min_hops_to_seed=distance,
            closeness_to_seed=0.0 if distance is None else 1.0 / (1.0 + distance),
        )
    return result
