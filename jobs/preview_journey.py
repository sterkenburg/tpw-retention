"""Preview the supplier journey (read-only, dry-run) — stage + next-best-action.

    python jobs/preview_journey.py [--sample N]

Places each supplier (latest `supplier_targeting` snapshot) in a lifecycle stage
and shows the levers they'd receive there + the gate blocking each. Writes nothing
and dispatches nothing — a purely inspectable view of the journey the brain would
run once channels are enabled (docs/strategy/28). Run jobs/build_targeting.py first.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from actions import directives
from signals import journey


def run(sample: int = 8) -> None:
    df = journey.classify()
    if df.empty:
        print("supplier_targeting is empty — run jobs/build_targeting.py first.")
        return

    counts = df["journey_stage"].value_counts()
    print(f"Suppliers: {len(df)}\n")

    print("Journey stage → next-best-action (count):")
    for st in journey.STAGE_ORDER:
        levers = ", ".join(journey.STAGE_LEVERS[st]) or "— (monitor, no directive)"
        print(f"  {st:<15} {int(counts.get(st, 0)):>6}  →  {levers}")

    print("\nLever gating (what blocks dispatch today):")
    for typ in dict.fromkeys(t for st in journey.STAGE_ORDER for t in journey.STAGE_LEVERS[st]):
        status, note = directives.lever_status(typ)
        print(f"  {typ:<11} {status:<8} {note}")

    cols = [
        c for c in ["profile_id", "category", "at_risk_tier",
                    "days_until_renewal", "first_term", "renewal_status"]
        if c in df.columns
    ]
    print(f"\nSample suppliers (first {sample}):")
    for _, r in df.head(sample).iterrows():
        st = r["journey_stage"]
        print("\n  " + "  ".join(f"{c}={r[c]}" for c in cols))
        print(f"    stage = {st}")
        acts = journey.actions_for(st)
        if not acts:
            print("    next action: monitor (no directive)")
        for a in acts:
            print(f"    {a['type']:<11} [{a['status']}: {a['note'] or a['channel']}]")


if __name__ == "__main__":
    n = 8
    if "--sample" in sys.argv:
        n = int(sys.argv[sys.argv.index("--sample") + 1])
    run(n)
