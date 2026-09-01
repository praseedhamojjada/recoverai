from pydantic import BaseModel
from typing import Optional


class Payment(BaseModel):
    payment_id: str
    customer_id: str
    amount: float
    currency: str = "INR"

    status: str
    failure_reason: Optional[str] = None

    payment_method: str

    retry_count: int = 0
    previous_success_rate: float = 0.0

    days_since_last_attempt: int = 0

    recovery_status: str = "pending"