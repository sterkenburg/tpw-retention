"""Build supplier_targeting (WS-B) — exposure-trend signal + at-risk + bundle cohort.

    python jobs/build_targeting.py

Reads supplier_exposure_daily (EU) + business_development (via suppliers), joins in
pandas, writes supplier_targeting to the US retention dataset.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from signals import targeting


def run() -> None:
    out = targeting.build()
    print(f"supplier_targeting: {len(out)} rows")
    print("\nBy segment:")
    print(out["segment"].value_counts().to_string())
    print("\nBy at-risk tier:")
    print(out["at_risk_tier"].value_counts().sort_index().to_string())
    elig = out[out["bundle_eligible"]]
    print(f"\nBundle-eligible (non-venue, low-exposure, active): {len(elig)}")
    print("  by category (top):")
    print(elig["category"].value_counts().head(8).to_string())


if __name__ == "__main__":
    run()
