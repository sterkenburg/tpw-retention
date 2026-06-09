"""Run the WS-E measurement harness — the G1 exposure-lift readout.

    python jobs/build_measurement.py [experiment_id]

Difference-in-differences on supplier_exposure_daily, treatment vs control arms
from cohort_assignment. Before the levers go live this reports BASELINE BALANCE
(arms should be indistinguishable); once they're live it reports the lift.
Writes the per-supplier pre/post panel to retention.measurement_panel.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analytics import measurement


def run(experiment_id: str = "stage1_exposure") -> None:
    r = measurement.readout(experiment_id)
    if "error" in r:
        print(f"{experiment_id}: {r['error']}")
        return

    print(f"Experiment: {r['experiment_id']}")
    print(f"Windows: pre={r['pre_days']}d  post={r['post_days']}d  "
          f"(observed post so far: {r['post_days_observed']}d)")
    if r["post_days_observed"] == 0:
        print(">> Levers not live yet — POST window empty. Reading BASELINE BALANCE "
              "only (baseline_balance_p should be NS / > 0.05).")

    print("\nPer-metric readout (per-supplier per-day rates):")
    header = (f"{'metric':<16}{'base_T':>8}{'base_C':>8}{'bal_p':>8}"
              f"{'post_T':>8}{'post_C':>8}{'lift%':>8}{'DiD_p':>8}{'d':>7}")
    print(header)
    print("-" * len(header))
    for m in r["metrics"]:
        print(f"{m['metric']:<16}"
              f"{m['baseline_treatment_per_day']:>8}{m['baseline_control_per_day']:>8}"
              f"{m['baseline_balance_p']:>8}"
              f"{m['post_treatment_per_day']:>8}{m['post_control_per_day']:>8}"
              f"{m['lift_pct']:>8}{m['did_p']:>8}{m['did_cohens_d']:>7}")

    c = r["contamination"]
    print(f"\nContamination audit: {c['status']}")
    print(f"  control n={c['control_n']}; logs checked: {c['emitter_logs_checked'] or 'none'}")
    if c["control_contamination"]:
        print(f"  leaks: {c['control_contamination']}")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "stage1_exposure")
