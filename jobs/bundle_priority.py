"""Synthesize the per-category reports into bundle-priority tiers.

Ranks non-venue categories by **Exposure-Addressable Revenue (EAR)** — an estimate
of the annual subscription euros each category could plausibly recover by closing
its exposure gap (lifting below-cliff suppliers to above-cliff churn):

    EAR = (active × below_cliff_share) × max(0, churn_below − churn_above) × avg_plan_value

i.e. (# below the 330-view cliff) × (the churn the cliff costs them) × (their fee).
When a category's above-cliff group is too small to be a reference (n<10), the
pooled non-venue above-cliff churn is used instead. Tiers combine EAR (impact),
the size of the addressable gap, churn, and renewal volume (measurability).
Writes docs/category_analysis/00_bundle_priority.md.
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from analytics import category_report
from data import client

_OUT = Path(__file__).parent.parent / "docs" / "category_analysis" / "00_bundle_priority.md"
_VENUE = "Trouwlocaties"
_RETAIL = {"Trouwringen", "Trouwpak", "Catering", "Trouwkaarten", "Huwelijksbedankjes",
           "Bruidsschoenen", "Bruidsaccessoires", "Trouwauto"}
_CLIFF = 330
_MIN_ACTIVE = 10
_SPAN_YEARS = (date.today() - date(2024, 3, 1)).days / 365.0


def _plan_values() -> pd.DataFrame:
    return client.query_eu(
        "SELECT category, COUNT(*) active, ROUND(AVG(plan_value)) avg_plan_value "
        "FROM `tpw-ga4-bigquery.retention.supplier_targeting` GROUP BY 1"
    )


def _metrics(category: str, coh: pd.DataFrame, pv: pd.DataFrame, pooled_above: float) -> dict:
    below = coh[coh.views_pre < _CLIFF]
    above = coh[coh.views_pre >= _CLIFF]
    # Use the category's own above-cliff churn only if it has a reliable N.
    churn_above = above.churned.mean() if len(above) >= 10 else pooled_above
    churn_below = below.churned.mean() if len(below) else 0.0
    row = pv[pv.category == category]
    active = int(row.active.iloc[0]) if len(row) else 0
    has_fee = len(row) and pd.notna(row.avg_plan_value.iloc[0])
    fee = float(row.avg_plan_value.iloc[0]) if has_fee else 0.0
    below_share = len(below) / len(coh)
    lift = max(0.0, churn_below - churn_above)
    return {
        "category": category, "active": active, "annual_renewals": len(coh) / _SPAN_YEARS,
        "churn": coh.churned.mean(), "below_cliff_share": below_share,
        "churn_below": churn_below, "churn_above": churn_above, "exposure_lift": lift,
        "ref_borrowed": len(above) < 10, "avg_plan_value": fee,
        "rev_at_risk": active * coh.churned.mean() * fee,
        "ear": active * below_share * lift * fee,
    }


def _tier(m: dict) -> int:
    """1=pilot now, 2=next wave, 3=different lever / monitor."""
    addressable = m["below_cliff_share"] >= 0.30 and m["exposure_lift"] >= 0.10
    if not addressable or m["ear"] < 1000:
        return 3  # exposure won't move them, or the € is commercially negligible
    powered = m["annual_renewals"] >= 40 or m["active"] >= 50
    if m["churn"] >= 0.25 and powered and m["ear"] >= 8000:
        return 1
    return 2


def run() -> None:
    pv = _plan_values()
    cats = [c for c in pv.category if c != _VENUE and c not in _RETAIL]

    # Pass 1: fetch cohorts; keep categories with enough current base + decisions.
    cohorts = {}
    for c in cats:
        active_n = int(pv[pv.category == c].active.iloc[0])
        if active_n < _MIN_ACTIVE:
            continue
        coh = category_report._fetch(c)["cohort"]
        if len(coh) >= 30:
            cohorts[c] = coh

    # Pooled non-venue above-cliff churn — the reference for thin-above categories.
    allc = pd.concat(cohorts.values())
    pooled_above = allc[allc.views_pre >= _CLIFF].churned.mean()

    rows = [_metrics(c, coh, pv, pooled_above) for c, coh in cohorts.items()]
    for m in rows:
        m["tier"] = _tier(m)
    rows.sort(key=lambda m: (m["tier"], -m["ear"]))

    lines = ["# Bundle-priority synthesis (non-venue categories)", "",
         f"_Generated {date.today()}. Ranked by **Exposure-Addressable Revenue (EAR)** — "
         "annual subscription € recoverable by closing each category's exposure gap. "
         "See per-category reports for detail._", "",
         "**EAR** = (active × share below 330-view cliff) × (churn_below − churn_above) "
         "× avg annual plan value. Rewards categories that are (a) exposure-starved, "
         "(b) where the cliff actually drives churn, and (c) worth real money. "
         f"Pooled non-venue above-cliff churn (reference for thin-above categories): "
         f"**{pooled_above*100:.0f}%**.", ""]

    tier_names = {1: "Tier 1 — Pilot now", 2: "Tier 2 — Next wave",
                  3: "Tier 3 — Different lever / monitor"}
    tier_desc = {
        1: "High churn, large below-cliff population where the cliff drives churn, enough "
           "renewals to measure, and meaningful € at stake. **Start here.**",
        2: "Exposure-addressable but smaller volume, lower churn, or less € — fold in "
           "after Tier 1 proves the mechanism.",
        3: "Already well-exposed (most above the cliff) so exposure won't move them, OR "
           "high-churn but low-fee / browse-not-inquire — a different lever (pricing / fit / "
           "model), not redistribution.",
    }
    for t in (1, 2, 3):
        grp = [m for m in rows if m["tier"] == t]
        if not grp:
            continue
        lines += [f"## {tier_names[t]}", "", tier_desc[t], "",
              "| category | active | renewals/yr | churn | below cliff | churn below→above | "
              "avg fee | rev at risk/yr | **EAR/yr** |", "|---|---|---|---|---|---|---|---|---|"]
        for m in grp:
            ref = "*" if m["ref_borrowed"] else ""
            lines.append(
                f"| {m['category']} | {m['active']} | {m['annual_renewals']:.0f} | "
                f"{m['churn']*100:.0f}% | {m['below_cliff_share']*100:.0f}% | "
                f"{m['churn_below']*100:.0f}%→{m['churn_above']*100:.0f}%{ref} | "
                f"€{m['avg_plan_value']:.0f} | €{m['rev_at_risk']:,.0f} | "
                f"**€{m['ear']:,.0f}** |")
        lines.append("")

    total_ear = sum(m["ear"] for m in rows if m["tier"] == 1)
    ear = {m["category"]: m["ear"] for m in rows}
    lines += ["## Notes", "",
          f"- **Tier-1 exposure-addressable revenue ≈ €{total_ear:,.0f}/yr** — the pilot's "
          "headline opportunity if the lever works.",
          "- `*` = above-cliff churn borrowed from the pooled non-venue reference (the "
          "category's own above-cliff group was too small, n<10).",
          "- EAR is an upper bound (assumes below-cliff suppliers reach the above-cliff "
          "churn rate); the holdout pilot measures the fraction actually captured.",
          "- Revenue from `plan_value` (avg annual fee); churn split by the 330-view cliff "
          "in the pre-renewal year. Venue + retail excluded (different models).",
          "- High-churn but low-EAR categories (e.g. Huwelijksnacht: 45% churn, €129 fee) "
          "are a **supply-health** concern, not a revenue one — note them, don't pilot them.",
          "- **Stage-1 cohort implication:** Trouwfotograaf is the clear #1 (Tier 1). The "
          "planned pool also adds Videograaf + Muziek — but by EAR, **Trouwambtenaar "
          f"(€{ear.get('Trouwambtenaar', 0):,.0f}) and Muziek (€{ear.get('Muziek', 0):,.0f}) "
          f"out-rank Videograaf (€{ear.get('Videograaf', 0):,.0f})**. "
          "Consider officiants over videographers for the pooled arm (WS-C EXPERIMENTS).", ""]
    _OUT.write_text("\n".join(lines))
    print(f"Wrote {_OUT}\n")
    for m in rows:
        print(f"  T{m['tier']}  {m['category']:<18} EAR €{m['ear']:>9,.0f}  "
              f"churn {m['churn']*100:>3.0f}%  below-cliff {m['below_cliff_share']*100:>3.0f}%"
              f"{'  (ref*)' if m['ref_borrowed'] else ''}")


if __name__ == "__main__":
    run()
