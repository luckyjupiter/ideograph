"""Public Figure Profiler: Extract ideological positions from open sources.

Two methods to populate the graph:
1. Signal Analysis: Profile public figures from their statements
2. Questionnaire: Direct user profiling

This module handles method 1.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import re

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.position import Position, Domain
from models.walker import Walker
from graph.forks import Fork, ForkTree, ForkLevel
from graph.stance import StanceExtractor, StanceSignature


@dataclass
class Statement:
    """A statement from a public figure."""
    text: str
    source: str                    # Where this came from
    date: Optional[datetime] = None
    context: str = ""              # Interview, tweet, speech, etc.
    confidence: float = 0.8        # How confident are we this is real


@dataclass
class ForkStance:
    """A detected stance on a fork."""
    fork_id: str
    choice: str                    # "a" or "b"
    confidence: float              # How confident in this detection
    evidence: list[Statement] = field(default_factory=list)

    @property
    def choice_label(self) -> str:
        return "Option A" if self.choice == "a" else "Option B"


@dataclass
class IdeologicalProfile:
    """Complete ideological profile of a figure."""
    name: str
    stances: dict[str, ForkStance] = field(default_factory=dict)  # fork_id -> stance
    statements: list[Statement] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.now)

    # Derived classifications
    traditions: list[str] = field(default_factory=list)
    anomalies: list[str] = field(default_factory=list)

    def add_stance(self, stance: ForkStance):
        """Add or update a stance."""
        if stance.fork_id in self.stances:
            existing = self.stances[stance.fork_id]
            # Merge evidence
            existing.evidence.extend(stance.evidence)
            # Update confidence (weighted average)
            total_evidence = len(existing.evidence)
            existing.confidence = (
                (existing.confidence * (total_evidence - len(stance.evidence)) +
                 stance.confidence * len(stance.evidence)) / total_evidence
            )
            # If new choice differs and higher confidence, switch
            if stance.choice != existing.choice and stance.confidence > existing.confidence:
                existing.choice = stance.choice
        else:
            self.stances[stance.fork_id] = stance

    def to_walker(self, graph) -> Walker:
        """Convert profile to a walker that can traverse the graph."""
        walker = Walker(user_id=f"profile:{self.name}")

        for fork_id, stance in self.stances.items():
            pos_id = f"{fork_id}_{stance.choice}"
            if pos_id in graph.positions:
                from models.walker import Choice
                walker.choices.append(Choice(
                    position_id=pos_id,
                    accepted=True,
                    confidence=stance.confidence
                ))
                walker.path.append(pos_id)

        return walker

    def infer_traditions(self, tree: ForkTree) -> list[str]:
        """Infer which traditions this profile aligns with."""
        tradition_scores = {}

        for fork_id, stance in self.stances.items():
            fork = tree.forks.get(fork_id)
            if not fork:
                continue

            traditions = fork.traditions_a if stance.choice == "a" else fork.traditions_b
            weight = stance.confidence * fork.importance

            for trad in traditions:
                tradition_scores[trad] = tradition_scores.get(trad, 0) + weight

        # Normalize and sort
        if tradition_scores:
            max_score = max(tradition_scores.values())
            sorted_trads = sorted(
                tradition_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            self.traditions = [t for t, s in sorted_trads if s > max_score * 0.3]

        return self.traditions

    def find_anomalies(self, tree: ForkTree) -> list[str]:
        """Find positions that don't fit the dominant traditions."""
        if not self.traditions:
            self.infer_traditions(tree)

        dominant = set(self.traditions[:3]) if self.traditions else set()
        anomalies = []

        for fork_id, stance in self.stances.items():
            fork = tree.forks.get(fork_id)
            if not fork:
                continue

            expected_traditions = fork.traditions_a if stance.choice == "a" else fork.traditions_b
            if not set(expected_traditions) & dominant:
                # This stance doesn't match dominant traditions
                anomalies.append(
                    f"{fork.question}: chose '{fork.option_a if stance.choice == 'a' else fork.option_b}' "
                    f"(unusual for {', '.join(dominant)})"
                )

        self.anomalies = anomalies
        return anomalies

    @property
    def summary(self) -> str:
        """Human-readable summary."""
        lines = [
            f"Profile: {self.name}",
            f"Stances: {len(self.stances)} forks",
            f"Statements analyzed: {len(self.statements)}",
        ]
        if self.traditions:
            lines.append(f"Traditions: {', '.join(self.traditions[:5])}")
        if self.anomalies:
            lines.append(f"Anomalies: {len(self.anomalies)}")
            for a in self.anomalies[:3]:
                lines.append(f"  - {a[:60]}...")
        return "\n".join(lines)


class FigureProfiler:
    """Profile public figures from their statements."""

    def __init__(self, tree: ForkTree):
        self.tree = tree
        self.extractor = StanceExtractor()

        # Keywords that indicate stances on forks
        self.fork_indicators = self._build_indicators()

    def _build_indicators(self) -> dict[str, list[tuple[str, str, float]]]:
        """Build keyword indicators for each fork.

        Returns: {fork_id: [(pattern, choice, confidence), ...]}
        """
        indicators = {}

        # Generic patterns based on fork options
        for fork_id, fork in self.tree.forks.items():
            patterns = []

            # Extract keywords from options
            a_words = set(fork.option_a.lower().split()) - {'a', 'the', 'is', 'are', 'and', 'or'}
            b_words = set(fork.option_b.lower().split()) - {'a', 'the', 'is', 'are', 'and', 'or'}

            for word in a_words:
                if len(word) > 4:
                    patterns.append((rf'\b{word}\b', 'a', 0.4))
            for word in b_words:
                if len(word) > 4:
                    patterns.append((rf'\b{word}\b', 'b', 0.4))

            indicators[fork_id] = patterns

        # Add specific high-confidence patterns
        specific = {
            "freedom_vs_equality": [
                (r"equality.{0,20}(most important|priority|must)", "a", 0.8),
                (r"freedom.{0,20}(most important|priority|must)", "b", 0.8),
                (r"liberty.{0,20}(can'?t|cannot|never).{0,10}sacrifice", "b", 0.9),
                (r"redistribu", "a", 0.7),
            ],
            "markets": [
                (r"free market", "b", 0.7),
                (r"laissez.?faire", "b", 0.8),
                (r"regulat.{0,20}(need|must|important)", "a", 0.7),
                (r"socialis", "a", 0.75),
                (r"capitalis.{0,20}(fail|problem|issue)", "a", 0.6),
            ],
            "immigration": [
                (r"open border", "a", 0.8),
                (r"illegal.{0,10}immigra", "b", 0.6),
                (r"deporta", "b", 0.7),
                (r"immigrant.{0,20}(enrich|contribut|benefit)", "a", 0.7),
                (r"culture.{0,20}(threat|destroy|replace)", "b", 0.8),
            ],
            "israel": [
                (r"palestin.{0,20}(rights|freedom|liberation)", "a", 0.85),
                (r"israel.{0,20}(defend|ally|right)", "b", 0.8),
                (r"apartheid", "a", 0.9),
                (r"hamas.{0,20}(terror|attack)", "b", 0.7),
                (r"occupation", "a", 0.75),
                (r"zionism", "b", 0.5),  # Neutral-ish, depends on context
                (r"anti.?semit", "b", 0.6),
            ],
            "china": [
                (r"(decouple|decoupling)", "b", 0.8),
                (r"china.{0,20}(threat|danger|enemy)", "b", 0.85),
                (r"engage.{0,20}china", "a", 0.7),
                (r"ccp.{0,10}(evil|threat|regime)", "b", 0.9),
                (r"taiwan.{0,20}defend", "b", 0.8),
            ],
            "foreign_intervention": [
                (r"anti.?imperialist", "a", 0.85),
                (r"non.?intervention", "a", 0.8),
                (r"(bring|spread).{0,10}democracy", "b", 0.8),
                (r"military.{0,15}necessary", "b", 0.75),
                (r"forever.?war", "a", 0.8),
            ],
            "tradition_vs_progress": [
                (r"progressive.{0,10}(value|vision)", "a", 0.7),
                (r"traditional.{0,10}value", "b", 0.8),
                (r"conservative", "b", 0.6),
                (r"(outdated|backward)", "a", 0.7),
                (r"chesterton", "b", 0.9),
            ],
            "abortion": [
                (r"pro.?choice", "a", 0.95),
                (r"pro.?life", "b", 0.95),
                (r"bodily.?autonom", "a", 0.9),
                (r"(unborn|fetus).{0,10}(life|rights)", "b", 0.85),
                (r"roe.{0,10}(v|vs|versus).{0,5}wade", "a", 0.6),  # Mentioning doesn't mean supporting
            ],
            "guns": [
                (r"gun.?control", "a", 0.8),
                (r"second.?amendment", "b", 0.8),
                (r"2a", "b", 0.85),
                (r"ar.?15", "b", 0.5),  # Neutral mention
                (r"assault.?weapon.{0,10}ban", "a", 0.85),
                (r"self.?defen[sc]e.{0,10}right", "b", 0.8),
            ],
            "speech": [
                (r"free speech.{0,15}absolut", "b", 0.9),
                (r"(hate|harm).{0,10}speech", "a", 0.7),
                (r"deplatform", "a", 0.75),
                (r"censorship.{0,10}(bad|wrong|never)", "b", 0.85),
                (r"content.{0,10}moderat", "a", 0.6),
            ],
            "crypto": [
                (r"bitcoin.{0,20}(freedom|liberating)", "b", 0.8),
                (r"crypto.{0,20}(scam|fraud|ponzi)", "a", 0.85),
                (r"decentral.{0,20}(good|important|future)", "b", 0.8),
                (r"blockchain.{0,20}(revolutionary|transform)", "b", 0.7),
            ],
            "climate": [
                (r"climate.{0,15}(emergency|crisis|urgent)", "a", 0.85),
                (r"degrowth", "a", 0.9),
                (r"climate.{0,15}(hoax|scam|alarmist)", "b", 0.9),
                (r"green.?new.?deal", "a", 0.8),
                (r"(nuclear|technology).{0,15}(solve|solution)", "b", 0.7),
            ],
            "ai_risk": [
                (r"ai.{0,15}(existential|x.?risk)", "a", 0.85),
                (r"(pause|stop).{0,10}ai", "a", 0.8),
                (r"e/acc|effective.?accelerat", "b", 0.9),
                (r"ai.{0,15}(doom|apocalypse)", "a", 0.7),
                (r"ai.{0,15}(overblown|exaggerat)", "b", 0.8),
            ],
        }

        for fork_id, patterns in specific.items():
            if fork_id in indicators:
                indicators[fork_id].extend(patterns)
            else:
                indicators[fork_id] = patterns

        return indicators

    def analyze_statement(self, statement: Statement) -> list[ForkStance]:
        """Analyze a single statement for fork stances."""
        stances = []
        text_lower = statement.text.lower()

        for fork_id, patterns in self.fork_indicators.items():
            fork = self.tree.forks.get(fork_id)
            if not fork:
                continue

            a_score = 0.0
            b_score = 0.0
            a_matches = []
            b_matches = []

            for pattern, choice, weight in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    if choice == "a":
                        a_score += weight * len(matches)
                        a_matches.extend(matches)
                    else:
                        b_score += weight * len(matches)
                        b_matches.extend(matches)

            # Only record if clear signal
            if max(a_score, b_score) >= 0.4:
                total = a_score + b_score
                if a_score > b_score * 1.5:  # Clear preference for A
                    stances.append(ForkStance(
                        fork_id=fork_id,
                        choice="a",
                        confidence=min(0.95, a_score / total if total > 0 else 0.5),
                        evidence=[statement]
                    ))
                elif b_score > a_score * 1.5:  # Clear preference for B
                    stances.append(ForkStance(
                        fork_id=fork_id,
                        choice="b",
                        confidence=min(0.95, b_score / total if total > 0 else 0.5),
                        evidence=[statement]
                    ))

        return stances

    def profile(self, name: str, statements: list[Statement]) -> IdeologicalProfile:
        """Create complete profile from statements."""
        profile = IdeologicalProfile(name=name, statements=statements)

        for statement in statements:
            stances = self.analyze_statement(statement)
            for stance in stances:
                profile.add_stance(stance)

        # Infer traditions and find anomalies
        profile.infer_traditions(self.tree)
        profile.find_anomalies(self.tree)

        return profile


# ═══════════════════════════════════════════════════════════════════
# EXAMPLE PROFILES (for demonstration)
# ═══════════════════════════════════════════════════════════════════

def create_example_profiles(tree: ForkTree) -> list[IdeologicalProfile]:
    """Create example profiles for demonstration."""
    profiler = FigureProfiler(tree)

    # Tucker Carlson (example statements)
    tucker_statements = [
        Statement(
            text="The border is open and nobody seems to care. Millions are coming.",
            source="Fox News",
            context="monologue"
        ),
        Statement(
            text="Ukraine is not a democracy. Why are we sending billions there?",
            source="Fox News",
            context="interview"
        ),
        Statement(
            text="Big tech has too much power. They're censoring conservatives.",
            source="Tucker Carlson Tonight",
            context="monologue"
        ),
        Statement(
            text="The Iraq war was a disaster. We shouldn't be the world's policeman.",
            source="Interview",
            context="podcast"
        ),
        Statement(
            text="Traditional values and the family are under attack.",
            source="Fox News",
            context="monologue"
        ),
        Statement(
            text="Free speech is absolute. Let people say what they want.",
            source="Interview",
            context="podcast"
        ),
        Statement(
            text="China is a threat but we've been stupid about how we handle it.",
            source="Tucker Carlson Tonight",
            context="monologue"
        ),
    ]

    tucker = profiler.profile("Tucker Carlson", tucker_statements)

    # AOC (example statements)
    aoc_statements = [
        Statement(
            text="We need a Green New Deal. Climate change is an existential threat.",
            source="Congress",
            context="speech"
        ),
        Statement(
            text="Medicare for All is a human right.",
            source="Twitter",
            context="tweet"
        ),
        Statement(
            text="The rich need to pay their fair share. Tax the billionaires.",
            source="Interview",
            context="TV"
        ),
        Statement(
            text="Abolish ICE. Immigration enforcement is cruel.",
            source="Rally",
            context="speech"
        ),
        Statement(
            text="Palestinians deserve rights. The occupation is wrong.",
            source="Congress",
            context="statement"
        ),
        Statement(
            text="Break up big tech. They have too much power.",
            source="Hearing",
            context="congress"
        ),
    ]

    aoc = profiler.profile("Alexandria Ocasio-Cortez", aoc_statements)

    # Peter Thiel (example statements)
    thiel_statements = [
        Statement(
            text="Competition is for losers. Monopoly is the goal of capitalism.",
            source="Zero to One",
            context="book"
        ),
        Statement(
            text="Crypto represents freedom from government money.",
            source="Interview",
            context="conference"
        ),
        Statement(
            text="I no longer believe that freedom and democracy are compatible.",
            source="Essay",
            context="cato"
        ),
        Statement(
            text="AI is the most important technology of the century.",
            source="Interview",
            context="podcast"
        ),
        Statement(
            text="China is the real threat. We need to decouple.",
            source="Interview",
            context="conference"
        ),
        Statement(
            text="The universities have been captured by the left.",
            source="Interview",
            context="podcast"
        ),
    ]

    thiel = profiler.profile("Peter Thiel", thiel_statements)

    return [tucker, aoc, thiel]
