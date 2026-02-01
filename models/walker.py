"""Walker: An entity traversing the ideological graph.

Key insight: Map trajectories, not just coordinates.
"The motion matters more than the position."

A lib-to-trad pipeline looks different from leftist-to-postleft
even if they land in similar places.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum

from models.aberration import Aberration, AberrationProfile


class TrajectoryPhase(Enum):
    """Phases of ideological motion."""
    EARLY = "early"  # Just starting to move
    TRANSITIONING = "transitioning"  # Actively shifting
    SETTLED = "settled"  # Reached stable position
    OSCILLATING = "oscillating"  # Moving back and forth


@dataclass
class Choice:
    """A decision point in the walk."""

    # What was presented
    position_id: str
    question: str = ""

    # What they chose
    accepted: bool = False  # Did they accept this position?
    confidence: float = 0.5  # How confident were they? 0=unsure, 1=certain
    reasoning: Optional[str] = None  # Why they chose this (if stated)

    # Prediction tracking
    was_predicted: bool = False  # Did we predict this choice?
    prediction_confidence: float = 0.0  # How confident was our prediction?

    # Timing
    timestamp: datetime = field(default_factory=datetime.now)
    response_time_ms: Optional[int] = None  # How long they took to decide

    @property
    def was_surprising(self) -> bool:
        """Was this choice surprising (prediction error)?"""
        return self.was_predicted and self.prediction_confidence > 0.7 and not self.accepted

    def __repr__(self):
        status = "+" if self.accepted else "-"
        return f"Choice({status}{self.position_id}, conf={self.confidence:.2f})"


@dataclass
class Trajectory:
    """The direction of ideological motion.

    "Map the conversions, not the coordinates."
    """

    # Named pipeline (learned from data)
    pipeline: str = "unknown"  # "lib_to_trad" | "leftist_to_postleft" | etc.

    # Current phase
    phase: TrajectoryPhase = TrajectoryPhase.EARLY

    # Origin and destination clusters
    origin_cluster: Optional[str] = None
    current_cluster: Optional[str] = None
    predicted_destination: Optional[str] = None

    # Motion vector in concept-space
    momentum: dict[str, float] = field(default_factory=dict)
    # Example: {"economics": -0.3, "social": +0.5} = moving left on econ, right on social

    # Velocity (rate of change)
    velocity: float = 0.0  # How fast they're moving through idea-space

    # Historical positions
    cluster_history: list[tuple[str, datetime]] = field(default_factory=list)

    def update_momentum(self, domain: str, direction: float):
        """Update momentum in a domain."""
        current = self.momentum.get(domain, 0.0)
        # Exponential moving average
        self.momentum[domain] = current * 0.7 + direction * 0.3

    def record_cluster(self, cluster: str):
        """Record entering a new cluster."""
        now = datetime.now()
        if not self.cluster_history or self.cluster_history[-1][0] != cluster:
            self.cluster_history.append((cluster, now))
            self.current_cluster = cluster

            # Update velocity based on cluster changes
            if len(self.cluster_history) >= 2:
                prev_time = self.cluster_history[-2][1]
                time_delta = (now - prev_time).total_seconds() / 3600  # hours
                self.velocity = 1.0 / max(time_delta, 0.1)  # inversely proportional to time

    @property
    def summary(self) -> str:
        """Human-readable trajectory summary."""
        origin = self.origin_cluster or "?"
        current = self.current_cluster or "?"
        dest = self.predicted_destination or "?"
        return f"{origin} → {current} → {dest} ({self.phase.value}, v={self.velocity:.2f})"

    def __repr__(self):
        return f"Trajectory({self.summary})"


@dataclass
class PredictionError:
    """A place where our model was wrong about this walker."""

    position_id: str
    predicted: bool  # What we predicted
    actual: bool  # What they actually chose
    prediction_confidence: float
    dimension_hint: Optional[str] = None  # What hidden dimension might explain this?

    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def severity(self) -> float:
        """How bad was this error? Worse if we were confident."""
        return self.prediction_confidence * (1.0 if self.predicted != self.actual else 0.0)


@dataclass
class Walker:
    """An entity traversing the ideological graph.

    Tracks their path, trajectory, aberrations, and how they
    update the global graph.
    """

    # Identity
    user_id: str
    session_id: str = ""

    # The walk (current state)
    path: list[str] = field(default_factory=list)  # Position IDs visited
    choices: list[Choice] = field(default_factory=list)  # Decision points

    # Trajectory (where they came from, where they're going)
    trajectory: Trajectory = field(default_factory=Trajectory)

    # Derived classification
    canonical_fit: Optional[str] = None  # Best-fit archetype
    canonical_fit_score: float = 0.0  # How well they fit (0=poor, 1=perfect)

    # Aberrations (what makes them unique)
    aberration_profile: AberrationProfile = None

    # Prediction tracking
    prediction_errors: list[PredictionError] = field(default_factory=list)

    # Graph contribution
    edges_strengthened: list[str] = field(default_factory=list)
    edges_weakened: list[str] = field(default_factory=list)

    # Session metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.session_id:
            self.session_id = f"{self.user_id}_{int(self.created_at.timestamp())}"
        if self.aberration_profile is None:
            self.aberration_profile = AberrationProfile(walker_id=self.user_id)

    def visit(self, position_id: str):
        """Visit a position."""
        if position_id not in self.path:
            self.path.append(position_id)
            self.updated_at = datetime.now()

    def record_choice(self, choice: Choice):
        """Record a choice made at a decision point."""
        self.choices.append(choice)

        # Check for prediction error
        if choice.was_surprising:
            self.prediction_errors.append(PredictionError(
                position_id=choice.position_id,
                predicted=True,
                actual=choice.accepted,
                prediction_confidence=choice.prediction_confidence
            ))

        self.updated_at = datetime.now()

    def add_aberration(self, aberration: Aberration):
        """Add a detected aberration."""
        self.aberration_profile.add(aberration)
        self.updated_at = datetime.now()

    def strengthen_edge(self, edge_id: str):
        """Record that this walk strengthened an edge."""
        if edge_id not in self.edges_strengthened:
            self.edges_strengthened.append(edge_id)

    def weaken_edge(self, edge_id: str):
        """Record that this walk weakened an edge."""
        if edge_id not in self.edges_weakened:
            self.edges_weakened.append(edge_id)

    @property
    def positions_accepted(self) -> list[str]:
        """Positions this walker accepted."""
        return [c.position_id for c in self.choices if c.accepted]

    @property
    def positions_rejected(self) -> list[str]:
        """Positions this walker rejected."""
        return [c.position_id for c in self.choices if not c.accepted]

    @property
    def surprise_rate(self) -> float:
        """What fraction of choices were surprising?"""
        if not self.choices:
            return 0.0
        surprising = sum(1 for c in self.choices if c.was_surprising)
        return surprising / len(self.choices)

    @property
    def summary(self) -> str:
        """Human-readable walker summary."""
        lines = [
            f"Walker: {self.user_id}",
            f"Path length: {len(self.path)}",
            f"Choices: {len(self.choices)} ({len(self.positions_accepted)} accepted)",
            f"Trajectory: {self.trajectory.summary}",
            f"Canonical fit: {self.canonical_fit or 'unknown'} ({self.canonical_fit_score:.2f})",
            f"Aberrations: {len(self.aberration_profile.aberrations)}",
            f"Prediction errors: {len(self.prediction_errors)} ({self.surprise_rate:.1%} surprise rate)",
        ]
        return "\n".join(lines)

    def __repr__(self):
        return f"Walker({self.user_id}: {len(self.path)} positions, {len(self.aberration_profile.aberrations)} aberrations)"
