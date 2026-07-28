from sqlalchemy import select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Log(Base):
    __tablename__ = "Logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    annual_income: Mapped[float]
    monthly_inhand_salary: Mapped[float]
    credit_history_age: Mapped[int]
    total_emi_per_month: Mapped[float]
    interest_rate: Mapped[float]
    num_of_loan: Mapped[int]
    delay_from_due_date: Mapped[int]
    num_of_delayed_payment: Mapped[int]
    num_credit_inquiries: Mapped[int]
    credit_mix: Mapped[str]
    outstanding_debt: Mapped[float]
    credit_utilization_ratio: Mapped[float]
    payment_of_min_amount: Mapped[str]
    monthly_balance: Mapped[float]
    spend_level: Mapped[str]
    value_level: Mapped[str]
    credit_risk: Mapped[int]
    predict_date: Mapped[datetime] = mapped_column(server_default=func.now())