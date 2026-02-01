"""Aberration: The deviations that define you.

Like chromosomal aberrations characterized by type and region,
ideological aberrations are what make someone unique - the places
where they deviate from canonical patterns.

Most people follow predictable paths. What defines you = where you DEVIATE.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import datetime


class AberrationType(Enum):
    """Types of ideological aberrations (like chromosomal mutations)."""

    DELETION = "deletion"
    # Missing expected position
    # "Fiscally conservative but no opinion on immigration"
    # Expected node in the path is absent

    INSERTION = "insertion"
    # Unexpected position present
    # "Marxist who loves Bitcoin"
    # Node present that shouldn't be in this path

    TRANSLOCATION = "translocation"
    # Position in wrong cluster
    # "Uses leftist framing for rightist conclusions"
    # Node exists but in unexpected region of graph

    INVERSION = "inversion"
    # Flipped valence on expected edge
    # "Pro-gun leftist"
    # Edge direction or sign is reversed from expectation


@dataclass
class Aberration:
    """A deviation from canonical ideological patterns.

    Aberrations are not bugs - they're the defining features.
    Most of what someone believes is predictable from their cluster.
    The aberrations are what make them them.
    """

    # Classification
    aberration_type: AberrationType
    region: str  # Which domain/subgraph this affects

    # Details
    description: str = ""
    expected: Optional[str] = None  # What we expected
    actual: Optional[str] = None  # What we found

    # Position references
    position_id: Optional[str] = None  # The position involved
    expected_edge_id: Optional[str] = None  # The edge we expected
    actual_edge_id: Optional[str] = None  # The edge we found (or didn't)

    # Significance
    rarity: float = 0.5  # How rare is this aberration? 0=common, 1=unique
    impact: float = 0.5  # How much does this change predictions? 0=minor, 1=major

    # For detecting patterns across users
    canonical_pattern: Optional[str] = None  # Which pattern this deviates from
    co_aberrations: list[str] = field(default_factory=list)  # Often appears with these

    # Metadata
    detected_at: datetime = field(default_factory=datetime.now)
    walker_id: Optional[str] = None

    @property
    def id(self) -> str:
        """Unique aberration identifier."""
        return f"{self.aberration_type.value}:{self.region}:{self.position_id or 'none'}"

    @property
    def signature(self) -> str:
        """Human-readable signature of this aberration."""
        type_symbol = {
            AberrationType.DELETION: "[-]",
            AberrationType.INSERTION: "[+]",
            AberrationType.TRANSLOCATION: "[~]",
            AberrationType.INVERSION: "[!]",
        }[self.aberration_type]
        return f"{type_symbol} {self.region}: {self.description[:50]}"

    def __repr__(self):
        return f"Aberration({self.signature})"


# Factory functions for common aberrations
def deletion(region: str, expected: str, description: str = "", **kwargs) -> Aberration:
    """Create a DELETION aberration: Missing expected position."""
    return Aberration(
        aberration_type=AberrationType.DELETION,
        region=region,
        expected=expected,
        description=description or f"Missing expected: {expected}",
        **kwargs
    )


def insertion(region: str, actual: str, description: str = "", **kwargs) -> Aberration:
    """Create an INSERTION aberration: Unexpected position present."""
    return Aberration(
        aberration_type=AberrationType.INSERTION,
        region=region,
        actual=actual,
        description=description or f"Unexpected: {actual}",
        **kwargs
    )


def translocation(region: str, position: str, expected_region: str,
                  description: str = "", **kwargs) -> Aberration:
    """Create a TRANSLOCATION aberration: Position in wrong cluster."""
    return Aberration(
        aberration_type=AberrationType.TRANSLOCATION,
        region=region,
        position_id=position,
        expected=expected_region,
        actual=region,
        description=description or f"{position} found in {region}, expected in {expected_region}",
        **kwargs
    )


def inversion(region: str, edge_id: str, description: str = "", **kwargs) -> Aberration:
    """Create an INVERSION aberration: Flipped edge direction/valence."""
    return Aberration(
        aberration_type=AberrationType.INVERSION,
        region=region,
        expected_edge_id=edge_id,
        description=description or f"Inverted edge: {edge_id}",
        **kwargs
    )


@dataclass
class AberrationProfile:
    """Collection of aberrations that define an individual."""

    walker_id: str
    aberrations: list[Aberration] = field(default_factory=list)

    # Derived metrics
    uniqueness_score: float = 0.0  # How aberrant overall
    primary_region: Optional[str] = None  # Where most aberrations cluster
    dominant_type: Optional[AberrationType] = None  # Most common aberration type

    def add(self, aberration: Aberration):
        """Add an aberration to the profile."""
        aberration.walker_id = self.walker_id
        self.aberrations.append(aberration)
        self._update_metrics()

    def _update_metrics(self):
        """Recalculate derived metrics."""
        if not self.aberrations:
            return

        # Uniqueness = average rarity * count factor
        avg_rarity = sum(a.rarity for a in self.aberrations) / len(self.aberrations)
        count_factor = min(1.0, len(self.aberrations) / 10)
        self.uniqueness_score = avg_rarity * (0.5 + 0.5 * count_factor)

        # Primary region
        regions = [a.region for a in self.aberrations]
        self.primary_region = max(set(regions), key=regions.count)

        # Dominant type
        types = [a.aberration_type for a in self.aberrations]
        self.dominant_type = max(set(types), key=types.count)

    def by_type(self, aberration_type: AberrationType) -> list[Aberration]:
        """Get aberrations of a specific type."""
        return [a for a in self.aberrations if a.aberration_type == aberration_type]

    def by_region(self, region: str) -> list[Aberration]:
        """Get aberrations in a specific region."""
        return [a for a in self.aberrations if a.region == region]

    @property
    def summary(self) -> str:
        """Human-readable summary of the aberration profile."""
        if not self.aberrations:
            return "No aberrations detected (canonical walker)"

        lines = [
            f"Uniqueness: {self.uniqueness_score:.2f}",
            f"Primary region: {self.primary_region}",
            f"Dominant type: {self.dominant_type.value if self.dominant_type else 'none'}",
            f"Aberrations ({len(self.aberrations)}):",
        ]
        for a in self.aberrations[:5]:
            lines.append(f"  {a.signature}")
        if len(self.aberrations) > 5:
            lines.append(f"  ... and {len(self.aberrations) - 5} more")

        return "\n".join(lines)

    def __repr__(self):
        return f"AberrationProfile({self.walker_id}: {len(self.aberrations)} aberrations)"
