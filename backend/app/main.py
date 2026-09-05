from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.app.services.audit_logger import (
    write_audit_log,
    read_audit_log,
)
from backend.app.services.recovery_pipeline import (
    run_recovery_pipeline,
)


app = FastAPI(
    title="RecoverAI",
    description="AI Revenue Recovery Agent",
    version="1.0.0",
)


# -----------------------------
# RECOVERY OPPORTUNITIES
# -----------------------------

@app.get("/recovery/opportunities")
def recovery_opportunities():

    df = run_recovery_pipeline()

    columns = [
        "payment_id",
        "customer_id",
        "amount",
        "currency",
        "failure_reason",
        "recovery_probability",
        "recommended_action",
        "expected_recovery",
        "recovery_allowed",
        "policy_reasons",
        "execution_status",
        "recovered_amount",
        "execution_message",
        "agent_reason",
    ]

    return df[columns].to_dict(
        orient="records"
    )


# -----------------------------
# RECOVERY METRICS
# -----------------------------

@app.get("/recovery/metrics")
def recovery_metrics():

    df = run_recovery_pipeline()

    total_at_risk = float(
        df["amount"].sum()
    )

    expected_recovery = float(
        df["expected_recovery"].sum()
    )

    recovered_revenue = float(
        df["recovered_amount"].sum()
    )

    approved = int(
        df["recovery_allowed"].sum()
    )

    blocked = int(
        (~df["recovery_allowed"]).sum()
    )

    recovery_rate = (
        (recovered_revenue / total_at_risk) * 100
        if total_at_risk > 0
        else 0
    )

    return {
        "failed_payments": len(df),

        "revenue_at_risk": round(
            total_at_risk,
            2
        ),

        "expected_recovery": round(
            expected_recovery,
            2
        ),

        "recovered_revenue": round(
            recovered_revenue,
            2
        ),

        "recovery_rate": round(
            recovery_rate,
            2
        ),

        "automated_recoveries_approved": approved,

        "recoveries_blocked": blocked,
    }


# -----------------------------
# PAYMENT DECISION DETAILS
# -----------------------------

@app.get("/recovery/payment/{payment_id}")
def payment_details(payment_id: str):

    df = run_recovery_pipeline()

    payment = df[
        df["payment_id"] == payment_id
    ]

    if payment.empty:
        return {
            "error": "Payment not found"
        }

    record = payment.iloc[0]

    return {
        "payment_id": record["payment_id"],
        "customer_id": record["customer_id"],
        "amount": float(record["amount"]),
        "currency": record["currency"],

        "failure_reason": record[
            "failure_reason"
        ],

        "recovery_probability": float(
            record["recovery_probability"]
        ),

        "recommended_action": record[
            "recommended_action"
        ],

        "action_probability": float(
            record["action_probability"]
        ),

        "expected_recovery": float(
            record["expected_recovery"]
        ),

        "agent_reason": record[
            "agent_reason"
        ],

        "recovery_allowed": bool(
            record["recovery_allowed"]
        ),

        "policy_reasons": record[
            "policy_reasons"
        ],

        "execution_status": record[
            "execution_status"
        ],

        "recovered_amount": float(
            record["recovered_amount"]
        ),

        "execution_message": record[
            "execution_message"
        ],
    }

# -----------------------------
# AUDIT LOG
# -----------------------------

@app.get("/recovery/audit")
def recovery_audit():

    df = run_recovery_pipeline()

    # Create a fresh audit snapshot
    write_audit_log(df)

    audit_records = read_audit_log()

    return {
        "total_records": len(audit_records),
        "records": audit_records,
    }
# -----------------------------
# FRONTEND
# -----------------------------

FRONTEND_DIR = (
    Path(__file__).resolve().parents[2]
    / "frontend"
)


app.mount(
    "/",
    StaticFiles(
        directory=str(FRONTEND_DIR),
        html=True
    ),
    name="frontend",
)