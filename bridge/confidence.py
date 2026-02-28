"""TrustGraph confidence bridge — jsonld-ex Subjective Logic integration."""

import sys
sys.path.insert(0, r"E:\data\code\claudecode\jsonld\jsonld-ex\packages\python\src")

from jsonld_ex.confidence_algebra import (
    Opinion,
    cumulative_fuse,
    trust_discount,
    pairwise_conflict,
    conflict_metric,
)
from jsonld_ex.confidence_bridge import combine_opinions_from_scalars
from datetime import datetime, timezone
from typing import Any


def scalar_to_opinion(confidence: float, source_count: int = 1) -> Opinion:
    """Convert a scalar confidence [0,1] into a Subjective Logic opinion.

    With more sources the uncertainty is lower (more evidence).
    """
    # Uncertainty decreases with more sources
    u = max(0.05, 1.0 / (source_count + 1))
    remaining = 1.0 - u

    if confidence >= 0.5:
        b = remaining * confidence
        d = remaining * (1.0 - confidence)
    else:
        b = remaining * confidence
        d = remaining * (1.0 - confidence)

    return Opinion(belief=b, disbelief=d, uncertainty=u, base_rate=0.5)


def fuse_evidence(opinions: list[Opinion]) -> Opinion:
    """Fuse multiple opinions using cumulative fusion."""
    if not opinions:
        return Opinion(belief=0.0, disbelief=0.0, uncertainty=1.0, base_rate=0.5)
    if len(opinions) == 1:
        return opinions[0]

    result = opinions[0]
    for op in opinions[1:]:
        result = cumulative_fuse(result, op)
    return result


def apply_trust_discount(opinion: Opinion, source_trust: float) -> Opinion:
    """Discount an opinion by the trustworthiness of its source.

    source_trust is in [0,1] — higher means more trusted.
    """
    trust_op = Opinion(
        belief=source_trust,
        disbelief=1.0 - source_trust,
        uncertainty=0.0,
        base_rate=0.5
    )
    return trust_discount(trust_op, opinion)


def detect_conflicts(opinions: list[Opinion], threshold: float = 0.3) -> list[dict]:
    """Detect pairwise conflicts among opinions.

    Returns list of conflict reports for pairs exceeding threshold.
    """
    conflicts = []
    for i in range(len(opinions)):
        for j in range(i + 1, len(opinions)):
            conf = pairwise_conflict(opinions[i], opinions[j])
            if conf > threshold:
                conflicts.append({
                    "pair": (i, j),
                    "conflict_degree": round(conf, 4),
                    "opinion_a": {
                        "belief": round(opinions[i].belief, 4),
                        "disbelief": round(opinions[i].disbelief, 4),
                        "uncertainty": round(opinions[i].uncertainty, 4),
                    },
                    "opinion_b": {
                        "belief": round(opinions[j].belief, 4),
                        "disbelief": round(opinions[j].disbelief, 4),
                        "uncertainty": round(opinions[j].uncertainty, 4),
                    },
                })
    return conflicts


def opinion_summary(op: Opinion) -> dict:
    """Return a human-readable summary of an opinion."""
    proj = float(op.belief + op.base_rate * op.uncertainty)
    return {
        "belief": round(float(op.belief), 4),
        "disbelief": round(float(op.disbelief), 4),
        "uncertainty": round(float(op.uncertainty), 4),
        "base_rate": round(float(op.base_rate), 4),
        "projected_probability": round(proj, 4),
        "verdict": (
            "supported" if proj >= 0.7
            else "contested" if 0.3 < proj < 0.7
            else "refuted"
        ),
    }


def build_jsonld_claim(claim_text: str, opinion: Opinion, sources: list[dict]) -> dict:
    """Build a JSON-LD document for a scored claim."""
    return {
        "@context": {
            "@vocab": "https://schema.org/",
            "ex": "https://jsonld-ex.org/vocab#",
            "prov": "http://www.w3.org/ns/prov#",
        },
        "@type": "ex:VerifiedClaim",
        "ex:claimText": claim_text,
        "ex:confidence": {
            "@type": "ex:SubjectiveOpinion",
            "ex:belief": round(float(opinion.belief), 4),
            "ex:disbelief": round(float(opinion.disbelief), 4),
            "ex:uncertainty": round(float(opinion.uncertainty), 4),
            "ex:baseRate": round(float(opinion.base_rate), 4),
            "ex:projectedProbability": round(float(opinion.belief + opinion.base_rate * opinion.uncertainty), 4),
        },
        "prov:wasGeneratedBy": {
            "@type": "prov:Activity",
            "prov:wasAssociatedWith": "TrustGraph Agent",
            "prov:endedAtTime": datetime.now(timezone.utc).isoformat(),
        },
        "ex:sources": sources,
    }
