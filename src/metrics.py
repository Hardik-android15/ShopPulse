"""
ShopPulse Conversion and Funnel Metrics Module.

Calculates key conversion metrics, funnel progression, behavioral comparisons,
and segment-level conversion benchmarks using Pandas and NumPy.
"""

from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


def calculate_conversion_rate(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate overall conversion rate metrics.
    """
    total_sessions = len(df)
    if total_sessions == 0:
        return {
            "total_sessions": 0,
            "conversions": 0,
            "non_conversions": 0,
            "conversion_rate_pct": 0.0,
        }

    conversions = int(df["Revenue"].sum())
    non_conversions = total_sessions - conversions
    conversion_rate = (conversions / total_sessions) * 100

    return {
        "total_sessions": total_sessions,
        "conversions": conversions,
        "non_conversions": non_conversions,
        "conversion_rate_pct": round(conversion_rate, 2),
    }


def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute core executive metrics / KPIs for the dashboard.
    """
    if len(df) == 0:
        return {
            "total_sessions": 0,
            "conversions": 0,
            "non_conversions": 0,
            "conversion_rate_pct": 0.0,
            "avg_pages_per_session": 0.0,
            "avg_duration_minutes": 0.0,
            "avg_bounce_rate_pct": 0.0,
            "avg_exit_rate_pct": 0.0,
            "avg_page_value": 0.0,
        }

    total_sessions = len(df)
    conversions = int(df["Revenue"].sum())
    conversion_rate = (conversions / total_sessions) * 100

    avg_pages = df["Total_Pages"].mean() if "Total_Pages" in df.columns else (
        df["Administrative"] + df["Informational"] + df["ProductRelated"]
    ).mean()

    avg_duration_min = df["Total_Duration_Min"].mean() if "Total_Duration_Min" in df.columns else (
        (df["Administrative_Duration"] + df["Informational_Duration"] + df["ProductRelated_Duration"]) / 60.0
    ).mean()

    avg_bounce_rate = (df["BounceRates"].mean()) * 100
    avg_exit_rate = (df["ExitRates"].mean()) * 100
    avg_page_value = df["PageValues"].mean()

    return {
        "total_sessions": total_sessions,
        "conversions": conversions,
        "non_conversions": total_sessions - conversions,
        "conversion_rate_pct": round(conversion_rate, 2),
        "avg_pages_per_session": round(float(avg_pages), 2),
        "avg_duration_minutes": round(float(avg_duration_min), 2),
        "avg_bounce_rate_pct": round(float(avg_bounce_rate), 2),
        "avg_exit_rate_pct": round(float(avg_exit_rate), 2),
        "avg_page_value": round(float(avg_page_value), 2),
    }


def calculate_conversion_by_dimension(
    df: pd.DataFrame, dimension: str, min_sessions: int = 1
) -> pd.DataFrame:
    """
    Calculate conversion counts and conversion rates across any categorical dimension.
    Returns DataFrame sorted by total sessions descending.
    """
    if dimension not in df.columns:
        raise ValueError(f"Dimension '{dimension}' not present in dataframe.")

    grouped = (
        df.groupby(dimension, observed=False)
        .agg(
            total_sessions=("Revenue", "count"),
            conversions=("Revenue", "sum"),
        )
        .reset_index()
    )

    grouped["non_conversions"] = grouped["total_sessions"] - grouped["conversions"]
    grouped["conversion_rate_pct"] = np.round(
        (grouped["conversions"] / np.maximum(grouped["total_sessions"], 1)) * 100, 2
    )
    grouped["share_of_traffic_pct"] = np.round(
        (grouped["total_sessions"] / np.maximum(len(df), 1)) * 100, 2
    )

    filtered = grouped[grouped["total_sessions"] >= min_sessions]
    return filtered.sort_values(by="total_sessions", ascending=False).reset_index(drop=True)


def compare_converting_vs_non_converting(
    df: pd.DataFrame, metrics: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Statistical comparison of behavioral metrics between converted and non-converted sessions.
    Compares means, medians, and relative difference multipliers.
    """
    if metrics is None:
        metrics = [
            "Total_Pages",
            "Total_Duration_Min",
            "ProductRelated",
            "ProductRelated_Duration",
            "Administrative",
            "Administrative_Duration",
            "Informational",
            "Informational_Duration",
            "BounceRates",
            "ExitRates",
            "PageValues",
        ]

    valid_metrics = [m for m in metrics if m in df.columns]

    conv_df = df[df["Revenue"] == True]
    non_conv_df = df[df["Revenue"] == False]

    records = []
    for m in valid_metrics:
        conv_mean = conv_df[m].mean()
        non_conv_mean = non_conv_df[m].mean()
        conv_median = conv_df[m].median()
        non_conv_median = non_conv_df[m].median()

        diff_ratio = (
            (conv_mean / non_conv_mean) if non_conv_mean != 0 else np.nan
        )

        records.append({
            "Metric": m,
            "Non_Converted_Mean": round(float(non_conv_mean), 2),
            "Converted_Mean": round(float(conv_mean), 2),
            "Non_Converted_Median": round(float(non_conv_median), 2),
            "Converted_Median": round(float(conv_median), 2),
            "Lift_Ratio (Conv / NonConv)": round(float(diff_ratio), 2) if not np.isnan(diff_ratio) else "N/A",
        })

    return pd.DataFrame(records)


def calculate_funnel_stages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates shopper conversion funnel progression through 5 logical milestones:
    Stage 1: All Sessions (Entry)
    Stage 2: Product Catalog Browsers (ProductRelated >= 1)
    Stage 3: Deep Engaged Shoppers (ProductRelated >= 5 or Total_Pages >= 5)
    Stage 4: High Intent / Account Activity (PageValues > 0 or Administrative >= 1)
    Stage 5: Converted Buyers (Revenue == True)
    """
    total = len(df)
    if total == 0:
        return pd.DataFrame()

    stage_1 = total
    stage_2 = int((df["ProductRelated"] >= 1).sum())
    stage_3 = int(
        ((df["ProductRelated"] >= 5) | (df.get("Total_Pages", df["ProductRelated"]) >= 5)).sum()
    )
    stage_4 = int(
        ((df["PageValues"] > 0) | (df["Administrative"] >= 1)).sum()
    )
    stage_5 = int(df["Revenue"].sum())

    stages = [
        {"Stage": "1. All Sessions", "Users": stage_1},
        {"Stage": "2. Product Browsing", "Users": stage_2},
        {"Stage": "3. Deep Engagement", "Users": stage_3},
        {"Stage": "4. Intent / Account Action", "Users": stage_4},
        {"Stage": "5. Completed Purchase", "Users": stage_5},
    ]

    funnel_df = pd.DataFrame(stages)
    funnel_df["Step_Conversion_Pct"] = np.round((funnel_df["Users"] / stage_1) * 100, 2)

    # Calculate drop-off from previous step
    prev_users = funnel_df["Users"].shift(1).fillna(stage_1)
    funnel_df["Progression_From_Prev_Pct"] = np.round((funnel_df["Users"] / prev_users) * 100, 2)
    funnel_df["Drop_Off_Count"] = prev_users.astype(int) - funnel_df["Users"]
    funnel_df["Drop_Off_Pct"] = np.round((funnel_df["Drop_Off_Count"] / prev_users) * 100, 2)

    return funnel_df


def calculate_engagement_matrix(
    df: pd.DataFrame,
    page_col: str = "Page_View_Bucket",
    duration_col: str = "Duration_Bucket",
) -> pd.DataFrame:
    """
    Cross-tabulates conversion rate (%) across Page View Buckets and Duration Buckets.
    """
    if page_col not in df.columns or duration_col not in df.columns:
        raise ValueError("Bucket columns missing from dataframe.")

    matrix = df.pivot_table(
        index=page_col,
        columns=duration_col,
        values="Revenue",
        aggfunc=lambda x: round(float(np.mean(x) * 100), 2) if len(x) > 0 else 0.0,
        observed=False,
    ).fillna(0.0)

    # Reindex by canonical order if applicable
    from src.data_cleaning import PAGE_VIEW_ORDER, DURATION_ORDER
    row_order = [p for p in PAGE_VIEW_ORDER if p in matrix.index]
    col_order = [d for d in DURATION_ORDER if d in matrix.columns]
    if row_order:
        matrix = matrix.reindex(index=row_order)
    if col_order:
        matrix = matrix.reindex(columns=col_order)

    return matrix
