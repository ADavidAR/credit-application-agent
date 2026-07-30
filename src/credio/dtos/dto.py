from sqlalchemy import select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

class BaseTree(DeclarativeBase):
    """Base SQLAlchemy para la bitácora del árbol de decisión ("Log_Tree")."""
    pass

class BaseKNN(DeclarativeBase):
    """Base SQLAlchemy para la bitácora del modelo KNN ("Log_KNN")."""
    pass

class Log_Tree(BaseTree):
    """
    Registro de una predicción hecha con el árbol de decisión. Guarda las
    variables usadas por ese modelo, la clase de riesgo predicha y la
    fecha de la predicción.
    """

    __tablename__ = "Logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    outstanding_debt: Mapped[float]
    credit_mix: Mapped[str]
    interest_rate: Mapped[float]
    credit_history_age: Mapped[int]
    delay_from_due_date: Mapped[int]
    credit_risk: Mapped[int]
    prediction_date: Mapped[datetime] = mapped_column(server_default=func.now())

class Log_KNN(BaseKNN):
    """
    Registro de una predicción hecha con el modelo KNN. Guarda las
    variables usadas por ese modelo, la clase de riesgo predicha y la
    fecha de la predicción.
    """

    __tablename__ = "Logs"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    credit_mix: Mapped[str]
    interest_rate: Mapped[float]
    payment_of_min_amount: Mapped[str]
    num_credit_inquiries: Mapped[int]
    delay_from_due_date: Mapped[int]
    credit_risk: Mapped[int]
    prediction_date: Mapped[datetime] = mapped_column(server_default=func.now())
