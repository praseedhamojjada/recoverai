from backend.app.services.risk_metrics import (
    calculate_financial_risk,
)


FILE_PATH = "backend/data/payments.csv"


def test_financial_risk():

    metrics = calculate_financial_risk(FILE_PATH)

    assert metrics["false_positives"] >= 0

    assert metrics["false_negatives"] >= 0

    assert metrics["false_positive_amount"] >= 0

    assert metrics["missed_revenue"] >= 0

    assert metrics[
        "estimated_false_positive_cost"
    ] >= 0