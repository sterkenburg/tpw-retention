"""Calculate estimated booking value per supplier."""

import os

import pandas as pd
import yaml

# Load category benchmarks
_CATEGORIES_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "config", "categories.yaml"
)
with open(_CATEGORIES_PATH) as f:
    _CONFIG = yaml.safe_load(f)
_CATEGORIES = _CONFIG["categories"]
_DEFAULT = _CONFIG.get("default", {
    "avg_booking_value": 1500,
    "inquiry_to_booking_rate": 0.30,
})


def get_category_config(category: str) -> dict:
    """Get benchmark config for a category."""
    return _CATEGORIES.get(category, _DEFAULT)


def calculate(
    df: pd.DataFrame,
    contact_clicks_col: str = "contact_clicks_30d",
    leads_col: str = "leads_60d",
    category_col: str = "category",
) -> pd.Series:
    """Calculate estimated booking value for each row in a DataFrame.

    Formula: (contact_clicks + leads) × category_booking_rate × category_avg_value × 0.5
    The 0.5 is a conservative discount for uncertainty.
    """
    def _calc_row(row):
        cfg = get_category_config(row.get(category_col, ""))
        total_leads = row.get(contact_clicks_col, 0) + row.get(leads_col, 0)
        rate = cfg["inquiry_to_booking_rate"]
        avg_value = cfg["avg_booking_value"]
        return total_leads * rate * avg_value * 0.5

    return df.apply(_calc_row, axis=1)


def add_benchmarks(df: pd.DataFrame, category_col: str = "category") -> pd.DataFrame:
    """Add benchmark columns (top 10% averages) for dashboard comparison."""
    def _benchmarks(row):
        cfg = get_category_config(row.get(category_col, ""))
        return pd.Series({
            "benchmark_views_top10pct": cfg.get("avg_views_top10pct", 250),
            "benchmark_leads_top10pct": cfg.get("avg_leads_top10pct", 12),
        })

    benchmarks = df.apply(_benchmarks, axis=1)
    return pd.concat([df, benchmarks], axis=1)
