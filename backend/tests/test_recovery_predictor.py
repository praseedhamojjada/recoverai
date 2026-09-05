from backend.app.services.recovery_predictor import (
    train_recovery_model,
    predict_recovery_probability,
)


FILE_PATH = "backend/data/payments.csv"


def test_model_training():

    model = train_recovery_model(FILE_PATH)

    assert model is not None


def test_probability_prediction():

    model = train_recovery_model(FILE_PATH)

    payment = {
        "amount": 1499,
        "payment_method": "upi",
        "failure_reason": "network_error",
        "retry_count": 0,
        "previous_success_rate": 0.8,
        "days_since_last_attempt": 1,
    }

    probability = predict_recovery_probability(
        model,
        payment
    )

    assert 0 <= probability <= 1

def test_model_evaluation():

    from backend.app.services.recovery_predictor import (
        evaluate_recovery_model,
    )

    metrics = evaluate_recovery_model(FILE_PATH)

    assert 0 <= metrics["accuracy"] <= 1
    assert 0 <= metrics["precision"] <= 1
    assert 0 <= metrics["recall"] <= 1
    assert 0 <= metrics["f1_score"] <= 1

    assert len(metrics["confusion_matrix"]) == 2