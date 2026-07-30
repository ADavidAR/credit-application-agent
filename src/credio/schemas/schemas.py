from typing import Optional, Literal

from pydantic import BaseModel, Field

CreditMix = Literal["Good", "Standard", "Bad"]
PaymentOfMinAmount = Literal["Yes", "No"]
RiskLevel = Literal["alto", "medio", "bajo"]
SpendLevel = Literal["Low", "High"]
ValueLevel = Literal["Small", "Medium", "Large"]

class PredictionRequest(BaseModel):
    annual_income: float
    monthly_inhand_salary: float
    credit_history_age: int
    total_emi_per_month: float
    interest_rate: float
    num_of_loan: int
    delay_from_due_date: int
    num_credit_inquiries: int
    credit_mix: CreditMix
    outstanding_debt: float
    credit_utilization_ratio: float
    payment_of_min_amount: PaymentOfMinAmount
    monthly_balance: float
    spend_level: SpendLevel
    value_level: ValueLevel


class CollectedData(BaseModel):
    annual_income: Optional[float] = None
    monthly_inhand_salary: Optional[float] = None
    credit_history_age: Optional[int] = None
    total_emi_per_month: Optional[float] = None
    interest_rate: Optional[float] = None
    num_of_loan: Optional[int] = None
    delay_from_due_date: Optional[int] = None
    num_credit_inquiries: Optional[int] = None
    credit_mix: Optional[CreditMix] = None
    outstanding_debt: Optional[float] = None
    credit_utilization_ratio: Optional[float] = None
    payment_of_min_amount: Optional[PaymentOfMinAmount] = None
    monthly_balance: Optional[float] = None
    spend_level: Optional[SpendLevel] = None
    value_level: Optional[ValueLevel] = None



    def missing_fields(self) -> list[str]:
        return [name for name, value in self.model_dump().items() if value is None]

    def is_complete(self) -> bool:
        return not self.missing_fields()

    def to_prediction_request(self) -> PredictionRequest:
        if not self.is_complete():
            raise ValueError("Faltan campos para construir PredictionRequest")
        return PredictionRequest(**self.model_dump())


class ConfirmationIntent(BaseModel):
    confirmed: Optional[bool] = Field(
        default=None,
        description="True si el usuario confirma que los datos mostrados son correctos, False si indica que algo está mal o quiere corregir un dato, null si la respuesta no es un sí/no claro.",
    )
