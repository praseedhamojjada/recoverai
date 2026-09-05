import pandas as pd

from backend.app.services.recovery_engine import analyze_payments
from backend.app.services.recovery_simulator import simulate_recovery
from backend.app.policies.recovery_policy import check_recovery_policy

from backend.app.services.recovery_value import (
    calculate_action_probability,
)

from backend.app.services.audit_logger import log_recovery_decision

from backend.app.agents.recovery_agent import (
    make_recovery_decision,
)

from backend.app.services.recovery_predictor import (
    train_recovery_model,
    predict_recovery_probability,
)


FILE_PATH = "backend/data/payments.csv"


def main():

    # --------------------------------------------------
    # STEP 1: ANALYZE FAILED PAYMENTS
    # --------------------------------------------------

    results = analyze_payments(FILE_PATH)

    # --------------------------------------------------
    # STEP 2: TRAIN ML RECOVERY MODEL
    # --------------------------------------------------

    ml_model = train_recovery_model(FILE_PATH)

    # --------------------------------------------------
    # STEP 3: PREDICT RECOVERY PROBABILITY USING ML
    # --------------------------------------------------

    results["recovery_probability"] = results.apply(
        lambda payment: predict_recovery_probability(
            ml_model,
            payment.to_dict()
        ),
        axis=1
    )

    # --------------------------------------------------
    # STEP 4: AI RECOVERY AGENT
    # --------------------------------------------------

    agent_decisions = results.apply(
        lambda payment: make_recovery_decision(
            payment.to_dict()
        ),
        axis=1
    )

    results["agent_selected_action"] = [
        decision["selected_action"]
        for decision in agent_decisions
    ]

    results["agent_expected_recovery"] = [
        decision["expected_recovery"]
        for decision in agent_decisions
    ]

    results["agent_reason"] = [
        decision["reason"]
        for decision in agent_decisions
    ]

    # Agent-selected action becomes the action
    # evaluated by the guardrails.
    results["recommended_action"] = results[
        "agent_selected_action"
    ]

    # --------------------------------------------------
    # STEP 5: CALCULATE ACTION PROBABILITY
    # --------------------------------------------------

    results["action_probability"] = results.apply(
        lambda payment: calculate_action_probability(
            payment["failure_reason"],
            payment["recommended_action"]
        ),
        axis=1
    )

    # --------------------------------------------------
    # STEP 6: CALCULATE EXPECTED RECOVERY
    # --------------------------------------------------

    results["expected_recovery"] = (
        results["amount"]
        * results["recovery_probability"]
        * results["action_probability"]
    ).round(2)

    results = results.sort_values(
        by="expected_recovery",
        ascending=False
    )

    # --------------------------------------------------
    # STEP 7: APPLY DETERMINISTIC GUARDRAILS
    # --------------------------------------------------

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

    # --------------------------------------------------
    # STEP 8: EXECUTE ONLY APPROVED RECOVERIES
    # --------------------------------------------------

    recovery_results = []

    for _, payment in results.iterrows():

        if payment["recovery_allowed"]:

            result = simulate_recovery(payment)

        else:

            result = {
                "payment_id": payment["payment_id"],
                "action": payment["recommended_action"],
                "success": False,
                "recovered_amount": 0.0,
            }

        recovery_results.append(result)

    results["recovery_success"] = [
        result["success"]
        for result in recovery_results
    ]

    results["recovered_amount"] = [
        result["recovered_amount"]
        for result in recovery_results
    ]

    total_recovered = results[
        "recovered_amount"
    ].sum()

    # --------------------------------------------------
    # STEP 9: CREATE AUDIT TRAIL
    # --------------------------------------------------

    for _, payment in results.iterrows():
        log_recovery_decision(payment)

    # --------------------------------------------------
    # STEP 10: DISPLAY RESULTS
    # --------------------------------------------------

    print(
        "\n========== RECOVERAI BATCH ANALYSIS ==========\n"
    )

    print(
        f"Failed payments analyzed: {len(results)}"
    )

    total_at_risk = results["amount"].sum()

    print(
        f"Total revenue at risk: "
        f"₹{total_at_risk:,.2f}"
    )

    # --------------------------------------------------
    # ML + AGENT DECISIONS
    # --------------------------------------------------

    print(
        "\n---------- ML + AI AGENT DECISIONS ----------\n"
    )

    agent_columns = [
        "payment_id",
        "amount",
        "failure_reason",
        "recovery_probability",
        "agent_selected_action",
        "agent_expected_recovery",
    ]

    print(
        results[agent_columns]
        .head(10)
        .to_string(index=False)
    )

    # --------------------------------------------------
    # TOP RECOVERY OPPORTUNITIES
    # --------------------------------------------------

    print(
        "\n---------- TOP RECOVERY OPPORTUNITIES ----------\n"
    )

    columns = [
        "payment_id",
        "amount",
        "failure_reason",
        "recovery_probability",
        "action_probability",
        "expected_recovery",
        "priority",
        "recommended_action",
    ]

    print(
        results[columns]
        .head(10)
        .to_string(index=False)
    )

    # --------------------------------------------------
    # PRIORITY SUMMARY
    # --------------------------------------------------

    print("\n---------- PRIORITY SUMMARY ----------\n")

    print(
        results["priority"]
        .value_counts()
        .to_string()
    )

    # --------------------------------------------------
    # EXPECTED RECOVERY
    # --------------------------------------------------

    print("\n---------- EXPECTED RECOVERY ----------\n")

    total_expected_recovery = results[
        "expected_recovery"
    ].sum()

    print(
        f"Expected recoverable revenue: "
        f"₹{total_expected_recovery:,.2f}"
    )

    # --------------------------------------------------
    # SIMULATED RECOVERY
    # --------------------------------------------------

    print("\n---------- SIMULATED RECOVERY ----------\n")

    successful_recoveries = results[
        "recovery_success"
    ].sum()

    recovery_attempts = results[
        "recovery_allowed"
    ].sum()

    print(
        f"Recovery attempts: "
        f"{recovery_attempts}"
    )

    print(
        f"Successful recoveries: "
        f"{successful_recoveries}"
    )

    print(
        f"Simulated recovered revenue: "
        f"₹{total_recovered:,.2f}"
    )

    # --------------------------------------------------
    # GUARDRAIL SUMMARY
    # --------------------------------------------------

    print("\n---------- GUARDRAIL SUMMARY ----------\n")

    approved_count = results[
        "recovery_allowed"
    ].sum()

    blocked_count = (
        ~results["recovery_allowed"]
    ).sum()

    print(
        f"Automated recoveries approved: "
        f"{approved_count}"
    )

    print(
        f"Recoveries blocked by guardrails: "
        f"{blocked_count}"
    )

    print("\nPolicy decisions:")

    print(
        results[
            [
                "payment_id",
                "amount",
                "recommended_action",
                "recovery_allowed",
                "policy_reasons",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()