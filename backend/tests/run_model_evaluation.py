from backend.app.services.recovery_predictor import (
    evaluate_recovery_model,
)


FILE_PATH = "backend/data/payments.csv"


metrics = evaluate_recovery_model(FILE_PATH)


print("\n========== ML MODEL EVALUATION ==========\n")

print(
    f"Accuracy:  {metrics['accuracy']:.2f}"
)

print(
    f"Precision: {metrics['precision']:.2f}"
)

print(
    f"Recall:    {metrics['recall']:.2f}"
)

print(
    f"F1 Score:  {metrics['f1_score']:.2f}"
)

print("\nConfusion Matrix:")

print(
    metrics["confusion_matrix"]
)