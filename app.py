import os
import re
import html
from datetime import date

import streamlit as st

st.set_page_config(
    page_title="The Investigation · Multi-Agent Research",
    page_icon="📜",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# On Streamlit Cloud, API keys live in st.secrets. Copy them into the environment
# before importing the pipeline, since tools.py / agents.py read keys at import time.
try:
    for key, value in st.secrets.items():
        if isinstance(value, str):
            os.environ.setdefault(key, value)
except Exception:
    pass  # no secrets.toml locally, fall back to .env

from dotenv import load_dotenv

load_dotenv()

# ------------------------------------------------------------------ styles

st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;0,900;1,500&family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap');

:root {
  --paper: #F7F3EA;
  --paper-deep: #EFE8D8;
  --ink: #1F1B16;
  --ink-soft: #5A5148;
  --oxblood: #7A1F1F;
  --gold: #A8864F;
  --rule: #CFC3AA;
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
  background: var(--paper);
}
.stApp, .stMarkdown, p, li, label, input, textarea, button {
  font-family: 'EB Garamond', Georgia, 'Times New Roman', serif !important;
}
.stMarkdown p, .stMarkdown li { font-size: 1.12rem; line-height: 1.7; color: var(--ink); }
h1, h2, h3, h4 { font-family: 'Playfair Display', Georgia, serif !important; color: var(--ink); }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2.5rem; max-width: 780px; }

/* ---- Masthead ---- */
.masthead { text-align: center; margin-bottom: 1.75rem; }
.masthead .kicker {
  font-variant: small-caps; letter-spacing: .22em; font-size: .95rem; color: var(--oxblood);
}
.masthead h1 {
  font-size: clamp(2.4rem, 7vw, 3.8rem); font-weight: 900; margin: .15rem 0 .35rem;
  letter-spacing: -.01em; line-height: 1.05; padding: 0;
}
.masthead .rule {
  border-top: 3px double var(--ink); border-bottom: 1px solid var(--ink);
  height: 5px; margin: .5rem 0;
}
.masthead .dateline {
  display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
  font-size: .95rem; color: var(--ink-soft); font-style: italic; padding: .1rem .25rem;
}
.masthead .motto { font-style: italic; color: var(--ink-soft); font-size: 1.1rem; margin-top: .9rem; }

/* ---- Inputs ---- */
[data-testid="stTextInput"] input {
  background: #FFFDF8; border: 1px solid var(--rule); border-radius: 2px;
  font-size: 1.15rem; padding: .7rem .9rem; color: var(--ink);
}
[data-testid="stTextInput"] input:focus { border-color: var(--oxblood); box-shadow: none; }
[data-testid="stForm"] { border: 1px solid var(--rule); border-radius: 2px; background: var(--paper-deep); padding: 1.4rem 1.4rem 1rem; }
.stButton button, [data-testid="stFormSubmitButton"] button, [data-testid="stDownloadButton"] button {
  border-radius: 2px; font-variant: small-caps; letter-spacing: .12em; font-size: 1.05rem;
}
[data-testid="stFormSubmitButton"] button {
  background: var(--oxblood); color: var(--paper); border: 1px solid var(--oxblood);
}
[data-testid="stFormSubmitButton"] button:hover { background: #5E1515; color: #fff; border-color: #5E1515; }

/* ---- Section heading with ornament ---- */
.section-title {
  display: flex; align-items: center; gap: .9rem; margin: 2.2rem 0 1rem;
  font-family: 'Playfair Display', serif; font-size: 1.05rem; font-variant: small-caps;
  letter-spacing: .2em; color: var(--ink-soft);
}
.section-title::before, .section-title::after { content: ""; flex: 1; border-top: 1px solid var(--rule); }

/* ---- Pipeline progress ---- */
.steps { display: grid; grid-template-columns: repeat(4, 1fr); gap: .6rem; }
@media (max-width: 640px) { .steps { grid-template-columns: repeat(2, 1fr); } }
.step {
  border: 1px solid var(--rule); background: #FFFDF8; padding: .9rem .8rem; text-align: center;
  border-radius: 2px; transition: all .3s ease;
}
.step .num { font-family: 'Playfair Display', serif; font-size: 1.6rem; color: var(--rule); line-height: 1; }
.step .name { font-family: 'Playfair Display', serif; font-weight: 700; font-size: 1rem; margin-top: .35rem; color: var(--ink-soft); }
.step .desc { font-size: .88rem; font-style: italic; color: var(--ink-soft); margin-top: .15rem; }
.step .status { font-variant: small-caps; letter-spacing: .12em; font-size: .82rem; margin-top: .5rem; color: var(--ink-soft); }
.step.active { border-color: var(--oxblood); box-shadow: 0 0 0 1px var(--oxblood) inset; }
.step.active .num, .step.active .status { color: var(--oxblood); }
.step.active .status::after { content: "…"; animation: blink 1.2s infinite; }
.step.done { background: var(--paper-deep); }
.step.done .num { color: var(--gold); }
.step.done .name { color: var(--ink); }
.step.done .status { color: var(--gold); }
.step.failed { border-color: var(--oxblood); }
.step.failed .status { color: var(--oxblood); }
@keyframes blink { 50% { opacity: .2; } }

/* ---- Report ---- */
.st-key-report {
  background: #FFFDF8; border: 1px solid var(--rule); padding: 2.2rem 2.4rem;
  box-shadow: 0 1px 0 var(--rule), 0 12px 30px -18px rgba(60, 40, 20, .35);
}
@media (max-width: 640px) { .st-key-report { padding: 1.3rem 1.1rem; } }
.st-key-report h1, .st-key-report h2 { border-bottom: 1px solid var(--rule); padding-bottom: .3rem; }
.st-key-report h2 { font-size: 1.55rem; margin-top: 1.4rem; }
.st-key-report h3 { font-size: 1.25rem; }
.st-key-report a { color: var(--oxblood); }
.report-head { text-align: center; margin-bottom: 1.2rem; }
.report-head .label { font-variant: small-caps; letter-spacing: .2em; color: var(--oxblood); font-size: .9rem; }
.report-head .topic { font-family: 'Playfair Display', serif; font-size: 2rem; font-weight: 700; line-height: 1.2; margin-top: .2rem; }
.report-head .fleuron { color: var(--gold); font-size: 1.3rem; margin-top: .4rem; }

/* ---- Critic verdict ---- */
.verdict { display: flex; gap: 1.5rem; align-items: center; margin-bottom: 1.2rem; flex-wrap: wrap; }
.seal {
  width: 118px; height: 118px; border-radius: 50%; flex: none;
  border: 2px solid var(--oxblood); outline: 1px solid var(--oxblood); outline-offset: 4px;
  display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--oxblood);
}
.seal .score { font-family: 'Playfair Display', serif; font-size: 2.6rem; font-weight: 900; line-height: 1; }
.seal .outof { font-variant: small-caps; letter-spacing: .15em; font-size: .85rem; }
.verdict .quote { flex: 1; min-width: 220px; font-style: italic; font-size: 1.3rem; line-height: 1.5; border-left: 3px solid var(--gold); padding-left: 1rem; }

/* ---- Tabs ---- */
[data-baseweb="tab-list"] { gap: 1.5rem; border-bottom: 1px solid var(--rule); }
[data-baseweb="tab"] p { font-family: 'Playfair Display', serif !important; font-size: 1.05rem !important; }
[data-baseweb="tab-highlight"] { background: var(--oxblood); }

.colophon { text-align: center; color: var(--ink-soft); font-style: italic; font-size: .95rem; margin-top: 3rem; }
.colophon .rule { border-top: 1px solid var(--rule); margin-bottom: .8rem; }
</style>
""")

# ------------------------------------------------------------------ helpers

STEPS = [
    ("search", "I", "Search", "Scours the web"),
    ("reader", "II", "Reader", "Studies the source"),
    ("writer", "III", "Writer", "Drafts the report"),
    ("critic", "IV", "Critic", "Reviews & scores"),
]
STATUS_LABEL = {"pending": "awaiting", "active": "at work", "done": "complete", "failed": "halted"}


def render_steps(statuses: dict) -> str:
    cards = []
    for key, numeral, name, desc in STEPS:
        status = statuses.get(key, "pending")
        cards.append(
            f'<div class="step {status}"><div class="num">{numeral}</div>'
            f'<div class="name">{name}</div><div class="desc">{desc}</div>'
            f'<div class="status">{STATUS_LABEL[status]}</div></div>'
        )
    return f'<div class="steps">{"".join(cards)}</div>'


def section(title: str):
    st.html(f'<div class="section-title">{html.escape(title)}</div>')


def parse_critique(text: str):
    """Pull the score and one-line verdict out of the critic's fixed-format response."""
    score = re.search(r"Score:\s*\**\s*(\d+(?:\.\d+)?)\s*/\s*10", text, re.I)
    verdict = re.search(r"One[- ]line verdict:\**\s*\n*\s*(.+)", text, re.I)
    return (score.group(1) if score else None), (verdict.group(1).strip(" *") if verdict else None)


def missing_keys() -> list:
    missing = []
    if not os.getenv("TAVILY_API_KEY"):
        missing.append("TAVILY_API_KEY")
    if not (os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")):
        missing.append("GOOGLE_API_KEY")
    return missing

# ------------------------------------------------------------------ masthead

today = date.today()
st.html(f"""
<div class="masthead">
  <div class="kicker">A Multi-Agent Research Desk</div>
  <h1>The Investigation</h1>
  <div class="rule"></div>
  <div class="dateline">
    <span>{today.strftime('%A, %B')} {today.day}, {today.year}</span>
    <span>Search · Read · Write · Critique</span>
  </div>
  <div class="rule"></div>
  <div class="motto">Name a subject, and four agents will research, write and review a report on it.</div>
</div>
""")

if "result" not in st.session_state:
    st.session_state.result = None
    st.session_state.topic = ""

with st.form("commission", border=True):
    topic = st.text_input(
        "Subject of inquiry",
        placeholder="e.g. The state of solid-state batteries in 2026",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Commission the Report", width="stretch")

# ------------------------------------------------------------------ run

if submitted:
    if not topic.strip():
        st.warning("Please name a subject before commissioning a report.")
    elif missing := missing_keys():
        st.error(
            f"Missing API key(s): **{', '.join(missing)}**. Add them to your `.env` file locally, "
            "or to the app's **Secrets** on Streamlit Cloud."
        )
    else:
        from pipeline import run_research_pipeline

        section("The Desk at Work")
        progress = st.empty()
        statuses = {}
        progress.html(render_steps(statuses))

        def on_step(step, status, _output):
            statuses[step] = "active" if status == "start" else "done"
            progress.html(render_steps(statuses))

        try:
            st.session_state.result = run_research_pipeline(topic.strip(), on_step=on_step)
            st.session_state.topic = topic.strip()
        except Exception as e:
            for key, *_ in STEPS:
                if statuses.get(key) == "active":
                    statuses[key] = "failed"
            progress.html(render_steps(statuses))
            st.error(f"The investigation was interrupted: {e}")
            st.session_state.result = None

# ------------------------------------------------------------------ results

result = st.session_state.result
if result:
    topic_done = st.session_state.topic
    section("The Findings")

    tab_report, tab_critique, tab_notes = st.tabs(["The Report", "The Critique", "Field Notes"])

    with tab_report:
        with st.container(key="report"):
            st.html(f"""
            <div class="report-head">
              <div class="label">Research Report</div>
              <div class="topic">{html.escape(topic_done)}</div>
              <div class="fleuron">❦</div>
            </div>""")
            st.markdown(result["report"])
        slug = re.sub(r"[^a-z0-9]+", "-", topic_done.lower()).strip("-")[:60] or "report"
        st.download_button(
            "Download Report (Markdown)",
            data=f"# {topic_done}\n\n{result['report']}\n\n---\n\n## Critique\n\n{result['critique']}\n",
            file_name=f"{slug}.md",
            mime="text/markdown",
            width="stretch",
        )

    with tab_critique:
        score, verdict = parse_critique(result["critique"])
        if score or verdict:
            st.html(f"""
            <div class="verdict">
              <div class="seal"><div class="score">{html.escape(score or "–")}</div><div class="outof">out of ten</div></div>
              <div class="quote">{html.escape(verdict or "")}</div>
            </div>""")
        with st.container(key="critique"):
            st.markdown(result["critique"])

    with tab_notes:
        st.caption("The raw material gathered by the Search and Reader agents.")
        with st.expander("I. Search Results", expanded=True):
            st.markdown(result["search_result"])
        with st.expander("II. Scraped Source"):
            st.markdown(result["scraped_content"])

st.html("""
<div class="colophon"><div class="rule"></div>
Set in Playfair Display &amp; EB Garamond · Powered by LangChain, Gemini &amp; Tavily
</div>""")
