"""Graph Compaction: Find the decisive forks.

Key insight from igloominance:
- Some forks are highly decisive, determining most downstream positions
- Graph compaction distills the crucial forks that decide one's worldview
- These map to psychological archetypes of political thinking

The null hypothesis: we all think the same way and the graph is linear.
The structure of divergence itself is the signal.
"""

from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
import math

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from graph.forks import Fork, ForkTree, ForkLevel
from models.walker import Walker


@dataclass
class ForkDecisiveness:
    """How decisive a fork is in determining downstream positions."""
    fork_id: str

    # Predictive power
    downstream_positions: int = 0      # How many positions does this fork influence?
    prediction_accuracy: float = 0.0   # How well does this fork predict others?
    information_gain: float = 0.0      # Entropy reduction from knowing this fork

    # Structural importance
    betweenness: float = 0.0           # How often is this fork on paths between others?
    depth: int = 0                     # How deep in the tree (0 = root)

    # Empirical importance
    variance_explained: float = 0.0    # How much of population variance does this explain?
    archetype_alignment: float = 0.0   # How well does this align with known archetypes?

    @property
    def decisiveness_score(self) -> float:
        """Combined decisiveness score."""
        return (
            self.information_gain * 0.3 +
            self.prediction_accuracy * 0.25 +
            (self.downstream_positions / 50) * 0.2 +  # Normalized
            self.variance_explained * 0.15 +
            self.betweenness * 0.1
        )


@dataclass
class Archetype:
    """A psychological archetype of political thinking.

    Derived from the decisive fork patterns.
    """
    name: str
    description: str

    # Defining fork choices
    fork_choices: dict[str, str] = field(default_factory=dict)  # fork_id -> "a" or "b"

    # Metadata
    population_share: float = 0.0  # Estimated % of population
    stability: float = 0.0         # How stable is this archetype over time?

    # Psychological correlates
    traits: list[str] = field(default_factory=list)  # Big Five correlates, etc.

    def matches(self, walker: Walker, tree: ForkTree) -> float:
        """How well does a walker match this archetype?"""
        if not self.fork_choices:
            return 0.0

        matches = 0
        total = 0

        for fork_id, expected_choice in self.fork_choices.items():
            pos_id_a = f"{fork_id}_a"
            pos_id_b = f"{fork_id}_b"

            if pos_id_a in walker.positions_accepted:
                total += 1
                if expected_choice == "a":
                    matches += 1
            elif pos_id_b in walker.positions_accepted:
                total += 1
                if expected_choice == "b":
                    matches += 1

        return matches / total if total > 0 else 0.0


class GraphCompactor:
    """Compacts the fork tree to find decisive forks."""

    def __init__(self, tree: ForkTree):
        self.tree = tree
        self.decisiveness: dict[str, ForkDecisiveness] = {}

    def analyze(self, walkers: list[Walker] = None) -> list[ForkDecisiveness]:
        """Analyze all forks for decisiveness."""

        for fork_id, fork in self.tree.forks.items():
            dec = ForkDecisiveness(fork_id=fork_id)

            # Calculate downstream positions
            dec.downstream_positions = self._count_downstream(fork_id)

            # Calculate depth
            dec.depth = len(self.tree.get_path_to_root(fork_id)) - 1

            # Calculate betweenness (simplified)
            dec.betweenness = self._calculate_betweenness(fork_id)

            # Calculate information gain (based on structure)
            dec.information_gain = self._calculate_information_gain(fork)

            # If we have walker data, calculate empirical metrics
            if walkers:
                dec.prediction_accuracy = self._calculate_prediction_accuracy(fork_id, walkers)
                dec.variance_explained = self._calculate_variance_explained(fork_id, walkers)

            self.decisiveness[fork_id] = dec

        # Sort by decisiveness
        return sorted(
            self.decisiveness.values(),
            key=lambda d: d.decisiveness_score,
            reverse=True
        )

    def _count_downstream(self, fork_id: str) -> int:
        """Count positions downstream of this fork."""
        count = 2  # The fork itself has 2 positions

        def recurse(fid: str):
            nonlocal count
            children = self.tree.get_children(fid)
            for child in children:
                count += 2  # Each child fork has 2 positions
                recurse(child.id)

        recurse(fork_id)
        return count

    def _calculate_betweenness(self, fork_id: str) -> float:
        """Simplified betweenness centrality."""
        fork = self.tree.forks.get(fork_id)
        if not fork:
            return 0.0

        # Betweenness approximated by: children * depth_factor
        children = len(self.tree.get_children(fork_id))
        path = self.tree.get_path_to_root(fork_id)
        depth = len(path) - 1

        # Middle of tree has highest betweenness
        max_depth = max(len(self.tree.get_path_to_root(f)) for f in self.tree.forks) - 1
        depth_factor = 1.0 - abs(depth - max_depth/2) / (max_depth/2 + 1)

        return min(1.0, children * 0.2 * depth_factor)

    def _calculate_information_gain(self, fork: Fork) -> float:
        """Information gain from knowing this fork's answer.

        Based on:
        - Polarization (high = more informative)
        - Importance (structural weight)
        - Number of downstream forks
        """
        downstream = self._count_downstream(fork.id)
        max_downstream = len(self.tree.forks) * 2

        # High polarization = more decisive
        polarization_factor = fork.polarization

        # More downstream = more informative
        downstream_factor = downstream / max_downstream

        # Importance weight
        importance_factor = fork.importance

        return (polarization_factor * 0.4 +
                downstream_factor * 0.3 +
                importance_factor * 0.3)

    def _calculate_prediction_accuracy(self, fork_id: str, walkers: list[Walker]) -> float:
        """How well does knowing this fork predict other forks?"""
        if not walkers:
            return 0.0

        fork = self.tree.forks.get(fork_id)
        if not fork:
            return 0.0

        # Get child forks
        children = self.tree.get_children(fork_id)
        if not children:
            return 0.5  # No children to predict

        correct = 0
        total = 0

        for walker in walkers:
            # Determine walker's choice on this fork
            pos_a = f"{fork_id}_a"
            pos_b = f"{fork_id}_b"

            if pos_a in walker.positions_accepted:
                parent_choice = "a"
            elif pos_b in walker.positions_accepted:
                parent_choice = "b"
            else:
                continue  # Walker hasn't taken this fork

            # Check if children align with expected traditions
            for child in children:
                child_a = f"{child.id}_a"
                child_b = f"{child.id}_b"

                if child_a in walker.positions_accepted:
                    child_choice = "a"
                elif child_b in walker.positions_accepted:
                    child_choice = "b"
                else:
                    continue

                # Predict: same traditions should correlate
                parent_traditions = set(fork.traditions_a if parent_choice == "a" else fork.traditions_b)
                child_expected = set(child.traditions_a if child_choice == "a" else child.traditions_b)

                # If traditions overlap, prediction is correct
                if parent_traditions & child_expected:
                    correct += 1
                total += 1

        return correct / total if total > 0 else 0.5

    def _calculate_variance_explained(self, fork_id: str, walkers: list[Walker]) -> float:
        """How much of population variance does this fork explain?"""
        if not walkers:
            return 0.0

        # Count choices
        a_count = 0
        b_count = 0

        for walker in walkers:
            if f"{fork_id}_a" in walker.positions_accepted:
                a_count += 1
            elif f"{fork_id}_b" in walker.positions_accepted:
                b_count += 1

        total = a_count + b_count
        if total == 0:
            return 0.0

        # Variance is maximized when split is 50/50
        p = a_count / total
        variance = 4 * p * (1 - p)  # Peaks at 0.5

        return variance

    def get_minimal_set(self, target_accuracy: float = 0.8) -> list[Fork]:
        """Get minimal set of forks that achieve target prediction accuracy.

        This is the "compacted" graph - the essential forks.
        """
        if not self.decisiveness:
            self.analyze()

        # Sort by decisiveness
        sorted_forks = sorted(
            self.decisiveness.items(),
            key=lambda x: x[1].decisiveness_score,
            reverse=True
        )

        minimal_set = []
        cumulative_accuracy = 0.0

        for fork_id, dec in sorted_forks:
            fork = self.tree.forks.get(fork_id)
            if fork:
                minimal_set.append(fork)
                # Approximate cumulative accuracy
                cumulative_accuracy += dec.information_gain * (1 - cumulative_accuracy)

                if cumulative_accuracy >= target_accuracy:
                    break

        return minimal_set

    def extract_archetypes(self, n: int = 6) -> list[Archetype]:
        """Extract psychological archetypes from decisive forks.

        These are the fundamental "types" of political thinking.
        """
        # Get the most decisive forks
        if not self.decisiveness:
            self.analyze()

        decisive = self.get_minimal_set(target_accuracy=0.7)[:5]

        # Generate archetypes from combinations of top fork choices
        # For now, use predefined archetypes aligned with decisive forks

        archetypes = [
            Archetype(
                name="The Traditionalist",
                description="Order through hierarchy and accumulated wisdom",
                fork_choices={
                    "human_nature": "a",      # Humans flawed
                    "knowledge": "a",          # Tradition
                    "equality_vs_hierarchy": "b",  # Natural hierarchy
                    "tradition_vs_progress": "b",  # Tradition
                    "freedom_vs_equality": "b",    # Freedom
                },
                traits=["conscientiousness", "low_openness", "orderliness"],
                population_share=0.20
            ),
            Archetype(
                name="The Progressive",
                description="Progress through liberation and rational reform",
                fork_choices={
                    "human_nature": "b",      # Humans perfectible
                    "knowledge": "b",          # Reason
                    "equality_vs_hierarchy": "a",  # Equality
                    "tradition_vs_progress": "a",  # Progress
                    "freedom_vs_equality": "a",    # Equality
                },
                traits=["openness", "agreeableness", "compassion"],
                population_share=0.22
            ),
            Archetype(
                name="The Libertarian",
                description="Freedom as the paramount value",
                fork_choices={
                    "human_nature": "b",      # Humans good (leave alone)
                    "individualism": "a",      # Individual
                    "freedom_vs_equality": "b",    # Freedom
                    "markets": "b",            # Free markets
                    "state": "b",              # Minimal state
                },
                traits=["low_agreeableness", "autonomy", "individualism"],
                population_share=0.12
            ),
            Archetype(
                name="The Communitarian",
                description="Society as organic whole, duty over rights",
                fork_choices={
                    "individualism": "b",      # Collective
                    "equality_vs_hierarchy": "a",  # Equality (of community)
                    "nationalism": "b",        # Bounded community
                    "welfare": "a",            # Expansive
                },
                traits=["agreeableness", "collectivism", "loyalty"],
                population_share=0.15
            ),
            Archetype(
                name="The Technocrat",
                description="Rational optimization by experts",
                fork_choices={
                    "knowledge": "b",          # Reason/empiricism
                    "change": "b",             # Bold transformation
                    "state": "a",              # Expansive (expert-led)
                    "tech_regulation": "a",    # Light touch
                },
                traits=["intellect", "systemizing", "low_tradition"],
                population_share=0.10
            ),
            Archetype(
                name="The Populist",
                description="The people vs the elites",
                fork_choices={
                    "equality_vs_hierarchy": "a",  # Against hierarchy
                    "nationalism": "b",        # National
                    "trade": "b",              # Protected
                    "immigration": "b",        # Restricted
                },
                traits=["distrust", "anti_elite", "in_group_loyalty"],
                population_share=0.18
            ),
        ]

        return archetypes[:n]


def analyze_fork_structure(tree: ForkTree) -> dict:
    """Analyze the structure of the fork tree.

    Tests the null hypothesis: is the graph linear or divergent?
    """
    compactor = GraphCompactor(tree)
    decisiveness = compactor.analyze()

    # Calculate structural metrics
    total_forks = len(tree.forks)
    max_depth = max(len(tree.get_path_to_root(f)) for f in tree.forks) - 1

    # Branching factor
    branch_counts = []
    for fork in tree.forks.values():
        children = len(tree.get_children(fork.id))
        if children > 0:
            branch_counts.append(children)
    avg_branching = sum(branch_counts) / len(branch_counts) if branch_counts else 1

    # Linearity score (1 = perfectly linear, 0 = maximally branched)
    linearity = 1.0 / avg_branching if avg_branching > 0 else 1.0

    # Top decisive forks
    top_decisive = decisiveness[:5]

    return {
        "total_forks": total_forks,
        "max_depth": max_depth,
        "avg_branching_factor": avg_branching,
        "linearity_score": linearity,
        "is_divergent": linearity < 0.8,
        "top_decisive_forks": [
            {
                "fork_id": d.fork_id,
                "question": tree.forks[d.fork_id].question[:50] + "...",
                "decisiveness": d.decisiveness_score,
                "information_gain": d.information_gain,
            }
            for d in top_decisive
        ],
        "minimal_set_size": len(compactor.get_minimal_set()),
        "archetypes": [a.name for a in compactor.extract_archetypes()],
    }
