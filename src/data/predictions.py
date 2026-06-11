"""Read the live churn model's daily predictions (external `churn_prediction`).

The cascading model (docs/strategy/12, 24) writes one snapshot per run to
`churn_prediction.daily_churn_predictions_segmented`, scoring every supplier
under BOTH segment models (New / Legacy) — and the table holds ONLY the latest
day, no history. This module reduces it to one row per supplier: the most
severe view across the segment models. Durable history accrues in
`supplier_targeting` (append-per-day) once these columns are blended in (WS-B),
which is what makes the union's recall lift measurable prospectively against
`outcomes`.
"""

import pandas as pd

from .client import query

_TABLE = "tpw-ga4-bigquery.churn_prediction.daily_churn_predictions_segmented"


def get_latest() -> pd.DataFrame:
    """Latest live-model prediction per supplier (most severe across segments).

    Columns:
      live_churn_probability  max probability across the segment models
      live_model_flag         the model's own `predicted_churn` at its
                              calibrated threshold (`threshold_used`)
      live_critical           risk_level 'Critical' (probability ≥ ~0.80)
    """
    sql = f"""
    WITH latest AS (
        SELECT *
        FROM `{_TABLE}`
        WHERE prediction_date = (SELECT MAX(prediction_date) FROM `{_TABLE}`)
    )
    SELECT
        CAST(profile_id AS STRING)          AS profile_id,
        MAX(churn_probability)              AS live_churn_probability,
        LOGICAL_OR(predicted_churn = 1)     AS live_model_flag,
        LOGICAL_OR(risk_level = 'Critical') AS live_critical
    FROM latest
    GROUP BY profile_id
    """
    df = query(sql)
    df["profile_id"] = df["profile_id"].astype(str)
    return df
