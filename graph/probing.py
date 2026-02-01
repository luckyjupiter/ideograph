"""Adaptive Probing: Find where predictions break to discover orthogonal dimensions.

Key insight from igloominance:
- If 5 responses are predicted by the first, they're redundant
- When prediction fails → orthogonal dimension discovered
- Counterfactual questions reveal causal structure in their mental model
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import math

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.position import Position
from models.walker import Walker, PredictionError


@dataclass
class Prediction:
    """A prediction about a walker's stance on a position."""
    position_id: str
    predicted_acceptance: float  # 0.0 - 1.0 probability they'll accept
    uncertainty: float  # 0.0 (certain) - 1.0 (no idea)
    reasoning: str = ""

    # After testing
    actual_acceptance: Optional[bool] = None
    was_tested: bool = False

    @property
    def was_wrong(self) -> bool:
        if not self.was_tested or self.actual_acceptance is None:
            return False
        predicted_yes = self.predicted_acceptance > 0.5
        return predicted_yes != self.actual_acceptance

    @property
    def error_magnitude(self) -> float:
        """How wrong were we? 0 = correct, 1 = completely wrong"""
        if not self.was_tested or self.actual_acceptance is None:
            return 0.0
        actual = 1.0 if self.actual_acceptance else 0.0
        return abs(self.predicted_acceptance - actual)


@dataclass
class ProbeQuestion:
    """A question to probe a walker's position."""
    position_id: str
    question: str
    prediction: Prediction
    probe_type: str = "direct"  # "direct" | "counterfactual" | "priority"


class AdaptiveProber:
    """Generates probes to discover orthogonal dimensions in a walker's beliefs."""

    def __init__(self, graph):
        self.graph = graph

    def predict_position(self, walker: Walker, position: Position) -> Prediction:
        """Predict whether a walker will accept a position.

        Uses:
        1. Co-occurrence with already-accepted positions
        2. IMPLIES edges from accepted positions
        3. CONTRADICTS edges with accepted positions
        """
        accepted = set(walker.positions_accepted)
        rejected = set(walker.positions_rejected)

        if not accepted and not rejected:
            # No data, maximum uncertainty
            return Prediction(
                position_id=position.id,
                predicted_acceptance=0.5,
                uncertainty=1.0,
                reasoning="No prior data"
            )

        # Check IMPLIES edges: if they accepted A and A→B, predict they accept B
        implies_score = 0.0
        implies_count = 0
        for edge in self.graph.edges_to(position.id):
            if edge.edge_type.value == "implies" and edge.source_id in accepted:
                implies_score += edge.weight
                implies_count += 1

        # Check CONTRADICTS edges: if they accepted A and A⊗B, predict they reject B
        contradicts_score = 0.0
        contradicts_count = 0
        for edge in self.graph.edges.values():
            if edge.edge_type.value != "contradicts":
                continue
            if (edge.source_id == position.id and edge.target_id in accepted) or \
               (edge.target_id == position.id and edge.source_id in accepted):
                contradicts_score += edge.weight
                contradicts_count += 1

        # Check if they already rejected similar positions
        rejected_similar = 0
        for rej_id in rejected:
            if self.graph.get_edge(rej_id, position.id):
                rejected_similar += 1

        # Combine signals
        total_signals = implies_count + contradicts_count + rejected_similar
        if total_signals == 0:
            return Prediction(
                position_id=position.id,
                predicted_acceptance=0.5,
                uncertainty=0.8,
                reasoning="No related positions tested"
            )

        # Implies pushes toward acceptance
        acceptance_push = implies_score / max(implies_count, 1)
        # Contradicts pushes toward rejection
        rejection_push = contradicts_score / max(contradicts_count, 1)

        predicted = 0.5 + (acceptance_push - rejection_push) * 0.4
        predicted = max(0.0, min(1.0, predicted))

        # Uncertainty decreases with more signals
        uncertainty = 1.0 / (1.0 + 0.3 * total_signals)

        reasoning_parts = []
        if implies_count > 0:
            reasoning_parts.append(f"{implies_count} implies edges suggest acceptance")
        if contradicts_count > 0:
            reasoning_parts.append(f"{contradicts_count} contradicts edges suggest rejection")

        return Prediction(
            position_id=position.id,
            predicted_acceptance=predicted,
            uncertainty=uncertainty,
            reasoning="; ".join(reasoning_parts) or "Based on graph structure"
        )

    def get_untested_positions(self, walker: Walker) -> list[Position]:
        """Get positions the walker hasn't been asked about."""
        tested = set(walker.path)
        return [p for p in self.graph.positions.values() if p.id not in tested]

    def find_highest_uncertainty(self, walker: Walker, n: int = 5) -> list[Prediction]:
        """Find positions where we're most uncertain about the walker's stance."""
        untested = self.get_untested_positions(walker)
        predictions = [self.predict_position(walker, p) for p in untested]

        # Sort by uncertainty (highest first)
        predictions.sort(key=lambda p: p.uncertainty, reverse=True)
        return predictions[:n]

    def find_most_informative(self, walker: Walker, n: int = 3) -> list[Prediction]:
        """Find positions that would most reduce our uncertainty.

        These are positions where:
        1. We're somewhat uncertain (not sure yes or no)
        2. They have many edges (testing them updates many predictions)
        """
        untested = self.get_untested_positions(walker)

        scored = []
        for pos in untested:
            pred = self.predict_position(walker, pos)

            # Information value = uncertainty * connectivity
            edges = len(self.graph.edges_from(pos.id)) + len(self.graph.edges_to(pos.id))
            info_value = pred.uncertainty * math.log(1 + edges)

            scored.append((pred, info_value))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored[:n]]

    def generate_probe(self, walker: Walker) -> Optional[ProbeQuestion]:
        """Generate the next probe question for a walker."""
        informative = self.find_most_informative(walker, n=1)
        if not informative:
            return None

        pred = informative[0]
        position = self.graph.get_position(pred.position_id)
        if not position:
            return None

        # Generate question based on their history
        question = self._generate_question(position, walker, pred)

        return ProbeQuestion(
            position_id=position.id,
            question=question,
            prediction=pred,
            probe_type="direct"
        )

    def generate_counterfactual_probe(self, walker: Walker,
                                       scenario: str) -> Optional[ProbeQuestion]:
        """Generate a counterfactual probe.

        Example: "If the US pivoted fully multipolar, would that change your view on X?"
        """
        # Find a position that's connected to their accepted positions
        # but where the connection depends on some assumption

        accepted = walker.positions_accepted
        if not accepted:
            return None

        # Find positions with MEDIATOR or CONFOUNDER edges
        for pos_id in accepted:
            for edge in self.graph.edges_from(pos_id):
                if edge.edge_type.value in ["mediator", "confounder"]:
                    target = self.graph.get_position(edge.target_id)
                    if target and target.id not in walker.path:
                        question = f"Suppose {scenario}. Would that change your view on: {target.claim}?"
                        return ProbeQuestion(
                            position_id=target.id,
                            question=question,
                            prediction=self.predict_position(walker, target),
                            probe_type="counterfactual"
                        )

        return None

    def generate_priority_probe(self, walker: Walker) -> Optional[ProbeQuestion]:
        """Generate a probe about value priorities.

        "When X and Y conflict, which do you prioritize?"
        """
        accepted = walker.positions_accepted
        if len(accepted) < 2:
            return None

        # Find two accepted positions that might conflict
        for i, pos_a_id in enumerate(accepted):
            for pos_b_id in list(accepted)[i+1:]:
                pos_a = self.graph.get_position(pos_a_id)
                pos_b = self.graph.get_position(pos_b_id)

                if not pos_a or not pos_b:
                    continue

                # Check if there's potential tension
                if pos_a.domain == pos_b.domain:
                    continue  # Same domain, less interesting

                question = (
                    f"When these conflict, which do you prioritize?\n"
                    f"A: {pos_a.claim}\n"
                    f"B: {pos_b.claim}"
                )

                return ProbeQuestion(
                    position_id=f"{pos_a.id}_vs_{pos_b.id}",
                    question=question,
                    prediction=Prediction(
                        position_id=f"{pos_a.id}_vs_{pos_b.id}",
                        predicted_acceptance=0.5,
                        uncertainty=0.9,
                        reasoning="Priority probe"
                    ),
                    probe_type="priority"
                )

        return None

    def _generate_question(self, position: Position, walker: Walker,
                           prediction: Prediction) -> str:
        """Generate a natural question about a position."""
        # Use their recent path for context
        if walker.path:
            last_pos = self.graph.get_position(walker.path[-1])
            if last_pos:
                return (
                    f"Given your view on '{last_pos.claim[:50]}...', "
                    f"what do you think about: {position.claim}?"
                )

        return f"What's your take on: {position.claim}?"

    def record_response(self, walker: Walker, probe: ProbeQuestion, accepted: bool):
        """Record the response to a probe and track prediction error."""
        probe.prediction.actual_acceptance = accepted
        probe.prediction.was_tested = True

        if probe.prediction.was_wrong:
            # We found an orthogonal dimension!
            walker.prediction_errors.append(PredictionError(
                position_id=probe.position_id,
                predicted=probe.prediction.predicted_acceptance > 0.5,
                actual=accepted,
                prediction_confidence=1.0 - probe.prediction.uncertainty,
                dimension_hint=self._infer_dimension(walker, probe)
            ))

    def _infer_dimension(self, walker: Walker, probe: ProbeQuestion) -> Optional[str]:
        """Try to infer what hidden dimension caused the prediction error."""
        position = self.graph.get_position(probe.position_id)
        if not position:
            return None

        # Check what they accepted that we thought would predict this
        accepted = set(walker.positions_accepted)

        conflicting_edges = []
        for edge in self.graph.edges_to(position.id):
            if edge.edge_type.value == "implies" and edge.source_id in accepted:
                conflicting_edges.append(edge)

        if conflicting_edges:
            return f"Implied by {len(conflicting_edges)} accepted positions but rejected"

        return f"Unexpected response in {position.domain.value} domain"
