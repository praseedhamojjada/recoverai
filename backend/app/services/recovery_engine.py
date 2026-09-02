import pandas as pd


def calculate_recovery_score(payment):
    """
    Calculate how likely a failed payment is to be recovered.
    Score ranges from 0 to 100.
    """

    score = 0

    # Customer has a good payment history
    if payment["previous_success_rate"] >= 0.7:
        score += 30
    elif payment["previous_success_rate"] >= 0.5:
        score += 20
    elif payment["previous_success_rate"] >= 0.3:
        score += 10

    # Fewer retries means we haven't exhausted recovery attempts
    if payment["retry_count"] == 0:
        score += 25
    elif payment["retry_count"] == 1:
        score += 20
    elif payment["retry_count"] == 2:
        score += 10

    # Recent failure is more recoverable
    if payment["days_since_last_attempt"] <= 1:
        score += 20
    elif payment["days_since_last_attempt"] <= 3:
        score += 15
    elif payment["days_since_last_attempt"] <= 5:
        score += 10

    # Some failure reasons are more recoverable
    if payment["failure_reason"] == "network_error":
        score += 15
    elif payment["failure_reason"] == "timeout":
        score += 15
    elif payment["failure_reason"] == "insufficient_funds":
        score += 10
    elif payment["failure_reason"] == "bank_declined":
        score += 5

    return min(score, 100)


def classify_priority(score):
    if score >= 70:
        return "HIGH"
    elif score >= 45:
        return "MEDIUM"
    else:
        return "LOW"


def recommend_action(payment, score):
    """
    Select a bounded recovery action.
    """

    if score < 45:
        return "manual_review"

    if payment["failure_reason"] == "network_error":
        return "retry_payment"

    if payment["failure_reason"] == "timeout":
        return "retry_payment"

    if payment["failure_reason"] == "insufficient_funds":
        return "send_payment_link"

    if payment["failure_reason"] == "bank_declined":
        return "send_payment_link"

    if payment["failure_reason"] == "expired_card":
        return "request_payment_method_update"

    return "manual_review"


def analyze_payments(file_path):
    df = pd.read_csv(file_path)

    failed = df[df["status"] == "failed"].copy()

    failed["recovery_score"] = failed.apply(
        calculate_recovery_score,
        axis=1
    )

    failed["priority"] = failed["recovery_score"].apply(
        classify_priority
    )

    failed["recommended_action"] = failed.apply(
        lambda payment: recommend_action(
            payment,
            payment["recovery_score"]
        ),
        axis=1
    )

    return failed.sort_values(
        by=["recovery_score", "amount"],
        ascending=[False, False]
    )