# TrustGraph — Agentic Knowledge Verification with Confidence Algebra

> **Most AI agents hallucinate confidently. TrustGraph makes confidence _explicit and mathematical._**

TrustGraph is an agentic AI system that doesn't just find information — it **verifies** it. Given a research question, TrustGraph builds a confidence-scored knowledge graph where every fact has a provenance chain, every source has a trust rating, and conflicting evidence is surfaced and resolved using formal **Subjective Logic** algebra.

![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue)
![Jaseci 0.11](https://img.shields.io/badge/jaseci-0.11-purple)
![jsonld-ex](https://img.shields.io/badge/jsonld--ex-0.6.7-green)

---

## 🚀 Quick Start (2 minutes)

### Prerequisites
- Python 3.12+
- API keys for [Gemini](https://aistudio.google.com/apikey) and [Tavily](https://tavily.com) (free tier)

### Install

```bash
pip install jaseci jsonld-ex streamlit
```

### Set API Keys

**PowerShell:**
```powershell
$env:GEMINI_API_KEY = "your-gemini-key"
$env:TAVILY_API_KEY = "tvly-your-tavily-key"
```

**Bash:**
```bash
export GEMINI_API_KEY="your-gemini-key"
export TAVILY_API_KEY="tvly-your-tavily-key"
```

### Run

**Web UI (recommended for demo):**
```bash
cd velrichack
streamlit run ui/app.py
```

**CLI:**
```bash
cd velrichack
jac run trustgraph.jac
```

---

## 🎯 What It Does

1. **You ask a question** — "Is remote work more productive than office work?"
2. **The agent decomposes it** into 3-5 specific, verifiable claims using byLLM
3. **Searches the web** for evidence (Tavily API) — finds real sources from .gov, .edu, news outlets
4. **Extracts evidence** from each source using byLLM, scoring relevance and confidence
5. **Applies Subjective Logic** (jsonld-ex) — formal opinion tuples (belief, disbelief, uncertainty, base rate) replace vague "I think this is right"
6. **Fuses evidence** mathematically — cumulative fusion across sources, trust discount by source reliability, conflict detection between contradicting findings
7. **Produces a verified report** with per-claim confidence scores, conflict analysis, and full JSON-LD output with PROV-O provenance

### Why This Matters

| Traditional AI Agent | TrustGraph |
|---|---|
| "I'm fairly confident..." | `P=0.817, b=0.733, d=0.100, u=0.167` |
| No source attribution | Full provenance chain per fact |
| Can't distinguish "strong evidence for 50%" from "no evidence at all" | Subjective Logic separates belief from uncertainty |
| Sources treated equally | Trust discount: .gov/.edu weighted higher than Reddit |
| Contradictions hidden | Conflicts detected and quantified |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                       │
│         Query → Live Progress → Scored Report            │
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
│  Opinion Tuples (b,d,u,a) → Cumulative Fusion            │
│  Trust Discount → Conflict Detection → JSON-LD Output    │
├──────────────────────────────────────────────────────────┤
│               External Tools                             │
│  Tavily Web Search │ Gemini LLM (via LiteLLM/byLLM)     │
└──────────────────────────────────────────────────────────┘
```

---

## 🔄 The Agentic Loop

```
User Query
    │
    ▼
[1] PLAN ──────── byLLM decomposes query into verifiable claims
    │
    ▼
[2] SEARCH ────── Tavily web search per claim, creates Source nodes
    │
    ▼
[3] EXTRACT ───── byLLM extracts evidence, scores relevance
    │
    ▼
[4] SCORE ─────── jsonld-ex Subjective Logic:
    │              • scalar → opinion tuple
    │              • trust discount by source reliability
    │              • cumulative fusion across sources
    │              • pairwise conflict detection
    ▼
[5] REPORT ────── byLLM synthesizes findings, outputs JSON-LD
```

**Guardrails:**
- Source trust heuristic (.gov/.edu = 0.9, Reddit = 0.35)
- Confidence thresholds for verdict classification
- Structured LLM output parsing with fallbacks
- Timeout handling on web searches

---

## 📂 Project Structure

```
velrichack/
├── jac.toml                 # Jaseci project config (Gemini model)
├── trustgraph.jac           # Main agent: OSP graph + walker + byLLM
├── bridge/
│   ├── __init__.py
│   └── confidence.py        # jsonld-ex Subjective Logic bridge
├── tools/
│   ├── __init__.py
│   └── search.py            # Tavily web search tool
├── ui/
│   └── app.py               # Streamlit web interface
├── models/
│   └── graph.jac            # OSP node/edge definitions (standalone test)
└── output.json              # Latest JSON-LD verification report
```

---

## 🧩 Where Jac & Jaseci Is Used

| Component | Jaseci Feature | Purpose |
|---|---|---|
| `trustgraph.jac` — Node definitions | **OSP Nodes** | `Query`, `Claim`, `Source`, `Evidence`, `ReportNode` — knowledge graph objects |
| `trustgraph.jac` — Edge definitions | **OSP Edges** | `Spawns`, `SupportsEdge`, `ContradictsEdge`, `DerivedFrom`, `HasEvidence` — typed relationships |
| `trustgraph.jac` — `TrustGraphAgent` | **OSP Walker** | Agentic workflow that traverses the graph, executing Plan→Search→Extract→Score→Report |
| `trustgraph.jac` — `decompose_query()` | **byLLM** (`by llm()`) | LLM-powered query decomposition into verifiable claims |
| `trustgraph.jac` — `extract_evidence()` | **byLLM** (`by llm()`) | LLM-powered evidence extraction and scoring from source text |
| `trustgraph.jac` — `assess_claim()` | **byLLM** (`by llm()`) | LLM-powered claim assessment synthesis |
| `trustgraph.jac` — `write_summary()` | **byLLM** (`by llm()`) | LLM-powered executive summary generation |
| `trustgraph.jac` — `claim_to_search_query()` | **byLLM** (`by llm()`) | LLM-powered search query optimization |
| `jac.toml` | **Jaseci Config** | Project config with byLLM model selection |
| `import from ...` | **Jac-Python Interop** | Jac imports Python modules (bridge, tools) natively |

---

## 🔬 What Makes It Agentic

| Criteria | Implementation |
|---|---|
| **Goal** | Verify claims and produce a trustworthy research brief |
| **Tools** | Web search (Tavily), LLM reasoning (Gemini via byLLM), confidence algebra (jsonld-ex) |
| **Loop** | Plan → Search → Extract → Score → Report (per claim, with cross-claim conflict detection) |
| **Guardrails** | Source trust heuristics, confidence thresholds, structured output parsing with fallbacks |
| **Product Surface** | Streamlit web UI with live progress, confidence visualization, JSON-LD export |

---

## 📦 JSON-LD Output

Every verification produces a machine-readable JSON-LD document with:

- **`@context`** — Schema.org + jsonld-ex + PROV-O vocabularies
- **`ex:claims`** — Each claim with Subjective Logic opinion tuple
- **`ex:conflicts`** — Pairwise conflict degrees between claims
- **`ex:summary`** — LLM-generated executive summary
- **`prov:wasGeneratedBy`** — Provenance attribution per claim

This output is interoperable with the entire semantic web ecosystem: SPARQL queries, RDF stores, SHACL validation, PROV-O provenance graphs.

---

## 🎥 Demo Script (2-3 minutes)

1. **[0:00]** Open Streamlit UI → explain: "TrustGraph doesn't just search — it verifies."
2. **[0:15]** Enter: "Is remote work more productive than office work?"
3. **[0:30]** Watch the live agent log: decomposing claims, searching sources, extracting evidence
4. **[1:00]** Show the metrics: claims verified, supported vs contested, conflicts detected
5. **[1:30]** Expand a claim: show the opinion bar (belief/disbelief/uncertainty), projected probability
6. **[1:45]** Show conflicts: "Source A says +13%, Source B says -5% for collaborative tasks"
7. **[2:00]** Expand JSON-LD output: "Every fact has provenance. Every confidence is mathematically derived."
8. **[2:15]** "The output is valid JSON-LD — queryable with SPARQL, validatable with SHACL."
9. **[2:30]** Close: "Most agents hallucinate confidently. TrustGraph makes confidence explicit."

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Graph Runtime | Jaseci OSP (nodes, edges, walkers) |
| LLM Integration | byLLM (`by llm()`) with Gemini via LiteLLM |
| Confidence Scoring | jsonld-ex Subjective Logic (Jøsang 2016) |
| Provenance | jsonld-ex `@source` + PROV-O vocabulary |
| Web Search | Tavily API |
| Web UI | Streamlit |

---

## 📄 License

MIT

---

## 👥 Team

Built at the Velric Miami Hackathon 2026 — Agentic AI Track.
