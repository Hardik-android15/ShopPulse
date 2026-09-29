"""
ShopPulse Exploratory and Behavioral Analysis Module.

Provides comprehensive analytical functions for visitor behavior, traffic sources,
session duration, page viewing patterns, and temporal analysis using Pandas and NumPy.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from src.data_cleaning import (
    PAGE_VIEW_ORDER,
    DURATION_ORDER,
    PAGE_VALUE_TIER_ORDER,
    SEASON_ORDER,
    QUARTER_ORDER,
    EXIT_RISK_ORDER,
    MONTH_NUM_MAP,
    ensure_categorical_types,
)
from src.metrics import (
    calculate_kpis,
    calculate_conversion_rate,
    compare_converting_vs_non_converting,
    calculate_engagement_matrix,
)


def analyze_visitor_behavior(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze behavioral differences across Visitor Types (Returning, New, Other):
    - Session counts and traffic share
    - Conversions and conversion rate
    - Average total pages and average session duration (minutes)
    - Average bounce and exit rates
    - Average PageValues
    """
    visitor_summary = (
        df.groupby("VisitorType", observed=False)
        .agg(
            total_sessions=("Revenue", "count"),
            conversions=("Revenue", "sum"),
            avg_pages=("Total_Pages", "mean"),
            avg_duration_min=("Total_Duration_Min", "mean"),
            avg_bounce_rate=("BounceRates", lambda x: np.mean(x) * 100),
            avg_exit_rate=("ExitRates", lambda x: np.mean(x) * 100),
            avg_page_value=("PageValues", "mean"),
        )
        .reset_index()
    )

    visitor_summary["traffic_share_pct"] = np.round(
        (visitor_summary["total_sessions"] / len(df)) * 100, 2
    )
    visitor_summary["conversion_rate_pct"] = np.round(
        (visitor_summary["conversions"] / visitor_summary["total_sessions"]) * 100, 2
    )

    # Round metrics for presentation
    for col in ["avg_pages", "avg_duration_min", "avg_bounce_rate", "avg_exit_rate", "avg_page_value"]:
        visitor_summary[col] = np.round(visitor_summary[col], 2)

    return visitor_summary.sort_values(by="total_sessions", ascending=False).reset_index(drop=True)


def analyze_traffic_sources(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Analyze performance across traffic sources:
    - Volume, conversions, conversion rate
    - Average bounce and exit rates
    - Returns top N traffic types by volume
    """
    traffic_summary = (
        df.groupby("TrafficType", observed=False)
        .agg(
            total_sessions=("Revenue", "count"),
            conversions=("Revenue", "sum"),
            conversion_rate_pct=("Revenue", lambda x: np.mean(x) * 100),
            avg_bounce_pct=("BounceRates", lambda x: np.mean(x) * 100),
            avg_exit_pct=("ExitRates", lambda x: np.mean(x) * 100),
            avg_page_value=("PageValues", "mean"),
        )
        .reset_index()
    )

    traffic_summary["traffic_share_pct"] = np.round(
        (traffic_summary["total_sessions"] / len(df)) * 100, 2
    )
    for col in ["conversion_rate_pct", "avg_bounce_pct", "avg_exit_pct", "avg_page_value"]:
        traffic_summary[col] = np.round(traffic_summary[col], 2)

    sorted_df = traffic_summary.sort_values(by="total_sessions", ascending=False)
    if top_n:
        return sorted_df.head(top_n).reset_index(drop=True)
    return sorted_df.reset_index(drop=True)


def analyze_page_and_duration_distribution(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Analyze session page counts and duration patterns:
    1. Metrics by Page View Buckets
    2. Metrics by Duration Buckets
    3. Page Category Mix (Product, Admin, Info shares) comparing Converted vs Non-Converted
    """
    # 1. By Page View Bucket
    page_bucket_df = (
        df.groupby("Page_View_Bucket", observed=False)
        .agg(
            total_sessions=("Revenue", "count"),
            conversions=("Revenue", "sum"),
            conversion_rate_pct=("Revenue", lambda x: np.mean(x) * 100),
            avg_duration_min=("Total_Duration_Min", "mean"),
            avg_page_values=("PageValues", "mean"),
        )
        .reset_index()
    )
    for col in ["conversion_rate_pct", "avg_duration_min", "avg_page_values"]:
        page_bucket_df[col] = np.round(page_bucket_df[col], 2)

    # 2. By Duration Bucket
    duration_bucket_df = (
        df.groupby("Duration_Bucket", observed=False)
        .agg(
            total_sessions=("Revenue", "count"),
            conversions=("Revenue", "sum"),
            conversion_rate_pct=("Revenue", lambda x: np.mean(x) * 100),
            avg_pages=("Total_Pages", "mean"),
            avg_page_values=("PageValues", "mean"),
        )
        .reset_index()
    )
    for col in ["conversion_rate_pct", "avg_pages", "avg_page_values"]:
        duration_bucket_df[col] = np.round(duration_bucket_df[col], 2)

    # 3. Page Browsing Mix by Conversion Status
    mix_df = (
        df.groupby("Conversion_Status", observed=False)
        .agg(
            avg_product_pages=("ProductRelated", "mean"),
            avg_admin_pages=("Administrative", "mean"),
            avg_info_pages=("Informational", "mean"),
            avg_product_share=("Product_Page_Share", lambda x: np.mean(x) * 100),
            avg_admin_share=("Admin_Page_Share", lambda x: np.mean(x) * 100),
            avg_info_share=("Info_Page_Share", lambda x: np.mean(x) * 100),
        )
        .reset_index()
    )
    for col in mix_df.columns:
        if col != "Conversion_Status":
            mix_df[col] = np.round(mix_df[col], 2)

    return {
        "page_view_buckets": page_bucket_df,
        "duration_buckets": duration_bucket_df,
        "page_mix": mix_df,
    }


def analyze_temporal_patterns(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Analyze conversion trends across temporal dimensions:
    1. Monthly trends (in chronological order)
    2. Weekend vs Weekday performance
    3. Special Day closeness impact
    """
    # 1. Monthly Trends
    month_df = (
        df.groupby("Month_Clean", observed=False)
        .agg(
            total_sessions=("Revenue", "count"),
            conversions=("Revenue", "sum"),
            conversion_rate_pct=("Revenue", lambda x: np.mean(x) * 100),
            avg_page_values=("PageValues", "mean"),
            avg_duration_min=("Total_Duration_Min", "mean"),
        )
        .reset_index()
    )
    month_df["Month_Num"] = month_df["Month_Clean"].map(MONTH_NUM_MAP)
    month_df = month_df.sort_values(by="Month_Num").reset_index(drop=True)
    for col in ["conversion_rate_pct", "avg_page_values", "avg_duration_min"]:
        month_df[col] = np.round(month_df[col], 2)

    # 2. Weekend vs Weekday
    day_df = (
        df.groupby("Day_Type", observed=False)
        .agg(
            total_sessions=("Revenue", "count"),
            conversions=("Revenue", "sum"),
            conversion_rate_pct=("Revenue", lambda x: np.mean(x) * 100),
            avg_pages=("Total_Pages", "mean"),
            avg_duration_min=("Total_Duration_Min", "mean"),
        )
        .reset_index()
    )
    for col in ["conversion_rate_pct", "avg_pages", "avg_duration_min"]:
        day_df[col] = np.round(day_df[col], 2)

    # 3. Special Day Impact
    special_day_df = (
        df.groupby("SpecialDay", observed=False)
        .agg(
            total_sessions=("Revenue", "count"),
            conversions=("Revenue", "sum"),
            conversion_rate_pct=("Revenue", lambda x: np.mean(x) * 100),
            avg_page_values=("PageValues", "mean"),
        )
        .reset_index()
        .sort_values(by="SpecialDay")
        .reset_index(drop=True)
    )
    for col in ["conversion_rate_pct", "avg_page_values"]:
        special_day_df[col] = np.round(special_day_df[col], 2)

    return {
        "monthly_trends": month_df,
        "day_type": day_df,
        "special_day": special_day_df,
    }


def analyze_exit_and_bounce_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze shopper behavior across Exit Risk Profiles:
    - Bounced vs High Exit Risk vs Engaged
    """
    profile_df = (
        df.groupby("Exit_Risk_Profile", observed=False)
        .agg(
            total_sessions=("Revenue", "count"),
            conversions=("Revenue", "sum"),
            conversion_rate_pct=("Revenue", lambda x: np.mean(x) * 100),
            avg_pages=("Total_Pages", "mean"),
            avg_duration_min=("Total_Duration_Min", "mean"),
            avg_page_value=("PageValues", "mean"),
        )
        .reset_index()
    )

    profile_df["share_of_traffic_pct"] = np.round(
        (profile_df["total_sessions"] / len(df)) * 100, 2
    )
    for col in ["conversion_rate_pct", "avg_pages", "avg_duration_min", "avg_page_value"]:
        profile_df[col] = np.round(profile_df[col], 2)

    return profile_df.sort_values(by="total_sessions", ascending=False).reset_index(drop=True)


def get_top_converting_segments(
    df: pd.DataFrame, dimensions: Optional[List[str]] = None, min_sessions: int = 50
) -> pd.DataFrame:
    """
    Identify high-yield vs low-yield shopper segments by multidimensional grouping.
    """
    if dimensions is None:
        dimensions = ["VisitorType", "Month_Clean", "Day_Type"]

    valid_dims = [d for d in dimensions if d in df.columns]

    segments = (
        df.groupby(valid_dims, observed=False)
        .agg(
            total_sessions=("Revenue", "count"),
            conversions=("Revenue", "sum"),
        )
        .reset_index()
    )

    segments = segments[segments["total_sessions"] >= min_sessions].copy()
    segments["conversion_rate_pct"] = np.round(
        (segments["conversions"] / segments["total_sessions"]) * 100, 2
    )

    return segments.sort_values(by="conversion_rate_pct", ascending=False).reset_index(drop=True)


# =====================================================================
# DASHBOARD-READY ANALYTICAL FUNCTIONS (Plotly & Streamlit Compatible)
# =====================================================================


def get_executive_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Expose executive summary KPIs (sessions, conversions, conversion rate, bounce rate, etc.)."""
    return calculate_kpis(df)


def get_conversion_rate_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Expose high-level conversion volume and percentage summary."""
    return calculate_conversion_rate(df)


def get_converting_vs_non_converting_comparison(
    df: pd.DataFrame, metrics: Optional[List[str]] = None
) -> pd.DataFrame:
    """Statistical comparison of shopper behavior between converted and non-converted sessions."""
    return compare_converting_vs_non_converting(df, metrics=metrics)


def analyze_visitor_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze conversion and behavioral engagement by visitor type."""
    res = analyze_visitor_behavior(df)
    res = res.rename(
        columns={
            "total_sessions": "Total_Sessions",
            "conversions": "Conversions",
            "traffic_share_pct": "Traffic_Share_Pct",
            "conversion_rate_pct": "Conversion_Rate_Pct",
            "avg_pages": "Avg_Pages",
            "avg_duration_min": "Avg_Duration_Min",
            "avg_bounce_rate": "Avg_Bounce_Rate_Pct",
            "avg_exit_rate": "Avg_Exit_Rate_Pct",
            "avg_page_value": "Avg_Page_Value",
        }
    )
    res["Non_Conversions"] = res["Total_Sessions"] - res["Conversions"]
    return res


def analyze_traffic_source_conversion(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Analyze conversion performance across traffic sources."""
    res = analyze_traffic_sources(df, top_n=top_n)
    res = res.rename(
        columns={
            "total_sessions": "Total_Sessions",
            "conversions": "Conversions",
            "traffic_share_pct": "Traffic_Share_Pct",
            "conversion_rate_pct": "Conversion_Rate_Pct",
            "avg_bounce_pct": "Avg_Bounce_Rate_Pct",
            "avg_exit_pct": "Avg_Exit_Rate_Pct",
            "avg_page_value": "Avg_Page_Value",
        }
    )
    res["Non_Conversions"] = res["Total_Sessions"] - res["Conversions"]
    return res


def analyze_page_view_bucket_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze conversion rate and volume across page-view count buckets in natural order."""
    df_cat = ensure_categorical_types(df)
    grouped = (
        df_cat.groupby("Page_View_Bucket", observed=False)
        .agg(
            Total_Sessions=("Revenue", "count"),
            Conversions=("Revenue", "sum"),
            Avg_Duration_Min=("Total_Duration_Min", "mean"),
            Avg_Page_Value=("PageValues", "mean"),
        )
        .reset_index()
    )
    total_count = len(df_cat)
    grouped["Non_Conversions"] = grouped["Total_Sessions"] - grouped["Conversions"]
    grouped["Conversion_Rate_Pct"] = np.round(
        (grouped["Conversions"] / np.maximum(grouped["Total_Sessions"], 1)) * 100, 2
    )
    grouped["Traffic_Share_Pct"] = np.round(
        (grouped["Total_Sessions"] / np.maximum(total_count, 1)) * 100, 2
    )
    grouped["Avg_Duration_Min"] = np.round(grouped["Avg_Duration_Min"], 2)
    grouped["Avg_Page_Value"] = np.round(grouped["Avg_Page_Value"], 2)

    order_map = {name: i for i, name in enumerate(PAGE_VIEW_ORDER)}
    grouped["_sort_order"] = grouped["Page_View_Bucket"].map(order_map)
    return grouped.sort_values(by="_sort_order").drop(columns=["_sort_order"]).reset_index(drop=True)


def analyze_duration_bucket_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze conversion rate and volume across session duration buckets in natural order."""
    df_cat = ensure_categorical_types(df)
    grouped = (
        df_cat.groupby("Duration_Bucket", observed=False)
        .agg(
            Total_Sessions=("Revenue", "count"),
            Conversions=("Revenue", "sum"),
            Avg_Pages=("Total_Pages", "mean"),
            Avg_Page_Value=("PageValues", "mean"),
        )
        .reset_index()
    )
    total_count = len(df_cat)
    grouped["Non_Conversions"] = grouped["Total_Sessions"] - grouped["Conversions"]
    grouped["Conversion_Rate_Pct"] = np.round(
        (grouped["Conversions"] / np.maximum(grouped["Total_Sessions"], 1)) * 100, 2
    )
    grouped["Traffic_Share_Pct"] = np.round(
        (grouped["Total_Sessions"] / np.maximum(total_count, 1)) * 100, 2
    )
    grouped["Avg_Pages"] = np.round(grouped["Avg_Pages"], 2)
    grouped["Avg_Page_Value"] = np.round(grouped["Avg_Page_Value"], 2)

    order_map = {name: i for i, name in enumerate(DURATION_ORDER)}
    grouped["_sort_order"] = grouped["Duration_Bucket"].map(order_map)
    return grouped.sort_values(by="_sort_order").drop(columns=["_sort_order"]).reset_index(drop=True)


def analyze_monthly_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze conversion trends across calendar months in chronological order."""
    df_cat = ensure_categorical_types(df)
    grouped = (
        df_cat.groupby("Month_Clean", observed=False)
        .agg(
            Total_Sessions=("Revenue", "count"),
            Conversions=("Revenue", "sum"),
            Avg_Pages=("Total_Pages", "mean"),
            Avg_Duration_Min=("Total_Duration_Min", "mean"),
            Avg_Page_Value=("PageValues", "mean"),
        )
        .reset_index()
    )
    total_count = len(df_cat)
    grouped["Non_Conversions"] = grouped["Total_Sessions"] - grouped["Conversions"]
    grouped["Conversion_Rate_Pct"] = np.round(
        (grouped["Conversions"] / np.maximum(grouped["Total_Sessions"], 1)) * 100, 2
    )
    grouped["Traffic_Share_Pct"] = np.round(
        (grouped["Total_Sessions"] / np.maximum(total_count, 1)) * 100, 2
    )
    grouped["Avg_Pages"] = np.round(grouped["Avg_Pages"], 2)
    grouped["Avg_Duration_Min"] = np.round(grouped["Avg_Duration_Min"], 2)
    grouped["Avg_Page_Value"] = np.round(grouped["Avg_Page_Value"], 2)
    grouped["Month_Num"] = grouped["Month_Clean"].map(MONTH_NUM_MAP)
    grouped = grouped.rename(columns={"Month_Clean": "Month"})
    return grouped.sort_values(by="Month_Num").reset_index(drop=True)


def analyze_seasonal_conversion(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Analyze conversion trends across Seasons and Quarters."""
    df_cat = ensure_categorical_types(df)
    total_count = len(df_cat)

    # Seasonal
    season_df = (
        df_cat.groupby("Season", observed=False)
        .agg(
            Total_Sessions=("Revenue", "count"),
            Conversions=("Revenue", "sum"),
            Avg_Duration_Min=("Total_Duration_Min", "mean"),
            Avg_Page_Value=("PageValues", "mean"),
        )
        .reset_index()
    )
    season_df["Non_Conversions"] = season_df["Total_Sessions"] - season_df["Conversions"]
    season_df["Conversion_Rate_Pct"] = np.round(
        (season_df["Conversions"] / np.maximum(season_df["Total_Sessions"], 1)) * 100, 2
    )
    season_df["Traffic_Share_Pct"] = np.round(
        (season_df["Total_Sessions"] / np.maximum(total_count, 1)) * 100, 2
    )
    season_df["Avg_Duration_Min"] = np.round(season_df["Avg_Duration_Min"], 2)
    season_df["Avg_Page_Value"] = np.round(season_df["Avg_Page_Value"], 2)
    s_order = {s: i for i, s in enumerate(SEASON_ORDER)}
    season_df["_sort"] = season_df["Season"].map(s_order)
    season_df = season_df.sort_values(by="_sort").drop(columns=["_sort"]).reset_index(drop=True)

    # Quarterly
    quarter_df = (
        df_cat.groupby("Quarter", observed=False)
        .agg(
            Total_Sessions=("Revenue", "count"),
            Conversions=("Revenue", "sum"),
            Avg_Duration_Min=("Total_Duration_Min", "mean"),
            Avg_Page_Value=("PageValues", "mean"),
        )
        .reset_index()
    )
    quarter_df["Non_Conversions"] = quarter_df["Total_Sessions"] - quarter_df["Conversions"]
    quarter_df["Conversion_Rate_Pct"] = np.round(
        (quarter_df["Conversions"] / np.maximum(quarter_df["Total_Sessions"], 1)) * 100, 2
    )
    quarter_df["Traffic_Share_Pct"] = np.round(
        (quarter_df["Total_Sessions"] / np.maximum(total_count, 1)) * 100, 2
    )
    quarter_df["Avg_Duration_Min"] = np.round(quarter_df["Avg_Duration_Min"], 2)
    quarter_df["Avg_Page_Value"] = np.round(quarter_df["Avg_Page_Value"], 2)
    q_order = {q: i for i, q in enumerate(QUARTER_ORDER)}
    quarter_df["_sort"] = quarter_df["Quarter"].map(q_order)
    quarter_df = quarter_df.sort_values(by="_sort").drop(columns=["_sort"]).reset_index(drop=True)

    return {
        "seasonal": season_df,
        "quarterly": quarter_df,
    }


def analyze_weekend_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze conversion differences between Weekend and Weekday sessions."""
    df_cat = ensure_categorical_types(df)
    total_count = len(df_cat)
    day_df = (
        df_cat.groupby("Day_Type", observed=False)
        .agg(
            Total_Sessions=("Revenue", "count"),
            Conversions=("Revenue", "sum"),
            Avg_Pages=("Total_Pages", "mean"),
            Avg_Duration_Min=("Total_Duration_Min", "mean"),
            Avg_Bounce_Rate_Pct=("BounceRates", lambda x: np.mean(x) * 100),
            Avg_Page_Value=("PageValues", "mean"),
        )
        .reset_index()
    )
    day_df["Non_Conversions"] = day_df["Total_Sessions"] - day_df["Conversions"]
    day_df["Conversion_Rate_Pct"] = np.round(
        (day_df["Conversions"] / np.maximum(day_df["Total_Sessions"], 1)) * 100, 2
    )
    day_df["Traffic_Share_Pct"] = np.round(
        (day_df["Total_Sessions"] / np.maximum(total_count, 1)) * 100, 2
    )
    for col in ["Avg_Pages", "Avg_Duration_Min", "Avg_Bounce_Rate_Pct", "Avg_Page_Value"]:
        day_df[col] = np.round(day_df[col], 2)

    return day_df.sort_values(by="Total_Sessions", ascending=False).reset_index(drop=True)


def analyze_exit_risk_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze conversion differences across behavioral Exit Risk Profiles (Engaged, High Exit Risk, Bounced)."""
    df_cat = ensure_categorical_types(df)
    total_count = len(df_cat)
    profile_df = (
        df_cat.groupby("Exit_Risk_Profile", observed=False)
        .agg(
            Total_Sessions=("Revenue", "count"),
            Conversions=("Revenue", "sum"),
            Avg_Pages=("Total_Pages", "mean"),
            Avg_Duration_Min=("Total_Duration_Min", "mean"),
            Avg_Page_Value=("PageValues", "mean"),
        )
        .reset_index()
    )
    profile_df["Non_Conversions"] = profile_df["Total_Sessions"] - profile_df["Conversions"]
    profile_df["Conversion_Rate_Pct"] = np.round(
        (profile_df["Conversions"] / np.maximum(profile_df["Total_Sessions"], 1)) * 100, 2
    )
    profile_df["Traffic_Share_Pct"] = np.round(
        (profile_df["Total_Sessions"] / np.maximum(total_count, 1)) * 100, 2
    )
    profile_df["Avg_Pages"] = np.round(profile_df["Avg_Pages"], 2)
    profile_df["Avg_Duration_Min"] = np.round(profile_df["Avg_Duration_Min"], 2)
    profile_df["Avg_Page_Value"] = np.round(profile_df["Avg_Page_Value"], 2)

    order_map = {name: i for i, name in enumerate(EXIT_RISK_ORDER)}
    profile_df["_sort"] = profile_df["Exit_Risk_Profile"].map(order_map)
    return profile_df.sort_values(by="_sort").drop(columns=["_sort"]).reset_index(drop=True)


def analyze_page_value_tier_conversion(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze conversion volume and rates across PageValue tiers (Zero, Low, Medium, High)."""
    df_cat = ensure_categorical_types(df)
    total_count = len(df_cat)
    pv_df = (
        df_cat.groupby("Page_Value_Tier", observed=False)
        .agg(
            Total_Sessions=("Revenue", "count"),
            Conversions=("Revenue", "sum"),
            Avg_Pages=("Total_Pages", "mean"),
            Avg_Duration_Min=("Total_Duration_Min", "mean"),
            Avg_Bounce_Rate_Pct=("BounceRates", lambda x: np.mean(x) * 100),
        )
        .reset_index()
    )
    pv_df["Non_Conversions"] = pv_df["Total_Sessions"] - pv_df["Conversions"]
    pv_df["Conversion_Rate_Pct"] = np.round(
        (pv_df["Conversions"] / np.maximum(pv_df["Total_Sessions"], 1)) * 100, 2
    )
    pv_df["Traffic_Share_Pct"] = np.round(
        (pv_df["Total_Sessions"] / np.maximum(total_count, 1)) * 100, 2
    )
    for col in ["Avg_Pages", "Avg_Duration_Min", "Avg_Bounce_Rate_Pct"]:
        pv_df[col] = np.round(pv_df[col], 2)

    order_map = {name: i for i, name in enumerate(PAGE_VALUE_TIER_ORDER)}
    pv_df["_sort"] = pv_df["Page_Value_Tier"].map(order_map)
    return pv_df.sort_values(by="_sort").drop(columns=["_sort"]).reset_index(drop=True)


def analyze_engagement_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Expose engagement matrix heatmap cross-tabulating Page View Buckets vs Duration Buckets."""
    return calculate_engagement_matrix(df)
