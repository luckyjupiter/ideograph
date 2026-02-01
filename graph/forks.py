"""Ideological Forks: The decision tree backbone.

Everything begins with gathering the relevant forks/dilemmas,
then superimposing paths onto them.

Structure:
- ROOT: Most general (meaning of life, human nature, etc.)
- BRANCHES: Major ideological axes (economics, social, governance)
- LEAVES: Specific contextual positions (policy on X)

Two population methods:
1. Signal Analysis: Extract from public figures/sources
2. Questionnaire: Profile users directly
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import datetime
import json
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.position import Position, Domain
from models.edge import Edge, EdgeType


class ForkLevel(Enum):
    """Depth level in the fork tree."""
    ROOT = "root"           # Deepest axioms (meaning, nature, etc.)
    METAPHYSICAL = "meta"   # Ontological commitments
    AXIOM = "axiom"         # Foundational values
    FRAMEWORK = "framework" # Organizing principles
    DOMAIN = "domain"       # Area-specific stances
    POLICY = "policy"       # Concrete positions
    CONTEXT = "context"     # Situational applications


@dataclass
class Fork:
    """A binary ideological decision point.

    "When you must choose, which side do you lean?"
    """
    id: str
    question: str                      # The dilemma framing
    option_a: str                      # One pole
    option_b: str                      # Other pole
    level: ForkLevel = ForkLevel.DOMAIN
    domain: Domain = Domain.UNCATEGORIZED
    parent_fork_id: Optional[str] = None  # What fork leads to this one
    child_forks: list[str] = field(default_factory=list)  # Forks that follow

    # Metadata
    traditions_a: list[str] = field(default_factory=list)  # Who typically chooses A
    traditions_b: list[str] = field(default_factory=list)  # Who typically chooses B

    # Weighting
    polarization: float = 0.5  # How strongly this divides people
    importance: float = 0.5    # How much downstream this affects

    def __post_init__(self):
        if not self.id:
            self.id = f"fork_{self.question[:20].lower().replace(' ', '_')}"

    def to_positions(self) -> tuple[Position, Position]:
        """Convert fork to two positions (one for each pole)."""
        pos_a = Position(
            id=f"{self.id}_a",
            claim=self.option_a,
            domain=self.domain,
            valence=-0.5,  # Convention: A is "left" pole
            level="position",
            traditions=self.traditions_a
        )
        pos_b = Position(
            id=f"{self.id}_b",
            claim=self.option_b,
            domain=self.domain,
            valence=0.5,   # Convention: B is "right" pole
            level="position",
            traditions=self.traditions_b
        )
        return pos_a, pos_b

    def to_edge(self) -> Edge:
        """Create contradiction edge between the poles."""
        return Edge(
            source_id=f"{self.id}_a",
            target_id=f"{self.id}_b",
            edge_type=EdgeType.CONTRADICTS,
            weight=self.polarization
        )


# ═══════════════════════════════════════════════════════════════════
# THE CANONICAL FORK TREE (Contemporary Ideology Backbone)
# ═══════════════════════════════════════════════════════════════════

FORK_TREE = [
    # ═══ ROOT: Deepest questions ═══
    Fork(
        id="meaning",
        question="What is the meaning of human existence?",
        option_a="Life has inherent meaning/purpose (theistic/essentialist)",
        option_b="Meaning is constructed/emergent (existentialist/materialist)",
        level=ForkLevel.ROOT,
        domain=Domain.METAPHYSICS,
        traditions_a=["religious", "classical", "traditionalist"],
        traditions_b=["secular", "existentialist", "progressive"],
        polarization=0.8,
        importance=1.0
    ),
    Fork(
        id="human_nature",
        question="What is human nature?",
        option_a="Humans are flawed/fallen, need constraint",
        option_b="Humans are good/perfectible, need liberation",
        level=ForkLevel.ROOT,
        domain=Domain.METAPHYSICS,
        traditions_a=["conservative", "religious", "realist"],
        traditions_b=["progressive", "anarchist", "utopian"],
        polarization=0.9,
        importance=1.0
    ),
    Fork(
        id="knowledge",
        question="How do we know what's true?",
        option_a="Tradition, revelation, accumulated wisdom",
        option_b="Reason, empiricism, individual inquiry",
        level=ForkLevel.ROOT,
        domain=Domain.EPISTEMOLOGY,
        traditions_a=["traditionalist", "religious", "burkean"],
        traditions_b=["rationalist", "scientific", "enlightenment"],
        polarization=0.7,
        importance=0.9
    ),

    # ═══ METAPHYSICAL: Ontological commitments ═══
    Fork(
        id="individualism",
        question="What is the basic unit of society?",
        option_a="The individual, with inherent rights",
        option_b="The collective/community, individuals embedded",
        level=ForkLevel.METAPHYSICAL,
        domain=Domain.GOVERNANCE,
        parent_fork_id="meaning",
        traditions_a=["libertarian", "liberal", "objectivist"],
        traditions_b=["communitarian", "socialist", "traditionalist"],
        polarization=0.85,
        importance=0.95
    ),
    Fork(
        id="equality_vs_hierarchy",
        question="What is the natural order of society?",
        option_a="Fundamental equality, hierarchy is imposed",
        option_b="Natural hierarchy, equality is artificial",
        level=ForkLevel.METAPHYSICAL,
        domain=Domain.GOVERNANCE,
        parent_fork_id="human_nature",
        traditions_a=["egalitarian", "socialist", "progressive"],
        traditions_b=["conservative", "monarchist", "meritocratic"],
        polarization=0.9,
        importance=0.95
    ),
    Fork(
        id="change",
        question="How should society change?",
        option_a="Gradual reform, preserve what works",
        option_b="Bold transformation, break what's broken",
        level=ForkLevel.METAPHYSICAL,
        domain=Domain.GOVERNANCE,
        parent_fork_id="knowledge",
        traditions_a=["conservative", "centrist", "institutionalist"],
        traditions_b=["progressive", "revolutionary", "accelerationist"],
        polarization=0.75,
        importance=0.85
    ),

    # ═══ AXIOM: Foundational values ═══
    Fork(
        id="freedom_vs_equality",
        question="When freedom and equality conflict, which prevails?",
        option_a="Equality—outcomes matter more than process",
        option_b="Freedom—liberty must not be sacrificed",
        level=ForkLevel.AXIOM,
        domain=Domain.GOVERNANCE,
        parent_fork_id="individualism",
        traditions_a=["socialist", "progressive", "social_democrat"],
        traditions_b=["libertarian", "classical_liberal", "conservative"],
        polarization=0.9,
        importance=0.9
    ),
    Fork(
        id="security_vs_liberty",
        question="When security and liberty conflict, which prevails?",
        option_a="Security—safety enables all other goods",
        option_b="Liberty—freedom cannot be traded for safety",
        level=ForkLevel.AXIOM,
        domain=Domain.GOVERNANCE,
        parent_fork_id="individualism",
        traditions_a=["statist", "authoritarian", "paternalist"],
        traditions_b=["libertarian", "aclu_liberal", "civil_libertarian"],
        polarization=0.8,
        importance=0.85
    ),
    Fork(
        id="tradition_vs_progress",
        question="Is the past a guide or obstacle?",
        option_a="Progress—history is moral improvement",
        option_b="Tradition—accumulated wisdom, Chesterton's fence",
        level=ForkLevel.AXIOM,
        domain=Domain.SOCIAL,
        parent_fork_id="change",
        traditions_a=["progressive", "transhumanist", "modernist"],
        traditions_b=["conservative", "traditionalist", "perennialist"],
        polarization=0.85,
        importance=0.85
    ),

    # ═══ FRAMEWORK: Organizing principles ═══
    Fork(
        id="markets",
        question="What role should markets play?",
        option_a="Markets need strong regulation/planning",
        option_b="Free markets allocate best, minimal intervention",
        level=ForkLevel.FRAMEWORK,
        domain=Domain.ECONOMICS,
        parent_fork_id="freedom_vs_equality",
        traditions_a=["socialist", "keynesian", "social_democrat"],
        traditions_b=["libertarian", "austrian", "neoliberal"],
        polarization=0.85,
        importance=0.8
    ),
    Fork(
        id="state",
        question="What should the state do?",
        option_a="Expansive: provide, protect, redistribute",
        option_b="Minimal: defense, courts, contracts only",
        level=ForkLevel.FRAMEWORK,
        domain=Domain.GOVERNANCE,
        parent_fork_id="freedom_vs_equality",
        traditions_a=["social_democrat", "progressive", "statist"],
        traditions_b=["libertarian", "minarchist", "classical_liberal"],
        polarization=0.85,
        importance=0.85
    ),
    Fork(
        id="nationalism",
        question="What is the proper scope of political community?",
        option_a="Cosmopolitan—universal humanity, global institutions",
        option_b="National—bounded communities, sovereignty",
        level=ForkLevel.FRAMEWORK,
        domain=Domain.FOREIGN_POLICY,
        parent_fork_id="individualism",
        traditions_a=["globalist", "liberal_internationalist", "eu_federalist"],
        traditions_b=["nationalist", "paleocon", "sovereigntist"],
        polarization=0.8,
        importance=0.75
    ),

    # ═══ DOMAIN: Area-specific stances ═══
    Fork(
        id="immigration",
        question="What should immigration policy prioritize?",
        option_a="Open—human mobility, economic growth",
        option_b="Restricted—cultural cohesion, labor protection",
        level=ForkLevel.DOMAIN,
        domain=Domain.SOCIAL,
        parent_fork_id="nationalism",
        traditions_a=["libertarian", "progressive", "neoliberal"],
        traditions_b=["populist", "nationalist", "labor_left"],
        polarization=0.85,
        importance=0.7
    ),
    Fork(
        id="trade",
        question="What trade policy is best?",
        option_a="Free trade—comparative advantage, globalization",
        option_b="Protected trade—domestic industry, strategic autonomy",
        level=ForkLevel.DOMAIN,
        domain=Domain.ECONOMICS,
        parent_fork_id="markets",
        traditions_a=["neoliberal", "libertarian", "establishment"],
        traditions_b=["populist", "labor", "nationalist"],
        polarization=0.7,
        importance=0.65
    ),
    Fork(
        id="welfare",
        question="What level of welfare state?",
        option_a="Expansive—universal services, safety net",
        option_b="Minimal—targeted, means-tested, personal responsibility",
        level=ForkLevel.DOMAIN,
        domain=Domain.ECONOMICS,
        parent_fork_id="state",
        traditions_a=["social_democrat", "progressive", "labor"],
        traditions_b=["conservative", "libertarian", "fiscal_hawk"],
        polarization=0.8,
        importance=0.75
    ),
    Fork(
        id="foreign_intervention",
        question="When should military force be used abroad?",
        option_a="Rarely—non-intervention, anti-imperialism",
        option_b="When necessary—for democracy, security, allies",
        level=ForkLevel.DOMAIN,
        domain=Domain.FOREIGN_POLICY,
        parent_fork_id="nationalism",
        traditions_a=["anti_war", "paleocon", "left_anti_imperialist"],
        traditions_b=["neocon", "liberal_interventionist", "hawk"],
        polarization=0.75,
        importance=0.7
    ),
    Fork(
        id="israel",
        question="What is the right approach to Israel-Palestine?",
        option_a="Palestinian rights—occupation is unjust",
        option_b="Israeli security—existential defense, ally",
        level=ForkLevel.DOMAIN,
        domain=Domain.FOREIGN_POLICY,
        parent_fork_id="foreign_intervention",
        traditions_a=["left", "anti_zionist", "arab_solidarity"],
        traditions_b=["zionist", "evangelical", "neocon"],
        polarization=0.95,
        importance=0.6
    ),
    Fork(
        id="china",
        question="How should the West approach China?",
        option_a="Engagement—interdependence, diplomacy",
        option_b="Confrontation—decoupling, containment",
        level=ForkLevel.DOMAIN,
        domain=Domain.FOREIGN_POLICY,
        parent_fork_id="nationalism",
        traditions_a=["globalist", "business", "realist_dove"],
        traditions_b=["hawk", "nationalist", "security_state"],
        polarization=0.7,
        importance=0.7
    ),
    Fork(
        id="tech_regulation",
        question="How should technology be governed?",
        option_a="Light touch—innovation, disruption good",
        option_b="Strong regulation—safety, antitrust, privacy",
        level=ForkLevel.DOMAIN,
        domain=Domain.TECHNOLOGY,
        parent_fork_id="markets",
        traditions_a=["libertarian", "tech_optimist", "accelerationist"],
        traditions_b=["progressive", "precautionary", "antitrust"],
        polarization=0.65,
        importance=0.65
    ),
    Fork(
        id="ai_risk",
        question="Is advanced AI an existential threat?",
        option_a="Yes—pause/regulate development urgently",
        option_b="No—benefits outweigh risks, continue",
        level=ForkLevel.DOMAIN,
        domain=Domain.TECHNOLOGY,
        parent_fork_id="tech_regulation",
        traditions_a=["ai_safety", "longtermist", "precautionary"],
        traditions_b=["e/acc", "tech_optimist", "industry"],
        polarization=0.75,
        importance=0.6
    ),
    Fork(
        id="climate",
        question="How urgent is climate action?",
        option_a="Urgent—transform economy, degrowth if needed",
        option_b="Gradual—technology will solve, cost-benefit",
        level=ForkLevel.DOMAIN,
        domain=Domain.ENVIRONMENT,
        parent_fork_id="change",
        traditions_a=["green", "progressive", "degrowth"],
        traditions_b=["conservative", "techno_optimist", "skeptic"],
        polarization=0.8,
        importance=0.7
    ),

    # ═══ POLICY: Concrete positions ═══
    Fork(
        id="abortion",
        question="What abortion policy is right?",
        option_a="Legal and accessible—bodily autonomy",
        option_b="Restricted/banned—fetal life",
        level=ForkLevel.POLICY,
        domain=Domain.SOCIAL,
        parent_fork_id="tradition_vs_progress",
        traditions_a=["feminist", "progressive", "libertarian"],
        traditions_b=["pro_life", "religious", "conservative"],
        polarization=0.95,
        importance=0.6
    ),
    Fork(
        id="guns",
        question="What gun policy is right?",
        option_a="Strict control—safety, regulation",
        option_b="Permissive—2A rights, self-defense",
        level=ForkLevel.POLICY,
        domain=Domain.CIVIL_LIBERTIES,
        parent_fork_id="security_vs_liberty",
        traditions_a=["progressive", "urban", "gun_control"],
        traditions_b=["conservative", "libertarian", "rural"],
        polarization=0.9,
        importance=0.55
    ),
    Fork(
        id="speech",
        question="How should offensive speech be handled?",
        option_a="Platform moderation—harm reduction, norms",
        option_b="Free speech absolutism—no censorship",
        level=ForkLevel.POLICY,
        domain=Domain.CIVIL_LIBERTIES,
        parent_fork_id="security_vs_liberty",
        traditions_a=["progressive", "harm_focused", "safety"],
        traditions_b=["libertarian", "free_speech", "civil_libertarian"],
        polarization=0.8,
        importance=0.6
    ),
    Fork(
        id="crypto",
        question="What is crypto's role?",
        option_a="Speculation/scam—needs heavy regulation",
        option_b="Financial freedom—decentralization, exit",
        level=ForkLevel.POLICY,
        domain=Domain.TECHNOLOGY,
        parent_fork_id="markets",
        traditions_a=["skeptic", "progressive", "statist"],
        traditions_b=["libertarian", "crypto_native", "accelerationist"],
        polarization=0.7,
        importance=0.45
    ),
]


class ForkTree:
    """The complete ideological fork tree."""

    def __init__(self):
        self.forks: dict[str, Fork] = {}
        self._build_tree()

    def _build_tree(self):
        """Build the tree from FORK_TREE."""
        for fork in FORK_TREE:
            self.forks[fork.id] = fork
            # Link children to parents
            if fork.parent_fork_id and fork.parent_fork_id in self.forks:
                self.forks[fork.parent_fork_id].child_forks.append(fork.id)

    def get_by_level(self, level: ForkLevel) -> list[Fork]:
        """Get all forks at a given level."""
        return [f for f in self.forks.values() if f.level == level]

    def get_children(self, fork_id: str) -> list[Fork]:
        """Get child forks."""
        fork = self.forks.get(fork_id)
        if not fork:
            return []
        return [self.forks[cid] for cid in fork.child_forks if cid in self.forks]

    def get_path_to_root(self, fork_id: str) -> list[Fork]:
        """Get path from fork to root."""
        path = []
        current_id = fork_id
        while current_id:
            fork = self.forks.get(current_id)
            if not fork:
                break
            path.append(fork)
            current_id = fork.parent_fork_id
        return path

    def to_graph_positions(self, graph) -> int:
        """Add all forks as positions to a graph.

        Returns: number of positions added
        """
        count = 0
        for fork in self.forks.values():
            pos_a, pos_b = fork.to_positions()
            graph.add_position(pos_a)
            graph.add_position(pos_b)
            graph.add_edge(fork.to_edge())
            count += 2

            # Add parent-child edges
            if fork.parent_fork_id:
                # Both poles of parent can lead to this fork
                parent_a = f"{fork.parent_fork_id}_a"
                parent_b = f"{fork.parent_fork_id}_b"
                for parent_id in [parent_a, parent_b]:
                    if parent_id in [p.id for p in graph.positions.values()]:
                        graph.add_edge(Edge(
                            source_id=parent_id,
                            target_id=pos_a.id,
                            edge_type=EdgeType.IMPLIES,
                            weight=0.3
                        ))
                        graph.add_edge(Edge(
                            source_id=parent_id,
                            target_id=pos_b.id,
                            edge_type=EdgeType.IMPLIES,
                            weight=0.3
                        ))
        return count

    def save(self, path: Path):
        """Save fork tree to JSON."""
        data = {
            fork_id: {
                "id": fork.id,
                "question": fork.question,
                "option_a": fork.option_a,
                "option_b": fork.option_b,
                "level": fork.level.value,
                "domain": fork.domain.value,
                "parent_fork_id": fork.parent_fork_id,
                "child_forks": fork.child_forks,
                "traditions_a": fork.traditions_a,
                "traditions_b": fork.traditions_b,
                "polarization": fork.polarization,
                "importance": fork.importance,
            }
            for fork_id, fork in self.forks.items()
        }
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> "ForkTree":
        """Load fork tree from JSON."""
        path = Path(path)
        if not path.exists():
            return cls()

        data = json.loads(path.read_text())
        tree = cls.__new__(cls)
        tree.forks = {}

        for fork_id, fdata in data.items():
            tree.forks[fork_id] = Fork(
                id=fdata["id"],
                question=fdata["question"],
                option_a=fdata["option_a"],
                option_b=fdata["option_b"],
                level=ForkLevel(fdata["level"]),
                domain=Domain(fdata["domain"]),
                parent_fork_id=fdata.get("parent_fork_id"),
                child_forks=fdata.get("child_forks", []),
                traditions_a=fdata.get("traditions_a", []),
                traditions_b=fdata.get("traditions_b", []),
                polarization=fdata.get("polarization", 0.5),
                importance=fdata.get("importance", 0.5),
            )

        return tree

    def __repr__(self):
        return f"ForkTree({len(self.forks)} forks)"


def generate_questionnaire(tree: ForkTree, start_level: ForkLevel = ForkLevel.AXIOM) -> list[Fork]:
    """Generate a questionnaire from the fork tree.

    Starts at the specified level and proceeds to more specific forks.
    """
    questionnaire = []

    # Get starting level forks
    starting = tree.get_by_level(start_level)
    questionnaire.extend(starting)

    # Add deeper forks
    for fork in starting:
        children = tree.get_children(fork.id)
        questionnaire.extend(children)

    return questionnaire
