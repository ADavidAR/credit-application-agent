from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from src.credio.schemas import PredictionRequest
from src.credio.dtos import Base, Log_Tree, Log_KNN

class LogService:
    def __init__(self, db_path: str ) -> None:
        self.db_path = db_path
        self._engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self._engine)

    def add_log(self, data: PredictionRequest, credit_risk: int) -> None:
        with Session(self._engine) as session:
            new_log = None
            if "tree" in self.db_path:
                new_log = Log_Tree(
                    outstanding_debt=data.outstanding_debt,
                    credit_mix=data.credit_mix,
                    interest_rate=data.interest_rate,
                    credit_utilization_ratio=data.credit_utilization_ratio,
                    delay_from_due_date=data.delay_from_due_date,
                    credit_risk=credit_risk
                )
            else:
                new_log = Log_KNN(
                    credit_mix=data.credit_mix,
                    interest_rate=data.interest_rate,
                    payment_of_min_amount=data.payment_of_min_amount,
                    num_credit_inquiries=data.num_credit_inquiries,
                    delay_from_due_date=data.delay_from_due_date,
                    credit_risk=credit_risk
                )
            session.add(new_log)
            session.commit()