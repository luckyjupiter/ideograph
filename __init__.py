"""IDEOGRAPH: Ideological Graph System

A map of idea-space where:
- Positions are NODES
- Relationships are EDGES (implies, contradicts, prioritizes)
- People WALK through it based on their beliefs
- Most walks are PREDICTABLE (attractors)
- What makes you YOU = the DEVIATIONS (aberrations)
- The system can CHALLENGE you by routing outside your basin
- Every walk UPDATES the map for everyone

It's Randonautica for your mind.

Spec by igloominance, architecture by Rook.
"""

from .models import (
    Position, Domain,
    Edge, EdgeType,
    Walker, Trajectory, Choice,
    Aberration, AberrationType,
)
from .graph import (
    IdeologicalGraph,
    CanonicalPattern, PatternMatcher,
    AttractorDetector, Attractor, Void,
)

__version__ = "0.1.0"
__all__ = [
    # Models
    'Position', 'Domain',
    'Edge', 'EdgeType',
    'Walker', 'Trajectory', 'Choice',
    'Aberration', 'AberrationType',
    # Graph
    'IdeologicalGraph',
    'CanonicalPattern', 'PatternMatcher',
    'AttractorDetector', 'Attractor', 'Void',
]
