import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


def train_recovery_model(file_path):
    """
    Train a model to predict whether a failed payment
    is likely to be recovered.
    """

    df = pd.read_csv(file_path)

    # We only train on failed payments
    df = df[df["status"] == "failed"].copy()

    # --------------------------------------------------
    # CREATE TRAINING LABEL
    # --------------------------------------------------

    # For our synthetic dataset, define a historical
    # recovery outcome using payment behavior.
    df["recovered"] = (
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

    # --------------------------------------------------
    # FEATURES
    # --------------------------------------------------

    features = [
        "amount",
        "payment_method",
        "failure_reason",
        "retry_count",
        "previous_success_rate",
        "days_since_last_attempt",
    ]

    X = df[features]
    y = df["recovered"]

    # --------------------------------------------------
    # CATEGORICAL FEATURES
    # --------------------------------------------------

    categorical_features = [
        "payment_method",
        "failure_reason",
    ]

    numerical_features = [
        "amount",
        "retry_count",
        "previous_success_rate",
        "days_since_last_attempt",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            (
                "numerical",
                "passthrough",
                numerical_features,
            ),
        ]
    )

    # --------------------------------------------------
    # RANDOM FOREST MODEL
    # --------------------------------------------------

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    pipeline.fit(X, y)

    return pipeline


def predict_recovery_probability(model, payment):
    """
    Predict the probability that a payment can be recovered.
    """

    features = [
        "amount",
        "payment_method",
        "failure_reason",
        "retry_count",
        "previous_success_rate",
        "days_since_last_attempt",
    ]

    payment_df = pd.DataFrame(
        [payment],
        columns=features
    )

    probability = model.predict_proba(
        payment_df
    )[0][1]

    return round(float(probability), 2)

def evaluate_recovery_model(file_path):
    """
    Evaluate the recovery prediction model using
    a train/test split.
    """

    df = pd.read_csv(file_path)

    # Only failed payments are relevant
    df = df[df["status"] == "failed"].copy()

    # Create synthetic historical recovery outcome
    df["recovered"] = (
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

    features = [
        "amount",
        "payment_method",
        "failure_reason",
        "retry_count",
        "previous_success_rate",
        "days_since_last_attempt",
    ]

    X = df[features]
    y = df["recovered"]

    categorical_features = [
        "payment_method",
        "failure_reason",
    ]

    numerical_features = [
        "amount",
        "retry_count",
        "previous_success_rate",
        "days_since_last_attempt",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            (
                "numerical",
                "passthrough",
                numerical_features,
            ),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    return {
        "accuracy": round(
            accuracy_score(y_test, predictions), 2
        ),
        "precision": round(
            precision_score(
                y_test,
                predictions,
                zero_division=0
            ),
            2
        ),
        "recall": round(
            recall_score(
                y_test,
                predictions,
                zero_division=0
            ),
            2
        ),
        "f1_score": round(
            f1_score(
                y_test,
                predictions,
                zero_division=0
            ),
            2
        ),
        "confusion_matrix": confusion_matrix(
            y_test,
            predictions
        ).tolist(),
    }