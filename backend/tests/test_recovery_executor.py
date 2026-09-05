from backend.app.services.recovery_executor import (
    execute_recovery,
)


def test_blocked_recovery():

    payment = {
        "payment_id": "test_001",
        "recovery_allowed": False,
        "recommended_action": "retry_payment",
    }

    result = execute_recovery(payment)

    assert result["status"] == "blocked"
    assert result["recovered_amount"] == 0.0