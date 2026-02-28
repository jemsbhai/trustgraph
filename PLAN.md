# TrustGraph — Agentic Knowledge Verification with Confidence Algebra

## Velric Miami Hackathon | Agentic AI Track

---

## Executive Summary

**TrustGraph** is an agentic AI system that doesn't just find information — it *verifies* it. Given a research question or set of claims, TrustGraph builds a confidence-scored knowledge graph where every fact has a provenance chain, every source has a trust rating, and conflicting evidence is surfaced and resolved using formal algebra.

**Why this is compelling:** Most AI agents hallucinate confidently. TrustGraph makes confidence *explicit and mathematical* using Subjective Logic (Jøsang 2016), turning vague "I think this is right" into rigorous opinion tuples with belief, disbelief, uncertainty, and base rate.

---

## Hackathon Fit Assessment

| Requirement | How We Meet It |
|---|---|
| **Agentic (goal)** | Verify claims and produce trustworthy research briefs |
| **Agentic (tools)** | Web search, jsonld-ex confidence algebra, LLM extraction |
| **Agentic (loop)** | Plan → Search → Extract → Score → Verify → Report |
| **Agentic (guardrails)** | Confidence thresholds, conflict detection, source validation |
| **Agentic (product surface)** | Web UI with interactive knowledge graph + CLI |
| **Jaseci component** | OSP graph model (nodes/edges/walkers) + byLLM for LLM integration |
| **Demo-able in 2-3 min** | Enter question → watch graph build → see scored report |
| **Real-world useful** | Research verification, fact-checking, due diligence |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Product Surface                            │
│  ┌──────────────┐  ┌──────────────────────────────────────────┐ │
│  │  CLI Demo    │  │  Web UI (Jac full-stack or Streamlit)    │ │
│  │  Quick test  │  │  • Query input                          │ │
│  │              │  │  • Live knowledge graph visualization    │ │
│  │              │  │  • Confidence-scored report output       │ │
│  └──────────────┘  └──────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                  Jaseci / Jac Layer (OSP + byLLM)               │
│                                                                 │
│  NODES (Objects)           EDGES (Relationships)                │
│  ┌──────────┐              ┌─────────────┐                      │
│  │ Query    │─────────────▶│ spawns      │──▶ Claim             │
│  │ Claim    │              │ supports    │                      │
│  │ Source   │              │ contradicts │                      │
│  │ Evidence │              │ derived_from│                      │
│  │ Report   │              │ cites       │                      │
│  └──────────┘              └─────────────┘                      │
│                                                                 │
│  WALKERS (Agentic Workflows)                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ ResearchWalker:  Query → decompose → search → extract   │    │
│  │ VerifyWalker:    Claims → cross-reference → score       │    │
│  │ ReportWalker:    Graph → synthesize → format output     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  byLLM Powers:                                                  │
│  • Claim extraction from text (by llm())                        │
│  • Evidence evaluation and relevance scoring                    │
│  • Conflict analysis between sources                            │
│  • Report generation with citations                             │
├─────────────────────────────────────────────────────────────────┤
│              jsonld-ex Layer (Confidence + Provenance)           │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │ Confidence       │  │ Provenance       │                     │
│  │ Algebra          │  │ Tracking         │                     │
│  │                  │  │                  │                     │
│  │ • Opinion tuples │  │ • @source chains │                     │
│  │   (b,d,u,a)     │  │ • PROV-O interop │                     │
│  │ • Cumulative     │  │ • Timestamps     │                     │
│  │   fusion         │  │ • Agent activity │                     │
│  │ • Trust discount │  │   attribution    │                     │
│  │ • Conflict       │  │                  │                     │
│  │   detection      │  │                  │                     │
│  └──────────────────┘  └──────────────────┘                     │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                     │
│  │ Validation       │  │ Graph Ops        │                     │
│  │                  │  │                  │                     │
│  │ • @shape rules   │  │ • Merge evidence │                     │
│  │ • Claim schema   │  │ • Semantic diff  │                     │
│  │   enforcement    │  │ • Conflict       │                     │
│  │ • Output quality │  │   resolution     │                     │
│  │   gates          │  │                  │                     │
│  └──────────────────┘  └──────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## The Agentic Loop (Detail)

```
User Query: "Is intermittent fasting effective for weight loss?"
          │
          ▼
   ┌──────────────┐
   │  1. PLAN     │  ResearchWalker decomposes query into sub-claims
   │  (byLLM)     │  → "IF reduces caloric intake"
   │              │  → "IF affects metabolic rate"
   │              │  → "IF has long-term adherence data"
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  2. SEARCH   │  Walker traverses to Source nodes
   │  (tools)     │  → PubMed, Google Scholar, web search
   │              │  → Each source gets a trust opinion (jsonld-ex)
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  3. EXTRACT  │  byLLM extracts claims + evidence from sources
   │  (byLLM)     │  → Creates Evidence nodes linked to Claims
   │              │  → Each evidence gets initial confidence
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  4. SCORE    │  jsonld-ex confidence algebra
   │  (jsonld-ex) │  → Cumulative fusion across multiple sources
   │              │  → Trust discount based on source reliability
   │              │  → Conflict detection for contradictions
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  5. VERIFY   │  VerifyWalker checks confidence thresholds
   │  (guardrail) │  → Flag low-confidence claims for more research
   │              │  → Loop back to SEARCH if needed (max 3 cycles)
   └──────┬───────┘
          ▼
   ┌──────────────┐
   │  6. REPORT   │  ReportWalker synthesizes final output
   │  (byLLM +    │  → Structured brief with confidence scores
   │   jsonld-ex) │  → Provenance chain for every claim
   │              │  → Conflict summary where sources disagree
   └──────────────┘
```

---

## Key Differentiators

### 1. Formal Confidence Algebra (not vibes)
Most agents say "I'm fairly confident." TrustGraph uses Subjective Logic opinion tuples `(belief, disbelief, uncertainty, base_rate)` and formal fusion operators. When two sources agree, cumulative fusion mathematically reduces uncertainty. When they disagree, conflict is detected and quantified.

### 2. Jaseci OSP = Natural Fit for Knowledge Graphs
Jaseci's node/edge/walker paradigm *is* a knowledge graph runtime. Claims are nodes. "Supports" and "contradicts" are edges. Walkers are agents that traverse the graph doing work. This isn't bolted on — it's the native paradigm.

### 3. Provenance is First-Class
Every fact in the output links back through a provenance chain: which source said it, when it was accessed, what agent extracted it, what confidence algebra produced the final score. Full PROV-O interop via jsonld-ex.

### 4. The Output is JSON-LD
The knowledge graph itself is valid JSON-LD with jsonld-ex extensions. This means it's interoperable with the entire semantic web ecosystem (SHACL validators, RDF stores, SPARQL queries, etc.).

---

## Implementation Plan

### Phase 1: Foundation (First ~2 hours)

**Step 1 — Project Scaffold**
- Initialize Jac project with `jac.toml`
- Set up Python environment with jsonld-ex dependency
- Create folder structure

**Step 2 — OSP Graph Model (Jac)**
- Define node types: `Query`, `Claim`, `Source`, `Evidence`, `Report`
- Define edge types: `spawns`, `supports`, `contradicts`, `derived_from`, `cites`
- Test basic graph construction

**Step 3 — jsonld-ex Integration Layer (Python)**
- Create bridge module that converts Jaseci graph nodes ↔ jsonld-ex documents
- Wire up confidence algebra (opinion creation, fusion, trust discount)
- Wire up provenance tracking (@source, timestamps)

### Phase 2: Agentic Walkers (Next ~2 hours)

**Step 4 — ResearchWalker**
- byLLM-powered query decomposition
- Web search tool integration
- Claim extraction from search results

**Step 5 — VerifyWalker**
- Cross-reference claims across sources
- Apply confidence algebra (cumulative fusion)
- Detect conflicts and flag low-confidence claims
- Re-search loop for under-confident claims

**Step 6 — ReportWalker**
- Traverse scored graph
- byLLM-powered synthesis
- Output structured JSON-LD report + human-readable summary

### Phase 3: Product Surface (Next ~1-2 hours)

**Step 7 — CLI Demo**
- `jac run trustgraph.jac --query "your question here"`
- Pretty-printed output with confidence scores and sources

**Step 8 — Web UI**
- Option A: Jac full-stack with jac-client (preferred for hackathon points)
- Option B: Streamlit fallback (faster to build)
- Interactive graph visualization (D3.js or vis.js)
- Query input → live progress → scored report

### Phase 4: Polish (Final hour)

**Step 9 — README & Demo**
- Setup instructions (pip install, env vars)
- 2-minute demo walkthrough
- Architecture explanation
- Where Jac/Jaseci is used
- What makes it agentic

**Step 10 — Edge Cases & Guardrails**
- Timeout handling
- Graceful degradation when sources are unavailable
- Maximum loop iterations
- Input validation

---

## File Structure

```
velrichack/
├── jac.toml                    # Jac project config
├── README.md                   # Hackathon submission README
├── PLAN.md                     # This file
│
├── trustgraph.jac              # Main entry point
├── models/
│   ├── graph.jac               # Node and edge definitions (OSP)
│   └── types.jac               # Shared types, enums, semstrings
│
├── walkers/
│   ├── research.jac            # ResearchWalker — decompose + search + extract
│   ├── verify.jac              # VerifyWalker — cross-reference + score
│   └── report.jac              # ReportWalker — synthesize output
│
├── bridge/
│   ├── __init__.py
│   ├── confidence.py           # jsonld-ex confidence algebra integration
│   ├── provenance.py           # jsonld-ex provenance/PROV-O integration
│   ├── converter.py            # Jaseci node ↔ JSON-LD document conversion
│   └── validation.py           # jsonld-ex @shape validation
│
├── tools/
│   ├── search.py               # Web search tool (for walker tool-calling)
│   └── fetch.py                # URL content fetcher
│
├── ui/                         # Web interface
│   ├── app.jac                 # Jac full-stack UI (or Streamlit fallback)
│   └── static/
│       └── graph.js            # D3/vis.js knowledge graph renderer
│
├── examples/
│   ├── demo_query.json         # Pre-built example for live demo
│   └── sample_output.jsonld    # Example JSON-LD output
│
└── tests/
    ├── test_graph.py
    ├── test_confidence.py
    └── test_walkers.py
```

---

## Tech Stack

| Component | Technology | Purpose |
|---|---|---|
| Graph Runtime | Jaseci OSP (nodes/edges/walkers) | Knowledge graph modeling + agentic traversal |
| LLM Integration | byLLM (`by llm()`) | Claim extraction, evaluation, synthesis |
| Confidence Scoring | jsonld-ex Confidence Algebra | Subjective Logic opinions, fusion, conflict |
| Provenance | jsonld-ex @source + PROV-O | Source tracking, attribution chains |
| Validation | jsonld-ex @shape | Schema enforcement on claims/evidence |
| Graph Ops | jsonld-ex merge/diff | Evidence merging, conflict resolution |
| Search | Web search API / SerpAPI | External information retrieval |
| UI | Jac full-stack (jac-client) or Streamlit | Interactive demo surface |
| Visualization | D3.js / vis.js | Knowledge graph rendering |

---

## Demo Script (2-3 minutes)

1. **[0:00]** "TrustGraph doesn't just search — it *verifies*. Let me show you."
2. **[0:15]** Enter query: "Is remote work more productive than office work?"
3. **[0:30]** Show the agent decomposing this into verifiable sub-claims
4. **[0:45]** Watch the knowledge graph build in real-time as sources are found
5. **[1:15]** Point out confidence scores — some claims are high-confidence (multiple sources agree), some are contested (sources conflict)
6. **[1:45]** Show the conflict detail: "Source A (Stanford study, 2023) says +13% productivity. Source B (Microsoft study, 2024) says -5% for collaborative tasks."
7. **[2:00]** Show the final report with per-claim confidence and full provenance
8. **[2:15]** "Every fact traces back to its source. Every confidence score is mathematically derived, not hallucinated. The entire graph is valid JSON-LD you can query with SPARQL."
9. **[2:30]** Show the JSON-LD output briefly — interoperable, machine-readable

---

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Jac learning curve | Use byLLM's Python interface as fallback; keep Jac usage focused on OSP graph modeling |
| jsonld-ex integration complexity | Bridge module isolates complexity; pre-test core functions first |
| Web search rate limits | Pre-cache example results; have offline demo mode |
| Demo time pressure | Build CLI demo FIRST, web UI second; pre-built example queries |
| Scope creep | MVP is: 1 walker loop + confidence scoring + CLI output. Everything else is enhancement |

---

## MVP Definition (Absolute Minimum to Submit)

If time runs short, the MVP is:

1. ✅ Jac file with node/edge/walker definitions (OSP)
2. ✅ One working walker that uses byLLM to extract claims from text
3. ✅ jsonld-ex confidence scoring on extracted claims
4. ✅ CLI output showing claims with confidence scores and sources
5. ✅ README explaining the architecture and demo flow
6. ✅ One pre-built example that works end-to-end

Everything else (web UI, graph visualization, multi-walker orchestration, PROV-O export) is enhancement.

---

## Next Steps

1. **You decide:** Does this direction feel right? Any adjustments to scope or focus?
2. **Install Jaseci:** `pip install jaseci` and verify `jac` CLI works
3. **Start Phase 1:** Scaffold project, define OSP graph model
4. **Iterate together:** We build step by step, testing each component
