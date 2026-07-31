from typing import Optional, Literal

from pydantic import BaseModel, Field

CreditMix = Literal["Good", "Standard", "Bad"]
PaymentOfMinAmount = Literal["Yes", "No"]
RiskLevel = Literal["alto", "medio", "bajo"]
SpendLevel = Literal["Low", "High"]
ValueLevel = Literal["Small", "Medium", "Large"]

class PredictionRequest(BaseModel):
    """
    Solicitud de evaluación de riesgo crediticio. Contiene los 15 campos
    ya completos que necesita el modelo predictivo ("/predict").
    """

    annual_income: float = Field(ge=0)
    monthly_inhand_salary: float = Field(ge=0)
    credit_history_age: int = Field(ge=0)
    total_emi_per_month: float = Field(ge=0)
    interest_rate: float = Field(ge=0)
    num_of_loan: int = Field(ge=0)
    delay_from_due_date: int
    num_credit_inquiries: int = Field(ge=0)
    credit_mix: CreditMix
    outstanding_debt: float = Field(ge=0)
    credit_utilization_ratio: float = Field(ge=0)
    payment_of_min_amount: PaymentOfMinAmount
    monthly_balance: float = Field(ge=0)
    spend_level: SpendLevel
    value_level: ValueLevel


class CollectedData(BaseModel):
    """
    Versión parcial de "PredictionRequest" usada mientras dura la
    conversación. Todos sus campos son opcionales, ya que se van llenando
    de a poco a medida que el usuario los proporciona.
    """

    annual_income: Optional[float] = Field(default=None, ge=0)
    monthly_inhand_salary: Optional[float] = Field(default=None, ge=0)
    credit_history_age: Optional[int] = Field(default=None, ge=0)
    total_emi_per_month: Optional[float] = Field(default=None, ge=0)
    interest_rate: Optional[float] = Field(default=None, ge=0)
    num_of_loan: Optional[int] = Field(default=None, ge=0)
    delay_from_due_date: Optional[int] = None
    num_credit_inquiries: Optional[int] = Field(default=None, ge=0)
    credit_mix: Optional[CreditMix] = None
    outstanding_debt: Optional[float] = Field(default=None, ge=0)
    credit_utilization_ratio: Optional[float] = Field(default=None, ge=0)
    payment_of_min_amount: Optional[PaymentOfMinAmount] = None
    monthly_balance: Optional[float] = Field(default=None, ge=0)
    spend_level: Optional[SpendLevel] = None
    value_level: Optional[ValueLevel] = None



    def missing_fields(self) -> list[str]:
        return [name for name, value in self.model_dump().items() if value is None]

    def is_complete(self) -> bool:
        return not self.missing_fields()

    def to_prediction_request(self) -> PredictionRequest:
        """
        Convierte los datos ya recopilados en un "PredictionRequest" listo
        para enviar a la API de predicción.

        Returns:
            PredictionRequest con los mismos valores ya recopilados.

        Raises:
            ValueError: si todavía falta algún campo por completar.
        """
        if not self.is_complete():
            raise ValueError("Faltan campos para construir PredictionRequest")
        return PredictionRequest(**self.model_dump())


class ConfirmationIntent(BaseModel):
    """
    Resultado de clasificar la respuesta del usuario ante el resumen de
    datos que se le mostró para confirmar antes de predecir.
    """

    confirmed: Optional[bool] = Field(
        default=None,
        description="True si el usuario confirma que los datos mostrados son correctos, False si indica que algo está mal o quiere corregir un dato, null si la respuesta no es un sí/no claro.",
    )
