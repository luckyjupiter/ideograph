"""Edge: Relationships between positions in the ideological graph.

Key insight from igloominance: PRIORITIZES_OVER is the most important edge type.
When two values clash, which wins? That ranking IS the ideology.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class EdgeType(Enum):
    """Types of relationships between positions.

    Causal structure matters - these aren't just associations.
    """

    # Basic relationships
    IMPLIES = "implies"
    # A → B: If you hold A, you typically hold B
    # Learned from co-occurrence across population

    CONTRADICTS = "contradicts"
    # A ⊗ B: Tension between positions
    # Rarely co-occur in same person

    DERIVES_FROM = "derives_from"
    # P → T: Position traces to a thinker/tradition
    # "Anti-globalism" derives from Dugin

    # THE KEY EDGE TYPE
    PRIORITIZES_OVER = "prioritizes_over"
    # A > B: When two values conflict, which wins
    # This ranking IS the ideology, more than positions themselves
    # Example: Freedom > Security = Libertarian
    #          Security > Freedom = Authoritarian

    # Causal structures (from DAG theory)
    COLLIDER = "collider"
    # A → X ← B: Two incompatible paths arrive at same position
    # Example: Libertarians AND ACLU liberals both reach "free speech absolutist"

    CONFOUNDER = "confounder"
    # X ← C → Y: Hidden variable drives both positions
    # Example: Class position secretly driving both "anti-woke" AND "pro-union"

    MEDIATOR = "mediator"
    # A → M → B: Gateway node between positions
    # Example: "Red pill" mediates mainstream conservatism → fringe right

    FORK = "fork"
    # A ← X → B: Single cause creating divergent branches
    # Example: 2008 crash forked into both Tea Party AND Occupy

    # Weak relationship
    ASSOCIATION = "association"
    # A — B: Co-occurrence without clear causal structure


@dataclass
class Edge:
    """A directed edge between two positions.

    Edges carry weight (strength), type (causal structure),
    and evidence (how we know this relationship exists).
    """

    # Connected positions
    source_id: str
    target_id: str

    # Relationship type
    edge_type: EdgeType = EdgeType.ASSOCIATION

    # Strength and evidence
    weight: float = 0.5  # 0.0 - 1.0, strength of connection
    evidence_count: int = 0  # Number of sources supporting this edge
    confidence: float = 0.5  # How sure we are about this edge

    # Dynamics (updated by walks)
    co_occurrence: int = 0  # How often these appear together
    tension: float = 0.0  # How often these conflict (for contradicts/collider)

    # For PRIORITIZES_OVER edges
    priority_context: Optional[str] = None  # When does this priority apply?

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    sources: list[str] = field(default_factory=list)  # URLs or references

    @property
    def id(self) -> str:
        """Unique edge identifier."""
        return f"{self.source_id}->{self.target_id}:{self.edge_type.value}"

    def strengthen(self, amount: float = 0.1):
        """Strengthen this edge (from co-occurrence or explicit evidence)."""
        self.weight = min(1.0, self.weight + amount * (1 - self.weight))
        self.co_occurrence += 1
        self.updated_at = datetime.now()

    def weaken(self, amount: float = 0.1):
        """Weaken this edge (from contradiction or disconfirmation)."""
        self.weight = max(0.0, self.weight - amount * self.weight)
        self.updated_at = datetime.now()

    def add_evidence(self, source: str):
        """Add evidence source for this edge."""
        if source not in self.sources:
            self.sources.append(source)
            self.evidence_count = len(self.sources)
            self.confidence = min(1.0, 0.3 + 0.1 * self.evidence_count)
            self.updated_at = datetime.now()

    def record_tension(self):
        """Record that these positions were in tension."""
        self.tension += 1
        self.updated_at = datetime.now()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Edge):
            return self.id == other.id
        return False

    def __repr__(self):
        return f"Edge({self.source_id} -{self.edge_type.value}-> {self.target_id}, w={self.weight:.2f})"


# Edge factory functions
def implies(source_id: str, target_id: str, weight: float = 0.5, **kwargs) -> Edge:
    """Create an IMPLIES edge: A typically leads to B."""
    return Edge(source_id=source_id, target_id=target_id,
                edge_type=EdgeType.IMPLIES, weight=weight, **kwargs)


def contradicts(source_id: str, target_id: str, weight: float = 0.5, **kwargs) -> Edge:
    """Create a CONTRADICTS edge: A and B rarely coexist."""
    return Edge(source_id=source_id, target_id=target_id,
                edge_type=EdgeType.CONTRADICTS, weight=weight, **kwargs)


def prioritizes(source_id: str, target_id: str, context: str = None, **kwargs) -> Edge:
    """Create a PRIORITIZES_OVER edge: When A and B clash, A wins."""
    return Edge(source_id=source_id, target_id=target_id,
                edge_type=EdgeType.PRIORITIZES_OVER,
                priority_context=context, **kwargs)


def derives_from(position_id: str, tradition: str, **kwargs) -> Edge:
    """Create a DERIVES_FROM edge: Position traces to tradition."""
    return Edge(source_id=position_id, target_id=tradition,
                edge_type=EdgeType.DERIVES_FROM, **kwargs)


def collider(path_a: str, path_b: str, destination: str, **kwargs) -> tuple[Edge, Edge]:
    """Create COLLIDER edges: Two paths arrive at same destination."""
    edge_a = Edge(source_id=path_a, target_id=destination,
                  edge_type=EdgeType.COLLIDER, **kwargs)
    edge_b = Edge(source_id=path_b, target_id=destination,
                  edge_type=EdgeType.COLLIDER, **kwargs)
    return edge_a, edge_b


def mediator(start: str, gateway: str, end: str, **kwargs) -> tuple[Edge, Edge]:
    """Create MEDIATOR edges: Gateway node between positions."""
    edge_a = Edge(source_id=start, target_id=gateway,
                  edge_type=EdgeType.MEDIATOR, **kwargs)
    edge_b = Edge(source_id=gateway, target_id=end,
                  edge_type=EdgeType.MEDIATOR, **kwargs)
    return edge_a, edge_b
