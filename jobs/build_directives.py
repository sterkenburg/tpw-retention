"""Build retention_directives (WS-D) — what each treatment supplier should receive.

    python jobs/build_directives.py [experiment_id]

Computes the four levers (boost / optimize / newsletter / email) for the TREATMENT
arm only (holdout enforced) and refreshes retention_directives. Channels dispatch
only once their G0 spike flips the flag in config; until then directives are
written with status='gated'. Nothing is sent to Elastic/Bird/scraper here.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from actions import directives


def run(experiment_id: str = "stage1_exposure") -> None:
    df = directives.build(experiment_id)
    print(f"Experiment: {experiment_id}")
    print(f"Directives written: {len(df)}  (treatment suppliers × {len(directives.LEVERS)} levers)")
    if df.empty:
        return
    print("\nBy type × status:")
    print(df.groupby(["type", "status"]).size().to_string())
    print("\nChannel gating (flip ON after the spike lands):")
    for typ, spec in directives.LEVERS.items():
        enabled = directives._DIR_CFG.get(spec["enable_flag"], False)
        state = "ENABLED" if enabled else f"gated → {spec['spike']}"
        print(f"  {typ:<11} {spec['channel']:<22} {state}")


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "stage1_exposure")
