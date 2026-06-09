"""Generate the per-category views/leads/danger-zone report.

    python jobs/analyze_category.py "Trouwfotograaf"
    python jobs/analyze_category.py --non-venue   # batch: every non-venue category
    python jobs/analyze_category.py               # lists categories with active suppliers

Writes docs/category_analysis/<slug>.md. Run once per category — the methodology
is identical across categories so the reports are directly comparable.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analytics import category_report
from data import client

_OUT = Path(__file__).parent.parent / "docs" / "category_analysis"

# Segment logic mirrors src/signals/targeting.py (venue + retail are excluded).
_VENUE = "Trouwlocaties"
_RETAIL = {"Trouwringen", "Trouwpak", "Catering", "Trouwkaarten", "Huwelijksbedankjes",
           "Bruidsschoenen", "Bruidsaccessoires", "Trouwauto"}
_MIN_ACTIVE = 10  # skip micro-categories with too little data to be meaningful


def _slug(category: str) -> str:
    return category.lower().replace(" ", "-").replace("/", "-")


def _list_categories() -> None:
    df = client.query_eu(
        "SELECT category, COUNT(*) n FROM `tpw-ga4-bigquery.retention.supplier_targeting` "
        "GROUP BY 1 ORDER BY n DESC"
    )
    print("Categories with active suppliers (pass one as an argument):")
    print(df.to_string(index=False))


def run(category: str) -> dict:
    md, stats = category_report.build_report(category)
    _OUT.mkdir(parents=True, exist_ok=True)
    path = _OUT / f"{_slug(category)}.md"
    path.write_text(md)
    print(f"Wrote {path}  (active={stats['n_active']} decisions={stats['n_decisions']} "
          f"churn={stats['churn_rate']} danger_zone={stats['danger_zone_share']})")
    return stats


def run_non_venue() -> None:
    cats = client.query_eu(
        "SELECT category, COUNT(*) n FROM `tpw-ga4-bigquery.retention.supplier_targeting` "
        "GROUP BY 1 ORDER BY n DESC"
    )
    targets = cats[
        (~cats.category.isin([_VENUE, *_RETAIL])) & (cats.n >= _MIN_ACTIVE)
    ].category.tolist()
    skipped = cats[(~cats.category.isin([_VENUE, *_RETAIL])) & (cats.n < _MIN_ACTIVE)]
    print(f"Generating {len(targets)} non-venue categories (active >= {_MIN_ACTIVE})...\n")
    rows = []
    for c in targets:
        rows.append(run(c))
    print("\nINDEX rows (paste into README):")
    for r in sorted(rows, key=lambda r: -r["n_active"]):
        dz = r["danger_zone_share"]
        dz_s = f"{dz*100:.0f}%" if dz is not None else "—"
        cr = r["churn_rate"]
        cr_s = f"{cr*100:.0f}%" if cr is not None else "—"
        print(f"| {r['category']} | {r['n_active']} | {r['n_decisions']} | {cr_s} | {dz_s} | "
              f"[{_slug(r['category'])}.md]({_slug(r['category'])}.md) |")
    if len(skipped):
        print(f"\nSkipped (active < {_MIN_ACTIVE}): "
              + ", ".join(f"{c} ({n})" for c, n in zip(skipped.category, skipped.n, strict=False)))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--non-venue":
        run_non_venue()
    elif len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        _list_categories()
