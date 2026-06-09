"""BigQuery client wrapper. Single point of contact for all BigQuery I/O."""

import os

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
DATASET_EU = _CONFIG["bigquery"].get("dataset_eu", "retention_eu")
LOCATION = _CONFIG["bigquery"].get("location", "EU")

# Ensure retention dataset exists — IN THE CONFIGURED LOCATION. Never let the
# BigQuery client default to US (it does when .location is unset): this dataset
# holds EU supplier PII and must stay in the EU.
_bq_client = bigquery.Client(project=PROJECT_ID)
_dataset_ref = f"{PROJECT_ID}.{DATASET}"
try:
    _bq_client.get_dataset(_dataset_ref)
except Exception:
    _ds = bigquery.Dataset(_dataset_ref)
    _ds.location = LOCATION
    _bq_client.create_dataset(_ds)


def query(sql: str, project_id: str = PROJECT_ID) -> pd.DataFrame:
    """Run a read query and return a DataFrame."""
    return pandas_gbq.read_gbq(sql, project_id=project_id)


def write(
    df: pd.DataFrame, table: str, if_exists: str = "append", location: str = LOCATION
) -> None:
    """Write a DataFrame to a BigQuery table.

    Args:
        df: DataFrame to write
        table: Table name (without project/dataset prefix)
        if_exists: 'append', 'replace', or 'fail'
        location: BigQuery location of the dataset (defaults to the configured EU).
            pandas_gbq otherwise defaults load jobs to US, which would fail against
            the EU retention dataset.
    """
    full_table = f"{PROJECT_ID}.{DATASET}.{table}"
    pandas_gbq.to_gbq(df, full_table, project_id=PROJECT_ID, if_exists=if_exists, location=location)


def query_eu(sql: str) -> pd.DataFrame:
    """Read a query that touches EU datasets (e.g. retention_eu), returning a df.

    pandas_gbq can mis-default the job location for EU tables, so this uses the
    BigQuery client with an explicit EU location.
    """
    return _bq_client.query(sql, location=LOCATION).to_dataframe()


def ensure_dataset(dataset: str, location: str = LOCATION) -> None:
    """Create a dataset in the given location if it doesn't already exist."""
    ref = f"{PROJECT_ID}.{dataset}"
    try:
        _bq_client.get_dataset(ref)
    except Exception:
        ds = bigquery.Dataset(ref)
        ds.location = location
        _bq_client.create_dataset(ds)


def execute(sql: str, location: str = LOCATION):
    """Run a server-side DDL/DML job (CREATE/INSERT/DELETE/MERGE) and wait.

    Use this for aggregations that must run *inside* BigQuery — never pull large
    source tables into pandas. Returns the completed job (job.num_dml_affected_rows
    is available for DML).
    """
    job = _bq_client.query(sql, location=location)
    job.result()
    return job


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
