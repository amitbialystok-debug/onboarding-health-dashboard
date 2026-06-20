# Business logic for computing onboarding health scores per account


def compute_health_score(account) -> dict:
    """
    Compute an onboarding health score (0-100) for an Account.

    Scoring model (four weighted components):
      - Seat adoption       35%  seats_active / seats_purchased
      - Login engagement    30%  logins_last_30_days / seats_active
      - Support ticket load 20%  support_tickets_open / seats_active
      - NPS score           15%  nps_score (skipped if None; remaining weight
                                 is redistributed proportionally)

    Each component is scored on three tiers: full (100%), partial (50%), low (0%).
    The final integer score maps to a risk level:
      70-100 → Healthy  |  40-69 → At Risk  |  0-39 → Critical
    """
    components = []  # list of (weight, points_earned, signal_str)

    # --- 1. Seat adoption (35%) ---
    adoption_rate = (
        account.seats_active / account.seats_purchased
        if account.seats_purchased > 0
        else 0.0
    )
    adoption_pct = round(adoption_rate * 100)
    if adoption_rate >= 0.80:
        points = 1.0
        signal = f"Strong seat adoption ({adoption_pct}%)"
    elif adoption_rate >= 0.50:
        points = 0.5
        signal = f"Moderate seat adoption ({adoption_pct}%)"
    else:
        points = 0.0
        signal = f"Low seat adoption ({adoption_pct}%)"
    components.append((35, points, signal))

    # --- 2. Login engagement (30%) ---
    logins_per_seat = (
        account.logins_last_30_days / account.seats_active
        if account.seats_active > 0
        else 0.0
    )
    logins_rounded = round(logins_per_seat, 1)
    if logins_per_seat >= 3.0:
        points = 1.0
        signal = f"Strong login engagement ({logins_rounded} logins per active seat)"
    elif logins_per_seat >= 1.0:
        points = 0.5
        signal = f"Moderate login engagement ({logins_rounded} logins per active seat)"
    else:
        points = 0.0
        signal = f"Low login engagement ({logins_rounded} logins per active seat)"
    components.append((30, points, signal))

    # --- 3. Support ticket load (20%) ---
    tickets_per_seat = (
        account.support_tickets_open / account.seats_active
        if account.seats_active > 0
        else 0.0
    )
    tickets_rounded = round(tickets_per_seat, 2)
    if tickets_per_seat < 0.10:
        points = 1.0
        signal = f"Low support ticket load ({tickets_rounded} tickets per active seat)"
    elif tickets_per_seat <= 0.30:
        points = 0.5
        signal = f"Moderate support ticket load ({tickets_rounded} tickets per active seat)"
    else:
        points = 0.0
        signal = f"High support ticket load ({tickets_rounded} tickets per active seat)"
    components.append((20, points, signal))

    # --- 4. NPS score (15%) — optional ---
    if account.nps_score is not None:
        nps = account.nps_score
        if nps >= 8:
            points = 1.0
            signal = f"Positive NPS score ({nps}/10)"
        elif nps >= 5:
            points = 0.5
            signal = f"Neutral NPS score ({nps}/10)"
        else:
            points = 0.0
            signal = f"Poor NPS score ({nps}/10)"
        components.append((15, points, signal))

    # --- Aggregate score ---
    # If NPS is absent the total weight is 85; normalise to keep score on 0-100.
    total_weight = sum(w for w, _, _ in components)
    raw = sum(w * p for w, p, _ in components)
    score = round((raw / total_weight) * 100) if total_weight > 0 else 0

    # --- Risk level ---
    if score >= 70:
        risk_level = "Healthy"
    elif score >= 40:
        risk_level = "At Risk"
    else:
        risk_level = "Critical"

    signals = [s for _, _, s in components]

    return {"score": score, "risk_level": risk_level, "signals": signals}
