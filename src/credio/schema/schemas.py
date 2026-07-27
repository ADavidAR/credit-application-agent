from pydantic import BaseModel

class PredictionRequest(BaseModel):
    credit_mix: int
    interest_rate: float
    payment_of_min_amount: int
    num_credit_inquiries: int
    delay_from_due_date: int
    