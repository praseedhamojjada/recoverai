import hashlib


def simulate_recovery(payment):
    """
    Deterministically simulate the outcome of a
    recovery action.

    The same payment will always produce the same
    simulated result.
    """

    action = payment["recommended_action"]
    amount = payment["amount"]
    failure_reason = payment["failure_reason"]

    # Automatic recovery is not attempted for manual review
    if action == "manual_review":
        return {
            "payment_id": payment["payment_id"],
            "action": action,
            "success": False,
            "recovered_amount": 0.0,
        }

    probabilities = {
        ("network_error", "retry_payment"): 0.80,
        ("timeout", "retry_payment"): 0.75,
        ("insufficient_funds", "send_payment_link"): 0.55,
        ("bank_declined", "send_payment_link"): 0.45,
        ("expired_card", "request_payment_method_update"): 0.60,
    }

    probability = probabilities.get(
        (failure_reason, action),
        0.30
    )

    # Generate a deterministic value between 0 and 1
    hash_value = hashlib.sha256(
        payment["payment_id"].encode()
    ).hexdigest()

    deterministic_value = (
        int(hash_value[:8], 16) / 0xFFFFFFFF
    )

    success = deterministic_value < probability

    recovered_amount = (
        amount if success else 0.0
    )

    return {
        "payment_id": payment["payment_id"],
        "action": action,
        "success": success,
        "recovered_amount": recovered_amount,
    }