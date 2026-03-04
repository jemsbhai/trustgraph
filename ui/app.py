"""TrustGraph — Interactive Web UI for Agentic Knowledge Verification."""

import streamlit as st
import subprocess
import json
import os
import time

st.set_page_config(
    page_title="TrustGraph",
    page_icon="🔍",
    layout="wide",
)

# ── Custom CSS ──
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #888;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    .claim-card {
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        border-left: 5px solid;
    }
    .supported { border-left-color: #00c853; background: #f0fdf4; }
    .contested { border-left-color: #ff9100; background: #fff8e1; }
    .refuted   { border-left-color: #ff1744; background: #fef2f2; }
    .no_evidence { border-left-color: #9e9e9e; background: #f5f5f5; }
    .opinion-bar {
        height: 24px;
        border-radius: 12px;
        display: flex;
        overflow: hidden;
        margin: 8px 0;
    }
    .belief-bar  { background: #00c853; }
    .disbelief-bar { background: #ff1744; }
    .uncertainty-bar { background: #e0e0e0; }
    .conflict-badge {
        display: inline-block;
        background: #ff9100;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .source-chip {
        display: inline-block;
        background: #e8eaf6;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.8rem;
        margin: 2px;
    }
    .metric-box {
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        background: #f8f9fa;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #888;
    }
    .jsonld-section {
        background: #1e1e1e;
        color: #d4d4d4;
        padding: 20px;
        border-radius: 12px;
        font-family: monospace;
        font-size: 0.85rem;
        max-height: 500px;
        overflow-y: auto;
    }
    .cohesion-bar-bg {
        height: 20px;
        border-radius: 10px;
        background: #e0e0e0;
        overflow: hidden;
        margin: 6px 0;
    }
    .cohesion-bar-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.3s;
    }
    .filtered-badge {
        display: inline-block;
        background: #fce4ec;
        color: #c62828;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.8rem;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown('<div class="main-header">🔍 TrustGraph</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Agentic Knowledge Verification with Confidence Algebra — powered by Jaseci OSP + byLLM + jsonld-ex</div>', unsafe_allow_html=True)


def render_opinion_bar(belief, disbelief, uncertainty):
    """Render a visual bar showing belief/disbelief/uncertainty proportions."""
    b_pct = belief * 100
    d_pct = disbelief * 100
    u_pct = uncertainty * 100
    return f"""
    <div class="opinion-bar">
        <div class="belief-bar" style="width:{b_pct}%" title="Belief: {belief:.3f}"></div>
        <div class="disbelief-bar" style="width:{d_pct}%" title="Disbelief: {disbelief:.3f}"></div>
        <div class="uncertainty-bar" style="width:{u_pct}%" title="Uncertainty: {uncertainty:.3f}"></div>
    </div>
    <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#888;">
        <span>🟢 Belief: {belief:.3f}</span>
        <span>🔴 Disbelief: {disbelief:.3f}</span>
        <span>⚪ Uncertainty: {uncertainty:.3f}</span>
    </div>
    """


def verdict_emoji(verdict):
    if verdict == "supported":
        return "✅"
    elif verdict == "contested":
        return "⚠️"
    elif verdict == "refuted":
        return "❌"
    return "❓"


def render_cohesion_bar(cohesion):
    """Render a cohesion bar: green for high agreement, red for low."""
    pct = cohesion * 100
    if cohesion >= 0.8:
        color = "#00c853"
    elif cohesion >= 0.5:
        color = "#ff9100"
    else:
        color = "#ff1744"
    return f"""
    <div style="font-size:0.8rem; color:#888; margin-top:8px;">Source Agreement (Cohesion): {cohesion:.3f}</div>
    <div class="cohesion-bar-bg">
        <div class="cohesion-bar-fill" style="width:{pct}%; background:{color};"></div>
    </div>
    """


# Project root is one level up from ui/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def run_agent(query, num_claims=0, enable_byzantine=True):
    """Run the TrustGraph Jac agent as a subprocess."""
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    cmd = ["jac", "run", "trustgraph.jac"]

    # Write the query and config
    with open(os.path.join(PROJECT_ROOT, "_query.txt"), "w", encoding="utf-8") as f:
        f.write(query)
    with open(os.path.join(PROJECT_ROOT, "_config.json"), "w", encoding="utf-8") as f:
        json.dump({"num_claims": num_claims, "enable_byzantine": enable_byzantine}, f)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=PROJECT_ROOT,
        env=env,
    )

    lines = []
    for line in process.stdout:
        lines.append(line.rstrip())
        yield line.rstrip()

    process.wait()


# ── Sidebar Settings ──
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    enable_byzantine = st.checkbox(
        "Byzantine Filtering",
        value=True,
        help="Remove highly discordant, low-trust sources before fusion. "
             "Uncheck to use standard cumulative fusion and see all evidence.",
    )

# ── Input ──
col1, col2, col3 = st.columns([4, 1, 1])
with col1:
    query = st.text_input(
        "Enter a research question or claim to verify:",
        placeholder="e.g., Is intermittent fasting effective for weight loss?",
        key="query_input",
    )
with col2:
    num_claims = st.slider("Claims", min_value=0, max_value=8, value=0,
                           help="0 = auto (3-5). Set 2-3 for quick checks, 6-8 for deep research.")
with col3:
    st.write("")  # spacing
    st.write("")
    run_clicked = st.button("🚀 Verify", type="primary", use_container_width=True)

# Example queries
st.markdown("**Try:** ", unsafe_allow_html=True)
example_cols = st.columns(3)
examples = [
    "Is remote work more productive than office work?",
    "Does intermittent fasting help with weight loss?",
    "Is nuclear energy safer than solar energy?",
]
for i, ex in enumerate(examples):
    with example_cols[i]:
        if st.button(ex, key=f"ex_{i}", use_container_width=True):
            st.session_state["selected_example"] = ex
            st.rerun()

# Apply selected example
if "selected_example" in st.session_state:
    query = st.session_state.pop("selected_example")
    run_clicked = True

st.divider()

# ── Run Agent ──
if run_clicked and query:
    # Progress section
    progress_container = st.container()
    with progress_container:
        st.markdown("### 🔄 Agent Running...")
        log_area = st.empty()
        progress_bar = st.progress(0)

    log_lines = []
    step_map = {
        "[1/5]": 0.15,
        "[2/5]": 0.35,
        "[3/5]": 0.55,
        "[4/5]": 0.75,
        "[5/5]": 0.90,
    }

    for line in run_agent(query, num_claims, enable_byzantine):
        log_lines.append(line)
        # Update progress based on step markers
        for marker, pct in step_map.items():
            if marker in line:
                progress_bar.progress(pct)
        # Show last 15 lines of log
        display_lines = log_lines[-15:]
        log_area.code("\n".join(display_lines), language="text")

    progress_bar.progress(1.0)
    time.sleep(0.5)

    # ── Load Results ──
    output_path = os.path.join(PROJECT_ROOT, "output.json")
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            report = json.load(f)

        # Clear progress
        progress_container.empty()

        # ── Summary Section ──
        st.markdown("### 📋 Verification Report")

        # Metrics row
        claims = report.get("ex:claims", [])
        conflicts = report.get("ex:conflicts", [])

        supported = sum(1 for c in claims if c.get("ex:confidence", {}).get("ex:projectedProbability", 0) >= 0.7)
        contested = sum(1 for c in claims if 0.3 < c.get("ex:confidence", {}).get("ex:projectedProbability", 0) < 0.7)
        refuted = sum(1 for c in claims if c.get("ex:confidence", {}).get("ex:projectedProbability", 0) <= 0.3)

        mean_coh = report.get("ex:meanCohesion", None)

        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(f"""<div class="metric-box">
                <div class="metric-value">{len(claims)}</div>
                <div class="metric-label">Claims Verified</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-box">
                <div class="metric-value" style="color:#00c853">{supported}</div>
                <div class="metric-label">Supported</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            st.markdown(f"""<div class="metric-box">
                <div class="metric-value" style="color:#ff9100">{contested}</div>
                <div class="metric-label">Contested</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            st.markdown(f"""<div class="metric-box">
                <div class="metric-value" style="color:#ff1744">{len(conflicts)}</div>
                <div class="metric-label">Conflicts</div>
            </div>""", unsafe_allow_html=True)
        with m5:
            coh_display = f"{mean_coh:.3f}" if mean_coh is not None else "N/A"
            coh_color = "#00c853" if mean_coh and mean_coh >= 0.8 else "#ff9100" if mean_coh and mean_coh >= 0.5 else "#ff1744"
            st.markdown(f"""<div class="metric-box">
                <div class="metric-value" style="color:{coh_color}">{coh_display}</div>
                <div class="metric-label">Mean Cohesion</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")

        # Summary
        summary = report.get("ex:summary", "")
        if summary:
            st.info(f"**Executive Summary:** {summary}")

        st.markdown("")

        # ── Claims Detail ──
        st.markdown("### 🎯 Claims Analysis")

        for i, claim in enumerate(claims):
            conf = claim.get("ex:confidence", {})
            prob = conf.get("ex:projectedProbability", 0)
            belief = conf.get("ex:belief", 0)
            disbelief = conf.get("ex:disbelief", 0)
            uncertainty = conf.get("ex:uncertainty", 0)

            if prob >= 0.7:
                verdict = "supported"
            elif prob > 0.3:
                verdict = "contested"
            else:
                verdict = "refuted"

            emoji = verdict_emoji(verdict)
            claim_text = claim.get("ex:claimText", "Unknown claim")

            with st.expander(f"{emoji} Claim {i+1}: {claim_text[:80]}... — **P={prob:.3f}** ({verdict})", expanded=(i == 0)):
                st.markdown(f"**Full Claim:** {claim_text}")
                st.markdown(render_opinion_bar(belief, disbelief, uncertainty), unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Projected Probability", f"{prob:.3f}")
                with c2:
                    st.metric("Verdict", verdict.upper())

                # Cohesion bar
                claim_cohesion = claim.get("ex:cohesion", None)
                if claim_cohesion is not None:
                    st.markdown(render_cohesion_bar(claim_cohesion), unsafe_allow_html=True)

                # Sources
                sources = claim.get("ex:sources", [])
                if sources:
                    st.markdown("**Sources:**")
                    for s in sources:
                        title = s.get("title", "Unknown")
                        url = s.get("url", "")
                        trust = s.get("trust_score", 0)
                        supports = s.get("supports", True)
                        icon = "✅" if supports else "❌"
                        label = "supports" if supports else "contradicts"
                        if url:
                            st.markdown(
                                f'<span class="source-chip">{icon} <a href="{url}">{title}</a> '
                                f'(trust: {trust:.2f}, {label})</span>',
                                unsafe_allow_html=True
                            )

                # Filtered evidence (Byzantine removal)
                filtered = claim.get("ex:filteredEvidence", [])
                if filtered:
                    st.markdown("**Filtered Evidence (Byzantine):**")
                    for flt in filtered:
                        reason = flt.get("reason", "unknown")
                        discord = flt.get("discord_score", 0)
                        st.markdown(
                            f'<span class="filtered-badge">🚫 Source #{flt.get("index", "?")} removed — '
                            f'discord: {discord:.3f}, {reason}</span>',
                            unsafe_allow_html=True
                        )

        # ── Conflicts ──
        if conflicts:
            st.markdown("### ⚡ Evidence Conflicts")
            for conf in conflicts:
                claim_text = conf.get("claim", "")
                degree = conf.get("conflict_degree", 0)
                dist = conf.get("opinion_distance", None)
                n_sup = conf.get("num_supporting", 0)
                n_con = conf.get("num_contradicting", 0)
                dist_str = f" | distance: {dist:.3f}" if dist is not None else ""
                st.warning(
                    f"**Conflict (degree: {degree:.3f}{dist_str})** in: \"{claim_text}\"\n\n"
                    f"{n_sup} source(s) support vs {n_con} source(s) contradict"
                )

        # ── JSON-LD Output ──
        st.markdown("### 📦 JSON-LD Output (Machine-Readable)")
        with st.expander("View JSON-LD (interoperable with SPARQL, RDF, PROV-O)"):
            st.json(report)

        # ── Agent Log ──
        with st.expander("📜 Agent Execution Log"):
            st.code("\n".join(log_lines), language="text")

    else:
        st.error("Agent did not produce output. Check the execution log above.")

elif not query and run_clicked:
    st.warning("Please enter a research question.")

# ── Footer ──
st.divider()
st.markdown("""
<div style="text-align:center; color:#888; font-size:0.85rem;">
    <b>TrustGraph</b> — Velric Miami Hackathon 2026 | 
    Jaseci OSP + byLLM + jsonld-ex Confidence Algebra (Subjective Logic) |
    Every fact is mathematically verified, not hallucinated.
</div>
""", unsafe_allow_html=True)
