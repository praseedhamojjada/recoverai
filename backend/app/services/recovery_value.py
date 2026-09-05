def estimate_recovery_probability(score):
    """
    Convert recovery score into an estimated
    probability of successful recovery.
    """

    return round(score / 100, 2)


def calculate_expected_recovery(amount, probability):
    """
    Estimate the monetary value expected
    from attempting recovery.
    """

    return round(amount * probability, 2)


def calculate_action_probability(failure_reason, action):
    """
    Estimate success probability for a
    particular recovery action.
    """

    probabilities = {
        ("network_error", "retry_payment"): 0.80,
        ("timeout", "retry_payment"): 0.75,
        ("insufficient_funds", "send_payment_link"): 0.55,
        ("bank_declined", "send_payment_link"): 0.45,
        ("expired_card", "request_payment_method_update"): 0.60,
    }

    return probabilities.get(
        (failure_reason, action),
        0.30
    )