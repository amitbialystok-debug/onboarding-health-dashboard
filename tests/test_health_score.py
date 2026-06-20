# pytest unit tests for the health score engine

from types import SimpleNamespace

from backend.services.health_score import compute_health_score


def test_healthy_account():
    account = SimpleNamespace(
        seats_purchased=100,
        seats_active=90,
        logins_last_30_days=400,
        support_tickets_open=3,
        nps_score=9,
    )
    result = compute_health_score(account)
    assert result["score"] >= 70
    assert result["risk_level"] == "Healthy"


def test_critical_account():
    account = SimpleNamespace(
        seats_purchased=100,
        seats_active=10,
        logins_last_30_days=4,
        support_tickets_open=20,
        nps_score=2,
    )
    result = compute_health_score(account)
    assert result["score"] < 40
    assert result["risk_level"] == "Critical"


def test_missing_nps():
    account = SimpleNamespace(
        seats_purchased=50,
        seats_active=40,
        logins_last_30_days=120,
        support_tickets_open=2,
        nps_score=None,
    )
    result = compute_health_score(account)
    assert isinstance(result["score"], int)
    assert result["risk_level"] in {"Healthy", "At Risk", "Critical"}
    assert isinstance(result["signals"], list)
    assert len(result["signals"]) == 3  # NPS component skipped, only 3 signals
