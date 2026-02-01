"""Productive Tension: Scoring challenges by what level they target.

Key insight from igloominance:
- Challenge derived beliefs, not foundational axioms
- Axioms (roots) → Positions → Policies (leaves)
- Best challenges target mid-level positions where change is tractable

Weighted Balance Theory integration (JASSS):
- SGM: Signed Graph Measure for attitude structure
- Issue constraint before evaluative extremeness
- Imbalanced triads create tension that drives change
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import math

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.position import Position
from models.edge import Edge, EdgeType
from models.walker import Walker


class TensionType(Enum):
    """Types of productive tension."""
    IMBALANCED_TRIAD = "imbalanced_triad"  # A→B→C but A⊗C
    PRIORITY_CONFLICT = "priority_conflict"  # Two values that compete
    LEVEL_MISMATCH = "level_mismatch"  # Holding policy without axiom
    TRAJECTORY_FRICTION = "trajectory_friction"  # Movement against momentum


@dataclass
class TensionScore:
    """A scored tension point in someone's belief system."""
    tension_type: TensionType
    positions_involved: list[str]
    score: float  # 0.0 (no tension) to 1.0 (high productive tension)
    tractability: float  # 0.0 (hard to change) to 1.0 (easy to shift)
    reasoning: str = ""

    @property
    def challenge_value(self) -> float:
        """Combined value for challenging this tension."""
        return self.score * self.tractability


@dataclass
class WeightedBalanceState:
    """Weighted Balance Theory state for a walker.

    From the JASSS article:
    - Attitudes have signed relations (positive/negative)
    - Triads should be balanced (product of signs = +)
    - Imbalanced triads create pressure to change
    """

    # Attitude structure (position_id -> valence from -1 to +1)
    attitudes: dict[str, float] = field(default_factory=dict)

    # Signed Graph Measure (SGM) - overall balance
    sgm: float = 0.0

    # Evaluative extremeness (how polarized)
    extremeness: float = 0.0

    # Issue constraint (how interconnected)
    constraint: float = 0.0

    def calculate_sgm(self, edges: list[Edge]) -> float:
        """Calculate Signed Graph Measure.

        SGM = (balanced triads - imbalanced triads) / total triads
        Balanced: product of edge signs = +
        Imbalanced: product of edge signs = -
        """
        if len(self.attitudes) < 3:
            return 0.0

        balanced = 0
        imbalanced = 0

        position_ids = list(self.attitudes.keys())

        # Find all triads
        for i, a in enumerate(position_ids):
            for j, b in enumerate(position_ids[i+1:], i+1):
                for c in position_ids[j+1:]:
                    # Get edge signs (or infer from attitudes)
                    sign_ab = self._get_relation_sign(a, b, edges)
                    sign_bc = self._get_relation_sign(b, c, edges)
                    sign_ca = self._get_relation_sign(c, a, edges)

                    if sign_ab is None or sign_bc is None or sign_ca is None:
                        continue

                    product = sign_ab * sign_bc * sign_ca
                    if product > 0:
                        balanced += 1
                    else:
                        imbalanced += 1

        total = balanced + imbalanced
        if total == 0:
            return 0.0

        self.sgm = (balanced - imbalanced) / total
        return self.sgm

    def _get_relation_sign(self, a: str, b: str, edges: list[Edge]) -> Optional[float]:
        """Get the signed relation between two positions."""
        for edge in edges:
            if (edge.source_id == a and edge.target_id == b) or \
               (edge.source_id == b and edge.target_id == a):
                if edge.edge_type == EdgeType.CONTRADICTS:
                    return -1.0
                elif edge.edge_type == EdgeType.IMPLIES:
                    return 1.0

        # Infer from attitude alignment
        if a in self.attitudes and b in self.attitudes:
            return 1.0 if self.attitudes[a] * self.attitudes[b] > 0 else -1.0

        return None

    def calculate_extremeness(self) -> float:
        """Calculate evaluative extremeness.

        How far from neutral are the attitudes on average?
        """
        if not self.attitudes:
            return 0.0

        total_extreme = sum(abs(v) for v in self.attitudes.values())
        self.extremeness = total_extreme / len(self.attitudes)
        return self.extremeness

    def calculate_constraint(self, edges: list[Edge]) -> float:
        """Calculate issue constraint.

        How interconnected are the positions?
        Higher constraint = changes cascade more.
        """
        if len(self.attitudes) < 2:
            return 0.0

        position_set = set(self.attitudes.keys())
        connection_count = 0

        for edge in edges:
            if edge.source_id in position_set and edge.target_id in position_set:
                connection_count += 1

        max_connections = len(self.attitudes) * (len(self.attitudes) - 1) / 2
        self.constraint = connection_count / max_connections if max_connections > 0 else 0.0
        return self.constraint

    def find_imbalanced_triads(self, edges: list[Edge]) -> list[tuple[str, str, str, float]]:
        """Find imbalanced triads that create tension.

        Returns: List of (pos_a, pos_b, pos_c, imbalance_score)
        """
        imbalanced = []
        position_ids = list(self.attitudes.keys())

        for i, a in enumerate(position_ids):
            for j, b in enumerate(position_ids[i+1:], i+1):
                for c in position_ids[j+1:]:
                    sign_ab = self._get_relation_sign(a, b, edges)
                    sign_bc = self._get_relation_sign(b, c, edges)
                    sign_ca = self._get_relation_sign(c, a, edges)

                    if sign_ab is None or sign_bc is None or sign_ca is None:
                        continue

                    product = sign_ab * sign_bc * sign_ca
                    if product < 0:
                        # Score by how strong the attitudes are
                        strength = (
                            abs(self.attitudes.get(a, 0)) +
                            abs(self.attitudes.get(b, 0)) +
                            abs(self.attitudes.get(c, 0))
                        ) / 3
                        imbalanced.append((a, b, c, strength))

        return sorted(imbalanced, key=lambda x: x[3], reverse=True)


class TensionAnalyzer:
    """Analyzes productive tension in a walker's belief system."""

    def __init__(self, graph):
        self.graph = graph

    def get_walker_balance_state(self, walker: Walker) -> WeightedBalanceState:
        """Build Weighted Balance Theory state from walker's positions."""
        state = WeightedBalanceState()

        # Convert choices to attitudes
        for choice in walker.choices:
            # Confidence affects magnitude, acceptance affects sign
            magnitude = choice.confidence
            sign = 1.0 if choice.accepted else -1.0
            state.attitudes[choice.position_id] = sign * magnitude

        # Calculate metrics
        all_edges = list(self.graph.edges.values())
        state.calculate_sgm(all_edges)
        state.calculate_extremeness()
        state.calculate_constraint(all_edges)

        return state

    def find_productive_tensions(self, walker: Walker) -> list[TensionScore]:
        """Find all productive tension points for a walker."""
        tensions = []

        # Get balance state
        balance = self.get_walker_balance_state(walker)

        # Find imbalanced triads
        all_edges = list(self.graph.edges.values())
        triads = balance.find_imbalanced_triads(all_edges)

        for a, b, c, strength in triads[:5]:  # Top 5
            tensions.append(TensionScore(
                tension_type=TensionType.IMBALANCED_TRIAD,
                positions_involved=[a, b, c],
                score=strength,
                tractability=self._estimate_tractability([a, b, c], walker),
                reasoning=f"Imbalanced triad: {a}, {b}, {c}"
            ))

        # Find priority conflicts
        priority_tensions = self._find_priority_conflicts(walker)
        tensions.extend(priority_tensions)

        # Find level mismatches
        level_tensions = self._find_level_mismatches(walker)
        tensions.extend(level_tensions)

        # Sort by challenge value
        tensions.sort(key=lambda t: t.challenge_value, reverse=True)

        return tensions

    def _find_priority_conflicts(self, walker: Walker) -> list[TensionScore]:
        """Find positions that compete via PRIORITIZES_OVER edges."""
        tensions = []
        accepted = set(walker.positions_accepted)

        # Find cases where they've accepted both sides of a priority
        for edge in self.graph.edges.values():
            if edge.edge_type != EdgeType.PRIORITIZES_OVER:
                continue

            if edge.source_id in accepted and edge.target_id in accepted:
                # They accept both, but graph says one should dominate
                source_pos = self.graph.get_position(edge.source_id)
                target_pos = self.graph.get_position(edge.target_id)

                if source_pos and target_pos:
                    tensions.append(TensionScore(
                        tension_type=TensionType.PRIORITY_CONFLICT,
                        positions_involved=[edge.source_id, edge.target_id],
                        score=edge.weight,
                        tractability=0.7,  # Priority conflicts are tractable
                        reasoning=f"'{source_pos.claim[:30]}...' typically prioritized over '{target_pos.claim[:30]}...'"
                    ))

        return tensions

    def _find_level_mismatches(self, walker: Walker) -> list[TensionScore]:
        """Find policy-level positions without supporting axioms."""
        tensions = []
        accepted = set(walker.positions_accepted)

        for pos_id in accepted:
            pos = self.graph.get_position(pos_id)
            if not pos or pos.level != "policy":
                continue

            # Check if any axiom implies this policy
            has_axiom_support = False
            implied_by = self.graph.implied_by(pos_id)

            for parent in implied_by:
                if parent.level == "axiom" and parent.id in accepted:
                    has_axiom_support = True
                    break

            if not has_axiom_support:
                tensions.append(TensionScore(
                    tension_type=TensionType.LEVEL_MISMATCH,
                    positions_involved=[pos_id],
                    score=0.6,
                    tractability=0.8,  # Leaf positions are most tractable
                    reasoning=f"Policy '{pos.claim[:40]}...' lacks axiom foundation"
                ))

        return tensions

    def _estimate_tractability(self, position_ids: list[str], walker: Walker) -> float:
        """Estimate how tractable these positions are to change.

        Key insight: Challenge derived beliefs, not foundational axioms.
        """
        if not position_ids:
            return 0.5

        tractability_sum = 0.0

        for pos_id in position_ids:
            pos = self.graph.get_position(pos_id)
            if not pos:
                tractability_sum += 0.5
                continue

            # Level affects tractability
            level_score = {
                "axiom": 0.2,      # Hardest to change
                "position": 0.6,  # Mid-level, best target
                "policy": 0.9,    # Easiest but least impactful
            }.get(pos.level, 0.5)

            # How confidently did they hold this?
            for choice in walker.choices:
                if choice.position_id == pos_id:
                    # Lower confidence = more tractable
                    level_score *= (1.5 - choice.confidence)
                    break

            tractability_sum += level_score

        return min(1.0, tractability_sum / len(position_ids))

    def score_challenge(self, position: Position, walker: Walker) -> float:
        """Score how productive it would be to challenge this position.

        Ideal challenge:
        - Mid-level (position, not axiom or policy)
        - Connected to many other positions
        - Held with moderate confidence
        - Part of imbalanced triads
        """
        score = 0.0

        # Level bonus (positions are best)
        level_scores = {"axiom": 0.3, "position": 1.0, "policy": 0.6}
        score += level_scores.get(position.level, 0.5) * 0.3

        # Connectivity bonus
        edges_from = len(self.graph.edges_from(position.id))
        edges_to = len(self.graph.edges_to(position.id))
        connectivity = min(1.0, (edges_from + edges_to) / 10)
        score += connectivity * 0.3

        # Confidence inversely affects score (high confidence = low challenge value)
        for choice in walker.choices:
            if choice.position_id == position.id:
                score += (1.0 - choice.confidence) * 0.2
                break

        # Tension bonus
        balance = self.get_walker_balance_state(walker)
        all_edges = list(self.graph.edges.values())
        triads = balance.find_imbalanced_triads(all_edges)

        in_imbalanced_triad = any(position.id in [a, b, c] for a, b, c, _ in triads)
        if in_imbalanced_triad:
            score += 0.2

        return min(1.0, score)

    def suggest_challenge(self, walker: Walker, n: int = 3) -> list[tuple[Position, float]]:
        """Suggest positions to challenge, ranked by productive tension score."""
        untested = []
        tested_ids = set(walker.path)

        for pos in self.graph.positions.values():
            if pos.id not in tested_ids:
                untested.append(pos)

        # Score each
        scored = [(pos, self.score_challenge(pos, walker)) for pos in untested]
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored[:n]
