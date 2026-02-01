#!/usr/bin/env python3
"""IDEOGRAPH Demo

Demonstrates the ideological graph system with sample data.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models.position import Position, Domain, axiom, position, policy
from models.edge import Edge, EdgeType, implies, contradicts, prioritizes, collider
from models.walker import Walker
from models.aberration import deletion, insertion, inversion
from graph.ideograph import IdeologicalGraph
from graph.attractors import AttractorDetector
from graph.patterns import create_default_patterns
from graph.probing import AdaptiveProber
from graph.tension import TensionAnalyzer
from graph.stance import StanceExtractor
from graph.forks import ForkTree, ForkLevel
from graph.profiler import FigureProfiler, create_example_profiles, Statement
from graph.compaction import GraphCompactor, analyze_fork_structure


def create_demo_graph() -> IdeologicalGraph:
    """Create a demo graph with sample ideological positions."""
    graph = IdeologicalGraph(name="demo")

    # ═══════════════════════════════════════════════════════════
    # AXIOMS (foundational beliefs)
    # ═══════════════════════════════════════════════════════════

    hierarchy_natural = axiom(
        "Hierarchy is natural and necessary",
        Domain.METAPHYSICS,
        valence=0.7
    )
    humans_perfectible = axiom(
        "Humans are perfectible through institutions",
        Domain.METAPHYSICS,
        valence=-0.5
    )
    freedom_primary = axiom(
        "Individual freedom is the primary value",
        Domain.GOVERNANCE,
        valence=0.3
    )
    equality_primary = axiom(
        "Equality is the primary value",
        Domain.GOVERNANCE,
        valence=-0.5
    )

    for a in [hierarchy_natural, humans_perfectible, freedom_primary, equality_primary]:
        graph.add_position(a)

    # ═══════════════════════════════════════════════════════════
    # POSITIONS (concrete stances)
    # ═══════════════════════════════════════════════════════════

    positions_data = [
        # Economics
        ("Free markets solve most problems", Domain.ECONOMICS, 0.7),
        ("Wealth redistribution is necessary", Domain.ECONOMICS, -0.7),
        ("Unions protect workers", Domain.ECONOMICS, -0.4),
        ("Regulations harm innovation", Domain.ECONOMICS, 0.6),

        # Social
        ("Traditional values matter", Domain.SOCIAL, 0.7),
        ("Progressive social change is good", Domain.SOCIAL, -0.7),
        ("Immigration enriches culture", Domain.SOCIAL, -0.3),
        ("Immigration threatens culture", Domain.SOCIAL, 0.5),

        # Foreign Policy
        ("US hegemony is good for the world", Domain.FOREIGN_POLICY, 0.5),
        ("Multipolarity is inevitable", Domain.FOREIGN_POLICY, -0.2),
        ("Military intervention is sometimes necessary", Domain.FOREIGN_POLICY, 0.3),
        ("Anti-imperialism is essential", Domain.FOREIGN_POLICY, -0.6),

        # Technology
        ("Tech progress is inherently good", Domain.TECHNOLOGY, 0.3),
        ("AI poses existential risk", Domain.TECHNOLOGY, 0.0),
        ("Crypto decentralizes power", Domain.TECHNOLOGY, 0.2),
        ("Tech needs regulation", Domain.TECHNOLOGY, -0.2),

        # Governance
        ("Democracy is the best system", Domain.GOVERNANCE, 0.0),
        ("Elites should lead", Domain.GOVERNANCE, 0.5),
        ("Direct action is valid", Domain.GOVERNANCE, -0.4),
        ("Institutions matter more than individuals", Domain.GOVERNANCE, 0.0),
    ]

    all_positions = {}
    for claim, domain, valence in positions_data:
        p = position(claim, domain, valence=valence)
        graph.add_position(p)
        all_positions[p.id] = p

    # ═══════════════════════════════════════════════════════════
    # EDGES (relationships)
    # ═══════════════════════════════════════════════════════════

    # Get position IDs for edges
    def find_pos(keyword):
        for pid, p in graph.positions.items():
            if keyword.lower() in p.claim.lower():
                return pid
        return None

    # Implies edges
    graph.add_edge(implies(
        find_pos("hierarchy is natural"),
        find_pos("traditional values"),
        weight=0.7
    ))
    graph.add_edge(implies(
        find_pos("free markets"),
        find_pos("regulations harm"),
        weight=0.6
    ))
    graph.add_edge(implies(
        find_pos("humans are perfectible"),
        find_pos("progressive social"),
        weight=0.6
    ))
    graph.add_edge(implies(
        find_pos("equality is the primary"),
        find_pos("wealth redistribution"),
        weight=0.7
    ))

    # Contradicts edges
    graph.add_edge(contradicts(
        find_pos("free markets"),
        find_pos("wealth redistribution"),
        weight=0.8
    ))
    graph.add_edge(contradicts(
        find_pos("traditional values"),
        find_pos("progressive social"),
        weight=0.9
    ))
    graph.add_edge(contradicts(
        find_pos("immigration enriches"),
        find_pos("immigration threatens"),
        weight=0.95
    ))

    # Prioritizes edges (the key ones)
    graph.add_edge(prioritizes(
        find_pos("freedom is the primary"),
        find_pos("equality is the primary"),
        context="When freedom and equality conflict"
    ))

    # Collider: Free speech absolutism
    # (Both libertarians and ACLU liberals arrive here)
    free_speech = position("Free speech is absolute", Domain.CIVIL_LIBERTIES)
    graph.add_position(free_speech)

    e1, e2 = collider(
        find_pos("freedom is the primary"),  # Libertarian path
        find_pos("progressive social"),  # ACLU liberal path
        free_speech.id
    )
    graph.add_edge(e1)
    graph.add_edge(e2)

    return graph


def simulate_walker(graph: IdeologicalGraph, name: str,
                    accepts: list[str], rejects: list[str]) -> Walker:
    """Simulate a walker with given positions."""
    walker = graph.create_walker(name)

    def find_pos(keyword):
        for pid, p in graph.positions.items():
            if keyword.lower() in p.claim.lower():
                return pid
        return None

    # Accept positions
    for keyword in accepts:
        pos_id = find_pos(keyword)
        if pos_id:
            graph.walk_step(walker, pos_id, accepted=True, confidence=0.8)

    # Reject positions
    for keyword in rejects:
        pos_id = find_pos(keyword)
        if pos_id:
            graph.walk_step(walker, pos_id, accepted=False, confidence=0.7)

    return walker


def main():
    print("=" * 60)
    print("IDEOGRAPH Demo")
    print("=" * 60)

    # Create demo graph
    graph = create_demo_graph()
    print(f"\nCreated graph: {graph}")
    print(f"Stats: {graph.stats}")

    # Create pattern matcher
    matcher = create_default_patterns()
    print(f"\nLoaded {len(matcher.patterns)} canonical patterns")

    # Simulate some walkers
    print("\n" + "=" * 60)
    print("Simulating Walkers")
    print("=" * 60)

    # Walker 1: Libertarian
    walker1 = simulate_walker(
        graph, "libertarian_user",
        accepts=["freedom is the primary", "free markets", "regulations harm", "free speech is absolute"],
        rejects=["equality is the primary", "wealth redistribution", "tech needs regulation"]
    )
    print(f"\n{walker1.summary}")

    # Walker 2: Progressive
    walker2 = simulate_walker(
        graph, "progressive_user",
        accepts=["equality is the primary", "wealth redistribution", "progressive social", "immigration enriches"],
        rejects=["hierarchy is natural", "traditional values", "elites should lead"]
    )
    print(f"\n{walker2.summary}")

    # Walker 3: Aberrant (Post-left type)
    walker3 = simulate_walker(
        graph, "postleft_user",
        accepts=["wealth redistribution", "unions protect", "traditional values", "multipolarity"],
        rejects=["progressive social", "us hegemony", "elites should lead"]
    )
    print(f"\n{walker3.summary}")

    # Detect aberrations for walker 3
    # (Accepting both wealth redistribution AND traditional values is unusual)
    walker3.add_aberration(insertion(
        region="social",
        actual="traditional values",
        description="Holds traditional values despite leftist economics"
    ))
    print(f"\nAberration profile for {walker3.user_id}:")
    print(walker3.aberration_profile.summary)

    # Detect attractors
    print("\n" + "=" * 60)
    print("Detecting Attractors and Voids")
    print("=" * 60)

    detector = AttractorDetector(graph)
    attractors = detector.detect_attractors(min_visits=1, min_strength=0.1)
    print(f"\nFound {len(attractors)} attractors:")
    for a in attractors[:5]:
        print(f"  {a}")

    voids = detector.detect_voids(min_expected=1, min_void_ratio=0.5)
    print(f"\nFound {len(voids)} voids:")
    for v in voids[:5]:
        print(f"  {v}")

    # Suggest outside-basin positions
    print("\n" + "=" * 60)
    print("Ideological Randonautica: Outside-Basin Suggestions")
    print("=" * 60)

    for walker in [walker1, walker2, walker3]:
        suggestions = graph.suggest_outside_basin(walker, n=3)
        print(f"\n{walker.user_id} should explore:")
        for pos in suggestions:
            print(f"  - {pos.claim}")

    # ═══════════════════════════════════════════════════════════
    # ADAPTIVE PROBING: Finding orthogonal dimensions
    # ═══════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Adaptive Probing: Finding Orthogonal Dimensions")
    print("=" * 60)

    prober = AdaptiveProber(graph)

    for walker in [walker1, walker3]:
        print(f"\n{walker.user_id}:")

        # Find most informative positions to probe
        informative = prober.find_most_informative(walker, n=3)
        print("  Most informative probes:")
        for pred in informative:
            pos = graph.get_position(pred.position_id)
            if pos:
                print(f"    - {pos.claim[:50]}... (uncertainty: {pred.uncertainty:.2f})")

        # Generate next probe
        probe = prober.generate_probe(walker)
        if probe:
            print(f"  Next question: {probe.question[:80]}...")
            print(f"  Prediction: {'accept' if probe.prediction.predicted_acceptance > 0.5 else 'reject'}")
            print(f"  Confidence: {1 - probe.prediction.uncertainty:.1%}")

        # Generate priority probe
        priority_probe = prober.generate_priority_probe(walker)
        if priority_probe:
            print(f"  Priority probe: {priority_probe.question[:80]}...")

    # ═══════════════════════════════════════════════════════════
    # PRODUCTIVE TENSION: Weighted Balance Theory
    # ═══════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Productive Tension Analysis")
    print("=" * 60)

    tension_analyzer = TensionAnalyzer(graph)

    for walker in [walker1, walker2, walker3]:
        print(f"\n{walker.user_id}:")

        # Get balance state
        balance = tension_analyzer.get_walker_balance_state(walker)
        print(f"  SGM (balance): {balance.sgm:.2f}")
        print(f"  Extremeness: {balance.extremeness:.2f}")
        print(f"  Constraint: {balance.constraint:.2f}")

        # Find productive tensions
        tensions = tension_analyzer.find_productive_tensions(walker)
        if tensions:
            print(f"  Top tensions:")
            for t in tensions[:3]:
                print(f"    - {t.tension_type.value}: {t.reasoning[:50]}... (score: {t.score:.2f})")

        # Suggest challenges
        challenges = tension_analyzer.suggest_challenge(walker, n=2)
        if challenges:
            print(f"  Suggested challenges:")
            for pos, score in challenges:
                print(f"    - {pos.claim[:50]}... (value: {score:.2f})")

    # ═══════════════════════════════════════════════════════════
    # STANCE EXTRACTION: Mining positions from text
    # ═══════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Stance Extraction from Headlines")
    print("=" * 60)

    extractor = StanceExtractor(graph)

    headlines = [
        "Government regulations threaten small business freedom",
        "Study shows wealth inequality rising despite economic growth",
        "Traditional values under attack from radical progressives",
        "Tech billionaires exploit workers while preaching innovation",
        "Immigration strengthens communities and economy, researchers find",
    ]

    for headline in headlines:
        print(f"\nHeadline: \"{headline}\"")
        sig = extractor.extract(headline)

        if sig.frames:
            print(f"  Frames: {', '.join(f.frame_type.value for f in sig.frames[:3])}")
        if sig.attributions:
            attr = sig.attributions[0]
            valence = "blame" if attr.valence < 0 else "credit" if attr.valence > 0 else "neutral"
            print(f"  Attribution: {attr.target.value} ({valence})")
        if sig.sources:
            print(f"  Source type: {sig.sources[0].source_type.value}")
        if sig.domain_scores:
            top_domain = max(sig.domain_scores.items(), key=lambda x: x[1])
            print(f"  Domain: {top_domain[0]}")

    # ═══════════════════════════════════════════════════════════
    # FORK TREE: The ideological backbone
    # ═══════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Fork Tree: Ideological Backbone")
    print("=" * 60)

    tree = ForkTree()
    print(f"\nLoaded {tree}")

    # Show structure by level
    for level in [ForkLevel.ROOT, ForkLevel.AXIOM, ForkLevel.DOMAIN]:
        forks = tree.get_by_level(level)
        print(f"\n{level.value.upper()} level ({len(forks)} forks):")
        for fork in forks[:3]:
            print(f"  {fork.question[:50]}...")
            print(f"    A: {fork.option_a[:40]}...")
            print(f"    B: {fork.option_b[:40]}...")

    # Add fork tree to graph
    fork_positions = tree.to_graph_positions(graph)
    print(f"\nAdded {fork_positions} positions from fork tree")
    print(f"Graph now has: {len(graph.positions)} positions, {len(graph.edges)} edges")

    # Save fork tree
    fork_path = Path(__file__).parent / "data" / "fork_tree.json"
    tree.save(fork_path)
    print(f"Saved fork tree to {fork_path}")

    # ═══════════════════════════════════════════════════════════
    # PUBLIC FIGURE PROFILING
    # ═══════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Public Figure Profiling: Signal Analysis")
    print("=" * 60)

    profiles = create_example_profiles(tree)

    for profile in profiles:
        print(f"\n{'-' * 40}")
        print(profile.summary)

        # Show specific stances
        print("  Key stances:")
        for fork_id in ["israel", "immigration", "markets", "climate"]:
            if fork_id in profile.stances:
                stance = profile.stances[fork_id]
                fork = tree.forks[fork_id]
                choice_text = fork.option_a if stance.choice == "a" else fork.option_b
                print(f"    {fork.question[:35]}...")
                print(f"      → {choice_text[:50]}... (conf: {stance.confidence:.0%})")

    # ═══════════════════════════════════════════════════════════
    # QUESTIONNAIRE MODE (Interactive Profiling)
    # ═══════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Questionnaire: User Profiling")
    print("=" * 60)

    from graph.forks import generate_questionnaire
    questionnaire = generate_questionnaire(tree, start_level=ForkLevel.AXIOM)
    print(f"\nGenerated questionnaire with {len(questionnaire)} questions")
    print("Sample questions:")
    for fork in questionnaire[:5]:
        print(f"\n  Q: {fork.question}")
        print(f"     A) {fork.option_a[:60]}...")
        print(f"     B) {fork.option_b[:60]}...")

    # ═══════════════════════════════════════════════════════════
    # GRAPH COMPACTION: Finding Decisive Forks
    # ═══════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("Graph Compaction: Decisive Forks & Archetypes")
    print("=" * 60)

    # Analyze structure
    structure = analyze_fork_structure(tree)
    print(f"\nStructure Analysis:")
    print(f"  Total forks: {structure['total_forks']}")
    print(f"  Max depth: {structure['max_depth']}")
    print(f"  Avg branching factor: {structure['avg_branching_factor']:.2f}")
    print(f"  Linearity score: {structure['linearity_score']:.2f}")
    print(f"  Is divergent: {structure['is_divergent']}")

    print(f"\nNull hypothesis test:")
    if structure['is_divergent']:
        print("  REJECTED - The graph is divergent, not linear.")
        print("  People think in genuinely different ways.")
    else:
        print("  NOT REJECTED - The graph is mostly linear.")

    print(f"\nTop decisive forks (predict everything else):")
    for fork_info in structure['top_decisive_forks']:
        print(f"  - {fork_info['question']}")
        print(f"    Decisiveness: {fork_info['decisiveness']:.3f}, Info gain: {fork_info['information_gain']:.3f}")

    print(f"\nMinimal set size: {structure['minimal_set_size']} forks")
    print(f"  (This many questions can predict most of ideology)")

    # Extract archetypes
    compactor = GraphCompactor(tree)
    compactor.analyze()
    archetypes = compactor.extract_archetypes()

    print(f"\nPsychological Archetypes of Political Thinking:")
    for arch in archetypes:
        print(f"\n  {arch.name} (~{arch.population_share:.0%} of population)")
        print(f"    {arch.description}")
        print(f"    Traits: {', '.join(arch.traits)}")
        key_forks = list(arch.fork_choices.items())[:3]
        for fork_id, choice in key_forks:
            fork = tree.forks.get(fork_id)
            if fork:
                chosen = fork.option_a if choice == "a" else fork.option_b
                print(f"    - {fork.question[:30]}... → {chosen[:30]}...")

    # Save graph
    save_path = Path(__file__).parent / "data" / "demo_graph.json"
    graph.save(save_path)
    print(f"\nSaved graph to {save_path}")

    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
