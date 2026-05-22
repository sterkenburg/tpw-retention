"""BigQuery client wrapper. Single point of contact for all BigQuery I/O."""

import os
from typing import Optional

import pandas as pd
import pandas_gbq
import yaml
from google.cloud import bigquery

# Load config once at module level
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
with open(_CONFIG_PATH) as f:
    _CONFIG = yaml.safe_load(f)

PROJECT_ID = _CONFIG["bigquery"]["project_id"]
DATASET = _CONFIG["bigquery"]["dataset"]

# Ensure retention dataset exists
_bq_client = bigquery.Client(project=PROJECT_ID)
_dataset_ref = f"{PROJECT_ID}.{DATASET}"
try:
    _bq_client.get_dataset(_dataset_ref)
except Exception:
    _bq_client.create_dataset(bigquery.Dataset(_dataset_ref))


def query(sql: str, project_id: str = PROJECT_ID) -> pd.DataFrame:
    """Run a read query and return a DataFrame."""
    return pandas_gbq.read_gbq(sql, project_id=project_id)


def write(df: pd.DataFrame, table: str, if_exists: str = "append") -> None:
    """Write a DataFrame to a BigQuery table.

    Args:
        df: DataFrame to write
        table: Table name (without project/dataset prefix)
        if_exists: 'append', 'replace', or 'fail'
    """
    full_table = f"{PROJECT_ID}.{DATASET}.{table}"
    pandas_gbq.to_gbq(df, full_table, project_id=PROJECT_ID, if_exists=if_exists)


def table_exists(table: str) -> bool:
    """Check if a table exists in the retention dataset."""
    try:
        _bq_client.get_table(f"{PROJECT_ID}.{DATASET}.{table}")
        return True
    except Exception:
        return False


def delete_today(table: str, date_column: str = "stats_date") -> None:
    """Delete rows for the current date from a retention table.

    Prevents duplicates when the pipeline is re-run on the same day.
    """
    full_table = f"{PROJECT_ID}.{DATASET}.{table}"
    sql = f"""
        DELETE FROM `{full_table}`
        WHERE {date_column} = CURRENT_DATE()
    """
    _bq_client.query(sql).result()
