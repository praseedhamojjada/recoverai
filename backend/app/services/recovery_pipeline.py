from backend.app.services.recovery_engine import analyze_payments
from backend.app.services.recovery_executor import (
    execute_recovery,
)
from backend.app.services.recovery_predictor import (
    train_recovery_model,
    predict_recovery_probability,
)
from backend.app.agents.recovery_agent import make_recovery_decision
from backend.app.services.recovery_value import (
    calculate_action_probability,
)
from backend.app.policies.recovery_policy import (
    check_recovery_policy,
)


FILE_PATH = "backend/data/payments.csv"


def run_recovery_pipeline(file_path=FILE_PATH):

    # 1. Detect failed payments
    results = analyze_payments(file_path)

    # 2. Train recovery prediction model
    model = train_recovery_model(file_path)

    # 3. Predict recovery probability
    results["recovery_probability"] = results.apply(
        lambda payment: predict_recovery_probability(
            model,
            payment.to_dict()
        ),
        axis=1
    )

    # 4. AI agent selects best action
    decisions = results.apply(
        lambda payment: make_recovery_decision(
            payment.to_dict()
        ),
        axis=1
    )

    results["recommended_action"] = [
        decision["selected_action"]
        for decision in decisions
    ]

    results["agent_reason"] = [
        decision["reason"]
        for decision in decisions
    ]

    # 5. Calculate action probability
    results["action_probability"] = results.apply(
        lambda payment: calculate_action_probability(
            payment["failure_reason"],
            payment["recommended_action"]
        ),
        axis=1
    )

    # 6. Calculate expected recovery
    results["expected_recovery"] = (
        results["amount"]
        * results["recovery_probability"]
        * results["action_probability"]
    ).round(2)

    # 7. Apply financial guardrails
    policy_results = results.apply(
        check_recovery_policy,
        axis=1
    )

    results["recovery_allowed"] = [
        result["allowed"]
        for result in policy_results
    ]

    results["policy_reasons"] = [
        ", ".join(result["reasons"])
        if result["reasons"]
        else "approved"
        for result in policy_results
    ]

    # 8. Sort by expected financial value
    results = results.sort_values(
        by="expected_recovery",
        ascending=False
    )
        # 9. Execute approved recovery actions
    execution_results = results.apply(
        lambda payment: execute_recovery(
            payment.to_dict()
        ),
        axis=1
    )

    results["execution_status"] = [
        result["status"]
        for result in execution_results
    ]

    results["recovered_amount"] = [
        result["recovered_amount"]
        for result in execution_results
    ]

    results["execution_message"] = [
        result["message"]
        for result in execution_results
    ]

    return results

    return results