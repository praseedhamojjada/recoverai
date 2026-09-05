from backend.app.services.recovery_simulator import (
    simulate_recovery,
)


def execute_recovery(payment):
    """
    Execute an approved recovery action.

    Guardrails must already have approved the action
    before this function is called.
    """

    if not payment["recovery_allowed"]:
        return {
            "payment_id": payment["payment_id"],
            "status": "blocked",
            "action": payment["recommended_action"],
            "recovered_amount": 0.0,
            "message": "Recovery blocked by policy.",
        }

    result = simulate_recovery(payment)

    if result["success"]:
        return {
            "payment_id": payment["payment_id"],
            "status": "recovered",
            "action": result["action"],
            "recovered_amount": result[
                "recovered_amount"
            ],
            "message": (
                "Recovery action succeeded."
            ),
        }

    return {
        "payment_id": payment["payment_id"],
        "status": "failed",
        "action": result["action"],
        "recovered_amount": 0.0,
        "message": (
            "Recovery action was attempted "
            "but was unsuccessful."
        ),
    }