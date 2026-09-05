import pandas as pd


def calculate_financial_risk(
    file_path,
    false_positive_cost_rate=0.02
):
    """
    Estimate the financial impact of incorrect
    recovery predictions.

    false_positive_cost_rate represents the estimated
    operational cost of attempting an unnecessary
    recovery action.
    """

    df = pd.read_csv(file_path)

    df = df[df["status"] == "failed"].copy()

    # Synthetic historical recovery outcome
    df["actual_recovered"] = (
        (
            (df["previous_success_rate"] >= 0.6)
            & (df["retry_count"] <= 1)
            & (df["days_since_last_attempt"] <= 3)
        )
        |
        (
            df["failure_reason"].isin(
                ["network_error", "timeout"]
            )
            & (df["retry_count"] == 0)
        )
    ).astype(int)

    # Train using the existing ML model
    from backend.app.services.recovery_predictor import (
        train_recovery_model,
    )

    model = train_recovery_model(file_path)

    features = [
        "amount",
        "payment_method",
        "failure_reason",
        "retry_count",
        "previous_success_rate",
        "days_since_last_attempt",
    ]

    predictions = model.predict(df[features])

    df["predicted_recoverable"] = predictions

    # --------------------------------------------------
    # FALSE POSITIVES
    # --------------------------------------------------

    false_positives = df[
        (df["predicted_recoverable"] == 1)
        & (df["actual_recovered"] == 0)
    ]

    # --------------------------------------------------
    # FALSE NEGATIVES
    # --------------------------------------------------

    false_negatives = df[
        (df["predicted_recoverable"] == 0)
        & (df["actual_recovered"] == 1)
    ]

    # --------------------------------------------------
    # FINANCIAL IMPACT
    # --------------------------------------------------

    false_positive_amount = false_positives[
        "amount"
    ].sum()

    false_negative_amount = false_negatives[
        "amount"
    ].sum()

    estimated_false_positive_cost = (
        false_positive_amount
        * false_positive_cost_rate
    )

    return {
        "false_positives": len(false_positives),
        "false_negatives": len(false_negatives),
        "false_positive_amount": float(
            false_positive_amount
        ),
        "missed_revenue": float(
            false_negative_amount
        ),
        "estimated_false_positive_cost": round(
            float(estimated_false_positive_cost),
            2
        ),
    }