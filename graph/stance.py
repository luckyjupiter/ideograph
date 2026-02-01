"""Stance Extraction: Mining ideological positions from text.

Three key signals:
1. Framing - How is the issue framed? (security vs freedom, etc.)
2. Attribution - Who/what is blamed or credited?
3. Sourcing - What authorities are cited?

This extracts position stances from:
- Headlines
- Forum posts
- Study abstracts
- Social media
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import datetime
import re

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.position import Position, Domain


class FrameType(Enum):
    """Common ideological framing types."""
    SECURITY = "security"          # Safety, protection, stability
    FREEDOM = "freedom"            # Liberty, autonomy, rights
    FAIRNESS = "fairness"          # Equality, justice, equity
    AUTHORITY = "authority"        # Tradition, order, loyalty
    PURITY = "purity"              # Sanctity, degradation, sacred
    CARE = "care"                  # Harm, suffering, compassion
    EFFICIENCY = "efficiency"      # Pragmatic, results, optimization
    IDENTITY = "identity"          # Group, heritage, belonging


class AttributionTarget(Enum):
    """Who/what is blamed or credited."""
    GOVERNMENT = "government"
    CORPORATIONS = "corporations"
    ELITES = "elites"
    MEDIA = "media"
    FOREIGN_ACTORS = "foreign_actors"
    INDIVIDUALS = "individuals"
    SYSTEMS = "systems"
    TECHNOLOGY = "technology"
    NATURE = "nature"
    CULTURE = "culture"


class SourceType(Enum):
    """Types of authority sources."""
    ACADEMIC = "academic"          # Studies, research, experts
    RELIGIOUS = "religious"        # Scripture, tradition, clergy
    POLITICAL = "political"        # Officials, parties, movements
    MEDIA = "media"                # News, journalism, pundits
    PERSONAL = "personal"          # Experience, anecdote, intuition
    ECONOMIC = "economic"          # Markets, business leaders
    SCIENTIFIC = "scientific"      # Data, experiments, consensus
    HISTORICAL = "historical"      # Precedent, founding documents


@dataclass
class Frame:
    """A detected frame in text."""
    frame_type: FrameType
    strength: float  # 0.0 to 1.0
    keywords: list[str] = field(default_factory=list)
    snippet: str = ""


@dataclass
class Attribution:
    """A detected attribution in text."""
    target: AttributionTarget
    valence: float  # -1.0 (blame) to +1.0 (credit)
    keywords: list[str] = field(default_factory=list)
    snippet: str = ""


@dataclass
class Source:
    """A detected source citation in text."""
    source_type: SourceType
    credibility_signal: float  # 0.0 (dismissive) to 1.0 (authoritative)
    keywords: list[str] = field(default_factory=list)
    snippet: str = ""


@dataclass
class StanceSignature:
    """The complete stance signature extracted from text."""
    text: str
    frames: list[Frame] = field(default_factory=list)
    attributions: list[Attribution] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)

    # Inferred position
    inferred_positions: list[str] = field(default_factory=list)  # Position IDs
    domain_scores: dict[str, float] = field(default_factory=dict)

    # Metadata
    extracted_at: datetime = field(default_factory=datetime.now)
    confidence: float = 0.5

    @property
    def dominant_frame(self) -> Optional[Frame]:
        """Get the strongest frame."""
        if not self.frames:
            return None
        return max(self.frames, key=lambda f: f.strength)

    @property
    def blame_target(self) -> Optional[Attribution]:
        """Get the primary blame target."""
        blames = [a for a in self.attributions if a.valence < 0]
        if not blames:
            return None
        return min(blames, key=lambda a: a.valence)

    @property
    def credit_target(self) -> Optional[Attribution]:
        """Get the primary credit target."""
        credits = [a for a in self.attributions if a.valence > 0]
        if not credits:
            return None
        return max(credits, key=lambda a: a.valence)


class StanceExtractor:
    """Extracts stance signatures from text."""

    # Frame detection patterns
    FRAME_PATTERNS = {
        FrameType.SECURITY: [
            r'\b(threat|danger|protect|safe|security|risk|defense|attack|vulnerable)\b',
            r'\b(stability|order|chaos|crime|terror|invade)\b',
        ],
        FrameType.FREEDOM: [
            r'\b(freedom|liberty|rights|autonomous|choice|consent|voluntary)\b',
            r'\b(oppression|tyranny|mandate|forced|coercion|censorship)\b',
        ],
        FrameType.FAIRNESS: [
            r'\b(fair|equal|justice|equity|discriminat|privilege|disadvantage)\b',
            r'\b(bias|imbalance|disparity|unequal|exploit)\b',
        ],
        FrameType.AUTHORITY: [
            r'\b(tradition|heritage|loyalty|patriot|respect|duty|hierarchy)\b',
            r'\b(subvers|betray|disrespect|undermine)\b',
        ],
        FrameType.PURITY: [
            r'\b(pure|sacred|moral|corrupt|degenerat|disgust|natural)\b',
            r'\b(contaminat|pollut|pervert|unnatural)\b',
        ],
        FrameType.CARE: [
            r'\b(harm|suffer|compassion|help|victim|vulnerable|protect)\b',
            r'\b(cruel|abuse|neglect|care|nurture)\b',
        ],
        FrameType.EFFICIENCY: [
            r'\b(efficient|effective|pragmatic|results|optimize|waste)\b',
            r'\b(bureaucra|bloat|streamline|productive)\b',
        ],
        FrameType.IDENTITY: [
            r'\b(identity|heritage|culture|community|belonging|tribe)\b',
            r'\b(authentic|roots|ancestors|people)\b',
        ],
    }

    # Attribution patterns
    ATTRIBUTION_PATTERNS = {
        AttributionTarget.GOVERNMENT: [
            (r'\b(government|state|federal|congress|administration|politician)\b', 0),
            (r'\b(government.{0,20}(fail|corrupt|waste|oppress))', -0.5),
            (r'\b(government.{0,20}(protect|provide|help|support))', 0.5),
        ],
        AttributionTarget.CORPORATIONS: [
            (r'\b(corporat|big tech|pharma|wall street|business|company)\b', 0),
            (r'\b(corporat.{0,20}(greed|exploit|profit|corrupt))', -0.5),
            (r'\b(corporat.{0,20}(innovate|job|grow|invest))', 0.5),
        ],
        AttributionTarget.ELITES: [
            (r'\b(elite|establishment|ruling class|billionaire|oligarch)\b', 0),
            (r'\b(elite.{0,20}(control|manipulat|exploit|corrupt))', -0.5),
        ],
        AttributionTarget.MEDIA: [
            (r'\b(media|press|journalist|news|msm|mainstream)\b', 0),
            (r'\b(media.{0,20}(lie|bias|propaganda|fake))', -0.5),
            (r'\b(media.{0,20}(expose|investigate|truth))', 0.5),
        ],
        AttributionTarget.FOREIGN_ACTORS: [
            (r'\b(china|russia|foreign|immigrant|outsider)\b', 0),
            (r'\b(foreign.{0,20}(interfere|threat|invade|steal))', -0.5),
        ],
        AttributionTarget.INDIVIDUALS: [
            (r'\b(personal responsibility|individual|self-made|choice)\b', 0),
            (r'\b(lazy|irresponsible|entitled)\b', -0.3),
        ],
        AttributionTarget.SYSTEMS: [
            (r'\b(system|structural|institution|capitalis|socialis)\b', 0),
            (r'\b(systemic.{0,20}(racism|oppression|failure))', -0.3),
        ],
    }

    # Source patterns
    SOURCE_PATTERNS = {
        SourceType.ACADEMIC: [
            (r'\b(study|research|professor|university|peer.?review|data shows)\b', 0.7),
            (r'\b(according to.{0,30}(researchers|scientists|experts))\b', 0.8),
        ],
        SourceType.RELIGIOUS: [
            (r'\b(bible|scripture|god|faith|church|religious|moral)\b', 0.6),
            (r'\b(tradition teaches|natural law)\b', 0.7),
        ],
        SourceType.POLITICAL: [
            (r'\b(democrat|republican|party|campaign|politician|congress)\b', 0.3),
            (r'\b(according to.{0,30}(senator|representative|president))\b', 0.4),
        ],
        SourceType.MEDIA: [
            (r'\b(report|article|news|journalist|source says)\b', 0.5),
            (r'\b(according to.{0,30}(NYT|WSJ|Fox|CNN|BBC))\b', 0.6),
        ],
        SourceType.PERSONAL: [
            (r'\b(I believe|in my experience|I\'ve seen|I think|my family)\b', 0.3),
            (r'\b(common sense|obvious|everyone knows)\b', 0.2),
        ],
        SourceType.SCIENTIFIC: [
            (r'\b(scientific|evidence|experiment|data|consensus|peer.?review)\b', 0.8),
            (r'\b(proven|demonstrated|statistically)\b', 0.7),
        ],
    }

    def __init__(self, graph=None):
        self.graph = graph

    def extract(self, text: str) -> StanceSignature:
        """Extract stance signature from text."""
        signature = StanceSignature(text=text)

        # Extract frames
        signature.frames = self._extract_frames(text)

        # Extract attributions
        signature.attributions = self._extract_attributions(text)

        # Extract sources
        signature.sources = self._extract_sources(text)

        # Infer domain scores
        signature.domain_scores = self._infer_domains(signature)

        # Calculate confidence
        signal_count = len(signature.frames) + len(signature.attributions) + len(signature.sources)
        signature.confidence = min(1.0, signal_count / 5)

        # Match to known positions if graph available
        if self.graph:
            signature.inferred_positions = self._match_positions(signature)

        return signature

    def _extract_frames(self, text: str) -> list[Frame]:
        """Extract frames from text."""
        text_lower = text.lower()
        frames = []

        for frame_type, patterns in self.FRAME_PATTERNS.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, text_lower, re.IGNORECASE)
                matches.extend(found)

            if matches:
                # Calculate strength based on match density
                strength = min(1.0, len(matches) / 5)
                frames.append(Frame(
                    frame_type=frame_type,
                    strength=strength,
                    keywords=list(set(matches))[:5],
                    snippet=text[:100]
                ))

        return sorted(frames, key=lambda f: f.strength, reverse=True)

    def _extract_attributions(self, text: str) -> list[Attribution]:
        """Extract attributions from text."""
        text_lower = text.lower()
        attributions = []

        for target, patterns in self.ATTRIBUTION_PATTERNS.items():
            total_valence = 0.0
            match_count = 0
            keywords = []

            for pattern, base_valence in patterns:
                found = re.findall(pattern, text_lower, re.IGNORECASE)
                if found:
                    match_count += len(found)
                    total_valence += base_valence * len(found)
                    if isinstance(found[0], tuple):
                        keywords.extend([f[0] for f in found])
                    else:
                        keywords.extend(found)

            if match_count > 0:
                avg_valence = total_valence / match_count if total_valence != 0 else 0
                attributions.append(Attribution(
                    target=target,
                    valence=max(-1.0, min(1.0, avg_valence)),
                    keywords=list(set(keywords))[:5],
                    snippet=text[:100]
                ))

        return sorted(attributions, key=lambda a: abs(a.valence), reverse=True)

    def _extract_sources(self, text: str) -> list[Source]:
        """Extract source citations from text."""
        text_lower = text.lower()
        sources = []

        for source_type, patterns in self.SOURCE_PATTERNS.items():
            total_credibility = 0.0
            match_count = 0
            keywords = []

            for pattern, base_credibility in patterns:
                found = re.findall(pattern, text_lower, re.IGNORECASE)
                if found:
                    match_count += len(found)
                    total_credibility += base_credibility * len(found)
                    if isinstance(found[0], tuple):
                        keywords.extend([f[0] for f in found])
                    else:
                        keywords.extend(found)

            if match_count > 0:
                avg_credibility = total_credibility / match_count
                sources.append(Source(
                    source_type=source_type,
                    credibility_signal=avg_credibility,
                    keywords=list(set(keywords))[:5],
                    snippet=text[:100]
                ))

        return sorted(sources, key=lambda s: s.credibility_signal, reverse=True)

    def _infer_domains(self, signature: StanceSignature) -> dict[str, float]:
        """Infer domain relevance from stance signals."""
        domains = {}

        # Frame → Domain mapping
        frame_domains = {
            FrameType.SECURITY: ["military", "law"],
            FrameType.FREEDOM: ["civil_liberties", "economics"],
            FrameType.FAIRNESS: ["economics", "civil_liberties"],
            FrameType.AUTHORITY: ["tradition", "governance"],
            FrameType.PURITY: ["tradition", "culture"],
            FrameType.CARE: ["welfare", "social"],
            FrameType.EFFICIENCY: ["economics", "governance"],
            FrameType.IDENTITY: ["culture", "tradition"],
        }

        for frame in signature.frames:
            for domain in frame_domains.get(frame.frame_type, []):
                domains[domain] = domains.get(domain, 0) + frame.strength

        # Normalize
        if domains:
            max_score = max(domains.values())
            domains = {k: v / max_score for k, v in domains.items()}

        return domains

    def _match_positions(self, signature: StanceSignature) -> list[str]:
        """Match extracted stance to known positions in graph."""
        if not self.graph:
            return []

        matched = []
        text_lower = signature.text.lower()

        for pos_id, position in self.graph.positions.items():
            # Simple keyword matching (could be enhanced with embeddings)
            claim_words = set(position.claim.lower().split())
            text_words = set(text_lower.split())

            overlap = len(claim_words & text_words)
            if overlap >= 3:  # At least 3 words in common
                matched.append(pos_id)

        return matched[:5]  # Limit to top 5


def extract_positions_from_headline(headline: str, graph=None) -> list[Position]:
    """Extract positions from a news headline."""
    extractor = StanceExtractor(graph)
    signature = extractor.extract(headline)

    positions = []

    # Create position from dominant frame
    if signature.dominant_frame:
        frame = signature.dominant_frame
        pos = Position(
            claim=headline,
            domain=Domain.UNCATEGORIZED,  # Would need better domain inference
            valence=0.0,  # Neutral until analyzed
            level="position",
        )
        pos.add_source(f"headline:{headline[:50]}")
        positions.append(pos)

    return positions
