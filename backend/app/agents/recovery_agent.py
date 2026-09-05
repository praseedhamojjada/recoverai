from backend.app.services.recovery_value import (
    calculate_action_probability,
)


def evaluate_actions(payment):
    """
    Evaluate possible recovery actions for a failed payment.
    """

    failure_reason = payment["failure_reason"]

    possible_actions = []

    if failure_reason in ["network_error", "timeout"]:

        possible_actions.append(
            "retry_payment"
        )

        possible_actions.append(
            "send_payment_link"
        )

    elif failure_reason == "insufficient_funds":

        possible_actions.append(
            "send_payment_link"
        )

        possible_actions.append(
            "retry_payment"
        )

    elif failure_reason == "bank_declined":

        possible_actions.append(
            "send_payment_link"
        )

        possible_actions.append(
            "request_payment_method_update"
        )

    elif failure_reason == "expired_card":

        possible_actions.append(
            "request_payment_method_update"
        )

        possible_actions.append(
            "send_payment_link"
        )

    else:

        possible_actions.append(
            "manual_review"
        )

    return [
        {
            "action": action,
            "probability": calculate_action_probability(
                failure_reason,
                action,
            ),
        }
        for action in possible_actions
    ]


def make_recovery_decision(payment):
    """
    Select the recovery action with the highest
    expected monetary recovery.
    """

    actions = evaluate_actions(payment)

    amount = payment["amount"]
    recovery_probability = payment[
        "recovery_probability"
    ]

    evaluated_actions = []

    for option in actions:

        expected_recovery = (
            amount
            * recovery_probability
            * option["probability"]
        )

        evaluated_actions.append(
            {
                "action": option["action"],
                "probability": option["probability"],
                "expected_recovery": round(
                    expected_recovery,
                    2,
                ),
            }
        )

    best = max(
        evaluated_actions,
        key=lambda x: x["expected_recovery"],
    )

    return {
        "payment_id": payment["payment_id"],
        "selected_action": best["action"],
        "expected_recovery": best[
            "expected_recovery"
        ],
        "evaluated_actions": evaluated_actions,
        "reason": (
            f"Selected {best['action']} because "
            f"it has the highest expected recovery "
            f"value."
        ),
    }