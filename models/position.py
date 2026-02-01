"""Position: A node in the ideological graph.

Each position represents a discrete ideological stance that can be
held, rejected, or be neutral on.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime
import hashlib


class Domain(Enum):
    """Ideological domains - emergent clusters, not predefined."""
    ECONOMICS = "economics"
    CIVIL_LIBERTIES = "civil_liberties"
    FOREIGN_POLICY = "foreign_policy"
    SOCIAL = "social"
    EPISTEMOLOGY = "epistemology"
    GOVERNANCE = "governance"
    TECHNOLOGY = "technology"
    ENVIRONMENT = "environment"
    IDENTITY = "identity"
    METAPHYSICS = "metaphysics"
    UNCATEGORIZED = "uncategorized"


@dataclass
class Source:
    """Evidence source for a position."""
    url: Optional[str] = None
    text: str = ""
    source_type: str = "unknown"  # headline, forum, study, conversation
    timestamp: Optional[datetime] = None
    credibility: float = 0.5  # 0.0 - 1.0

    def __hash__(self):
        return hash((self.url, self.text[:100]))


@dataclass
class Position:
    """A node in the ideological graph.

    Represents a discrete ideological stance. Can be a concrete claim
    ("The 2nd Amendment is absolute") or an abstract axiom
    ("Hierarchy is natural").
    """

    # Identity
    id: str = ""
    claim: str = ""  # The actual assertion

    # Classification
    domain: Domain = Domain.UNCATEGORIZED
    valence: Optional[float] = None  # -1.0 (left) to +1.0 (right), None if orthogonal

    # Hierarchy level
    level: str = "position"  # "axiom" | "position" | "policy"

    # Evidence
    sources: list[Source] = field(default_factory=list)

    # Graph metrics (updated by walks)
    visit_count: int = 0
    canonical_score: float = 0.5  # How "expected" given neighbors

    # Thinkers/traditions this derives from
    traditions: list[str] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Generate ID if not provided."""
        if not self.id and self.claim:
            # Create deterministic ID from claim
            self.id = self._generate_id(self.claim)

    @staticmethod
    def _generate_id(claim: str) -> str:
        """Generate a short deterministic ID from the claim."""
        # Normalize and hash
        normalized = claim.lower().strip()
        hash_bytes = hashlib.sha256(normalized.encode()).hexdigest()[:12]
        # Create readable prefix from first words
        words = normalized.split()[:3]
        prefix = "_".join(w[:4] for w in words if w.isalnum() or w[0].isalnum())[:20]
        return f"{prefix}_{hash_bytes}"

    def add_source(self, source: Source):
        """Add evidence source."""
        if source not in self.sources:
            self.sources.append(source)
            self.updated_at = datetime.now()

    def record_visit(self):
        """Record that a walker visited this position."""
        self.visit_count += 1
        self.updated_at = datetime.now()

    def update_canonical_score(self, score: float):
        """Update how 'expected' this position is."""
        self.canonical_score = max(0.0, min(1.0, score))
        self.updated_at = datetime.now()

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.id == other.id
        return False

    def __repr__(self):
        return f"Position({self.id}: {self.claim[:50]}...)"


# Common position templates
def axiom(claim: str, domain: Domain = Domain.UNCATEGORIZED, **kwargs) -> Position:
    """Create an axiom-level position (foundational belief)."""
    return Position(claim=claim, domain=domain, level="axiom", **kwargs)


def position(claim: str, domain: Domain = Domain.UNCATEGORIZED, **kwargs) -> Position:
    """Create a position-level stance (concrete belief)."""
    return Position(claim=claim, domain=domain, level="position", **kwargs)


def policy(claim: str, domain: Domain = Domain.UNCATEGORIZED, **kwargs) -> Position:
    """Create a policy-level stance (specific policy preference)."""
    return Position(claim=claim, domain=domain, level="policy", **kwargs)
