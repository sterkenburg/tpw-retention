"""Daily retention pipeline. THE main job.

Runs at 7 AM via Cloud Scheduler.
1. Load data
2. Calculate supplier stats
3. Calculate signals (churn, engagement, renewal)
4. Determine actions
5. Execute actions (CRM tasks, Slack)
6. Save everything to BigQuery

Note: Email actions are disabled until email addresses are available.
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from actions import crm, slack
from analytics import projected_value, supplier_stats
from data import activity, client, leads, suppliers
from signals import churn_scorer, engagement


def run():
    print(f"\n{'='*60}")
    print(f"TPW Retention Pipeline — {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    # ------------------------------------------------------------------
    # 1. Load data
    # ------------------------------------------------------------------
    print("[1/6] Loading data...")
    df_suppliers = suppliers.get_current()
    df_activity = activity.get_last_90d()
    df_leads = leads.get_last_90d()
    df_contract_activity = activity.get_contract_period_views(df_suppliers)
    df_contract_leads = leads.get_contract_period_leads(df_suppliers)
    print(f"        Suppliers: {len(df_suppliers)}")
    print(f"        Activity events: {len(df_activity)}")
    print(f"        Leads: {len(df_leads)}")
    print(f"        Contract views: {len(df_contract_activity)}")
    print(f"        Contract leads: {len(df_contract_leads)}")

    # ------------------------------------------------------------------
    # 2. Calculate supplier stats
    # ------------------------------------------------------------------
    print("[2/6] Calculating supplier stats...")
    stats = supplier_stats.calculate(
        df_suppliers, df_activity, df_leads,
        contract_activity=df_contract_activity,
        contract_leads=df_contract_leads,
    )
    stats = projected_value.add_benchmarks(stats)
    stats["estimated_value_30d"] = projected_value.calculate(stats)
    print(f"        Stats rows: {len(stats)}")

    # ------------------------------------------------------------------
    # 3. Calculate signals
    # ------------------------------------------------------------------
    print("[3/6] Calculating signals...")
    signals = churn_scorer.calculate(stats)
    print(f"        P1: {(signals['priority_tier'] == 'P1').sum()}")
    print(f"        P2: {(signals['priority_tier'] == 'P2').sum()}")
    print(f"        P3: {(signals['priority_tier'] == 'P3').sum()}")
    print(f"        P4: {(signals['priority_tier'] == 'P4').sum()}")

    declining = engagement.detect_decline(signals)
    inactive = engagement.detect_no_activity(signals)
    print(f"        Declining engagement: {len(declining)}")
    print(f"        No activity 30d: {len(inactive)}")

    # ------------------------------------------------------------------
    # 4. Determine actions
    # ------------------------------------------------------------------
    print("[4/6] Determining actions...")
    actions_taken = []

    # P1 → CRM tasks
    p1 = signals[signals["priority_tier"] == "P1"]
    for _, row in p1.iterrows():
        created = crm.create_retention_task(
            profile_id=row["profile_id"],
            profile_name=row["profile_name"],
            category=row["category"],
            plan_value=row["plan_value"],
            plan_end=row["plan_end"],
            churn_probability=row["churn_probability"],
            risk_factors=row["risk_factors"],
            account_manager=row.get("account_manager", ""),
        )
        actions_taken.append({
            "profile_id": row["profile_id"],
            "action_type": "crm_task",
            "action_detail": "P1 retention task",
            "executed": created,
            "action_date": pd.Timestamp.now(),
        })
    print(f"        CRM tasks created: {sum(a['executed'] for a in actions_taken)}")

    # NOTE: Email actions disabled until supplier email addresses are available
    # TODO: Add email source (profiles table, CRM, or separate user table)

    # ------------------------------------------------------------------
    # 5. Save to BigQuery
    # ------------------------------------------------------------------
    print("[5/6] Saving to BigQuery...")

    # Supplier stats — align columns to BigQuery schema
    stats_cols = [
        "profile_id", "profile_name", "email", "phone", "category",
        "plan_name", "plan_value", "plan_start", "plan_end",
        "days_until_renewal", "business_status", "account_manager",
        "profile_completion_pct", "profile_views_30d", "profile_views_30_60d",
        "engagement_trend", "leads_30d", "days_since_last_lead",
        "days_since_last_login", "estimated_value_30d",
        "contract_views_total", "contract_leads_total",
        "category_avg_views_30d", "category_avg_leads_30d",
        "benchmark_views_top10pct", "benchmark_leads_top10pct",
        "churn_probability", "priority_tier", "risk_factors",
        "recommended_action", "stats_date",
    ]
    stats_df = signals.copy()
    for col in stats_cols:
        if col not in stats_df.columns:
            stats_df[col] = None

    # Delete today's rows first to prevent duplicates on re-runs
    client.delete_today("supplier_stats_daily", date_column="stats_date")
    client.write(stats_df[stats_cols], "supplier_stats_daily", if_exists="append")
    print("        → supplier_stats_daily")

    # Signals (subset)
    signals_cols = [
        "profile_id", "churn_probability", "priority_tier",
        "risk_factors", "recommended_action", "stats_date",
    ]
    client.delete_today("signals_daily", date_column="stats_date")
    client.write(signals[signals_cols], "signals_daily", if_exists="append")
    print("        → signals_daily")

    # Actions log
    if actions_taken:
        df_actions = pd.DataFrame(actions_taken)
        client.delete_today("actions_log", date_column="DATE(action_date)")
        client.write(df_actions, "actions_log", if_exists="append")
        print("        → actions_log")

    # ------------------------------------------------------------------
    # 6. Slack summary
    # ------------------------------------------------------------------
    print("[6/6] Posting Slack summary...")
    revenue_at_risk = p1["plan_value"].sum() + signals[signals["priority_tier"] == "P2"]["plan_value"].sum()
    slack.send_summary(
        total_suppliers=len(signals),
        p1_count=len(p1),
        p2_count=(signals["priority_tier"] == "P2").sum(),
        p3_count=(signals["priority_tier"] == "P3").sum(),
        revenue_at_risk=revenue_at_risk,
    )
    print("        → Slack sent")

    print(f"\n{'='*60}")
    print("Pipeline complete.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    run()
