MAX_RETRIES = 2
MIN_RECOVERY_SCORE = 45
HIGH_VALUE_THRESHOLD = 5000


def check_recovery_policy(payment):
    """
    Apply deterministic safety rules before
    allowing an automated recovery action.
    """

    reasons = []

    # Rule 1: Too many previous retries
    if payment["retry_count"] >= MAX_RETRIES:
        reasons.append("maximum_retry_limit_reached")

    # Rule 2: Recovery score too low
    if payment["recovery_score"] < MIN_RECOVERY_SCORE:
        reasons.append("low_recovery_probability")

    # Rule 3: High-value transactions require review
    if payment["amount"] >= HIGH_VALUE_THRESHOLD:
        reasons.append("high_value_transaction")

    # Decide whether automated recovery is allowed
    if reasons:
        return {
            "allowed": False,
            "reasons": reasons
        }

    return {
        "allowed": True,
        "reasons": []
    }