# Ideograph

An ideological graph system for mapping belief structures and challenging worldviews.

## Core Concept

Map trajectories, not just coordinates. The motion through idea-space matters more than any snapshot position.

```
           ┌─────────────────────────────────────────┐
           │         MEANING OF LIFE                 │  ROOT
           │   inherent ←───────→ constructed        │
           └────────────────┬────────────────────────┘
                            │
           ┌────────────────┴────────────────┐
           ▼                                 ▼
    ┌──────────────┐                ┌──────────────┐
    │ HUMAN NATURE │                │  KNOWLEDGE   │   META
    │ fallen/good  │                │ trad/reason  │
    └──────┬───────┘                └──────┬───────┘
           │                               │
           ▼                               ▼
    ┌──────────────┐                ┌──────────────┐
    │   FREEDOM    │                │  TRADITION   │   AXIOM
    │  vs EQUALITY │                │ vs PROGRESS  │
    └──────┬───────┘                └──────┬───────┘
           │                               │
     ┌─────┴─────┐                   ┌─────┴─────┐
     ▼           ▼                   ▼           ▼
 ┌───────┐  ┌───────┐           ┌───────┐  ┌───────┐
 │MARKETS│  │ STATE │           │CLIMATE│  │SOCIAL │   DOMAIN
 └───┬───┘  └───┬───┘           └───┬───┘  └───┬───┘
     │          │                   │          │
     ▼          ▼                   ▼          ▼
 ┌───────┐  ┌───────┐           ┌───────┐  ┌───────┐
 │CRYPTO │  │WELFARE│           │ GREEN │  │ABORT- │   POLICY
 │       │  │       │           │ DEAL  │  │ ION   │
 └───────┘  └───────┘           └───────┘  └───────┘
```

## Key Features

### Fork Tree
25 ideological dilemmas structured from ROOT (meaning of life) to POLICY (abortion, guns). Each fork is a binary choice that reveals where someone stands.

### Walker Tracking
Track paths through the graph. A lib-to-trad pipeline looks different from leftist-to-postleft even if they land in similar places.

### Adaptive Probing
Find where predictions fail to discover orthogonal dimensions. If 5 responses are predicted by the first, they're redundant. When prediction fails → orthogonal dimension discovered.

### Weighted Balance Theory
SGM (Signed Graph Measure), evaluative extremeness, imbalanced triad detection. Issue constraint before evaluative extremeness.

### Signal Analysis
Extract ideological positions from text using framing, attribution, and sourcing signals. Profile public figures from their statements.

### Aberrations
What makes someone unique isn't their coordinates—it's their aberrations from the canonical pattern:
- **DELETION**: Missing expected position
- **INSERTION**: Unexpected position present
- **TRANSLOCATION**: Position in wrong region
- **INVERSION**: Opposite of expected

## Usage

```python
from graph.ideograph import IdeologicalGraph
from graph.forks import ForkTree
from graph.profiler import FigureProfiler

# Load fork tree (the backbone)
tree = ForkTree()

# Create graph and populate from forks
graph = IdeologicalGraph()
tree.to_graph_positions(graph)

# Walk a user through the graph
walker = graph.create_walker("user_123")
graph.walk_step(walker, "freedom_vs_equality_b", accepted=True)

# Suggest positions outside their basin (Randonautica)
suggestions = graph.suggest_outside_basin(walker)

# Profile a public figure
profiler = FigureProfiler(tree)
profile = profiler.profile("Tucker Carlson", statements)
```

## Structure

```
ideograph/
├── models/
│   ├── position.py     # Nodes: claim, domain, valence, level
│   ├── edge.py         # IMPLIES, CONTRADICTS, PRIORITIZES_OVER, etc.
│   ├── walker.py       # Path, trajectory, choices
│   └── aberration.py   # DELETION, INSERTION, TRANSLOCATION, INVERSION
│
├── graph/
│   ├── ideograph.py    # Main graph class
│   ├── forks.py        # Fork tree backbone (25 dilemmas)
│   ├── patterns.py     # Canonical patterns (bernie_bro_crypto, etc.)
│   ├── attractors.py   # Attractor/void detection
│   ├── probing.py      # Adaptive probing for orthogonal dimensions
│   ├── tension.py      # Weighted Balance Theory, productive tension
│   ├── stance.py       # Extract positions from text
│   └── profiler.py     # Profile public figures
│
└── demo.py             # Full demonstration
```

## Edge Types

| Type | Symbol | Meaning |
|------|--------|---------|
| IMPLIES | → | If A then typically B |
| CONTRADICTS | ⊗ | A and B rarely coexist |
| PRIORITIZES_OVER | > | When A and B conflict, A wins |
| COLLIDER | ← → | Independent causes, same effect |
| CONFOUNDER | → ← | Hidden common cause |
| MEDIATOR | → ○ → | Intervening variable |

## Credits

Concept from igloominance (igloosha). Weighted Balance Theory from JASSS article on attitude polarization.
