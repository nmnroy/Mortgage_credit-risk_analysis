"""
Mortgage Credit Risk & Macro Stress Testing Interactive Analytics Dashboard.

Provides portfolio risk officers, data analysts, and executive stakeholders
an interactive BI platform for exploring:
  - Portfolio Delinquency Dynamics & Roll Rates
  - Vintage Curves & Macro Shocks
  - Bivariate Risk Drivers & Multi-factor Heatmaps
  - Statistical PD Scorecard & Challenger Benchmark Models
  - Federal Reserve Severely Adverse Stress Testing Simulator

Run:
    streamlit run app.py
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

OUT = Path("outputs")

st.set_page_config(
    page_title="Mortgage Credit Risk & Stress Testing Platform",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #2a78d6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #111827;
    }
    .metric-label {
        font-size: 13px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-delta {
        font-size: 13px;
        color: #dc2626;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_csv(name: str):
    p = OUT / name
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


# Load Key Datasets
vintage_curves = load_csv("vintage_curves.csv")
calendar_d90 = load_csv("calendar_d90.csv")
risk_drivers = load_csv("risk_drivers.csv")
risk_grid = load_csv("risk_grid.csv")
pd_metrics = load_csv("pd_model_metrics.csv")
pd_coef = load_csv("pd_model_coefficients.csv")
pd_deciles = load_csv("pd_backtest_deciles.csv")
el_summary = load_csv("el_scorecard_summary.csv")
el_vintage = load_csv("el_vintage.csv")
stress_wf = load_csv("stress_waterfall.csv")
stress_vint = load_csv("stress_vintage.csv")
roll_rate = load_csv("roll_rate.csv")

# Header
st.title("🏦 Mortgage Credit Risk Analysis & Stress Testing Platform")
st.markdown(
    "**Portfolio Analytics & Quantitative Risk Platform** | Analyzing 250,000 Freddie Mac Mortgages across 5 Vintages "
    "under Basel & Federal Reserve Severely Adverse Stress Scenarios."
)

# Sidebar
st.sidebar.image("outputs/dashboard.png" if (OUT / "dashboard.png").exists() else None, use_container_width=True)
st.sidebar.markdown("### Portfolio Controls")
st.sidebar.info(
    "**Analyst:** Naman Roy\n\n"
    "**Target Asset:** Freddie Mac Single-Family Conforming Mortgages\n\n"
    "**Baseline Period:** Q1 2026\n\n"
    "**Stress Horizon:** Fed 2026 Severe Recession"
)

# KPI Bar
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Active Book Balance</div>
        <div class="metric-value">$25.8 Billion</div>
        <div class="metric-delta" style="color: #4b5563;">114,860 Active Loans</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">90+ Days Delinquent Rate</div>
        <div class="metric-value">0.75%</div>
        <div class="metric-delta">▲ 2.1x vs 24 Months Ago (0.36%)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">12-Month Expected Loss</div>
        <div class="metric-value">$12.5M (4.9 bps)</div>
        <div class="metric-delta">Scorecard PD Adjusted (AUC 0.90)</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card" style="border-left-color: #dc2626;">
        <div class="metric-label">Fed Severe Stressed Loss</div>
        <div class="metric-value">$128.6M (49.8 bps)</div>
        <div class="metric-delta">▲ 11.0x Baseline Loss</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# Navigation Tabs
tabs = st.tabs([
    "📊 Executive Summary",
    "📈 Vintage Dynamics & COVID Shock",
    "🎯 Risk Drivers & Heatmap",
    "🤖 PD Scorecard & Backtest",
    "⚡ Stress Test Simulator",
    "📋 Transition Matrices & LGD",
])

# Tab 1: Executive Summary
with tabs[0]:
    st.subheader("Executive Risk Assessment: The 2023 Vintage Vulnerability")
    st.markdown("""
    Four independent quantitative methodologies confirm that the **2023 origination vintage** represents the primary source of credit vulnerability in this book:
    """)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown("""
        | Analytical Lens | Quantitative Finding for 2023 Vintage | Credit Implication |
        |---|---|---|
        | **Vintage Curves** | At age 24m, defaults rise faster than all historical cohorts except 2019 (COVID). | High debt burdens and peak entry prices erode cash cushions. |
        | **Calendar Delinquency** | Highest share 90+ days late today (**1.24%**, up from 0.87% YoY). | Deterioration is active and compounding in a non-recessionary regime. |
        | **Expected Loss (EL)** | Represents 40% of active unpaid balance but **54%–60% of total 12M expected loss**. | Severe loss concentration requiring targeted risk provisioning. |
        | **Macro Stress Test** | **52% of 2023 loans fall underwater** under a 30% HPI decline, generating **62% of stressed loss**. | Extreme sensitivity to home price correction due to thin equity. |
        """)
    with c2:
        if (OUT / "stress_vintage.png").exists():
            st.image(str(OUT / "stress_vintage.png"), caption="Share of Active Portfolio vs Share of Stressed Loss", use_container_width=True)

    st.markdown("---")
    st.subheader("Key Portfolio Risk Metrics")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Scorecard Discrimination (AUC)", "0.9008", "+0.145 vs Segment PD")
    with m2:
        st.metric("Gini Coefficient", "0.8017", "Bank-Grade Separation")
    with m3:
        st.metric("Kolmogorov-Smirnov (KS)", "0.6435", "Top Decile Holds 79% of Bad Loans")

# Tab 2: Vintage Curves & Calendar Analysis
with tabs[1]:
    st.subheader("Cohort Delinquency Performance & Systemic Shock Tracking")
    vcol1, vcol2 = st.columns(2)

    with vcol1:
        st.markdown("### 1. Cumulative D90+ Rate by Loan Age (Months)")
        st.markdown("Tracks delinquency progression normalized by seasoned age. Notice the sharp spike in 2019 loans at age 12-24m when COVID occurred.")
        if (OUT / "vintage_curves.png").exists():
            st.image(str(OUT / "vintage_curves.png"), use_container_width=True)

    with vcol2:
        st.markdown("### 2. Calendar View: Systemic Shock vs Underwriting")
        st.markdown("Turning vintage curves sideways demonstrates that COVID hit **all vintages simultaneously** in Q2–Q3 2020, confirming a macro systemic shock rather than cohort underwriting weakness.")
        if (OUT / "calendar_d90.png").exists():
            st.image(str(OUT / "calendar_d90.png"), use_container_width=True)

    if not vintage_curves.empty:
        with st.expander("Explore Raw Vintage Curves Data"):
            st.dataframe(vintage_curves, use_container_width=True)

# Tab 3: Risk Drivers & Heatmap
with tabs[2]:
    st.subheader("Bivariate Risk Drivers & Non-Linear Risk Layering")
    rcol1, rcol2 = st.columns([1.1, 1])

    with rcol1:
        st.markdown("### Marginal Risk Lift across Core Underwriting Attributes")
        st.markdown("Lift is calculated as the bucket's 24-month delinquency rate divided by the portfolio average:")
        if (OUT / "risk_drivers_lift.png").exists():
            st.image(str(OUT / "risk_drivers_lift.png"), use_container_width=True)

    with rcol2:
        st.markdown("### Multi-Factor FICO × LTV Risk Matrix")
        st.markdown("Notice the compounding non-linear risk layering: default rates expand from **0.26%** (Prime FICO, Low LTV) to **7.42%** (Subprime, High LTV) — a **29x risk spread**.")
        if (OUT / "risk_grid_heatmap.png").exists():
            st.image(str(OUT / "risk_grid_heatmap.png"), use_container_width=True)

    if not risk_drivers.empty:
        with st.expander("View Risk Driver Lift Table"):
            st.dataframe(risk_drivers, use_container_width=True)

# Tab 4: Scorecard Modeling & Backtest
with tabs[3]:
    st.subheader("Statistical Probability of Default (PD) Scorecard")
    st.markdown("""
    Built using Weight-of-Evidence / Monotonic Binning and Logistic Regression with Out-of-Time validation (train: 2016–2023 snapshots; test: 2024–2025 snapshots).
    """)

    sc1, sc2 = st.columns(2)

    with sc1:
        st.markdown("### Model Benchmark Comparison")
        if not pd_metrics.empty:
            st.dataframe(pd_metrics, use_container_width=True)
        if (OUT / "pd_calibration.png").exists():
            st.image(str(OUT / "pd_calibration.png"), caption="Decile Calibration: Predicted vs Actual Default Rate", use_container_width=True)

    with sc2:
        st.markdown("### Scorecard Out-of-Time Calibration over Time")
        if (OUT / "pd_backtest_time.png").exists():
            st.image(str(OUT / "pd_backtest_time.png"), caption="Backtest Stability Across Snapshots", use_container_width=True)
        if not pd_coef.empty:
            with st.expander("Top Feature Odds Ratios (Scorecard Coefficients)"):
                st.dataframe(pd_coef.sort_values("odds_ratio", ascending=False), use_container_width=True)

# Tab 5: Stress Test Simulator
with tabs[4]:
    st.subheader("Federal Reserve Severely Adverse Macroeconomic Stress Test")
    st.markdown("""
    Simulate the Federal Reserve Comprehensive Capital Analysis and Review (CCAR) Severely Adverse Scenario:
    Unemployment jumping from 4.5% to 10.0%, coupled with a 30% nationwide decline in home prices.
    """)

    sim1, sim2 = st.columns([1, 1.2])

    with sim1:
        st.markdown("### Interactive Stress Levers")
        hpi_drop = st.slider("House Price Index (HPI) Shock (%)", min_value=10, max_value=45, value=30, step=5)
        ue_mult = st.slider("Unemployment Stress PD Multiplier", min_value=1.0, max_value=4.0, value=2.2, step=0.2)
        underwater_mult = st.slider("Underwater Loan Default Multiplier", min_value=1.0, max_value=3.5, value=2.0, step=0.2)

        base_loss = 11.7
        ue_added = base_loss * (ue_mult - 1.0)
        neg_added = 15.0 * (hpi_drop / 30.0) * (underwater_mult / 2.0)
        conv_added = 35.0 * (hpi_drop / 30.0)
        sev_added = 42.0 * (hpi_drop / 30.0)
        simulated_loss = base_loss + ue_added + neg_added + conv_added + sev_added

        st.markdown(f"""
        <div style="background-color: #fef2f2; padding: 16px; border-radius: 8px; border-left: 4px solid #ef4444;">
            <div style="font-size: 14px; font-weight: 600; color: #991b1b;">SIMULATED 12M STRESSED LOSS</div>
            <div style="font-size: 32px; font-weight: 800; color: #b91c1c;">${simulated_loss:.1f} Million</div>
            <div style="font-size: 14px; color: #7f1d1d;">Loss Rate: {(simulated_loss / 258.0):.1f} bps | {simulated_loss/base_loss:.1f}x Baseline</div>
        </div>
        """, unsafe_allow_html=True)

    with sim2:
        st.markdown("### Stress Loss Waterfall Breakdown")
        if (OUT / "stress_waterfall.png").exists():
            st.image(str(OUT / "stress_waterfall.png"), caption="Official Fed Severely Adverse Loss Waterfall", use_container_width=True)

# Tab 6: Roll Rates & LGD
with tabs[5]:
    st.subheader("Transition Dynamics (Roll Rates) & Loss Given Default (LGD)")
    tcol1, tcol2 = st.columns(2)

    with tcol1:
        st.markdown("### Delinquency Roll-Rate Dynamics: Normal vs COVID")
        st.markdown("""
        - **30d → 60d Roll Rate:** Rose from **15.5%** (Normal) to **37.7%** (COVID).
        - **60d → 90+ Roll Rate:** Rose from **37.1%** to **64.1%**.
        - **90+ → Default Rate:** Dropped from **1.06%** to **0.09%**, as federal foreclosure moratorium and CARES Act forbearance prevented terminal liquidation.
        """)
        if not roll_rate.empty:
            st.dataframe(roll_rate, use_container_width=True)

    with tcol2:
        st.markdown("### Loss Given Default (LGD) & Severity Drivers")
        st.markdown("""
        From 485 empirical liquidation events:
        - **Overall Portfolio Severity:** 23.7% of balance at default.
        - **Judicial Foreclosure States:** **30.8%** vs **19.6%** in non-judicial states (extended carrying timelines and legal expense).
        - **Mortgage Insurance Benefit:** Mitigates severity from **28.8%** down to **15.9%**.
        """)
        lgd_df = load_csv("lgd_summary.csv")
        if not lgd_df.empty:
            st.dataframe(lgd_df, use_container_width=True)

st.markdown("---")
st.markdown("© 2026 **Naman Roy** | Portfolio Credit Risk Analysis & Quantitative Stress Testing.")
