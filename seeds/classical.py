"""Classical Forks: Greek & Roman philosophical divergences.

These tensions shaped Western philosophy and still structure
contemporary debates. Plato vs Aristotle echoes through everything.

"The safest general characterization of the European philosophical
tradition is that it consists of a series of footnotes to Plato."
- Alfred North Whitehead
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from graph.forks import Fork, ForkLevel
from models.position import Domain


CLASSICAL_FORKS = [
    # ═══ METAPHYSICS: PLATO VS ARISTOTLE ═══
    Fork(
        id="forms",
        question="What is ultimately real?",
        option_a="Forms/Ideas—abstract universals, material world is shadow",
        option_b="Particulars—concrete individuals, universals abstracted from them",
        level=ForkLevel.ROOT,
        domain=Domain.METAPHYSICS,
        traditions_a=["platonist", "idealist", "rationalist"],
        traditions_b=["aristotelian", "empiricist", "nominalist"],
        polarization=0.9,
        importance=1.0
    ),
    Fork(
        id="being_becoming",
        question="Is reality static or dynamic?",
        option_a="Being—Parmenides, reality is unchanging, motion illusion",
        option_b="Becoming—Heraclitus, flux is fundamental, you can't step in same river",
        level=ForkLevel.ROOT,
        domain=Domain.METAPHYSICS,
        traditions_a=["eleatic", "eternalist", "platonist"],
        traditions_b=["heraclitean", "process", "pragmatist"],
        polarization=0.85,
        importance=0.9
    ),
    Fork(
        id="monism_pluralism",
        question="How many fundamental substances exist?",
        option_a="Monism—one substance, all is One (water, air, Being, God)",
        option_b="Pluralism—many substances, irreducible multiplicity",
        level=ForkLevel.METAPHYSICAL,
        domain=Domain.METAPHYSICS,
        traditions_a=["presocratic", "spinozist", "idealist"],
        traditions_b=["atomist", "pluralist", "empiricist"],
        polarization=0.8,
        importance=0.85
    ),

    # ═══ EPISTEMOLOGY ═══
    Fork(
        id="knowledge_source",
        question="What is the source of knowledge?",
        option_a="Reason—a priori, innate ideas, deduction from first principles",
        option_b="Experience—a posteriori, tabula rasa, induction from observation",
        level=ForkLevel.ROOT,
        domain=Domain.EPISTEMOLOGY,
        traditions_a=["rationalist", "platonist", "cartesian"],
        traditions_b=["empiricist", "aristotelian", "lockean"],
        polarization=0.9,
        importance=0.95
    ),
    Fork(
        id="skepticism",
        question="Can we have certain knowledge?",
        option_a="Yes—episteme possible, apodictic certainty achievable",
        option_b="No—only doxa/opinion, suspend judgment, ataraxia through doubt",
        level=ForkLevel.AXIOM,
        domain=Domain.EPISTEMOLOGY,
        traditions_a=["dogmatist", "stoic", "rationalist"],
        traditions_b=["skeptic", "pyrrhonist", "academic"],
        polarization=0.85,
        importance=0.85
    ),

    # ═══ ETHICS ═══
    Fork(
        id="good",
        question="What is the nature of the Good?",
        option_a="Transcendent—Good exists beyond, we apprehend it (Plato's Form)",
        option_b="Immanent—good is natural flourishing, function well (Aristotle's eudaimonia)",
        level=ForkLevel.AXIOM,
        domain=Domain.METAPHYSICS,
        parent_fork_id="forms",
        traditions_a=["platonist", "neoplatonist", "augustinian"],
        traditions_b=["aristotelian", "naturalist", "virtue_ethics"],
        polarization=0.8,
        importance=0.9
    ),
    Fork(
        id="virtue_pleasure",
        question="What should we pursue?",
        option_a="Virtue—excellence, arete, fulfill your nature/function",
        option_b="Pleasure—hedone, maximize pleasure minimize pain",
        level=ForkLevel.AXIOM,
        domain=Domain.SOCIAL,
        traditions_a=["stoic", "aristotelian", "platonic"],
        traditions_b=["epicurean", "cyrenaic", "utilitarian"],
        polarization=0.85,
        importance=0.9
    ),
    Fork(
        id="pleasure_type",
        question="What kind of pleasure matters?",
        option_a="Ataraxia—tranquility, absence of disturbance, simple pleasures",
        option_b="Kinetic pleasure—active enjoyment, intensity, variety",
        level=ForkLevel.DOMAIN,
        domain=Domain.SOCIAL,
        parent_fork_id="virtue_pleasure",
        traditions_a=["epicurean", "stoic", "buddhist"],
        traditions_b=["cyrenaic", "hedonist", "sensualist"],
        polarization=0.7,
        importance=0.7
    ),

    # ═══ POLITICAL PHILOSOPHY ═══
    Fork(
        id="regime",
        question="What is the best form of government?",
        option_a="Rule of the wise—philosopher kings, aristocracy of virtue",
        option_b="Mixed constitution—balance of powers, checks, polity",
        level=ForkLevel.FRAMEWORK,
        domain=Domain.GOVERNANCE,
        traditions_a=["platonic", "technocratic", "meritocratic"],
        traditions_b=["aristotelian", "republican", "constitutional"],
        polarization=0.8,
        importance=0.85
    ),
    Fork(
        id="polis_cosmos",
        question="What is the scope of political community?",
        option_a="Polis—bounded city-state, citizenship particular, local",
        option_b="Cosmopolis—world citizen, universal humanity, no borders",
        level=ForkLevel.FRAMEWORK,
        domain=Domain.GOVERNANCE,
        traditions_a=["aristotelian", "civic_republican", "communitarian"],
        traditions_b=["stoic", "cynic", "cosmopolitan"],
        polarization=0.85,
        importance=0.8
    ),
    Fork(
        id="nature_convention",
        question="Is justice natural or conventional?",
        option_a="Natural—physis, justice exists in nature, natural law",
        option_b="Conventional—nomos, justice is human agreement, social contract",
        level=ForkLevel.AXIOM,
        domain=Domain.GOVERNANCE,
        traditions_a=["stoic", "natural_law", "aristotelian"],
        traditions_b=["sophist", "contractarian", "positivist"],
        polarization=0.85,
        importance=0.9
    ),

    # ═══ HUMAN NATURE ═══
    Fork(
        id="soul",
        question="What is the soul?",
        option_a="Immortal—separable from body, preexists, transmigrates",
        option_b="Mortal—form of body, dies with it, no afterlife",
        level=ForkLevel.METAPHYSICAL,
        domain=Domain.METAPHYSICS,
        traditions_a=["platonic", "pythagorean", "orphic"],
        traditions_b=["aristotelian", "epicurean", "materialist"],
        polarization=0.9,
        importance=0.85
    ),
    Fork(
        id="reason_passion",
        question="What should govern human action?",
        option_a="Reason—logos rules, passions are horses to be controlled",
        option_b="Passion integrated—thumos/eros have proper role, not suppressed",
        level=ForkLevel.AXIOM,
        domain=Domain.SOCIAL,
        traditions_a=["stoic", "platonic", "rationalist"],
        traditions_b=["aristotelian", "romantic", "nietzschean"],
        polarization=0.75,
        importance=0.8
    ),

    # ═══ FATE & FREEDOM ═══
    Fork(
        id="fate",
        question="Is fate fixed or changeable?",
        option_a="Determinism—logos/heimarmene governs all, accept fate (amor fati)",
        option_b="Contingency—future open, genuine alternatives, we shape destiny",
        level=ForkLevel.METAPHYSICAL,
        domain=Domain.METAPHYSICS,
        traditions_a=["stoic", "fatalist", "determinist"],
        traditions_b=["epicurean", "libertarian", "existentialist"],
        polarization=0.85,
        importance=0.85
    ),
    Fork(
        id="providence",
        question="Is the cosmos providentially ordered?",
        option_a="Yes—logos/nous orders all for the best, teleology",
        option_b="No—atoms and void, chance, no purpose in nature",
        level=ForkLevel.ROOT,
        domain=Domain.METAPHYSICS,
        traditions_a=["stoic", "platonic", "aristotelian"],
        traditions_b=["epicurean", "atomist", "materialist"],
        polarization=0.9,
        importance=0.9
    ),

    # ═══ SOCIAL ENGAGEMENT ═══
    Fork(
        id="engagement",
        question="How should the wise person live?",
        option_a="Engaged—participate in politics, duty to polis/cosmos",
        option_b="Withdrawn—lathe biosas (live hidden), garden, private",
        level=ForkLevel.DOMAIN,
        domain=Domain.GOVERNANCE,
        traditions_a=["stoic", "platonic", "ciceronian"],
        traditions_b=["epicurean", "cynic", "quietist"],
        polarization=0.75,
        importance=0.75
    ),
    Fork(
        id="property",
        question="What is the proper attitude toward property?",
        option_a="Communal—guardians share, private property corrupts",
        option_b="Private—natural right, incentivizes virtue, protects family",
        level=ForkLevel.DOMAIN,
        domain=Domain.ECONOMICS,
        traditions_a=["platonic", "spartan", "cynic"],
        traditions_b=["aristotelian", "roman", "lockean"],
        polarization=0.8,
        importance=0.75
    ),

    # ═══ RHETORIC & TRUTH ═══
    Fork(
        id="rhetoric",
        question="What is the relationship between rhetoric and truth?",
        option_a="Dangerous—sophistry, makes weaker argument stronger, corrupts",
        option_b="Neutral/useful—tool for persuasion, can serve truth or falsehood",
        level=ForkLevel.DOMAIN,
        domain=Domain.EPISTEMOLOGY,
        traditions_a=["platonic", "philosophical", "anti_sophist"],
        traditions_b=["aristotelian", "isocratean", "ciceronian"],
        polarization=0.7,
        importance=0.7
    ),

    # ═══ ROMAN ADDITIONS ═══
    Fork(
        id="republic_empire",
        question="Is republican or imperial government better?",
        option_a="Republic—senate, mixed constitution, civic virtue",
        option_b="Empire—strong leader, pax romana, efficient order",
        level=ForkLevel.POLICY,
        domain=Domain.GOVERNANCE,
        parent_fork_id="regime",
        traditions_a=["republican", "ciceronian", "senatorial"],
        traditions_b=["caesarist", "imperial", "authoritarian"],
        polarization=0.85,
        importance=0.8
    ),
    Fork(
        id="mos_maiorum",
        question="How much should tradition constrain innovation?",
        option_a="Strongly—mos maiorum (way of ancestors), conserve customs",
        option_b="Weakly—adapt to circumstances, pragmatic innovation",
        level=ForkLevel.AXIOM,
        domain=Domain.SOCIAL,
        traditions_a=["conservative", "cato", "traditionalist"],
        traditions_b=["reformist", "gracchi", "pragmatist"],
        polarization=0.75,
        importance=0.8
    ),
]
