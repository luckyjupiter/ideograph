"""Attractors and Voids: Density patterns in the ideological graph.

ATTRACTOR = Position where many paths converge (common ideological basins)
VOID = Position that SHOULD exist but nobody occupies (structurally possible, socially rare)

Voids are interesting - they represent positions that *should* exist
given the graph structure but are rarely occupied. Why?
- Socially costly to hold
- Requires rare combination of experiences
- Actively suppressed
- Simply not articulated yet
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Attractor:
    """A high-traffic position or cluster.

    Attractors are basins where many ideological paths converge.
    """

    # Center position
    center_id: str
    center_claim: str = ""

    # Basin (positions that flow into this attractor)
    basin_ids: set[str] = field(default_factory=set)

    # Traffic metrics
    visit_count: int = 0
    unique_walkers: int = 0

    # Canonical patterns that pass through here
    patterns: list[str] = field(default_factory=list)

    # Strength
    strength: float = 0.0  # How strong is this attractor?

    # Metadata
    detected_at: datetime = field(default_factory=datetime.now)

    def __repr__(self):
        return f"Attractor({self.center_id}: {self.visit_count} visits, strength={self.strength:.2f})"


@dataclass
class Void:
    """A structurally expected but rarely visited position.

    Voids are interesting because they represent ideological blind spots.
    """

    # The empty position
    position_id: str
    position_claim: str = ""

    # Why we expected visitors
    expected_from: list[str] = field(default_factory=list)  # Edges that point here
    expected_visitors: int = 0  # How many we predicted

    # Actual visitors
    actual_visitors: int = 0

    # Void ratio (how empty relative to expectation)
    void_ratio: float = 0.0  # 0 = as expected, 1 = completely empty

    # Hypotheses for why this is a void
    possible_reasons: list[str] = field(default_factory=list)
    # - "socially_costly": holding this position has social costs
    # - "rare_combination": requires unusual belief combination
    # - "suppressed": actively suppressed in discourse
    # - "unarticulated": simply hasn't been articulated yet

    # Metadata
    detected_at: datetime = field(default_factory=datetime.now)

    def __repr__(self):
        return f"Void({self.position_id}: expected {self.expected_visitors}, got {self.actual_visitors})"


class AttractorDetector:
    """Detects attractors and voids in the ideological graph."""

    def __init__(self, graph):
        self.graph = graph

    def detect_attractors(self, min_visits: int = 10,
                         min_strength: float = 0.3) -> list[Attractor]:
        """Find positions with high visit density."""
        attractors = []

        for pos_id, position in self.graph.positions.items():
            if position.visit_count < min_visits:
                continue

            # Calculate strength based on:
            # 1. Raw visit count
            # 2. Number of incoming edges
            # 3. Weight of incoming edges

            incoming = self.graph.edges_to(pos_id)
            incoming_count = len(incoming)
            incoming_weight = sum(e.weight for e in incoming) if incoming else 0

            # Normalize visit count
            max_visits = max(p.visit_count for p in self.graph.positions.values()) or 1
            visit_score = position.visit_count / max_visits

            # Combine signals
            strength = (
                visit_score * 0.5 +
                min(1.0, incoming_count / 10) * 0.25 +
                min(1.0, incoming_weight / 5) * 0.25
            )

            if strength >= min_strength:
                # Find basin (positions that imply this one)
                basin_ids = set()
                for edge in incoming:
                    basin_ids.add(edge.source_id)

                attractors.append(Attractor(
                    center_id=pos_id,
                    center_claim=position.claim,
                    basin_ids=basin_ids,
                    visit_count=position.visit_count,
                    strength=strength,
                ))

        # Sort by strength
        attractors.sort(key=lambda a: a.strength, reverse=True)
        return attractors

    def detect_voids(self, min_expected: int = 5,
                    min_void_ratio: float = 0.7) -> list[Void]:
        """Find positions that should exist but are rarely visited."""
        voids = []

        for pos_id, position in self.graph.positions.items():
            # Calculate expected visitors based on incoming edges
            incoming = self.graph.edges_to(pos_id)
            if not incoming:
                continue

            # Expected = sum of (source visits * edge weight)
            expected = 0
            expected_from = []
            for edge in incoming:
                source = self.graph.get_position(edge.source_id)
                if source:
                    expected += source.visit_count * edge.weight
                    expected_from.append(edge.source_id)

            if expected < min_expected:
                continue

            actual = position.visit_count
            void_ratio = 1.0 - (actual / expected) if expected > 0 else 0

            if void_ratio >= min_void_ratio:
                # Generate hypotheses
                reasons = self._hypothesize_void_reasons(position, incoming)

                voids.append(Void(
                    position_id=pos_id,
                    position_claim=position.claim,
                    expected_from=expected_from,
                    expected_visitors=int(expected),
                    actual_visitors=actual,
                    void_ratio=void_ratio,
                    possible_reasons=reasons,
                ))

        # Sort by void ratio
        voids.sort(key=lambda v: v.void_ratio, reverse=True)
        return voids

    def _hypothesize_void_reasons(self, position, incoming_edges) -> list[str]:
        """Generate hypotheses for why a position is a void."""
        reasons = []

        # Check for contradicting popular positions
        contradictions = self.graph.contradicts(position.id)
        high_traffic_contradictions = [
            p for p in contradictions
            if p.visit_count > 10
        ]
        if high_traffic_contradictions:
            reasons.append("socially_costly")

        # Check if it requires positions from different clusters
        source_domains = set()
        for edge in incoming_edges:
            source = self.graph.get_position(edge.source_id)
            if source:
                source_domains.add(source.domain.value)
        if len(source_domains) >= 3:
            reasons.append("rare_combination")

        # Check if position has low canonical score
        if position.canonical_score < 0.3:
            reasons.append("unarticulated")

        # Default
        if not reasons:
            reasons.append("unknown")

        return reasons

    def find_basin_for_walker(self, walker) -> Optional[Attractor]:
        """Find which attractor basin a walker is in."""
        accepted = set(walker.positions_accepted)

        # Find attractor with most overlap with accepted positions
        attractors = self.detect_attractors()

        best_attractor = None
        best_overlap = 0

        for attractor in attractors:
            # Check if walker is in this basin
            overlap = len(accepted & attractor.basin_ids)
            if attractor.center_id in accepted:
                overlap += 2  # Bonus for being at the center

            if overlap > best_overlap:
                best_overlap = overlap
                best_attractor = attractor

        return best_attractor

    def suggest_void_exploration(self, walker, n: int = 3) -> list[Void]:
        """Suggest voids that might be interesting for a walker to explore.

        This is part of the Ideological Randonautica function.
        """
        voids = self.detect_voids()

        # Filter to voids that are:
        # 1. Not already visited by this walker
        # 2. Connected to positions they've accepted

        accepted = set(walker.positions_accepted)
        visited = set(walker.path)

        candidates = []
        for void in voids:
            if void.position_id in visited:
                continue

            # Check connection to accepted positions
            connection_score = len(set(void.expected_from) & accepted)
            if connection_score > 0:
                candidates.append((void, connection_score))

        # Sort by connection score (most connected first)
        candidates.sort(key=lambda x: x[1], reverse=True)

        return [c[0] for c in candidates[:n]]
