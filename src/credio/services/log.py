from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session

from credio.schemas import PredictionRequest
from credio.dtos import BaseTree, BaseKNN, Log_Tree, Log_KNN

class LogService:
    def __init__(self, db_path: str ) -> None:
        self.db_path = db_path
        self._engine = create_engine(f"sqlite:///{self.db_path}")
        if "logs_tree.db" in self.db_path:
            BaseTree.metadata.create_all(self._engine)
        else:
            BaseKNN.metadata.create_all(self._engine)
            
    def add_log(self, data: PredictionRequest, credit_risk: int) -> None:
        with Session(self._engine) as session:
            new_log = None
            if "logs_tree.db" in self.db_path:
                new_log = Log_Tree(
                    outstanding_debt=data.outstanding_debt,
                    credit_mix=data.credit_mix,
                    interest_rate=data.interest_rate,
                    credit_history_age=data.credit_history_age,
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
            print("added")
            session.commit()
            print("commited")