from backend.app.services.recovery_engine import (
    calculate_recovery_score,
    classify_priority,
    recommend_action,
)


def test_recovery_score():

    payment = {
        "previous_success_rate": 0.8,
        "retry_count": 0,
        "days_since_last_attempt": 1,
        "failure_reason": "network_error",
    }

    score = calculate_recovery_score(payment)

    assert score == 90


def test_priority():

    assert classify_priority(90) == "HIGH"
    assert classify_priority(60) == "MEDIUM"
    assert classify_priority(30) == "LOW"


def test_recommendation():

    payment = {
        "failure_reason": "network_error"
    }

    assert recommend_action(payment, 80) == "retry_payment"