# 🔍 TrustGraph

### Agentic AI that verifies, not hallucinates: powered by Subjective Logic confidence algebra

> An agentic knowledge verification system that mathematically scores every claim using Jaseci OSP (nodes/edges/walkers), byLLM, jsonld-ex Subjective Logic, and Tavily web search. Built at Velric Miami Hackathon 2026.

---

## The Problem: AI Hallucinations Are Dangerous

Every major AI system today has the same fatal flaw: **it states opinions as facts and guesses with the same confidence as knowledge.**

When ChatGPT says "studies show remote work increases productivity by 13%," you have no way to know:

- Is that number from one study or twenty?
- Do other studies contradict it?
- Was the source a peer-reviewed journal or a blog post?
- How much of that answer is evidence vs. how much is the model filling in gaps?

This isn't a minor UX issue. **Hallucinations in AI-generated research, due diligence, medical advice, legal analysis, and financial decisions cause real harm.** Organizations are making million-dollar decisions based on AI outputs that look authoritative but have no mathematical grounding.

The root cause is simple: traditional AI agents treat confidence as a single number (or worse, don't track it at all). A scalar `confidence = 0.5` is meaningless: it could mean "strong evidence that the probability is 50%" or "we have literally no evidence and are guessing." These are fundamentally different situations that require fundamentally different responses.

---

## The Solution: TrustGraph

TrustGraph is an **agentic AI system that doesn't just find information, it verifies it** using formal mathematics from Subjective Logic (Jøsang 2016).

Every fact in a TrustGraph report comes with:

- **A mathematical opinion tuple** `(belief, disbelief, uncertainty, base_rate)` : not a vibe, not a guess, a formally computed score
- **A provenance chain** : which source said it, when, and how trustworthy that source is
- **Conflict detection** : where sources disagree, quantified to a precise degree
- **Trust-weighted evidence fusion** : .gov and .edu sources count more than Reddit posts

### How It Works

```
You ask: "Is remote work more productive than office work?"
                    │
                    ▼
        ┌───────────────────────┐
   [1]  │  PLAN                 │  Agent decomposes your question into
        │  (byLLM + Gemini)     │  3-5 specific, verifiable claims
        └───────────┬───────────┘
                    ▼
        ┌───────────────────────┐
   [2]  │  SEARCH               │  Searches the web for each claim
        │  (Tavily API)         │  using optimized queries
        └───────────┬───────────┘
                    ▼
        ┌───────────────────────┐
   [3]  │  EXTRACT              │  LLM reads each source and extracts
        │  (byLLM + Gemini)     │  evidence for/against with relevance
        └───────────┬───────────┘
                    ▼
        ┌───────────────────────┐
   [4]  │  SCORE                │  Subjective Logic algebra:
        │  (jsonld-ex)          │  • Scalar → opinion tuple (b,d,u,a)
        │                       │  • Trust discount by source quality
        │                       │  • Cumulative fusion across sources
        │                       │  • Pairwise conflict detection
        └───────────┬───────────┘
                    ▼
        ┌───────────────────────┐
   [5]  │  REPORT               │  Synthesized brief with per-claim
        │  (byLLM + JSON-LD)    │  confidence, conflicts, provenance
        └───────────────────────┘
```

---

## Why Subjective Logic Changes Everything

Traditional AI confidence is a single number. **Subjective Logic uses four numbers, and that makes all the difference.**

### The Opinion Tuple: `ω = (belief, disbelief, uncertainty, base_rate)`

| Component | Meaning | Why It Matters |
|---|---|---|
| **Belief** (b) | Evidence FOR the claim | How much evidence supports this |
| **Disbelief** (d) | Evidence AGAINST the claim | How much evidence contradicts this |
| **Uncertainty** (u) | ABSENCE of evidence | How much we simply don't know |
| **Base Rate** (a) | Prior probability | What we'd assume with zero evidence |

**Constraint:** `b + d + u = 1` : your total epistemic state is always fully accounted for.

### Why This Matters: The Same Number Means Different Things

| Scenario | Scalar Confidence | Subjective Logic Opinion |
|---|---|---|
| "Strong evidence it's 50/50" | 0.5 | b=0.45, d=0.45, **u=0.10**, a=0.5 |
| "We have no idea" | 0.5 | b=0.00, d=0.00, **u=1.00**, a=0.5 |
| "Sources violently disagree" | 0.5 | b=0.40, d=0.40, **u=0.20**, a=0.5 |

A traditional agent would treat all three as identical. TrustGraph distinguishes them, and that distinction drives completely different downstream decisions:

- **Low uncertainty, balanced belief/disbelief** → "The evidence genuinely shows this is a toss-up"
- **High uncertainty** → "We need more sources before making a call"
- **High conflict** → "Sources disagree: here's exactly where and by how much"

### Evidence Fusion: More Sources = Less Uncertainty

When multiple sources agree, **cumulative fusion** mathematically reduces uncertainty:

```
Source 1 alone:     b=0.567, d=0.100, u=0.333  →  P=0.733
Source 2 alone:     b=0.675, d=0.075, u=0.250  →  P=0.800

Fused (1 + 2):      b=0.733, d=0.100, u=0.167  →  P=0.817
                                        ↑ uncertainty dropped by 50%
```

This is exactly how human reasoning works: each independent source that agrees shrinks our uncertainty.

### Trust Discount: Not All Sources Are Equal

A .gov study and a Reddit comment shouldn't carry equal weight. TrustGraph applies **trust discount** : an opinion from an untrusted source gets its belief diluted and its uncertainty inflated:

```
High-trust source (0.9):  b=0.510, d=0.090, u=0.400  →  P=0.710 (verdict: SUPPORTED)
Low-trust source  (0.3):  b=0.045, d=0.105, u=0.850  →  P=0.470 (verdict: CONTESTED)
```

Same raw evidence, but the low-trust source produces a much more uncertain opinion. The system knows it shouldn't rely on that source alone.

### Conflict Detection: Where Sources Disagree

When two opinions point in opposite directions, TrustGraph detects and quantifies the conflict:

```
Source A says: "Remote work increases productivity" (b=0.7, d=0.1)
Source B says: "Remote work decreases productivity" (b=0.1, d=0.7)

Conflict degree: 0.84 (severe disagreement)
```

This surfaces in the report as a flagged conflict: the user sees exactly where the evidence is split and can investigate further.

---

## What This Means For Real-World Use Cases

| Use Case | Without TrustGraph | With TrustGraph |
|---|---|---|
| **Research & Due Diligence** | "Studies suggest X" (which studies? how many? do they agree?) | "3 sources support X (P=0.82), 1 contradicts (conflict=0.34), uncertainty=0.12" |
| **Fact-Checking** | "This claim is mostly true" | "Belief=0.73, Disbelief=0.10, Uncertainty=0.17 : supported with high confidence from .gov and .edu sources" |
| **Medical Research** | "Treatment A may be effective" | "4 peer-reviewed sources fuse to P=0.89, but 1 contradicts (conflict=0.41) : flag for human review" |
| **Legal Analysis** | "Precedent suggests..." | Per-claim provenance chain, source trust ratings, formal conflict quantification |
| **Business Intelligence** | "Market trends indicate..." | Mathematically weighted evidence from multiple sources with uncertainty quantified |

The key insight: **TrustGraph doesn't eliminate uncertainty : it makes uncertainty visible and mathematically precise.** This lets humans make better decisions because they know exactly what the AI knows, what it doesn't know, and where the evidence disagrees.

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **Gemini API Key** (free) - [Get one here](https://aistudio.google.com/apikey)
- **Tavily API Key** (free, 1000 searches/month) - [Get one here](https://tavily.com)

### 1. Clone & Install

```bash
git clone https://github.com/jemsbhai/trustgraph.git
cd trustgraph
pip install jaseci jsonld-ex streamlit
```

### 2. Set Environment Variables

**PowerShell (Windows):**
```powershell
$env:GEMINI_API_KEY = "your-gemini-api-key"
$env:TAVILY_API_KEY = "tvly-your-tavily-api-key"
```

**Bash (Mac/Linux):**
```bash
export GEMINI_API_KEY="your-gemini-api-key"
export TAVILY_API_KEY="tvly-your-tavily-api-key"
```

### 3. Run

**Web UI (recommended, best for demos):**
```bash
streamlit run ui/app.py
```
Opens a browser at `http://localhost:8501` with an interactive dashboard.

**CLI (quick test):**
```bash
jac run trustgraph.jac
```
Runs the default query and prints results to terminal. Edit `_query.txt` to change the question.


---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                       │
│   Query Input → Live Agent Log → Confidence Dashboard    │
│   Opinion Bars → Conflict Detection → JSON-LD Export     │
├──────────────────────────────────────────────────────────┤
│              Jaseci / Jac Layer (OSP + byLLM)            │
│                                                          │
│  NODES              EDGES              WALKER            │
│  Query              Spawns             TrustGraphAgent    │
│  Claim              SupportsEdge       • Plan (decompose)│
│  Source             ContradictsEdge    • Search (Tavily)  │
│  Evidence           DerivedFrom        • Extract (byLLM)  │
│  ReportNode         HasEvidence        • Score (jsonld-ex)│
│                     HasClaim           • Report (byLLM)   │
├──────────────────────────────────────────────────────────┤
│            jsonld-ex Confidence Algebra Bridge            │
│                                                          │
│  scalar_to_opinion() → fuse_evidence()                   │
│  apply_trust_discount() → detect_conflicts()             │
│  opinion_summary() → build_jsonld_claim()                │
├──────────────────────────────────────────────────────────┤
│               External Tools                             │
│  Tavily Web Search    │    Gemini LLM (via byLLM)        │
└──────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
trustgraph/
├── jac.toml                 # Jaseci project config (Gemini model)
├── trustgraph.jac           # Core agent: OSP graph model + walker + 5 byLLM functions
├── bridge/
│   ├── __init__.py
│   └── confidence.py        # jsonld-ex Subjective Logic integration
│                             #   scalar_to_opinion, fuse_evidence,
│                             #   apply_trust_discount, detect_conflicts,
│                             #   opinion_summary, build_jsonld_claim
├── tools/
│   ├── __init__.py
│   └── search.py            # Tavily web search tool
├── models/
│   └── graph.jac            # Standalone OSP node/edge test
├── ui/
│   └── app.py               # Streamlit dashboard
├── examples/
│   └── sample_output.jsonld # Example JSON-LD verification report
├── README.md
└── PLAN.md                  # Original architecture plan
```

---

## 🧩 Where Jac & Jaseci Is Used

This project uses Jaseci extensively, not as a thin wrapper, but as the **core runtime for the entire agent**.

### OSP Graph Model (Object-Spatial Programming)

The knowledge graph is defined using Jac's native node/edge primitives:

**Nodes** — the objects in our verification graph:
- `Query` — the user's research question
- `Claim` — a specific verifiable statement decomposed from the query
- `Source` — a web source with URL, title, and trust score
- `Evidence` — extracted text from a source, with relevance and confidence
- `ReportNode` — the final synthesized report

**Edges** — typed relationships between nodes:
- `Spawns` — Query → Claim (decomposition)
- `SupportsEdge` / `ContradictsEdge` — Evidence → Claim (for/against)
- `DerivedFrom` — Evidence → Source (provenance)
- `HasEvidence` — Claim → Evidence (collection)
- `HasClaim` — Report → Claim (aggregation)

### Walker (Agentic Workflow)

`TrustGraphAgent` is a Jac walker, an autonomous agent that traverses the graph executing the Plan→Search→Extract→Score→Report loop. The walker:
- Creates nodes and edges as it discovers information
- Carries state (`query_text`, `max_search_per_claim`, `report`)
- Orchestrates the full agentic pipeline in a single graph traversal

### byLLM Integration (5 LLM-powered functions)

All LLM calls use Jac's `by llm()` declaration: no prompt engineering, no API boilerplate:

```jac
"""Given a research question, decompose it into 3-5 specific verifiable claims."""
def decompose_query(question: str) -> list[str]
    by llm();
```

The five byLLM functions:
1. `decompose_query()` — breaks a question into verifiable claims
2. `extract_evidence()` — analyzes source text for evidence
3. `assess_claim()` — synthesizes an assessment from collected evidence
4. `write_summary()` — generates an executive summary
5. `claim_to_search_query()` — optimizes a claim for web search

### Jac-Python Interop

Jac natively imports our Python modules:
```jac
import from bridge.confidence { scalar_to_opinion, fuse_evidence, ... }
import from tools.search { web_search }
```

This lets us use the full jsonld-ex library (pure Python) directly from Jac code.

---

## 🔬 What Makes It Agentic

| Criteria | Implementation |
|---|---|
| **Goal** | Verify claims and produce a mathematically grounded research brief |
| **Tools** | Web search (Tavily), LLM reasoning (Gemini via byLLM), confidence algebra (jsonld-ex Subjective Logic) |
| **Loop** | Plan → Search → Extract → Score → Report : executed per claim, with cross-claim conflict detection |
| **Guardrails** | Source trust heuristics (.gov=0.9, Reddit=0.35), confidence thresholds, structured output parsing with fallbacks, search timeouts |
| **Product Surface** | Streamlit web UI with live progress streaming, confidence visualization, JSON-LD export |

---

## 📦 JSON-LD Output

Every verification produces a **machine-readable JSON-LD document** conforming to Schema.org, jsonld-ex, and PROV-O vocabularies:

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "ex": "https://jsonld-ex.org/vocab#",
    "prov": "http://www.w3.org/ns/prov#"
  },
  "@type": "ex:TrustGraphReport",
  "ex:query": "Is remote work more productive?",
  "ex:claims": [
    {
      "@type": "ex:VerifiedClaim",
      "ex:claimText": "Remote workers report higher output...",
      "ex:confidence": {
        "@type": "ex:SubjectiveOpinion",
        "ex:belief": 0.733,
        "ex:disbelief": 0.100,
        "ex:uncertainty": 0.167,
        "ex:baseRate": 0.5,
        "ex:projectedProbability": 0.817
      },
      "prov:wasGeneratedBy": {
        "@type": "prov:Activity",
        "prov:wasAssociatedWith": "TrustGraph Agent"
      }
    }
  ],
  "ex:conflicts": [...],
  "ex:summary": "..."
}
```

This output is interoperable with the entire semantic web ecosystem: SPARQL queries, RDF stores, SHACL validation, OWL reasoning, PROV-O provenance graphs.

---

## 🛠️ Tech Stack

| Component | Technology | Role |
|---|---|---|
| **Graph Runtime** | Jaseci OSP (nodes, edges, walkers) | Knowledge graph modeling + agentic traversal |
| **LLM Integration** | byLLM (`by llm()`) + Gemini via LiteLLM | Claim decomposition, evidence extraction, synthesis |
| **Confidence Scoring** | jsonld-ex Subjective Logic (Jøsang 2016) | Opinion tuples, cumulative fusion, trust discount, conflict detection |
| **Provenance** | jsonld-ex + PROV-O vocabulary | Source tracking, attribution chains |
| **Web Search** | Tavily API | Real-time web evidence retrieval |
| **Web UI** | Streamlit | Interactive dashboard with live progress |

---

## 📚 References

- Jøsang, A. (2016). *Subjective Logic: A Formalism for Reasoning Under Uncertainty.* Springer.
- jsonld-ex: JSON-LD 1.2 Extensions for AI/ML : [PyPI](https://pypi.org/project/jsonld-ex/) | [GitHub](https://github.com/jemsbhai/jsonld-ex)
- Jaseci & Jac : [docs.jaseci.org](https://docs.jaseci.org) | [GitHub](https://github.com/jaseci-labs/jaseci)
- W3C PROV-O : [Provenance Ontology](https://www.w3.org/TR/prov-o/)

---

## 📄 License

MIT

---

## 👥 Team

Built at the **Velric Miami Hackathon 2026** by Fifi and Muntaser — Agentic AI Track.
