"""Per-category views / leads / churn-danger-zone report.

Generates the analysis we run for each marketplace category: the exposure (views)
and demand (leads) distributions for the active base, the views→leads relationship,
and the churn "danger zone" — churn rate by leads received in the year before the
renewal decision, the size of the low-lead group, and the thresholds to escape it.

Reusable across categories: `build_report(category)` returns (markdown, stats).
Run via `jobs/analyze_category.py <Category>` which writes docs/category_analysis/.

Data sources & definitions (kept identical across categories for comparability):
  - Active base   : retention.supplier_targeting (current active paid suppliers).
  - Views         : views_365d (trailing year, from supplier_exposure_daily).
  - Leads         : ga4_dataform_output.generate_lead, keyed by company_id=profile_id.
  - Churn cohort  : business_development renewal decisions with an OBSERVED outcome
                    (next plan exists), plan_end ≥ 2024-03-01 so the full prior-year
                    of leads is available (lead history starts 2023-02). Churn =
                    next plan downgraded to 'Gratis'.
"""

import numpy as np
import pandas as pd

from data import client

# Lead history starts 2023-02; require the full prior-year window to be observable.
_COHORT_START = "2024-03-01"
_LEAD_HISTORY_START = "2023-02-01"


def _pct(s: pd.Series, qs=(10, 25, 50, 75, 90, 100)) -> str:
    v = np.percentile(s, qs)
    return "  ".join(f"p{q}={x:.0f}" for q, x in zip(qs, v, strict=False))


def _fetch(category: str) -> dict:
    cat = category.replace("'", "''")
    # Active base + current-year leads (both EU → one query).
    active = client.query_eu(f"""
        WITH leads AS (
          SELECT CAST(company_id AS STRING) profile_id, COUNT(*) leads_365d
          FROM `tpw-ga4-bigquery.ga4_dataform_output.generate_lead`
          WHERE event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 365 DAY)
          GROUP BY 1
        )
        SELECT t.profile_id, t.views_365d, COALESCE(l.leads_365d,0) AS leads_365d, t.first_term
        FROM `tpw-ga4-bigquery.retention.supplier_targeting` t
        LEFT JOIN leads l ON t.profile_id = l.profile_id
        WHERE t.category = '{cat}'
    """)

    # Renewal-decision cohort (europe-west3).
    coh = client.query(f"""
        WITH p AS (
          SELECT profile_id, plan_name, plan_end,
                 LEAD(plan_name) OVER (PARTITION BY profile_id ORDER BY plan_start) AS next_plan
          FROM `tpw-ga4-bigquery.churn_prediction.business_development`
          WHERE category = '{cat}'
        )
        SELECT CAST(profile_id AS STRING) profile_id, plan_end,
               CASE WHEN next_plan='Gratis' THEN 1 ELSE 0 END AS churned
        FROM p
        WHERE plan_name!='Gratis' AND next_plan IS NOT NULL
          AND plan_end BETWEEN DATE('{_COHORT_START}') AND CURRENT_DATE()
    """)
    coh["plan_end"] = pd.to_datetime(coh["plan_end"])
    coh = coh.reset_index(drop=True)
    coh["did"] = coh.index

    # Leads in each supplier's pre-decision year (leads are EU, cohort is west3).
    ids = set(active["profile_id"]) | set(coh["profile_id"])
    leads = pd.DataFrame(columns=["profile_id", "event_date"])
    if ids:
        leads = client.query_eu(f"""
            SELECT CAST(company_id AS STRING) profile_id, event_date
            FROM `tpw-ga4-bigquery.ga4_dataform_output.generate_lead`
            WHERE event_date >= DATE('{_LEAD_HISTORY_START}')
              AND company_id IN ({",".join(str(int(i)) for i in ids if str(i).isdigit())})
        """)
        leads["event_date"] = pd.to_datetime(leads["event_date"])

    # Profile VIEWS history (view_item, EU) — same shape as leads. Filter to real
    # profile views ('Profiles index') so blog/article rows can't inflate a profile.
    views = pd.DataFrame(columns=["profile_id", "event_date", "v"])
    if ids:
        views = client.query_eu(f"""
            SELECT CAST(item_id AS STRING) profile_id, event_date, COUNT(*) v
            FROM `tpw-ga4-bigquery.ga4_dataform_output.view_item`
            WHERE event_date >= DATE('{_LEAD_HISTORY_START}')
              AND item_list_name IN ('Profiles index','profiles index')
              AND item_id IN ({",".join(f"'{i}'" for i in ids if str(i).isdigit())})
            GROUP BY 1, 2
        """)
        views["event_date"] = pd.to_datetime(views["event_date"])

    def _prewindow(events: pd.DataFrame, value_col: str | None) -> pd.Series:
        """Sum events (or rows) in each decision's pre-renewal year, by did."""
        if coh.empty or events.empty:
            return pd.Series(0, index=coh.index)
        mm = coh[["did", "profile_id", "plan_end"]].merge(events, on="profile_id", how="left")
        inwin = (mm.event_date > mm.plan_end - pd.Timedelta(days=365)) & (
            mm.event_date <= mm.plan_end
        )
        mm = mm[inwin.fillna(False)]
        agg = mm.groupby("did")[value_col].sum() if value_col else mm.groupby("did").size()
        return coh["did"].map(agg).fillna(0).astype(int)

    coh["leads_pre"] = _prewindow(leads, None)
    coh["views_pre"] = _prewindow(views, "v")
    return {"active": active, "cohort": coh}


_BUCKETS = [(0, 0, "0"), (1, 2, "1-2"), (3, 5, "3-5"), (6, 10, "6-10"),
            (11, 20, "11-20"), (21, 10**9, "21+")]

# Views/yr buckets centred on the 330-view churn cliff.
_VIEW_BUCKETS = [(0, 99, "0-99"), (100, 199, "100-199"), (200, 329, "200-329"),
                 (330, 499, "330-499"), (500, 999, "500-999"), (1000, 10**9, "1000+")]


def build_report(category: str) -> tuple[str, dict]:
    d = _fetch(category)
    a, coh = d["active"], d["cohort"]
    n = len(a)
    lines = [f"# {category} — views, leads & churn danger zone", ""]
    lines.append(f"_Generated from live data. Active paid suppliers: **{n}**. "
             f"Renewal decisions analysed (since {_COHORT_START}): **{len(coh)}**._")
    lines.append("")

    if n:
        a = a.copy()
        a["conv"] = a.leads_365d / a.views_365d.replace(0, np.nan) * 100
        corr = a[["views_365d", "leads_365d"]].corr().iloc[0, 1]
        lo = a.views_365d < 330
        lines += [
            "## Exposure & demand (active base, trailing year)", "",
            f"- **Views/yr:** mean {a.views_365d.mean():.0f}, median {a.views_365d.median():.0f}  "
            f"({_pct(a.views_365d)})",
            f"- **Leads/yr:** mean {a.leads_365d.mean():.1f}, median {a.leads_365d.median():.0f}  "
            f"({_pct(a.leads_365d)})",
            f"- **Got ≥1 lead:** {(a.leads_365d>0).mean()*100:.0f}% of suppliers",
            f"- **Views→leads:** Pearson r = **{corr:.2f}**, "
            f"median conversion **{a.conv.median():.2f} leads / 100 views**",
            f"- **Exposure split:** <330 views/yr → {lo.sum()} suppliers avg "
            f"{a.leads_365d[lo].mean():.1f} leads; ≥330 → {(~lo).sum()} suppliers avg "
            f"{a.leads_365d[~lo].mean():.1f} leads",
            "",
        ]

    if len(coh) >= 30:
        base = coh.churned.mean() * 100
        # --- By LEADS (with avg views per bucket) ---
        lines += ["## Churn danger zone — by LEADS (in the pre-renewal year)", "",
              f"Overall churn for this cohort: **{base:.0f}%**.", "",
              "| leads/yr | suppliers | % of base | churn rate | avg views/yr |",
              "|---|---|---|---|---|"]
        for lo_, hi_, lab in _BUCKETS:
            g = coh[(coh.leads_pre >= lo_) & (coh.leads_pre <= hi_)]
            if len(g):
                lines.append(f"| {lab} | {len(g)} | {len(g)/len(coh)*100:.0f}% | "
                         f"{g.churned.mean()*100:.0f}% | {g.views_pre.mean():.0f} |")
        lines.append("")
        dz = coh[coh.leads_pre <= 2]
        above2 = coh[coh.leads_pre > 2].churned.mean() * 100
        lines.append(f"**Danger zone (≤2 leads/yr): {len(dz)} suppliers = "
                 f"{len(dz)/len(coh)*100:.0f}% of the base, churning at "
                 f"{dz.churned.mean()*100:.0f}%** (vs {above2:.0f}% for those above 2). "
                 f"They average just {dz.views_pre.mean():.0f} views/yr.")
        lines.append("")
        # Only show a threshold when the "above" group is large enough to trust (n≥10).
        thr_parts = [f">{t}→{coh[coh.leads_pre>t].churned.mean()*100:.0f}%"
                     for t in [2, 5, 10, 20] if len(coh[coh.leads_pre > t]) >= 10]
        if thr_parts:
            lines.append("Thresholds to escape (leads): " + ", ".join(thr_parts) + ".")
            lines.append("")

        # --- By VIEWS (the upstream driver) ---
        vbase = coh[coh.views_pre > 0]
        lines += ["## Churn danger zone — by VIEWS (the upstream driver)", "",
              f"Pre-renewal-year profile views; r(views,leads) here is strong, so views "
              f"move churn earlier in the funnel. (Suppliers with view history: {len(vbase)}.)",
              "", "| views/yr | suppliers | % of base | churn rate | avg leads/yr |",
              "|---|---|---|---|---|"]
        for lo_, hi_, lab in _VIEW_BUCKETS:
            g = coh[(coh.views_pre >= lo_) & (coh.views_pre <= hi_)]
            if len(g):
                lines.append(f"| {lab} | {len(g)} | {len(g)/len(coh)*100:.0f}% | "
                         f"{g.churned.mean()*100:.0f}% | {g.leads_pre.mean():.1f} |")
        lines.append("")
        dzv = coh[coh.views_pre < 330]
        abovev = coh[coh.views_pre >= 330].churned.mean() * 100
        lines.append(f"**Below the 330-view cliff: {len(dzv)} suppliers = "
                 f"{len(dzv)/len(coh)*100:.0f}% of the base, churning at "
                 f"{dzv.churned.mean()*100:.0f}%** (vs {abovev:.0f}% at ≥330 views/yr).")
        lines.append("")
    else:
        lines += ["## Churn danger zone", "",
              f"_Only {len(coh)} renewal decisions since {_COHORT_START} — too few for a "
              "reliable per-bucket churn rate. See the non-venue aggregate in the README "
              "for the segment-level pattern._", ""]

    lines += ["## Caveats", "",
          "- Leads from `generate_lead` keyed by `company_id`=`profile_id`.",
          "- Views from `view_item` (`item_list_name`='Profiles index', keyed by "
          "`item_id`=`profile_id`) — real profile views only, excludes blog/article rows. "
          "History from 2023; this differs slightly from the active-base `views_365d` "
          "(supplier_exposure_daily, 2025+).",
          "- Churn = next plan downgraded to `Gratis`; cohort = observed outcomes only.",
          "- Distribution section = current active base (trailing 365d); danger-zone "
          "sections = historical renewal cohort (leads & views in each supplier's "
          "pre-decision year).",
          ""]
    stats = {
        "category": category, "n_active": n, "n_decisions": len(coh),
        "churn_rate": float(coh.churned.mean()) if len(coh) else None,
        "danger_zone_share": float((coh.leads_pre <= 2).mean()) if len(coh) else None,
    }
    return "\n".join(lines), stats
