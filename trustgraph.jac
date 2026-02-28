"""TrustGraph — Agentic Knowledge Verification with Confidence Algebra.

An AI agent that doesn't just find information — it VERIFIES it.
Uses Jaseci OSP (nodes/edges/walkers) + byLLM + jsonld-ex confidence algebra.
"""

import from byllm.lib { Model }
import from tools.search { web_search }
import from bridge.confidence {
    scalar_to_opinion,
    fuse_evidence,
    apply_trust_discount,
    detect_conflicts,
    opinion_summary,
    build_jsonld_claim
}
import json;
import from datetime { datetime, timezone }

glob llm = Model(model_name="gemini/gemini-2.5-flash");

# ──────────────────────────────────────────────
# Node Types
# ──────────────────────────────────────────────

node Query {
    has text: str;
    has created_at: str = "";
}

node Claim {
    has text: str;
    has confidence: float = 0.0;
    has status: str = "unverified";
    has opinion_data: dict = {};
}

node Source {
    has url: str = "";
    has title: str = "";
    has content: str = "";
    has trust_score: float = 0.5;
    has source_type: str = "web";
}

node Evidence {
    has text: str;
    has supports_claim: bool = True;
    has relevance: float = 0.0;
    has confidence_raw: float = 0.5;
}

node ReportNode {
    has summary: str = "";
    has overall_confidence: float = 0.0;
    has claims_data: list = [];
    has conflicts: list = [];
    has jsonld_output: dict = {};
}

# ──────────────────────────────────────────────
# Edge Types
# ──────────────────────────────────────────────

edge Spawns {}
edge SupportsEdge {}
edge ContradictsEdge {}
edge DerivedFrom {}
edge HasEvidence {}
edge HasClaim {}

# ──────────────────────────────────────────────
# byLLM Functions
# ──────────────────────────────────────────────

"""Given a research question, decompose it into 3-5 specific, verifiable factual claims.
Each claim should be a concrete statement that can be checked against evidence.
Return only the claims as a list of strings."""
def decompose_query(question: str) -> list[str]
    by llm();

"""Given a claim and text from a source, extract the key evidence.
Return a JSON string with fields:
- "evidence": the specific text that supports or contradicts the claim
- "supports": true if the evidence supports the claim, false if it contradicts
- "relevance": a float 0-1 indicating how directly relevant this evidence is
- "confidence": a float 0-1 indicating how confident you are in this assessment"""
def extract_evidence(claim: str, source_text: str) -> str
    by llm();

"""Given a claim and all the evidence collected for and against it,
write a concise 2-3 sentence assessment summarizing the finding.
Include the confidence level and note any conflicts between sources."""
def assess_claim(claim: str, supporting_evidence: list[str], contradicting_evidence: list[str], confidence_score: float) -> str
    by llm();

"""Given a research question and a list of assessed claims with confidence scores,
write a concise executive summary (3-5 sentences) of the overall findings.
Highlight areas of agreement and disagreement among sources."""
def write_summary(question: str, assessed_claims: list[str]) -> str
    by llm();

"""Given a claim, generate a good web search query to find evidence for or against it.
Return just the search query string, optimized for finding research and data."""
def claim_to_search_query(claim: str) -> str
    by llm();

# ──────────────────────────────────────────────
# Source Trust Heuristic
# ──────────────────────────────────────────────

def estimate_source_trust(url: str, title: str) -> float {
    """Heuristic trust scoring based on source domain."""
    url_lower = url.lower();

    # Academic & government sources
    if ".gov" in url_lower or ".edu" in url_lower {
        return 0.9;
    }
    # Major research orgs
    if "nature.com" in url_lower or "sciencedirect" in url_lower
       or "pubmed" in url_lower or "arxiv" in url_lower
       or "nber.org" in url_lower {
        return 0.85;
    }
    # Major news outlets
    if "reuters" in url_lower or "bbc.com" in url_lower
       or "nytimes" in url_lower or "wsj.com" in url_lower
       or "economist" in url_lower {
        return 0.75;
    }
    # General web
    if "wikipedia" in url_lower {
        return 0.6;
    }
    if "reddit.com" in url_lower or "quora.com" in url_lower {
        return 0.35;
    }
    # Default
    return 0.5;
}

# ──────────────────────────────────────────────
# Main Agentic Walker
# ──────────────────────────────────────────────

walker TrustGraphAgent {
    has query_text: str = "";
    has max_search_per_claim: int = 3;
    has report: dict = {};

    can run with entry {
        print(f"\n{'='*60}");
        print(f"  TrustGraph — Agentic Knowledge Verification");
        print(f"{'='*60}");
        print(f"\n  Query: {self.query_text}\n");

        # ── STEP 1: PLAN ──
        print("[1/5] PLAN — Decomposing query into verifiable claims...");
        claims_text = decompose_query(self.query_text);
        print(f"      Found {len(claims_text)} claims to verify.\n");

        # Create Query node
        q = Query(
            text=self.query_text,
            created_at=str(datetime.now(timezone.utc))
        );
        here ++> q;

        # Create Claim nodes
        claim_nodes: list = [];
        for i in range(len(claims_text)) {
            c = Claim(text=claims_text[i]);
            q +>: Spawns :+> c;
            claim_nodes.append(c);
        }

        # ── STEP 2-4: SEARCH + EXTRACT + SCORE per claim ──
        all_opinions: list = [];
        all_conflicts: list = [];
        assessed_claims: list = [];

        for ci in range(len(claim_nodes)) {
            claim = claim_nodes[ci];
            print(f"[2/5] SEARCH — Claim {ci+1}: {claim.text[:70]}...");

            # Generate search query
            search_query = claim_to_search_query(claim.text);
            results = web_search(search_query, self.max_search_per_claim);
            print(f"      Found {len(results)} sources.");

            # ── STEP 3: EXTRACT ──
            print(f"[3/5] EXTRACT — Analyzing evidence...");
            evidence_opinions: list = [];
            supporting: list = [];
            contradicting: list = [];

            for ri in range(len(results)) {
                r = results[ri];
                # Create Source node
                trust = estimate_source_trust(r["url"], r["title"]);
                src = Source(
                    url=r["url"],
                    title=r["title"],
                    content=r["content"][:500],
                    trust_score=trust,
                    source_type="web"
                );

                # Extract evidence using byLLM
                raw = extract_evidence(claim.text, r["content"]);
                # Parse the LLM response
                ev_data = {"evidence": raw, "supports": True, "relevance": 0.5, "confidence": 0.5};
                try {
                    parsed = json.loads(raw);
                    ev_data = parsed;
                } except Exception as e {
                    ev_data = ev_data;
                }

                ev = Evidence(
                    text=str(ev_data.get("evidence", raw))[:300],
                    supports_claim=bool(ev_data.get("supports", True)),
                    relevance=float(ev_data.get("relevance", 0.5)),
                    confidence_raw=float(ev_data.get("confidence", 0.5))
                );

                # Connect: Evidence -> Source
                ev +>: DerivedFrom :+> src;
                # Connect: Claim -> Evidence
                if ev.supports_claim {
                    claim +>: HasEvidence :+> ev;
                    supporting.append(ev.text);
                } else {
                    claim +>: HasEvidence :+> ev;
                    contradicting.append(ev.text);
                }

                # Build opinion with trust discount
                raw_opinion = scalar_to_opinion(ev.confidence_raw, len(results));
                discounted = apply_trust_discount(raw_opinion, trust);
                evidence_opinions.append(discounted);

                print(f"        [{r['title'][:40]}] trust={trust} conf={ev.confidence_raw}");
            }

            # ── STEP 4: SCORE ──
            print(f"[4/5] SCORE — Fusing evidence with Subjective Logic...");
            if len(evidence_opinions) > 0 {
                fused = fuse_evidence(evidence_opinions);
                summary = opinion_summary(fused);
                claim.confidence = summary["projected_probability"];
                claim.status = summary["verdict"];
                claim.opinion_data = summary;
                all_opinions.append(fused);

                print(f"      Result: {summary['verdict']} (P={summary['projected_probability']})");
                print(f"      Opinion: b={summary['belief']} d={summary['disbelief']} u={summary['uncertainty']}");
            } else {
                claim.status = "no_evidence";
                print(f"      No evidence found.");
            }

            # Assess claim
            assessment = assess_claim(
                claim.text,
                supporting,
                contradicting,
                claim.confidence
            );
            assessed_claims.append(
                f"[{claim.status.upper()} P={claim.confidence:.2f}] {claim.text}\n  Assessment: {assessment}"
            );
            print(f"      Assessment: {assessment[:100]}...\n");
        }

        # Detect cross-claim conflicts
        if len(all_opinions) > 1 {
            conflicts = detect_conflicts(all_opinions, 0.15);
            for conf in conflicts {
                all_conflicts.append({
                    "claims": [claim_nodes[conf["pair"][0]].text[:50],
                               claim_nodes[conf["pair"][1]].text[:50]],
                    "conflict_degree": conf["conflict_degree"]
                });
            }
        }

        # ── STEP 5: REPORT ──
        print(f"[5/5] REPORT — Generating summary...\n");
        summary_text = write_summary(self.query_text, assessed_claims);

        # Build JSON-LD output
        jsonld_claims: list = [];
        for ci in range(len(claim_nodes)) {
            c = claim_nodes[ci];
            if len(all_opinions) > ci {
                jc = build_jsonld_claim(c.text, all_opinions[ci], []);
                jsonld_claims.append(jc);
            }
        }

        jsonld_output = {
            "@context": {
                "@vocab": "https://schema.org/",
                "ex": "https://jsonld-ex.org/vocab#",
                "prov": "http://www.w3.org/ns/prov#"
            },
            "@type": "ex:TrustGraphReport",
            "ex:query": self.query_text,
            "ex:generatedAt": str(datetime.now(timezone.utc)),
            "ex:claims": jsonld_claims,
            "ex:conflicts": all_conflicts,
            "ex:summary": summary_text
        };

        # Print final report
        print(f"{'='*60}");
        print(f"  TRUSTGRAPH VERIFICATION REPORT");
        print(f"{'='*60}");
        print(f"\n  Query: {self.query_text}\n");

        print("  CLAIMS:");
        for ci in range(len(assessed_claims)) {
            print(f"    {ci+1}. {assessed_claims[ci]}\n");
        }

        if len(all_conflicts) > 0 {
            print("  CONFLICTS DETECTED:");
            for conf in all_conflicts {
                print(f"    - {conf['claims'][0]}... vs {conf['claims'][1]}...");
                print(f"      Conflict degree: {conf['conflict_degree']}");
            }
            print("");
        }

        print(f"  SUMMARY:\n    {summary_text}\n");
        print(f"{'='*60}");
        print(f"  JSON-LD output: {len(json.dumps(jsonld_output))} bytes");
        print(f"{'='*60}\n");

        self.report = jsonld_output;

        # Save JSON-LD to file
        with open("output.json", "w") as f {
            json.dump(jsonld_output, f, indent=2);
        }
        print(f"  JSON-LD saved to output.json");
    }
}

# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

with entry {
    import sys;
    query = "Is remote work more productive than office work?";

    # Check for query file from UI
    import os;
    if os.path.exists("_query.txt") {
        with open("_query.txt", "r") as f {
            file_query = f.read().strip();
        }
        if len(file_query) > 0 {
            query = file_query;
        }
    }

    # CLI args override
    if len(sys.argv) > 1 {
        query = " ".join(sys.argv[1:]);
    }

    agent = TrustGraphAgent(query_text=query);
    root spawn agent;
}
