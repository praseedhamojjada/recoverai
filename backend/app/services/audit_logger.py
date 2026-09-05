import csv
import os
from datetime import datetime


AUDIT_FILE = "backend/data/recovery_audit.csv"


def write_audit_log(df):
    """
    Write the current recovery batch to the audit log.

    The file is replaced for each new batch so repeated
    dashboard/API requests do not create duplicate entries.
    """

    timestamp = datetime.now().isoformat(
        timespec="seconds"
    )

    file_exists = os.path.exists(AUDIT_FILE)

    with open(
        AUDIT_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "timestamp",
            "payment_id",
            "customer_id",
            "amount",
            "failure_reason",
            "recovery_probability",
            "recommended_action",
            "action_probability",
            "expected_recovery",
            "recovery_allowed",
            "policy_reasons",
            "execution_status",
            "recovered_amount",
            "agent_reason",
            "execution_message",
        ])

        for _, payment in df.iterrows():

            writer.writerow([
                timestamp,
                payment["payment_id"],
                payment["customer_id"],
                payment["amount"],
                payment["failure_reason"],
                payment["recovery_probability"],
                payment["recommended_action"],
                payment["action_probability"],
                payment["expected_recovery"],
                payment["recovery_allowed"],
                payment["policy_reasons"],
                payment["execution_status"],
                payment["recovered_amount"],
                payment["agent_reason"],
                payment["execution_message"],
            ])


def read_audit_log():
    """
    Read the latest recovery batch from the audit log.
    """

    if not os.path.exists(AUDIT_FILE):
        return []

    with open(
        AUDIT_FILE,
        "r",
        newline="",
        encoding="utf-8",
    ) as file:

        reader = csv.DictReader(file)

        return list(reader)