"""Shared test setup: src on the path + synthetic-data builders.

These are unit tests of the holdout/decisioning machinery (doc 29 §5, item 10):
every BigQuery touchpoint is monkeypatched, so the suite runs without network
access to the warehouse. Synthetic frames mirror the real table shapes.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def targeting_df():
    """Builder for synthetic supplier_targeting snapshots (latest-day rows)."""

    def build(rows: list[dict]) -> pd.DataFrame:
        defaults = {
            "category": "Trouwfotograaf",
            "segment": "non-venue",
            "bundle_eligible": False,
            "first_term": False,
            "renewal_status": "active",
            "days_until_renewal": 200,
            "views_60d": 10,
            "views_365d": 100,
            "stats_date": pd.Timestamp("2026-06-11"),
        }
        return pd.DataFrame([{**defaults, **r} for r in rows])

    return build
