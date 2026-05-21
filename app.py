import html
import os
import re
import sqlite3
from typing import Optional

import pandas as pd
import streamlit as st
from google import genai
from google.genai import types

from db_setup import TABLES, get_connection, get_schema_description

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Talking with Database",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS: Figma-inspired moving background + glass UI ─────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --bg-1: #050816;
    --bg-2: #08111f;
    --glass: rgba(255, 255, 255, 0.075);
    --glass-strong: rgba(255, 255, 255, 0.12);
    --stroke: rgba(255, 255, 255, 0.16);
    --text: #f7fbff;
    --muted: #9eb2d6;
    --muted-2: #6f83a8;
    --cyan: #4df7ff;
    --blue: #6d8dff;
    --violet: #a855f7;
    --pink: #ff4ecd;
    --green: #5ff7a1;
}

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    color: var(--text);
    background:
        radial-gradient(circle at 15% 20%, rgba(77, 247, 255, 0.22), transparent 28%),
        radial-gradient(circle at 82% 12%, rgba(168, 85, 247, 0.28), transparent 30%),
        radial-gradient(circle at 60% 85%, rgba(255, 78, 205, 0.16), transparent 32%),
        linear-gradient(135deg, var(--bg-1), var(--bg-2) 55%, #0b0720);
    overflow-x: hidden;
}

.stApp::before,
.stApp::after {
    content: "";
    position: fixed;
    inset: -18%;
    pointer-events: none;
    z-index: 0;
}

.stApp::before {
    background:
        linear-gradient(115deg, transparent 0 42%, rgba(77, 247, 255, 0.11) 44%, transparent 47%),
        linear-gradient(245deg, transparent 0 55%, rgba(255, 78, 205, 0.10) 57%, transparent 60%);
    animation: driftGrid 18s ease-in-out infinite alternate;
}

.stApp::after {
    background-image:
        radial-gradient(circle, rgba(255,255,255,0.14) 1px, transparent 1px),
        radial-gradient(circle, rgba(77,247,255,0.12) 1px, transparent 1px);
    background-size: 48px 48px, 88px 88px;
    opacity: 0.42;
    animation: moveDots 28s linear infinite;
}

@keyframes driftGrid {
    from { transform: translate3d(-2%, -1%, 0) rotate(0deg) scale(1); }
    to   { transform: translate3d(2%, 2%, 0) rotate(5deg) scale(1.08); }
}

@keyframes moveDots {
    from { transform: translate3d(0, 0, 0); }
    to   { transform: translate3d(-90px, -90px, 0); }
}

.block-container {
    position: relative;
    z-index: 1;
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1320px;
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { right: 1rem; }

[data-testid="stSidebar"] {
    background: rgba(4, 10, 24, 0.72) !important;
    backdrop-filter: blur(24px);
    border-right: 1px solid var(--stroke);
}

[data-testid="stSidebar"] * { color: var(--text); }

section[data-testid="stSidebar"] .block-container {
    padding-top: 1.6rem;
}

.hero {
    position: relative;
    overflow: hidden;
    border: 1px solid var(--stroke);
    border-radius: 34px;
    min-height: 420px;
    padding: 34px;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.13), rgba(255,255,255,0.045)),
        radial-gradient(circle at 70% 30%, rgba(77,247,255,0.20), transparent 26%),
        radial-gradient(circle at 35% 90%, rgba(168,85,247,0.18), transparent 30%);
    box-shadow: 0 26px 90px rgba(0,0,0,0.38);
    backdrop-filter: blur(22px);
}

.hero::before {
    content: "";
    position: absolute;
    width: 420px;
    height: 420px;
    right: -110px;
    top: -130px;
    border-radius: 999px;
    background: conic-gradient(from 180deg, var(--cyan), var(--violet), var(--pink), var(--cyan));
    filter: blur(28px);
    opacity: 0.30;
    animation: spinGlow 12s linear infinite;
}

@keyframes spinGlow { to { transform: rotate(360deg); } }

.hero-grid {
    position: relative;
    z-index: 1;
    display: grid;
    grid-template-columns: 1.05fr 0.95fr;
    gap: 26px;
    align-items: center;
}

.kicker {
    width: fit-content;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 8px 13px;
    border: 1px solid rgba(77,247,255,0.35);
    border-radius: 999px;
    background: rgba(77,247,255,0.09);
    color: #cafcff;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
}

.kicker-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 22px var(--green);
}

.hero-title {
    margin: 18px 0 12px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(42px, 6vw, 82px);
    line-height: 0.93;
    letter-spacing: -0.07em;
    font-weight: 700;
}

.gradient-text {
    background: linear-gradient(90deg, #ffffff, #4df7ff 38%, #a855f7 70%, #ff4ecd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-copy {
    max-width: 660px;
    color: var(--muted);
    font-size: 17px;
    line-height: 1.8;
}

.hero-actions {
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    margin-top: 24px;
}

.pill {
    border-radius: 999px;
    padding: 11px 15px;
    border: 1px solid var(--stroke);
    background: rgba(255,255,255,0.07);
    color: var(--text);
    font-size: 13px;
    font-weight: 700;
}

.visual-card {
    position: relative;
    min-height: 330px;
    border-radius: 28px;
    padding: 22px;
    border: 1px solid rgba(255,255,255,0.18);
    background: rgba(2, 8, 22, 0.64);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.12), 0 22px 60px rgba(0,0,0,0.3);
    overflow: hidden;
}

.visual-card::before {
    content: "";
    position: absolute;
    inset: 20px;
    border-radius: 26px;
    background:
        linear-gradient(90deg, rgba(77,247,255,0.08) 1px, transparent 1px),
        linear-gradient(0deg, rgba(77,247,255,0.08) 1px, transparent 1px);
    background-size: 26px 26px;
    mask-image: radial-gradient(circle at 50% 50%, #000, transparent 74%);
}

.orbit {
    position: absolute;
    inset: 42px;
    border: 1px dashed rgba(77,247,255,0.30);
    border-radius: 50%;
    animation: slowSpin 18s linear infinite;
}

.orbit.two {
    inset: 75px;
    border-color: rgba(255,78,205,0.28);
    animation-duration: 12s;
    animation-direction: reverse;
}

@keyframes slowSpin { to { transform: rotate(360deg); } }

.node {
    position: absolute;
    display: grid;
    place-items: center;
    width: 86px;
    height: 86px;
    border-radius: 26px;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.20);
    backdrop-filter: blur(16px);
    font-weight: 900;
    box-shadow: 0 16px 40px rgba(0,0,0,0.26);
}

.node.ai { top: 28px; left: 30px; color: var(--cyan); }
.node.sql { right: 34px; top: 96px; color: #ffd166; }
.node.db { bottom: 34px; left: 112px; color: var(--green); }

.code-window {
    position: absolute;
    right: 28px;
    bottom: 28px;
    left: 28px;
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.16);
    background: rgba(0,0,0,0.34);
    padding: 14px;
    font-family: 'Space Grotesk', sans-serif;
    color: #d6e4ff;
    font-size: 13px;
}

.window-dots span {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
    background: rgba(255,255,255,0.35);
}

.sql-line { margin-top: 10px; color: #7df9ff; }

.stat-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 14px;
    margin-top: 18px;
}

.stat-card, .glass-card {
    border: 1px solid var(--stroke);
    border-radius: 24px;
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(18px);
    box-shadow: 0 18px 56px rgba(0,0,0,0.24);
}

.stat-card { padding: 18px; }
.stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px;
    font-weight: 700;
}
.stat-label { color: var(--muted-2); font-size: 13px; margin-top: 4px; }

.section-title {
    margin: 28px 0 12px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px;
    letter-spacing: -0.04em;
}

.ask-card {
    padding: 22px;
    margin-top: 18px;
}

.user-bubble {
    max-width: 86%;
    margin-left: auto;
    width: fit-content;
    padding: 14px 18px;
    border-radius: 22px 22px 6px 22px;
    background: linear-gradient(135deg, rgba(77,247,255,0.28), rgba(168,85,247,0.28));
    border: 1px solid rgba(255,255,255,0.16);
    color: white;
    box-shadow: 0 12px 38px rgba(77,247,255,0.12);
}

.bot-card {
    padding: 18px;
    margin-top: 12px;
}

.sql-block, .explain-block, .error-block {
    border-radius: 18px;
    padding: 16px;
    line-height: 1.7;
    border: 1px solid var(--stroke);
}

.sql-block {
    font-family: 'Space Grotesk', sans-serif;
    color: #8ffaff;
    background: rgba(0,0,0,0.32);
    white-space: pre-wrap;
    overflow-x: auto;
}

.explain-block {
    color: #d7e5ff;
    background: rgba(255,255,255,0.055);
}

.error-block {
    color: #ffd6d6;
    background: rgba(255, 54, 96, 0.12);
    border-color: rgba(255, 54, 96, 0.28);
}

.schema-chip {
    display: inline-block;
    margin: 5px 5px 0 0;
    padding: 7px 10px;
    border-radius: 999px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.13);
    color: #dbeafe;
    font-size: 12px;
    font-weight: 700;
}

.sidebar-brand {
    padding: 18px;
    border-radius: 26px;
    background: linear-gradient(135deg, rgba(77,247,255,0.16), rgba(168,85,247,0.16));
    border: 1px solid rgba(255,255,255,0.16);
}

.sidebar-logo {
    width: 48px;
    height: 48px;
    display: grid;
    place-items: center;
    border-radius: 18px;
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    color: #04111c;
    font-size: 25px;
    font-weight: 900;
    margin-bottom: 12px;
}

.sidebar-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: -0.04em;
}

.sidebar-subtitle {
    color: var(--muted);
    font-size: 13px;
    margin-top: 4px;
}

.stButton > button {
    border: 0 !important;
    border-radius: 999px !important;
    color: white !important;
    background: linear-gradient(135deg, #18d5ff, #7c3aed 55%, #ff4ecd) !important;
    box-shadow: 0 16px 40px rgba(124,58,237,0.27) !important;
    font-weight: 800 !important;
    letter-spacing: 0.02em !important;
    transition: all 180ms ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px) scale(1.01);
    filter: brightness(1.08);
}

.stTextArea textarea, .stTextInput input {
    border: 1px solid rgba(255,255,255,0.16) !important;
    background: rgba(255,255,255,0.075) !important;
    color: white !important;
    border-radius: 20px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.08) !important;
}

.stTextArea textarea::placeholder, .stTextInput input::placeholder { color: #7f93b8 !important; }

[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 18px !important;
    overflow: hidden;
}

[data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.13) !important;
    background: rgba(255,255,255,0.055) !important;
    border-radius: 18px !important;
}

.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 999px;
    padding: 8px 14px;
    background: rgba(255,255,255,0.06);
}

hr {
    border: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
}

@media (max-width: 900px) {
    .hero-grid, .stat-row { grid-template-columns: 1fr; }
    .hero { padding: 24px; min-height: auto; }
    .visual-card { min-height: 300px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Helpers ──────────────────────────────────────────────────────────────────
def safe_text(value: object) -> str:
    return html.escape(str(value), quote=True)


def clean_sql(text: str) -> str:
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:sql)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned


def fallback_sql(question: str) -> Optional[str]:
    q = question.lower()
    if "engineering" in q and "employee" in q:
        return "SELECT * FROM employees WHERE department = 'Engineering';"
    if "average" in q and "salary" in q:
        return "SELECT department, ROUND(AVG(salary), 2) AS average_salary FROM employees GROUP BY department ORDER BY average_salary DESC;"
    if "top" in q and "sales" in q:
        return "SELECT * FROM sales ORDER BY amount DESC LIMIT 5;"
    if "active" in q and "project" in q:
        return "SELECT COUNT(*) AS active_projects FROM projects WHERE status = 'active';"
    if "hired" in q and ("2022" in q or "after" in q):
        return "SELECT * FROM employees WHERE hire_date > '2022-01-01' ORDER BY hire_date;"
    if "highest" in q and "budget" in q:
        return "SELECT name, budget, location FROM departments ORDER BY budget DESC LIMIT 1;"
    if "region" in q and "sales" in q:
        return "SELECT region, SUM(amount) AS total_sales FROM sales GROUP BY region ORDER BY total_sales DESC;"
    if "department" in q and "budget" in q:
        return "SELECT name, budget, location FROM departments ORDER BY budget DESC;"
    return None


def simple_explanation(sql: str) -> str:
    sql_low = sql.lower()
    if "avg(salary)" in sql_low:
        return "This query groups employees by department and calculates the average salary for each team. It helps compare which departments have higher salary levels."
    if "from sales" in sql_low and "order by amount" in sql_low:
        return "This query lists the largest sales records first. It helps identify the strongest sales transactions in the database."
    if "active_projects" in sql_low:
        return "This query counts how many projects are currently marked as active. It gives a quick view of ongoing project workload."
    if "from employees" in sql_low:
        return "This query filters employee records based on your question. It helps you quickly inspect the matching staff details."
    return "This query reads the matching database records and returns the result in a table so you can analyze it quickly."


conn = get_connection()
SCHEMA_DESC = get_schema_description(conn)


def get_api_key() -> str:
    """Read Gemini API key safely from Streamlit secrets or environment.

    The app must not crash when the key is missing. Without a key, it runs in
    demo mode using built-in sample questions.
    """
    try:
        secret_key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        secret_key = ""
    return (secret_key or os.getenv("GEMINI_API_KEY", "") or "").strip()


api_key = get_api_key()
try:
    client = genai.Client(api_key=api_key) if api_key else None
except Exception:
    # Keep the UI running even if an invalid/empty key is configured.
    client = None
GEMINI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = f"""You are a SQLite SQL expert. The user has a SQLite database with this schema:

{SCHEMA_DESC}

Your job:
1. Convert the user's natural language question into a valid SQLite SQL query.
2. Output ONLY the raw SQL query — no explanation, no markdown, no backticks, no comments.
3. Make sure the SQL is correct for SQLite syntax.
4. If the question is unclear, write the most reasonable SQL interpretation.
"""

EXPLAIN_PROMPT = f"""You are a friendly data analyst. Given a SQL query for this schema:

{SCHEMA_DESC}

Explain in 2-3 plain sentences what the query does and what insights it gives.
Be concise and non-technical. Do not repeat the SQL.
"""

if "history" not in st.session_state:
    st.session_state.history = []

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-logo">DB</div>
            <div class="sidebar-title">Talking Database</div>
            <div class="sidebar-subtitle">AI-powered natural language SQL workspace.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Database schema")
    for tbl, cols in TABLES.items():
        with st.expander(f"{tbl}", expanded=False):
            st.markdown("".join([f"<span class='schema-chip'>{safe_text(col)}</span>" for col in cols]), unsafe_allow_html=True)

    st.markdown("### Ask examples")
    samples = [
        "Show all employees in Engineering",
        "Average salary by department",
        "Top 5 sales by amount",
        "Active projects count",
        "Employees hired after 2022",
        "Which department has the highest budget?",
        "Total sales amount per region",
    ]
    for sample in samples:
        if st.button(sample, key=f"sample_{sample}", use_container_width=True):
            st.session_state["prefill"] = sample

    st.markdown("---")
    if st.button("Clear workspace", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# ── Hero ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <section class="hero">
        <div class="hero-grid">
            <div>
                <div class="kicker"><span class="kicker-dot"></span> Natural language to SQL</div>
                <h1 class="hero-title">Talk to your <span class="gradient-text">database</span> like a chatbot.</h1>
                <p class="hero-copy">
                    Ask business questions in simple English. The app converts them into SQLite queries,
                    runs them instantly, and explains the result in a clean dashboard-style interface.
                </p>
                <div class="hero-actions">
                    <span class="pill">Gemini AI</span>
                    <span class="pill">SQLite</span>
                    <span class="pill">Streamlit</span>
                    <span class="pill">Animated UI</span>
                </div>
            </div>
            <div class="visual-card">
                <div class="orbit"></div>
                <div class="orbit two"></div>
                <div class="node ai">AI</div>
                <div class="node sql">SQL</div>
                <div class="node db">DB</div>
                <div class="code-window">
                    <div class="window-dots"><span></span><span></span><span></span></div>
                    <div class="sql-line">SELECT department, AVG(salary)</div>
                    <div class="sql-line">FROM employees GROUP BY department;</div>
                </div>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="stat-row">
        <div class="stat-card"><div class="stat-value">4</div><div class="stat-label">Connected sample tables</div></div>
        <div class="stat-card"><div class="stat-value">AI</div><div class="stat-label">Question to SQL engine</div></div>
        <div class="stat-card"><div class="stat-value">Live</div><div class="stat-label">Query result preview</div></div>
        <div class="stat-card"><div class="stat-value">UX</div><div class="stat-label">Moving glass background</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Ask panel ────────────────────────────────────────────────────────────────
st.markdown('<h2 class="section-title">Ask your database</h2>', unsafe_allow_html=True)
st.markdown('<div class="glass-card ask-card">', unsafe_allow_html=True)

prefill = st.session_state.pop("prefill", "")
with st.form("ask_form", clear_on_submit=False):
    question = st.text_area(
        "Question",
        value=prefill,
        placeholder="Example: What is the average salary by department?",
        height=92,
        label_visibility="collapsed",
    )
    col_run, col_info = st.columns([1, 4])
    with col_run:
        run = st.form_submit_button("Run query", use_container_width=True)
    with col_info:
        if not api_key:
            st.caption("Demo mode: add GEMINI_API_KEY to enable AI generation for any custom question.")
        else:
            st.caption("AI mode active: Gemini will generate SQL from your natural language question.")

st.markdown('</div>', unsafe_allow_html=True)

# ── Process ──────────────────────────────────────────────────────────────────
if run and question.strip():
    sql = ""
    error = None
    explanation = ""
    df = None

    with st.spinner("Generating SQL and fetching results…"):
        try:
            if client:
                sql_response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=question,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        max_output_tokens=500,
                        temperature=0.1,
                    ),
                )
                sql = clean_sql(sql_response.text or "")
            else:
                sql = fallback_sql(question) or ""
                if not sql:
                    error = "AI key is missing, and this custom question is not available in demo mode. Add GEMINI_API_KEY or try a sample question."
        except Exception as exc:
            fallback = fallback_sql(question)
            if fallback:
                sql = fallback
            else:
                error = f"AI error: {exc}"

        if sql and not error:
            try:
                df = pd.read_sql_query(sql, conn)
            except Exception as exc:
                error = f"SQL error: {exc}"

        if sql and not error:
            try:
                if client:
                    exp_response = client.models.generate_content(
                        model=GEMINI_MODEL,
                        contents=f"Explain this SQL: {sql}",
                        config=types.GenerateContentConfig(
                            system_instruction=EXPLAIN_PROMPT,
                            max_output_tokens=200,
                            temperature=0.2,
                        ),
                    )
                    explanation = (exp_response.text or "").strip()
                else:
                    explanation = simple_explanation(sql)
            except Exception:
                explanation = simple_explanation(sql)

    st.session_state.history.insert(
        0,
        {
            "question": question.strip(),
            "sql": sql,
            "df": df,
            "error": error,
            "explanation": explanation,
        },
    )
    st.rerun()

# ── Results history ──────────────────────────────────────────────────────────
st.markdown('<h2 class="section-title">Workspace results</h2>', unsafe_allow_html=True)
if not st.session_state.history:
    st.markdown(
        """
        <div class="glass-card bot-card">
            <div class="explain-block">Start with a sample question from the sidebar or type your own question above. Results, SQL, and explanation will appear here.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

for item in st.session_state.history:
    st.markdown(f'<div class="user-bubble">{safe_text(item["question"])}</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card bot-card">', unsafe_allow_html=True)
    if item.get("error"):
        st.markdown(f'<div class="error-block">{safe_text(item["error"])}</div>', unsafe_allow_html=True)
    else:
        tab1, tab2, tab3 = st.tabs(["Results", "SQL", "Explanation"])
        with tab1:
            if item.get("df") is not None and not item["df"].empty:
                st.dataframe(item["df"], use_container_width=True, hide_index=True)
                st.caption(f"{len(item['df'])} row(s) returned")
            else:
                st.info("Query returned no rows.")
        with tab2:
            st.markdown(f'<div class="sql-block">{safe_text(item["sql"])}</div>', unsafe_allow_html=True)
        with tab3:
            st.markdown(f'<div class="explain-block">{safe_text(item.get("explanation", ""))}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
