import random
import pandas as pd


random.seed(42)

payment_methods = ["upi", "card", "netbanking", "wallet"]

failure_reasons = [
    "insufficient_funds",
    "bank_declined",
    "network_error",
    "expired_card",
    "timeout",
]

records = []

for i in range(1, 101):

    status = random.choices(
        ["success", "failed"],
        weights=[65, 35]
    )[0]

    amount = random.choice([
        199, 299, 499, 999, 1499,
        2499, 4999, 9999
    ])

    payment_method = random.choice(payment_methods)

    if status == "failed":
        failure_reason = random.choice(failure_reasons)
    else:
        failure_reason = None

    retry_count = random.randint(0, 3)

    previous_success_rate = round(
        random.uniform(0.2, 1.0), 2
    )

    days_since_last_attempt = random.randint(0, 7)

    recovery_status = (
        "pending" if status == "failed"
        else "not_required"
    )

    records.append({
        "payment_id": f"pay_{1000 + i}",
        "customer_id": f"cust_{random.randint(100, 130)}",
        "amount": amount,
        "currency": "INR",
        "status": status,
        "failure_reason": failure_reason,
        "payment_method": payment_method,
        "retry_count": retry_count,
        "previous_success_rate": previous_success_rate,
        "days_since_last_attempt": days_since_last_attempt,
        "recovery_status": recovery_status,
    })


df = pd.DataFrame(records)

df.to_csv(
    "backend/data/payments.csv",
    index=False
)

print("Dataset generated successfully!")
print(f"Total payments: {len(df)}")
print(f"Successful payments: {(df['status'] == 'success').sum()}")
print(f"Failed payments: {(df['status'] == 'failed').sum()}")
print(
    f"Revenue at risk: "
    f"₹{df.loc[df['status'] == 'failed', 'amount'].sum():,.2f}"
)