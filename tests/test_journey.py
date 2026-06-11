"""Journey stage routing — including the will_churn save-population rules."""

import pytest

from actions import directives
from signals import journey


def _row(**overrides):
    base = {
        "renewal_status": "active",
        "first_term": False,
        "days_until_renewal": 200,
        "at_risk_tier": "P4",
    }
    return {**base, **overrides}


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        # priority order: lapsed wins over everything
        (_row(renewal_status="lapsed", first_term=True, at_risk_tier="P1"), "lapsed"),
        (_row(renewal_status="some_future_status"), "lapsed"),  # unknown ⇒ winback pool
        # already_renewed is retained for a future term
        (_row(renewal_status="already_renewed", at_risk_tier="P1"), "healthy"),
        # active first-termers onboard; will_churn first-termers do NOT
        (_row(first_term=True), "onboarding"),
        (
            _row(renewal_status="will_churn", first_term=True, days_until_renewal=30),
            "renewal_window",
        ),
        (
            _row(renewal_status="will_churn", first_term=True, at_risk_tier="P2"),
            "at_risk",
        ),
        # renewal window outranks at_risk
        (_row(days_until_renewal=45, at_risk_tier="P1"), "renewal_window"),
        (_row(days_until_renewal=0, at_risk_tier="P4"), "renewal_window"),
        # at_risk needs P1/P2
        (_row(at_risk_tier="P1"), "at_risk"),
        (_row(at_risk_tier="P2"), "at_risk"),
        (_row(at_risk_tier="P3"), "healthy"),
        # will_churn never lands healthy when tiered P1/P2 (the +0.40 bump
        # guarantees ≥ P2 in production)
        (_row(renewal_status="will_churn", at_risk_tier="P2"), "at_risk"),
        (_row(), "healthy"),
    ],
)
def test_stage_routing(row, expected):
    assert journey.stage(row) == expected


def test_stage_levers_reference_real_levers():
    for stage_name, lever_types in journey.STAGE_LEVERS.items():
        for typ in lever_types:
            assert typ in directives.LEVERS, f"{stage_name} → unknown lever {typ}"


def test_every_stage_has_a_lever_mapping():
    assert set(journey.STAGE_LEVERS) == set(journey.STAGE_ORDER)
