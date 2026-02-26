import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from models.simulation import simulate_tariff_impact, compare_scenarios, get_forecast_series
from components.charts import (
    import_trend_chart, price_trend_chart, tariff_impact_bar,
    dependency_gauge, forecast_chart, scenario_heatmap
)
# Auto-generate data if not present
if not os.path.exists('data/cpo_data.csv'):
    import subprocess
    subprocess.run(['python', 'data/generate_data.py'])
# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Palm Oil Tariff Impact Simulator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── DESIGN SYSTEM ─────────────────────────────────────────────────────────────
# Palette
# --navy:       #1B2A4A   (primary text, sidebar bg)
# --teal:       #2E7D82   (accent, active elements)
# --teal-light: #EBF4F5   (tinted backgrounds)
# --red:        #B94040   (warning, impact)
# --amber:      #A0622A   (moderate alerts)
# --green:      #2D6A4F   (positive delta)
# --bg:         #F7F8FA   (page background)
# --surface:    #FFFFFF   (cards)
# --border:     #DDE1E7   (dividers, card borders)
# --text-body:  #374151   (body copy)
# --text-muted: #6B7280   (labels, captions)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Source+Sans+3:wght@300;400;500;600&display=swap');

:root {
    --navy:       #1B2A4A;
    --teal:       #2E7D82;
    --teal-light: #EBF4F5;
    --teal-mid:   #C2DCE0;
    --red:        #B94040;
    --red-light:  #FDF1F1;
    --amber:      #A0622A;
    --amber-light:#FDF6EE;
    --green:      #2D6A4F;
    --green-light:#EDF5F0;
    --bg:         #F7F8FA;
    --surface:    #FFFFFF;
    --border:     #DDE1E7;
    --border-dark:#C4CAD4;
    --text:       #1B2A4A;
    --text-body:  #374151;
    --text-muted: #6B7280;
    --text-faint: #9CA3AF;
}

/* ── RESET ── */
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'Source Sans 3', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text-body) !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background-color: var(--navy) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * {
    color: #C8D3E8 !important;
}
[data-testid="stSidebar"] .stSlider > label,
[data-testid="stSidebar"] .stMultiSelect > label,
[data-testid="stSidebar"] .stSelectSlider > label {
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    color: #93A5C4 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
[data-testid="stSidebar"] hr {
    border-color: #2D3F5E !important;
    margin: 16px 0 !important;
}
[data-testid="stSidebar"] h3 {
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: #5A7099 !important;
    margin: 20px 0 10px 0 !important;
}

/* ── TOP NAV BAR ── */
.top-nav {
    background: var(--navy);
    padding: 10px 0 10px 0;
    margin-bottom: 0;
    display: flex;
    align-items: center;
    gap: 16px;
}
.top-nav .institution {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #93A5C4;
}
.top-nav .divider { color: #2D3F5E; }
.top-nav .course {
    font-size: 0.72rem;
    color: #5A7099;
    letter-spacing: 0.5px;
}

/* ── PAGE HEADER ── */
.page-header {
    background: var(--surface);
    border-bottom: 2px solid var(--navy);
    padding: 28px 0 22px 0;
    margin-bottom: 24px;
}
.page-header .report-type {
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--teal);
    margin-bottom: 6px;
}
.page-header h1 {
    font-family: 'Source Serif 4', serif !important;
    font-size: 1.85rem !important;
    font-weight: 700 !important;
    color: var(--navy) !important;
    margin: 0 0 6px 0 !important;
    line-height: 1.15 !important;
    letter-spacing: -0.3px !important;
}
.page-header .subtitle {
    font-size: 0.9rem;
    color: var(--text-muted);
    font-weight: 400;
    letter-spacing: 0.1px;
}
.page-header .meta-row {
    display: flex;
    gap: 20px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
}
.page-header .meta-item {
    font-size: 0.72rem;
    color: var(--text-faint);
    letter-spacing: 0.3px;
}
.page-header .meta-item strong {
    color: var(--text-muted);
    font-weight: 600;
}

/* ── STATUS BANNER ── */
.status-banner {
    padding: 10px 16px;
    border-radius: 4px;
    border-left: 4px solid;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.82rem;
    font-weight: 500;
}
.status-critical {
    background: var(--red-light);
    border-color: var(--red);
    color: #7A2B2B;
}
.status-elevated {
    background: var(--amber-light);
    border-color: var(--amber);
    color: #6B4020;
}
.status-stable {
    background: var(--green-light);
    border-color: var(--green);
    color: #1D4A35;
}
.status-label {
    font-weight: 700;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.status-sep { opacity: 0.3; }

/* ── SECTION HEADERS ── */
.section-header {
    margin: 28px 0 14px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}
.section-header h2 {
    font-family: 'Source Serif 4', serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: var(--navy) !important;
    margin: 0 !important;
    letter-spacing: -0.1px !important;
}
.section-header p {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin: 3px 0 0 0;
}

/* ── KPI CARDS ── */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 18px 18px 14px 18px;
    box-shadow: 0 1px 3px rgba(27,42,74,0.06);
    position: relative;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 6px 6px 0 0;
}
.kpi-teal::before   { background: var(--teal); }
.kpi-amber::before  { background: var(--amber); }
.kpi-red::before    { background: var(--red); }
.kpi-green::before  { background: var(--green); }

.kpi-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--text-muted);
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'Source Serif 4', serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    color: var(--navy);
    letter-spacing: -0.5px;
}
.kpi-unit {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 0.85rem;
    font-weight: 400;
    color: var(--text-muted);
    margin-left: 2px;
}
.kpi-delta {
    font-size: 0.73rem;
    margin-top: 6px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 4px;
}
.delta-pos-bad  { color: var(--red); }
.delta-pos-good { color: var(--green); }
.delta-neg-good { color: var(--green); }
.delta-neg-bad  { color: var(--red); }
.delta-neutral  { color: var(--text-faint); }

/* ── DEPENDENCY BAR ── */
.dep-section {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(27,42,74,0.06);
    height: 100%;
}
.dep-title {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--text-muted);
    margin-bottom: 14px;
}
.dep-value {
    font-family: 'Source Serif 4', serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: var(--navy);
    line-height: 1;
    letter-spacing: -1px;
    margin-bottom: 10px;
}
.dep-bar-track {
    background: var(--border);
    border-radius: 3px;
    height: 8px;
    width: 100%;
    overflow: hidden;
    margin-bottom: 6px;
}
.dep-bar-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.4s ease;
}
.dep-bar-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.62rem;
    color: var(--text-faint);
    margin-top: 4px;
}
.dep-stats {
    margin-top: 16px;
    padding-top: 14px;
    border-top: 1px solid var(--border);
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}
.dep-stat-label {
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: var(--text-faint);
    margin-bottom: 2px;
}
.dep-stat-val {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--navy);
}

/* ── INSIGHT PANELS ── */
.insight-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(27,42,74,0.06);
    height: 100%;
}
.insight-tag {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    padding: 3px 8px;
    border-radius: 3px;
    margin-bottom: 10px;
}
.tag-consumer { background: var(--teal-light); color: var(--teal); }
.tag-balanced { background: var(--amber-light); color: var(--amber); }
.tag-farmer   { background: var(--green-light); color: var(--green); }
.tag-outlook  { background: #EEF0F4; color: var(--navy); }

.insight-text {
    font-size: 0.83rem;
    line-height: 1.65;
    color: var(--text-body);
}
.insight-highlight {
    font-weight: 600;
    color: var(--navy);
}

/* ── CHART WRAPPERS ── */
.chart-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 4px 4px 0 4px;
    box-shadow: 0 1px 3px rgba(27,42,74,0.06);
}

/* ── DATA TABLE ── */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    overflow: hidden !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] button {
    background: var(--navy) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    padding: 8px 20px !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: #253D6A !important;
}

/* ── SIDEBAR BRAND ── */
.sidebar-brand {
    padding: 20px 0 16px 0;
    border-bottom: 1px solid #2D3F5E;
    margin-bottom: 4px;
}
.brand-title {
    font-family: 'Source Serif 4', serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #E8EDF5;
    line-height: 1.25;
    letter-spacing: -0.2px;
}
.brand-sub {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #5A7099;
    margin-top: 4px;
}

/* ── FOOTER ── */
.page-footer {
    margin-top: 32px;
    padding: 16px 0;
    border-top: 1px solid var(--border);
    font-size: 0.7rem;
    color: var(--text-faint);
    letter-spacing: 0.3px;
}

hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)


# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_historical():
    if os.path.exists('data/cpo_data.csv'):
        return pd.read_csv('data/cpo_data.csv', parse_dates=['date'])
    import subprocess
    subprocess.run(['python', 'data/generate_data.py'])
    return pd.read_csv('data/cpo_data.csv', parse_dates=['date'])

try:
    hist_df = load_historical()
    data_loaded = True
except Exception:
    data_loaded = False


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-title">Palm Oil Tariff<br>Impact Simulator</div>
        <div class="brand-sub">Economic Policy Platform</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Simulation Controls")
    tariff_rate = st.slider(
        "Customs Duty Rate (%)",
        min_value=0.0, max_value=100.0, value=16.5, step=0.5,
        help="India's current CPO customs duty is 16.5% (2025)"
    )
    global_price = st.slider(
        "Global CPO Price (USD / ton)",
        min_value=400.0, max_value=1800.0, value=1086.0, step=10.0,
        help="International CPO market price approx. USD 1,086/ton (Feb 2025)"
    )

    st.markdown("---")
    st.markdown("### Scenario Comparison")
    compare_tariffs = st.multiselect(
        "Select tariff rates to compare (%)",
        options=[0, 5, 10, 15, 16.5, 20, 27.5, 30, 50, 100],
        default=[0, 5, 10, 15, 27.5]
    )

    st.markdown("---")
    st.markdown("### Forecast Horizon")
    forecast_months = st.select_slider(
        "Months ahead",
        options=[3, 6, 12, 18, 24],
        value=12
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:0.65rem; color:#3D5278; line-height:2;">
        CSI3901 — TARP Assessment 2<br>
        VIT School of Computer Science<br>
        Winter Semester 2025–26<br><br>
        Raagesh A &nbsp;·&nbsp; 22MID0089<br>
        Monish Kumar S &nbsp;·&nbsp; 22MID0119<br>
        Sathish V &nbsp;·&nbsp; 22MID0160<br>
        Sanjay S &nbsp;·&nbsp; 22MID0189
    </div>
    """, unsafe_allow_html=True)


# ── SIMULATION ────────────────────────────────────────────────────────────────
result      = simulate_tariff_impact(tariff_rate, global_price)
forecast_df = get_forecast_series(tariff_rate, forecast_months)
scenario_df = compare_scenarios(compare_tariffs, global_price) if compare_tariffs else None


# ── PAGE HEADER ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div class="report-type">Policy Simulation Dashboard</div>
    <h1>Palm Oil Tariff Impact Simulator</h1>
    <div class="subtitle">Economic Policy Simulation &amp; Forecasting Dashboard &nbsp;&mdash;&nbsp; Crude Palm Oil (CPO) Import Analysis</div>
    <div class="meta-row">
        <div class="meta-item"><strong>Customs Duty</strong> &nbsp;{tariff_rate}%</div>
        <div class="meta-item"><strong>Global CPO Price</strong> &nbsp;USD {global_price:,.0f} / ton</div>
        <div class="meta-item"><strong>INR / USD</strong> &nbsp;84.00</div>
        <div class="meta-item"><strong>Reference Date</strong> &nbsp;February 2025</div>
        <div class="meta-item"><strong>Forecast Horizon</strong> &nbsp;{forecast_months} months</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── STATUS BANNER ─────────────────────────────────────────────────────────────
dep = result['import_dependency_pct']
if dep > 88:
    cls, level, detail = "status-critical", "Critical Dependency", "Import reliance exceeds safe threshold. Domestic production insufficient to buffer supply shocks."
elif dep > 75:
    cls, level, detail = "status-elevated", "Elevated Dependency", "Moderate import exposure. Monitor global price volatility and NMEO-OP production targets."
else:
    cls, level, detail = "status-stable", "Stable Dependency", "Import dependency within manageable range. Domestic cultivation trends are positive."

st.markdown(f"""
<div class="status-banner {cls}">
    <span class="status-label">{level}</span>
    <span class="status-sep">|</span>
    <span>{detail}</span>
</div>
""", unsafe_allow_html=True)


# ── KPI CARDS ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <h2>Key Economic Indicators</h2>
    <p>Simulated values at current tariff and global price settings</p>
</div>
""", unsafe_allow_html=True)

def delta_html(val, positive_is_bad=False):
    if abs(val) < 0.05:
        return '<span class="delta-neutral">No change vs. baseline</span>'
    arrow = "+" if val > 0 else ""
    if positive_is_bad:
        cls = "delta-pos-bad" if val > 0 else "delta-neg-good"
    else:
        cls = "delta-pos-good" if val > 0 else "delta-neg-bad"
    return f'<span class="{cls}">{arrow}{val:.1f}% vs. baseline</span>'

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card kpi-teal">
        <div class="kpi-label">Import Dependency</div>
        <div class="kpi-value">{result['import_dependency_pct']:.1f}<span class="kpi-unit">%</span></div>
        <div class="kpi-delta">{delta_html(result['import_dependency_change_pct'], True)}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card kpi-amber">
        <div class="kpi-label">Farmer Gate Price</div>
        <div class="kpi-value">&#8377;{result['farmer_price_inr']:.2f}<span class="kpi-unit">/kg</span></div>
        <div class="kpi-delta">{delta_html(result['farmer_price_change_pct'])}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card kpi-red">
        <div class="kpi-label">Consumer Retail Price</div>
        <div class="kpi-value">&#8377;{result['consumer_price_inr']:.1f}<span class="kpi-unit">/kg</span></div>
        <div class="kpi-delta">{delta_html(result['consumer_price_change_pct'], True)}</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card kpi-green">
        <div class="kpi-label">Cultivation Area</div>
        <div class="kpi-value">{result['cultivation_area_mha']:.3f}<span class="kpi-unit">Mha</span></div>
        <div class="kpi-delta">{delta_html(result['cultivation_change_pct'])}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)


# ── DEPENDENCY + FORECAST ─────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <h2>Forecasting Results</h2>
    <p>Import dependency assessment and forward projection under current simulation parameters</p>
</div>
""", unsafe_allow_html=True)

col_dep, col_fc = st.columns([1, 2])

with col_dep:
    bar_color = "#B94040" if dep > 88 else ("#A0622A" if dep > 75 else "#2E7D82")
    bar_width = min(dep, 100)
    st.markdown(f"""
    <div class="dep-section">
        <div class="dep-title">Import Dependency Ratio</div>
        <div class="dep-value">{dep:.1f}%</div>
        <div class="dep-bar-track">
            <div class="dep-bar-fill" style="width:{bar_width}%; background:{bar_color};"></div>
        </div>
        <div class="dep-bar-labels"><span>0%</span><span>Safe: 60%</span><span>100%</span></div>
        <div class="dep-stats">
            <div>
                <div class="dep-stat-label">Import Volume</div>
                <div class="dep-stat-val">{result['import_volume_mt']:.4f} MT</div>
            </div>
            <div>
                <div class="dep-stat-label">Domestic Prod.</div>
                <div class="dep-stat-val">{result['domestic_production_mt']:.4f} MT</div>
            </div>
            <div>
                <div class="dep-stat-label">vs. Baseline</div>
                <div class="dep-stat-val" style="color:{'#B94040' if result['import_dependency_change_pct']>0 else '#2D6A4F'}">{result['import_dependency_change_pct']:+.1f}%</div>
            </div>
            <div>
                <div class="dep-stat-label">Risk Level</div>
                <div class="dep-stat-val" style="color:{bar_color}">{'High' if dep>88 else ('Moderate' if dep>75 else 'Low')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_fc:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(forecast_chart(forecast_df), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── HISTORICAL DATA ───────────────────────────────────────────────────────────
if data_loaded:
    st.markdown("""
    <div class="section-header">
        <h2>Historical Trade Data</h2>
        <p>Monthly CPO import volumes, domestic production, and price trends — 2014 to 2025</p>
    </div>
    """, unsafe_allow_html=True)
    h1, h2 = st.columns(2)
    with h1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(import_trend_chart(hist_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with h2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(price_trend_chart(hist_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ── SCENARIO COMPARISON ───────────────────────────────────────────────────────
if scenario_df is not None and len(scenario_df) > 0:
    st.markdown("""
    <div class="section-header">
        <h2>Scenario Comparison</h2>
        <p>Side-by-side impact analysis across selected customs duty scenarios</p>
    </div>
    """, unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(tariff_impact_bar(scenario_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with s2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.plotly_chart(scenario_heatmap(scenario_df), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)

    dc = {
        'tariff_rate':'Tariff (%)',
        'import_volume_mt':'Import Vol (MT)',
        'domestic_production_mt':'Domestic Prod (MT)',
        'import_dependency_pct':'Import Dep (%)',
        'farmer_price_inr':'Farmer Price (Rs/kg)',
        'consumer_price_inr':'Consumer Price (Rs/kg)',
        'cultivation_area_mha':'Cultivation (Mha)'
    }
    tbl = scenario_df[list(dc.keys())].rename(columns=dc)
    st.dataframe(
        tbl.style
           .background_gradient(subset=['Import Dep (%)'], cmap='RdYlGn_r')
           .background_gradient(subset=['Consumer Price (Rs/kg)'], cmap='YlOrRd')
           .format({c: '{:.2f}' for c in tbl.select_dtypes('float').columns}),
        use_container_width=True, height=240
    )
    st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
    st.download_button(
        label="Download Scenario Report (CSV)",
        data=tbl.to_csv(index=False).encode(),
        file_name="cpo_tariff_scenario_report.csv",
        mime="text/csv"
    )


# ── POLICY INSIGHTS ───────────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <h2>Policy Insights</h2>
    <p>Automated interpretation of simulation results for evidence-based decision support</p>
</div>
""", unsafe_allow_html=True)

p1, p2 = st.columns(2)

with p1:
    if tariff_rate < 10:
        tag_cls, tag_txt = "tag-consumer", "Pro-Consumer"
        body = f"At a <span class='insight-highlight'>{tariff_rate}% customs duty</span>, import volumes remain high and consumer retail prices are suppressed. Domestic farmers receive minimal price support and farm-gate income is unlikely to improve. This scenario prioritises short-term consumer affordability at the cost of agricultural self-sufficiency and NMEO-OP targets."
    elif tariff_rate < 25:
        tag_cls, tag_txt = "tag-balanced", "Balanced Policy"
        body = f"At <span class='insight-highlight'>{tariff_rate}% duty</span>, the model projects a moderate equilibrium between farmer income protection and consumer price stability. Import dependency reduces marginally. This range is broadly aligned with India's NMEO-OP domestic cultivation objectives."
    else:
        tag_cls, tag_txt = "tag-farmer", "High Protection"
        body = f"At <span class='insight-highlight'>{tariff_rate}% duty</span>, domestic farmer prices rise significantly, providing strong income support. However, consumer retail prices are projected to reach <span class='insight-highlight'>Rs. {result['consumer_price_inr']:.0f}/kg</span>, representing a potential inflationary risk for low-income households."

    st.markdown(f"""
    <div class="insight-panel">
        <span class="insight-tag {tag_cls}">{tag_txt}</span>
        <div class="insight-text">{body}</div>
    </div>""", unsafe_allow_html=True)

with p2:
    outlook = "Significant expansion in oil palm cultivation is projected under this tariff regime. If sustained, domestic supply growth may begin reducing import dependency within a 3–5 year horizon, supporting NMEO-OP self-sufficiency goals." if result['cultivation_change_pct'] > 5 else "Minimal cultivation response is expected at this tariff level. Domestic production is unlikely to meaningfully substitute imports in the near-to-medium term without additional policy support."
    st.markdown(f"""
    <div class="insight-panel">
        <span class="insight-tag tag-outlook">Cultivation Outlook</span>
        <div class="insight-text">
            Projected oil palm cultivation area at <span class='insight-highlight'>{tariff_rate}% tariff</span>:
            <span class='insight-highlight'>{result['cultivation_area_mha']:.4f} Mha</span>
            (<span style="color:{'#2D6A4F' if result['cultivation_change_pct']>=0 else '#B94040'}">{result['cultivation_change_pct']:+.1f}%</span> vs. baseline).
            <br><br>{outlook}
        </div>
    </div>""", unsafe_allow_html=True)


# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-footer">
    CSI3901 &nbsp;/&nbsp; Technical Answers for Real World Problems — TARP Assessment 2 &nbsp;&nbsp;&middot;&nbsp;&nbsp;
    AI-Powered Import Impact Simulator for Palm Oil Tariffs &nbsp;&nbsp;&middot;&nbsp;&nbsp;
    Vellore Institute of Technology, School of Computer Science and Engineering &nbsp;&nbsp;&middot;&nbsp;&nbsp;
    Winter Semester 2025–26
</div>
""", unsafe_allow_html=True)