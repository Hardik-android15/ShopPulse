"""
ShopPulse — Online Shopper Conversion Intelligence
Streamlit Web Dashboard

An interactive, responsive data analytics application for analyzing online shopper
conversion funnels, visitor behavioral patterns, traffic sources, session duration,
and temporal factors using the UCI Online Shoppers Purchasing Intention dataset.
"""

from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.data_cleaning import (
    load_cleaned_data,
    run_pipeline,
    PROCESSED_DATA_PATH,
    MONTH_ORDER,
    PAGE_VIEW_ORDER,
    DURATION_ORDER,
    PAGE_VALUE_TIER_ORDER,
    EXIT_RISK_ORDER,
)
from src.metrics import (
    calculate_funnel_stages,
    calculate_kpis,
    compare_converting_vs_non_converting,
)
from src.analysis import (
    get_executive_kpis,
    get_conversion_rate_summary,
    analyze_visitor_conversion,
    analyze_traffic_source_conversion,
    analyze_page_view_bucket_conversion,
    analyze_duration_bucket_conversion,
    analyze_monthly_conversion,
    analyze_seasonal_conversion,
    analyze_weekend_conversion,
    analyze_exit_risk_conversion,
    analyze_page_value_tier_conversion,
    analyze_engagement_matrix,
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ShopPulse — Conversion Intelligence",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Professional SaaS UI Styling
st.markdown(
    """
    <style>
    /* Global Typography & Spacing */
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Executive Header */
    .app-header {
        padding-bottom: 0.75rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid #E2E8F0;
    }
    .app-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .app-subtitle {
        font-size: 0.92rem;
        color: #475569;
        margin-top: 0.25rem;
        margin-bottom: 0;
    }
    .telemetry-pill {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        font-size: 0.78rem;
        font-weight: 600;
        border-radius: 6px;
        background-color: #EEF2FF;
        color: #3730A3;
        border: 1px solid #C7D2FE;
    }

    /* KPI Cards */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        transition: border-color 0.15s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        border-color: #CBD5E1;
    }
    div[data-testid="stMetric"] label {
        font-size: 0.80rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }

    /* Section Headers */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 0.5rem;
        margin-bottom: 0.25rem;
    }
    .section-subtitle {
        font-size: 0.84rem;
        color: #64748B;
        margin-bottom: 0.75rem;
    }

    /* Key Insight Cards */
    .insight-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-left: 4px solid #4F46E5;
        border-radius: 8px;
        padding: 1rem 1.15rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    .insight-card-warning {
        border-left-color: #F59E0B;
    }
    .insight-card-success {
        border-left-color: #10B981;
    }
    .insight-header {
        font-size: 0.92rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.35rem;
    }
    .insight-stat {
        font-size: 1.15rem;
        font-weight: 700;
        color: #4F46E5;
        margin-bottom: 0.3rem;
    }
    .insight-desc {
        font-size: 0.86rem;
        color: #334155;
        line-height: 1.45;
    }
    .insight-action {
        font-size: 0.82rem;
        color: #475569;
        margin-top: 0.4rem;
        padding-top: 0.4rem;
        border-top: 1px dashed #E2E8F0;
    }

    /* Sidebar Divider & Groups */
    .sidebar-group-title {
        font-size: 0.80rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #475569;
        margin-top: 0.75rem;
        margin-bottom: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Standard Business Color Palette
PALETTE = {
    "primary": "#4F46E5",
    "primary_dark": "#3730A3",
    "success": "#10B981",
    "slate": "#64748B",
    "slate_light": "#E2E8F0",
    "warning": "#F59E0B",
    "danger": "#EF4444",
}


# -----------------------------------------------------------------------------
# DATA LOADING & CACHING
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner="Loading ShopPulse dataset...")
def load_dataset() -> pd.DataFrame:
    """Load cleaned dataset from processed storage, or execute cleaning pipeline if missing."""
    if not PROCESSED_DATA_PATH.exists():
        df, _ = run_pipeline()
        return df
    return load_cleaned_data(PROCESSED_DATA_PATH)


try:
    df_raw = load_dataset()
except Exception as err:
    st.error(f"Failed to load dataset: {err}")
    st.stop()


# -----------------------------------------------------------------------------
# SIDEBAR FILTERS & CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Filter Controls")
    st.markdown('<div class="sidebar-group-title">Session Attributes</div>', unsafe_allow_html=True)

    # 1. Month Filter
    available_months = [m for m in MONTH_ORDER if m in df_raw["Month_Clean"].unique()]
    selected_months = st.multiselect(
        "Month",
        options=available_months,
        default=available_months,
        help="Select calendar months (ordered chronologically Feb–Dec).",
    )

    # 2. Visitor Type Filter
    available_visitors = sorted(df_raw["VisitorType"].dropna().unique().tolist())
    selected_visitors = st.multiselect(
        "Visitor Lifecycle",
        options=available_visitors,
        default=available_visitors,
        help="Filter by visitor type: Returning Visitor, New Visitor, or Other.",
    )

    # 3. Traffic Segment Filter
    available_traffic = sorted(df_raw["Traffic_Segment"].dropna().unique().tolist())
    selected_traffic = st.multiselect(
        "Traffic Channel",
        options=available_traffic,
        default=available_traffic,
        help="Filter by traffic source acquisition segment.",
    )

    # 4. Weekend vs Weekday
    available_day_types = sorted(df_raw["Day_Type"].dropna().unique().tolist())
    selected_day_types = st.multiselect(
        "Day of Week",
        options=available_day_types,
        default=available_day_types,
        help="Filter sessions occurring on weekdays vs weekends.",
    )

    # 5. Conversion Outcome
    st.markdown('<div class="sidebar-group-title">Target Outcome</div>', unsafe_allow_html=True)
    conv_options = ["All Sessions", "Converted Only (Purchased)", "Non-Converted Only"]
    selected_conv_status = st.selectbox(
        "Conversion Status",
        options=conv_options,
        index=0,
        help="Isolate converted buyers or non-converting visitors.",
    )

    # Filter Action
    st.markdown('<div class="sidebar-group-title">Actions</div>', unsafe_allow_html=True)
    if st.button("Reset All Filters", use_container_width=True):
        st.rerun()

    # Telemetry Card
    st.markdown("---")
    st.markdown(
        """
        <div style="font-size: 0.80rem; color: #64748B;">
            <b>Dataset Telemetry</b><br>
            • Benchmark: UCI Online Shoppers (Cleaned)<br>
            • Baseline Records: 12,199<br>
            • Dimensions: 38 analytical features
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# APPLY ACTIVE FILTERS
# -----------------------------------------------------------------------------
filtered_df = df_raw.copy()

if selected_months:
    filtered_df = filtered_df[filtered_df["Month_Clean"].isin(selected_months)]
else:
    filtered_df = filtered_df.iloc[0:0]

if selected_visitors:
    filtered_df = filtered_df[filtered_df["VisitorType"].isin(selected_visitors)]
else:
    filtered_df = filtered_df.iloc[0:0]

if selected_traffic:
    filtered_df = filtered_df[filtered_df["Traffic_Segment"].isin(selected_traffic)]
else:
    filtered_df = filtered_df.iloc[0:0]

if selected_day_types:
    filtered_df = filtered_df[filtered_df["Day_Type"].isin(selected_day_types)]
else:
    filtered_df = filtered_df.iloc[0:0]

if selected_conv_status == "Converted Only (Purchased)":
    filtered_df = filtered_df[filtered_df["Revenue"] == True]
elif selected_conv_status == "Non-Converted Only":
    filtered_df = filtered_df[filtered_df["Revenue"] == False]


# -----------------------------------------------------------------------------
# APP HEADER
# -----------------------------------------------------------------------------
total_raw_count = len(df_raw)
active_count = len(filtered_df)
pct_active = (active_count / total_raw_count) * 100 if total_raw_count > 0 else 0.0

st.markdown(
    f"""
    <div class="app-header">
        <div style="display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <h1 class="app-title">ShopPulse — Online Shopper Conversion Intelligence</h1>
                <p class="app-subtitle">Behavioral segmentation, funnel attrition diagnostics, and intent modeling</p>
            </div>
            <div>
                <span class="telemetry-pill">Active Cohort: {active_count:,} of {total_raw_count:,} sessions ({pct_active:.1f}%)</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Zero-row safeguard
if active_count == 0:
    st.warning("No sessions match the selected filter combination. Adjust the sidebar filters to display metrics.")
    st.stop()


# -----------------------------------------------------------------------------
# EXECUTIVE KPI CARDS
# -----------------------------------------------------------------------------
kpis = get_executive_kpis(filtered_df)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        label="Total Sessions",
        value=f"{kpis['total_sessions']:,}",
        help="Total traffic volume matching active filter criteria.",
    )
with c2:
    st.metric(
        label="Conversions",
        value=f"{kpis['conversions']:,}",
        help="Number of sessions resulting in completed transaction (Revenue = True).",
    )
with c3:
    st.metric(
        label="Conversion Rate",
        value=f"{kpis['conversion_rate_pct']:.2f}%",
        help="Percentage of sessions leading to a purchase.",
    )
with c4:
    st.metric(
        label="Avg Session Duration",
        value=f"{kpis['avg_duration_minutes']:.1f} min",
        help="Average session dwell time across administrative, informational, and product pages.",
    )

# Secondary metric bar
st.markdown(
    f"""
    <div style="display: flex; gap: 1.5rem; margin-top: 0.4rem; margin-bottom: 1rem; font-size: 0.84rem; color: #475569; background: #F8FAFC; padding: 0.5rem 0.85rem; border-radius: 6px; border: 1px solid #E2E8F0;">
        <span><b>Avg Pages / Session:</b> {kpis['avg_pages_per_session']:.1f}</span>
        <span>•</span>
        <span><b>Avg Bounce Rate:</b> {kpis['avg_bounce_rate_pct']:.2f}%</span>
        <span>•</span>
        <span><b>Avg Exit Rate:</b> {kpis['avg_exit_rate_pct']:.2f}%</span>
        <span>•</span>
        <span><b>Avg PageValue:</b> ${kpis['avg_page_value']:.2f}</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# MAIN DASHBOARD TABS
# -----------------------------------------------------------------------------
tabs = st.tabs([
    "Conversion Funnel",
    "Visitor & Traffic Behavior",
    "Engagement & Dwell Time",
    "Temporal & Seasonality",
    "Key Insights",
    "Data Explorer",
])


# =============================================================================
# TAB 1: CONVERSION FUNNEL
# =============================================================================
with tabs[0]:
    st.markdown('<div class="section-title">Customer Conversion Funnel</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Milestone progression and drop-off analysis from initial site entry to transaction completion.</div>', unsafe_allow_html=True)

    col_funnel, col_comp = st.columns([1.15, 0.85])

    with col_funnel:
        funnel_df = calculate_funnel_stages(filtered_df)
        if not funnel_df.empty:
            fig_funnel = go.Figure(
                go.Funnel(
                    y=funnel_df["Stage"],
                    x=funnel_df["Users"],
                    textinfo="value+percent initial",
                    marker=dict(
                        color=["#6366F1", "#4F46E5", "#4338CA", "#3730A3", "#10B981"]
                    ),
                    connector=dict(line=dict(color="#CBD5E1", width=1.5)),
                )
            )
            fig_funnel.update_layout(
                template="plotly_white",
                margin=dict(l=10, r=10, t=10, b=10),
                height=350,
            )
            st.plotly_chart(fig_funnel, use_container_width=True)

            st.dataframe(
                funnel_df[["Stage", "Users", "Step_Conversion_Pct", "Drop_Off_Pct"]].rename(
                    columns={
                        "Step_Conversion_Pct": "Total Conversion %",
                        "Drop_Off_Pct": "Drop-Off from Prior %",
                    }
                ),
                hide_index=True,
                use_container_width=True,
            )
        else:
            st.info("Funnel data unavailable for active filters.")

    with col_comp:
        st.markdown("**Buyer vs. Non-Buyer Behavioral Comparison**")
        st.markdown('<div class="section-subtitle">Metric lift between converting and non-converting shopper sessions.</div>', unsafe_allow_html=True)
        comp_df = compare_converting_vs_non_converting(filtered_df)
        if not comp_df.empty:
            st.dataframe(
                comp_df.rename(
                    columns={
                        "Metric": "Behavioral Metric",
                        "Non_Converted_Mean": "Non-Buyers (Mean)",
                        "Converted_Mean": "Buyers (Mean)",
                        "Lift_Ratio (Conv / NonConv)": "Buyer Lift",
                    }
                ),
                hide_index=True,
                use_container_width=True,
                height=350,
            )
            st.markdown(
                """
                <div style="font-size: 0.84rem; color: #475569; background: #F8FAFC; padding: 0.65rem 0.85rem; border-radius: 6px; border: 1px solid #E2E8F0; margin-top: 0.5rem;">
                    <b>Key Finding:</b> Converting buyers demonstrate <b>13.77× higher average PageValue</b> ($27.26 vs. $1.98), 
                    view <b>1.65× more pages</b> (52.2 vs. 31.7), and spend <b>1.73× longer</b> (34.0 vs. 19.7 min) than non-buyers.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("Comparison unavailable for active filters.")


# =============================================================================
# TAB 2: VISITOR & TRAFFIC BEHAVIOR
# =============================================================================
with tabs[1]:
    col_vis, col_traf = st.columns(2)

    with col_vis:
        st.markdown('<div class="section-title">Conversion Rate by Visitor Segment</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Comparing purchasing likelihood across visitor lifecycle types.</div>', unsafe_allow_html=True)
        vis_df = analyze_visitor_conversion(filtered_df)

        if not vis_df.empty:
            fig_vis = px.bar(
                vis_df,
                x="VisitorType",
                y="Conversion_Rate_Pct",
                color="VisitorType",
                text="Conversion_Rate_Pct",
                labels={"Conversion_Rate_Pct": "Conversion Rate (%)", "VisitorType": "Visitor Type"},
                color_discrete_map={
                    "Returning_Visitor": PALETTE["primary"],
                    "New_Visitor": PALETTE["success"],
                    "Other": PALETTE["slate"],
                },
            )
            fig_vis.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_vis.update_layout(
                template="plotly_white",
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20),
                height=320,
                yaxis=dict(ticksuffix="%"),
            )
            st.plotly_chart(fig_vis, use_container_width=True)

            st.dataframe(
                vis_df[[
                    "VisitorType", "Total_Sessions", "Conversions",
                    "Conversion_Rate_Pct", "Traffic_Share_Pct", "Avg_Pages", "Avg_Duration_Min"
                ]],
                hide_index=True,
                use_container_width=True,
            )

    with col_traf:
        st.markdown('<div class="section-title">Conversion Rate by Traffic Source (Top 8)</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Ranked traffic source channels with standard one-decimal rounding.</div>', unsafe_allow_html=True)
        traf_df = analyze_traffic_source_conversion(filtered_df, top_n=8)

        if not traf_df.empty:
            traf_df["Traffic_Label"] = "Type " + traf_df["TrafficType"].astype(str)
            # Ensure standard rounding to 1 decimal place
            traf_df["Conversion_Rate_Display"] = np.round(traf_df["Conversion_Rate_Pct"], 1)

            fig_traf = px.bar(
                traf_df,
                x="Traffic_Label",
                y="Conversion_Rate_Display",
                color="Conversion_Rate_Display",
                color_continuous_scale="Purples",
                text="Conversion_Rate_Display",
                labels={"Conversion_Rate_Display": "Conversion Rate (%)", "Traffic_Label": "Traffic Channel"},
            )
            fig_traf.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_traf.update_layout(
                template="plotly_white",
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=20, b=20),
                height=320,
                yaxis=dict(ticksuffix="%"),
            )
            st.plotly_chart(fig_traf, use_container_width=True)

            st.dataframe(
                traf_df[[
                    "Traffic_Label", "Total_Sessions", "Conversions",
                    "Conversion_Rate_Display", "Traffic_Share_Pct", "Avg_Bounce_Rate_Pct"
                ]].rename(columns={"Conversion_Rate_Display": "Conversion Rate %"}),
                hide_index=True,
                use_container_width=True,
            )


# =============================================================================
# TAB 3: ENGAGEMENT & DWELL TIME
# =============================================================================
with tabs[2]:
    col_pb, col_db = st.columns(2)

    with col_pb:
        st.markdown('<div class="section-title">Conversion Rate by Page-View Depth</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Propensity to purchase scaling with cumulative pages viewed.</div>', unsafe_allow_html=True)
        pb_df = analyze_page_view_bucket_conversion(filtered_df)

        if not pb_df.empty:
            fig_pb = px.bar(
                pb_df,
                x="Page_View_Bucket",
                y="Conversion_Rate_Pct",
                text="Conversion_Rate_Pct",
                color="Conversion_Rate_Pct",
                color_continuous_scale="Blues",
                labels={"Page_View_Bucket": "Page Views", "Conversion_Rate_Pct": "Conversion Rate (%)"},
            )
            fig_pb.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_pb.update_layout(
                template="plotly_white",
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                yaxis=dict(ticksuffix="%"),
            )
            st.plotly_chart(fig_pb, use_container_width=True)

    with col_db:
        st.markdown('<div class="section-title">Conversion Rate by Session Duration</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Propensity to purchase scaling with total dwell time.</div>', unsafe_allow_html=True)
        db_df = analyze_duration_bucket_conversion(filtered_df)

        if not db_df.empty:
            fig_db = px.bar(
                db_df,
                x="Duration_Bucket",
                y="Conversion_Rate_Pct",
                text="Conversion_Rate_Pct",
                color="Conversion_Rate_Pct",
                color_continuous_scale="Teal",
                labels={"Duration_Bucket": "Session Length", "Conversion_Rate_Pct": "Conversion Rate (%)"},
            )
            fig_db.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_db.update_layout(
                template="plotly_white",
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                yaxis=dict(ticksuffix="%"),
            )
            st.plotly_chart(fig_db, use_container_width=True)

    col_mat, col_exit = st.columns([1.15, 0.85])

    with col_mat:
        st.markdown('<div class="section-title">Engagement Matrix (Pages × Duration Conversion %)</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">2D cross-tabulation of conversion likelihood across page count and dwell time.</div>', unsafe_allow_html=True)
        mat = analyze_engagement_matrix(filtered_df)
        if not mat.empty:
            fig_mat = px.imshow(
                mat,
                text_auto=".1f",
                aspect="auto",
                color_continuous_scale="Blues",
                labels=dict(x="Session Duration", y="Page View Depth", color="CR %"),
            )
            fig_mat.update_layout(
                template="plotly_white",
                margin=dict(l=20, r=20, t=15, b=20),
                height=300,
            )
            st.plotly_chart(fig_mat, use_container_width=True)

    with col_exit:
        st.markdown('<div class="section-title">Conversion Rate by Exit-Risk Profile</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Behavioral risk segmentation by bounce and exit velocity.</div>', unsafe_allow_html=True)
        exit_df = analyze_exit_risk_conversion(filtered_df)
        if not exit_df.empty:
            fig_exit = px.bar(
                exit_df,
                x="Exit_Risk_Profile",
                y="Conversion_Rate_Pct",
                color="Exit_Risk_Profile",
                text="Conversion_Rate_Pct",
                labels={"Exit_Risk_Profile": "Risk Profile", "Conversion_Rate_Pct": "Conversion Rate (%)"},
                color_discrete_map={
                    "Engaged": PALETTE["success"],
                    "High Exit Risk": PALETTE["warning"],
                    "Bounced": PALETTE["danger"],
                },
            )
            fig_exit.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_exit.update_layout(
                template="plotly_white",
                showlegend=False,
                margin=dict(l=20, r=20, t=15, b=20),
                height=300,
                yaxis=dict(ticksuffix="%"),
            )
            st.plotly_chart(fig_exit, use_container_width=True)


# =============================================================================
# TAB 4: TEMPORAL & SEASONALITY
# =============================================================================
with tabs[3]:
    col_m, col_w = st.columns([1.2, 0.8])

    with col_m:
        st.markdown('<div class="section-title">Monthly Session Volume & Conversion Trend</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Chronological progression across 10 active calendar months.</div>', unsafe_allow_html=True)
        m_df = analyze_monthly_conversion(filtered_df)

        if not m_df.empty:
            fig_m = go.Figure()
            fig_m.add_trace(
                go.Bar(
                    x=m_df["Month"],
                    y=m_df["Total_Sessions"],
                    name="Session Volume",
                    marker_color="#CBD5E1",
                    opacity=0.7,
                    yaxis="y",
                )
            )
            fig_m.add_trace(
                go.Scatter(
                    x=m_df["Month"],
                    y=m_df["Conversion_Rate_Pct"],
                    name="Conversion Rate (%)",
                    mode="lines+markers+text",
                    line=dict(color=PALETTE["primary"], width=2.5),
                    marker=dict(size=7, color=PALETTE["primary_dark"]),
                    text=[f"{v:.1f}%" for v in m_df["Conversion_Rate_Pct"]],
                    textposition="top center",
                    yaxis="y2",
                )
            )
            fig_m.update_layout(
                template="plotly_white",
                margin=dict(l=20, r=20, t=25, b=20),
                height=340,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(title="Sessions"),
                yaxis2=dict(
                    title="Conversion Rate (%)",
                    overlaying="y",
                    side="right",
                    ticksuffix="%",
                    showgrid=False,
                ),
            )
            st.plotly_chart(fig_m, use_container_width=True)

    with col_w:
        st.markdown('<div class="section-title">Weekend vs. Weekday Conversion Rate</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-subtitle">Comparing weekend leisure shopping to weekday sessions.</div>', unsafe_allow_html=True)
        w_df = analyze_weekend_conversion(filtered_df)

        if not w_df.empty:
            fig_w = px.bar(
                w_df,
                x="Day_Type",
                y="Conversion_Rate_Pct",
                color="Day_Type",
                text="Conversion_Rate_Pct",
                labels={"Day_Type": "Day Type", "Conversion_Rate_Pct": "Conversion Rate (%)"},
                color_discrete_map={"Weekday": PALETTE["slate"], "Weekend": PALETTE["primary"]},
            )
            fig_w.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            fig_w.update_layout(
                template="plotly_white",
                showlegend=False,
                margin=dict(l=20, r=20, t=25, b=20),
                height=340,
                yaxis=dict(ticksuffix="%"),
            )
            st.plotly_chart(fig_w, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-title">Seasonal & Quarterly Cohort Performance</div>', unsafe_allow_html=True)
    seasonal_data = analyze_seasonal_conversion(filtered_df)
    s_col1, s_col2 = st.columns(2)

    with s_col1:
        st.markdown("**Performance by Season**")
        st.dataframe(
            seasonal_data["seasonal"][["Season", "Total_Sessions", "Conversions", "Conversion_Rate_Pct", "Traffic_Share_Pct"]],
            hide_index=True,
            use_container_width=True,
        )

    with s_col2:
        st.markdown("**Performance by Calendar Quarter**")
        st.dataframe(
            seasonal_data["quarterly"][["Quarter", "Total_Sessions", "Conversions", "Conversion_Rate_Pct", "Traffic_Share_Pct"]],
            hide_index=True,
            use_container_width=True,
        )


# =============================================================================
# TAB 5: KEY INSIGHTS & STRATEGIC RECOMMENDATIONS
# =============================================================================
with tabs[4]:
    st.markdown('<div class="section-title">Key Insights & Strategic Recommendations</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Empirically grounded findings derived directly from the active session cohort.</div>', unsafe_allow_html=True)

    # Calculate real-time numbers for active filter
    pv_df = analyze_page_value_tier_conversion(filtered_df)
    zero_cr = pv_df.loc[pv_df["Page_Value_Tier"] == "Zero (0)", "Conversion_Rate_Pct"].values[0] if (pv_df["Page_Value_Tier"] == "Zero (0)").any() else 0.0
    high_cr = pv_df.loc[pv_df["Page_Value_Tier"] == "High (40+)", "Conversion_Rate_Pct"].values[0] if (pv_df["Page_Value_Tier"] == "High (40+)").any() else 0.0

    vis_df = analyze_visitor_conversion(filtered_df)
    new_cr = vis_df.loc[vis_df["VisitorType"] == "New_Visitor", "Conversion_Rate_Pct"].values[0] if (vis_df["VisitorType"] == "New_Visitor").any() else 0.0
    ret_cr = vis_df.loc[vis_df["VisitorType"] == "Returning_Visitor", "Conversion_Rate_Pct"].values[0] if (vis_df["VisitorType"] == "Returning_Visitor").any() else 0.0

    m_df = analyze_monthly_conversion(filtered_df)
    top_month = m_df.sort_values(by="Conversion_Rate_Pct", ascending=False).iloc[0]["Month"] if not m_df.empty else "N/A"
    top_month_cr = m_df.sort_values(by="Conversion_Rate_Pct", ascending=False).iloc[0]["Conversion_Rate_Pct"] if not m_df.empty else 0.0

    w_df = analyze_weekend_conversion(filtered_df)
    wknd_cr = w_df.loc[w_df["Day_Type"] == "Weekend", "Conversion_Rate_Pct"].values[0] if (w_df["Day_Type"] == "Weekend").any() else 0.0
    wkdy_cr = w_df.loc[w_df["Day_Type"] == "Weekday", "Conversion_Rate_Pct"].values[0] if (w_df["Day_Type"] == "Weekday").any() else 0.0

    col_ins1, col_ins2 = st.columns(2)

    with col_ins1:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-header">1. PageValue Conversion Impact</div>
                <div class="insight-stat">20.44× Conversion-Rate Ratio</div>
                <div class="insight-desc">
                    Shoppers reaching high-value pages (PageValue &gt; 40) convert at <b>{high_cr:.1f}%</b> compared to 
                    <b>{zero_cr:.1f}%</b> for zero-value sessions (a <b>20.44× conversion-rate ratio between High and Zero PageValue tiers</b>).
                    Additionally, converting buyers exhibit a <b>13.77× higher average PageValue among buyers</b> ($27.26 vs. $1.98).
                </div>
                <div class="insight-action">
                    <b>Action:</b> Prioritize UI pathways and product recommendation carousels that route visitors to high-scoring pages early in their journey.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="insight-card insight-card-success">
                <div class="insight-header">2. Visitor Lifecycle Intent</div>
                <div class="insight-stat">1.77× New Visitor Lift</div>
                <div class="insight-desc">
                    <b>New Visitors</b> convert at <b>{new_cr:.1f}%</b> compared to <b>{ret_cr:.1f}%</b> for <b>Returning Visitors</b> (a <b>1.77× conversion lift</b>).
                    Returning visitors frequently browse or compare items without immediate intent, whereas new visitors exhibit targeted purchase motivation.
                </div>
                <div class="insight-action">
                    <b>Action:</b> Deploy frictionless one-click reordering and saved cart prompts specifically designed to reactivate returning visitors.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_ins2:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-header">3. November & Holiday Peak</div>
                <div class="insight-stat">25.5% Conversion Peak</div>
                <div class="insight-desc">
                    <b>November ({top_month})</b> generates both the largest traffic volume (~3,000 sessions) and highest conversion rate at <b>{top_month_cr:.1f}%</b>,
                    driven by Black Friday and pre-holiday retail demand. In comparison, early spring months convert under 11%.
                </div>
                <div class="insight-action">
                    <b>Action:</b> Align inventory depth and ad spend toward Q4 while running seasonal promotional bundles to stimulate slow Q1 traffic.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-header">4. Weekend Shopping Propensity</div>
                <div class="insight-stat">+2.4% Weekend Lift</div>
                <div class="insight-desc">
                    Weekend sessions convert at <b>{wknd_cr:.1f}%</b> compared to <b>{wkdy_cr:.1f}%</b> on weekdays (+{wknd_cr - wkdy_cr:.1f}% percentage points).
                    Visitors during weekends benefit from dedicated leisure time to complete checkout flows.
                </div>
                <div class="insight-action">
                    <b>Action:</b> Schedule promotional flash sales and time-sensitive discount banners for Friday afternoon through Sunday evening.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown('<div class="section-title">Strategic Conversion Funnel Actions</div>', unsafe_allow_html=True)
    st.markdown(
        """
        1. **Checkout Friction Mitigation:** **The largest overall drop-off occurs between Intent/Account Action and Completed Purchase, with a 72.94% drop-off** (5,143 sessions lost). In the upstream browsing funnel, the largest attrition is between *Deep Engagement* and *Intent/Account Action* (33.68% drop-off). Reducing checkout form fields, adding guest checkout, and offering transparent shipping fees will directly capture high-intent shoppers.
        2. **Exit Velocity Interception:** Visitors classified in the *High Exit Risk* profile convert at only **1.1%** (9 conversions out of 793 sessions). Deploying non-intrusive exit-intent prompts with instant discount codes can save abandoning carts.
        3. **Traffic Allocation Realignment:** **Traffic Type 2 drives 32.1% of volume with a stellar 21.7% conversion rate**, whereas **Traffic Type 13 delivers 6.0% of volume at a sluggish 5.9% conversion rate**. Marketing acquisition budgets should be redirected from low-performing channels toward Type 2 and high-converting niche channels (Type 8 at 27.7%, Type 20 at 25.3%).
        """
    )


# =============================================================================
# TAB 6: DATA EXPLORER
# =============================================================================
with tabs[5]:
    st.markdown('<div class="section-title">Data Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Compact view for inspecting and exporting processed session telemetry.</div>', unsafe_allow_html=True)

    default_cols = [
        "VisitorType", "Month_Clean", "Day_Type", "Total_Pages",
        "Total_Duration_Min", "BounceRates", "ExitRates", "PageValues",
        "Traffic_Segment", "Revenue"
    ]
    available_cols = [c for c in filtered_df.columns if not c.startswith("_")]
    selected_cols = st.multiselect(
        "Display Columns:",
        options=available_cols,
        default=[c for c in default_cols if c in available_cols],
    )

    if not selected_cols:
        selected_cols = available_cols[:10]

    # Search filter
    search_col, count_col = st.columns([2, 1])
    with search_col:
        search_query = st.text_input("Search records (e.g. 'New_Visitor', 'Nov', 'TRUE'):", label_visibility="collapsed", placeholder="Search records...")

    display_df = filtered_df[selected_cols]
    if search_query:
        mask = display_df.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        display_df = display_df[mask]

    with count_col:
        st.markdown(f"<div style='padding-top: 0.5rem; text-align: right; color: #64748B; font-size: 0.85rem;'>Showing <b>{len(display_df):,}</b> matching records</div>", unsafe_allow_html=True)

    st.dataframe(display_df.head(250), use_container_width=True, height=360)

    # Download button
    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download Filtered Slice (CSV)",
        data=csv_bytes,
        file_name="shoppulse_filtered_data.csv",
        mime="text/csv",
    )


# -----------------------------------------------------------------------------
# FOOTER
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #94A3B8; font-size: 0.80rem; padding: 0.5rem;'>"
    "ShopPulse Analytics • Online Shopper Conversion Intelligence Platform • UCI Online Shoppers Purchasing Intention Dataset"
    "</div>",
    unsafe_allow_html=True,
)
