"""TrustGraph — OSP Graph Model for Knowledge Verification."""

# --- Node Types ---

node Query {
    has text: str;
    has created_at: str = "";
}

node Claim {
    has text: str;
    has confidence: float = 0.0;
    has status: str = "unverified";
}

node Source {
    has url: str = "";
    has title: str = "";
    has trust_score: float = 0.5;
    has source_type: str = "web";
}

node Evidence {
    has text: str;
    has relevance: float = 0.0;
    has extracted_at: str = "";
}

node Report {
    has summary: str = "";
    has overall_confidence: float = 0.0;
    has generated_at: str = "";
}

# --- Edge Types ---

edge Spawns {}
edge Supports {}
edge Contradicts {}
edge DerivedFrom {}
edge Cites {}
edge Contains {}


# --- Smoke Test Walker ---

walker TestGraph {
    can build with entry {
        q = Query(text="Is remote work more productive?");
        here ++> q;

        c1 = Claim(text="Remote workers report higher productivity");
        c2 = Claim(text="Collaboration suffers in remote settings");
        q +>: Spawns :+> c1;
        q +>: Spawns :+> c2;

        s1 = Source(
            url="https://example.com/study",
            title="Stanford Remote Work Study",
            trust_score=0.85
        );

        e1 = Evidence(text="13% performance increase observed", relevance=0.9);
        e1 +>: DerivedFrom :+> s1;
        e1 +>: Supports :+> c1;

        e2 = Evidence(text="Team collaboration metrics declined 20%", relevance=0.8);
        e2 +>: DerivedFrom :+> s1;
        e2 +>: Supports :+> c2;

        print("TrustGraph OSP model works!");
        print(f"   Query: {q.text}");
        print(f"   Claims: {c1.text}, {c2.text}");
        print(f"   Source: {s1.title} (trust: {s1.trust_score})");
        print(f"   Evidence nodes: 2");
    }
}

with entry {
    root spawn TestGraph();
}
