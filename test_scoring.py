"""
Standalone smoke test for the health score engine.
Run from the project root: python test_scoring.py
"""

from types import SimpleNamespace

from backend.services.health_score import compute_health_score

accounts = [
    SimpleNamespace(
        company_name="Acme Corp",
        seats_purchased=50,
        seats_active=12,
        logins_last_30_days=30,
        support_tickets_open=8,
        nps_score=6,
    ),
    SimpleNamespace(
        company_name="GrowthFlow",
        seats_purchased=30,
        seats_active=28,
        logins_last_30_days=180,
        support_tickets_open=1,
        nps_score=9,
    ),
    SimpleNamespace(
        company_name="StallCo",
        seats_purchased=40,
        seats_active=6,
        logins_last_30_days=8,
        support_tickets_open=14,
        nps_score=3,
    ),
]

for account in accounts:
    result = compute_health_score(account)
    print(f"\n{account.company_name}")
    print(f"  Score:      {result['score']}/100")
    print(f"  Risk level: {result['risk_level']}")
    print("  Signals:")
    for signal in result["signals"]:
        print(f"    - {signal}")
