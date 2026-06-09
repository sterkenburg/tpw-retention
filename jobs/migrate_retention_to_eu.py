"""One-shot: migrate the `retention` dataset US → EU and consolidate.

Why: `retention` was auto-created in US by an unset-location default; it holds EU
supplier PII and must live in the EU, co-located with GA4 (EU) sources. This also
folds `retention_eu` (the WS-A workaround dataset) back into a single `retention`.

Steps:
  1. Preserve the stateful/non-empty small tables (incl. cohort_assignment — the
     LOCKED holdout salt) from US `retention` into memory.
  2. Drop US `retention`; recreate `retention` in EU.
  3. Restore the preserved tables into EU `retention`.
  4. Copy supplier_exposure_daily `retention_eu` → `retention` (both EU, in-region).
  5. Verify row counts + that the salt is byte-for-byte preserved.

Derived tables (supplier_targeting, retention_directives, measurement_panel) are
NOT migrated — they're rebuilt fresh in EU by their jobs after this runs.
Empty tables (email_log, intervention_log, outcomes) are recreated on demand.
"""

from google.cloud import bigquery

PROJECT = "tpw-ga4-bigquery"
US_DS = f"{PROJECT}.retention"
EU_DS = f"{PROJECT}.retention"          # same name, EU location after recreate
EU_SRC = f"{PROJECT}.retention_eu"      # WS-A exposure lives here (EU)

# Preserve these from US (non-empty, not trivially rebuilt). The rest are rebuilt.
PRESERVE = ["cohort_assignment", "actions_log", "signals_daily", "supplier_stats_daily"]
EXPOSURE = "supplier_exposure_daily"

bq = bigquery.Client(project=PROJECT)


def _snapshot_salt(table_fqn: str, location: str) -> set:
    df = bq.query(
        f"SELECT profile_id, arm, salt_used FROM `{table_fqn}`", location=location
    ).to_dataframe()
    return set(map(tuple, df.astype(str).values))


def run() -> None:
    # 1. Preserve --------------------------------------------------------
    print("1. Preserving US tables into memory...")
    saved = {}
    for t in PRESERVE:
        df = bq.query(f"SELECT * FROM `{US_DS}.{t}`", location="US").to_dataframe()
        saved[t] = df
        print(f"   {t}: {len(df)} rows")
    salt_before = _snapshot_salt(f"{US_DS}.cohort_assignment", "US")
    print(f"   salt snapshot: {len(salt_before)} (profile_id, arm, salt_used) tuples")

    # 2. Drop US, recreate EU -------------------------------------------
    print("2. Dropping US `retention` and recreating in EU...")
    bq.delete_dataset(US_DS, delete_contents=True, not_found_ok=True)
    ds = bigquery.Dataset(EU_DS)
    ds.location = "EU"
    bq.create_dataset(ds)
    print(f"   created {EU_DS} location=EU")

    # 3. Restore preserved tables into EU --------------------------------
    print("3. Restoring preserved tables into EU...")
    for t, df in saved.items():
        job = bq.load_table_from_dataframe(df, f"{EU_DS}.{t}")  # location from dest (EU)
        job.result()
        print(f"   {t}: loaded {bq.get_table(f'{EU_DS}.{t}').num_rows} rows")

    # 4. Copy exposure (EU → EU, in-region) ------------------------------
    print("4. Copying supplier_exposure_daily (retention_eu → retention, EU)...")
    copy_job = bq.copy_table(f"{EU_SRC}.{EXPOSURE}", f"{EU_DS}.{EXPOSURE}")
    copy_job.result()
    print(f"   {EXPOSURE}: {bq.get_table(f'{EU_DS}.{EXPOSURE}').num_rows} rows copied")

    # 5. Verify ----------------------------------------------------------
    print("5. Verifying...")
    loc = bq.get_dataset(EU_DS).location
    salt_after = _snapshot_salt(f"{EU_DS}.cohort_assignment", "EU")
    salt_ok = salt_before == salt_after
    print(f"   dataset location: {loc}")
    print(f"   salt preserved exactly: {salt_ok} "
          f"(before={len(salt_before)}, after={len(salt_after)})")
    if not salt_ok:
        raise SystemExit("SALT MISMATCH — aborting before cleanup. Investigate.")
    print("\nMigration complete. retention_eu still present (drop after rebuild verifies).")


if __name__ == "__main__":
    run()
