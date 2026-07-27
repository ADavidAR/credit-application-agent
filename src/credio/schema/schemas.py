from typing import Optional, Literal

from pydantic import BaseModel

CreditMix = Literal["Good", "Standard", "Bad"]
PaymentOfMinAmount = Literal["Yes", "No"]
RiskLevel = Literal["alto", "medio", "bajo"]


class PredictionRequest(BaseModel):
    credit_mix: CreditMix
    interest_rate: float
    payment_of_min_amount: PaymentOfMinAmount
    num_credit_inquiries: int
    delay_from_due_date: int

class CollectedData(BaseModel):
    credit_mix: Optional[CreditMix] = None
    interest_rate: Optional[float] = None
    payment_of_min_amount: Optional[PaymentOfMinAmount] = None
    num_credit_inquiries: Optional[int] = None
    delay_from_due_date: Optional[int] = None

    def missing_fields(self) -> list[str]:
        return [name for name, value in self.model_dump().items() if value is None]

    def is_complete(self) -> bool:
        return not self.missing_fields()

    def to_prediction_request(self) -> PredictionRequest:
        if not self.is_complete():
            raise ValueError("Faltan campos para construir PredictionRequest")
        return PredictionRequest(**self.model_dump())
    