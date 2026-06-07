import streamlit as st
import sys
import io
from contextlib import redirect_stdout

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* ── base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: #0b0c10;
    color: #e8e6e1;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] { background: transparent; }

/* ── hero title ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero h1 {
    font-family: 'DM Serif Display', serif;
    font-size: clamp(2.8rem, 6vw, 5rem);
    letter-spacing: -0.02em;
    color: #f0ede6;
    margin: 0;
    line-height: 1.05;
}
.hero h1 span { color: #c8a96e; font-style: italic; }
.hero p {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #6b6860;
    margin-top: 0.6rem;
}

/* ── input area ── */
[data-testid="stTextInput"] input {
    background: #13141a !important;
    border: 1px solid #2a2b32 !important;
    border-radius: 6px !important;
    color: #e8e6e1 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 1.05rem !important;
    padding: 0.85rem 1.1rem !important;
    transition: border-color 0.2s;
}
[data-testid="stTextInput"] input:focus {
    border-color: #c8a96e !important;
    box-shadow: 0 0 0 3px rgba(200,169,110,0.12) !important;
}

/* ── primary button ── */
[data-testid="stButton"] button {
    background: #c8a96e !important;
    color: #0b0c10 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    padding: 0.75rem 2rem !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: background 0.2s, transform 0.1s !important;
    width: 100%;
}
[data-testid="stButton"] button:hover {
    background: #dfc080 !important;
    transform: translateY(-1px) !important;
}

/* ── pipeline step cards ── */
.step-card {
    background: #13141a;
    border: 1px solid #1e1f26;
    border-left: 3px solid #c8a96e;
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.step-header {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #c8a96e;
    margin-bottom: 0.5rem;
}
.step-content {
    font-size: 0.93rem;
    color: #c2bfb8;
    line-height: 1.65;
    white-space: pre-wrap;
    word-break: break-word;
}

/* ── report block ── */
.report-block {
    background: #0f1015;
    border: 1px solid #2a2b32;
    border-radius: 10px;
    padding: 2rem 2.2rem;
    margin-top: 0.5rem;
    font-size: 0.96rem;
    line-height: 1.8;
    color: #dedad3;
}

/* ── score badge ── */
.score-badge {
    display: inline-block;
    background: #c8a96e;
    color: #0b0c10;
    font-family: 'DM Mono', monospace;
    font-size: 1.4rem;
    font-weight: 500;
    padding: 0.25rem 0.9rem;
    border-radius: 4px;
    margin-bottom: 0.8rem;
}

/* ── divider ── */
.fancy-divider {
    border: none;
    border-top: 1px solid #1e1f26;
    margin: 2.5rem 0;
}

/* ── spinner text ── */
[data-testid="stStatusWidget"] { color: #c8a96e !important; }

/* ── expander ── */
[data-testid="stExpander"] {
    background: #13141a !important;
    border: 1px solid #1e1f26 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    font-family: 'DM Mono', monospace;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6b6860;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>Research<span>Agent</span></h1>
  <p>Multi-Agent Research System &nbsp;·&nbsp; search · read · write · critique</p>
</div>
""", unsafe_allow_html=True)

# ── Input row ─────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 5, 1.4])
with col2:
    topic = st.text_input(
        label="topic",
        label_visibility="collapsed",
        placeholder="Enter a research topic  e.g. 'Quantum computing breakthroughs 2024'",
        key="topic_input",
    )
with col3:
    run_btn = st.button("Run Pipeline", key="run")

st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)

# ── Pipeline execution ────────────────────────────────────────────────────────
if run_btn and topic.strip():

    # Import here so Streamlit can still load even if deps are absent
    try:
        from pipeline import run_research_pipeline
    except ImportError as e:
        st.error(f"Could not import pipeline: {e}")
        st.stop()

    # ── Step indicators (live feedback) ──────────────────────────────────────
    status_placeholder = st.empty()

    step_ph = {
        1: st.empty(),
        2: st.empty(),
        3: st.empty(),
        4: st.empty(),
    }

    STEP_LABELS = {
        1: "Step 1 — Search Agent",
        2: "Step 2 — Reader Agent",
        3: "Step 3 — Writer Chain",
        4: "Step 4 — Critic Chain",
    }

    # Render skeleton cards immediately
    for i in range(1, 5):
        step_ph[i].markdown(f"""
        <div class="step-card">
          <div class="step-header">{STEP_LABELS[i]}</div>
          <div class="step-content" style="color:#3a3b42;">waiting…</div>
        </div>
        """, unsafe_allow_html=True)

    def render_step(idx, content, done=False):
        border_col = "#4caf85" if done else "#c8a96e"
        text_col   = "#c2bfb8" if done else "#e8e6e1"
        preview = content[:600] + ("…" if len(content) > 600 else "")
        step_ph[idx].markdown(f"""
        <div class="step-card" style="border-left-color:{border_col};">
          <div class="step-header" style="color:{border_col};">{STEP_LABELS[idx]}</div>
          <div class="step-content" style="color:{text_col};">{preview}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Run with spinner ──────────────────────────────────────────────────────
    with st.spinner("Pipeline running…"):

        # Monkey-patch pipeline print() to intercept step outputs live
        import builtins, agents as _agents_mod, pipeline as _pipeline_mod

        _step_outputs = {}
        _current_step = [0]

        _orig_print = builtins.print

        def _capture_print(*args, **kwargs):
            text = " ".join(str(a) for a in args)
            _orig_print(*args, **kwargs)   # keep terminal output

            ltext = text.lower()
            if "step 1" in ltext and "search" in ltext:
                _current_step[0] = 1
            elif "step 2" in ltext and "reader" in ltext:
                _current_step[0] = 2
            elif "step 3" in ltext and "writer" in ltext:
                _current_step[0] = 3
            elif "step 4" in ltext and "critic" in ltext:
                _current_step[0] = 4

        builtins.print = _capture_print

        try:
            state = run_research_pipeline(topic.strip())
        finally:
            builtins.print = _orig_print

    # ── Render final step results ─────────────────────────────────────────────
    render_step(1, state.get("search_results", ""), done=True)
    render_step(2, state.get("scraped_content", ""), done=True)

    # Step 3 — full report in expander
    report = state.get("report", "")
    step_ph[3].markdown(f"""
    <div class="step-card" style="border-left-color:#4caf85;">
      <div class="step-header" style="color:#4caf85;">{STEP_LABELS[3]}</div>
      <div class="step-content" style="color:#c2bfb8;">Report generated — see below ↓</div>
    </div>
    """, unsafe_allow_html=True)

    # Step 4 — critic
    feedback = state.get("feedback", "")
    # extract score line for badge
    score_line = ""
    for line in feedback.splitlines():
        if line.lower().startswith("score"):
            score_line = line.strip()
            break
    step_ph[4].markdown(f"""
    <div class="step-card" style="border-left-color:#4caf85;">
      <div class="step-header" style="color:#4caf85;">{STEP_LABELS[4]}</div>
      <div class="step-content" style="color:#c2bfb8;">{score_line or 'Review complete'}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)

    # ── Report ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:0.72rem;letter-spacing:0.18em;
                text-transform:uppercase;color:#c8a96e;margin-bottom:0.6rem;">
      📄 Full Report
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<div class="report-block">{report}</div>', unsafe_allow_html=True)

    st.markdown("<hr class='fancy-divider'>", unsafe_allow_html=True)

    # ── Critic feedback ───────────────────────────────────────────────────────
    st.markdown("""
    <div style="font-family:'DM Mono',monospace;font-size:0.72rem;letter-spacing:0.18em;
                text-transform:uppercase;color:#c8a96e;margin-bottom:0.6rem;">
      🧠 Critic Feedback
    </div>
    """, unsafe_allow_html=True)

    if score_line:
        score_val = score_line.replace("Score:", "").replace("score:", "").strip()
        st.markdown(f'<div class="score-badge">{score_val}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="report-block">{feedback}</div>', unsafe_allow_html=True)

    # ── Raw state download ────────────────────────────────────────────────────
    import json
    st.download_button(
        label="⬇ Download full state (JSON)",
        data=json.dumps(state, indent=2),
        file_name=f"research_{topic[:40].replace(' ','_')}.json",
        mime="application/json",
    )

elif run_btn and not topic.strip():
    st.warning("Please enter a research topic first.")