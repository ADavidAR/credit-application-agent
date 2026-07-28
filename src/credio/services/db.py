from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from pathlib import Path

from src.credio.schemas import PredictionRequest
from src.credio.dtos import Base, Log

class DBService:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self._engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self._engine)

    def insert_record(self, data: PredictionRequest, credit_risk: int) -> None:
        with Session(self._engine) as session:
            new_log = Log(
                annual_income=data.annual_income,
                monthly_inhand_salary=data.monthly_inhand_salary,
                credit_history_age=data.credit_history_age,
                total_emi_per_month=data.total_emi_per_month,
                interest_rate=data.interest_rate,
                num_of_loan=data.num_of_loan,
                delay_from_due_date=data.delay_from_due_date,
                num_of_delayed_payment=data.num_of_delayed_payment,
                num_credit_inquiries=data.num_credit_inquiries,
                credit_mix=data.credit_mix,
                outstanding_debt=data.outstanding_debt,
                credit_utilization_ratio=data.credit_utilization_ratio,
                payment_of_min_amount=data.payment_of_min_amount,
                monthly_balance=data.monthly_balance,
                spend_level=data.spend_level,
                value_level=data.value_level,
                credit_risk=credit_risk
            )
            session.add(new_log)
            session.commit()