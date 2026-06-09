"""WS-D — directive generation (the decisioning brain's output).

This repo is the retention **brain**: it decides WHAT each treatment supplier
should receive, writes those decisions to `retention_directives` (the single
source of truth), and leaves DELIVERY to the systems that own each surface
(Elastic, Bird/marketing_flow, profile_auto_complete). See docs/strategy/19.

Four levers (docs/strategy/18, doc 20 WS-D1–D4):
  - boost       → Elastic `retention_boost`, **free layer only** (the core lever)
  - optimize    → profile_auto_complete: optimize the profile before boosting it
                  (a boosted weak profile wastes the placement — always paired)
  - newsletter  → Bird/marketing_flow: feature the supplier in a couple newsletter
  - email       → Bird/marketing_flow: monthly exposure-first results email

**Holdout enforcement is structural here:** directives are generated ONLY for the
treatment arm (`cohort.treatment_ids`); control suppliers can never receive one.
Every row records its `arm` so `measurement.contamination_audit` can prove it.

**Channel gating:** each channel dispatches only after its G0 confirmation spike
(config `directives.*_enabled`). Until then directives are still COMPUTED and
stored with `status='gated'` (+ the blocking spike in `note`) — so the brain is
fully testable now and dispatch is a single flag-flip away once a spike lands.
"""

import json
import os

import pandas as pd
import yaml

from data import client
from signals import cohort

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "settings.yaml")
with open(_CONFIG_PATH) as _f:
    _CONFIG = yaml.safe_load(_f)

_DIR_CFG = _CONFIG.get("directives", {})
_TABLE = _CONFIG["tables"]["retention_directives"]
_BOOST_LAYER = _DIR_CFG.get("boost_layer", "free")

# Lever registry: type → channel, the enable flag that gates dispatch, the
# blocking G0 spike, and the static params each directive carries.
LEVERS = {
    "boost": {
        "channel": "elastic",
        "enable_flag": "elastic_enabled",
        "spike": "YOO-228 (Elastic boost)",
        "params": {
            "directive": "retention_boost",
            "layer": _BOOST_LAYER,  # free/owned only — never paid premium
            "surfaces": ["cross_profile_reco", "discover_rising", "regional_search"],
            "exclude_premium": True,
        },
    },
    "optimize": {
        "channel": "profile_auto_complete",
        "enable_flag": "scraper_enabled",
        "spike": "scraper optimize-trigger spike",
        "params": {"action": "optimize_list", "reason": "paired_with_boost"},
    },
    "newsletter": {
        "channel": "bird_marketing_flow",
        "enable_flag": "bird_enabled",
        "spike": "Bird newsletter spike",
        "params": {"campaign": "couple_newsletter_feature"},
    },
    "email": {
        "channel": "bird_marketing_flow",
        "enable_flag": "bird_enabled",
        "spike": "Bird email spike",
        "params": {
            "template": "monthly_results",
            "exposure_first": True,        # lead with exposure, not leads
            "include_masked_leads": True,  # concrete proof; full PII in-dashboard only
        },
    },
}

_OUTPUT_COLUMNS = [
    "profile_id", "experiment_id", "arm", "type", "channel",
    "params", "status", "note", "created_at", "delivered_at",
]


def _status_for(spec: dict, now: pd.Timestamp) -> tuple[str, str, object]:
    """Resolve (status, note, delivered_at) for a directive given channel gating."""
    if not _DIR_CFG.get(spec["enable_flag"], False):
        return "gated", f"pending {spec['spike']}", pd.NaT
    if _DIR_CFG.get("dry_run", True):
        return "dry_run", "channel enabled; dry_run on (would dispatch)", pd.NaT
    return "delivered", "", now


def generate(experiment_id: str = "stage1_exposure") -> pd.DataFrame:
    """Compute the directive set for the treatment arm (does not write)."""
    treat = sorted(cohort.treatment_ids(experiment_id))
    now = pd.Timestamp.now()
    rows = []
    for pid in treat:
        for typ, spec in LEVERS.items():
            status, note, delivered = _status_for(spec, now)
            rows.append({
                "profile_id": pid,
                "experiment_id": experiment_id,
                "arm": "treatment",
                "type": typ,
                "channel": spec["channel"],
                "params": json.dumps(spec["params"]),
                "status": status,
                "note": note,
                "created_at": now,
                "delivered_at": delivered,
            })
    df = pd.DataFrame(rows, columns=_OUTPUT_COLUMNS)

    # Structural holdout guarantee: no control supplier may appear.
    control = cohort.client.query(
        f"SELECT profile_id FROM "
        f"`{client.PROJECT_ID}.{client.DATASET}.{_CONFIG['tables']['cohort_assignment']}` "
        f"WHERE experiment_id = '{experiment_id}' AND arm = 'control'"
    )
    leak = set(df["profile_id"]) & set(control["profile_id"].astype(str))
    if leak:
        raise AssertionError(f"Holdout violation: control suppliers in directives: {leak}")
    return df


def build(experiment_id: str = "stage1_exposure") -> pd.DataFrame:
    """Refresh `retention_directives` to the current intended state for the experiment."""
    df = generate(experiment_id)
    if client.table_exists(_TABLE):
        client.execute(
            f"DELETE FROM `{client.PROJECT_ID}.{client.DATASET}.{_TABLE}` "
            f"WHERE experiment_id = '{experiment_id}'",
        )
    if not df.empty:
        client.write(df, _TABLE, if_exists="append")
    return df
