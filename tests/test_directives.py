"""Directive generation: treatment-only output, leak assertion, gating, scoping."""

import pandas as pd
import pytest

from actions import directives
from signals import cohort


def _patch_arms(monkeypatch, treatment: set[str], control: set[str]):
    monkeypatch.setattr(cohort, "treatment_ids", lambda eid: set(treatment))
    monkeypatch.setattr(
        cohort.client,
        "query",
        lambda sql, **kw: pd.DataFrame({"profile_id": sorted(control)}),
    )


def test_generate_emits_treatment_only_all_levers(monkeypatch):
    _patch_arms(monkeypatch, treatment={"10", "11"}, control={"20"})
    df = directives.generate("stage1_exposure")
    assert set(df["profile_id"]) == {"10", "11"}
    assert (df["arm"] == "treatment").all()
    assert set(df["type"]) == {"boost", "optimize", "newsletter", "email"}
    assert len(df) == 2 * 4  # every treatment supplier × every stage1 lever


def test_generate_raises_on_control_leak(monkeypatch):
    # A control id appearing in the produced set must hard-fail, never dispatch.
    _patch_arms(monkeypatch, treatment={"10", "20"}, control={"20"})
    with pytest.raises(AssertionError, match="Holdout violation"):
        directives.generate("stage1_exposure")


def test_levers_are_scoped_per_experiment():
    assert set(directives.levers_for("stage1_exposure")) == {
        "boost", "optimize", "newsletter", "email",
    }
    assert directives.levers_for("onboarding") == ["onboarding"]
    assert directives.levers_for("winback") == ["winback"]


def test_status_gated_until_flag_then_dry_run_then_delivered(monkeypatch):
    spec = directives.LEVERS["email"]
    now = pd.Timestamp("2026-06-11 12:00:00")

    monkeypatch.setattr(directives, "_DIR_CFG", {"bird_enabled": False, "dry_run": True})
    status, note, delivered = directives._status_for(spec, now)
    assert status == "gated" and spec["spike"] in note and pd.isna(delivered)

    monkeypatch.setattr(directives, "_DIR_CFG", {"bird_enabled": True, "dry_run": True})
    status, _, delivered = directives._status_for(spec, now)
    assert status == "dry_run" and pd.isna(delivered)

    monkeypatch.setattr(directives, "_DIR_CFG", {"bird_enabled": True, "dry_run": False})
    status, _, delivered = directives._status_for(spec, now)
    assert status == "delivered" and delivered == now


def test_every_lever_has_dispatch_contract_fields():
    for typ, spec in directives.LEVERS.items():
        for field in ("channel", "enable_flag", "spike", "experiments", "params"):
            assert field in spec, f"{typ} missing {field}"
        assert spec["experiments"], f"{typ} belongs to no experiment"
        assert all(e in cohort.EXPERIMENTS for e in spec["experiments"])
