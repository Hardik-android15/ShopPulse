"""
ShopPulse Data Cleaning and Preprocessing Pipeline.

Loads raw UCI Online Shoppers Purchasing Intention dataset, validates schema,
handles justified data quality issues, creates analytical derived features,
and exports the cleaned dataset.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd

RAW_DATA_PATH = Path("data/raw/online_shoppers_intention.csv")
PROCESSED_DATA_PATH = Path("data/processed/cleaned_data.csv")

EXPECTED_COLUMNS = [
    "Administrative",
    "Administrative_Duration",
    "Informational",
    "Informational_Duration",
    "ProductRelated",
    "ProductRelated_Duration",
    "BounceRates",
    "ExitRates",
    "PageValues",
    "SpecialDay",
    "Month",
    "OperatingSystems",
    "Browser",
    "Region",
    "TrafficType",
    "VisitorType",
    "Weekend",
    "Revenue",
]

MONTH_ORDER = ["Feb", "Mar", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_NUM_MAP = {
    "Feb": 2,
    "Mar": 3,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}
QUARTER_MAP = {
    "Feb": "Q1",
    "Mar": "Q1",
    "May": "Q2",
    "Jun": "Q2",
    "Jul": "Q3",
    "Aug": "Q3",
    "Sep": "Q3",
    "Oct": "Q4",
    "Nov": "Q4",
    "Dec": "Q4",
}
SEASON_MAP = {
    "Dec": "Winter",
    "Feb": "Winter",
    "Mar": "Spring",
    "May": "Spring",
    "Jun": "Summer",
    "Jul": "Summer",
    "Aug": "Summer",
    "Sep": "Fall",
    "Oct": "Fall",
    "Nov": "Fall",
}

PAGE_VIEW_ORDER = ["1 page", "2-5 pages", "6-15 pages", "16-30 pages", "31+ pages"]
DURATION_ORDER = ["< 1 min", "1-5 min", "5-15 min", "15-30 min", "30+ min"]
PAGE_VALUE_TIER_ORDER = ["Zero (0)", "Low (0-10)", "Medium (10-40)", "High (40+)"]
SEASON_ORDER = ["Winter", "Spring", "Summer", "Fall"]
QUARTER_ORDER = ["Q1", "Q2", "Q3", "Q4"]
EXIT_RISK_ORDER = ["Engaged", "High Exit Risk", "Bounced"]


def ensure_categorical_types(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure categorical columns have consistent ordered categorical types."""
    df_cat = df.copy()
    if "Page_View_Bucket" in df_cat.columns:
        df_cat["Page_View_Bucket"] = pd.Categorical(
            df_cat["Page_View_Bucket"], categories=PAGE_VIEW_ORDER, ordered=True
        )
    if "Duration_Bucket" in df_cat.columns:
        df_cat["Duration_Bucket"] = pd.Categorical(
            df_cat["Duration_Bucket"], categories=DURATION_ORDER, ordered=True
        )
    if "Page_Value_Tier" in df_cat.columns:
        df_cat["Page_Value_Tier"] = pd.Categorical(
            df_cat["Page_Value_Tier"], categories=PAGE_VALUE_TIER_ORDER, ordered=True
        )
    if "Month_Clean" in df_cat.columns:
        df_cat["Month_Clean"] = pd.Categorical(
            df_cat["Month_Clean"], categories=MONTH_ORDER, ordered=True
        )
    if "Season" in df_cat.columns:
        df_cat["Season"] = pd.Categorical(
            df_cat["Season"], categories=SEASON_ORDER, ordered=True
        )
    if "Quarter" in df_cat.columns:
        df_cat["Quarter"] = pd.Categorical(
            df_cat["Quarter"], categories=QUARTER_ORDER, ordered=True
        )
    if "Exit_Risk_Profile" in df_cat.columns:
        df_cat["Exit_Risk_Profile"] = pd.Categorical(
            df_cat["Exit_Risk_Profile"], categories=EXIT_RISK_ORDER, ordered=True
        )
    return df_cat


def load_cleaned_data(file_path: Path = PROCESSED_DATA_PATH) -> pd.DataFrame:
    """Load processed CSV and restore ordered categorical types."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Cleaned dataset not found at: {path.resolve()}")
    df = pd.read_csv(path)
    return ensure_categorical_types(df)


def load_raw_data(file_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw CSV dataset into a Pandas DataFrame."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found at: {path.resolve()}")
    df = pd.read_csv(path)
    return df


def validate_raw_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate dataset columns, null counts, duplicate records, and basic constraints.
    Returns a dictionary of validation metrics.
    """
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset missing expected columns: {missing_cols}")

    null_counts = df.isnull().sum().to_dict()
    total_nulls = int(df.isnull().sum().sum())
    duplicate_count = int(df.duplicated().sum())
    total_rows = len(df)

    # Ghost sessions: 0 page views across administrative, informational, and product categories
    ghost_sessions = int(
        (
            (df["Administrative"] == 0)
            & (df["Informational"] == 0)
            & (df["ProductRelated"] == 0)
        ).sum()
    )

    validation_report = {
        "total_rows": total_rows,
        "total_columns": len(df.columns),
        "total_nulls": total_nulls,
        "null_counts": null_counts,
        "duplicate_rows": duplicate_count,
        "ghost_sessions": ghost_sessions,
        "raw_conversion_rate": float(
            (df["Revenue"].astype(str).str.upper() == "TRUE").mean() * 100
        ),
    }
    return validation_report


def clean_data(
    df: pd.DataFrame, drop_duplicates: bool = True, drop_ghost_sessions: bool = True
) -> pd.DataFrame:
    """
    Handle justified data quality issues:
    1. Standardize string casing and strip whitespace.
    2. Normalize Month names ('June' -> 'Jun') for uniform 3-letter representations.
    3. Convert boolean columns ('TRUE'/'FALSE' strings or booleans) to native bool.
    4. Cast categorical identifier columns to categorical/object representation.
    5. Deduplicate exact duplicate rows if enabled (removes artifact logs).
    6. Remove ghost sessions (0 page visits across all page types) if enabled.
    """
    cleaned = df.copy()

    # 1. Clean and normalize string categorical values
    for col in ["VisitorType", "Month"]:
        if col in cleaned.columns:
            cleaned[col] = cleaned[col].astype(str).str.strip()

    # Standardize 'June' to 'Jun'
    cleaned["Month"] = cleaned["Month"].replace({"June": "Jun"})

    # 2. Convert boolean fields to native boolean
    for bool_col in ["Weekend", "Revenue"]:
        if bool_col in cleaned.columns:
            cleaned[bool_col] = cleaned[bool_col].astype(str).str.upper() == "TRUE"

    # 3. Ensure numeric columns are properly typed
    int_cols = ["Administrative", "Informational", "ProductRelated"]
    float_cols = [
        "Administrative_Duration",
        "Informational_Duration",
        "ProductRelated_Duration",
        "BounceRates",
        "ExitRates",
        "PageValues",
        "SpecialDay",
    ]
    for col in int_cols:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0).astype(int)
    for col in float_cols:
        cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce").fillna(0.0).astype(float)

    # 4. Remove exact duplicate records
    if drop_duplicates:
        cleaned = cleaned.drop_duplicates().reset_index(drop=True)

    # 5. Remove ghost sessions with 0 total page views
    if drop_ghost_sessions:
        non_ghost_mask = (
            (cleaned["Administrative"] > 0)
            | (cleaned["Informational"] > 0)
            | (cleaned["ProductRelated"] > 0)
        )
        cleaned = cleaned[non_ghost_mask].reset_index(drop=True)

    return cleaned


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate derived analytical features for conversion funnel and behavioural analysis:
    - Total page views and total session duration
    - Page browsing ratios (Product, Admin, Informational shares)
    - Average time spent per page
    - Conversion indicator (integer flag and status string)
    - PageValue flag and tier
    - Categorical engagement buckets (Page views, Duration)
    - Bounce/Exit behavioral risk profiles
    - Temporal features (Calendar month order, Quarter, Season, DayType)
    - Traffic group classification
    """
    feat = df.copy()

    # 1. Aggregate Volume & Duration Metrics
    feat["Total_Pages"] = (
        feat["Administrative"] + feat["Informational"] + feat["ProductRelated"]
    )
    feat["Total_Duration"] = (
        feat["Administrative_Duration"]
        + feat["Informational_Duration"]
        + feat["ProductRelated_Duration"]
    )
    feat["Total_Duration_Min"] = np.round(feat["Total_Duration"] / 60.0, 2)

    # 2. Average Duration per Page Visited (safe division)
    safe_pages = np.maximum(feat["Total_Pages"], 1)
    feat["Avg_Duration_Per_Page"] = np.round(feat["Total_Duration"] / safe_pages, 2)

    # 3. Browsing Mix Shares (% of session dedicated to each page category)
    feat["Product_Page_Share"] = np.round(feat["ProductRelated"] / safe_pages, 4)
    feat["Admin_Page_Share"] = np.round(feat["Administrative"] / safe_pages, 4)
    feat["Info_Page_Share"] = np.round(feat["Informational"] / safe_pages, 4)

    # 4. Target Conversion Encodings
    feat["Revenue_Int"] = feat["Revenue"].astype(int)
    feat["Conversion_Status"] = np.where(feat["Revenue"], "Converted", "Not Converted")

    # 5. Page Value Signals & Tiers
    feat["Has_Page_Values"] = feat["PageValues"] > 0
    feat["Page_Value_Tier"] = pd.cut(
        feat["PageValues"],
        bins=[-np.inf, 0, 10, 40, np.inf],
        labels=["Zero (0)", "Low (0-10)", "Medium (10-40)", "High (40+)"],
    )

    # 6. Page-View Engagement Buckets
    feat["Page_View_Bucket"] = pd.cut(
        feat["Total_Pages"],
        bins=[0, 1, 5, 15, 30, np.inf],
        labels=["1 page", "2-5 pages", "6-15 pages", "16-30 pages", "31+ pages"],
        right=True,
    )

    # 7. Duration Engagement Buckets
    feat["Duration_Bucket"] = pd.cut(
        feat["Total_Duration_Min"],
        bins=[-np.inf, 1, 5, 15, 30, np.inf],
        labels=["< 1 min", "1-5 min", "5-15 min", "15-30 min", "30+ min"],
        right=True,
    )

    # 8. Bounce & Exit Behavioral Risk Profile
    # Engaged: low bounce and low exit
    # High Exit: low bounce but high exit (exploring then dropping off)
    # Bounced: high bounce (left immediately)
    conditions = [
        feat["BounceRates"] >= 0.10,
        (feat["ExitRates"] >= 0.08) & (feat["BounceRates"] < 0.10),
    ]
    choices = ["Bounced", "High Exit Risk"]
    feat["Exit_Risk_Profile"] = np.select(conditions, choices, default="Engaged")

    # 9. Temporal & Seasonality Dimensions
    feat["Month_Clean"] = pd.Categorical(
        feat["Month"], categories=MONTH_ORDER, ordered=True
    )
    feat["Month_Num"] = feat["Month"].map(MONTH_NUM_MAP)
    feat["Quarter"] = feat["Month"].map(QUARTER_MAP)
    feat["Season"] = feat["Month"].map(SEASON_MAP)
    feat["Day_Type"] = np.where(feat["Weekend"], "Weekend", "Weekday")

    # 10. Traffic Categorization (top channels vs niche/other)
    top_traffic_types = [1, 2, 3, 4]
    niche_high_converting = [7, 8, 10, 20]
    conditions_traffic = [
        feat["TrafficType"].isin(top_traffic_types),
        feat["TrafficType"].isin(niche_high_converting),
    ]
    choices_traffic = [
        "Major Channel (Types 1-4)",
        "High-Converting Niche (Types 7,8,10,20)",
    ]
    feat["Traffic_Segment"] = np.select(
        conditions_traffic, choices_traffic, default="Other Channels"
    )

    return feat


def run_pipeline(
    raw_path: Path = RAW_DATA_PATH, output_path: Path = PROCESSED_DATA_PATH
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    End-to-end data pipeline:
    1. Load raw CSV
    2. Validate raw data
    3. Clean data (deduplicate, remove ghost sessions, cast types, clean months)
    4. Engineer analytical features
    5. Save processed data to data/processed/cleaned_data.csv
    6. Return cleaned DataFrame and summary stats
    """
    print(f"[ShopPulse Pipeline] Loading raw data from: {raw_path}")
    raw_df = load_raw_data(raw_path)

    validation_summary = validate_raw_data(raw_df)
    print(f"[ShopPulse Pipeline] Raw Data Loaded: {validation_summary['total_rows']} rows, {validation_summary['total_columns']} columns")
    print(f"[ShopPulse Pipeline] Raw Duplicates Found: {validation_summary['duplicate_rows']}")
    print(f"[ShopPulse Pipeline] Ghost Sessions Found: {validation_summary['ghost_sessions']}")

    print("[ShopPulse Pipeline] Cleaning data...")
    cleaned_df = clean_data(raw_df, drop_duplicates=True, drop_ghost_sessions=True)

    print("[ShopPulse Pipeline] Engineering features...")
    processed_df = engineer_features(cleaned_df)

    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[ShopPulse Pipeline] Saving cleaned data to: {output_path}")
    processed_df.to_csv(output_path, index=False)

    final_summary = {
        "initial_rows": validation_summary["total_rows"],
        "final_rows": len(processed_df),
        "removed_duplicates": validation_summary["duplicate_rows"],
        "removed_ghost_sessions": validation_summary["ghost_sessions"],
        "total_columns": len(processed_df.columns),
        "converted_sessions": int(processed_df["Revenue"].sum()),
        "conversion_rate_pct": round(float(processed_df["Revenue"].mean() * 100), 2),
        "output_file": str(output_path),
    }

    print(f"[ShopPulse Pipeline] Pipeline Completed Successfully!")
    print(f"[ShopPulse Pipeline] Rows: {final_summary['final_rows']} | Columns: {final_summary['total_columns']} | Conversion Rate: {final_summary['conversion_rate_pct']}%")

    return processed_df, final_summary


if __name__ == "__main__":
    run_pipeline()
