"""Targeting signal: tier blend (live-model union), scoring, segmentation."""

import pytest

from signals import targeting

# --- Live-model union (doc 24 §3) ------------------------------------------

@pytest.mark.parametrize(
    ("rule", "flag", "critical", "expected"),
    [
        ("P4", False, False, "P4"),  # no live signal → rule unchanged
        ("P4", True, False, "P2"),   # model flag lifts to at least P2
        ("P3", True, False, "P2"),
        ("P4", True, True, "P1"),    # Critical lifts to P1
        ("P2", True, True, "P1"),
        ("P1", True, False, "P1"),   # never downgraded
        ("P1", False, False, "P1"),
        ("P2", True, False, "P2"),   # already at the live tier → unchanged
    ],
)
def test_blend_tier_union(rule, flag, critical, expected):
    assert targeting._blend_tier(rule, flag, critical) == expected


# --- Rule score -------------------------------------------------------------

def _row(**overrides):
    base = {
        "views_365d": 1000,
        "exposure_trend": 0.0,
        "first_term": False,
        "term_months": 12,
        "days_since_last_view": 5,
        "renewal_status": "active",
    }
    return {**base, **overrides}


def test_at_risk_score_baseline_is_low():
    assert targeting._at_risk_score(_row()) == 0.10


def test_at_risk_score_low_exposure_stacks():
    assert targeting._at_risk_score(_row(views_365d=300)) == pytest.approx(0.40)
    assert targeting._at_risk_score(_row(views_365d=100)) == pytest.approx(0.50)


def test_at_risk_score_will_churn_bump_guarantees_p2():
    # base 0.10 + will_churn 0.40 = 0.50 ⇒ P2 even with perfect exposure
    score = targeting._at_risk_score(_row(renewal_status="will_churn"))
    assert score == pytest.approx(0.50)
    assert targeting._tier(score) == "P2"


def test_at_risk_score_clamps_to_one():
    score = targeting._at_risk_score(
        _row(
            views_365d=0,
            exposure_trend=-0.9,
            first_term=True,
            term_months=6,
            days_since_last_view=999,
            renewal_status="will_churn",
        )
    )
    assert score == 1.0


def test_tier_boundaries():
    assert targeting._tier(0.70) == "P1"
    assert targeting._tier(0.69) == "P2"
    assert targeting._tier(0.50) == "P2"
    assert targeting._tier(0.49) == "P3"
    assert targeting._tier(0.30) == "P3"
    assert targeting._tier(0.29) == "P4"


# --- Segmentation + status allowlist ----------------------------------------

def test_segment_classification():
    assert targeting._segment("Trouwlocaties") == "venue"
    assert targeting._segment("Trouwringen") == "retail"
    assert targeting._segment("Trouwfotograaf") == "non-venue"


def test_retained_statuses_allowlist():
    # will_churn = paid term still running (save population), NOT winback
    assert {"active", "already_renewed", "will_churn"} == targeting.RETAINED_STATUSES
