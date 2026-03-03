"""TrustGraph confidence bridge — jsonld-ex Subjective Logic integration."""

from jsonld_ex.confidence_algebra import (
    Opinion,
    cumulative_fuse,
    trust_discount,
    pairwise_conflict,
    conflict_metric,
)
from jsonld_ex.confidence_bridge import combine_opinions_from_scalars
from jsonld_ex.confidence_byzantine import (
    byzantine_fuse,
    ByzantineConfig,
    ByzantineFusionReport,
    cohesion_score,
    opinion_distance,
)
from datetime import datetime, timezone
from typing import Any


def scalar_to_opinion(confidence: float, evidence_weight: float = 1.0) -> Opinion:
    """Convert a scalar confidence [0,1] into a Subjective Logic opinion.

    Args:
        confidence: LLM-assessed confidence in [0, 1].
        evidence_weight: How much evidence this represents (default 1.0).
            Higher values reduce uncertainty (e.g. a meta-analysis = 2.0).
            For individual evidence pieces, always use 1.0.
            Fusion handles combining multiple pieces.

    The mapping:
        - Base uncertainty = 0.3 for weight=1.0 (a single source still
          has meaningful uncertainty, but P can reach 0.85 for conf=1.0)
        - Remaining probability mass split by confidence ratio
        - b + d + u = 1 always holds
    """
    # Uncertainty: decreases with evidence weight, floor at 0.05
    u = max(0.05, 0.3 / evidence_weight)
    remaining = 1.0 - u

    b = remaining * confidence
    d = remaining * (1.0 - confidence)

    return Opinion(belief=b, disbelief=d, uncertainty=u, base_rate=0.5)


def flip_opinion(op: Opinion) -> Opinion:
    """Flip an opinion: swap belief and disbelief.

    Use this when evidence CONTRADICTS a claim. The LLM's confidence
    in the contradiction (high belief) should map to high disbelief
    in the claim itself. Without this flip, supporting and contradicting
    evidence both have high belief and pairwise_conflict sees no disagreement.
    """
    return Opinion(
        belief=op.disbelief,
        disbelief=op.belief,
        uncertainty=op.uncertainty,
        base_rate=op.base_rate
    )


def fuse_evidence(opinions: list[Opinion]) -> Opinion:
    """Fuse multiple opinions using cumulative fusion.

    Each opinion represents one piece of evidence. Cumulative fusion
    reduces uncertainty as more independent sources agree, and balances
    belief/disbelief when sources disagree. This is the correct way
    to combine evidence — NOT inflating source_count per piece.
    """
    if not opinions:
        return Opinion(belief=0.0, disbelief=0.0, uncertainty=1.0, base_rate=0.5)
    if len(opinions) == 1:
        return opinions[0]

    result = opinions[0]
    for op in opinions[1:]:
        result = cumulative_fuse(result, op)
    return result


def fuse_evidence_byzantine(
    opinions: list[Opinion],
    trust_weights: list[float] | None = None,
    threshold: float = 0.15,
    min_agents: int = 2,
) -> dict:
    """Fuse evidence opinions with Byzantine-resistant filtering.

    Uses the "combined" strategy: discord × (1 − trust), which
    prioritizes removal of sources that are both highly discordant
    AND lowly trusted.

    Falls back to regular cumulative fusion when fewer than 3 opinions
    are provided (Byzantine filtering needs at least 3 to be meaningful).

    Args:
        opinions:      List of per-evidence opinions (already trust-discounted
                       and flipped for contradicting evidence).
        trust_weights: Per-opinion source trust scores in [0, 1]. Must match
                       length of opinions. Required for Byzantine filtering;
                       ignored when falling back to regular fusion.
        threshold:     Discord score above which an agent may be removed.
        min_agents:    Never reduce below this many evidence pieces.

    Returns:
        Dict with keys:
            fused:             The final fused Opinion.
            filtered:          List of dicts describing removed evidence
                               (index, opinion, discord_score, reason).
            cohesion:          Cohesion score of surviving evidence [0, 1].
            surviving_indices: Indices of opinions that survived filtering.
            used_byzantine:    Whether Byzantine filtering was applied.
    """
    # Fallback: too few opinions for Byzantine filtering
    if len(opinions) < 3 or trust_weights is None:
        fused = fuse_evidence(opinions)
        return {
            "fused": fused,
            "filtered": [],
            "cohesion": cohesion_score(opinions) if len(opinions) > 1 else 1.0,
            "surviving_indices": list(range(len(opinions))),
            "used_byzantine": False,
        }

    config = ByzantineConfig(
        strategy="combined",
        trust_weights=trust_weights,
        threshold=threshold,
        min_agents=min_agents,
    )

    report: ByzantineFusionReport = byzantine_fuse(opinions, config=config)

    filtered = [
        {
            "index": removal.index,
            "opinion": {
                "belief": round(float(removal.opinion.belief), 4),
                "disbelief": round(float(removal.opinion.disbelief), 4),
                "uncertainty": round(float(removal.opinion.uncertainty), 4),
            },
            "discord_score": round(float(removal.discord_score), 4),
            "reason": removal.reason,
        }
        for removal in report.removed
    ]

    return {
        "fused": report.fused,
        "filtered": filtered,
        "cohesion": round(float(report.cohesion_score), 4),
        "surviving_indices": report.surviving_indices,
        "used_byzantine": True,
    }


def apply_trust_discount(opinion: Opinion, source_trust: float) -> Opinion:
    """Discount an opinion by the trustworthiness of its source.

    source_trust in [0, 1]:
        1.0 = fully trusted (opinion unchanged)
        0.0 = completely untrusted (opinion becomes pure uncertainty)

    This implements Jøsang's trust discount operator: the recommender's
    trust opinion modulates the evidence opinion.
    """
    trust_op = Opinion(
        belief=source_trust,
        disbelief=1.0 - source_trust,
        uncertainty=0.0,
        base_rate=0.5
    )
    return trust_discount(trust_op, opinion)


def detect_conflicts_within_claim(
    supporting_opinions: list[Opinion],
    contradicting_opinions: list[Opinion],
    threshold: float = 0.2
) -> dict | None:
    """Detect conflict WITHIN a single claim between supporting and contradicting evidence.

    This is semantically correct: we compare evidence FOR a claim against
    evidence AGAINST the same claim. Cross-claim comparison is meaningless
    because different claims are about different propositions.

    Returns a conflict report if the two sides disagree above threshold,
    or None if no significant conflict.
    """
    if not supporting_opinions or not contradicting_opinions:
        return None

    # Fuse all supporting evidence into one opinion
    fused_for = fuse_evidence(supporting_opinions)
    # Fuse all contradicting evidence into one opinion
    fused_against = fuse_evidence(contradicting_opinions)

    # Measure conflict between the two sides
    conf = pairwise_conflict(fused_for, fused_against)
    # opinion_distance is a proper metric (d(A,A)=0, triangle inequality)
    # and complements pairwise_conflict for reporting how far apart the sides are
    dist = opinion_distance(fused_for, fused_against)

    if conf > threshold:
        return {
            "conflict_degree": round(float(conf), 4),
            "opinion_distance": round(float(dist), 4),
            "supporting_opinion": {
                "belief": round(float(fused_for.belief), 4),
                "disbelief": round(float(fused_for.disbelief), 4),
                "uncertainty": round(float(fused_for.uncertainty), 4),
            },
            "contradicting_opinion": {
                "belief": round(float(fused_against.belief), 4),
                "disbelief": round(float(fused_against.disbelief), 4),
                "uncertainty": round(float(fused_against.uncertainty), 4),
            },
            "num_supporting": len(supporting_opinions),
            "num_contradicting": len(contradicting_opinions),
        }
    return None


def detect_conflicts(opinions: list[Opinion], threshold: float = 0.3) -> list[dict]:
    """Detect pairwise conflicts among opinions.

    DEPRECATED for cross-claim use. Kept for backward compatibility.
    Prefer detect_conflicts_within_claim() for semantically correct conflict detection.
    """
    conflicts = []
    for i in range(len(opinions)):
        for j in range(i + 1, len(opinions)):
            conf = pairwise_conflict(opinions[i], opinions[j])
            if conf > threshold:
                conflicts.append({
                    "pair": (i, j),
                    "conflict_degree": round(float(conf), 4),
                    "opinion_a": {
                        "belief": round(float(opinions[i].belief), 4),
                        "disbelief": round(float(opinions[i].disbelief), 4),
                        "uncertainty": round(float(opinions[i].uncertainty), 4),
                    },
                    "opinion_b": {
                        "belief": round(float(opinions[j].belief), 4),
                        "disbelief": round(float(opinions[j].disbelief), 4),
                        "uncertainty": round(float(opinions[j].uncertainty), 4),
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


def build_jsonld_claim(
    claim_text: str,
    opinion: Opinion,
    sources: list[dict],
    conflict: dict | None = None,
    cohesion: float | None = None,
    filtered_evidence: list[dict] | None = None,
) -> dict:
    """Build a JSON-LD document for a scored claim.

    Args:
        claim_text:        The claim text.
        opinion:           Fused opinion for the claim.
        sources:           List of source dicts.
        conflict:          Conflict report from detect_conflicts_within_claim().
        cohesion:          Cohesion score of surviving evidence [0, 1].
        filtered_evidence: List of evidence pieces removed by Byzantine filtering.
    """
    proj = float(opinion.belief + opinion.base_rate * opinion.uncertainty)
    doc = {
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
            "ex:projectedProbability": round(proj, 4),
        },
        "prov:wasGeneratedBy": {
            "@type": "prov:Activity",
            "prov:wasAssociatedWith": "TrustGraph Agent",
            "prov:endedAtTime": datetime.now(timezone.utc).isoformat(),
        },
        "ex:sources": sources,
    }
    if conflict:
        doc["ex:conflict"] = conflict
    if cohesion is not None:
        doc["ex:cohesion"] = round(float(cohesion), 4)
        doc["ex:distanceMetric"] = "euclidean"
    if filtered_evidence:
        doc["ex:filteredEvidence"] = filtered_evidence
    return doc


def mean_cohesion(cohesion_scores: list[float]) -> float:
    """Compute mean cohesion across all claims in a report.

    Args:
        cohesion_scores: Per-claim cohesion values from fuse_evidence_byzantine().

    Returns:
        Mean cohesion in [0, 1]. Returns 1.0 for empty list (no claims = no disagreement).
    """
    if not cohesion_scores:
        return 1.0
    return round(sum(cohesion_scores) / len(cohesion_scores), 4)
