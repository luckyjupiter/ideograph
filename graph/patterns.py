"""Canonical Patterns: Named ideological trajectories.

Patterns are attractors - basins where many paths converge.
Examples: "bernie_bro_crypto", "lib_to_trad", "rationalist_technocrat"
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.walker import Walker


@dataclass
class CanonicalPattern:
    """A named ideological trajectory pattern.

    Learned from observing many walkers following similar paths.
    """

    # Identity
    name: str  # "bernie_bro_crypto", "tea_party_populist", etc.
    description: str = ""

    # Defining positions (in order of typical traversal)
    path_signature: list[str] = field(default_factory=list)  # Position IDs

    # Required positions (must have most of these to match)
    required_positions: set[str] = field(default_factory=set)

    # Forbidden positions (having these disqualifies match)
    forbidden_positions: set[str] = field(default_factory=set)

    # Statistics
    walker_count: int = 0  # How many walkers matched this pattern
    avg_fit_score: float = 0.0  # Average fit score of matched walkers

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def match_score(self, walker: Walker) -> float:
        """Calculate how well a walker matches this pattern.

        Returns: 0.0 (no match) to 1.0 (perfect match)
        """
        accepted = set(walker.positions_accepted)
        rejected = set(walker.positions_rejected)

        # Check forbidden positions
        if self.forbidden_positions & accepted:
            return 0.0  # Instant disqualification

        # Check required positions
        if self.required_positions:
            required_match = len(self.required_positions & accepted)
            required_score = required_match / len(self.required_positions)
        else:
            required_score = 0.5

        # Check path signature overlap
        if self.path_signature:
            path_overlap = len(set(self.path_signature) & accepted)
            path_score = path_overlap / len(self.path_signature)
        else:
            path_score = 0.5

        # Check rejected forbidden (bonus for rejecting what we expect to reject)
        if self.forbidden_positions:
            forbidden_rejected = len(self.forbidden_positions & rejected)
            forbidden_score = forbidden_rejected / len(self.forbidden_positions)
        else:
            forbidden_score = 0.5

        # Weighted combination
        return (required_score * 0.5 + path_score * 0.3 + forbidden_score * 0.2)

    def record_match(self, walker: Walker, score: float):
        """Record that a walker matched this pattern."""
        self.walker_count += 1
        # Running average
        self.avg_fit_score = (
            (self.avg_fit_score * (self.walker_count - 1) + score)
            / self.walker_count
        )
        self.updated_at = datetime.now()

    def __repr__(self):
        return f"CanonicalPattern({self.name}: {self.walker_count} matches)"


@dataclass
class PatternMatcher:
    """Matches walkers to canonical patterns."""

    patterns: dict[str, CanonicalPattern] = field(default_factory=dict)
    match_threshold: float = 0.6  # Minimum score to consider a match

    def add_pattern(self, pattern: CanonicalPattern):
        """Add a pattern to the matcher."""
        self.patterns[pattern.name] = pattern

    def match(self, walker: Walker) -> Optional[tuple[CanonicalPattern, float]]:
        """Find the best matching pattern for a walker.

        Returns: (pattern, score) or None if no match above threshold
        """
        best_pattern = None
        best_score = 0.0

        for pattern in self.patterns.values():
            score = pattern.match_score(walker)
            if score > best_score:
                best_score = score
                best_pattern = pattern

        if best_pattern and best_score >= self.match_threshold:
            best_pattern.record_match(walker, best_score)
            return (best_pattern, best_score)

        return None

    def all_matches(self, walker: Walker) -> list[tuple[CanonicalPattern, float]]:
        """Get all patterns that match above threshold, sorted by score."""
        matches = []
        for pattern in self.patterns.values():
            score = pattern.match_score(walker)
            if score >= self.match_threshold:
                matches.append((pattern, score))

        return sorted(matches, key=lambda x: x[1], reverse=True)


# ═══════════════════════════════════════════════════════════
# PREDEFINED PATTERNS (examples, should be learned from data)
# ═══════════════════════════════════════════════════════════

def create_default_patterns() -> PatternMatcher:
    """Create pattern matcher with default patterns."""
    matcher = PatternMatcher()

    # Bernie Bro → Crypto
    matcher.add_pattern(CanonicalPattern(
        name="bernie_bro_crypto",
        description="Progressive economics → tech optimism → crypto adoption → class skepticism",
        required_positions={"progressive_economics", "tech_optimism", "crypto_positive"},
        forbidden_positions={"maga", "trad_values"},
    ))

    # Tea Party Populist
    matcher.add_pattern(CanonicalPattern(
        name="tea_party_populist",
        description="Fiscal conservative → anti-establishment → Trump realignment",
        required_positions={"fiscal_conservative", "anti_establishment", "trump_positive"},
        forbidden_positions={"progressive_economics", "open_borders"},
    ))

    # Rationalist Technocrat
    matcher.add_pattern(CanonicalPattern(
        name="rationalist_technocrat",
        description="Evidence-based → EA → AI risk → longtermism",
        required_positions={"evidence_based", "effective_altruism", "ai_risk_concerned"},
        forbidden_positions={"anti_tech", "religious_fundamentalist"},
    ))

    # Post-Left
    matcher.add_pattern(CanonicalPattern(
        name="post_left",
        description="Marxist critique → anti-idpol → class reductionism → heterodox alliances",
        required_positions={"class_analysis", "anti_idpol"},
        forbidden_positions={"maga", "woke_positive"},
    ))

    # Trad Cath Integralist
    matcher.add_pattern(CanonicalPattern(
        name="trad_cath_integralist",
        description="Social conservative → anti-liberal → Catholic social teaching → integralism",
        required_positions={"social_conservative", "catholic_tradition", "anti_liberalism"},
        forbidden_positions={"libertarian", "progressive_social"},
    ))

    # Lib to Trad Pipeline
    matcher.add_pattern(CanonicalPattern(
        name="lib_to_trad",
        description="Liberal → disillusioned → red pilled → traditional values",
        path_signature=["liberal_baseline", "disillusionment", "red_pill", "trad_values"],
        required_positions={"trad_values"},
        forbidden_positions={"progressive_social"},
    ))

    # Leftist to Post-Left Pipeline
    matcher.add_pattern(CanonicalPattern(
        name="leftist_to_postleft",
        description="Socialist → anti-idpol turn → heterodox",
        path_signature=["socialist_baseline", "idpol_critique", "heterodox_left"],
        required_positions={"class_analysis", "anti_idpol"},
    ))

    return matcher
