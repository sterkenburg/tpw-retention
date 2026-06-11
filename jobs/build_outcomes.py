"""Build outcomes — renewal decisions for ended paid terms (ended-terms feed).

    python jobs/build_outcomes.py [months_back]

One labelled row per completed paid term in the window (default 24 months):
renewed / pending, plus the experiment arm where the decision happened after
enrolment. Feeds the Stage-2 renewal endpoint, the doc-24 recall backtest, and
winback analysis (doc 29 §2.5). Rebuilt in full on every run.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analytics import outcomes


def run(months_back: int = 24) -> None:
    df = outcomes.build(months_back=months_back)
    decided = df[~df["pending"]]
    print(f"outcomes: {len(df)} rows / {df['profile_id'].nunique()} suppliers "
          f"(terms ended in the last {months_back} months)")
    print(f"pending (ended inside the {outcomes.suppliers.RENEWAL_GRACE_DAYS}d grace window): "
          f"{int(df['pending'].sum())}")
    print(f"\nRenewal rate (decided): {decided['renewed'].mean():.1%}  (n={len(decided)})")
    print("\nBy first_term (decided):")
    print(decided.groupby("first_term")["renewed"].agg(["count", "mean"]).round(3).to_string())
    print("\nBy segment (decided):")
    print(decided.groupby("segment")["renewed"].agg(["count", "mean"]).round(3).to_string())

    enrolled = df[df["experiment_id"].notna()]
    if enrolled.empty:
        print("\nPost-enrolment outcome rows: 0 (no enrolled supplier has reached "
              "a renewal decision yet — expected pre-launch)")
    else:
        print("\nPost-enrolment outcome rows by experiment × arm:")
        print(enrolled.groupby(["experiment_id", "arm"]).size().to_string())


if __name__ == "__main__":
    run(int(sys.argv[1]) if len(sys.argv) > 1 else 24)
