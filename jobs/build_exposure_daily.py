"""Build supplier_exposure_daily (WS-A).

Usage:
    python jobs/build_exposure_daily.py                  # incremental: last 3 days
    python jobs/build_exposure_daily.py 2023-01-01 2026-05-31   # backfill a range
    python jobs/build_exposure_daily.py 2026-05-01              # single day onward to today

Runs the aggregation inside BigQuery (source is ~388M rows). Idempotent per date.
"""

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data import exposure


def run(start_date: str | None = None, end_date: str | None = None) -> None:
    today = date.today()
    if start_date is None:
        start_date = (today - timedelta(days=3)).isoformat()
    if end_date is None:
        end_date = today.isoformat()

    print(f"Building supplier_exposure_daily for {start_date} … {end_date}")
    rows = exposure.build(start_date, end_date)
    print(f"  → {rows:,} rows written")


if __name__ == "__main__":
    args = sys.argv[1:]
    run(*args)
