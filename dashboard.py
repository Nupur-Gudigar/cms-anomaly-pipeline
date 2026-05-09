import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import snowflake.connector
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="CMS Medicare Anomaly Detection — Nupur Gudigar",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;1,400&family=Inter:wght@300;400;500;600&display=swap');

body, .stApp { font-family: 'Inter', sans-serif; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

.main-wrapper {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 2.5rem 4rem 2.5rem;
}

/* ── Top nav ── */
.topnav {
    border-bottom: 1px solid var(--nav-border);
    padding: 1.1rem 2.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0;
}
.topnav-left {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
}
.topnav-right {
    display: flex;
    gap: 1.5rem;
    align-items: center;
}
.topnav-right a {
    font-size: 12px;
    font-weight: 400;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    text-decoration: none;
    color: var(--muted);
    transition: color 0.15s;
}
.topnav-right a:hover { color: var(--text); }

/* ── Hero ── */
.hero {
    padding: 4rem 0 3rem 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 3rem;
}
.hero-eyebrow {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 54px;
    font-weight: 400;
    line-height: 1.1;
    color: var(--text);
    margin-bottom: 1.5rem;
}
.hero-title em {
    font-style: italic;
    color: var(--accent);
}
.hero-body {
    font-size: 16px;
    font-weight: 300;
    line-height: 1.8;
    color: var(--muted);
    max-width: 620px;
    margin-bottom: 2rem;
}
.tech-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.tech-pill {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    padding: 4px 12px;
    border: 1px solid var(--border);
    border-radius: 2px;
    color: var(--muted);
}

/* ── Section labels ── */
.section-label {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    border-top: 2px solid var(--accent);
    padding-top: 10px;
    margin-bottom: 1.5rem;
    display: inline-block;
}

/* ── Metrics ── */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    border: 1px solid var(--border);
    border-radius: 4px;
    margin-bottom: 3rem;
    overflow: hidden;
}
.metric-item {
    padding: 1.5rem;
    border-right: 1px solid var(--border);
}
.metric-item:last-child { border-right: none; }
.metric-item-label {
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
}
.metric-item-value {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 36px;
    font-weight: 400;
    color: var(--text);
    line-height: 1;
    margin-bottom: 6px;
}
.metric-item-sub {
    font-size: 11px;
    color: var(--accent);
    font-weight: 400;
}

/* ── Story sections ── */
.story-section {
    margin-bottom: 4rem;
    padding-bottom: 4rem;
    border-bottom: 1px solid var(--border);
}
.story-headline {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 28px;
    font-weight: 400;
    color: var(--text);
    margin-bottom: 8px;
    line-height: 1.3;
}
.story-body {
    font-size: 14px;
    font-weight: 300;
    line-height: 1.8;
    color: var(--muted);
    max-width: 640px;
    margin-bottom: 1.5rem;
}

/* ── Table ── */
.findings-header {
    display: grid;
    grid-template-columns: 2fr 2.5fr 0.8fr 1.5fr 1.5fr 1.2fr;
    gap: 12px;
    padding: 10px 16px;
    background: var(--row-header-bg);
    border-bottom: 1px solid var(--border);
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    border-radius: 4px 4px 0 0;
}
.badge-anom {
    display: inline-block;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.04em;
    padding: 2px 8px;
    border-radius: 2px;
    background: var(--badge-bg);
    color: var(--badge-text);
}

/* ── Footer ── */
.footer {
    padding: 2rem 0;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}
.footer-left {
    font-size: 12px;
    color: var(--muted);
    font-weight: 300;
    line-height: 1.8;
}
.footer-right {
    display: flex;
    gap: 1.5rem;
}
.footer-right a {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    text-decoration: none;
    color: var(--muted);
}
.footer-right a:hover { color: var(--text); }

/* ── Light mode ── */
[data-theme="light"], .stApp[data-theme="light"] {
    --text: #0f0f0f;
    --muted: #6b7280;
    --accent: #185FA5;
    --border: #e5e7eb;
    --nav-border: #e5e7eb;
    --bg: #ffffff;
    --surface: #f9fafb;
    --row-header-bg: #f3f4f6;
    --badge-bg: #fee2e2;
    --badge-text: #991b1b;
}

/* ── Dark mode ── */
[data-theme="dark"], .stApp[data-theme="dark"] {
    --text: #f3f4f6;
    --muted: #9ca3af;
    --accent: #60a5fa;
    --border: #374151;
    --nav-border: #374151;
    --bg: #111827;
    --surface: #1f2937;
    --row-header-bg: #1f2937;
    --badge-bg: #450a0a;
    --badge-text: #fca5a5;
}

/* Force remove default streamlit padding */
section[data-testid="stSidebar"] { display: none; }
div[data-testid="stToolbar"] { display: none; }
header[data-testid="stHeader"] { display: none; }
.stDeployButton { display: none; }

/* Plotly chart borders */
.js-plotly-plot {
    border: 1px solid var(--border);
    border-radius: 4px;
}

/* Selectbox styling */
div[data-testid="stSelectbox"] label {
    font-size: 10px !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Detect color mode for charts ──────────────────────────────────────
is_dark = st.get_option("theme.base") == "dark"
PLOT_BG = "#111827" if is_dark else "#ffffff"
PAPER_BG = "#111827" if is_dark else "#ffffff"
GRID_COLOR = "#374151" if is_dark else "#f3f4f6"
TEXT_COLOR = "#f3f4f6" if is_dark else "#111827"
MUTED_COLOR = "#9ca3af" if is_dark else "#6b7280"
ACCENT = "#60a5fa" if is_dark else "#185FA5"
BLUE_MID = "#93c5fd" if is_dark else "#B5D4F4"
RED = "#f87171" if is_dark else "#E24B4A"

def plot_layout(height=400, title=""):
    return dict(
        height=height,
        plot_bgcolor=PLOT_BG,
        paper_bgcolor=PAPER_BG,
        font_family="Inter, sans-serif",
        font_color=TEXT_COLOR,
        title_text=title,
        title_font_size=13,
        title_font_color=TEXT_COLOR,
        xaxis=dict(
            showgrid=True, gridcolor=GRID_COLOR,
            linecolor=GRID_COLOR, tickfont=dict(size=11, color=MUTED_COLOR),
            title_font=dict(size=11, color=MUTED_COLOR)
        ),
        yaxis=dict(
            showgrid=True, gridcolor=GRID_COLOR,
            linecolor=GRID_COLOR, tickfont=dict(size=11, color=MUTED_COLOR),
            title_font=dict(size=11, color=MUTED_COLOR)
        ),
        margin=dict(l=60, r=20, t=50, b=60),
        legend=dict(
            font=dict(size=11, color=MUTED_COLOR),
            bgcolor="rgba(0,0,0,0)",
            title_text=""
        )
    )

# ── Load data ─────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_data():
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )
    df = pd.read_sql("""
        SELECT PRESCRIBER_NPI, LAST_NAME, FIRST_NAME, STATE, SPECIALTY,
               TOTAL_CLAIMS, TOTAL_DRUG_COST, TOTAL_BENEFICIARIES,
               UNIQUE_DRUGS_PRESCRIBED, AVG_COST_PER_CLAIM,
               COST_PER_BENEFICIARY, ANOMALY_SCORE_RAW, IS_ANOMALY
        FROM CMS_MEDICARE.RESULTS.ANOMALY_SCORES
    """, conn)
    conn.close()
    return df

with st.spinner("Loading..."):
    df = load_data()

total = len(df)
anomalies = int(df["IS_ANOMALY"].sum())
rate = (anomalies / total) * 100
spend = df["TOTAL_DRUG_COST"].sum()
df["Status"] = df["IS_ANOMALY"].map({0: "Normal", 1: "Anomaly"})
df["Full name"] = df["FIRST_NAME"].str.title() + " " + df["LAST_NAME"].str.title()

# ── Top nav ───────────────────────────────────────────────────────────
st.markdown("""
<div class="topnav">
  <div class="topnav-left">Portfolio Project &nbsp;·&nbsp; Data Engineering</div>
  <div class="topnav-right">
    <a href="https://github.com/Nupur-Gudigar" target="_blank">GitHub</a>
    <a href="https://www.linkedin.com/in/nupur-gudigar" target="_blank">LinkedIn</a>
    <a href="mailto:nupurgudigar.tech@gmail.com">Email</a>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-eyebrow">CMS Medicare Part D · 2023 · 500,000 Claims</div>
  <div class="hero-title">Detecting <em>anomalous</em><br>prescriber billing<br>patterns</div>
  <div class="hero-body">
    An end-to-end data engineering pipeline that loads real Medicare Part D claims
    data into Snowflake, transforms it with dbt, and applies Isolation Forest
    machine learning to surface the top 0.5% of statistically suspicious prescribers
    across 20,935 providers nationwide.
  </div>
  <div class="tech-row">
    <span class="tech-pill">Snowflake</span>
    <span class="tech-pill">dbt</span>
    <span class="tech-pill">Isolation Forest</span>
    <span class="tech-pill">Great Expectations</span>
    <span class="tech-pill">Apache Airflow</span>
    <span class="tech-pill">Python</span>
    <span class="tech-pill">Streamlit</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Metrics ───────────────────────────────────────────────────────────
st.markdown('<span class="section-label">At a glance</span>', unsafe_allow_html=True)
st.markdown(f"""
<div class="metrics-grid">
  <div class="metric-item">
    <div class="metric-item-label">Prescribers analyzed</div>
    <div class="metric-item-value">{total:,}</div>
    <div class="metric-item-sub">2023 dataset</div>
  </div>
  <div class="metric-item">
    <div class="metric-item-label">Anomalies detected</div>
    <div class="metric-item-value">{anomalies:,}</div>
    <div class="metric-item-sub">flagged for review</div>
  </div>
  <div class="metric-item">
    <div class="metric-item-label">Anomaly rate</div>
    <div class="metric-item-value">{rate:.2f}%</div>
    <div class="metric-item-sub">within 0.6% threshold</div>
  </div>
  <div class="metric-item">
    <div class="metric-item-label">Medicare spend</div>
    <div class="metric-item-value">${spend/1e9:.2f}B</div>
    <div class="metric-item-sub">total analyzed</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Section 1: Filter + Scatter ───────────────────────────────────────
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown('<span class="section-label">Explore</span>', unsafe_allow_html=True)
st.markdown("""
<div class="story-headline">Every dot is a doctor.</div>
<div class="story-body">
  Plot each of the 20,935 prescribers by their total claim volume and total
  drug cost. Normal prescribers cluster together. Anomalous ones — shown in red —
  sit far from the group, isolated by the Isolation Forest algorithm.
  Use the filters to explore by state or specialty.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    states = ["All states"] + sorted(df["STATE"].dropna().unique().tolist())
    state = st.selectbox("State", states)
with col2:
    specs = ["All specialties"] + sorted(
        df["SPECIALTY"].dropna().unique().tolist()
    )
    spec = st.selectbox("Specialty", specs)

fdf = df.copy()
if state != "All states":
    fdf = fdf[fdf["STATE"] == state]
if spec != "All specialties":
    fdf = fdf[fdf["SPECIALTY"] == spec]

fig_scatter = px.scatter(
    fdf, x="TOTAL_CLAIMS", y="TOTAL_DRUG_COST",
    color="Status",
    color_discrete_map={"Normal": BLUE_MID, "Anomaly": RED},
    hover_data={
        "Full name": True, "SPECIALTY": True, "STATE": True,
        "AVG_COST_PER_CLAIM": ":.0f", "TOTAL_BENEFICIARIES": True,
        "Status": False, "TOTAL_CLAIMS": False, "TOTAL_DRUG_COST": False
    },
    labels={
        "TOTAL_CLAIMS": "Total claims",
        "TOTAL_DRUG_COST": "Total drug cost ($)",
        "SPECIALTY": "Specialty", "STATE": "State",
        "AVG_COST_PER_CLAIM": "Avg cost/claim ($)",
        "TOTAL_BENEFICIARIES": "Patients"
    }
)
fig_scatter.update_traces(marker=dict(size=5, opacity=0.6))
layout = plot_layout(420)
layout["yaxis"]["tickformat"] = "$,.0f"
fig_scatter.update_layout(**layout)
st.plotly_chart(fig_scatter, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Section 2: Geographic + Distribution ─────────────────────────────
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown('<span class="section-label">Distribution</span>', unsafe_allow_html=True)
st.markdown("""
<div class="story-headline">Where anomalies concentrate.</div>
<div class="story-body">
  Anomalies are not evenly distributed. High-population states with more
  prescribers produce more flagged cases. The cost distribution reveals
  that anomalous prescribers cluster at the extreme high end — billing
  far more than their peers.
</div>
""", unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    state_counts = (
        fdf[fdf["IS_ANOMALY"] == 1]
        .groupby("STATE").size()
        .reset_index(name="Anomalies")
        .sort_values("Anomalies", ascending=True)
        .tail(12)
    )
    fig_bar = px.bar(
        state_counts, x="Anomalies", y="STATE", orientation="h",
        labels={"STATE": ""}
    )
    fig_bar.update_traces(marker_color=ACCENT, marker_line_width=0)
    layout_bar = plot_layout(360, "Anomalies by state")
    layout_bar["margin"]["l"] = 80
    fig_bar.update_layout(**layout_bar)
    st.plotly_chart(fig_bar, use_container_width=True)

with col_r:
    fig_hist = px.histogram(
        fdf, x="TOTAL_DRUG_COST", color="Status", nbins=60,
        color_discrete_map={"Normal": BLUE_MID, "Anomaly": RED},
        labels={"TOTAL_DRUG_COST": "Total drug cost ($)"}
    )
    fig_hist.update_traces(opacity=0.75)
    layout_hist = plot_layout(360, "Drug cost distribution")
    layout_hist["barmode"] = "overlay"
    layout_hist["xaxis"]["tickformat"] = "$,.0f"
    layout_hist["xaxis"]["tickfont"]["size"] = 10
    fig_hist.update_layout(**layout_hist)
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Section 3: Box plot ───────────────────────────────────────────────
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown('<span class="section-label">By specialty</span>', unsafe_allow_html=True)
st.markdown("""
<div class="story-headline">Specialty context matters.</div>
<div class="story-body">
  An oncologist billing $10,000 per claim may be entirely normal — cancer drugs
  are expensive. The same cost from a family practice doctor is a red flag.
  This chart shows how cost-per-claim varies by specialty, with anomalies
  overlaid as red dots above the normal range.
</div>
""", unsafe_allow_html=True)

top_specs = (
    fdf.groupby("SPECIALTY").size()
    .sort_values(ascending=False).head(8).index.tolist()
)
box_df = fdf[fdf["SPECIALTY"].isin(top_specs)]
fig_box = px.box(
    box_df, x="SPECIALTY", y="AVG_COST_PER_CLAIM", color="Status",
    color_discrete_map={"Normal": BLUE_MID, "Anomaly": RED},
    labels={"AVG_COST_PER_CLAIM": "Avg cost per claim ($)", "SPECIALTY": ""}
)
layout_box = plot_layout(400, "Cost per claim by specialty")
layout_box["xaxis"]["tickangle"] = -25
layout_box["xaxis"]["showgrid"] = False
layout_box["yaxis"]["tickformat"] = "$,.0f"
fig_box.update_layout(**layout_box)
st.plotly_chart(fig_box, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Section 4: Findings table ─────────────────────────────────────────
st.markdown('<div class="story-section">', unsafe_allow_html=True)
st.markdown('<span class="section-label">Findings</span>', unsafe_allow_html=True)

anomaly_count_filtered = len(fdf[fdf["IS_ANOMALY"] == 1])
st.markdown(f"""
<div class="story-headline">{anomaly_count_filtered} prescribers flagged.</div>
<div class="story-body">
  Sorted by anomaly severity — the most statistically isolated prescribers
  appear first. A lower anomaly score indicates greater isolation from the
  normal cluster. These cases warrant further human investigation before
  any conclusions are drawn.
</div>
""", unsafe_allow_html=True)

adf = fdf[fdf["IS_ANOMALY"] == 1].sort_values("ANOMALY_SCORE_RAW").copy()

display = adf[[
    "LAST_NAME", "FIRST_NAME", "STATE", "SPECIALTY",
    "TOTAL_CLAIMS", "TOTAL_DRUG_COST",
    "AVG_COST_PER_CLAIM", "UNIQUE_DRUGS_PRESCRIBED",
    "ANOMALY_SCORE_RAW"
]].copy()

display.columns = [
    "Last name", "First name", "State", "Specialty",
    "Total claims", "Total drug cost",
    "Avg cost / claim", "Unique drugs", "Anomaly score"
]
display["Total drug cost"] = display["Total drug cost"].map("${:,.0f}".format)
display["Avg cost / claim"] = display["Avg cost / claim"].map("${:,.0f}".format)
display["Total claims"] = display["Total claims"].map("{:,.0f}".format)
display["Anomaly score"] = display["Anomaly score"].map("{:.4f}".format)

st.dataframe(display, use_container_width=True, height=450)
st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  <div class="footer-left">
    Built by <strong>Nupur Gudigar</strong><br>
    Data: CMS Medicare Part D 2023 &nbsp;·&nbsp;
    Model: Isolation Forest &nbsp;·&nbsp;
    Stack: Snowflake · dbt · Airflow · Great Expectations · Streamlit
  </div>
  <div class="footer-right">
    <a href="https://github.com/Nupur-Gudigar" target="_blank">GitHub</a>
    <a href="https://www.linkedin.com/in/nupur-gudigar" target="_blank">LinkedIn</a>
    <a href="mailto:nupurgudigar.tech@gmail.com">Email</a>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)