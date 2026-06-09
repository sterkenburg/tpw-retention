"""Build cohort_assignment (WS-C) — stable-hash holdout for the retention pilot.

    python jobs/build_cohort.py [experiment_id]

Append-only: enrols newly-eligible suppliers from supplier_targeting into the
experiment via a stable hash (existing arms never reshuffle). Default experiment
is Stage-1 (low-exposure photographers ± videographers/music), exposure-lift test.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from signals import cohort


def run(experiment_id: str = "stage1_exposure") -> None:
    new = cohort.build(experiment_id)
    print(f"Experiment: {experiment_id}")
    print(f"Newly enrolled this run: {len(new)}")
    if not new.empty:
        print("\nNew enrolments by arm:")
        print(new["arm"].value_counts().to_string())
        print("\nNew enrolments by category × arm:")
        print(new.groupby(["category", "arm"]).size().to_string())

    # Full standing roster for the experiment.
    table = f"{cohort.client.PROJECT_ID}.{cohort.client.DATASET}.{cohort._COHORT_TABLE}"
    total = cohort.client.query(
        f"SELECT arm, COUNT(*) n FROM `{table}` "
        f"WHERE experiment_id = '{experiment_id}' GROUP BY arm ORDER BY arm"
    )
    print("\nStanding roster (all runs):")
    print(total.to_string(index=False))


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "stage1_exposure")
