"""
Streamlit UI for the multi-agent research pipeline.

Run with:
    streamlit run app.py

Mirrors the logic in pipeline.py (search -> read -> write -> critique) and
streams progress into the UI stage by stage, styled as a "research dossier":
each run is a case file that moves through Evidence -> Deep Read -> Draft ->
Review, ending in a stamped report.
"""

import streamlit as st
from agents import build_search_agent, build_reader_agent, writer_chain, critic_chain


# ----------------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="The Research Dossier",
    page_icon="🗂️",
    layout="wide",
)

# ----------------------------------------------------------------------------
# Theme — "research dossier": ink-navy ground, parchment report card,
# brass/gold stamp accent, serif display type for the case file voice,
# mono type for status/metadata (the paper-trail details).
# ----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,500&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --ink: #10161D;
        --ink-2: #1A222C;
        --ink-3: #232D39;
        --line: #33404D;
        --parchment: #F4EEDD;
        --parchment-2: #ECE3CB;
        --gold: #C9A24B;
        --gold-soft: #8C7230;
        --text-light: #E9E4D6;
        --text-muted: #94A0AC;
        --text-dark: #2A2620;
    }

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: var(--ink);
        color: var(--text-light);
    }

    /* ---- Hero ---- */
    .dossier-kicker {
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.18em;
        font-size: 0.72rem;
        color: var(--gold);
        text-transform: uppercase;
        border: 1px solid var(--gold-soft);
        display: inline-block;
        padding: 3px 10px;
        border-radius: 3px;
        margin-bottom: 14px;
    }
    .dossier-title {
        font-family: 'Fraunces', serif;
        font-weight: 600;
        font-size: 2.6rem;
        line-height: 1.15;
        color: var(--text-light);
        margin: 0 0 6px 0;
    }
    .dossier-title em {
        color: var(--gold);
        font-style: italic;
    }
    .dossier-sub {
        color: var(--text-muted);
        font-size: 1.02rem;
        max-width: 640px;
        margin-bottom: 6px;
    }
    .dossier-rule {
        border: none;
        border-top: 1px solid var(--line);
        margin: 22px 0 26px 0;
    }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: var(--ink-2);
        border-right: 1px solid var(--line);
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-light);
    }
    .side-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--gold);
        margin-bottom: 8px;
    }
    .side-step {
        display: flex;
        gap: 10px;
        align-items: baseline;
        padding: 7px 0;
        border-bottom: 1px dashed var(--line);
        font-size: 0.9rem;
    }
    .side-step:last-child { border-bottom: none; }
    .side-step .n {
        font-family: 'JetBrains Mono', monospace;
        color: var(--gold);
        font-size: 0.78rem;
    }

    /* ---- Inputs ---- */
    .stTextInput input {
        background: var(--ink-2) !important;
        color: var(--text-light) !important;
        border: 1px solid var(--line) !important;
        border-radius: 4px !important;
        font-family: 'Inter', sans-serif;
        padding: 12px 14px !important;
    }
    .stTextInput input:focus {
        border-color: var(--gold) !important;
        box-shadow: 0 0 0 1px var(--gold) !important;
    }
    .stTextInput label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-muted) !important;
    }

    /* ---- Buttons ---- */
    .stButton > button {
        background: var(--gold) !important;
        color: var(--ink) !important;
        border: none !important;
        border-radius: 3px !important;
        font-weight: 600 !important;
        letter-spacing: 0.03em;
        padding: 0.55rem 1.4rem !important;
        transition: transform 0.12s ease, background 0.12s ease;
    }
    .stButton > button:hover {
        background: #D9B662 !important;
        transform: translateY(-1px);
    }
    .stButton > button:disabled {
        background: var(--ink-3) !important;
        color: var(--text-muted) !important;
    }
    .stDownloadButton > button {
        background: transparent !important;
        color: var(--gold) !important;
        border: 1px solid var(--gold-soft) !important;
        border-radius: 3px !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--gold) !important;
        color: #D9B662 !important;
    }

    /* ---- Status widgets (pipeline stages) ---- */
    div[data-testid="stExpander"], div[data-testid="stStatusWidget"], [data-testid="stStatus"] {
        background: var(--ink-2) !important;
        border: 1px solid var(--line) !important;
        border-left: 3px solid var(--gold) !important;
        border-radius: 4px !important;
    }
    div[data-testid="stExpander"] summary, [data-testid="stStatus"] p {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.88rem !important;
        color: var(--text-light) !important;
    }

    /* ---- Section headers ---- */
    h3 {
        font-family: 'Fraunces', serif !important;
        color: var(--text-light) !important;
    }

    /* ---- Parchment report card ---- */
    .parchment {
        background: var(--parchment);
        color: var(--text-dark);
        border-radius: 6px;
        padding: 34px 40px;
        margin-top: 10px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
        position: relative;
        border-top: 4px solid var(--gold);
    }
    .parchment h1, .parchment h2, .parchment h3, .parchment h4 {
        font-family: 'Fraunces', serif !important;
        color: var(--text-dark) !important;
    }
    .parchment p, .parchment li {
        font-family: 'Inter', sans-serif;
        line-height: 1.65;
    }
    .stamp {
        position: absolute;
        top: 22px;
        right: 30px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        color: var(--gold-soft);
        border: 2px solid var(--gold-soft);
        border-radius: 50%;
        width: 78px;
        height: 78px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        transform: rotate(8deg);
        opacity: 0.85;
        text-transform: uppercase;
    }

    /* ---- Critic / feedback card ---- */
    .critic-card {
        background: var(--ink-2);
        border: 1px solid var(--line);
        border-left: 3px solid #7A8B99;
        border-radius: 4px;
        padding: 22px 26px;
        margin-top: 14px;
        color: var(--text-light);
    }
    .critic-card p, .critic-card li { line-height: 1.6; }

    /* ---- Footer note ---- */
    .foot-note {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--text-muted);
        letter-spacing: 0.05em;
        margin-top: 40px;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ----------------------------------------------------------------------------
# Hero
# ----------------------------------------------------------------------------
st.markdown('<div class="dossier-kicker">Agent Pipeline — Search · Read · Write · Review</div>', unsafe_allow_html=True)
st.markdown('<div class="dossier-title">The Research <em>Dossier</em></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="dossier-sub">Hand a topic to four agents. One gathers evidence, '
    'one reads the strongest lead in full, one drafts the report, and one reviews it '
    'before it goes in the file.</div>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="dossier-rule">', unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Cache expensive agent/chain construction so it only happens once per session
# ----------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_search_agent():
    return build_search_agent()


@st.cache_resource(show_spinner=False)
def get_reader_agent():
    return build_reader_agent()


# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
if "state" not in st.session_state:
    st.session_state.state = {}
if "running" not in st.session_state:
    st.session_state.running = False


# ----------------------------------------------------------------------------
# Pipeline runner (same logic as pipeline.py, but updates the UI as it goes)
# ----------------------------------------------------------------------------
def run_research_pipeline_ui(topic: str) -> dict:
    state = {}

    search_agent = get_search_agent()
    reader_agent = get_reader_agent()

    # --- Stage 1: Search -----------------------------------------------
    with st.status("01 · GATHERING EVIDENCE — searching the web", expanded=True) as status:
        search_result = search_agent.invoke(
            {"messages": [("user", f"find recent, reliable and detailed information about : {topic}")]}
        )
        state["search_result"] = search_result["messages"][-1].content
        status.update(label="01 · EVIDENCE GATHERED", state="complete")

    with st.expander("Search results", expanded=False):
        st.markdown(state["search_result"])

    # --- Stage 2: Read / scrape -----------------------------------------
    with st.status("02 · DEEP READ — scraping the strongest lead", expanded=True) as status:
        reader_result = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"pick the most relevant URL and scrape it for deeper content\n\n"
                        f"Search Results:\n{state['search_result'][:800]}",
                    )
                ]
            }
        )
        state["scraped_content"] = reader_result["messages"][-1].content
        status.update(label="02 · SOURCE READ IN FULL", state="complete")

    with st.expander("Scraped content", expanded=False):
        st.markdown(state["scraped_content"])

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_result']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    # --- Stage 3: Write ---------------------------------------------------
    with st.status("03 · DRAFTING — writing the report", expanded=True) as status:
        state["report"] = writer_chain.invoke({"topic": topic, "research": research_combined})
        status.update(label="03 · DRAFT COMPLETE", state="complete")

    # --- Stage 4: Critique --------------------------------------------
    with st.status("04 · REVIEW — critic reading the draft", expanded=True) as status:
        state["feedback"] = critic_chain.invoke({"report": state["report"]})
        status.update(label="04 · REVIEW COMPLETE", state="complete")

    return state


# ----------------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="side-label">Case File Process</div>', unsafe_allow_html=True)
    steps = [
        ("01", "Search agent", "finds candidate sources"),
        ("02", "Reader agent", "scrapes the best one in full"),
        ("03", "Writer chain", "drafts the report"),
        ("04", "Critic chain", "reviews it for gaps"),
    ]
    for n, name, desc in steps:
        st.markdown(
            f'<div class="side-step"><span class="n">{n}</span><span><b>{name}</b> — {desc}</span></div>',
            unsafe_allow_html=True,
        )
    st.write("")
    if st.button("Clear file", use_container_width=True):
        st.session_state.state = {}
        st.rerun()


# ----------------------------------------------------------------------------
# Main input
# ----------------------------------------------------------------------------
topic = st.text_input("Research topic", placeholder="e.g. Latest advances in solid-state batteries")

run_clicked = st.button("Open case", type="primary", disabled=st.session_state.running or not topic.strip())

if run_clicked and topic.strip():
    st.session_state.running = True
    try:
        result_state = run_research_pipeline_ui(topic.strip())
        st.session_state.state = result_state
    except Exception as e:
        st.error(f"Pipeline failed: {e}")
    finally:
        st.session_state.running = False

# ----------------------------------------------------------------------------
# Final report display (persists across reruns)
# ----------------------------------------------------------------------------
if st.session_state.state.get("report"):
    st.markdown('<hr class="dossier-rule">', unsafe_allow_html=True)
    st.markdown("### Field Report")

    report_text = st.session_state.state["report"]
    report_text = report_text if isinstance(report_text, str) else str(report_text)

    st.markdown('<div class="parchment"><div class="stamp">On File</div>', unsafe_allow_html=True)
    st.markdown(report_text)
    st.markdown("</div>", unsafe_allow_html=True)

    st.download_button(
        label="Download report as .md",
        data=report_text,
        file_name="research_report.md",
        mime="text/markdown",
    )

    if st.session_state.state.get("feedback"):
        st.markdown("### Reviewer's Notes")
        feedback_text = st.session_state.state["feedback"]
        feedback_text = feedback_text if isinstance(feedback_text, str) else str(feedback_text)
        st.markdown(f'<div class="critic-card">', unsafe_allow_html=True)
        st.markdown(feedback_text)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="foot-note">END OF FILE</div>', unsafe_allow_html=True)