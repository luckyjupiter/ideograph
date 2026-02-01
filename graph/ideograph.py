"""IdeologicalGraph: The main graph structure.

An ideological tree mined from headlines, forums, studies.
Starts fully connected, then eroded/weighted by evidence.
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Iterator, Callable
from datetime import datetime
import random

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.position import Position, Domain
from models.edge import Edge, EdgeType
from models.walker import Walker
from models.aberration import Aberration, AberrationType


@dataclass
class IdeologicalGraph:
    """The main ideological graph.

    Nodes are Positions, edges are typed relationships.
    Walkers traverse the graph and update weights.
    """

    # Core data
    positions: dict[str, Position] = field(default_factory=dict)
    edges: dict[str, Edge] = field(default_factory=dict)

    # Walkers (active and historical)
    walkers: dict[str, Walker] = field(default_factory=dict)

    # Graph metadata
    name: str = "ideograph"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Configuration
    learning_rate: float = 0.1  # How fast edges update from walks
    decay_rate: float = 0.05  # How fast unused edges decay

    # ═══════════════════════════════════════════════════════════
    # POSITION OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def add_position(self, position: Position) -> Position:
        """Add a position to the graph."""
        if position.id in self.positions:
            # Merge with existing
            existing = self.positions[position.id]
            for source in position.sources:
                existing.add_source(source)
            return existing

        self.positions[position.id] = position
        self.updated_at = datetime.now()
        return position

    def get_position(self, position_id: str) -> Optional[Position]:
        """Get a position by ID."""
        return self.positions.get(position_id)

    def find_positions(self, query: str, limit: int = 10) -> list[Position]:
        """Find positions matching a query (simple text search)."""
        query_lower = query.lower()
        matches = []
        for pos in self.positions.values():
            if query_lower in pos.claim.lower():
                matches.append(pos)
                if len(matches) >= limit:
                    break
        return matches

    def positions_by_domain(self, domain: str) -> list[Position]:
        """Get all positions in a domain."""
        return [p for p in self.positions.values() if p.domain.value == domain]

    # ═══════════════════════════════════════════════════════════
    # EDGE OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def add_edge(self, edge: Edge) -> Edge:
        """Add an edge to the graph."""
        if edge.id in self.edges:
            # Strengthen existing edge
            existing = self.edges[edge.id]
            existing.strengthen(self.learning_rate)
            return existing

        self.edges[edge.id] = edge
        self.updated_at = datetime.now()
        return edge

    def connect(self, source_id: str, target_id: str,
                edge_type: EdgeType = EdgeType.IMPLIES,
                weight: float = 0.5, **kwargs) -> Edge:
        """Connect two positions with an edge."""
        edge = Edge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            weight=weight,
            **kwargs
        )
        return self.add_edge(edge)

    def get_edge(self, source_id: str, target_id: str,
                 edge_type: Optional[EdgeType] = None) -> Optional[Edge]:
        """Get an edge between two positions."""
        if edge_type:
            edge_id = f"{source_id}->{target_id}:{edge_type.value}"
            return self.edges.get(edge_id)

        # Find any edge between these positions
        for edge in self.edges.values():
            if edge.source_id == source_id and edge.target_id == target_id:
                return edge
        return None

    def edges_from(self, position_id: str) -> list[Edge]:
        """Get all edges originating from a position."""
        return [e for e in self.edges.values() if e.source_id == position_id]

    def edges_to(self, position_id: str) -> list[Edge]:
        """Get all edges pointing to a position."""
        return [e for e in self.edges.values() if e.target_id == position_id]

    def neighbors(self, position_id: str) -> list[Position]:
        """Get neighboring positions (via any edge)."""
        neighbor_ids = set()
        for edge in self.edges_from(position_id):
            neighbor_ids.add(edge.target_id)
        for edge in self.edges_to(position_id):
            neighbor_ids.add(edge.source_id)
        return [self.positions[pid] for pid in neighbor_ids if pid in self.positions]

    def implied_by(self, position_id: str) -> list[Position]:
        """Get positions that imply this one."""
        return [
            self.positions[e.source_id]
            for e in self.edges_to(position_id)
            if e.edge_type == EdgeType.IMPLIES and e.source_id in self.positions
        ]

    def implies(self, position_id: str) -> list[Position]:
        """Get positions implied by this one."""
        return [
            self.positions[e.target_id]
            for e in self.edges_from(position_id)
            if e.edge_type == EdgeType.IMPLIES and e.target_id in self.positions
        ]

    def contradicts(self, position_id: str) -> list[Position]:
        """Get positions that contradict this one."""
        result = []
        for edge in self.edges.values():
            if edge.edge_type != EdgeType.CONTRADICTS:
                continue
            if edge.source_id == position_id and edge.target_id in self.positions:
                result.append(self.positions[edge.target_id])
            elif edge.target_id == position_id and edge.source_id in self.positions:
                result.append(self.positions[edge.source_id])
        return result

    # ═══════════════════════════════════════════════════════════
    # WALKER OPERATIONS
    # ═══════════════════════════════════════════════════════════

    def create_walker(self, user_id: str) -> Walker:
        """Create a new walker."""
        walker = Walker(user_id=user_id)
        self.walkers[walker.session_id] = walker
        return walker

    def get_walker(self, session_id: str) -> Optional[Walker]:
        """Get a walker by session ID."""
        return self.walkers.get(session_id)

    def walkers_for_user(self, user_id: str) -> list[Walker]:
        """Get all walkers for a user."""
        return [w for w in self.walkers.values() if w.user_id == user_id]

    # ═══════════════════════════════════════════════════════════
    # WALKING THE GRAPH
    # ═══════════════════════════════════════════════════════════

    def walk_step(self, walker: Walker, position_id: str, accepted: bool,
                  confidence: float = 0.5, reasoning: str = None) -> list[Position]:
        """Take a step in the walk.

        Returns: suggested next positions to consider
        """
        from models.walker import Choice

        position = self.get_position(position_id)
        if not position:
            return []

        # Record the visit
        walker.visit(position_id)
        position.record_visit()

        # Record the choice
        choice = Choice(
            position_id=position_id,
            accepted=accepted,
            confidence=confidence,
            reasoning=reasoning,
        )
        walker.record_choice(choice)

        # Update edges based on this choice
        self._update_edges_from_choice(walker, choice)

        # Get next positions to consider
        if accepted:
            # Follow implications
            next_positions = self.implies(position_id)
        else:
            # Look at contradictions or alternatives
            next_positions = self.contradicts(position_id)

        # Add some exploration (positions not yet visited)
        for neighbor in self.neighbors(position_id):
            if neighbor.id not in walker.path and neighbor not in next_positions:
                next_positions.append(neighbor)

        return next_positions[:5]  # Limit suggestions

    def _update_edges_from_choice(self, walker: Walker, choice):
        """Update edge weights based on a choice."""
        if len(walker.path) < 2:
            return

        prev_position_id = walker.path[-2]
        current_position_id = choice.position_id

        # Get or create edge between previous and current
        edge = self.get_edge(prev_position_id, current_position_id)

        if choice.accepted:
            if edge:
                edge.strengthen(self.learning_rate)
                walker.strengthen_edge(edge.id)
            else:
                # Create new edge from co-occurrence
                new_edge = self.connect(
                    prev_position_id, current_position_id,
                    EdgeType.IMPLIES, weight=0.3
                )
                walker.strengthen_edge(new_edge.id)
        else:
            if edge and edge.edge_type == EdgeType.IMPLIES:
                # Weaken implication that didn't hold
                edge.weaken(self.learning_rate)
                walker.weaken_edge(edge.id)

    def suggest_outside_basin(self, walker: Walker, n: int = 3) -> list[Position]:
        """Suggest positions outside the walker's current basin.

        This is the Ideological Randonautica function.
        """
        visited = set(walker.path)
        accepted = set(walker.positions_accepted)

        # Find positions that are:
        # 1. Not visited
        # 2. Not implied by accepted positions
        # 3. Not contradicting core positions

        implied_by_accepted = set()
        for pos_id in accepted:
            for p in self.implies(pos_id):
                implied_by_accepted.add(p.id)

        candidates = []
        for pos in self.positions.values():
            if pos.id in visited:
                continue
            if pos.id in implied_by_accepted:
                continue
            # Score by how "far" from current basin
            basin_distance = self._estimate_basin_distance(pos, accepted)
            candidates.append((pos, basin_distance))

        # Sort by distance (furthest first) but not contradicting
        candidates.sort(key=lambda x: x[1], reverse=True)

        return [c[0] for c in candidates[:n]]

    def _estimate_basin_distance(self, position: Position,
                                  accepted: set[str]) -> float:
        """Estimate how far a position is from accepted positions."""
        if not accepted:
            return 0.5

        # Simple heuristic: fewer edges to accepted = more distant
        connections = 0
        for pos_id in accepted:
            if self.get_edge(pos_id, position.id):
                connections += 1
            if self.get_edge(position.id, pos_id):
                connections += 1

        # Inverse: more connections = closer = lower score
        max_connections = len(accepted) * 2
        return 1.0 - (connections / max_connections) if max_connections > 0 else 0.5

    # ═══════════════════════════════════════════════════════════
    # PERSISTENCE
    # ═══════════════════════════════════════════════════════════

    def save(self, path: Path):
        """Save the graph to disk."""
        data = {
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": datetime.now().isoformat(),
            "positions": {
                pid: {
                    "id": p.id,
                    "claim": p.claim,
                    "domain": p.domain.value,
                    "valence": p.valence,
                    "level": p.level,
                    "visit_count": p.visit_count,
                    "canonical_score": p.canonical_score,
                    "traditions": p.traditions,
                }
                for pid, p in self.positions.items()
            },
            "edges": {
                eid: {
                    "source_id": e.source_id,
                    "target_id": e.target_id,
                    "edge_type": e.edge_type.value,
                    "weight": e.weight,
                    "evidence_count": e.evidence_count,
                    "confidence": e.confidence,
                    "co_occurrence": e.co_occurrence,
                    "tension": e.tension,
                }
                for eid, e in self.edges.items()
            },
        }

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> "IdeologicalGraph":
        """Load a graph from disk."""
        from models.position import Domain

        path = Path(path)
        if not path.exists():
            return cls()

        data = json.loads(path.read_text())

        graph = cls(
            name=data.get("name", "ideograph"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
        )

        # Load positions
        for pid, pdata in data.get("positions", {}).items():
            pos = Position(
                id=pdata["id"],
                claim=pdata["claim"],
                domain=Domain(pdata.get("domain", "uncategorized")),
                valence=pdata.get("valence"),
                level=pdata.get("level", "position"),
                visit_count=pdata.get("visit_count", 0),
                canonical_score=pdata.get("canonical_score", 0.5),
                traditions=pdata.get("traditions", []),
            )
            graph.positions[pid] = pos

        # Load edges
        for eid, edata in data.get("edges", {}).items():
            edge = Edge(
                source_id=edata["source_id"],
                target_id=edata["target_id"],
                edge_type=EdgeType(edata.get("edge_type", "association")),
                weight=edata.get("weight", 0.5),
                evidence_count=edata.get("evidence_count", 0),
                confidence=edata.get("confidence", 0.5),
                co_occurrence=edata.get("co_occurrence", 0),
                tension=edata.get("tension", 0.0),
            )
            graph.edges[eid] = edge

        return graph

    # ═══════════════════════════════════════════════════════════
    # STATS
    # ═══════════════════════════════════════════════════════════

    @property
    def stats(self) -> dict:
        """Get graph statistics."""
        return {
            "positions": len(self.positions),
            "edges": len(self.edges),
            "walkers": len(self.walkers),
            "total_visits": sum(p.visit_count for p in self.positions.values()),
            "avg_edge_weight": (
                sum(e.weight for e in self.edges.values()) / len(self.edges)
                if self.edges else 0
            ),
            "edge_types": {
                et.value: sum(1 for e in self.edges.values() if e.edge_type == et)
                for et in EdgeType
            },
        }

    def __repr__(self):
        return f"IdeologicalGraph({self.name}: {len(self.positions)} positions, {len(self.edges)} edges)"
